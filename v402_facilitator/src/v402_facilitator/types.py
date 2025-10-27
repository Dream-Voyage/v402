"""
Type definitions for v402 Facilitator.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict


class VerifyRequest(BaseModel):
    """Request to verify a payment."""

    x402_version: int = Field(..., alias="x402Version")
    payment_payload: Dict[str, Any] = Field(..., alias="paymentPayload")
    payment_requirements: Dict[str, Any] = Field(..., alias="paymentRequirements")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class VerifyResponseModel(BaseModel):
    """Response from payment verification."""

    is_valid: bool = Field(..., alias="isValid")
    invalid_reason: Optional[str] = Field(None, alias="invalidReason")
    payer: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class SettleRequest(BaseModel):
    """Request to settle a payment."""

    x402_version: int = Field(..., alias="x402Version")
    payment_payload: Dict[str, Any] = Field(..., alias="paymentPayload")
    payment_requirements: Dict[str, Any] = Field(..., alias="paymentRequirements")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class SettleResponseModel(BaseModel):
    """Response from payment settlement."""

    success: bool
    error_reason: Optional[str] = Field(None, alias="errorReason")
    transaction: Optional[str] = None
    network: Optional[str] = None
    payer: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class SupportedKind(BaseModel):
    """Supported payment scheme and network combination."""

    scheme: str
    network: str


class SupportedResponse(BaseModel):
    """Response listing supported payment kinds."""

    kinds: list[SupportedKind]


class TransactionRecord(BaseModel):
    """Database record of a transaction."""

    id: Optional[int] = None
    transaction_hash: str
    payer: str
    payee: str
    amount: str
    network: str
    scheme: str
    resource: str
    timestamp: datetime
    status: str  # pending, confirmed, failed
    gas_used: Optional[str] = None
    block_number: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class DiscoveryResource(BaseModel):
    """Resource available for discovery."""

    resource: str
    type: str = "http"
    x402_version: int = Field(..., alias="x402Version")
    accepts: list[Dict[str, Any]]
    last_updated: datetime = Field(..., alias="lastUpdated")
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class DiscoveryPagination(BaseModel):
    """Pagination info for discovery results."""

    limit: int
    offset: int
    total: int


class DiscoveryResponse(BaseModel):
    """Response from discovery endpoint."""

    x402_version: int = Field(..., alias="x402Version")
    items: list[DiscoveryResource]
    pagination: DiscoveryPagination

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

