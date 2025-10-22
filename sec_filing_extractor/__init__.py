"""
SEC Filing Extractor - Download and extract data from SEC EDGAR filings.
"""
from .config import Config
from .sec_client import SECClient
from .company_lookup import CompanyLookup
from .filing_downloader import FilingDownloader, Filing
from .filing_manager import FilingManager
from .cli import CLI
from .exceptions import (
    SECFilingException,
    TickerNotFoundError,
    CIKNotFoundError,
    FilingNotFoundError,
    DownloadError,
    ExtractionError,
    APIError,
    RateLimitError,
    ValidationError,
)

__version__ = "2.0.0"
__author__ = "SEC Filing Extractor Contributors"

__all__ = [
    # Core classes
    "Config",
    "SECClient",
    "CompanyLookup",
    "FilingDownloader",
    "Filing",
    "FilingManager",
    "CLI",

    # Exceptions
    "SECFilingException",
    "TickerNotFoundError",
    "CIKNotFoundError",
    "FilingNotFoundError",
    "DownloadError",
    "ExtractionError",
    "APIError",
    "RateLimitError",
    "ValidationError",

    # Metadata
    "__version__",
    "__author__",
]
