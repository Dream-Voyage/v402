"""
Configuration management for v402 client.

This module provides comprehensive configuration management including
environment variables, config files, and programmatic configuration.
"""

import os
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any, List
from v402_client.types.enums import ChainType


class ChainConfig(BaseSettings):
    """Configuration for a specific blockchain network."""

    name: str = Field(..., description="Chain name (e.g., 'ethereum', 'base')")
    type: ChainType = Field(..., description="Chain type (EVM, Solana, etc.)")
    rpc_url: str = Field(..., description="RPC endpoint URL")
    chain_id: Optional[int] = Field(None, description="Chain ID (for EVM chains)")
    native_currency: str = Field(default="ETH", description="Native currency symbol")
    explorer_url: Optional[str] = Field(None, description="Block explorer URL")

    # Advanced settings
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    gas_multiplier: float = Field(default=1.2, description="Gas price multiplier")

    model_config = SettingsConfigDict(
        env_prefix="V402_CHAIN_",
        case_sensitive=False,
    )

    @field_validator("rpc_url")
    @classmethod
    def validate_rpc_url(cls, v: str) -> str:
        """Validate RPC URL format."""
        if not v.startswith(("http://", "https://", "wss://", "ws://")):
            raise ValueError("RPC URL must start with http://, https://, ws://, or wss://")
        return v

    @field_validator("gas_multiplier")
    @classmethod
    def validate_gas_multiplier(cls, v: float) -> float:
        """Validate gas multiplier is reasonable."""
        if not (0.5 <= v <= 5.0):
            raise ValueError("Gas multiplier must be between 0.5 and 5.0")
        return v

    @staticmethod
    def ethereum(mainnet: bool = True) -> "ChainConfig":
        """Create Ethereum chain configuration."""
        return ChainConfig(
            name="ethereum",
            type=ChainType.EVM,
            rpc_url=os.getenv(
                "ETH_RPC_URL",
                "https://eth-mainnet.g.alchemy.com/v2/demo" if mainnet else "https://eth-sepolia.g.alchemy.com/v2/demo"
            ),
            chain_id=1 if mainnet else 11155111,
            native_currency="ETH",
            explorer_url="https://etherscan.io" if mainnet else "https://sepolia.etherscan.io",
        )

    @staticmethod
    def base(mainnet: bool = True) -> "ChainConfig":
        """Create Base chain configuration."""
        return ChainConfig(
            name="base",
            type=ChainType.EVM,
            rpc_url=os.getenv(
                "BASE_RPC_URL",
                "https://mainnet.base.org" if mainnet else "https://sepolia.base.org"
            ),
            chain_id=8453 if mainnet else 84532,
            native_currency="ETH",
            explorer_url="https://basescan.org" if mainnet else "https://sepolia.basescan.org",
        )

    @staticmethod
    def polygon(mainnet: bool = True) -> "ChainConfig":
        """Create Polygon chain configuration."""
        return ChainConfig(
            name="polygon",
            type=ChainType.EVM,
            rpc_url=os.getenv(
                "POLYGON_RPC_URL",
                "https://polygon-rpc.com" if mainnet else "https://rpc-mumbai.maticvigil.com"
            ),
            chain_id=137 if mainnet else 80001,
            native_currency="MATIC",
            explorer_url="https://polygonscan.com" if mainnet else "https://mumbai.polygonscan.com",
        )

    @staticmethod
    def bsc(mainnet: bool = True) -> "ChainConfig":
        """Create BSC chain configuration."""
        return ChainConfig(
            name="bsc",
            type=ChainType.EVM,
            rpc_url=os.getenv(
                "BSC_RPC_URL",
                "https://bsc-dataseed1.binance.org" if mainnet else "https://data-seed-prebsc-1-s1.binance.org:8545"
            ),
            chain_id=56 if mainnet else 97,
            native_currency="BNB",
            explorer_url="https://bscscan.com" if mainnet else "https://testnet.bscscan.com",
        )

    @staticmethod
    def solana(mainnet: bool = True) -> "ChainConfig":
        """Create Solana chain configuration."""
        return ChainConfig(
            name="solana",
            type=ChainType.SOLANA,
            rpc_url=os.getenv(
                "SOLANA_RPC_URL",
                "https://api.mainnet-beta.solana.com" if mainnet else "https://api.devnet.solana.com"
            ),
            native_currency="SOL",
            explorer_url="https://explorer.solana.com",
        )


