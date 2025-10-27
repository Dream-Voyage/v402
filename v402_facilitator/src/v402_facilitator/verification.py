"""
Payment verification logic for v402 Facilitator.

This module handles cryptographic verification of payment signatures
and authorization structures.
"""

import logging
import os
import sys
from typing import Tuple, Optional

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../x402/src"))

from eth_account import Account
from eth_account.messages import encode_structured_data
from x402.types import (
    PaymentPayload,
    PaymentRequirements,
    ExactPaymentPayload,
)

logger = logging.getLogger(__name__)


class PaymentVerifier:
    """
    Handles verification of payment signatures and authorizations.

    This class implements the cryptographic verification logic for
    the "exact" payment scheme using EIP-712 signatures.
    """

    def __init__(self):
        """Initialize the payment verifier."""
        pass

    async def verify_payment(
        self,
        payment_payload: PaymentPayload,
        payment_requirements: PaymentRequirements,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify a payment payload against requirements.

        Args:
            payment_payload: The payment payload to verify
            payment_requirements: The expected payment requirements

        Returns:
            Tuple of (is_valid, error_reason, payer_address)
        """
        try:
            # Check scheme
            if payment_payload.scheme != payment_requirements.scheme:
                return False, "Scheme mismatch", None

            # Check network
            if payment_payload.network != payment_requirements.network:
                return False, "Network mismatch", None

            # Verify based on scheme
            if payment_payload.scheme == "exact":
                return await self._verify_exact_payment(
                    payment_payload, payment_requirements
                )
            else:
                return False, f"Unsupported scheme: {payment_payload.scheme}", None

        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return False, str(e), None

    async def _verify_exact_payment(
        self,
        payment_payload: PaymentPayload,
        payment_requirements: PaymentRequirements,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify an "exact" payment scheme.

        This implements EIP-3009 signature verification for exact payments.

        Args:
            payment_payload: Payment payload
            payment_requirements: Payment requirements

        Returns:
            Tuple of (is_valid, error_reason, payer_address)
        """
        try:
            # Parse exact payment payload
            exact_payload = ExactPaymentPayload(**payment_payload.payload)
            authorization = exact_payload.authorization
            signature = exact_payload.signature

            # Verify amount
            if authorization.value != payment_requirements.max_amount_required:
                return False, "Payment amount mismatch", None

            # Verify recipient
            if authorization.to.lower() != payment_requirements.pay_to.lower():
                return False, "Recipient address mismatch", None

            # Verify time validity
            import time

            current_time = int(time.time())
            valid_after = int(authorization.valid_after)
            valid_before = int(authorization.valid_before)

            if current_time < valid_after:
                return False, "Payment not yet valid", None

            if current_time > valid_before:
                return False, "Payment expired", None

            # Verify EIP-712 signature
            payer = self._verify_eip712_signature(
                authorization=authorization,
                signature=signature,
                asset_address=payment_requirements.asset,
                extra=payment_requirements.extra or {},
            )

            if not payer:
                return False, "Invalid signature", None

            # Verify payer matches authorization
            if payer.lower() != authorization.from_.lower():
                return False, "Payer address mismatch", None

            logger.info(f"Payment verified: {authorization.value} from {payer}")
            return True, None, payer

        except Exception as e:
            logger.error(f"Exact payment verification error: {e}")
            return False, str(e), None

    def _verify_eip712_signature(
        self,
        authorization: Any,
        signature: str,
        asset_address: str,
        extra: dict,
    ) -> Optional[str]:
        """
        Verify EIP-712 signature for payment authorization.

        Args:
            authorization: Authorization object
            signature: Hex-encoded signature
            asset_address: Token contract address
            extra: Extra domain information (name, version)

        Returns:
            Recovered signer address or None if invalid
        """
        try:
            # Get domain information from extra
            domain_name = extra.get("name", "USD Coin")
            domain_version = extra.get("version", "2")

            # Construct EIP-712 structured data
            structured_data = {
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"},
                    ],
                    "TransferWithAuthorization": [
                        {"name": "from", "type": "address"},
                        {"name": "to", "type": "address"},
                        {"name": "value", "type": "uint256"},
                        {"name": "validAfter", "type": "uint256"},
                        {"name": "validBefore", "type": "uint256"},
                        {"name": "nonce", "type": "bytes32"},
                    ],
                },
                "primaryType": "TransferWithAuthorization",
                "domain": {
                    "name": domain_name,
                    "version": domain_version,
                    "chainId": self._get_chain_id_for_network(),
                    "verifyingContract": asset_address,
                },
                "message": {
                    "from": authorization.from_,
                    "to": authorization.to,
                    "value": int(authorization.value),
                    "validAfter": int(authorization.valid_after),
                    "validBefore": int(authorization.valid_before),
                    "nonce": authorization.nonce,
                },
            }

            # Encode and recover signer
            encoded_data = encode_structured_data(structured_data)
            recovered_address = Account.recover_message(
                encoded_data, signature=signature
            )

            return recovered_address

        except Exception as e:
            logger.error(f"EIP-712 signature verification error: {e}")
            return None

    def _get_chain_id_for_network(self) -> int:
        """
        Get chain ID for current network.

        Returns:
            Chain ID
        """
        from v402_facilitator.config import settings

        # Map network names to chain IDs
        chain_ids = {
            "base-sepolia": 84532,
            "base": 8453,
            "ethereum": 1,
            "sepolia": 11155111,
        }

        return chain_ids.get(settings.network, settings.chain_id)

