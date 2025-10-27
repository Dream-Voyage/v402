"""
Main V402 Client implementation.

This module provides the synchronous client interface for v402 payments.
It handles multi-chain payment processing, connection pooling, and error recovery.
"""

import asyncio
import os
import sys
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Union

# Add x402 to path for local import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../x402/src"))

from v402_client.config.settings import ClientSettings, ChainConfig
from v402_client.core.async_client import AsyncV402Client
from v402_client.core.pool import ConnectionPool
from v402_client.types.models import PaymentResponse, PaymentHistory, PaymentStatistics
from v402_client.exceptions.base import V402Exception
from v402_client.logging.logger import get_logger
from v402_client.monitoring.metrics import MetricsCollector


class V402Client:
    """
    Synchronous v402 client for payment processing.

    This client provides a synchronous interface that wraps the async client.
    It's suitable for synchronous applications and simple scripts.

    Features:
    - Multi-chain payment support
    - Automatic connection pooling
    - Circuit breaker pattern
    - Comprehensive error handling
    - Metrics collection

    Example:
        >>> client = V402Client(
        ...     private_key="0x...",
        ...     chains=[ChainConfig.ethereum(), ChainConfig.base()]
        ... )
        >>> with client:
        ...     response = client.get("https://example.com/premium")
        ...     print(response.json())
    """

    def __init__(
        self,
        private_key: Optional[str] = None,
        settings: Optional[ClientSettings] = None,
        chains: Optional[List[ChainConfig]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the V402 client.

        Args:
            private_key: Private key for signing transactions
            settings: Complete client settings
            chains: List of chain configurations
            **kwargs: Additional settings passed to ClientSettings

        Raises:
            V402Exception: If configuration is invalid
        """
        self.logger = get_logger(__name__)

        # Build settings from parameters
        if settings is None:
            if private_key is None:
                raise V402Exception("private_key is required")

            settings_dict = {"private_key": private_key}
            if chains:
                settings_dict["chains"] = chains
            settings_dict.update(kwargs)

            settings = ClientSettings(**settings_dict)

        self.settings = settings

        # Initialize components
        self._pool: Optional[ConnectionPool] = None
        self._async_client: Optional[AsyncV402Client] = None
        self._metrics: Optional[MetricsCollector] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

        # State tracking
        self._is_initialized = False
        self._is_closed = False

        self.logger.info(
            "V402Client initialized",
            extra={
                "chains": [c.name for c in self.settings.chains],
                "auto_pay": self.settings.auto_pay,
                "max_amount": self.settings.max_amount_per_request,
            }
        )

    def _ensure_initialized(self) -> None:
        """Ensure client is initialized."""
        if not self._is_initialized:
            self._initialize()

    def _initialize(self) -> None:
        """Initialize the client components."""
        if self._is_initialized:
            return

        try:
            # Create event loop for async operations
            try:
                self._event_loop = asyncio.get_event_loop()
            except RuntimeError:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)

            # Initialize connection pool
            self._pool = ConnectionPool(
                max_connections=self.settings.max_connections,
                keep_alive=self.settings.keep_alive,
                timeout=self.settings.timeout,
            )

            # Initialize async client
            self._async_client = AsyncV402Client(
                settings=self.settings,
                pool=self._pool,
            )

            # Initialize metrics collector
            if self.settings.metrics.enabled:
                self._metrics = MetricsCollector(
                    port=self.settings.metrics.port,
                    path=self.settings.metrics.path,
                )
                self._metrics.start()

            # Run async initialization
            self._event_loop.run_until_complete(self._async_client._initialize())

            self._is_initialized = True
            self.logger.info("V402Client initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize V402Client", exc_info=True)
            raise V402Exception(f"Client initialization failed: {e}") from e

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        auto_pay: Optional[bool] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform a GET request with automatic payment handling.

        Args:
            url: URL to request
            headers: Additional headers
            auto_pay: Override auto_pay setting
            **kwargs: Additional request parameters

        Returns:
            PaymentResponse containing response data and payment info

        Raises:
            V402Exception: If request fails
        """
        self._ensure_initialized()

        if self._is_closed:
            raise V402Exception("Client is closed")

        try:
            coro = self._async_client.get(
                url=url,
                headers=headers,
                auto_pay=auto_pay,
                **kwargs
            )

            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error(
                "GET request failed",
                extra={"url": url, "error": str(e)}
            )
            raise

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        auto_pay: Optional[bool] = None,
        **kwargs: Any,
    ) -> PaymentResponse:
        """
        Perform a POST request with automatic payment handling.

        Args:
            url: URL to request
            headers: Additional headers
            json_data: JSON data for request body
            data: Raw data for request body
            auto_pay: Override auto_pay setting
            **kwargs: Additional request parameters

        Returns:
            PaymentResponse containing response data and payment info

        Raises:
            V402Exception: If request fails
        """
        self._ensure_initialized()

        if self._is_closed:
            raise V402Exception("Client is closed")

        try:
            coro = self._async_client.post(
                url=url,
                headers=headers,
                json_data=json_data,
                data=data,
                auto_pay=auto_pay,
                **kwargs
            )

            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error(
                "POST request failed",
                extra={"url": url, "error": str(e)}
            )
            raise

    def batch_get(
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

        Raises:
            V402Exception: If batch request fails
        """
        self._ensure_initialized()

        if self._is_closed:
            raise V402Exception("Client is closed")

        try:
            coro = self._async_client.batch_get(
                urls=urls,
                auto_pay=auto_pay,
                max_concurrent=max_concurrent,
                **kwargs
            )

            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error(
                "Batch GET failed",
                extra={"url_count": len(urls), "error": str(e)}
            )
            raise

    def get_payment_history(
        self,
        limit: Optional[int] = None,
        since: Optional[time.struct_time] = None,
    ) -> List[PaymentHistory]:
        """
        Get payment history.

        Args:
            limit: Maximum number of records
            since: Only return payments since this time

        Returns:
            List of payment history records
        """
        self._ensure_initialized()

        try:
            coro = self._async_client.get_payment_history(limit=limit, since=since)
            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error("Failed to get payment history", exc_info=True)
            raise V402Exception(f"Failed to get payment history: {e}") from e

    def get_payment_statistics(
        self,
        start_time: Optional[time.struct_time] = None,
        end_time: Optional[time.struct_time] = None,
    ) -> PaymentStatistics:
        """
        Get payment statistics.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Payment statistics
        """
        self._ensure_initialized()

        try:
            coro = self._async_client.get_payment_statistics(
                start_time=start_time,
                end_time=end_time
            )
            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error("Failed to get payment statistics", exc_info=True)
            raise V402Exception(f"Failed to get payment statistics: {e}") from e

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on client and its components.

        Returns:
            Health status information
        """
        try:
            self._ensure_initialized()

            coro = self._async_client.health_check()
            return self._event_loop.run_until_complete(coro)

        except Exception as e:
            self.logger.error("Health check failed", exc_info=True)
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    def close(self) -> None:
        """Close the client and clean up resources."""
        if self._is_closed:
            return

        self.logger.info("Closing V402Client")

        try:
            if self._async_client:
                coro = self._async_client.close()
                if self._event_loop and not self._event_loop.is_closed():
                    self._event_loop.run_until_complete(coro)

            if self._pool:
                coro = self._pool.close()
                if self._event_loop and not self._event_loop.is_closed():
                    self._event_loop.run_until_complete(coro)

            if self._metrics:
                self._metrics.stop()

            if self._event_loop and not self._event_loop.is_closed():
                # Don't close the event loop if we didn't create it
                pass

        except Exception as e:
            self.logger.error("Error during client shutdown", exc_info=True)
        finally:
            self._is_closed = True

    def __enter__(self) -> "V402Client":
        """Context manager entry."""
        self._ensure_initialized()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    @contextmanager
    def temporary_settings(self, **settings: Any):
        """
        Temporarily modify client settings.

        Args:
            **settings: Settings to temporarily override

        Example:
            >>> with client.temporary_settings(auto_pay=False):
            ...     response = client.get(url)  # Won't auto-pay
        """
        if not self._async_client:
            raise V402Exception("Client not initialized")

        original_settings = {}

        try:
            # Save original settings
            for key, value in settings.items():
                if hasattr(self.settings, key):
                    original_settings[key] = getattr(self.settings, key)
                    setattr(self.settings, key, value)

            yield

        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(self.settings, key, value)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"V402Client("
            f"chains={len(self.settings.chains)}, "
            f"auto_pay={self.settings.auto_pay}, "
            f"initialized={self._is_initialized}, "
            f"closed={self._is_closed}"
            f")"
        )
