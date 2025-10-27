"""
Asynchronous V402 Client implementation.

This module provides the core async client for v402 payments with
advanced features like connection pooling, circuit breaking, and metrics.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../x402/src"))

import httpx
from x402.types import (
    x402PaymentRequiredResponse,
    PaymentRequirements as X402PaymentRequirements,
)
from x402.clients.base import decode_x_payment_response

from v402_client.config.settings import ClientSettings
from v402_client.core.pool import ConnectionPool
from v402_client.chains.manager import ChainManager
from v402_client.payment.manager import PaymentManager
from v402_client.payment.history import PaymentHistoryManager
from v402_client.types.models import PaymentResponse, PaymentHistory, PaymentStatistics
from v402_client.types.enums import PaymentStatus
from v402_client.exceptions.base import V402Exception
from v402_client.exceptions.payment import PaymentVerificationFailed
from v402_client.exceptions.network import ConnectionTimeout, RequestFailed
from v402_client.logging.logger import get_logger
from v402_client.utils.retry import RetryManager
from v402_client.utils.cache import ResponseCache
from v402_client.monitoring.metrics import MetricsCollector


class AsyncV402Client:
    """
    Asynchronous v402 client with enterprise-grade features.

    This is the core client implementation that provides:
    - Asynchronous HTTP operations
    - Multi-chain payment processing
    - Connection pooling and keep-alive
    - Circuit breaker pattern
    - Retry with exponential backoff
    - Response caching
    - Comprehensive metrics
    - Structured logging

    Example:
        >>> async with AsyncV402Client(settings) as client:
        ...     response = await client.get("https://example.com/premium")
        ...     print(response.json())
    """

    def __init__(
        self,
        settings: ClientSettings,
        pool: Optional[ConnectionPool] = None,
        metrics: Optional[MetricsCollector] = None,
    ):
        """
        Initialize the async client.

        Args:
            settings: Client configuration
            pool: Connection pool (optional)
            metrics: Metrics collector (optional)
        """
        self.settings = settings
        self.logger = get_logger(__name__)

        # Core components
        self._pool = pool
        self._metrics = metrics
        self._http_client: Optional[httpx.AsyncClient] = None

        # Managers
        self._chain_manager: Optional[ChainManager] = None
        self._payment_manager: Optional[PaymentManager] = None
        self._history_manager: Optional[PaymentHistoryManager] = None
        self._retry_manager: Optional[RetryManager] = None
        self._cache: Optional[ResponseCache] = None

        # State
        self._is_initialized = False
        self._is_closed = False

    async def _initialize(self) -> None:
        """Initialize all client components."""
        if self._is_initialized:
            return

        try:
            self.logger.info("Initializing AsyncV402Client")

            # Initialize HTTP client with connection pooling
            limits = httpx.Limits(
                max_keepalive_connections=self.settings.max_connections,
                max_connections=self.settings.max_connections * 2,
                keepalive_expiry=300,  # 5 minutes
            )

            self._http_client = httpx.AsyncClient(
                limits=limits,
                timeout=httpx.Timeout(self.settings.timeout),
                follow_redirects=True,
                http2=True,  # Enable HTTP/2
            )

            # Initialize chain manager
            self._chain_manager = ChainManager(
                chains=self.settings.chains,
                logger=self.logger,
            )
            await self._chain_manager.initialize()

            # Initialize payment manager with x402 integration
            self._payment_manager = PaymentManager(
                private_key=self.settings.private_key,
                chains=self.settings.chains,
                max_amount=self.settings.max_amount_per_request,
                facilitator_url=self.settings.facilitator_url,
                logger=self.logger,
            )
            await self._payment_manager.initialize()

            # Initialize history manager
            self._history_manager = PaymentHistoryManager(
                logger=self.logger
            )

            # Initialize retry manager
            self._retry_manager = RetryManager(
                max_retries=self.settings.resilience.max_retries,
                backoff_multiplier=self.settings.resilience.retry_backoff,
                jitter=self.settings.resilience.retry_jitter,
                logger=self.logger,
            )

            # Initialize cache
            if self.settings.enable_cache:
                self._cache = ResponseCache(
                    max_size=self.settings.cache_max_size,
                    ttl=self.settings.cache_ttl,
                    logger=self.logger,
                )

            self._is_initialized = True
            self.logger.info("AsyncV402Client initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize AsyncV402Client", exc_info=True)
            raise V402Exception(f"Client initialization failed: {e}") from e

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        auto_pay: Optional[bool] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform an async GET request with payment handling.

        Args:
            url: URL to request
            headers: Additional headers
            auto_pay: Override auto_pay setting
            **kwargs: Additional request parameters

        Returns:
            PaymentResponse with content and payment info
        """
        return await self._request(
            method="GET",
            url=url,
            headers=headers,
            auto_pay=auto_pay,
            **kwargs
        )

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        auto_pay: Optional[bool] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform an async POST request with payment handling.

        Args:
            url: URL to request
            headers: Additional headers
            json_data: JSON data for request body
            data: Raw data for request body
            auto_pay: Override auto_pay setting
            **kwargs: Additional request parameters

        Returns:
            PaymentResponse with content and payment info
        """
        request_kwargs = kwargs.copy()

        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["content"] = data

        return await self._request(
            method="POST",
            url=url,
            headers=headers,
            auto_pay=auto_pay,
            **request_kwargs
        )

    async def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        auto_pay: Optional[bool] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Core request method with full v402 payment handling.

        This method implements the complete v402 flow:
        1. Check cache for response
        2. Make initial request
        3. Handle 402 Payment Required
        4. Select payment requirements
        5. Create and sign payment
        6. Retry with payment header
        7. Process settlement response
        8. Cache successful response
        """
        if not self._is_initialized:
            await self._initialize()

        if self._is_closed:
            raise V402Exception("Client is closed")

        auto_pay = auto_pay if auto_pay is not None else self.settings.auto_pay
        headers = headers or {}

        start_time = time.time()

        # Metrics tracking
        if self._metrics:
            self._metrics.increment_counter("requests_total", {"method": method})

        try:
            # Check cache first
            if self._cache and method == "GET":
                cached_response = await self._cache.get(url)
                if cached_response:
                    self.logger.debug("Cache hit", extra={"url": url})
                    if self._metrics:
                        self._metrics.increment_counter("cache_hits_total")
                    return cached_response

            # Execute request with retry
            response = await self._retry_manager.execute(
                self._make_request_with_payment,
                method=method,
                url=url,
                headers=headers,
                auto_pay=auto_pay,
                **kwargs
            )

            # Cache successful GET responses
            if self._cache and method == "GET" and response.status_code == 200:
                await self._cache.set(url, response)

            # Track metrics
            duration = time.time() - start_time
            if self._metrics:
                self._metrics.observe_histogram(
                    "request_duration_seconds",
                    duration,
                    {"method": method, "status": str(response.status_code)}
                )

                if response.payment_made:
                    self._metrics.increment_counter("payments_total", {"network": response.network})

            return response

        except Exception as e:
            # Track error metrics
            if self._metrics:
                self._metrics.increment_counter(
                    "requests_failed_total",
                    {"method": method, "error": e.__class__.__name__}
                )

            self.logger.error(
                "Request failed",
                extra={
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "duration": time.time() - start_time,
                }
            )
            raise

    async def _make_request_with_payment(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        auto_pay: bool,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Make HTTP request with v402 payment handling.

        This implements the core v402 protocol flow.
        """
        # Make initial request
        response = await self._make_http_request(method, url, headers, **kwargs)

        # Check if payment is required
        if response.status_code == 402:
            if not auto_pay:
                self.logger.info(
                    "Payment required but auto_pay disabled",
                    extra={"url": url}
                )
                return self._create_payment_response(response, url, False)

            # Handle payment requirement
            payment_response = await self._handle_payment_required(
                response, method, url, headers, **kwargs
            )
            return payment_response

        # Return non-payment response
        return self._create_payment_response(response, url, False)

    async def _make_http_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        **kwargs: Any,
    ) -> httpx.Response:
        """Make the actual HTTP request."""
        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            return response

        except httpx.TimeoutException as e:
            raise ConnectionTimeout(url, self.settings.timeout) from e
        except httpx.RequestError as e:
            raise RequestFailed(url, None, str(e)) from e

    async def _handle_payment_required(
        self,
        response: httpx.Response,
        method: str,
        url: str,
        headers: Dict[str, str],
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Handle 402 Payment Required response.

        This method:
        1. Parses payment requirements
        2. Selects appropriate payment option
        3. Creates payment authorization
        4. Signs payment with x402 protocol
        5. Retries request with payment header
        6. Processes settlement response
        """
        self.logger.info("Payment required", extra={"url": url})

        try:
            # Parse payment requirements
            response_data = response.json()
            payment_required = x402PaymentRequiredResponse(**response_data)

            if not payment_required.accepts:
                raise PaymentVerificationFailed(
                    "No payment options available",
                    {"url": url, "response": response_data}
                )

            # Select payment requirements using payment manager
            selected_requirements = await self._payment_manager.select_payment_requirements(
                payment_required.accepts,
                url=url,
            )

            # Create payment authorization
            payment_header = await self._payment_manager.create_payment_header(
                selected_requirements,
                x402_version=payment_required.x402_version,
            )

            # Add payment header and retry request
            payment_headers = headers.copy()
            payment_headers["X-PAYMENT"] = payment_header

            self.logger.info(
                "Retrying request with payment",
                extra={
                    "url": url,
                    "amount": selected_requirements.max_amount_required,
                    "network": selected_requirements.network,
                }
            )

            # Make paid request
            paid_response = await self._make_http_request(
                method, url, payment_headers, **kwargs
            )

            # Process payment settlement
            settlement_info = await self._process_payment_settlement(
                paid_response, selected_requirements
            )

            # Record payment history
            await self._history_manager.record_payment(
                url=url,
                amount=selected_requirements.max_amount_required,
                network=selected_requirements.network,
                payer=settlement_info.get("payer", ""),
                payee=selected_requirements.pay_to,
                transaction_hash=settlement_info.get("transaction", ""),
                description=selected_requirements.description,
                status=PaymentStatus.CONFIRMED if settlement_info.get("success") else PaymentStatus.FAILED,
            )

            return self._create_payment_response(
                paid_response,
                url,
                True,
                selected_requirements.max_amount_required,
                settlement_info.get("transaction"),
                selected_requirements.network,
                settlement_info.get("payer"),
            )

        except Exception as e:
            self.logger.error(
                "Payment handling failed",
                extra={"url": url, "error": str(e)},
                exc_info=True
            )
            raise PaymentVerificationFailed(
                f"Payment processing failed: {str(e)}",
                {"url": url, "original_error": str(e)}
            ) from e

    async def _process_payment_settlement(
        self,
        response: httpx.Response,
        requirements: X402PaymentRequirements,
    ) -> Dict[str, Any]:
        """
        Process payment settlement response.

        Extracts settlement information from X-PAYMENT-RESPONSE header.
        """
        settlement_header = response.headers.get("X-PAYMENT-RESPONSE")

        if settlement_header:
            try:
                settlement_info = decode_x_payment_response(settlement_header)
                self.logger.info(
                    "Payment settled",
                    extra={
                        "transaction": settlement_info.get("transaction"),
                        "success": settlement_info.get("success"),
                        "network": settlement_info.get("network"),
                    }
                )
                return settlement_info

            except Exception as e:
                self.logger.error(
                    "Failed to decode settlement response",
                    extra={"header": settlement_header, "error": str(e)}
                )

        # Return default info if no settlement header
        return {
            "success": response.status_code == 200,
            "transaction": None,
            "network": requirements.network,
            "payer": None,
        }

    def _create_payment_response(
        self,
        response: httpx.Response,
        url: str,
        payment_made: bool,
        amount: Optional[str] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None,
        payer: Optional[str] = None,
    ) -> PaymentResponse:
        """Create a PaymentResponse from httpx Response."""
        return PaymentResponse(
            status_code=response.status_code,
            content=response.content,
            headers=dict(response.headers),
            url=url,
            payment_made=payment_made,
            payment_amount=amount,
            transaction_hash=transaction_hash,
            network=network,
            payer=payer,
            timestamp=datetime.utcnow(),
        )

    async def batch_get(
        self,
        urls: List[str],
        auto_pay: Optional[bool] = None,
        max_concurrent: int = 10,
        **kwargs: Any,
    ) -> List[PaymentResponse]:
        """
        Perform multiple GET requests concurrently.

        Args:
            urls: List of URLs to request
            auto_pay: Override auto_pay setting
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional request parameters

        Returns:
            List of PaymentResponse objects
        """
        if not self._is_initialized:
            await self._initialize()

        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_get(url: str) -> PaymentResponse:
            async with semaphore:
                return await self.get(url, auto_pay=auto_pay, **kwargs)

        tasks = [bounded_get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed responses
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                # Create error response
                results.append(PaymentResponse(
                    status_code=500,
                    content=str(response).encode(),
                    headers={},
                    url=urls[i],
                    payment_made=False,
                ))
            else:
                results.append(response)

        return results

    async def get_payment_history(
        self,
        limit: Optional[int] = None,
        since: Optional[time.struct_time] = None,
    ) -> List[PaymentHistory]:
        """Get payment history."""
        if not self._history_manager:
            return []

        return await self._history_manager.get_history(limit=limit, since=since)

    async def get_payment_statistics(
        self,
        start_time: Optional[time.struct_time] = None,
        end_time: Optional[time.struct_time] = None,
    ) -> PaymentStatistics:
        """Get payment statistics."""
        if not self._history_manager:
            return PaymentStatistics(
                total_payments=0,
                successful_payments=0,
                failed_payments=0,
                total_amount="0",
                average_amount="0",
                min_amount="0",
                max_amount="0",
                unique_resources=0,
                unique_networks=0,
                time_period_start=datetime.utcnow(),
                time_period_end=datetime.utcnow(),
            )

        return await self._history_manager.get_statistics(
            start_time=start_time,
            end_time=end_time
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "healthy": True,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
        }

        try:
            # Check HTTP client
            if self._http_client:
                health_status["components"]["http_client"] = {"healthy": True}
            else:
                health_status["components"]["http_client"] = {"healthy": False}
                health_status["healthy"] = False

            # Check chain manager
            if self._chain_manager:
                chain_health = await self._chain_manager.health_check()
                health_status["components"]["chains"] = chain_health
                if not all(c.get("healthy", False) for c in chain_health.values()):
                    health_status["healthy"] = False

            # Check payment manager
            if self._payment_manager:
                payment_health = await self._payment_manager.health_check()
                health_status["components"]["payment"] = payment_health
                if not payment_health.get("healthy", False):
                    health_status["healthy"] = False

        except Exception as e:
            health_status["healthy"] = False
            health_status["error"] = str(e)

        return health_status

    async def close(self) -> None:
        """Close the client and clean up resources."""
        if self._is_closed:
            return

        self.logger.info("Closing AsyncV402Client")

        try:
            # Close all managers
            if self._chain_manager:
                await self._chain_manager.close()

            if self._payment_manager:
                await self._payment_manager.close()

            if self._cache:
                await self._cache.close()

            # Close HTTP client
            if self._http_client:
                await self._http_client.aclose()

        except Exception as e:
            self.logger.error("Error during client shutdown", exc_info=True)
        finally:
            self._is_closed = True

    async def __aenter__(self) -> "AsyncV402Client":
        """Async context manager entry."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AsyncV402Client("
            f"chains={len(self.settings.chains)}, "
            f"initialized={self._is_initialized}, "
            f"closed={self._is_closed}"
            f")"
        )
