"""
Batch Processing Example with v402

Demonstrates batch processing of multiple URLs with:
- Concurrent processing
- Payment batching
- Error handling and retries
- Statistics and reporting
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    batch_size: int = 10
    max_concurrent: int = 5
    timeout: int = 30
    retry_max: int = 3
    retry_delay: float = 1.0


class BatchV402Client:
    """Batch processing client for v402."""

    def __init__(self, public_key: str, config: BatchConfig):
        self.public_key = public_key
        self.config = config
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "payments_made": 0,
            "total_amount": 0,
        }

    async def process_batch(self, urls: List[str]) -> Dict[str, Any]:
        """
        Process a batch of URLs.

        Args:
            urls: List of URLs to process

        Returns:
            Dict with processing results and statistics
        """
        logger.info(f"Processing batch of {len(urls)} URLs")
        start_time = datetime.now()

        # Process URLs in batches
        for i in range(0, len(urls), self.config.batch_size):
            batch = urls[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            total_batches = (len(urls) + self.config.batch_size - 1) // self.config.batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches}")

            # Process batch with concurrency limit
            semaphore = asyncio.Semaphore(self.config.max_concurrent)

            async def process_with_limit(url):
                async with semaphore:
                    return await self.process_url_with_retry(url)

            batch_results = await asyncio.gather(
                *[process_with_limit(url) for url in batch],
                return_exceptions=True
            )

            # Update statistics
            for result in batch_results:
                if isinstance(result, Exception):
                    self.stats["failed"] += 1
                else:
                    self.stats["total_processed"] += 1
                    if result.get("success"):
                        self.stats["successful"] += 1
                        if result.get("payment_made"):
                            self.stats["payments_made"] += 1
                            self.stats["total_amount"] += result.get("payment_amount", 0)
                    else:
                        self.stats["failed"] += 1

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "duration_seconds": duration,
            "throughput": len(urls) / duration,
            "statistics": self.stats,
        }

    async def process_url_with_retry(self, url: str) -> Dict[str, Any]:
        """
        Process a single URL with retry logic.

        Args:
            url: URL to process

        Returns:
            Dict with processing result
        """
        for attempt in range(self.config.retry_max):
            try:
                return await self.process_url(url)
            except Exception as e:
                if attempt < self.config.retry_max - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}, retrying...")
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All attempts failed for {url}: {e}")
                    return {
                        "url": url,
                        "success": False,
                        "error": str(e),
                        "attempts": attempt + 1,
                    }

        return {"success": False, "error": "Max retries exceeded"}

    async def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a single URL.

        Args:
            url: URL to process

        Returns:
            Dict with processing result
        """
        # Simulate processing
        await asyncio.sleep(0.1)

        # Simulate payment decision
        payment_made = False
        payment_amount = 0

        return {
            "url": url,
            "success": True,
            "payment_made": payment_made,
            "payment_amount": payment_amount,
            "content_length": 1024,
        }


async def main():
    """Main example function."""
    # Example URLs to process
    urls = [
        f"https://example.com/article-{i}"
        for i in range(1, 51)
    ]

    # Configure batch processing
    config = BatchConfig(
        batch_size=10,
        max_concurrent=5,
        timeout=30,
    )

    # Create client
    client = BatchV402Client(
        public_key="0x1234567890abcdef1234567890abcdef12345678",
        config=config
    )

    # Process batch
    results = await client.process_batch(urls)

    # Print results
    print("\n=== Batch Processing Results ===")
    print(f"Duration: {results['duration_seconds']:.2f}s")
    print(f"Throughput: {results['throughput']:.2f} req/s")
    print(f"\nStatistics:")
    for key, value in results['statistics'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())

