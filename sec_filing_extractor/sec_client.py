"""
SEC API client with rate limiting and retry logic.
"""
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .exceptions import APIError, RateLimitError, DownloadError


logger = logging.getLogger(__name__)


class SECClient:
    """
    Client for interacting with SEC EDGAR API.

    Handles rate limiting, retries, and provides a consistent interface
    for all SEC API interactions.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize SEC client.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self._last_request_time = 0
        self._session = self._create_session()
        logger.info("SEC Client initialized")

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.

        Returns:
            Configured requests Session object.
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(self.config.headers)

        return session

    def _rate_limit(self):
        """
        Enforce rate limiting between requests.

        Ensures minimum delay between consecutive requests.
        """
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.request_delay:
            sleep_time = self.config.request_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def get(self, url: str, params: Optional[Dict] = None, stream: bool = False) -> requests.Response:
        """
        Perform a GET request with rate limiting.

        Args:
            url: URL to request.
            params: Optional query parameters.
            stream: Whether to stream the response.

        Returns:
            Response object.

        Raises:
            APIError: If the request fails.
            RateLimitError: If rate limit is exceeded.
        """
        self._rate_limit()

        try:
            logger.debug(f"GET request: {url}")
            response = self._session.get(url, params=params, stream=stream, timeout=30)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise RateLimitError("SEC API rate limit exceeded") from e
            logger.error(f"HTTP error: {e}")
            raise APIError(f"SEC API request failed: {e}") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request to SEC API failed: {e}") from e

    def get_json(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform a GET request and parse JSON response.

        Args:
            url: URL to request.
            params: Optional query parameters.

        Returns:
            Parsed JSON data as dictionary.

        Raises:
            APIError: If the request fails or JSON parsing fails.
        """
        response = self.get(url, params=params)

        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON response from {url}")
            raise APIError(f"Invalid JSON response from SEC API") from e

    def download_file(
        self,
        url: str,
        dest_path: Path,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        Download a file from SEC with streaming.

        Args:
            url: URL of file to download.
            dest_path: Destination path for downloaded file.
            progress_callback: Optional callback function for progress updates.

        Returns:
            Path to downloaded file.

        Raises:
            DownloadError: If download fails.
        """
        # Ensure parent directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            response = self.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            logger.info(f"Downloading {url} to {dest_path}")

            downloaded = 0
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size:
                            progress_callback(downloaded, total_size)

            logger.info(f"Successfully downloaded {dest_path.name}")
            return dest_path

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            # Clean up partial download
            if dest_path.exists():
                dest_path.unlink()
            raise DownloadError(f"Failed to download file: {e}") from e

    def get_company_submissions(self, cik: str) -> Dict[str, Any]:
        """
        Get company submissions data from SEC API.

        Args:
            cik: 10-digit CIK string.

        Returns:
            Company submissions data.

        Raises:
            APIError: If request fails.
        """
        url = f"{self.config.sec_api_base}/submissions/CIK{cik}.json"
        logger.info(f"Fetching submissions for CIK {cik}")
        return self.get_json(url)

    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get company facts (XBRL data) from SEC API.

        Args:
            cik: 10-digit CIK string.

        Returns:
            Company facts data.

        Raises:
            APIError: If request fails.
        """
        url = f"{self.config.sec_api_base}/api/xbrl/companyfacts/CIK{cik}.json"
        logger.info(f"Fetching company facts for CIK {cik}")
        return self.get_json(url)

    def get_company_tickers(self) -> Dict[str, Any]:
        """
        Get mapping of ticker symbols to CIK numbers.

        Returns:
            Dictionary mapping tickers to company information.

        Raises:
            APIError: If request fails.
        """
        url = f"{self.config.sec_files_base}/files/company_tickers.json"
        logger.info("Fetching company tickers mapping")
        return self.get_json(url)

    def get_ticker_mapping_text(self) -> str:
        """
        Get text-based ticker to CIK mapping.

        Returns:
            Text content of ticker mapping file.

        Raises:
            APIError: If request fails.
        """
        url = f"{self.config.sec_files_base}/include/ticker.txt"
        logger.info("Fetching ticker mapping text file")
        response = self.get(url)
        return response.text

    def get_filing_index(self, cik_no_zeros: str, accession_no_dash: str) -> Dict[str, Any]:
        """
        Get filing index JSON for a specific filing.

        Args:
            cik_no_zeros: CIK without leading zeros.
            accession_no_dash: Accession number without dashes.

        Returns:
            Filing index data.

        Raises:
            APIError: If request fails.
        """
        url = (f"{self.config.sec_files_base}/Archives/edgar/data/"
               f"{cik_no_zeros}/{accession_no_dash}/index.json")
        logger.info(f"Fetching filing index for {accession_no_dash}")
        return self.get_json(url)

    def close(self):
        """Close the session."""
        self._session.close()
        logger.info("SEC Client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
