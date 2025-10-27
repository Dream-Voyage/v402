"""
Advanced configuration management for v402 facilitator.

This module provides comprehensive configuration management with multiple sources,
environment-specific settings, and runtime configuration validation.
"""

import secrets
from enum import Enum
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict, List, Optional


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels."""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    # PostgreSQL Main Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "v402"
    POSTGRES_PASSWORD: str = "v402"
    POSTGRES_DB: str = "v402_facilitator"
    POSTGRES_MAX_CONNECTIONS: int = 20
    POSTGRES_MIN_CONNECTIONS: int = 5
    POSTGRES_CONNECTION_TIMEOUT: int = 30
    POSTGRES_ECHO: bool = False

    # Redis Cache & Session Store
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_CONNECTION_TIMEOUT: int = 10
    REDIS_CLUSTER_MODE: bool = False

    # MongoDB Analytics Database
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_DB: str = "v402_analytics"
    MONGODB_MAX_CONNECTIONS: int = 100

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        auth = ""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            auth = f"{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@"
        return f"mongodb://{auth}{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""

    # JWT Configuration
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # API Keys
    API_KEY_LENGTH: int = 32
    API_KEY_PREFIX: str = "v402_"

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]

    # SSL/TLS Configuration
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    SSL_VERIFY_MODE: bool = True

    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class BlockchainConfig(BaseSettings):
    """Blockchain network configuration."""

    # Ethereum Configuration
    ETHEREUM_RPC_URL: str = "https://eth-mainnet.g.alchemy.com/v2/demo"
    ETHEREUM_CHAIN_ID: int = 1
    ETHEREUM_GAS_LIMIT: int = 21000
    ETHEREUM_GAS_PRICE_MULTIPLIER: float = 1.2
    ETHEREUM_CONFIRMATION_BLOCKS: int = 3

    # Base Configuration
    BASE_RPC_URL: str = "https://mainnet.base.org"
    BASE_CHAIN_ID: int = 8453
    BASE_GAS_LIMIT: int = 21000
    BASE_GAS_PRICE_MULTIPLIER: float = 1.1
    BASE_CONFIRMATION_BLOCKS: int = 1

    # Polygon Configuration
    POLYGON_RPC_URL: str = "https://polygon-rpc.com"
    POLYGON_CHAIN_ID: int = 137
    POLYGON_GAS_LIMIT: int = 21000
    POLYGON_GAS_PRICE_MULTIPLIER: float = 1.3
    POLYGON_CONFIRMATION_BLOCKS: int = 20

    # Arbitrum Configuration
    ARBITRUM_RPC_URL: str = "https://arb1.arbitrum.io/rpc"
    ARBITRUM_CHAIN_ID: int = 42161
    ARBITRUM_GAS_LIMIT: int = 21000
    ARBITRUM_GAS_PRICE_MULTIPLIER: float = 1.0
    ARBITRUM_CONFIRMATION_BLOCKS: int = 1

    # Optimism Configuration
    OPTIMISM_RPC_URL: str = "https://mainnet.optimism.io"
    OPTIMISM_CHAIN_ID: int = 10
    OPTIMISM_GAS_LIMIT: int = 21000
    OPTIMISM_GAS_PRICE_MULTIPLIER: float = 1.0
    OPTIMISM_CONFIRMATION_BLOCKS: int = 1

    # BSC Configuration
    BSC_RPC_URL: str = "https://bsc-dataseed1.binance.org"
    BSC_CHAIN_ID: int = 56
    BSC_GAS_LIMIT: int = 21000
    BSC_GAS_PRICE_MULTIPLIER: float = 1.1
    BSC_CONFIRMATION_BLOCKS: int = 10

    # Solana Configuration
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_COMMITMENT: str = "confirmed"
    SOLANA_CONFIRMATION_BLOCKS: int = 32

    # General Blockchain Settings
    SUPPORTED_CHAINS: List[str] = [
        "ethereum", "base", "polygon", "arbitrum", "optimism", "bsc", "solana"
    ]
    DEFAULT_CHAIN: str = "ethereum"
    CHAIN_HEALTH_CHECK_INTERVAL: int = 30
    TRANSACTION_TIMEOUT: int = 300
    MAX_GAS_PRICE: str = "100000000000"  # 100 gwei in wei


class PaymentConfig(BaseSettings):
    """Payment processing configuration."""

    # Payment Limits
    MIN_PAYMENT_AMOUNT: str = "1000000000000000"  # 0.001 ETH in wei
    MAX_PAYMENT_AMOUNT: str = "10000000000000000000"  # 10 ETH in wei
    DEFAULT_PAYMENT_TIMEOUT: int = 900  # 15 minutes

    # Fee Configuration
    FACILITATOR_FEE_PERCENTAGE: float = 0.025  # 2.5%
    MIN_FACILITATOR_FEE: str = "1000000000000000"  # 0.001 ETH
    MAX_FACILITATOR_FEE: str = "100000000000000000"  # 0.1 ETH

    # Payment Processing
    PAYMENT_BATCH_SIZE: int = 100
    PAYMENT_PROCESSING_INTERVAL: int = 10
    FAILED_PAYMENT_RETRY_COUNT: int = 3
    FAILED_PAYMENT_RETRY_DELAY: int = 60

    # Settlement Configuration
    SETTLEMENT_BATCH_SIZE: int = 50
    SETTLEMENT_INTERVAL: int = 300  # 5 minutes
    SETTLEMENT_CONFIRMATION_BLOCKS: int = 3

    @validator("MIN_PAYMENT_AMOUNT", "MAX_PAYMENT_AMOUNT")
    def validate_amounts(cls, v):
        try:
            int(v)
            return v
        except ValueError:
            raise ValueError("Payment amounts must be valid integers in wei")


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""

    # Metrics Configuration
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    METRICS_NAMESPACE: str = "v402_facilitator"

    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30
    HEALTH_CHECK_TIMEOUT: int = 10
    HEALTH_CHECK_RETRIES: int = 3

    # Sentry Configuration
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_SAMPLE_RATE: float = 1.0

    # OpenTelemetry Configuration
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "v402-facilitator"
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = "midnight"
    LOG_RETENTION: int = 30  # days


class APIConfig(BaseSettings):
    """API server configuration."""

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    RELOAD: bool = False

    # API Versioning
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    # Request Configuration
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT: int = 30

    # Response Configuration
    RESPONSE_COMPRESSION: bool = True
    RESPONSE_CACHE_TTL: int = 300  # 5 minutes

    # Documentation Configuration
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_TITLE: str = "v402 Facilitator API"
    DOCS_DESCRIPTION: str = """
    ## v402 Facilitator API
    
    Enterprise-grade payment facilitation service for the v402 protocol.
    
    ### Features:
    - Multi-chain payment processing
    - Content provider management  
    - Analytics and reporting
    - Real-time payment tracking
    - Webhook notifications
    """


class CacheConfig(BaseSettings):
    """Caching configuration."""

    # Cache Backends
    CACHE_BACKEND: str = "redis"  # redis, memory, dummy
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000

    # Specific Cache Settings
    PAYMENT_CACHE_TTL: int = 900  # 15 minutes
    PRODUCT_CACHE_TTL: int = 1800  # 30 minutes
    USER_CACHE_TTL: int = 600  # 10 minutes
    ANALYTICS_CACHE_TTL: int = 3600  # 1 hour

    # Cache Invalidation
    CACHE_INVALIDATION_ENABLED: bool = True
    CACHE_SOFT_INVALIDATION: bool = True


class QueueConfig(BaseSettings):
    """Message queue configuration."""

    # Queue Backend
    QUEUE_BACKEND: str = "redis"  # redis, rabbitmq, sqs
    QUEUE_DEFAULT_PRIORITY: int = 5
    QUEUE_MAX_RETRIES: int = 3

    # Queue Names
    PAYMENT_QUEUE: str = "payment_processing"
    SETTLEMENT_QUEUE: str = "settlement_processing"
    NOTIFICATION_QUEUE: str = "notifications"
    ANALYTICS_QUEUE: str = "analytics_processing"

    # Worker Configuration
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_TASK_SOFT_TIME_LIMIT: int = 240


class NotificationConfig(BaseSettings):
    """Notification system configuration."""

    # Webhook Configuration
    WEBHOOK_ENABLED: bool = True
    WEBHOOK_MAX_RETRIES: int = 5
    WEBHOOK_RETRY_DELAY: int = 60
    WEBHOOK_TIMEOUT: int = 30

    # Email Configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAIL_FROM: Optional[str] = None

    # SMS Configuration
    SMS_PROVIDER: Optional[str] = None  # twilio, aws_sns
    SMS_API_KEY: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application Information
    APP_NAME: str = "v402 Facilitator"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise payment facilitation service for v402 protocol"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # Component Configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    blockchain: BlockchainConfig = Field(default_factory=BlockchainConfig)
    payment: PaymentConfig = Field(default_factory=PaymentConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)

    # Runtime Configuration
    STARTUP_BANNER: bool = True
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 30

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v == Environment.PRODUCTION:
            # Additional production validations
            pass
        return v

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.model_dump()

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings
