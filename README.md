# v402 Framework

**A next-generation multi-chain framework for agent-based content monetization built on the x402 protocol.**

## 🌟 Overview

In the era of AI explosion, v402 provides a foundational solution for **"low-cost paid distribution of premium content"**, creating a virtuous cycle among creators, platforms, and the AI ecosystem.

v402 is built on the **x402 protocol** and extends it with multi-language SDK support and multi-chain capabilities.

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    v402 Ecosystem                          │
│      Multi-Chain Framework on x402 Protocol                │
│                                                            │
│  ┌─────────────────┐              ┌──────────────────┐     │
│  │ Index Clients   │              │ Content Provider │     │
│  │ (AI/Crawlers)   │              │  (UGC Websites)  │     │
│  │                 │              │                  │     │
│  │ • Python SDK    │◄─X-PAYMENT── ┤ • JavaScript/TS  │     │
│  │ • Go SDK        │              │ • React Component│     │
│  │ • Java SDK      │  402 Resp──► │ • Vue Plugin     │     │
│  │ • Rust SDK      │              │ • Web Component  │     │
│  └────────┬────────┘              └─────────┬────────┘     │
│           │                                 │              │
│           │         v402_facilitator        │              │
│           │    (x402 Protocol Service)      │              │
│           └────────────┬────────────────────┘              │
│                        │                                   │
│              Multi-Chain Support                           │
│   ┌─────────┬──────────┼──────────┬──────────┐             │
│   ▼         ▼          ▼          ▼          ▼             │
│  EVM     Solana      BSC      Polygon    Arbitrum          │
└────────────────────────────────────────────────────────────┘
```

## 🚀 Components

### 1. v402_index_client (Multi-Language SDKs)

Payment client SDKs for AI/crawler platforms in multiple languages:

#### 🐍 [Python SDK](./clients/python/)
- Enterprise-grade async client
- Advanced payment strategies
- Comprehensive logging & monitoring
- Production-ready configuration

#### 🔵 [Go SDK](./clients/go/)
- High-performance concurrent processing
- Native goroutine support
- Structured logging with zap
- Context-aware request handling

#### ☕ [Java SDK](./clients/java/)
- Spring Boot integration
- Reactive programming with Project Reactor
- Comprehensive metrics with Micrometer
- Enterprise patterns (Circuit Breaker, Retry)

#### 🦀 [Rust SDK](./clients/rust/)
- Zero-cost abstractions
- Memory-safe operations
- Tokio async runtime
- Type-safe blockchain interactions

#### 🌐 [HTTP API](./API_DOCUMENTATION.md)
- **Direct REST API integration** - No SDK required
- Use your blockchain **public key** as credentials
- Pay with **x402 payment tokens** on-chain for each request
- All transactions recorded on-chain for verifiable accounting
- Perfect for custom integrations, mobile apps, or any programming language

### 2. v402_providers (JavaScript/TypeScript Components)

Enterprise-grade SDK for content creators and UGC platforms:

#### 📦 [Core SDK](./v402_providers/)
- Framework-agnostic core library
- Comprehensive API client for V402 facilitator
- Product management, analytics, and revenue tracking
- Advanced caching, retry logic, and monitoring

#### ⚛️ [React Integration](./v402_providers/src/integrations/react/)
- React hooks (`useV402Provider`, `useProducts`, `usePayments`)
- Pre-built React components (`<V402PaymentButton>`, `<V402ProductCard>`)
- TypeScript definitions
- Next.js integration support

#### 💚 [Vue Integration](./v402_providers/src/integrations/vue/)
- Vue 3 Composition API composables
- Vue components with TypeScript
- Nuxt.js module support
- Pinia state management integration

### 3. v402_facilitator (Backend Service)

Multi-chain settlement service built on x402 protocol:

- ✅ **x402 Protocol Implementation**
- ✅ **Multi-Chain Support** (EVM, Solana, BSC, Polygon)
- ✅ **Cryptographic Verification** (EIP-712, Ed25519)
- ✅ **On-Chain Settlement** (EIP-3009, SPL Token)
- ✅ **Resource Discovery Service**
- ✅ **Advanced Analytics & Monitoring**

## 📦 Installation

### Client SDKs

```bash
# Python
pip install v402-client-python

# Go
go get github.com/v402/client-go

# Java
mvn install com.v402:v402-client-java

# Rust
cargo add v402-client
```

### Provider SDK

```bash
# JavaScript/TypeScript Core + Framework Integrations
npm install @v402/providers

