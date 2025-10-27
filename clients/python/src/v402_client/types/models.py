"""
Data models for v402 client.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from v402_client.types.enums import PaymentStatus, PaymentScheme, ChainType


class PaymentRequirements(BaseModel):
    """Payment requirements returned by server."""

    scheme: PaymentScheme
    network: str
    max_amount_required: str
    resource: str
    description: str
    mime_type: str
    pay_to: str
    max_timeout_seconds: int
    asset: str
    extra: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaymentResponse(BaseModel):
    """Response from a paid request."""

    status_code: int
    content: bytes
    headers: Dict[str, str]
    url: str

    # Payment information
    payment_made: bool = False
    payment_amount: Optional[str] = None
    transaction_hash: Optional[str] = None
    network: Optional[str] = None
    payer: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Performance metrics
    total_time: Optional[float] = None
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def json(self) -> Any:
        """Parse response as JSON."""
        import orjson
        return orjson.loads(self.content)

    def text(self) -> str:
        """Get response as text."""
        return self.content.decode("utf-8")


class PaymentHistory(BaseModel):
    """Record of a payment transaction."""

    payment_id: str = Field(..., description="Unique payment identifier")
    url: str
    amount: str
    transaction_hash: str
    network: str
    chain_type: ChainType
    payer: str
    payee: str
    timestamp: datetime
    status: PaymentStatus
    description: str
    scheme: PaymentScheme

    # Additional metadata
    block_number: Optional[int] = None
    gas_used: Optional[str] = None
    gas_price: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChainInfo(BaseModel):
    """Information about a blockchain network."""

    name: str
    type: ChainType
    chain_id: Optional[int]
    rpc_url: str
    native_currency: str
    explorer_url: Optional[str]
    is_connected: bool = False
    last_block: Optional[int] = None
    sync_status: Optional[str] = None


class PaymentStatistics(BaseModel):
    """Statistics about payments made."""

    total_payments: int
    successful_payments: int
    failed_payments: int
    total_amount: str
    average_amount: str
    min_amount: str
    max_amount: str
    unique_resources: int
    unique_networks: int
    time_period_start: datetime
    time_period_end: datetime

    # Per-network breakdown
    network_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class CircuitBreakerState(BaseModel):
    """Circuit breaker state information."""

    is_open: bool
    failure_count: int
    success_count: int
    last_failure_time: Optional[datetime]
    last_success_time: Optional[datetime]
    next_retry_time: Optional[datetime]


class HealthStatus(BaseModel):
    """Health status of the client."""

    is_healthy: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Component statuses
    http_client_healthy: bool = True
    chains_healthy: Dict[str, bool] = Field(default_factory=dict)
    facilitator_healthy: bool = True
    cache_healthy: bool = True

    # Resource usage
    active_connections: int = 0
    cache_size: int = 0
    memory_usage_mb: Optional[float] = None

    # Error information
    last_error: Optional[str] = None
    error_count: int = 0

