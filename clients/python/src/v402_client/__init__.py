"""
v402 Python Client - Enterprise-grade multi-chain payment client.

This package provides a comprehensive client for the v402 payment protocol,
supporting multiple blockchain networks including EVM chains, Solana, BSC, and Polygon.
"""

from v402_client.core.async_client import AsyncV402Client
from v402_client.config.settings import ClientSettings, ChainConfig
from v402_client.types.models import PaymentResponse, PaymentHistory

__version__ = "1.0.0"

__all__ = [
    # Core clients
    "V402Client",
    "AsyncV402Client",
    # Configuration
    "ClientSettings",
    "ChainConfig",
    # Models
    "PaymentResponse",
    "PaymentHistory",
    # Enums
    "ChainType",
    "PaymentStatus",
    # Exceptions
    "V402Exception",
    "PaymentException",
    "PaymentLimitExceeded",
    "PaymentVerificationFailed",
    "ChainException",
    "UnsupportedChain",
]

