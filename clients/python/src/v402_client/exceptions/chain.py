"""
Blockchain-related exceptions.
"""

from typing import Optional
from v402_client.exceptions.base import V402Exception


class ChainException(V402Exception):
    """Base exception for blockchain errors."""

    pass


class UnsupportedChain(ChainException):
    """Raised when blockchain network is not supported."""

    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        super().__init__(
            f"Chain '{chain_name}' is not supported",
            code="UNSUPPORTED_CHAIN",
            details={"chain_name": chain_name},
        )


class ChainConnectionError(ChainException):
    """Raised when connection to blockchain fails."""

    def __init__(self, chain_name: str, reason: str):
        self.chain_name = chain_name
        self.reason = reason
        super().__init__(
            f"Failed to connect to {chain_name}: {reason}",
            code="CHAIN_CONNECTION_ERROR",
            details={"chain_name": chain_name, "reason": reason},
        )


class InvalidTransaction(ChainException):
    """Raised when transaction is invalid."""

    def __init__(self, reason: str, transaction_data: Optional[dict] = None):
        self.reason = reason
        self.transaction_data = transaction_data
        super().__init__(
            f"Invalid transaction: {reason}",
            code="INVALID_TRANSACTION",
            details={"reason": reason, "transaction": transaction_data},
        )


class TransactionFailed(ChainException):
    """Raised when transaction execution fails."""

    def __init__(self, transaction_hash: str, reason: str):
        self.transaction_hash = transaction_hash
        self.reason = reason
        super().__init__(
            f"Transaction {transaction_hash} failed: {reason}",
            code="TRANSACTION_FAILED",
            details={"transaction_hash": transaction_hash, "reason": reason},
        )

