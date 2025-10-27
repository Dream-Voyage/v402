# v402 Facilitator

**Backend settlement service for verifying and settling x402 payments on-chain.**

## Overview

The v402 Facilitator is the critical infrastructure component that:

- Verifies payment signatures and authorizations
- Settles payments on blockchain networks
- Provides discovery endpoints for resources
- Tracks transaction history
- Supports multiple blockchain networks

## Features

- **Payment Verification**: Cryptographic verification of payment signatures
- **On-Chain Settlement**: Automatic settlement to blockchain
- **Multi-Network**: Support for Ethereum, Base, and other EVM chains
- **Discovery Service**: Resource discovery for AI platforms
- **Transaction Tracking**: Complete audit trail of all payments
- **High Performance**: Async architecture for scalability
- **Database Support**: PostgreSQL/SQLite for persistence

## Architecture

```
┌─────────────────────┐
│   Content Provider  │
│                     │
└──────────┬──────────┘
           │ /verify
           │ /settle
           ▼
┌─────────────────────┐         ┌──────────────┐
│    Facilitator      │────────▶│  Blockchain  │
│   (FastAPI Server)  │         │  (EVM Chains)│
└──────────▲──────────┘         └──────────────┘
           │
           │ /discovery/resources
           │
┌──────────┴──────────┐
│   Index Platform    │
└─────────────────────┘
```

## Installation

```bash
pip install -e .
```

## Quick Start

### Configuration

Create a `.env` file:

```bash
# Blockchain Configuration
NETWORK=base-sepolia
RPC_URL=https://sepolia.base.org
PRIVATE_KEY=0x...

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/v402
# Or use SQLite
# DATABASE_URL=sqlite:///./v402.db

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
API_KEY=your-secret-api-key
ENABLE_RATE_LIMIT=true
```

### Running the Server

```bash
# Development mode
python -m v402_facilitator.main

# Production with uvicorn
uvicorn v402_facilitator.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /verify

Verify a payment signature.

**Request:**
```json
{
  "x402Version": 1,
  "paymentPayload": {...},
  "paymentRequirements": {...}
}
```

**Response:**
```json
{
  "isValid": true,
  "invalidReason": null,
  "payer": "0x..."
}
```

### POST /settle

Settle a payment on-chain.

**Request:**
```json
{
  "x402Version": 1,
  "paymentPayload": {...},
  "paymentRequirements": {...}
}
```

**Response:**
```json
{
  "success": true,
  "transaction": "0x...",
  "network": "base-sepolia",
  "payer": "0x..."
}
```

### GET /discovery/resources

Discover available paid resources.

**Query Parameters:**
- `type`: Resource type (default: "http")
- `limit`: Results per page
- `offset`: Pagination offset

**Response:**
```json
{
  "x402Version": 1,
  "items": [...],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 100
  }
}
```

### GET /supported

Get supported payment schemes and networks.

**Response:**
```json
{
  "kinds": [
    {
      "scheme": "exact",
      "network": "base-sepolia"
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETWORK` | Blockchain network | `base-sepolia` |
| `RPC_URL` | RPC endpoint URL | Required |
| `PRIVATE_KEY` | Settlement private key | Required |
| `DATABASE_URL` | Database connection | `sqlite:///./v402.db` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `API_KEY` | API authentication key | Optional |
| `ENABLE_RATE_LIMIT` | Enable rate limiting | `false` |

### Database Migrations

```bash
# Initialize database
python -m v402_facilitator.db.migrations init

# Run migrations
python -m v402_facilitator.db.migrations migrate
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Deployment

### Docker

```bash
# Build image
docker build -t v402-facilitator .

# Run container
docker run -p 8000:8000 --env-file .env v402-facilitator
```

### Docker Compose

```bash
docker-compose up -d
```

## Monitoring

The facilitator provides health check endpoints:

- `GET /health` - Server health status
- `GET /metrics` - Prometheus metrics

## Security

- All payments are cryptographically verified
- Private keys are never exposed
- Rate limiting prevents abuse
- API key authentication for sensitive endpoints
- Database encryption for sensitive data

## API Reference

See [API Documentation](./docs/api.md) for detailed API reference.

