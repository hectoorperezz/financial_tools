"""
Filing manager to orchestrate all filing operations.
"""
import logging
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import Config
from .sec_client import SECClient
from .company_lookup import CompanyLookup
from .filing_downloader import FilingDownloader, Filing
from .extractors import (
    TableExtractor,
    SectionExtractor,
    FinancialStatementExtractor
)


logger = logging.getLogger(__name__)


class FilingManager:
    """
    High-level manager for SEC filing operations.

    Coordinates company lookup, filing download, and data extraction.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize filing manager.

        Args:
            config: Configuration object.
        """
        self.config = config or Config()
        self.client = SECClient(self.config)
        self.company_lookup = CompanyLookup(self.client, self.config)
        self.downloader = FilingDownloader(self.client, self.config)
        self.table_extractor = TableExtractor(self.config)
        self.section_extractor = SectionExtractor(self.config)
        self.financial_extractor = FinancialStatementExtractor(self.client, self.config)

        logger.info("FilingManager initialized")

    def search_company(self, ticker: str) -> Dict[str, Any]:
        """
        Search for company by ticker.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Company information dictionary.
        """
        logger.info(f"Searching for company: {ticker}")
        return self.company_lookup.get_company_info(ticker)

    def get_filings(
        self,
        ticker: str,
        form_types: Optional[tuple] = None,
        limit: int = 20
    ) -> List[Filing]:
        """
        Get recent filings for a company.

        Args:
            ticker: Stock ticker symbol.
            form_types: Tuple of form types to filter.
            limit: Maximum number of filings.

        Returns:
            List of Filing objects.
        """
        logger.info(f"Getting filings for {ticker}")

        cik = self.company_lookup.get_cik_from_ticker(ticker)
        filings = self.downloader.get_recent_filings(cik, form_types, limit)

        return filings

    def download_filing(
        self,
        filing: Filing,
        output_dir: Optional[Path] = None,
        include_exhibits: bool = False
    ) -> Dict[str, Any]:
        """
        Download a complete filing.

        Args:
            filing: Filing object to download.
            output_dir: Output directory.
            include_exhibits: Whether to include exhibits.

        Returns:
            Dictionary with download results:
                - filing_dir: Path to filing directory
                - files: List of downloaded files
                - file_count: Number of files downloaded
                - preferred_view: Path to recommended viewing file
        """
        logger.info(f"Downloading filing: {filing}")

        if output_dir is None:
            output_dir = self.config.output_dir

        files = self.downloader.download_filing(
            filing,
            output_dir,
            include_exhibits
        )

        filing_dir = output_dir / filing.accession
        preferred_view = self.downloader.get_preferred_view_file(filing_dir, filing)

        return {
            "filing_dir": filing_dir,
            "files": [str(f) for f in files],
            "file_count": len(files),
            "preferred_view": str(preferred_view) if preferred_view else None,
            "filing": filing,
        }

    def extract_tables(
        self,
        html_file: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Extract tables from HTML filing.

        Args:
            html_file: Path to HTML file.
            output_dir: Output directory for tables.

        Returns:
            Extraction results dictionary.
        """
        logger.info(f"Extracting tables from {html_file}")

        if output_dir is None:
            output_dir = html_file.parent / "tables"

        return self.table_extractor.extract(html_file, output_dir)

    def extract_sections(
        self,
        html_file: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Extract text sections from HTML filing.

        Args:
            html_file: Path to HTML file.
            output_dir: Output directory for sections.

        Returns:
            Extraction results dictionary.
        """
        logger.info(f"Extracting sections from {html_file}")

        if output_dir is None:
            output_dir = html_file.parent / "sections"

        return self.section_extractor.extract(html_file, output_dir)

    def extract_financials(
        self,
        cik: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Extract financial statements from company facts.

        Args:
            cik: 10-digit CIK string.
            output_dir: Output directory for statements.

        Returns:
            Extraction results dictionary.
        """
        logger.info(f"Extracting financial statements for CIK {cik}")

        return self.financial_extractor.extract(cik, output_dir)

    def process_filing_complete(
        self,
        filing: Filing,
        output_dir: Optional[Path] = None,
        include_exhibits: bool = False,
        extract_tables: bool = True,
        extract_sections: bool = True,
        extract_financials: bool = True
    ) -> Dict[str, Any]:
        """
        Complete filing processing: download and extract all data.

        Args:
            filing: Filing object to process.
            output_dir: Output directory.
            include_exhibits: Whether to include exhibits.
            extract_tables: Whether to extract tables.
            extract_sections: Whether to extract text sections.
            extract_financials: Whether to extract financial statements.

        Returns:
            Comprehensive results dictionary.
        """
        logger.info(f"Complete processing of filing: {filing}")

        results = {}

        # Download filing
        download_result = self.download_filing(filing, output_dir, include_exhibits)
        results["download"] = download_result

        filing_dir = download_result["filing_dir"]
        preferred_view = download_result.get("preferred_view")

        # Extract tables
        if extract_tables and preferred_view:
            try:
                tables_dir = filing_dir / "tables"
                tables_result = self.extract_tables(Path(preferred_view), tables_dir)
                results["tables"] = tables_result
            except Exception as e:
                logger.error(f"Table extraction failed: {e}")
                results["tables"] = {"error": str(e)}

        # Extract sections
        if extract_sections and preferred_view:
            try:
                sections_dir = filing_dir / "sections"
                sections_result = self.extract_sections(Path(preferred_view), sections_dir)
                results["sections"] = sections_result
            except Exception as e:
                logger.error(f"Section extraction failed: {e}")
                results["sections"] = {"error": str(e)}

        # Extract financials
        if extract_financials:
            try:
                facts_dir = filing_dir / "facts"
                financials_result = self.extract_financials(filing.cik, facts_dir)
                results["financials"] = financials_result
            except Exception as e:
                logger.error(f"Financial extraction failed: {e}")
                results["financials"] = {"error": str(e)}

        logger.info("Complete filing processing finished")
        return results

    def open_in_browser(self, file_path: Path) -> bool:
        """
        Open a file in the default web browser.

        Args:
            file_path: Path to file to open.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False

            uri = file_path.resolve().as_uri()
            webbrowser.open(uri)
            logger.info(f"Opened in browser: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to open in browser: {e}")
            return False

    def get_filing_urls(self, filing: Filing) -> Dict[str, str]:
        """
        Get URLs for a filing.

        Args:
            filing: Filing object.

        Returns:
            Dictionary of URLs.
        """
        return self.downloader.build_filing_urls(filing)

    def close(self):
        """Close all resources."""
        self.client.close()
        logger.info("FilingManager closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
