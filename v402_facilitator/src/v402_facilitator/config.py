"""
Configuration management for v402 Facilitator.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden by environment variables.
    """

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1

    # Blockchain configuration
    network: str = "base-sepolia"
    rpc_url: str = ""
    private_key: str = ""
    chain_id: int = 84532  # Base Sepolia

    # Database configuration
    database_url: str = "sqlite+aiosqlite:///./v402.db"

    # Security
    api_key: Optional[str] = None
    enable_rate_limit: bool = False
    rate_limit_per_minute: int = 60

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # x402 Protocol
    x402_version: int = 1
    supported_schemes: list[str] = ["exact"]

    # Settlement configuration
    settlement_gas_multiplier: float = 1.2
    settlement_retry_attempts: int = 3
    settlement_timeout: int = 300  # seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

