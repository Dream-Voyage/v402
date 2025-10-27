# v402 JavaScript/TypeScript Provider

**Embeddable payment component for content monetization.**

## Features

- 🎨 **UI Components**: Ready-to-use payment buttons and modals
- 🌐 **Framework Agnostic**: Works with any JavaScript framework
- 🔌 **Web Components**: Standards-based custom elements
- 🎯 **TypeScript**: Full type safety
- 🌍 **Multi-Chain**: Support for EVM, Solana, BSC, Polygon
- 📊 **Analytics**: Built-in revenue tracking
- 🎨 **Customizable**: Flexible styling and theming

## Architecture

```
providers/javascript/
├── packages/
│   ├── core/                   # Core library
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client/
│   │   │   │   ├── V402Client.ts
│   │   │   │   └── HttpClient.ts
│   │   │   ├── payment/
│   │   │   │   ├── PaymentManager.ts
│   │   │   │   ├── Signer.ts
│   │   │   │   └── Verifier.ts
│   │   │   ├── chains/
│   │   │   │   ├── ChainAdapter.ts
│   │   │   │   ├── EVMChain.ts
│   │   │   │   ├── SolanaChain.ts
│   │   │   │   └── BSCChain.ts
│   │   │   ├── ui/
│   │   │   │   ├── PaymentButton.ts
│   │   │   │   ├── PaymentModal.ts
│   │   │   │   └── PaymentGate.ts
│   │   │   ├── config/
│   │   │   │   └── Configuration.ts
│   │   │   ├── utils/
│   │   │   │   ├── crypto.ts
│   │   │   │   ├── storage.ts
│   │   │   │   └── logger.ts
│   │   │   └── types/
│   │   │       ├── models.ts
│   │   │       └── events.ts
│   │   └── package.json
│   │
│   ├── web-components/         # Web Components (Custom Elements)
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── components/
│   │   │   │   ├── v402-payment-button.ts
│   │   │   │   ├── v402-payment-modal.ts
│   │   │   │   ├── v402-payment-gate.ts
│   │   │   │   └── v402-revenue-dashboard.ts
│   │   │   └── styles/
│   │   │       ├── button.css
│   │   │       └── modal.css
│   │   └── package.json
│   │
│   ├── react/                  # React Components
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── components/
│   │   │   │   ├── V402PaymentButton.tsx
│   │   │   │   ├── V402PaymentGate.tsx
│   │   │   │   ├── V402PaymentModal.tsx
│   │   │   │   └── V402RevenueDashboard.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useV402Payment.ts
│   │   │   │   ├── useV402Config.ts
│   │   │   │   └── useV402Analytics.ts
│   │   │   └── context/
│   │   │       └── V402Context.tsx
│   │   └── package.json
│   │
│   └── vue/                    # Vue Components
│       ├── src/
│       │   ├── index.ts
│       │   ├── components/
│       │   │   ├── V402PaymentButton.vue
│       │   │   ├── V402PaymentGate.vue
│       │   │   └── V402RevenueDashboard.vue
│       │   ├── composables/
│       │   │   ├── useV402Payment.ts
│       │   │   └── useV402Analytics.ts
│       │   └── plugin/
│       │       └── index.ts
│       └── package.json
├── examples/                    # Usage examples
├── docs/                        # Documentation
└── package.json                # Monorepo root
```

## Installation

### Core Library (Framework Agnostic)

```bash
npm install @v402/provider
# or
yarn add @v402/provider
# or
pnpm add @v402/provider
```

### Web Components

```bash
npm install @v402/web-components
```

### React

```bash
npm install @v402/provider-react
```

### Vue

```bash
npm install @v402/provider-vue
```

## Quick Start

### Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import { V402Provider } from 'https://cdn.jsdelivr.net/npm/@v402/provider/dist/index.js';
        
        // Initialize provider
        const provider = new V402Provider({
            walletAddress: '0x...',
            facilitatorUrl: 'https://facilitator.v402.org',
            chains: ['ethereum', 'base', 'polygon']
        });
        
        // Create payment button
        const button = provider.createPaymentButton({
            price: '0.001',
            chain: 'ethereum',
            description: 'Premium Article Access',
            onSuccess: (tx) => {
                console.log('Payment successful:', tx);
                // Show premium content
            },
            onError: (error) => {
                console.error('Payment failed:', error);
            }
        });
        
        document.getElementById('payment-container').appendChild(button);
    </script>
</head>
<body>
    <div id="payment-container"></div>
</body>
</html>
```

### Web Components

```html
<!DOCTYPE html>
<html>
<head>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@v402/web-components/dist/index.js"></script>
</head>
<body>
    <!-- Payment Button -->
    <v402-payment-button
        price="0.001"
        chain="ethereum"
        description="Premium Article"
        wallet-address="0x..."
        facilitator-url="https://facilitator.v402.org"
    >
        Unlock Premium Content
    </v402-payment-button>
    
    <!-- Payment Gate (hides content until paid) -->
    <v402-payment-gate
        price="0.001"
        chain="ethereum"
        wallet-address="0x..."
    >
        <div class="premium-content">
            <h1>Premium Article</h1>
            <p>This content is protected by v402...</p>
        </div>
    </v402-payment-gate>
    
    <!-- Revenue Dashboard -->
    <v402-revenue-dashboard
        wallet-address="0x..."
        facilitator-url="https://facilitator.v402.org"
    ></v402-revenue-dashboard>
