"""
Custom exceptions for langchain-hreflang package.
"""


class HreflangAPIError(Exception):
    """Base exception for Hreflang API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class HreflangAuthenticationError(HreflangAPIError):
    """Raised when API key is invalid or missing."""
    pass


class HreflangRateLimitError(HreflangAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class HreflangTestTimeoutError(HreflangAPIError):
    """Raised when test takes too long to complete."""
    pass


class HreflangInvalidURLError(HreflangAPIError):
    """Raised when provided URLs are invalid."""
    pass