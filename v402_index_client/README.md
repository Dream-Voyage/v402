# v402 Index Client

**Payment client SDK for AI/crawler platforms to automatically handle micropayments for premium content.**

## Overview

The v402 Index Client is designed for AI platforms, search engines, and content aggregators that need to access paid content. It automatically:

- Detects `402 Payment Required` responses
- Selects appropriate payment methods
- Creates and signs payment transactions
- Retries requests with payment headers
- Tracks payment history

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from v402_index_client import V402IndexClient

# Initialize client with your private key
client = V402IndexClient(
    private_key="0x...",
    max_amount_per_request="1000000",  # Maximum wei per request
    network="base-sepolia"
)

# Automatic payment handling
response = await client.get(
    "https://example.com/premium-article",
    auto_pay=True
)

# Check payment status
if response.payment_made:
    print(f"Paid {response.payment_amount} to access content")
    print(f"Transaction: {response.transaction_hash}")
```

## Features

- **Automatic Payment Detection**: Automatically handles 402 responses
- **Multi-Network Support**: Works with Ethereum, Base, and other EVM chains
- **Payment Limits**: Configure maximum payment amounts
- **Retry Logic**: Built-in retry with exponential backoff
- **Payment Tracking**: Track all payments made
- **Async Support**: Full async/await support

## Configuration

```python
client = V402IndexClient(
    private_key="0x...",
    max_amount_per_request="1000000",  # in wei
    network="base-sepolia",
    facilitator_url="http://localhost:8000",
    retry_attempts=3,
    timeout=30
)
```

## Advanced Usage

### Custom Payment Selection

```python
def my_payment_selector(accepts, network, scheme, max_value):
    # Custom logic to select payment requirements
    return accepts[0]

client = V402IndexClient(
    private_key="0x...",
    payment_selector=my_payment_selector
)
```

### Batch Requests

```python
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
]

responses = await client.batch_get(urls, auto_pay=True)
```

### Payment History

```python
# Get payment history
history = client.get_payment_history()
for payment in history:
    print(f"URL: {payment.url}")
    print(f"Amount: {payment.amount}")
    print(f"Tx: {payment.transaction_hash}")
```

## API Reference

See [API Documentation](./docs/api.md) for detailed API reference.

