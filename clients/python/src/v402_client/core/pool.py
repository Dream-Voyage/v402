"""
Connection pool management for v402 client.

This module provides HTTP connection pooling with health checks,
load balancing, and automatic failover capabilities.
"""

import asyncio
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import httpx

from v402_client.logging.logger import get_logger


@dataclass
class PoolStats:
    """Connection pool statistics."""

    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_health_check: Optional[float] = None


@dataclass
class ConnectionInfo:
    """Information about a connection."""

    url: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    request_count: int = 0
    error_count: int = 0
    is_healthy: bool = True
    response_times: List[float] = field(default_factory=list)


class ConnectionPool:
    """
    Advanced HTTP connection pool with health monitoring.

    Features:
    - Connection reuse and keep-alive
    - Health checks and automatic failover
    - Load balancing across connections
    - Connection limits and timeouts
    - Comprehensive statistics

    Example:
        >>> pool = ConnectionPool(max_connections=50)
        >>> async with pool.get_connection() as client:
        ...     response = await client.get("https://example.com")
    """

    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive: int = 20,
        keepalive_expiry: float = 300.0,  # 5 minutes
        timeout: float = 30.0,
        keep_alive: bool = True,
        health_check_interval: float = 60.0,  # 1 minute
        max_retries: int = 3,
    ):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum total connections
            max_keepalive: Maximum keep-alive connections
            keepalive_expiry: Keep-alive expiry time in seconds
            timeout: Default request timeout
            keep_alive: Enable keep-alive connections
            health_check_interval: Health check interval in seconds
            max_retries: Maximum retry attempts
        """
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self.keep_alive = keep_alive
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries

        self.logger = get_logger(__name__)

        # Connection tracking
        self._connections: Dict[str, httpx.AsyncClient] = {}
        self._connection_info: Dict[str, ConnectionInfo] = {}
        self._active_connections: Set[str] = set()
        self._lock = asyncio.Lock()

        # Statistics
        self._stats = PoolStats()
        self._response_times: List[float] = []

        # Health checking
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_closed = False

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        self.logger.info("Initializing connection pool")

        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        self.logger.info(
            "Connection pool initialized",
            extra={
                "max_connections": self.max_connections,
                "max_keepalive": self.max_keepalive,
                "timeout": self.timeout,
            }
        )

    @asynccontextmanager
    async def get_connection(self, url: Optional[str] = None):
        """
        Get a connection from the pool.

        Args:
            url: Base URL for connection affinity

        Yields:
            httpx.AsyncClient: HTTP client connection
        """
        connection_key = url or "default"

        async with self._lock:
            # Get or create connection
            client = await self._get_or_create_connection(connection_key, url)

            # Mark as active
            self._active_connections.add(connection_key)
            self._stats.active_connections = len(self._active_connections)

        try:
            yield client
        finally:
            async with self._lock:
                # Mark as inactive
                self._active_connections.discard(connection_key)
                self._stats.active_connections = len(self._active_connections)

                # Update connection info
                if connection_key in self._connection_info:
                    self._connection_info[connection_key].last_used = time.time()

    async def _get_or_create_connection(
        self,
        key: str,
        url: Optional[str] = None
    ) -> httpx.AsyncClient:
        """Get existing connection or create new one."""

        # Check if connection exists and is healthy
        if key in self._connections:
            connection_info = self._connection_info.get(key)
            if connection_info and connection_info.is_healthy:
                # Check if connection is expired
                if (time.time() - connection_info.last_used) < self.keepalive_expiry:
                    connection_info.request_count += 1
                    return self._connections[key]
                else:
                    # Connection expired, close it
                    await self._close_connection(key)

        # Create new connection if under limit
        if len(self._connections) >= self.max_connections:
            # Remove oldest idle connection
            await self._evict_oldest_connection()

        # Create new client
        limits = httpx.Limits(
            max_keepalive_connections=self.max_keepalive,
            max_connections=self.max_connections,
            keepalive_expiry=self.keepalive_expiry,
        )

        timeout_config = httpx.Timeout(
            connect=self.timeout,
            read=self.timeout,
            write=self.timeout,
            pool=self.timeout,
        )

        client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout_config,
            follow_redirects=True,
            http2=True,
            base_url=url,
        )

        # Store connection and info
        self._connections[key] = client
        self._connection_info[key] = ConnectionInfo(
            url=url or "",
            request_count=1,
        )

        self._stats.total_connections = len(self._connections)

        self.logger.debug(
            "Created new connection",
            extra={"key": key, "url": url, "total": len(self._connections)}
        )

        return client

    async def _evict_oldest_connection(self) -> None:
        """Evict the oldest idle connection."""
        oldest_key = None
        oldest_time = float('inf')

        for key, info in self._connection_info.items():
            if key not in self._active_connections:  # Only evict idle connections
                if info.last_used < oldest_time:
                    oldest_time = info.last_used
                    oldest_key = key

        if oldest_key:
            await self._close_connection(oldest_key)

    async def _close_connection(self, key: str) -> None:
        """Close a specific connection."""
        if key in self._connections:
            try:
                await self._connections[key].aclose()
            except Exception as e:
                self.logger.warning(
                    "Error closing connection",
                    extra={"key": key, "error": str(e)}
                )

            del self._connections[key]

        if key in self._connection_info:
            del self._connection_info[key]

        self._active_connections.discard(key)
        self._stats.total_connections = len(self._connections)

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while not self._is_closed:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "Health check error",
                    extra={"error": str(e)},
                    exc_info=True
                )

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all connections."""
        if not self._connections:
            return

        self.logger.debug("Performing connection health checks")

        async with self._lock:
            unhealthy_connections = []

            for key, info in self._connection_info.items():
                # Check if connection is stale
                if (time.time() - info.last_used) > self.keepalive_expiry * 2:
                    unhealthy_connections.append(key)
                    continue

                # Check error rate
                if info.request_count > 0:
                    error_rate = info.error_count / info.request_count
                    if error_rate > 0.5:  # 50% error rate threshold
                        info.is_healthy = False
                        unhealthy_connections.append(key)

            # Close unhealthy connections
            for key in unhealthy_connections:
                await self._close_connection(key)

        self._stats.last_health_check = time.time()

    async def record_request(
        self,
        connection_key: str,
        success: bool,
        response_time: float
    ) -> None:
        """
        Record request statistics.

        Args:
            connection_key: Connection identifier
            success: Whether request was successful
            response_time: Response time in seconds
        """
        async with self._lock:
            self._stats.total_requests += 1

            if not success:
                self._stats.failed_requests += 1

            # Update connection info
            if connection_key in self._connection_info:
                info = self._connection_info[connection_key]
                if not success:
                    info.error_count += 1

                info.response_times.append(response_time)

                # Keep only recent response times (last 100)
                if len(info.response_times) > 100:
                    info.response_times = info.response_times[-100:]

            # Update global response times
            self._response_times.append(response_time)
            if len(self._response_times) > 1000:
                self._response_times = self._response_times[-1000:]

            # Update average response time
            if self._response_times:
                self._stats.average_response_time = sum(self._response_times) / len(self._response_times)

    def get_stats(self) -> PoolStats:
        """Get current pool statistics."""
        self._stats.idle_connections = len(self._connections) - len(self._active_connections)
        return self._stats

    def get_connection_info(self) -> Dict[str, Dict[str, any]]:
        """Get detailed connection information."""
        info = {}

        for key, conn_info in self._connection_info.items():
            avg_response_time = 0.0
            if conn_info.response_times:
                avg_response_time = sum(conn_info.response_times) / len(conn_info.response_times)

            info[key] = {
                "url": conn_info.url,
                "created_at": conn_info.created_at,
                "last_used": conn_info.last_used,
                "request_count": conn_info.request_count,
                "error_count": conn_info.error_count,
                "error_rate": conn_info.error_count / max(conn_info.request_count, 1),
                "is_healthy": conn_info.is_healthy,
                "is_active": key in self._active_connections,
                "average_response_time": avg_response_time,
            }

        return info

    async def close(self) -> None:
        """Close the connection pool and all connections."""
        if self._is_closed:
            return

        self.logger.info("Closing connection pool")
        self._is_closed = True

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        async with self._lock:
            for key in list(self._connections.keys()):
                await self._close_connection(key)

        self.logger.info("Connection pool closed")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ConnectionPool("
            f"connections={len(self._connections)}, "
            f"active={len(self._active_connections)}, "
            f"max={self.max_connections}"
            f")"
        )
