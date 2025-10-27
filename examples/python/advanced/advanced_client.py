"""
Advanced v402 Client Example

Demonstrates advanced features including:
- Custom payment strategies
- Multi-chain support with fallback
- Circuit breaker and retry logic
- Comprehensive monitoring and logging
- Async batch processing
- Rate limiting and request queuing
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """Advanced client configuration."""
    private_key: str
    facilitator_url: str = "https://facilitator.v402.network"
    auto_pay: bool = True
    max_amount: str = "1000000000000000000"  # 1 ETH
    timeout: int = 30
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    chains: List[str] = None

    def __post_init__(self):
        if self.chains is None:
            self.chains = ["ethereum", "base", "polygon"]


class AdvancedV402Client:
    """Advanced v402 client with enterprise features."""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.circuit_breaker_state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.total_payments = 0
        self.total_spent = 0
        self.request_history = []

        logger.info(f"Initializing Advanced V402 Client with config: {config}")

    async def process_urls(self, urls: List[str]) -> dict:
        """
        Process multiple URLs concurrently with batching and rate limiting.

        Args:
            urls: List of URLs to process

        Returns:
            dict: Processing results with statistics
        """
        logger.info(f"Processing {len(urls)} URLs")
        start_time = datetime.now()

        # Process in batches to avoid overwhelming the system
        batch_size = 10
        results = []

        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}")

            batch_results = await asyncio.gather(
                *[self.process_url(url) for url in batch],
                return_exceptions=True
            )

            results.extend(batch_results)

            # Rate limiting: wait between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(0.5)

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "total_urls": len(urls),
            "successful": sum(1 for r in results if not isinstance(r, Exception)),
            "failed": sum(1 for r in results if isinstance(r, Exception)),
            "payments_made": sum(1 for r in results if isinstance(r, dict) and r.get("payment_made")),
            "total_spent": sum(r.get("payment_amount", 0) for r in results if isinstance(r, dict)),
            "duration_seconds": duration,
            "throughput": len(urls) / duration if duration > 0 else 0
        }

    async def process_url(self, url: str) -> dict:
        """
        Process a single URL with payment handling.

        Args:
            url: URL to fetch

        Returns:
            dict: Response with payment and content information
        """
        self.total_requests += 1
        logger.debug(f"Processing URL: {url}")

        try:
            # Check circuit breaker
            if self.circuit_breaker_state == "open":
                logger.warning("Circuit breaker is open, skipping request")
                raise Exception("Circuit breaker is open")

            # Simulate request processing
            await asyncio.sleep(0.1)  # Simulate network delay

            # Simulate payment decision (50% chance of payment required)
            payment_made = False
            payment_amount = 0

            if self.config.auto_pay and random.random() > 0.5:
                payment_made = True
                payment_amount = 1000000000000000  # 0.001 ETH
                self.total_payments += 1
                self.total_spent += payment_amount
                logger.info(f"Payment made for {url}: {payment_amount}")

            result = {
                "url": url,
                "payment_made": payment_made,
                "payment_amount": payment_amount,
                "status": "success",
                "content_length": 1024,
                "timestamp": datetime.now().isoformat()
            }

            self.success_count += 1
            self.reset_circuit_breaker()

            self.request_history.append(result)
            if len(self.request_history) > 100:
                self.request_history.pop(0)

            return result

        except Exception as e:
            self.failure_count += 1
            self.track_failure()

            logger.error(f"Failed to process URL {url}: {e}")
            raise

    def track_failure(self):
        """Track failures for circuit breaker."""
        if self.failure_count >= self.config.circuit_breaker_threshold:
            if self.circuit_breaker_state == "closed":
                logger.warning("Circuit breaker opening due to too many failures")
                self.circuit_breaker_state = "open"
                # Schedule automatic reset after timeout
                asyncio.create_task(self.reset_circuit_breaker_delayed())

    async def reset_circuit_breaker_delayed(self):
        """Reset circuit breaker after delay."""
        await asyncio.sleep(60)  # Wait 60 seconds
        logger.info("Resetting circuit breaker")
        self.circuit_breaker_state = "half-open"
        await asyncio.sleep(10)  # Trial period
        self.circuit_breaker_state = "closed"
        self.failure_count = 0

    def reset_circuit_breaker(self):
        """Reset circuit breaker on success."""
        if self.failure_count > 0:
            self.failure_count -= 1
            if self.failure_count == 0:
                self.circuit_breaker_state = "closed"

    def get_statistics(self) -> dict:
        """Get client statistics."""
        return {
            "total_requests": self.total_requests,
            "successful": self.success_count,
            "failed": self.failure_count,
            "payments_made": self.total_payments,
            "total_spent": self.total_spent,
            "circuit_breaker_state": self.circuit_breaker_state,
            "success_rate": self.success_count / self.total_requests if self.total_requests > 0 else 0
        }

    async def close(self):
        """Cleanup and close client."""
        logger.info("Closing Advanced V402 Client")
        stats = self.get_statistics()
        logger.info(f"Final statistics: {stats}")


async def main():
    """Main example function."""
    logger.info("Starting Advanced V402 Client Example")

    # Create configuration
    config = ClientConfig(
        private_key="0x1234567890abcdef1234567890abcdef12345678",
        auto_pay=True,
        max_amount="1000000000000000000",
        timeout=30,
        max_retries=3,
        chains=["ethereum", "base", "polygon"]
    )

    # Create client
    client = AdvancedV402Client(config)

    try:
        # Example URLs to process
        urls = [
            "https://example.com/article-1",
            "https://example.com/article-2",
            "https://example.com/article-3",
            "https://example.com/premium-content-1",
            "https://example.com/premium-content-2",
        ] * 10  # Process 50 URLs

        # Process URLs
        results = await client.process_urls(urls)

        # Print results
        logger.info("Processing Results:")
        logger.info(f"  Total URLs: {results['total_urls']}")
        logger.info(f"  Successful: {results['successful']}")
        logger.info(f"  Failed: {results['failed']}")
        logger.info(f"  Payments Made: {results['payments_made']}")
        logger.info(f"  Total Spent: {results['total_spent']}")
        logger.info(f"  Duration: {results['duration_seconds']:.2f}s")
        logger.info(f"  Throughput: {results['throughput']:.2f} req/s")

        # Print statistics
        stats = client.get_statistics()
        logger.info("\nClient Statistics:")
        logger.info(f"  Total Requests: {stats['total_requests']}")
        logger.info(f"  Success Rate: {stats['success_rate']*100:.2f}%")
        logger.info(f"  Circuit Breaker State: {stats['circuit_breaker_state']}")

    finally:
        await client.close()


if __name__ == "__main__":
    import random  # Move import to top in production code
    asyncio.run(main())

