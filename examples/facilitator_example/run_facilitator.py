"""
Example: Running the v402 Facilitator service.

This script demonstrates how to start the facilitator backend service
for payment verification and settlement.
"""

import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Run the facilitator service."""
    logger.info("Starting v402 Facilitator...")

    # Import after loading env vars
    from v402_facilitator.main import app
    from v402_facilitator.config import settings
    import uvicorn

    logger.info(f"Network: {settings.network}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Server: http://{settings.host}:{settings.port}")

    # Run server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()

