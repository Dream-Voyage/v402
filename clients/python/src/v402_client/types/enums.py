"""
Enumeration types for v402 client.
"""

from enum import Enum


class ChainType(str, Enum):
    """Blockchain network type."""

    EVM = "evm"
    SOLANA = "solana"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class PaymentStatus(str, Enum):
    """Payment transaction status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"


class PaymentScheme(str, Enum):
    """Payment scheme type."""

    EXACT = "exact"
    UPTO = "upto"
    DYNAMIC = "dynamic"


class NetworkEnvironment(str, Enum):
    """Network environment."""

    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"
    LOCAL = "local"


class LogLevel(str, Enum):
    """Logging level."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheStrategy(str, Enum):
    """Cache eviction strategy."""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    RANDOM = "random"


class RetryStrategy(str, Enum):
    """Retry backoff strategy."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"
    FIBONACCI = "fibonacci"

