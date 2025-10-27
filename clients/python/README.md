# v402 Python SDK

**Enterprise-grade Python client for v402 multi-chain payment protocol.**

## Features

- 🚀 **High Performance**: Async-first design with connection pooling
- 🔒 **Security**: Hardware wallet support, key management
- 🌍 **Multi-Chain**: Support for EVM, Solana, BSC, Polygon
- 📊 **Monitoring**: Prometheus metrics, structured logging
- 🔄 **Resilience**: Circuit breaker, retry policies, fallback
- 🎯 **Type-Safe**: Full type hints and runtime validation

## Architecture

```
clients/python/
├── src/v402_client/
│   ├── core/                   # Core client implementation
│   │   ├── client.py          # Main V402Client class
│   │   ├── async_client.py    # Async client implementation
│   │   ├── pool.py            # Connection pool manager
│   │   └── session.py         # HTTP session management
│   ├── chains/                 # Chain-specific implementations
│   │   ├── base.py            # Abstract chain interface
│   │   ├── evm.py             # EVM chains (Ethereum, Base, etc.)
│   │   ├── solana.py          # Solana implementation
│   │   ├── bsc.py             # Binance Smart Chain
│   │   └── polygon.py         # Polygon/Matic
│   ├── payment/                # Payment processing
│   │   ├── signer.py          # Transaction signing
│   │   ├── verifier.py        # Payment verification
│   │   ├── strategies.py      # Payment selection strategies
│   │   └── history.py         # Payment history tracking
│   ├── config/                 # Configuration management
│   │   ├── settings.py        # Settings and environment
│   │   ├── chains.py          # Chain configurations
│   │   └── validation.py      # Config validation
│   ├── logging/                # Logging infrastructure
│   │   ├── logger.py          # Structured logging
│   │   ├── formatters.py      # Log formatters (JSON, etc.)
│   │   └── handlers.py        # Custom log handlers
│   ├── monitoring/             # Monitoring and metrics
│   │   ├── metrics.py         # Prometheus metrics
│   │   ├── tracing.py         # Distributed tracing
│   │   └── health.py          # Health checks
│   ├── utils/                  # Utility modules
│   │   ├── crypto.py          # Cryptographic utilities
│   │   ├── encoding.py        # Encoding/decoding helpers
│   │   ├── retry.py           # Retry logic
│   │   └── cache.py           # Caching layer
│   ├── exceptions/             # Exception hierarchy
│   │   ├── base.py            # Base exceptions
│   │   ├── payment.py         # Payment exceptions
│   │   └── chain.py           # Chain-specific exceptions
│   └── types/                  # Type definitions
│       ├── models.py          # Pydantic models
│       ├── enums.py           # Enumerations
│       └── protocols.py       # Protocol definitions
├── tests/                      # Comprehensive test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   └── performance/           # Performance benchmarks
├── examples/                   # Usage examples
├── docs/                       # Documentation
└── pyproject.toml             # Project configuration
```

## Installation

```bash
pip install v402-client-python

# With all extras
pip install v402-client-python[all]

# Production dependencies only
pip install v402-client-python[prod]
```

## Quick Start

```python
from v402_client import V402Client, ChainConfig
from v402_client.config import ClientSettings

# Basic usage
async with V402Client(
    private_key="0x...",
    chains=[ChainConfig.ETHEREUM_MAINNET, ChainConfig.BASE],
    settings=ClientSettings(
        auto_pay=True,
        max_amount_per_request="1000000",
        enable_metrics=True,
    )
) as client:
    response = await client.get("https://example.com/premium")
    print(response.json())
```

## Advanced Usage

### Multi-Chain Configuration

```python
from v402_client import V402Client
from v402_client.chains import EVMChain, SolanaChain
from v402_client.config import ChainConfig

client = V402Client(
    private_key="0x...",
    chains=[
        ChainConfig(
            name="ethereum",
            type="evm",
            rpc_url="https://eth-mainnet.g.alchemy.com/v2/...",
            chain_id=1,
            native_currency="ETH"
        ),
        ChainConfig(
            name="solana",
            type="solana",
            rpc_url="https://api.mainnet-beta.solana.com",
            native_currency="SOL"
        ),
    ]
)
```

### Custom Payment Strategy

```python
from v402_client.payment import PaymentStrategy

class LowestCostStrategy(PaymentStrategy):
    """Select payment option with lowest cost."""
    
    async def select(self, options):
        return min(options, key=lambda x: int(x.max_amount_required))

client = V402Client(
    private_key="0x...",
    payment_strategy=LowestCostStrategy()
)
```

### Monitoring & Metrics

```python
from v402_client.monitoring import PrometheusMetrics
from prometheus_client import start_http_server

# Enable Prometheus metrics
metrics = PrometheusMetrics()
client = V402Client(
    private_key="0x...",
    metrics=metrics
)

# Start metrics server
start_http_server(8000)
```

### Circuit Breaker & Retry

```python
from v402_client.config import ResilienceConfig

client = V402Client(
    private_key="0x...",
    resilience=ResilienceConfig(
        enable_circuit_breaker=True,
        failure_threshold=5,
        success_threshold=2,
        timeout=30,
        max_retries=3,
        retry_backoff=2.0
    )
)
```

## Configuration

### Environment Variables

```bash
V402_PRIVATE_KEY=0x...
V402_CHAINS=ethereum,base,polygon
V402_MAX_AMOUNT=1000000
V402_FACILITATOR_URL=https://facilitator.v402.org
V402_ENABLE_METRICS=true
V402_LOG_LEVEL=INFO
V402_LOG_FORMAT=json
```

### Configuration File

```yaml
# config.yaml
client:
  auto_pay: true
  max_amount_per_request: "1000000"
  timeout: 30
  
chains:
  - name: ethereum
    type: evm
    rpc_url: https://eth-mainnet.g.alchemy.com/v2/...
    chain_id: 1
    
  - name: solana
    type: solana
    rpc_url: https://api.mainnet-beta.solana.com

logging:
  level: INFO
  format: json
  output: stdout
  
metrics:
  enabled: true
  port: 8000
  path: /metrics
```

## API Reference

See [API Documentation](./docs/api.md)

## Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Format
black src/
```

