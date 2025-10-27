"""
On-chain settlement logic for v402 Facilitator.

This module handles the actual blockchain transactions for settling payments.
"""

import logging
import os
import sys
from typing import Optional, Tuple

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../x402/src"))

from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
from x402.types import (
    PaymentPayload,
    PaymentRequirements,
    ExactPaymentPayload,
)

logger = logging.getLogger(__name__)


class SettlementEngine:
    """
    Handles on-chain settlement of verified payments.

    This class manages blockchain interactions for settling payments,
    including gas estimation, transaction submission, and confirmation tracking.
    """

    def __init__(self, rpc_url: str, private_key: str, chain_id: int):
        """
        Initialize the settlement engine.

        Args:
            rpc_url: RPC endpoint URL
            private_key: Private key for signing transactions
            chain_id: Blockchain chain ID
        """
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        # Add PoA middleware for networks like Base
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.account = Account.from_key(private_key)
        self.chain_id = chain_id

        if not self.web3.is_connected():
            logger.error(f"Failed to connect to RPC: {rpc_url}")
            raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")

        logger.info(
            f"SettlementEngine initialized with account {self.account.address}"
        )

    async def settle_payment(
        self,
        payment_payload: PaymentPayload,
        payment_requirements: PaymentRequirements,
        payer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Settle a verified payment on-chain.

        Args:
            payment_payload: Verified payment payload
            payment_requirements: Payment requirements
            payer: Verified payer address

        Returns:
            Tuple of (success, transaction_hash, error_message)
        """
        try:
            # Handle settlement based on scheme
            if payment_payload.scheme == "exact":
                return await self._settle_exact_payment(
                    payment_payload, payment_requirements, payer
                )
            else:
                return False, None, f"Unsupported scheme: {payment_payload.scheme}"

        except Exception as e:
            logger.error(f"Settlement error: {e}")
            return False, None, str(e)

    async def _settle_exact_payment(
        self,
        payment_payload: PaymentPayload,
        payment_requirements: PaymentRequirements,
        payer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Settle an "exact" payment using EIP-3009.

        This calls the `receiveWithAuthorization` function on the ERC-20 token contract.

        Args:
            payment_payload: Payment payload
            payment_requirements: Payment requirements
            payer: Payer address

        Returns:
            Tuple of (success, transaction_hash, error_message)
        """
        try:
            exact_payload = ExactPaymentPayload(**payment_payload.payload)
            authorization = exact_payload.authorization
            signature = exact_payload.signature

            # Get token contract
            asset_address = payment_requirements.asset

            # EIP-3009 receiveWithAuthorization function ABI
            receive_abi = {
                "inputs": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "validAfter", "type": "uint256"},
                    {"name": "validBefore", "type": "uint256"},
                    {"name": "nonce", "type": "bytes32"},
                    {"name": "v", "type": "uint8"},
                    {"name": "r", "type": "bytes32"},
                    {"name": "s", "type": "bytes32"},
                ],
                "name": "receiveWithAuthorization",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }

            # Create contract instance
            contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(asset_address),
                abi=[receive_abi],
            )

            # Parse signature (remove 0x prefix if present)
            sig = signature.replace("0x", "")
            r = "0x" + sig[0:64]
            s = "0x" + sig[64:128]
            v = int(sig[128:130], 16)

            # Build transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)

            transaction = contract.functions.receiveWithAuthorization(
                Web3.to_checksum_address(authorization.from_),
                Web3.to_checksum_address(authorization.to),
                int(authorization.value),
                int(authorization.valid_after),
                int(authorization.valid_before),
                Web3.to_bytes(hexstr=authorization.nonce),
                v,
                Web3.to_bytes(hexstr=r),
                Web3.to_bytes(hexstr=s),
            ).build_transaction(
                {
                    "chainId": self.chain_id,
                    "gas": 100000,  # Estimate or use fixed value
                    "gasPrice": self.web3.eth.gas_price,
                    "nonce": nonce,
                }
            )

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.account.key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt.status == 1:
                tx_hash_hex = tx_hash.hex()
                logger.info(
                    f"Payment settled successfully: {tx_hash_hex} "
                    f"({authorization.value} from {payer})"
                )
                return True, tx_hash_hex, None
            else:
                logger.error(f"Transaction failed: {tx_hash.hex()}")
                return False, None, "Transaction reverted"

        except Exception as e:
            logger.error(f"Exact payment settlement error: {e}")
            return False, None, str(e)

    def get_balance(self, address: str, token_address: Optional[str] = None) -> str:
        """
        Get balance of an address.

        Args:
            address: Address to check
            token_address: Token contract address (None for native token)

        Returns:
            Balance as string in wei
        """
        try:
            if token_address:
                # ERC-20 balance
                balance_abi = {
                    "inputs": [{"name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function",
                }
                contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=[balance_abi],
                )
                balance = contract.functions.balanceOf(
                    Web3.to_checksum_address(address)
                ).call()
            else:
                # Native token balance
                balance = self.web3.eth.get_balance(
                    Web3.to_checksum_address(address)
                )

            return str(balance)

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return "0"

    def estimate_gas(
        self, from_address: str, to_address: str, value: str
    ) -> Optional[int]:
        """
        Estimate gas for a transaction.

        Args:
            from_address: Sender address
            to_address: Recipient address
            value: Transaction value in wei

        Returns:
            Estimated gas or None
        """
        try:
            gas_estimate = self.web3.eth.estimate_gas(
                {
                    "from": Web3.to_checksum_address(from_address),
                    "to": Web3.to_checksum_address(to_address),
                    "value": int(value),
                }
            )
            return gas_estimate
        except Exception as e:
            logger.error(f"Gas estimation error: {e}")
            return None

