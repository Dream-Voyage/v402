"""
Basic v402 Client Example

Demonstrates basic usage of v402 client for fetching premium content.
"""

import asyncio
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BasicV402Client:
    """Basic v402 client example."""
    
    def __init__(self, public_key: str, facilitator_url: str = "https://facilitator.v402.network"):
        """
        Initialize v402 client.
        
        Args:
            public_key: Your blockchain public key
            facilitator_url: v402 facilitator base URL
        """
        self.public_key = public_key
        self.facilitator_url = facilitator_url
        self.session = None
        logger.info(f"Initializing Basic V402 Client with public key: {public_key[:10]}...")
        
    async def fetch_content(self, content_url: str) -> dict:
        """
        Fetch content from v402-protected URL.
        
        Args:
            content_url: URL to fetch
            
        Returns:
            dict: Response with content and payment information
        """
        logger.info(f"Fetching content from: {content_url}")
        
        try:
            # Simulate API call with public key authentication
            # In real implementation, this would make HTTP request to v402 facilitator
            
            # Simulate payment (50% chance)
            payment_made = False
            payment_amount = 0
            
            # Simulate response
            result = {
                "url": content_url,
                "content": "This is premium content...",
                "payment_made": payment_made,
                "payment_amount": payment_amount,
                "transaction_hash": None,
                "status": "success"
            }
            
            logger.info(f"Successfully fetched content from {content_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch content: {e}")
            raise
    
    async def fetch_multiple(self, urls: List[str]) -> List[dict]:
        """
        Fetch multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            List of response dictionaries
        """
        logger.info(f"Fetching {len(urls)} URLs concurrently")
        
        tasks = [self.fetch_content(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if not isinstance(r, Exception) else {"error": str(r)}
            for r in results
        ]
    
    async def close(self):
        """Close client connections."""
        logger.info("Closing Basic V402 Client")


async def main():
    """Main example function."""
    logger.info("Starting Basic V402 Client Example")
    
    # Initialize client with your public key
    client = BasicV402Client(
        public_key="0x1234567890abcdef1234567890abcdef12345678",
        facilitator_url="https://facilitator.v402.network"
    )
    
    try:
        # Example URLs
        urls = [
            "https://example.com/article-1",
            "https://example.com/article-2",
            "https://example.com/premium-content-1",
            "https://example.com/premium-content-2",
        ]
        
        # Fetch URLs
        results = await client.fetch_multiple(urls)
        
        # Print results
        print("\n=== Fetch Results ===")
        for i, result in enumerate(results, 1):
            if "error" in result:
                print(f"\n❌ URL {i}: Error - {result['error']}")
            else:
                payment_status = "✅ Paid" if result.get("payment_made") else "Free"
                print(f"\n✓ URL {i}: {result['url']}")
                print(f"  Status: {result.get('status')}")
                print(f"  Payment: {payment_status}")
                if result.get("payment_amount"):
                    print(f"  Amount: {result['payment_amount']} wei")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

