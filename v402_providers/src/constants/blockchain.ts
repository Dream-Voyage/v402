/**
 * V402 Providers SDK - Blockchain Constants
 * 
 * This file contains all blockchain-related constants including
 * chain IDs, network configurations, contract addresses, and
 * blockchain-specific parameters for multi-chain support.
 * 
 * @author V402 Team
 * @version 1.0.0
 * @since 2024-01-01
 */

/**
 * Supported blockchain networks
 */
export const BLOCKCHAIN_NETWORKS = {
  ETHEREUM: 'ethereum',
  POLYGON: 'polygon',
  BSC: 'bsc',
  ARBITRUM: 'arbitrum',
  OPTIMISM: 'optimism',
  BASE: 'base',
  AVALANCHE: 'avalanche',
  FANTOM: 'fantom',
  SOLANA: 'solana',
  NEAR: 'near',
  COSMOS: 'cosmos',
  POLKADOT: 'polkadot',
} as const;

/**
 * Chain IDs for EVM-compatible networks
 */
export const CHAIN_IDS = {
  // Ethereum
  ETHEREUM_MAINNET: 1,
  ETHEREUM_GOERLI: 5,
  ETHEREUM_SEPOLIA: 11155111,
  
  // Polygon
  POLYGON_MAINNET: 137,
  POLYGON_MUMBAI: 80001,
  
  // Binance Smart Chain
  BSC_MAINNET: 56,
  BSC_TESTNET: 97,
  
  // Arbitrum
  ARBITRUM_ONE: 42161,
  ARBITRUM_NOVA: 42170,
  ARBITRUM_GOERLI: 421613,
  
  // Optimism
  OPTIMISM_MAINNET: 10,
  OPTIMISM_GOERLI: 420,
  
  // Base
  BASE_MAINNET: 8453,
  BASE_GOERLI: 84531,
  
  // Avalanche
  AVALANCHE_C_CHAIN: 43114,
  AVALANCHE_FUJI: 43113,
  
  // Fantom
  FANTOM_OPERA: 250,
  FANTOM_TESTNET: 4002,
} as const;

/**
 * RPC endpoints for different networks
 */
export const RPC_ENDPOINTS = {
  ETHEREUM: {
    MAINNET: [
      'https://mainnet.infura.io/v3/{API_KEY}',
      'https://eth-mainnet.alchemyapi.io/v2/{API_KEY}',
      'https://rpc.ankr.com/eth',
    ],
    GOERLI: [
      'https://goerli.infura.io/v3/{API_KEY}',
      'https://eth-goerli.alchemyapi.io/v2/{API_KEY}',
    ],
    SEPOLIA: [
      'https://sepolia.infura.io/v3/{API_KEY}',
      'https://eth-sepolia.g.alchemy.com/v2/{API_KEY}',
    ],
  },
  POLYGON: {
    MAINNET: [
      'https://polygon-mainnet.infura.io/v3/{API_KEY}',
      'https://polygon-mainnet.g.alchemy.com/v2/{API_KEY}',
      'https://rpc.ankr.com/polygon',
    ],
    MUMBAI: [
      'https://polygon-mumbai.infura.io/v3/{API_KEY}',
      'https://polygon-mumbai.g.alchemy.com/v2/{API_KEY}',
    ],
  },
  BSC: {
    MAINNET: [
      'https://bsc-dataseed1.binance.org',
      'https://bsc-dataseed2.binance.org',
      'https://rpc.ankr.com/bsc',
    ],
    TESTNET: [
      'https://data-seed-prebsc-1-s1.binance.org:8545',
      'https://data-seed-prebsc-2-s1.binance.org:8545',
    ],
  },
  ARBITRUM: {
    ONE: [
      'https://arbitrum-mainnet.infura.io/v3/{API_KEY}',
      'https://arb-mainnet.g.alchemy.com/v2/{API_KEY}',
      'https://rpc.ankr.com/arbitrum',
    ],
    NOVA: [
      'https://nova.arbitrum.io/rpc',
    ],
    GOERLI: [
      'https://arbitrum-goerli.infura.io/v3/{API_KEY}',
    ],
  },
  OPTIMISM: {
    MAINNET: [
      'https://optimism-mainnet.infura.io/v3/{API_KEY}',
      'https://opt-mainnet.g.alchemy.com/v2/{API_KEY}',
      'https://rpc.ankr.com/optimism',
    ],
    GOERLI: [
      'https://optimism-goerli.infura.io/v3/{API_KEY}',
    ],
  },
  BASE: {
    MAINNET: [
      'https://mainnet.base.org',
      'https://base-mainnet.g.alchemy.com/v2/{API_KEY}',
    ],
    GOERLI: [
      'https://goerli.base.org',
    ],
  },
  SOLANA: {
    MAINNET: [
      'https://api.mainnet-beta.solana.com',
      'https://solana-api.projectserum.com',
    ],
    DEVNET: [
      'https://api.devnet.solana.com',
    ],
    TESTNET: [
      'https://api.testnet.solana.com',
    ],
  },
} as const;

