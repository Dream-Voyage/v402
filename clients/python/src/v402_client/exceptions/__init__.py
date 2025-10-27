"""
Exception hierarchy for v402 client.
"""

from v402_client.exceptions.base import V402Exception

__all__ = [
    "V402Exception",
    "PaymentException",
    "PaymentLimitExceeded",
    "PaymentVerificationFailed",
    "PaymentSettlementFailed",
    "InsufficientFunds",
    "ChainException",
    "UnsupportedChain",
    "ChainConnectionError",
    "InvalidTransaction",
    "NetworkException",
    "ConnectionTimeout",
    "RequestFailed",
]

