"""
v402 Index Client - Payment client SDK for AI/crawler platforms.

This module provides a high-level client for AI platforms and crawlers to
automatically handle micropayments when accessing premium content.
"""

from v402_index_client.client import V402IndexClient

__version__ = "0.1.0"

__all__ = [
    "V402IndexClient",
    "PaymentResponse",
    "PaymentHistory",
    "ClientConfig",
    "PaymentException",
    "PaymentLimitExceeded",
    "PaymentFailed",
    "NetworkNotSupported",
]

