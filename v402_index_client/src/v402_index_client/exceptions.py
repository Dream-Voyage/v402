"""
Exception classes for v402 Index Client.
"""


class PaymentException(Exception):
    """Base exception for payment-related errors."""

    pass


class PaymentLimitExceeded(PaymentException):
    """Raised when payment amount exceeds configured maximum."""

    def __init__(self, amount: str, max_amount: str):
        self.amount = amount
        self.max_amount = max_amount
        super().__init__(
            f"Payment amount {amount} exceeds maximum allowed {max_amount}"
        )


class PaymentFailed(PaymentException):
    """Raised when payment transaction fails."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Payment failed: {reason}")


class NetworkNotSupported(PaymentException):
    """Raised when requested network is not supported."""

    def __init__(self, network: str):
        self.network = network
        super().__init__(f"Network {network} is not supported")


class ContentNotAvailable(PaymentException):
    """Raised when content is not available even after payment."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Content at {url} is not available")


class InvalidPaymentResponse(PaymentException):
    """Raised when payment response is invalid."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid payment response: {reason}")

