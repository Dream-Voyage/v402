"""
Example: Basic index client for accessing paid content.

This example shows how AI platforms and crawlers can automatically
handle payments when accessing premium content.
"""

import asyncio
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from dotenv import load_dotenv

from v402_index_client import V402IndexClient

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def main():
    """
    Demonstrate basic client usage.

    This example:
    1. Initializes the client with credentials
    2. Makes requests to paid endpoints
    3. Automatically handles payment
    4. Displays content and payment info
    """
    logger.info("Starting v402 Index Client example...")

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

    logger.info(f"Client initialized for network: {os.getenv('NETWORK')}")
    logger.info(f"Provider URL: {provider_url}")

    try:
        # Example 1: Access free content (no payment)
        logger.info("\n=== Example 1: Free Content ===")
        response = await client.get(f"{provider_url}/")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Payment made: {response.payment_made}")
        logger.info(f"Content: {response.json()}")

        # Example 2: Access paid content (automatic payment)
        logger.info("\n=== Example 2: Premium Article (Paid) ===")
        response = await client.get(f"{provider_url}/premium-article")

        logger.info(f"Status: {response.status_code}")
        logger.info(f"Payment made: {response.payment_made}")

        if response.payment_made:
            logger.info(f"Payment amount: {response.payment_amount} wei")
            logger.info(f"Transaction: {response.transaction_hash}")
            logger.info(f"Network: {response.network}")

        if response.status_code == 200:
            content = response.json()
            logger.info(f"Article title: {content.get('title')}")
            logger.info(f"Author: {content.get('author')}")
            logger.info(f"Content preview: {content.get('content')[:100]}...")
        else:
            logger.error(f"Failed to access content: {response.status_code}")

        # Example 3: Access another paid endpoint
        logger.info("\n=== Example 3: Premium Data (Paid) ===")
        response = await client.get(f"{provider_url}/premium-data")

        logger.info(f"Status: {response.status_code}")
        logger.info(f"Payment made: {response.payment_made}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Dataset: {data.get('dataset')}")
            logger.info(f"Records: {data.get('records')}")
            logger.info(f"Format: {data.get('format')}")

        # Example 4: Check payment requirements without paying
        logger.info("\n=== Example 4: Check Payment Requirements ===")
        try:
            requirements = await client.get_payment_requirements(
                f"{provider_url}/ai-training-data"
            )
            logger.info(f"URL: {requirements.url}")
            logger.info(f"Description: {requirements.description}")
            logger.info(f"Min amount: {requirements.min_amount} wei")
            logger.info(f"Max amount: {requirements.max_amount} wei")
            logger.info(f"Supported networks: {requirements.supported_networks}")
            logger.info(f"Supported schemes: {requirements.supported_schemes}")
        except Exception as e:
            logger.error(f"Error getting requirements: {e}")

        # Example 5: View payment history
        logger.info("\n=== Example 5: Payment History ===")
        history = client.get_payment_history()

        logger.info(f"Total payments made: {len(history)}")
        for payment in history:
            logger.info(
                f"  - {payment.url}: {payment.amount} wei "
                f"(tx: {payment.transaction_hash[:10]}...)"
            )

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

    finally:
        # Clean up
        await client.close()
        logger.info("\nClient closed")


if __name__ == "__main__":
    asyncio.run(main())

