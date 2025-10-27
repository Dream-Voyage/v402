"""
Example: End-to-end v402 workflow.

This example demonstrates the complete flow:
1. Start facilitator
2. Register content provider
3. Discover resources
4. Make payment and access content
5. Verify settlement
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class E2ETest:
    """End-to-end test orchestrator."""

    def __init__(self):
        self.facilitator_process: Optional[subprocess.Popen] = None
        self.provider_process: Optional[subprocess.Popen] = None
        self.facilitator_url = "http://localhost:8000"
        self.provider_url = "http://localhost:8001"

    async def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to be ready."""
        logger.info(f"Waiting for service at {url}...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        logger.info(f"Service at {url} is ready")
                        return True
            except:
                pass

            await asyncio.sleep(1)

        logger.error(f"Service at {url} not ready after {timeout}s")
        return False

    async def test_facilitator_health(self):
        """Test facilitator health endpoint."""
        logger.info("\n=== Testing Facilitator Health ===")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.facilitator_url}/health")
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Response: {response.json()}")

        assert response.status_code == 200

    async def test_supported_schemes(self):
        """Test supported schemes endpoint."""
        logger.info("\n=== Testing Supported Schemes ===")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.facilitator_url}/supported")
            data = response.json()

            logger.info(f"Supported schemes: {data['kinds']}")

        assert len(data["kinds"]) > 0

    async def test_content_discovery(self):
        """Test resource discovery."""
        logger.info("\n=== Testing Content Discovery ===")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.facilitator_url}/discovery/resources",
                params={"limit": 10, "offset": 0},
            )
            data = response.json()

            logger.info(f"x402 Version: {data['x402Version']}")
            logger.info(f"Total resources: {data['pagination']['total']}")
            logger.info(f"Resources found: {len(data['items'])}")

            for item in data["items"]:
                logger.info(f"  - {item['resource']}: {item['type']}")

    async def test_payment_flow(self):
        """Test complete payment flow."""
        logger.info("\n=== Testing Payment Flow ===")

        from v402_index_client import V402IndexClient

        # Initialize client
        client = V402IndexClient(
            private_key=os.getenv("PRIVATE_KEY", "0x" + "0" * 64),
            max_amount_per_request="10000000",
            network="base-sepolia",
            facilitator_url=self.facilitator_url,
            auto_pay=True,
        )

        try:
            # Test accessing free content
            logger.info("1. Accessing free content...")
            response = await client.get(f"{self.provider_url}/")
            logger.info(f"   Status: {response.status_code}")
            logger.info(f"   Payment made: {response.payment_made}")

            # Test accessing paid content
            logger.info("2. Accessing paid content...")
            response = await client.get(f"{self.provider_url}/premium-article")
            logger.info(f"   Status: {response.status_code}")
            logger.info(f"   Payment made: {response.payment_made}")

            if response.payment_made:
                logger.info(f"   Amount: {response.payment_amount} wei")
                logger.info(f"   Transaction: {response.transaction_hash}")

            # Check payment history
            logger.info("3. Checking payment history...")
            history = client.get_payment_history()
            logger.info(f"   Total payments: {len(history)}")

            for payment in history:
                logger.info(f"   - {payment.description}: {payment.amount} wei")

        finally:
            await client.close()

    async def run_tests(self):
        """Run all end-to-end tests."""
        try:
            # Wait for services to be ready
            logger.info("Checking if services are ready...")

            facilitator_ready = await self.wait_for_service(
                f"{self.facilitator_url}/health"
            )
            provider_ready = await self.wait_for_service(f"{self.provider_url}/")

            if not facilitator_ready:
                logger.error("Facilitator not ready. Please start it manually.")
                logger.info(
                    "Run: cd ../facilitator_example && python run_facilitator.py"
                )
                return False

            if not provider_ready:
                logger.error("Content provider not ready. Please start it manually.")
                logger.info(
                    "Run: cd ../content_provider_example && python fastapi_provider.py"
                )
                return False

            # Run tests
            await self.test_facilitator_health()
            await self.test_supported_schemes()
            await self.test_content_discovery()
            await self.test_payment_flow()

            logger.info("\n=== All Tests Passed! ===")
            return True

        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
            return False


async def main():
    """Run end-to-end test."""
    logger.info("Starting v402 End-to-End Test...")
    logger.info("\nPrerequisites:")
    logger.info("1. Facilitator running on port 8000")
    logger.info("2. Content provider running on port 8001")
    logger.info("\nTo start services manually:")
    logger.info("  Terminal 1: cd ../facilitator_example && python run_facilitator.py")
    logger.info(
        "  Terminal 2: cd ../content_provider_example && python fastapi_provider.py"
    )
    logger.info("\n" + "=" * 60 + "\n")

    test = E2ETest()
    success = await test.run_tests()

    if success:
        logger.info("\n✅ End-to-end test completed successfully!")
    else:
        logger.error("\n❌ End-to-end test failed!")

    return success


if __name__ == "__main__":
    asyncio.run(main())

