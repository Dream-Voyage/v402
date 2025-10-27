"""
Network-related exceptions.
"""

from typing import Optional
from v402_client.exceptions.base import V402Exception


class NetworkException(V402Exception):
    """Base exception for network errors."""

    pass


class ConnectionTimeout(NetworkException):
    """Raised when connection times out."""

    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        super().__init__(
            f"Connection to {url} timed out after {timeout}s",
            code="CONNECTION_TIMEOUT",
            details={"url": url, "timeout": timeout},
        )


class RequestFailed(NetworkException):
    """Raised when HTTP request fails."""

    def __init__(self, url: str, status_code: Optional[int], reason: str):
        self.url = url
        self.status_code = status_code
        self.reason = reason
        super().__init__(
            f"Request to {url} failed: {reason}",
            code="REQUEST_FAILED",
            details={"url": url, "status_code": status_code, "reason": reason},
        )


class TooManyRetries(NetworkException):
    """Raised when maximum retry attempts exceeded."""

    def __init__(self, url: str, attempts: int):
        self.url = url
        self.attempts = attempts
        super().__init__(
            f"Request to {url} failed after {attempts} attempts",
            code="TOO_MANY_RETRIES",
            details={"url": url, "attempts": attempts},
        )

