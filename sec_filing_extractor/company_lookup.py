"""
Company lookup functionality for resolving tickers to CIK numbers.
"""
import logging
from typing import Optional, Dict

from .sec_client import SECClient
from .config import Config
from .exceptions import TickerNotFoundError, ValidationError


logger = logging.getLogger(__name__)


class CompanyLookup:
    """
    Handles company information lookup and ticker to CIK resolution.
    """

    def __init__(self, client: Optional[SECClient] = None, config: Optional[Config] = None):
        """
        Initialize company lookup.

        Args:
            client: SEC API client. If None, creates a new one.
            config: Configuration object.
        """
        self.config = config or Config()
        self.client = client or SECClient(self.config)
        self._ticker_cache: Dict[str, str] = {}
        logger.info("CompanyLookup initialized")

    def get_cik_from_ticker(self, ticker: str, use_cache: bool = True) -> str:
        """
        Resolve ticker symbol to 10-digit CIK.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').
            use_cache: Whether to use cached results.

        Returns:
            10-digit CIK string.

        Raises:
            TickerNotFoundError: If ticker cannot be resolved.
            ValidationError: If ticker format is invalid.
        """
        ticker = self._validate_ticker(ticker)

        # Check cache first
        if use_cache and ticker in self._ticker_cache:
            logger.debug(f"Using cached CIK for {ticker}")
            return self._ticker_cache[ticker]

        # Try JSON endpoint first
        cik = self._lookup_from_json(ticker)
        if cik:
            self._ticker_cache[ticker] = cik
            logger.info(f"Resolved {ticker} to CIK {cik}")
            return cik

        # Fallback to text mapping
        cik = self._lookup_from_text(ticker)
        if cik:
            self._ticker_cache[ticker] = cik
            logger.info(f"Resolved {ticker} to CIK {cik} (from text mapping)")
            return cik

        logger.error(f"Ticker not found: {ticker}")
        raise TickerNotFoundError(f"Ticker '{ticker}' not found in SEC database")

    def _validate_ticker(self, ticker: str) -> str:
        """
        Validate and normalize ticker symbol.

        Args:
            ticker: Raw ticker input.

        Returns:
            Normalized ticker (uppercase, stripped).

        Raises:
            ValidationError: If ticker is invalid.
        """
        if not ticker or not isinstance(ticker, str):
            raise ValidationError("Ticker must be a non-empty string")

        ticker = ticker.strip().upper()

        if not ticker:
            raise ValidationError("Ticker cannot be empty after stripping whitespace")

        if len(ticker) > 10:
            raise ValidationError("Ticker symbol too long (max 10 characters)")

        # Basic validation - letters and maybe a hyphen or period
        if not all(c.isalnum() or c in ('-', '.') for c in ticker):
            raise ValidationError(f"Invalid ticker format: {ticker}")

        return ticker

    def _lookup_from_json(self, ticker: str) -> Optional[str]:
        """
        Look up ticker in company_tickers.json.

        Args:
            ticker: Normalized ticker symbol.

        Returns:
            10-digit CIK string or None if not found.
        """
        try:
            data = self.client.get_company_tickers()

            # Data can be dict of indices or list
            rows = data.values() if isinstance(data, dict) else data

            for row in rows:
                if not isinstance(row, dict):
                    continue

                row_ticker = row.get("ticker", "").upper()
                if row_ticker == ticker:
                    cik_str = row.get("cik_str")
                    if cik_str is not None:
                        return f"{int(cik_str):010d}"

        except Exception as e:
            logger.warning(f"Failed to lookup from JSON: {e}")

        return None

    def _lookup_from_text(self, ticker: str) -> Optional[str]:
        """
        Look up ticker in ticker.txt mapping file.

        Args:
            ticker: Normalized ticker symbol.

        Returns:
            10-digit CIK string or None if not found.
        """
        try:
            text_content = self.client.get_ticker_mapping_text()

            for line in text_content.splitlines():
                if "|" not in line:
                    continue

                parts = line.split("|", 1)
                if len(parts) != 2:
                    continue

                file_ticker, cik = parts
                if file_ticker.upper() == ticker:
                    return f"{int(cik):010d}"

        except Exception as e:
            logger.warning(f"Failed to lookup from text file: {e}")

        return None

    def get_company_info(self, ticker: str) -> Dict[str, any]:
        """
        Get comprehensive company information.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Dictionary with company information including CIK, name, etc.

        Raises:
            TickerNotFoundError: If ticker cannot be resolved.
        """
        cik = self.get_cik_from_ticker(ticker)

        try:
            submissions = self.client.get_company_submissions(cik)

            return {
                "ticker": ticker,
                "cik": cik,
                "name": submissions.get("name", "Unknown"),
                "sic": submissions.get("sic"),
                "sic_description": submissions.get("sicDescription"),
                "category": submissions.get("category"),
                "fiscal_year_end": submissions.get("fiscalYearEnd"),
                "entity_type": submissions.get("entityType"),
                "state_of_incorporation": submissions.get("stateOfIncorporation"),
            }

        except Exception as e:
            logger.warning(f"Could not fetch full company info: {e}")
            return {
                "ticker": ticker,
                "cik": cik,
                "name": "Unknown",
            }

    def validate_cik(self, cik: str) -> str:
        """
        Validate and normalize CIK format.

        Args:
            cik: CIK string to validate.

        Returns:
            Normalized 10-digit CIK string.

        Raises:
            ValidationError: If CIK is invalid.
        """
        if not cik or not isinstance(cik, str):
            raise ValidationError("CIK must be a non-empty string")

        cik = cik.strip()

        try:
            cik_int = int(cik)
            if cik_int < 0:
                raise ValidationError("CIK cannot be negative")
            return f"{cik_int:010d}"

        except ValueError:
            raise ValidationError(f"Invalid CIK format: {cik}")

    def clear_cache(self):
        """Clear the ticker-to-CIK cache."""
        self._ticker_cache.clear()
        logger.info("Ticker cache cleared")
