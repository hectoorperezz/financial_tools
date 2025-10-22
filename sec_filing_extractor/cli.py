"""
Command-line interface for SEC Filing Extractor.
"""
import logging
from pathlib import Path
from typing import Optional

from .config import Config
from .filing_manager import FilingManager
from .filing_downloader import Filing
from .exceptions import SECFilingException


logger = logging.getLogger(__name__)


class CLI:
    """
    Interactive command-line interface for SEC Filing Extractor.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize CLI.

        Args:
            config: Configuration object.
        """
        self.config = config or Config()
        self.manager = FilingManager(self.config)
        logger.info("CLI initialized")

    def run(self):
        """Run the interactive CLI."""
        print("=" * 70)
        print("SEC Filing Extractor - Interactive CLI")
        print("=" * 70)
        print()

        try:
            # Get ticker from user
            ticker = self._get_ticker()
            if not ticker:
                print("No ticker provided. Exiting.")
                return

            # Get company info
            print(f"\nLooking up {ticker}...")
            try:
                company_info = self.manager.search_company(ticker)
                self._print_company_info(company_info)
            except SECFilingException as e:
                print(f"Error: {e}")
                return

            # Get filings
            print(f"\nFetching recent filings...")
            try:
                filings = self.manager.get_filings(ticker)
                self._print_filings(filings)
            except SECFilingException as e:
                print(f"Error: {e}")
                return

            # Select filing
            filing = self._select_filing(filings)
            if not filing:
                print("No filing selected. Exiting.")
                return

            # Show filing details
            self._print_filing_details(filing)

            # Download filing
            if self._confirm("Download this filing?"):
                include_exhibits = self._confirm("Include exhibits?", default=False)
                self._download_and_process(filing, include_exhibits)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting.")
        except Exception as e:
            logger.exception("Unexpected error in CLI")
            print(f"\nUnexpected error: {e}")
        finally:
            self.manager.close()

    def _get_ticker(self) -> Optional[str]:
        """
        Get ticker from user input.

        Returns:
            Ticker symbol or None.
        """
        ticker = input("Enter ticker symbol (e.g., AAPL): ").strip()
        return ticker if ticker else None

    def _print_company_info(self, info: dict):
        """Print company information."""
        print("\n" + "=" * 70)
        print("COMPANY INFORMATION")
        print("=" * 70)
        print(f"Ticker:        {info.get('ticker', 'N/A')}")
        print(f"Name:          {info.get('name', 'N/A')}")
        print(f"CIK:           {info.get('cik', 'N/A')}")
        print(f"SIC:           {info.get('sic', 'N/A')}")
        print(f"Industry:      {info.get('sic_description', 'N/A')}")
        print(f"Fiscal Year:   {info.get('fiscal_year_end', 'N/A')}")
        print(f"Entity Type:   {info.get('entity_type', 'N/A')}")
        print("=" * 70)

    def _print_filings(self, filings: list):
        """Print list of filings."""
        print("\n" + "=" * 70)
        print("RECENT FILINGS")
        print("=" * 70)
        for idx, filing in enumerate(filings, 1):
            print(f"{idx:3d}. {filing.form:8s} | {filing.filing_date} | {filing.accession}")
        print("=" * 70)

    def _select_filing(self, filings: list) -> Optional[Filing]:
        """
        Let user select a filing.

        Args:
            filings: List of Filing objects.

        Returns:
            Selected Filing or None.
        """
        while True:
            choice = input(f"\nSelect filing [1-{len(filings)}] (Enter for 1): ").strip()

            if not choice:
                return filings[0]

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            idx = int(choice) - 1
            if 0 <= idx < len(filings):
                return filings[idx]

            print(f"Please enter a number between 1 and {len(filings)}.")

    def _print_filing_details(self, filing: Filing):
        """Print filing details."""
        urls = self.manager.get_filing_urls(filing)

        print("\n" + "=" * 70)
        print("FILING DETAILS")
        print("=" * 70)
        print(f"Form Type:         {filing.form}")
        print(f"Filing Date:       {filing.filing_date}")
        print(f"Accession:         {filing.accession}")
        print(f"Primary Document:  {filing.primary_doc}")
        print(f"\nURLs:")
        print(f"  Primary Doc:     {urls['primary_doc']}")
        print(f"  Index JSON:      {urls['index_json']}")
        print(f"  Filing Page:     {urls['filing_page']}")
        print("=" * 70)

    def _download_and_process(self, filing: Filing, include_exhibits: bool):
        """
        Download and process a filing.

        Args:
            filing: Filing to download.
            include_exhibits: Whether to include exhibits.
        """
        print("\nDownloading filing... This may take a few minutes.")

        try:
            result = self.manager.download_filing(filing, include_exhibits=include_exhibits)

            print(f"\n✓ Downloaded {result['file_count']} files to: {result['filing_dir']}")

            preferred_view = result.get('preferred_view')
            if preferred_view:
                print(f"✓ Recommended viewing file: {Path(preferred_view).name}")

                # Offer to open in browser
                if self._confirm("\nOpen in browser?", default=False):
                    self.manager.open_in_browser(Path(preferred_view))

                # Offer to extract tables
                if self._confirm("\nExtract tables to CSV?", default=True):
                    print("Extracting tables...")
                    tables_result = self.manager.extract_tables(Path(preferred_view))
                    print(f"✓ Extracted {tables_result['table_count']} tables")
                    if tables_result.get('json_file'):
                        print(f"  JSON: {Path(tables_result['json_file']).name}")

                # Offer to extract sections
                if self._confirm("\nExtract text sections to Markdown?", default=True):
                    print("Extracting sections...")
                    sections_result = self.manager.extract_sections(Path(preferred_view))
                    print(f"✓ Extracted {sections_result['section_count']} sections")
                    if sections_result.get('index_file'):
                        print(f"  Index: {Path(sections_result['index_file']).name}")

            # Offer to extract financials
            if self._confirm("\nExtract financial statements (XBRL)?", default=True):
                print("Extracting financial statements...")
                facts_dir = result['filing_dir'] / "facts"
                financials_result = self.manager.extract_financials(filing.cik, facts_dir)
                print(f"✓ Extracted {financials_result['statement_count']} statements")
                for stmt, path in financials_result.items():
                    if stmt not in ['statement_count', 'cik', 'raw_json']:
                        print(f"  {stmt}: {Path(path).name}")

            print("\n" + "=" * 70)
            print("PROCESSING COMPLETE")
            print("=" * 70)
            print(f"All files saved to: {result['filing_dir']}")

        except SECFilingException as e:
            print(f"\n✗ Error: {e}")
        except Exception as e:
            logger.exception("Error during download and processing")
            print(f"\n✗ Unexpected error: {e}")

    def _confirm(self, message: str, default: bool = True) -> bool:
        """
        Get yes/no confirmation from user.

        Args:
            message: Prompt message.
            default: Default value if user just presses Enter.

        Returns:
            True for yes, False for no.
        """
        suffix = "(Y/n)" if default else "(y/N)"
        while True:
            response = input(f"{message} {suffix}: ").strip().lower()

            if not response:
                return default

            if response in ('y', 'yes'):
                return True

            if response in ('n', 'no'):
                return False

            print("Please answer 'y' or 'n'.")

    def run_quick(self, ticker: str, form_type: str = "10-K", download: bool = True):
        """
        Quick non-interactive mode.

        Args:
            ticker: Stock ticker symbol.
            form_type: Form type to download.
            download: Whether to download and process.
        """
        try:
            print(f"Processing {ticker} - {form_type}")

            # Get company and filings
            company_info = self.manager.search_company(ticker)
            print(f"Company: {company_info['name']} (CIK: {company_info['cik']})")

            filings = self.manager.get_filings(ticker, form_types=(form_type,), limit=1)
            if not filings:
                print(f"No {form_type} filings found.")
                return

            filing = filings[0]
            print(f"Latest {form_type}: {filing.filing_date} - {filing.accession}")

            if download:
                print("Downloading and processing...")
                result = self.manager.process_filing_complete(
                    filing,
                    extract_tables=True,
                    extract_sections=True,
                    extract_financials=True
                )
                print(f"✓ Complete. Files saved to: {result['download']['filing_dir']}")

        except SECFilingException as e:
            print(f"Error: {e}")
        except Exception as e:
            logger.exception("Error in quick mode")
            print(f"Unexpected error: {e}")
        finally:
            self.manager.close()
