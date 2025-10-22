"""
Filing download functionality.
"""
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass

from .sec_client import SECClient
from .config import Config
from .exceptions import DownloadError, FilingNotFoundError


logger = logging.getLogger(__name__)


@dataclass
class Filing:
    """Represents a single SEC filing."""
    form: str
    accession: str
    filing_date: str
    primary_doc: str
    cik: str = ""
    company_name: str = ""

    @property
    def accession_no_dash(self) -> str:
        """Get accession number without dashes."""
        return self.accession.replace("-", "")

    def __str__(self) -> str:
        return f"{self.form} | {self.filing_date} | {self.accession}"


class FilingDownloader:
    """
    Handles downloading of SEC filings and related files.
    """

    def __init__(
        self,
        client: Optional[SECClient] = None,
        config: Optional[Config] = None
    ):
        """
        Initialize filing downloader.

        Args:
            client: SEC API client. If None, creates a new one.
            config: Configuration object.
        """
        self.config = config or Config()
        self.client = client or SECClient(self.config)
        logger.info("FilingDownloader initialized")

    def get_recent_filings(
        self,
        cik: str,
        form_types: Optional[Tuple[str, ...]] = None,
        limit: int = 20
    ) -> List[Filing]:
        """
        Get recent filings for a company.

        Args:
            cik: 10-digit CIK string.
            form_types: Tuple of form types to filter (e.g., ('10-K', '10-Q')).
                       If None, uses config default.
            limit: Maximum number of filings to return.

        Returns:
            List of Filing objects.

        Raises:
            FilingNotFoundError: If no filings found.
        """
        if form_types is None:
            form_types = self.config.supported_form_types

        logger.info(f"Fetching recent filings for CIK {cik}, forms: {form_types}")

        submissions = self.client.get_company_submissions(cik)
        recent = submissions.get("filings", {}).get("recent", {})

        if not recent:
            raise FilingNotFoundError(f"No filings found for CIK {cik}")

        company_name = submissions.get("name", "Unknown")
        filings = []

        forms = recent.get("form", [])
        accessions = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        primary_docs = recent.get("primaryDocument", [])

        for i, form in enumerate(forms):
            if form in form_types:
                filings.append(Filing(
                    form=form,
                    accession=accessions[i],
                    filing_date=filing_dates[i],
                    primary_doc=primary_docs[i],
                    cik=cik,
                    company_name=company_name
                ))

            if len(filings) >= limit:
                break

        if not filings:
            raise FilingNotFoundError(
                f"No filings found for CIK {cik} with types {form_types}"
            )

        logger.info(f"Found {len(filings)} filings")
        return filings

    def build_filing_urls(self, filing: Filing) -> Dict[str, str]:
        """
        Build URLs for a filing.

        Args:
            filing: Filing object.

        Returns:
            Dictionary with URLs (index_json, primary_doc, folder, filing_page).
        """
        cik_no_zeros = str(int(filing.cik))
        acc_nodash = filing.accession_no_dash

        base_url = (f"{self.config.sec_files_base}/Archives/edgar/data/"
                   f"{cik_no_zeros}/{acc_nodash}")

        return {
            "index_json": f"{base_url}/index.json",
            "primary_doc": f"{base_url}/{filing.primary_doc}",
            "folder": base_url,
            "filing_page": (f"{self.config.sec_files_base}/cgi-bin/viewer?"
                          f"action=view&cik={cik_no_zeros}&accession_number="
                          f"{filing.accession_no_dash}&xbrl_type=v"),
        }

    def download_filing(
        self,
        filing: Filing,
        output_dir: Optional[Path] = None,
        include_exhibits: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Path]:
        """
        Download entire filing package.

        Args:
            filing: Filing object to download.
            output_dir: Output directory. If None, uses config default.
            include_exhibits: Whether to include exhibit files.
            progress_callback: Optional callback for progress updates (current, total).

        Returns:
            List of downloaded file paths.

        Raises:
            DownloadError: If download fails.
        """
        if output_dir is None:
            output_dir = self.config.output_dir

        filing_dir = output_dir / filing.accession
        filing_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading filing {filing.accession} to {filing_dir}")

        try:
            # Get file index
            urls = self.build_filing_urls(filing)
            cik_no_zeros = str(int(filing.cik))
            index_data = self.client.get_filing_index(
                cik_no_zeros,
                filing.accession_no_dash
            )

            files = index_data.get("directory", {}).get("item", [])
            if not files:
                raise DownloadError("No files found in filing index")

            # Filter files if not including exhibits
            if not include_exhibits:
                files = [
                    f for f in files
                    if re.search(r"\.(htm|html|txt|xml)$", f["name"], re.I)
                ]

            downloaded_paths = []
            total_files = len(files)

            logger.info(f"Downloading {total_files} files")

            for idx, file_info in enumerate(files):
                filename = file_info["name"]
                file_url = f"{urls['folder']}/{filename}"
                dest_path = filing_dir / filename

                try:
                    self.client.download_file(file_url, dest_path)
                    downloaded_paths.append(dest_path)

                    if progress_callback:
                        progress_callback(idx + 1, total_files)

                except Exception as e:
                    logger.warning(f"Failed to download {filename}: {e}")

            logger.info(f"Successfully downloaded {len(downloaded_paths)} files")
            return downloaded_paths

        except Exception as e:
            logger.error(f"Failed to download filing: {e}")
            raise DownloadError(f"Failed to download filing: {e}") from e

    def get_preferred_view_file(
        self,
        filing_dir: Path,
        filing: Filing
    ) -> Optional[Path]:
        """
        Determine the best file to view for a filing.

        Uses heuristics to find the most useful HTML file for viewing.

        Args:
            filing_dir: Directory containing downloaded filing.
            filing: Filing object.

        Returns:
            Path to preferred file, or None if not found.
        """
        if not filing_dir.exists():
            logger.warning(f"Filing directory not found: {filing_dir}")
            return None

        def file_size(p: Path) -> int:
            try:
                return p.stat().st_size
            except Exception:
                return 0

        # Priority 1: Primary document if substantial
        primary_path = filing_dir / filing.primary_doc
        if primary_path.exists() and file_size(primary_path) > 2048:
            logger.debug(f"Using primary document: {primary_path}")
            return primary_path

        # Priority 2: index-headers.html
        headers_path = filing_dir / f"{filing.accession}-index-headers.html"
        if headers_path.exists():
            logger.debug(f"Using index-headers: {headers_path}")
            return headers_path

        # Priority 3: index.html
        index_path = filing_dir / f"{filing.accession}-index.html"
        if index_path.exists():
            logger.debug(f"Using index: {index_path}")
            return index_path

        # Priority 4: R1.htm
        r1_path = filing_dir / "R1.htm"
        if r1_path.exists():
            logger.debug(f"Using R1.htm: {r1_path}")
            return r1_path

        # Priority 5: Largest R*.htm file
        r_files = list(filing_dir.glob("R*.htm*"))
        if r_files:
            largest_r = max(r_files, key=file_size)
            logger.debug(f"Using largest R file: {largest_r}")
            return largest_r

        # Priority 6: Largest non-exhibit HTML file
        def is_exhibit(name: str) -> bool:
            lower = name.lower()
            return lower.startswith("ex") or "exhibit" in lower or "xex" in lower

        html_files = [
            p for p in filing_dir.glob("*.htm*")
            if not is_exhibit(p.name)
        ]
        if html_files:
            largest_html = max(html_files, key=file_size)
            logger.debug(f"Using largest HTML: {largest_html}")
            return largest_html

        # Fallback: primary document even if small
        if primary_path.exists():
            logger.debug(f"Fallback to primary document: {primary_path}")
            return primary_path

        logger.warning("No suitable view file found")
        return None
