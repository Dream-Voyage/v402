"""
Prometheus metrics collection.
"""

from prometheus_client import Counter, Histogram, start_http_server
from typing import Dict


class MetricsCollector:
    """Prometheus metrics collector for v402 client."""

    def __init__(self, port: int, path: str):
        self.port = port
        self.path = path
        self.server = None

        # Define metrics
        self.requests_total = Counter(
            'v402_requests_total',
            'Total number of requests',
            ['method', 'status']
        )

        self.payments_total = Counter(
            'v402_payments_total',
            'Total number of payments',
            ['network']
        )

        self.request_duration = Histogram(
            'v402_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'status']
        )

        self.cache_hits = Counter(
            'v402_cache_hits_total',
            'Total cache hits'
        )

    def start(self):
        """Start metrics server."""
        if not self.server:
            self.server = start_http_server(self.port)

    def stop(self):
        """Stop metrics server."""
        if self.server:
            self.server.shutdown()
            self.server = None

    def increment_counter(self, name: str, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        if name == 'requests_total':
            self.requests_total.labels(**(labels or {})).inc()
        elif name == 'payments_total':
            self.payments_total.labels(**(labels or {})).inc()
        elif name == 'cache_hits_total':
            self.cache_hits.inc()

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram metric."""
        if name == 'request_duration_seconds':
            self.request_duration.labels(**(labels or {})).observe(value)