/**
 * V402 Contract Addresses per network
 */
export const V402_CONTRACTS = {
  ETHEREUM: {
    MAINNET: {
      PAYMENT_PROCESSOR: '0x1234567890123456789012345678901234567890',
      TOKEN_REGISTRY: '0x2345678901234567890123456789012345678901',
      ESCROW: '0x3456789012345678901234567890123456789012',
    },
    GOERLI: {
      PAYMENT_PROCESSOR: '0x4567890123456789012345678901234567890123',
      TOKEN_REGISTRY: '0x5678901234567890123456789012345678901234',
      ESCROW: '0x6789012345678901234567890123456789012345',
    },
  },
  POLYGON: {
    MAINNET: {
      PAYMENT_PROCESSOR: '0x7890123456789012345678901234567890123456',
      TOKEN_REGISTRY: '0x8901234567890123456789012345678901234567',
      ESCROW: '0x9012345678901234567890123456789012345678',
    },
    MUMBAI: {
      PAYMENT_PROCESSOR: '0x0123456789012345678901234567890123456789',
      TOKEN_REGISTRY: '0x1234567890123456789012345678901234567890',
      ESCROW: '0x2345678901234567890123456789012345678901',
    },
  },
  BSC: {
    MAINNET: {
      PAYMENT_PROCESSOR: '0x3456789012345678901234567890123456789012',
      TOKEN_REGISTRY: '0x4567890123456789012345678901234567890123',
      ESCROW: '0x5678901234567890123456789012345678901234',
    },
    TESTNET: {
      PAYMENT_PROCESSOR: '0x6789012345678901234567890123456789012345',
      TOKEN_REGISTRY: '0x7890123456789012345678901234567890123456',
      ESCROW: '0x8901234567890123456789012345678901234567',
    },
  },
} as const;

/**
 * Gas configuration per network
 */
export const GAS_CONFIGS = {
  ETHEREUM: {
    STANDARD: {
      gasLimit: '21000',
      gasPrice: '20000000000', // 20 Gwei
      maxFeePerGas: '30000000000', // 30 Gwei
      maxPriorityFeePerGas: '2000000000', // 2 Gwei
    },
    FAST: {
      gasLimit: '21000',
      gasPrice: '40000000000', // 40 Gwei
      maxFeePerGas: '60000000000', // 60 Gwei
      maxPriorityFeePerGas: '4000000000', // 4 Gwei
    },
  },
  POLYGON: {
    STANDARD: {
      gasLimit: '21000',
      gasPrice: '30000000000', // 30 Gwei
      maxFeePerGas: '40000000000', // 40 Gwei
      maxPriorityFeePerGas: '30000000000', // 30 Gwei
    },
    FAST: {
      gasLimit: '21000',
      gasPrice: '50000000000', // 50 Gwei
      maxFeePerGas: '70000000000', // 70 Gwei
      maxPriorityFeePerGas: '50000000000', // 50 Gwei
    },
  },
  BSC: {
    STANDARD: {
      gasLimit: '21000',
      gasPrice: '5000000000', // 5 Gwei
    },
    FAST: {
      gasLimit: '21000',
      gasPrice: '10000000000', // 10 Gwei
    },
  },
} as const;

/**
 * Block confirmation requirements
 */
