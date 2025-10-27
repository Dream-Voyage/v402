"""
Payment-related exceptions.
"""

from typing import Optional, Dict, Any
from v402_client.exceptions.base import V402Exception


class PaymentException(V402Exception):
    """Base exception for payment errors."""

    pass


class PaymentLimitExceeded(PaymentException):
    """Raised when payment amount exceeds configured maximum."""

    def __init__(self, amount: str, max_amount: str):
        self.amount = amount
        self.max_amount = max_amount
        super().__init__(
            f"Payment amount {amount} exceeds maximum {max_amount}",
            code="PAYMENT_LIMIT_EXCEEDED",
            details={"amount": amount, "max_amount": max_amount},
        )


class PaymentVerificationFailed(PaymentException):
    """Raised when payment verification fails."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        self.reason = reason
        super().__init__(
            f"Payment verification failed: {reason}",
            code="PAYMENT_VERIFICATION_FAILED",
            details=details or {"reason": reason},
        )


class PaymentSettlementFailed(PaymentException):
    """Raised when payment settlement on-chain fails."""

    def __init__(self, reason: str, transaction_hash: Optional[str] = None):
        self.reason = reason
        self.transaction_hash = transaction_hash
        super().__init__(
            f"Payment settlement failed: {reason}",
            code="PAYMENT_SETTLEMENT_FAILED",
            details={"reason": reason, "transaction_hash": transaction_hash},
        )


class InsufficientFunds(PaymentException):
    """Raised when account has insufficient funds for payment."""

    def __init__(self, required: str, available: str):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient funds: required {required}, available {available}",
            code="INSUFFICIENT_FUNDS",
            details={"required": required, "available": available},
        )


class PaymentExpired(PaymentException):
    """Raised when payment authorization has expired."""

    def __init__(self, expiry_time: str):
        self.expiry_time = expiry_time
        super().__init__(
            f"Payment authorization expired at {expiry_time}",
            code="PAYMENT_EXPIRED",
            details={"expiry_time": expiry_time},
        )


class InvalidPaymentScheme(PaymentException):
    """Raised when payment scheme is not supported."""

    def __init__(self, scheme: str, supported_schemes: list):
        self.scheme = scheme
        self.supported_schemes = supported_schemes
        super().__init__(
            f"Payment scheme '{scheme}' not supported. Supported: {supported_schemes}",
            code="INVALID_PAYMENT_SCHEME",
            details={"scheme": scheme, "supported_schemes": supported_schemes},
        )