</body>
</html>
```

### React

```tsx
import { V402Provider, V402PaymentGate, V402PaymentButton } from '@v402/provider-react';

function App() {
    return (
        <V402Provider
            walletAddress="0x..."
            facilitatorUrl="https://facilitator.v402.org"
            chains={['ethereum', 'base', 'polygon']}
        >
            <div>
                {/* Payment Button */}
                <V402PaymentButton
                    price="0.001"
                    chain="ethereum"
                    description="Premium Article"
                    onSuccess={(tx) => console.log('Paid:', tx)}
                >
                    Unlock Content
                </V402PaymentButton>
                
                {/* Payment Gate */}
                <V402PaymentGate
                    price="0.001"
                    chain="ethereum"
                    description="Premium Article Access"
                >
                    <PremiumArticle />
                </V402PaymentGate>
            </div>
        </V402Provider>
    );
}

function PremiumArticle() {
    return (
        <article>
            <h1>Premium Content</h1>
            <p>This content is protected by v402...</p>
        </article>
    );
}
```

### Vue 3

```vue
<template>
    <V402Provider
        wallet-address="0x..."
        :chains="['ethereum', 'base', 'polygon']"
    >
        <!-- Payment Button -->
        <V402PaymentButton
            price="0.001"
            chain="ethereum"
            description="Premium Article"
            @success="handleSuccess"
        >
            Unlock Content
        </V402PaymentButton>
        
        <!-- Payment Gate -->
        <V402PaymentGate
            price="0.001"
            chain="ethereum"
            description="Premium Article"
        >
            <PremiumArticle />
        </V402PaymentGate>
    </V402Provider>
</template>

<script setup lang="ts">
import { V402Provider, V402PaymentButton, V402PaymentGate } from '@v402/provider-vue';
import PremiumArticle from './PremiumArticle.vue';

function handleSuccess(tx: Transaction) {
    console.log('Payment successful:', tx);
}
</script>
```

## Advanced Usage

### Custom Styling

```typescript
import { V402Provider } from '@v402/provider';

const provider = new V402Provider({
    walletAddress: '0x...',
    theme: {
        primaryColor: '#6366f1',
        borderRadius: '8px',
        fontFamily: 'Inter, sans-serif',
        buttonStyle: {
            background: 'linear-gradient(to right, #6366f1, #8b5cf6)',
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
        },
        modalStyle: {
            overlay: 'rgba(0, 0, 0, 0.5)',
            backgroundColor: '#ffffff',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        }
    }
});
```

### Multi-Chain Support

```typescript
const button = provider.createPaymentButton({
    price: {
        ethereum: '0.001',
        base: '0.0008',
        polygon: '1.5',
        solana: '0.05'
    },
    description: 'Premium Article',
    allowChainSelection: true,  // Let user choose chain
    preferredChain: 'base',     // Default selection
});
```

### Revenue Analytics

```typescript
import { useV402Analytics } from '@v402/provider-react';

function RevenueDashboard() {
    const { stats, payments, loading } = useV402Analytics({
        walletAddress: '0x...',
        timeRange: 'last30days'
    });
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div>
            <h2>Revenue Analytics</h2>
            <div>Total Revenue: {stats.totalRevenue} ETH</div>
            <div>Total Payments: {stats.totalPayments}</div>
            <div>Unique Payers: {stats.uniquePayers}</div>
            
            <h3>Recent Payments</h3>
            <ul>
                {payments.map(p => (
                    <li key={p.txHash}>
                        {p.amount} {p.currency} - {p.description}
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

### Wallet Integration

```typescript
import { V402Provider } from '@v402/provider';
import { ethers } from 'ethers';

// Connect with MetaMask
async function connectWallet() {
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    await provider.send("eth_requestAccounts", []);
    const signer = provider.getSigner();
    const address = await signer.getAddress();
    
    const v402 = new V402Provider({
        walletAddress: address,
        signer: signer,  // Use connected wallet for signing
    });
    
    return v402;
}
```

## Configuration

### TypeScript Configuration

```typescript
interface V402Config {
    walletAddress: string;
    facilitatorUrl?: string;
    chains?: ChainName[];
    theme?: ThemeConfig;
    signer?: Signer;
    onPaymentSuccess?: (tx: Transaction) => void;
    onPaymentError?: (error: Error) => void;
    debug?: boolean;
}
```

### Environment Variables

```bash
VITE_V402_WALLET_ADDRESS=0x...
VITE_V402_FACILITATOR_URL=https://facilitator.v402.org
VITE_V402_CHAINS=ethereum,base,polygon
VITE_V402_DEBUG=false
```

## API Reference

See [API Documentation](./docs/api.md)

## Development

```bash
# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run tests
pnpm test

# Run examples
pnpm dev

# Lint
pnpm lint

# Type check
pnpm type-check
```

## Examples

- [Basic Button](./examples/basic-button/)
- [Payment Gate](./examples/payment-gate/)
- [Multi-Chain](./examples/multi-chain/)
- [Custom Styling](./examples/custom-styling/)
- [React Integration](./examples/react-app/)
- [Vue Integration](./examples/vue-app/)
- [Next.js App](./examples/nextjs-app/)
- [Nuxt.js App](./examples/nuxt-app/)