export const CONFIRMATION_BLOCKS = {
  ETHEREUM: {
    SAFE: 12,
    FAST: 6,
    INSTANT: 1,
  },
  POLYGON: {
    SAFE: 20,
    FAST: 10,
    INSTANT: 1,
  },
  BSC: {
    SAFE: 10,
    FAST: 5,
    INSTANT: 1,
  },
  ARBITRUM: {
    SAFE: 1,
    FAST: 1,
    INSTANT: 1,
  },
  OPTIMISM: {
    SAFE: 1,
    FAST: 1,
    INSTANT: 1,
  },
  BASE: {
    SAFE: 1,
    FAST: 1,
    INSTANT: 1,
  },
} as const;

/**
 * Native token symbols
 */
export const NATIVE_TOKENS = {
  ETHEREUM: 'ETH',
  POLYGON: 'MATIC',
  BSC: 'BNB',
  ARBITRUM: 'ETH',
  OPTIMISM: 'ETH',
  BASE: 'ETH',
  AVALANCHE: 'AVAX',
  FANTOM: 'FTM',
  SOLANA: 'SOL',
} as const;

/**
 * Supported ERC standards
 */
export const ERC_STANDARDS = {
  ERC20: 'ERC20',
  ERC721: 'ERC721',
  ERC1155: 'ERC1155',
  ERC777: 'ERC777',
  ERC4626: 'ERC4626',
} as const;

/**
 * Wallet connection types
 */
export const WALLET_TYPES = {
  METAMASK: 'metamask',
  WALLETCONNECT: 'walletconnect',
  COINBASE_WALLET: 'coinbase_wallet',
  TRUST_WALLET: 'trust_wallet',
  RAINBOW: 'rainbow',
  PHANTOM: 'phantom', // Solana
  SOLFLARE: 'solflare', // Solana
  NEAR_WALLET: 'near_wallet', // Near
  KEPLR: 'keplr', // Cosmos
  POLKADOT_JS: 'polkadot_js', // Polkadot
} as const;

/**
 * Transaction types
 */
export const TRANSACTION_TYPES = {
  LEGACY: 0,
  ACCESS_LIST: 1,
  FEE_MARKET: 2,
} as const;

/**
 * Block explorer URLs
 */
export const BLOCK_EXPLORERS = {
  ETHEREUM: {
    MAINNET: 'https://etherscan.io',
    GOERLI: 'https://goerli.etherscan.io',
    SEPOLIA: 'https://sepolia.etherscan.io',
  },
  POLYGON: {
    MAINNET: 'https://polygonscan.com',
    MUMBAI: 'https://mumbai.polygonscan.com',
  },
  BSC: {
    MAINNET: 'https://bscscan.com',
    TESTNET: 'https://testnet.bscscan.com',
  },
  ARBITRUM: {
    ONE: 'https://arbiscan.io',
    NOVA: 'https://nova.arbiscan.io',
    GOERLI: 'https://goerli.arbiscan.io',
  },
  OPTIMISM: {
    MAINNET: 'https://optimistic.etherscan.io',
    GOERLI: 'https://goerli-optimism.etherscan.io',
  },
  BASE: {
    MAINNET: 'https://basescan.org',
    GOERLI: 'https://goerli.basescan.org',
  },
  SOLANA: {
    MAINNET: 'https://explorer.solana.com',
    DEVNET: 'https://explorer.solana.com/?cluster=devnet',
    TESTNET: 'https://explorer.solana.com/?cluster=testnet',
  },
} as const;

export type BlockchainNetwork = typeof BLOCKCHAIN_NETWORKS[keyof typeof BLOCKCHAIN_NETWORKS];
export type ChainId = typeof CHAIN_IDS[keyof typeof CHAIN_IDS];
export type NativeToken = typeof NATIVE_TOKENS[keyof typeof NATIVE_TOKENS];
export type ErcStandard = typeof ERC_STANDARDS[keyof typeof ERC_STANDARDS];
export type WalletType = typeof WALLET_TYPES[keyof typeof WALLET_TYPES];
export type TransactionType = typeof TRANSACTION_TYPES[keyof typeof TRANSACTION_TYPES];
