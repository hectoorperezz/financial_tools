"""
Custom exceptions for the SEC Filing Extractor.
"""


class SECFilingException(Exception):
    """Base exception for SEC filing operations."""
    pass


class TickerNotFoundError(SECFilingException):
    """Raised when a ticker symbol cannot be found."""
    pass


class CIKNotFoundError(SECFilingException):
    """Raised when a CIK cannot be found."""
    pass


class FilingNotFoundError(SECFilingException):
    """Raised when a filing cannot be found."""
    pass


class DownloadError(SECFilingException):
    """Raised when a download operation fails."""
    pass


class ExtractionError(SECFilingException):
    """Raised when data extraction fails."""
    pass


class APIError(SECFilingException):
    """Raised when SEC API returns an error."""
    pass


class RateLimitError(SECFilingException):
    """Raised when SEC API rate limit is exceeded."""
    pass


class ValidationError(SECFilingException):
    """Raised when input validation fails."""
    pass
