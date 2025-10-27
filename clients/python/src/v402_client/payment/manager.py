"""
Payment manager for v402 client.
"""

import os
import sys
from eth_account import Account
from typing import List, Dict, Any

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../x402/src"))

from x402.types import PaymentRequirements as X402PaymentRequirements
from x402.clients.base import x402Client


class PaymentManager:
    """Manages payment processing and x402 integration."""

    def __init__(self, private_key: str, chains, max_amount: str, facilitator_url: str, logger):
        self.private_key = private_key
        self.chains = chains
        self.max_amount = max_amount
        self.facilitator_url = facilitator_url
        self.logger = logger
        self.account = Account.from_key(private_key)
        self.x402_client = None

    async def initialize(self):
        """Initialize payment manager."""
        self.x402_client = x402Client(
            account=self.account,
            max_value=int(self.max_amount),
        )
        self.logger.info("Payment manager initialized")

    async def select_payment_requirements(
        self,
        accepts: List[X402PaymentRequirements],
        url: str
    ) -> X402PaymentRequirements:
        """Select best payment requirements."""
        return self.x402_client.select_payment_requirements(accepts)

    async def create_payment_header(
        self,
        requirements: X402PaymentRequirements,
        x402_version: int
    ) -> str:
        """Create signed payment header."""
        return self.x402_client.create_payment_header(requirements, x402_version)

    async def health_check(self) -> Dict[str, Any]:
        """Check payment manager health."""
        return {"healthy": True, "account": self.account.address}

    async def close(self):
        """Close payment manager."""
        pass