class ResilienceConfig(BaseSettings):
    """Configuration for resilience patterns (circuit breaker, retry, etc.)."""

    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker")
    failure_threshold: int = Field(default=5, description="Failures before opening circuit")
    success_threshold: int = Field(default=2, description="Successes to close circuit")
    timeout: int = Field(default=30, description="Circuit breaker timeout in seconds")

    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff: float = Field(default=2.0, description="Exponential backoff multiplier")
    retry_jitter: bool = Field(default=True, description="Add jitter to retry delays")

    model_config = SettingsConfigDict(
        env_prefix="V402_RESILIENCE_",
        case_sensitive=False,
    )


class LoggingConfig(BaseSettings):
    """Configuration for logging."""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format (json, text)")
    output: str = Field(default="stdout", description="Log output (stdout, file)")
    file_path: Optional[str] = Field(None, description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size (10MB)")
    backup_count: int = Field(default=5, description="Number of backup files")

    model_config = SettingsConfigDict(
        env_prefix="V402_LOG_",
        case_sensitive=False,
    )


class MetricsConfig(BaseSettings):
    """Configuration for metrics and monitoring."""

    enabled: bool = Field(default=True, description="Enable metrics collection")
    port: int = Field(default=9090, description="Metrics server port")
    path: str = Field(default="/metrics", description="Metrics endpoint path")
    include_labels: bool = Field(default=True, description="Include detailed labels")

    model_config = SettingsConfigDict(
        env_prefix="V402_METRICS_",
        case_sensitive=False,
    )


class ClientSettings(BaseSettings):
    """Main client configuration."""

    private_key: str = Field(..., description="Private key for signing transactions")
    chains: List[ChainConfig] = Field(default_factory=list, description="Supported chains")

    # Payment settings
    auto_pay: bool = Field(default=True, description="Automatically handle payments")
    max_amount_per_request: str = Field(default="1000000", description="Max payment in wei")

    # HTTP settings
    timeout: int = Field(default=30, description="HTTP timeout in seconds")
    max_connections: int = Field(default=100, description="Max HTTP connections")
    keep_alive: bool = Field(default=True, description="Keep HTTP connections alive")

    # Facilitator settings
    facilitator_url: str = Field(
        default="https://facilitator.v402.org",
        description="Facilitator service URL"
    )

    # Advanced settings
    resilience: ResilienceConfig = Field(default_factory=ResilienceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)

    # Cache settings
    enable_cache: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Max cache entries")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="V402_",
        case_sensitive=False,
        extra="allow",
    )

    @field_validator("private_key")
    @classmethod
    def validate_private_key(cls, v: str) -> str:
        """Validate private key format."""
        if not v.startswith("0x"):
            v = "0x" + v
        if len(v) != 66:  # 0x + 64 hex chars
            raise ValueError("Private key must be 32 bytes (64 hex characters)")
        return v

    @field_validator("max_amount_per_request")
    @classmethod
    def validate_max_amount(cls, v: str) -> str:
        """Validate max amount is a valid integer string."""
        try:
            int(v)
        except ValueError:
            raise ValueError("max_amount_per_request must be a valid integer string")
        return v

    @model_validator(mode="after")
    def validate_chains(self) -> "ClientSettings":
        """Validate at least one chain is configured."""
        if not self.chains:
            # Add default chains if none specified
            self.chains = [
                ChainConfig.ethereum(mainnet=False),
                ChainConfig.base(mainnet=False),
            ]
        return self

    @classmethod
    def from_yaml(cls, path: str) -> "ClientSettings":
        """Load settings from YAML file."""
        import yaml
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientSettings":
        """Create settings from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump(mode="json")

