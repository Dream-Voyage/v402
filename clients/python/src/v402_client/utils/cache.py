"""
Response caching utilities.
"""

from cachetools import TTLCache
from typing import Optional
from v402_client.types.models import PaymentResponse


class ResponseCache:
    """TTL-based response cache."""

    def __init__(self, max_size: int, ttl: int, logger):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)
        self.logger = logger

    async def get(self, key: str) -> Optional[PaymentResponse]:
        """Get cached response."""
        return self.cache.get(key)

    async def set(self, key: str, response: PaymentResponse):
        """Cache response."""
        self.cache[key] = response
        self.logger.debug(f"Cached response for {key}")

    async def close(self):
        """Close cache."""
        self.cache.clear()
