# v402 Architecture

This document describes the architecture and design decisions of the v402 framework.

## Overview

v402 is a framework for agent-based content monetization built on the x402 protocol. It consists of three core components that work together to enable micropayments for content access.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         v402 Ecosystem                               │
│     Multi-Chain Content Monetization Framework on x402 Protocol      │
│                                                                       │
│  ┌──────────────────────────┐      ┌──────────────────────────┐     │
│  │    Index Platforms       │      │   Content Providers      │     │
│  │    (AI/Crawlers)         │      │   (UGC Websites)         │     │
│  │                          │      │                          │     │
│  │  v402_index_client       │      │  v402_content_provider   │     │
│  │  ├── Python SDK          │      │  ├── JavaScript/TS       │     │
│  │  ├── Go SDK              │      │  ├── React Component     │     │
│  │  ├── Java SDK            │      │  ├── Vue Plugin          │     │
│  │  └── Rust SDK            │      │  └── Web Component       │     │
│  └────────────┬─────────────┘      └────────────┬─────────────┘     │
│               │                                  │                   │
│               │  X-PAYMENT Header                │  402 Required     │
│               │  (Signed Transaction)            │  Response         │
│               │                                  │                   │
│               ▼                                  ▼                   │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │              v402_facilitator                           │        │
│  │        (Built on x402 Protocol Standard)                │        │
│  │                                                          │        │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │        │
│  │  │Verification  │  │ Settlement   │  │  Discovery   │  │        │
│  │  │   Engine     │  │   Engine     │  │   Service    │  │        │
│  │  │              │  │              │  │              │  │        │
│  │  │- EIP-712     │  │- EIP-3009    │  │- Resource    │  │        │
│  │  │- Signature   │  │- Multi-Chain │  │  Registry    │  │        │
│  │  │  Verify      │  │  Settlement  │  │- Analytics   │  │        │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │        │
│  │                                                          │        │
│  │  ┌──────────────────────────────────────────────────┐   │        │
│  │  │         x402 Protocol Implementation             │   │        │
│  │  │  - Payment Requirements Generation               │   │        │
│  │  │  - Cryptographic Verification                    │   │        │
│  │  │  - On-Chain Settlement Coordination              │   │        │
│  │  └──────────────────────────────────────────────────┘   │        │
│  └────────────────────────┬─────────────────────────────────┘        │
│                           │                                          │
│                           │  Multi-Chain Support                     │
│                           ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │              Blockchain Networks Layer                   │       │
│  │                                                           │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │       │
│  │  │   EVM   │  │ Solana  │  │   BSC   │  │ Polygon │    │       │
│  │  │ Chains  │  │         │  │         │  │         │    │       │
│  │  │         │  │         │  │         │  │         │    │       │
│  │  │- Base   │  │- Mainnet│  │- Mainnet│  │- Mainnet│    │       │
│  │  │- Ethereum│ │- Devnet │  │- Testnet│  │- Mumbai │    │       │
│  │  │- Arbitrum│ │         │  │         │  │         │    │       │
│  │  │- Optimism│ │         │  │         │  │         │    │       │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │       │
│  └──────────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. v402_index_client

**Purpose**: SDK for AI platforms and crawlers to access paid content.

**Key Features**:
- Automatic 402 detection
- Payment header creation and signing
- Retry logic with exponential backoff
- Payment history tracking
- Batch request support

**Architecture**:
```
v402_index_client
├── client.py           # Main client implementation
├── types.py            # Type definitions
├── exceptions.py       # Custom exceptions
└── __init__.py         # Public API

Dependencies:
- x402 (local)          # Base x402 protocol implementation
- httpx                 # Async HTTP client
- eth-account           # Ethereum account management
```

**Design Decisions**:
1. **Async First**: All operations are async for better performance
2. **Stateful Client**: Maintains payment history for analytics
3. **Automatic Retry**: Built-in retry logic for network failures
4. **Flexible Configuration**: Support for custom payment selectors

### 2. v402_content_provider

**Purpose**: SDK for content creators and UGC websites to monetize content.

**Key Features**:
- Simple decorator-based API
- Framework integration (FastAPI/Flask)
- Payment verification via facilitator
- Revenue tracking and analytics
- Automatic settlement

**Architecture**:
```
v402_content_provider
├── provider.py         # Main provider implementation
├── types.py            # Type definitions
├── exceptions.py       # Custom exceptions
└── __init__.py         # Public API

Dependencies:
- x402 (local)          # Base x402 protocol implementation
- fastapi               # FastAPI integration
- flask                 # Flask integration
```

**Design Decisions**:
1. **Decorator Pattern**: Easy-to-use decorators for protection
2. **Framework Agnostic**: Support multiple web frameworks
3. **Verification First**: Always verify before serving content
4. **Revenue Tracking**: Built-in analytics and reporting

### 3. v402_facilitator

**Purpose**: Backend service for payment verification and settlement.

**Key Features**:
- Cryptographic payment verification
- On-chain settlement
- Multi-network support
- Resource discovery
- Transaction tracking