# Or install specific framework integration
# React
npm install @v402/providers react
# Vue
npm install @v402/providers vue
```

### Facilitator

```bash
docker pull v402/facilitator:latest
# or
go install github.com/v402/facilitator@latest
```

## 🎯 Quick Start

### For Content Creators (JavaScript)

```javascript
import { V402PaymentButton } from '@v402/provider';

// Simple payment button
<V402PaymentButton
  price="0.001"
  chain="ethereum"
  onSuccess={(tx) => console.log('Payment received:', tx)}
>
  Unlock Premium Content
</V402PaymentButton>
```

### For React Applications

```jsx
import { V402PaymentGate } from '@v402/provider-react';

function PremiumArticle() {
  return (
    <V402PaymentGate
      price="1000000"
      description="Premium Article Access"
      facilitatorUrl="https://facilitator.v402.org"
    >
      <ArticleContent />
    </V402PaymentGate>
  );
}
```

### For AI Platforms (Python)

```python
from v402_client import V402Client, ChainConfig

client = V402Client(
    private_key="0x...",
    chains=[
        ChainConfig.ETHEREUM_MAINNET,
        ChainConfig.BASE,
        ChainConfig.POLYGON
    ],
    auto_pay=True
)

async with client:
    response = await client.get("https://example.com/premium")
    content = response.json()
```

### For AI Platforms (Go)

```go
import "github.com/v402/client-go/v402"

client := v402.NewClient(&v402.Config{
    PrivateKey: "0x...",
    Chains: []v402.Chain{
        v402.ChainEthereum,
        v402.ChainBase,
        v402.ChainPolygon,
    },
    AutoPay: true,
})

resp, err := client.Get(ctx, "https://example.com/premium")
```

## 🌍 Multi-Chain Support

v402 supports multiple blockchain networks:

### EVM Chains
- Ethereum (Mainnet, Sepolia, Goerli)
- Base (Mainnet, Sepolia)
- Arbitrum (One, Nova, Sepolia)
- Optimism (Mainnet, Sepolia)
- Polygon (Mainnet, Mumbai)
- BSC (Mainnet, Testnet)

### Non-EVM Chains
- Solana (Mainnet-Beta, Devnet, Testnet)

## 📚 Documentation

### Core Documentation
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete HTTP API reference for v402 facilitator
- [Architecture](./ARCHITECTURE.md) - System architecture and design
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment instructions
- [Examples](./examples/) - Comprehensive examples and tutorials

### Client SDKs
v402 provides multiple client integration options - choose what works best for you:

#### SDKs (Recommended for Most Use Cases)
- [Python SDK](./clients/python/README.md) - Async Python client
- [Go SDK](./clients/go/README.md) - High-performance Go client  
- [Java SDK](./clients/java/README.md) - Enterprise Java client
- [Rust SDK](./clients/rust/README.md) - Memory-safe Rust client

#### HTTP API (For Custom Integrations)
See [Complete API Documentation](./API_DOCUMENTATION.md) for direct REST API access without SDKs

#### Provider SDK
- [JavaScript/TypeScript Provider SDK](./v402_providers/README.md) - For content creators

## 🎓 Examples

Explore comprehensive examples for different use cases:

- [Python Examples](./examples/python/) - Async Python client examples
- [Go Examples](./examples/go/) - High-performance concurrent examples
- [JavaScript/React Examples](./examples/javascript/) - React, Vue, and vanilla JS
- [Rust Examples](./examples/rust/) - Performance-optimized examples
- [End-to-End Example](./examples/end_to_end_example/) - Complete integration
- [Index Client Examples](./examples/index_client_example/) - Basic and batch processing

See [Examples README](./examples/README.md) for detailed documentation and usage guides.

## 🔧 Development

### Prerequisites
- Python 3.10+, Go 1.21+, Java 17+, Rust 1.70+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+

### Build All Components

```bash
# Clone repository
git clone https://github.com/yourusername/v402.git
cd v402

# Build all clients
make build-clients

# Build all providers
make build-providers

# Build facilitator
make build-facilitator

# Run all tests
make test-all
```

## 🎯 Vision

We believe that in the future:

- **Paid content crawlers will deliver higher-quality data**
- **AI systems will prefer to index premium sources**
- **Creators get rewarded, platforms gain better materials**
- **Multi-chain support enables global adoption**

This is v402's vision: **the next-generation framework for content distribution and incentive alignment** — powered by x402 protocol.

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

Apache-2.0 License

## 🙏 Acknowledgments

Built on top of the [x402 protocol](https://github.com/coinbase/x402) by Coinbase.

---

**Join us in building the future of AI-powered content distribution! 🚀**
