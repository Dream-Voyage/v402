"""
EVM chain implementation.
"""

from typing import Dict, Any
from v402_client.config.settings import ChainConfig
from web3 import Web3


class EVMChain:
    """EVM-compatible blockchain implementation."""

    def __init__(self, config: ChainConfig, logger):
        self.config = config
        self.logger = logger
        self.w3 = None

    async def initialize(self):
        """Initialize Web3 connection."""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
            if not self.w3.is_connected():
                raise Exception(f"Failed to connect to {self.config.name}")
            self.logger.info(f"Connected to {self.config.name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.config.name}: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check chain health."""
        if not self.w3:
            return {"healthy": False, "error": "Not initialized"}

        try:
            block_number = self.w3.eth.block_number
            return {"healthy": True, "block_number": block_number}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def close(self):
        """Close connection."""
        self.w3 = None
