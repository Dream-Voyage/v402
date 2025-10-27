"""
Main client implementation for v402 Index Client.

This module provides the core client class that handles automatic payment
detection, transaction signing, and content retrieval.
"""

import httpx
import logging
import os
import sys
from datetime import datetime
from eth_account import Account
from typing import Optional, List, Dict, Any, Callable

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../x402/src"))

from x402.types import (
    x402PaymentRequiredResponse,
)
from x402.clients.base import (
    x402Client,
    decode_x_payment_response,
    PaymentAmountExceededError,
)
from x402.common import x402_VERSION

from v402_index_client.types import (
    ClientConfig,
    PaymentResponse,
    PaymentHistory,
    PaymentRequirementsInfo,
)
from v402_index_client.exceptions import (
    PaymentLimitExceeded,
    ContentNotAvailable,
)

logger = logging.getLogger(__name__)


class V402IndexClient:
    """
    High-level client for AI/crawler platforms to handle automatic payments.

    This client wraps the base x402 client and provides additional functionality:
    - Automatic 402 detection and retry
    - Payment history tracking
    - Batch request support
    - Error handling and logging

    Example:
        >>> client = V402IndexClient(private_key="0x...")
        >>> response = await client.get("https://example.com/premium", auto_pay=True)
        >>> print(response.json())
    """

    def __init__(
        self,
        private_key: str,
        max_amount_per_request: str = "1000000",
        network: str = "base-sepolia",
        facilitator_url: str = "http://localhost:8000",
        retry_attempts: int = 3,
        timeout: int = 30,
        auto_pay: bool = True,
        payment_selector: Optional[Callable] = None,
    ):
        """
        Initialize the V402 Index Client.

        Args:
            private_key: Ethereum private key for signing payments
            max_amount_per_request: Maximum payment amount in wei
            network: Blockchain network to use
            facilitator_url: URL of the facilitator service
            retry_attempts: Number of retry attempts for failed requests
            timeout: Request timeout in seconds
            auto_pay: Whether to automatically pay when encountering 402
            payment_selector: Custom payment requirements selector function
        """
        self.config = ClientConfig(
            private_key=private_key,
            max_amount_per_request=max_amount_per_request,
            network=network,
            facilitator_url=facilitator_url,
            retry_attempts=retry_attempts,
            timeout=timeout,
            auto_pay=auto_pay,
        )

        # Initialize eth account
        self.account = Account.from_key(private_key)

        # Initialize x402 client
        self.x402_client = x402Client(
            account=self.account,
            max_value=int(max_amount_per_request),
            payment_requirements_selector=payment_selector,
        )

        # Payment history storage
        self._payment_history: List[PaymentHistory] = []

        # HTTP client
        self._http_client = httpx.AsyncClient(timeout=timeout)

        logger.info(
            f"V402IndexClient initialized for network {network} "
            f"with max amount {max_amount_per_request} wei"
        )

    async def get(
        self,
        url: str,
        auto_pay: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform a GET request with automatic payment handling.

        Args:
            url: URL to request
            auto_pay: Override default auto_pay setting
            headers: Additional headers to send
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            PaymentResponse object containing response data and payment info

        Raises:
            PaymentLimitExceeded: If payment amount exceeds maximum
            PaymentFailed: If payment transaction fails
            NetworkNotSupported: If required network is not supported
        """
        auto_pay = auto_pay if auto_pay is not None else self.config.auto_pay
        return await self._request("GET", url, auto_pay, headers, **kwargs)

    async def post(
        self,
        url: str,
        auto_pay: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform a POST request with automatic payment handling.

        Args:
            url: URL to request
            auto_pay: Override default auto_pay setting
            headers: Additional headers to send
            json_data: JSON data to send in request body
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            PaymentResponse object containing response data and payment info
        """
        auto_pay = auto_pay if auto_pay is not None else self.config.auto_pay
        if json_data:
            kwargs["json"] = json_data
        return await self._request("POST", url, auto_pay, headers, **kwargs)

    async def _request(
        self,
        method: str,
        url: str,
        auto_pay: bool,
        headers: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Internal method to perform HTTP request with payment handling.

        This method:
        1. Makes initial request
        2. Detects 402 Payment Required
        3. Selects appropriate payment method
        4. Creates and signs payment
        5. Retries request with payment header
        6. Tracks payment history

        Args:
            method: HTTP method
            url: URL to request
            auto_pay: Whether to automatically handle payment
            headers: Request headers
            **kwargs: Additional request arguments

        Returns:
            PaymentResponse object
        """
        if headers is None:
            headers = {}

        # Initial request
        response = await self._http_client.request(method, url, headers=headers, **kwargs)

        # Check if payment required
        if response.status_code == 402:
            if not auto_pay:
                logger.info(f"Payment required for {url}, but auto_pay is disabled")
                return self._create_response(response, url, False)

            logger.info(f"Payment required for {url}, attempting to pay...")

            # Parse payment requirements
            payment_required_response = x402PaymentRequiredResponse(
                **response.json()
            )

            # Select payment requirements
            try:
                selected_requirements = self.x402_client.select_payment_requirements(
                    payment_required_response.accepts,
                    network_filter=self.config.network,
                    scheme_filter="exact",
                )
            except PaymentAmountExceededError as e:
                raise PaymentLimitExceeded(
                    amount=str(e),
                    max_amount=self.config.max_amount_per_request,
                )

            # Create payment header
            payment_header = self.x402_client.create_payment_header(
                selected_requirements,
                x402_version=x402_VERSION,
            )

            # Retry request with payment
            headers["X-PAYMENT"] = payment_header
            paid_response = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )

            # Extract payment response
            payment_response_header = paid_response.headers.get("X-PAYMENT-RESPONSE")
            if payment_response_header:
                payment_info = decode_x_payment_response(payment_response_header)

                # Record payment history
                self._record_payment(
                    url=url,
                    amount=selected_requirements.max_amount_required,
                    transaction_hash=payment_info.get("transaction", ""),
                    network=payment_info.get("network", ""),
                    description=selected_requirements.description,
                    payer=self.account.address,
                    payee=selected_requirements.pay_to,
                    success=payment_info.get("success", False),
                )

                return self._create_response(
                    paid_response,
                    url,
                    True,
                    selected_requirements.max_amount_required,
                    payment_info.get("transaction"),
                    payment_info.get("network"),
                )
            else:
                logger.warning("Payment made but no X-PAYMENT-RESPONSE header received")
                return self._create_response(paid_response, url, True)

        # No payment required
        return self._create_response(response, url, False)

    def _create_response(
        self,
        response: httpx.Response,
        url: str,
        payment_made: bool,
        amount: Optional[str] = None,
        tx_hash: Optional[str] = None,
        network: Optional[str] = None,
    ) -> PaymentResponse:
        """
        Create a PaymentResponse object from httpx Response.

        Args:
            response: httpx Response object
            url: Requested URL
            payment_made: Whether payment was made
            amount: Payment amount if made
            tx_hash: Transaction hash if payment made
            network: Network used if payment made

        Returns:
            PaymentResponse object
        """
        return PaymentResponse(
            status_code=response.status_code,
            content=response.content,
            headers=dict(response.headers),
            payment_made=payment_made,
            payment_amount=amount,
            transaction_hash=tx_hash,
            network=network,
            url=url,
        )

    def _record_payment(
        self,
        url: str,
        amount: str,
        transaction_hash: str,
        network: str,
        description: str,
        payer: str,
        payee: str,
        success: bool,
    ) -> None:
        """
        Record a payment in the history.

        Args:
            url: URL that was accessed
            amount: Payment amount
            transaction_hash: Blockchain transaction hash
            network: Network used
            description: Content description
            payer: Payer address
            payee: Payee address
            success: Whether payment succeeded
        """
        history = PaymentHistory(
            url=url,
            amount=amount,
            transaction_hash=transaction_hash,
            network=network,
            timestamp=datetime.utcnow(),
            description=description,
            payer=payer,
            payee=payee,
            success=success,
        )
        self._payment_history.append(history)
        logger.info(f"Payment recorded: {amount} wei to {payee} for {url}")

    def get_payment_history(
        self, limit: Optional[int] = None
    ) -> List[PaymentHistory]:
        """
        Get payment history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of PaymentHistory objects
        """
        if limit:
            return self._payment_history[-limit:]
        return self._payment_history

    async def get_payment_requirements(self, url: str) -> PaymentRequirementsInfo:
        """
        Get payment requirements for a URL without making payment.

        Args:
            url: URL to check

        Returns:
            PaymentRequirementsInfo object

        Raises:
            ContentNotAvailable: If content doesn't require payment
        """
        response = await self._http_client.get(url)

        if response.status_code != 402:
            raise ContentNotAvailable(f"Content at {url} does not require payment")

        payment_required = x402PaymentRequiredResponse(**response.json())

        return PaymentRequirementsInfo(
            url=url,
            payment_options=[
                req.model_dump() for req in payment_required.accepts
            ],
            min_amount=min(
                int(req.max_amount_required) for req in payment_required.accepts
            ).__str__(),
            max_amount=max(
                int(req.max_amount_required) for req in payment_required.accepts
            ).__str__(),
            supported_networks=list(
                set(req.network for req in payment_required.accepts)
            ),
            supported_schemes=list(
                set(req.scheme for req in payment_required.accepts)
            ),
            description=payment_required.accepts[0].description
            if payment_required.accepts
            else "",
        )

    async def batch_get(
        self, urls: List[str], auto_pay: Optional[bool] = None
    ) -> List[PaymentResponse]:
        """
        Perform multiple GET requests in batch.

        Args:
            urls: List of URLs to request
            auto_pay: Override default auto_pay setting

        Returns:
            List of PaymentResponse objects
        """
        import asyncio

        tasks = [self.get(url, auto_pay=auto_pay) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> "V402IndexClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

