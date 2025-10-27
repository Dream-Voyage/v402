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
│                                                             │
│  ┌─────────────────┐              ┌──────────────────┐    │
│  │ Index Clients   │              │ Content Provider │    │
│  │ (AI/Crawlers)   │              │  (UGC Websites)  │    │
│  │                 │              │                  │    │
│  │ • Python SDK    │◄─X-PAYMENT──┤ • JavaScript/TS  │    │
│  │ • Go SDK        │              │ • React Component│    │
│  │ • Java SDK      │  402 Resp──►│ • Vue Plugin     │    │
│  │ • Rust SDK      │              │ • Web Component  │    │
│  └────────┬────────┘              └─────────┬────────┘    │
│           │                                 │             │
│           │         v402_facilitator        │             │
│           │    (x402 Protocol Service)      │             │
│           └────────────┬────────────────────┘             │
│                        │                                  │
│              Multi-Chain Support                          │
│   ┌─────────┬──────────┼──────────┬──────────┐           │
│   ▼         ▼          ▼          ▼          ▼           │
│  EVM     Solana      BSC      Polygon    Arbitrum        │
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

### 2. v402_content_provider (JavaScript/TypeScript Components)

Embeddable payment components for content creators:

#### 📦 [JavaScript Core](./providers/javascript/)
- Framework-agnostic core library
- Web Component implementation
- Payment button with customizable UI
- Revenue analytics dashboard

#### ⚛️ [React Component](./providers/react/)
- Ready-to-use React hooks
- `<V402PaymentGate>` component
- TypeScript definitions
- Next.js integration

#### 💚 [Vue Plugin](./providers/vue/)
- Vue 3 Composition API
- `v-v402-payment` directive
- Nuxt.js module
- Pinia state management

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

### Provider Components

```bash
# JavaScript/TypeScript
npm install @v402/provider

# React
npm install @v402/provider-react

# Vue
npm install @v402/provider-vue
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

- [Architecture](./ARCHITECTURE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Reference](./docs/API.md)
- [Multi-Chain Guide](./docs/MULTI_CHAIN.md)
- [Examples](./examples/)

### Language-Specific Docs
- [Python SDK Documentation](./clients/python/README.md)
- [Go SDK Documentation](./clients/go/README.md)
- [Java SDK Documentation](./clients/java/README.md)
- [Rust SDK Documentation](./clients/rust/README.md)
- [JavaScript Provider Documentation](./providers/javascript/README.md)

## 🎓 Examples

- [Python: AI Content Crawler](./examples/python-ai-crawler/)
- [Go: High-Performance Indexer](./examples/go-indexer/)
- [Java: Enterprise Integration](./examples/java-enterprise/)
- [Rust: Blockchain Indexer](./examples/rust-indexer/)
- [React: Blog with Paywall](./examples/react-blog/)
- [Vue: Premium Course Platform](./examples/vue-course/)
- [End-to-End: Complete Flow](./examples/e2e/)

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