**Architecture**:
```
v402_facilitator
├── main.py             # FastAPI application
├── config.py           # Configuration management
├── types.py            # Type definitions
├── verification.py     # Payment verification logic
├── settlement.py       # On-chain settlement logic
├── database.py         # Database operations
└── __init__.py

Dependencies:
- fastapi               # Web framework
- sqlalchemy            # Database ORM
- web3                  # Blockchain interaction
- eth-account           # Cryptographic operations
```

**Design Decisions**:
1. **FastAPI**: High performance async web framework
2. **Stateless API**: RESTful design for scalability
3. **Database Backed**: Persistent storage for transactions
4. **Pluggable Storage**: Support SQLite and PostgreSQL
5. **Separation of Concerns**: Verification and settlement are separate

## Data Flow

### Payment Flow

```
1. Client Request (No Payment)
   ┌─────────┐
   │ Client  │──GET /content──>┌──────────┐
   └─────────┘                  │ Provider │
                                └────┬─────┘
                                     │
                                     ▼
                            Return 402 + Requirements

2. Client Payment
   ┌─────────┐
   │ Client  │
   └────┬────┘
        │ 1. Select payment requirements
        │ 2. Create authorization
        │ 3. Sign with EIP-712
        │ 4. Encode as base64
        │
        ▼
   X-PAYMENT: base64(payload)
        │
        ▼
   ┌──────────┐
   │ Provider │──POST /verify──>┌─────────────┐
   └──────────┘                  │ Facilitator │
                                 └──────┬──────┘
                                        │
                                        ▼
                                Verify Signature
                                        │
                                        ▼
                                  Return Valid


3. Settlement
   ┌──────────┐
   │ Provider │──POST /settle──>┌─────────────┐
   └──────────┘                  │ Facilitator │
                                 └──────┬──────┘
                                        │
                                        ▼
                              Submit to Blockchain
                                        │
                                        ▼
                           ┌────────────────────┐
                           │ Blockchain Network │
                           └────────────────────┘
```

### Discovery Flow

```
┌──────────┐
│ Provider │──POST /discovery/resources──>┌─────────────┐
└──────────┘                                │ Facilitator │
                                            └──────┬──────┘
                                                   │
                                                   ▼
                                          Store in Database


┌─────────┐
│ Client  │──GET /discovery/resources──>┌─────────────┐
└─────────┘                              │ Facilitator │
                                         └──────┬──────┘
                                                │
                                                ▼
                                       Query Database
                                                │
                                                ▼
                                        Return Resources
```

## Security

### Payment Verification

1. **Signature Verification**: EIP-712 signatures ensure authenticity
2. **Amount Validation**: Verify payment amount matches requirements
3. **Time Windows**: Valid before/after timestamps prevent replay
4. **Nonce Tracking**: Prevent double-spending
5. **Recipient Validation**: Ensure payment goes to correct address

### Data Protection

1. **Private Keys**: Never exposed or transmitted
2. **Database Encryption**: Sensitive data encrypted at rest
3. **HTTPS Only**: All production traffic over TLS
4. **API Authentication**: Optional API key protection
5. **Rate Limiting**: Prevent abuse

## Scalability

### Horizontal Scaling

The facilitator is designed to scale horizontally:

1. **Stateless API**: No session data on servers
2. **Database Backed**: Shared state in database
3. **Load Balancing**: Standard HTTP load balancing
4. **Caching**: Redis for frequently accessed data

### Performance Optimizations

1. **Async Operations**: Non-blocking I/O throughout
2. **Connection Pooling**: Reuse database and HTTP connections
3. **Batch Processing**: Process multiple requests concurrently
4. **Lazy Loading**: Load data only when needed

## Extensibility

### Adding New Payment Schemes

1. Define scheme in x402 protocol
2. Implement verification logic in facilitator
3. Update client to support scheme
4. Add scheme to supported list

### Adding New Networks

1. Configure RPC endpoint
2. Add chain ID mapping
3. Update network list in configuration
4. Test with test network first

### Custom Integrations

1. **Web Frameworks**: Add middleware for new frameworks
2. **Databases**: Implement new database adapters
3. **Payment Methods**: Extend beyond EIP-3009
4. **Analytics**: Add custom metrics and tracking

## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution

### Integration Tests
- Test component interactions
- Use test networks
- Verify end-to-end flows

### E2E Tests
- Test complete user workflows
- Real database and blockchain
- Performance testing

## Deployment

### Development
```bash
# Local development with hot reload
python -m v402_facilitator.main
```

### Production
```bash
# Multiple workers with uvicorn
uvicorn v402_facilitator.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["uvicorn", "v402_facilitator.main:app", "--host", "0.0.0.0"]
```

## Monitoring

### Metrics
- Request rate
- Payment success rate
- Settlement time
- Error rates
- Database performance

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for tracing

### Alerting
- Payment verification failures
- Settlement failures
- High error rates
- Performance degradation

## Future Enhancements

1. **Additional Schemes**: Support for "upto" and other schemes
2. **Multi-Currency**: Support for multiple tokens
3. **Layer 2**: Integration with L2 networks
4. **Advanced Analytics**: ML-powered insights
5. **Decentralized Discovery**: On-chain resource registry
6. **Reputation System**: Track content quality and provider reliability

