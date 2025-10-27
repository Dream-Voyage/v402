"""
Example: Batch processing with index client.

This example demonstrates how to efficiently crawl multiple paid
resources concurrently with automatic payment handling.
"""

import asyncio
import logging
import os
import sys
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from dotenv import load_dotenv

from v402_index_client import V402IndexClient, PaymentResponse

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def main():
    """
    Demonstrate batch processing of paid content.

    This example shows how to:
    1. Process multiple URLs concurrently
    2. Handle payments automatically for each
    3. Aggregate results and payment statistics
    """
    logger.info("Starting v402 Batch Client example...")

    # Initialize client
    client = V402IndexClient(
        private_key=os.getenv("PRIVATE_KEY", "0x" + "0" * 64),
        max_amount_per_request=os.getenv("MAX_AMOUNT_PER_REQUEST", "10000000"),
        network=os.getenv("NETWORK", "base-sepolia"),
        facilitator_url=os.getenv("FACILITATOR_URL", "http://localhost:8000"),
        auto_pay=True,
    )

    # Content provider URL
    provider_url = os.getenv("PROVIDER_URL", "http://localhost:8001")

    # List of URLs to crawl
    urls = [
        f"{provider_url}/",
        f"{provider_url}/premium-article",
        f"{provider_url}/premium-data",
        f"{provider_url}/ai-training-data",
    ]

    logger.info(f"Processing {len(urls)} URLs concurrently...")

    try:
        # Batch request with automatic payments
        responses: List[PaymentResponse] = await client.batch_get(urls, auto_pay=True)

        # Process results
        total_paid = 0
        total_cost = 0
        successful = 0
        failed = 0

        logger.info("\n=== Batch Results ===")
        for i, response in enumerate(responses):
            logger.info(f"\nURL {i + 1}: {response.url}")
            logger.info(f"  Status: {response.status_code}")
            logger.info(f"  Payment made: {response.payment_made}")

            if response.payment_made:
                total_paid += 1
                amount = int(response.payment_amount or "0")
                total_cost += amount
                logger.info(f"  Amount: {response.payment_amount} wei")
                logger.info(f"  Transaction: {response.transaction_hash}")

            if response.status_code == 200:
                successful += 1
                try:
                    content = response.json()
                    # Log key information from content
                    if "title" in content:
                        logger.info(f"  Title: {content['title']}")
                    elif "dataset" in content:
                        logger.info(f"  Dataset: {content['dataset']}")
                    elif "service" in content:
                        logger.info(f"  Service: {content['service']}")
                except:
                    logger.info(f"  Content length: {len(response.content)} bytes")
            else:
                failed += 1
                logger.warning(f"  Failed to access content")

        # Summary statistics
        logger.info("\n=== Summary Statistics ===")
        logger.info(f"Total URLs processed: {len(responses)}")
        logger.info(f"Successful requests: {successful}")
        logger.info(f"Failed requests: {failed}")
        logger.info(f"Payments made: {total_paid}")
        logger.info(f"Total cost: {total_cost} wei")
        logger.info(f"Average cost per paid request: {total_cost // total_paid if total_paid > 0 else 0} wei")

        # Payment history
        logger.info("\n=== Full Payment History ===")
        history = client.get_payment_history()
        for payment in history:
            logger.info(
                f"{payment.timestamp.isoformat()} - "
                f"{payment.description}: {payment.amount} wei - "
                f"{'SUCCESS' if payment.success else 'FAILED'}"
            )

    except Exception as e:
        logger.error(f"Error during batch processing: {e}", exc_info=True)

    finally:
        await client.close()
        logger.info("\nClient closed")


if __name__ == "__main__":
    asyncio.run(main())

