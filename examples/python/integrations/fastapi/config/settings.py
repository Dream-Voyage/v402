"""
FastAPI Configuration and Settings
"""

from pydantic import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    app_name: str = "v402 FastAPI Integration"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Database Configuration
    database_url: str = "sqlite:///./v402.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # v402 Configuration
    v402_base_url: str = "https://api.v402.network"
    v402_timeout: int = 30
    v402_retry_count: int = 3

    # Blockchain Configuration
    chain_id: int = 1  # Ethereum mainnet
    rpc_url: str = "https://mainnet.infura.io/v3/your-project-id"
    contract_address: str = "0x1234567890abcdef1234567890abcdef12345678"

    # Payment Configuration
    default_currency: str = "USDC"
    gas_limit: int = 100000
    gas_price: str = "20000000000"  # 20 gwei

    # Security Configuration
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Monitoring Configuration
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check: bool = True

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Cache Configuration
    cache_ttl: int = 300  # seconds
    cache_max_size: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
