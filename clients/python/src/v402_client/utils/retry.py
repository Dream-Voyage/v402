"""
Retry logic with exponential backoff.
"""

import asyncio
import random
from typing import Callable, Any


class RetryManager:
    """Advanced retry manager with exponential backoff."""

    def __init__(self, max_retries: int, backoff_multiplier: float, jitter: bool, logger):
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.logger = logger

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                delay = self._calculate_delay(attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = (self.backoff_multiplier ** attempt)
        
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)
        
        return min(delay, 60.0)  # Max 60 seconds
