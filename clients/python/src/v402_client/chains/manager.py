"""
Multi-chain manager for v402 client.
"""

import asyncio
from typing import Dict, List, Any
from v402_client.chains.evm import EVMChain
from v402_client.chains.solana import SolanaChain
from v402_client.config.settings import ChainConfig
from v402_client.exceptions.chain import UnsupportedChain
from v402_client.types.enums import ChainType


class ChainManager:
    """Manages multiple blockchain connections."""

    def __init__(self, chains: List[ChainConfig], logger):
        self.chains = {}
        self.logger = logger

        for chain_config in chains:
            if chain_config.type == ChainType.EVM:
                self.chains[chain_config.name] = EVMChain(chain_config, logger)
            elif chain_config.type == ChainType.SOLANA:
                self.chains[chain_config.name] = SolanaChain(chain_config, logger)
            else:
                raise UnsupportedChain(chain_config.name)

    async def initialize(self):
        """Initialize all chains."""
        tasks = [chain.initialize() for chain in self.chains.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all chains."""
        health = {}
        for name, chain in self.chains.items():
            health[name] = await chain.health_check()
        return health

    async def close(self):
        """Close all chain connections."""
        tasks = [chain.close() for chain in self.chains.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
