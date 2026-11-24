"""Custom exceptions for the FloodLock SDK."""

class FloodLockError(Exception):
    """Base exception for all FloodLock SDK errors."""
    pass

class APIError(FloodLockError):
    """Raised when the Cloudflare Edge API returns a non-200 HTTP response."""
    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body or {}

class AuthenticationError(APIError):
    """Raised when an invalid or revoked API key is provided."""
    pass

class RateLimitError(APIError):
    """Raised when daily quota or rate limit is exhausted."""
    pass
