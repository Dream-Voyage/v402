"""
Type definitions for v402 Index Client.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, List


class ClientConfig(BaseModel):
    """Configuration for the V402 Index Client."""

    private_key: str = Field(..., description="Private key for signing payments")
    max_amount_per_request: str = Field(
        default="1000000", description="Maximum payment amount per request in wei"
    )
    network: str = Field(default="base-sepolia", description="Blockchain network to use")
    facilitator_url: str = Field(
        default="http://localhost:8000", description="Facilitator service URL"
    )
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    auto_pay: bool = Field(
        default=True, description="Automatically pay when encountering 402 responses"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PaymentResponse(BaseModel):
    """Response object containing payment information and content."""

    status_code: int = Field(..., description="HTTP status code")
    content: bytes = Field(..., description="Response content")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    payment_made: bool = Field(default=False, description="Whether payment was made")
    payment_amount: Optional[str] = Field(None, description="Payment amount in wei")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    network: Optional[str] = Field(None, description="Network used for payment")
    url: str = Field(..., description="Requested URL")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def json(self) -> Any:
        """Parse content as JSON if possible."""
        import json

        return json.loads(self.content.decode("utf-8"))

    def text(self) -> str:
        """Get content as text."""
        return self.content.decode("utf-8")


class PaymentHistory(BaseModel):
    """Record of a payment transaction."""

    url: str = Field(..., description="URL that was accessed")
    amount: str = Field(..., description="Payment amount in wei")
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    network: str = Field(..., description="Network used")
    timestamp: datetime = Field(..., description="Payment timestamp")
    description: str = Field(..., description="Content description")
    payer: str = Field(..., description="Payer address")
    payee: str = Field(..., description="Payee address")
    success: bool = Field(..., description="Whether payment succeeded")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PaymentRequirementsInfo(BaseModel):
    """Information about payment requirements for a resource."""

    url: str = Field(..., description="Resource URL")
    payment_options: List[Dict[str, Any]] = Field(
        ..., description="Available payment options"
    )
    min_amount: str = Field(..., description="Minimum payment amount")
    max_amount: str = Field(..., description="Maximum payment amount")
    supported_networks: List[str] = Field(..., description="Supported blockchain networks")
    supported_schemes: List[str] = Field(..., description="Supported payment schemes")
    description: str = Field(..., description="Resource description")

    model_config = ConfigDict(arbitrary_types_allowed=True)

