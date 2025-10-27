# 📚 v402 Facilitator API Documentation

## 🌟 Overview

The v402 Facilitator is an enterprise-grade payment facilitation service that implements the x402 protocol for content monetization. It provides comprehensive APIs for content providers, index clients, and system administrators.

### 🔑 v402 Auth 3.0: Cryptographic Identity & Usage-Based Payments

v402 uses a revolutionary authentication and billing system:

1. **Public Key as Credential**: Your blockchain public key (e.g., `0x1234...`) is your identity - no centralized API keys
2. **x402 Payment Tokens for Usage**: Every API call is paid for using x402 payment tokens on-chain
3. **On-Chain Accounting**: All transactions are recorded on blockchain for transparent, verifiable billing
4. **No Points Balance**: Unlike traditional systems, there's no stored "balance" - payments are made on-demand

This enables **trustless, composable API monetization** where usage itself becomes a tokenized asset.

### 🚀 Key Features

- **Multi-chain Support**: Ethereum, Base, Polygon, Arbitrum, Optimism, BSC, Solana
- **x402 Protocol**: Full implementation of x402 payment protocol
- **Enterprise Security**: Rate limiting, authentication, audit logging
- **Real-time Analytics**: Comprehensive business intelligence and insights
- **Webhook Notifications**: Real-time event notifications
- **High Performance**: Async processing, connection pooling, caching

### 🔗 Base URL

```
Production:  https://facilitator.v402.network/api/v1
Staging:     https://staging-facilitator.v402.network/api/v1
Development: http://localhost:8080/api/v1
```

## 🔐 Authentication - v402 Auth 3.0

The v402 Facilitator implements cryptographic authentication using **public keys** instead of traditional API keys:

### Public Key Authentication

Your blockchain public key serves as your credential. Include it in requests:

```http
Authorization: Bearer <your_public_key>
X-Public-Key: 0x1234567890abcdef1234567890abcdef12345678
X-Signature: <cryptographic_signature>
```

### How It Works

1. **Generate a key pair** using your blockchain wallet (Ethereum, Solana, etc.)
2. **Use your public key** as your identifier
3. **Sign requests** with your private key for authentication
4. **All usage is paid** via x402 payment tokens, not stored points

### x402 Payment Tokens

Usage credits are represented as **x402 payment tokens** - on-chain payment proofs that can be verified:
- No centralized point system
- Payments recorded on-chain
- Fully composable and transferable
- Tamper-proof accounting

### x402 Payment Headers

For payment-related requests:

```http
X-PAYMENT: v402.1.0:signature:payload:metadata
```

## 📋 API Endpoints Overview

| Category | Endpoint Prefix | Purpose |
|----------|----------------|---------|
| **Content Providers** | `/providers` | Product management, analytics, payments |
| **Index Clients** | `/clients` | Content discovery, access, payments |
| **Administration** | `/admin` | System management, monitoring, user management |
| **Core Services** | `/` | Health checks, metrics, protocol discovery |

---

## 🏪 Content Provider APIs

*For content creators, websites, and service providers*

### 📦 Product Management

#### Create Product

```http
POST /providers/products
Content-Type: application/json
Authorization: Bearer {public_key}

{
  "title": "Premium AI Tutorial Series",
  "description": "Comprehensive guide to modern AI development",
  "content_url": "https://example.com/content/ai-tutorial-series",
  "type": "course",
  "category": "education",
  "tags": ["ai", "machine-learning", "tutorial"],
  "price": "5000000000000000000",
  "currency": "ETH",
  "payment_scheme": "exact",
  "thumbnail_url": "https://example.com/thumbnails/ai-course.jpg",
  "content_type": "video/series",
  "preview_content": "Learn AI development from basics to advanced...",
  "access_duration": 86400
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Premium AI Tutorial Series",
  "status": "draft",
  "price": "5000000000000000000",
  "view_count": 0,
  "purchase_count": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List Products

```http
GET /providers/products?page=1&size=20&status=active&category=education&sort_by=created_at&sort_order=desc
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Premium AI Tutorial Series",
      "status": "active",
      "price": "5000000000000000000",
      "view_count": 1250,
      "purchase_count": 89,
      "rating": 4.85,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### Update Product

```http
PUT /providers/products/{product_id}
Authorization: Bearer {public_key}

{
  "title": "Advanced AI Tutorial Series - Updated",
  "price": "4500000000000000000",
  "status": "active"
}
```

#### Publish Product

```http
POST /providers/products/{product_id}/publish
Authorization: Bearer {public_key}
```

### 📊 Analytics & Insights

#### Product Analytics

```http
GET /providers/products/{product_id}/analytics?start_date=2024-01-01&end_date=2024-01-31&group_by=day
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "total_count": 1250,
  "data": [
    {
      "date": "2024-01-15",
      "views": 45,
      "unique_visitors": 38,
      "purchases": 3,
      "revenue": "15000000000000000000",
      "conversion_rate": 0.067
    }
  ],
  "summary": {
    "total_views": 1250,
    "total_purchases": 89,
    "total_revenue": "445000000000000000000",
    "average_conversion_rate": 0.071
  }
}
```

#### Dashboard Analytics

```http
GET /providers/analytics/dashboard?days=30
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "summary": {
    "total_products": 15,
    "active_products": 12,
    "total_revenue": "2500000000000000000000",
    "total_views": 15750,
    "total_purchases": 342,
    "conversion_rate": 0.022
  },
  "trends": {
    "revenue_growth": 0.15,
    "view_growth": 0.08,
    "new_customers": 89
  },
  "top_products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Premium AI Tutorial Series",
      "revenue": "445000000000000000000",
      "purchases": 89
    }
  ],
  "geographic_distribution": {
    "US": 45.2,
    "EU": 32.1,
    "ASIA": 22.7
  }
}
```

#### Revenue Analytics

```http
GET /providers/analytics/revenue?start_date=2024-01-01&end_date=2024-01-31&group_by=week
Authorization: Bearer {public_key}
```

### 🔍 Access Logs & Unpaid Requests

#### Access Logs

```http
GET /providers/access-logs?page=1&size=50&unpaid_only=true&start_date=2024-01-15T00:00:00Z
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": "log-123",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (compatible; AI-Crawler/1.0)",
      "status": "requested",
      "access_granted": false,
      "country_code": "US",
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "size": 50,
  "pages": 4
}
```

#### Unpaid Requests Analysis

```http
GET /providers/unpaid-requests?hours=24&min_requests=3
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "items": [
    {
      "ip_address": "192.168.1.100",
      "request_count": 15,
      "last_request": "2024-01-15T14:30:00Z",
      "products_requested": [
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001"
      ],
      "country_code": "US",
      "user_agent": "Mozilla/5.0 (compatible; AI-Crawler/1.0)",
      "potential_value": "75000000000000000000"
    }
  ],
  "total_potential_revenue": "1250000000000000000000",
  "unique_requesters": 23,
  "top_requested_products": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440000", 
      "title": "Premium AI Tutorial Series",
      "unpaid_requests": 89
    }
  ]
}
```

### 💳 Payment Management

#### List Received Payments

```http
GET /providers/payments?page=1&size=50&status=confirmed&chain=ethereum&start_date=2024-01-01
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "items": [
    {
      "id": "pay-123",
      "transaction_hash": "0xabc123...",
      "chain": "ethereum", 
      "amount": "5000000000000000000",
      "facilitator_fee": "125000000000000000",
      "status": "confirmed",
      "payer_address": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
      "product_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-15T10:45:00Z",
      "confirmed_at": "2024-01-15T10:47:00Z"
    }
  ],
  "total": 89,
  "page": 1,
  "size": 50
}
```

### 🔔 Webhook Management

#### List Webhooks

```http
GET /providers/webhooks
Authorization: Bearer {public_key}
```

#### Create Webhook

```http
POST /providers/webhooks
Authorization: Bearer {public_key}

{
  "url": "https://yourapp.com/webhooks/v402",
  "events": ["payment.confirmed", "payment.failed", "product.viewed"],
  "secret": "your_webhook_secret_key"
}
```

### 💡 Business Insights

#### Top Products

```http
GET /providers/insights/top-products?period=30d&metric=revenue&limit=10
Authorization: Bearer {public_key}
```

#### Business Recommendations

```http
GET /providers/insights/recommendations
Authorization: Bearer {public_key}
```

**Response:**
```json
{
  "recommendations": [
    {
      "type": "pricing",
      "title": "Optimize Pricing Strategy",
      "description": "Consider reducing price by 10% for products with <5% conversion rate",
      "products_affected": ["550e8400-e29b-41d4-a716-446655440000"],
      "potential_impact": "+25% conversion rate",
      "confidence": 0.85
    },
    {
      "type": "content",
      "title": "Focus on Video Content", 
      "description": "Video content shows 3x higher engagement rates",
      "data": {
        "video_conversion": 0.12,
        "text_conversion": 0.04
      },
      "confidence": 0.92
    }
  ],
  "market_insights": {
    "trending_categories": ["ai", "blockchain", "data-science"],
    "optimal_price_range": {
      "min": "1000000000000000000",
      "max": "10000000000000000000"
    }
  }
}
```

---

## 🔍 Index Client APIs  

*For AI platforms, search engines, and content consumers*

### 🎯 Content Discovery

#### Discover Content

```http
GET /clients/discover?query=artificial intelligence&category=education&min_price=1000000000000000000&max_price=10000000000000000000&chain=ethereum&sort_by=relevance&page=1&size=20
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Premium AI Tutorial Series",
      "description": "Comprehensive guide to modern AI development",
      "type": "course",
      "category": "education",
      "price": "5000000000000000000",
      "currency": "ETH",
      "payment_scheme": "exact",
      "thumbnail_url": "https://example.com/thumbnails/ai-course.jpg",
      "rating": 4.85,
      "purchase_count": 89,
      "provider": {
        "id": "provider-123",
        "name": "AI Education Hub",
        "verified": true
      },
      "access_info": {
        "duration": 86400,
        "max_accesses": null,
        "content_type": "video/series"
      }
    }
  ],
  "total": 156,
  "page": 1,
  "size": 20,
  "filters_applied": {
    "query": "artificial intelligence",
    "category": "education",
    "price_range": ["1000000000000000000", "10000000000000000000"]
  },
  "suggestions": ["machine learning", "deep learning", "neural networks"]
}
```

#### Get Content Information

```http
GET /clients/content/{product_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Premium AI Tutorial Series",
  "description": "Comprehensive guide covering neural networks, deep learning...",
  "type": "course", 
  "category": "education",
  "price": "5000000000000000000",
  "currency": "ETH",
  "payment_scheme": "exact",
  "preview_content": "Module 1: Introduction to AI - What is artificial intelligence...",
  "payment_options": [
    {
      "chain": "ethereum",
      "address": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
      "estimated_fee": "50000000000000000"
    },
    {
      "chain": "base", 
      "address": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
      "estimated_fee": "1000000000000000"
    }
  ],
  "provider": {
    "name": "AI Education Hub",
    "website": "https://aieducationhub.com",
    "verified": true,
    "rating": 4.9
  },
  "statistics": {
    "view_count": 1250,
    "purchase_count": 89,
    "rating": 4.85,
    "review_count": 67
  }
}
```

#### Browse Categories

```http
GET /clients/categories?include_count=true
```

#### Trending Content

```http
GET /clients/trending?period=24h&limit=10&category=ai
```

### 🔐 Content Access (x402 Protocol)

#### Request Content Access

```http
GET /clients/access/{product_id}
User-Agent: AI-Platform/1.0
Referer: https://ai-platform.com/search
```

**Response (Payment Required - 402):**
```json
{
  "x402Version": 1,
  "accepts": [
    {
      "scheme": "exact",
      "network": "ethereum",
      "maxAmountRequired": "5000000000000000000",
      "resource": "/clients/access/550e8400-e29b-41d4-a716-446655440000",
      "description": "Premium AI Tutorial Series",
      "mimeType": "video/series",
      "payTo": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
      "maxTimeoutSeconds": 900,
      "asset": "ETH"
    }
  ],
  "error": "Payment required to access this content"
}
```

#### Access with Payment

```http
GET /clients/access/{product_id}
X-PAYMENT: v402.1.0:0xsignature:payload:metadata
User-Agent: AI-Platform/1.0
```

**Response (Access Granted - 200):**
```json
{
  "status": "success",
  "content_url": "https://secure-content.example.com/ai-tutorial-series?token=abc123",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-01-16T10:45:00Z",
  "payment_info": {
    "amount": "5000000000000000000",
    "transaction_hash": "0xdef456...",
    "network": "ethereum",
    "confirmations": 3
  }
}
```

### 💰 Payment Processing

#### Create Payment

```http
POST /clients/payments
Content-Type: application/json

{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "payer_address": "0x123...",
  "payee_address": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
  "amount": "5000000000000000000",
  "chain": "ethereum",
  "currency": "ETH",
  "payment_scheme": "exact",
  "external_reference": "ai-platform-order-123"
}
```

**Response:**
```json
{
  "id": "pay-456",
  "transaction_hash": null,
  "chain": "ethereum",
  "payer_address": "0x123...",
  "payee_address": "0x742d35cc6cf25a8a8c498d0b3045fc22b2b8f7f9",
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "5000000000000000000",
  "facilitator_fee": "125000000000000000",
  "status": "pending",
  "created_at": "2024-01-15T10:45:00Z",
  "expires_at": "2024-01-15T11:00:00Z"
}
```

#### Check Payment Status

```http
GET /clients/payments/{payment_id}
```

#### Confirm Payment

```http
POST /clients/payments/{payment_id}/confirm
Content-Type: application/json

{
  "transaction_hash": "0xdef456...",
  "block_number": 18750000,
  "gas_used": 21000,
  "gas_price": "20000000000"
}
```

#### Report Payment Failure

```http
POST /clients/payments/{payment_id}/fail
Content-Type: application/json

{
  "reason": "Insufficient funds",
  "error_code": "INSUFFICIENT_PAYMENT_TOKENS"
}
```

### 👤 User Management

#### User Profile

```http
GET /clients/profile
Authorization: Bearer {jwt_token}
```

#### Payment History

```http
GET /clients/payment-history?page=1&size=20&status=confirmed
Authorization: Bearer {jwt_token}
```

### ⛓️ Blockchain Information

#### Supported Chains

```http
GET /clients/chains
```

**Response:**
```json
[
  {
    "name": "ethereum",
    "display_name": "Ethereum",
    "chain_id": 1,
    "currency": "ETH", 
    "status": "active",
    "average_fee": "50000000000000000",
    "confirmation_time": "3-5 minutes"
  },
  {
    "name": "base",
    "display_name": "Base",
    "chain_id": 8453,
    "currency": "ETH",
    "status": "active", 
    "average_fee": "1000000000000000",
    "confirmation_time": "10-30 seconds"
  }
]
```

---

## ⚙️ Admin APIs

*For system administrators and platform management*

### 👥 User Management

#### List Users

```http
GET /admin/users?page=1&size=50&role=content_provider&status=active&search=john@example.com
Authorization: Bearer {admin_token}
```

#### Get User Details

```http
GET /admin/users/{user_id}
Authorization: Bearer {admin_token}
```

#### Update User Status

```http
PATCH /admin/users/{user_id}/status?reason=Terms violation
Authorization: Bearer {admin_token}

{
  "new_status": "suspended"
}
```

#### Reset User Public Key

```http
POST /admin/users/{user_id}/reset-api-key
Authorization: Bearer {admin_token}
```

### 📊 System Analytics

#### System Overview

```http
GET /admin/analytics/overview?period=30d
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "users": {
    "total": 1250,
    "active": 890,
    "new_this_period": 156,
    "growth_rate": 0.15
  },
  "content": {
    "total_products": 5670,
    "active_products": 4580,
    "new_this_period": 234
  },
  "payments": {
    "total_volume": "125000000000000000000000",
    "successful_payments": 15678,
    "failed_payments": 234,
    "success_rate": 0.985
  },
  "revenue": {
    "platform_revenue": "3125000000000000000000",
    "facilitator_fees": "781250000000000000000",
    "growth_rate": 0.22
  },
  "health": {
    "system_status": "healthy",
    "uptime": 0.9998,
    "avg_response_time": 145
  }
}
```

#### Revenue Analytics

```http
GET /admin/analytics/revenue?start_date=2024-01-01&end_date=2024-01-31&group_by=week&chain=ethereum
Authorization: Bearer {admin_token}
```

#### User Analytics

```http
GET /admin/analytics/users?period=90d&segment=content_providers
Authorization: Bearer {admin_token}
```

### 🏥 System Monitoring

#### System Health

```http
GET /admin/health
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:45:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 15,
      "connections": {
        "active": 12,
        "max": 100
      }
    },
    "redis": {
      "status": "healthy",
      "memory_usage": 0.45,
      "hit_rate": 0.92
    },
    "blockchain": {
      "ethereum": {
        "status": "healthy",
        "block_height": 18750000,
        "sync_status": "synced"
      },
      "base": {
        "status": "healthy", 
        "block_height": 8920000,
        "sync_status": "synced"
      }
    }
  },
  "uptime": 86400
}
```

#### System Metrics

```http
GET /admin/metrics?metric_type=performance&time_range=1h
Authorization: Bearer {admin_token}
```

#### System Logs

```http
GET /admin/logs?level=ERROR&limit=100&start_time=2024-01-15T00:00:00Z&service=payment_processor
Authorization: Bearer {admin_token}
```

### 💳 Payment Management

#### List All Payments

```http
GET /admin/payments?page=1&size=100&status=failed&chain=ethereum&min_amount=1000000000000000000
Authorization: Bearer {admin_token}
```

#### Process Refund

```http
POST /admin/payments/{payment_id}/refund
Authorization: Bearer {admin_token}

{
  "reason": "Content unavailable",
  "amount": "5000000000000000000",
  "notify_user": true
}
```

### 📝 Content Moderation

#### List All Content

```http
GET /admin/products?page=1&size=50&flagged_only=true&status=active
Authorization: Bearer {admin_token}
```

#### Moderate Content

```http
POST /admin/products/{product_id}/moderate?moderation_action=flag&reason=Inappropriate content
Authorization: Bearer {admin_token}
```

---

## 🔧 Core Service APIs

### 🏥 Health & Status

#### Service Health

```http
GET /health
```

#### Prometheus Metrics

```http
GET /metrics
```

#### Version Information

```http
GET /version
```

#### x402 Protocol Discovery

```http
GET /.well-known/x402
```

**Response:**
```json
{
  "version": "1.0",
  "facilitator": {
    "name": "v402 Facilitator",
    "version": "1.0.0",
    "url": "/api/v1"
  },
  "supported_chains": ["ethereum", "base", "polygon", "arbitrum", "optimism", "bsc", "solana"],
  "supported_schemes": ["exact", "upto", "dynamic"],
  "features": [
    "payment_verification",
    "multi_chain_support",
    "batch_payments", 
    "webhooks",
    "analytics"
  ],
  "endpoints": {
    "discovery": "/api/v1/clients/discover",
    "payment": "/api/v1/clients/payments", 
    "access": "/api/v1/clients/access"
  }
}
```

---

## 🔒 Security & Rate Limiting

### Rate Limits

| User Type | Endpoint Category | Rate Limit |
|-----------|------------------|------------|
| **Anonymous** | Discovery APIs | 20 req/min |
| **Authenticated** | General APIs | 100 req/min |
| **Content Provider** | Provider APIs | 200 req/min |
| **Admin** | Admin APIs | 500 req/min |

### Security Headers

All responses include security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### Error Handling

Standard error response format:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid payment amount",
  "details": {
    "field": "amount",
    "code": "AMOUNT_TOO_LOW"
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

## 📝 Integration Examples

### Content Provider Integration

```javascript
// 1. Create product
const product = await fetch('/api/v1/providers/products', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_public_key_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Premium Content',
    content_url: 'https://yoursite.com/premium/content-123',
    price: '5000000000000000000', // 5 ETH in wei
    type: 'article'
  })
});

// 2. Monitor analytics
const analytics = await fetch('/api/v1/providers/analytics/dashboard?days=30', {
  headers: { 'Authorization': 'Bearer v402_your_api_key' }
});

// 3. Check unpaid requests
const unpaidRequests = await fetch('/api/v1/providers/unpaid-requests?hours=24', {
  headers: { 'Authorization': 'Bearer v402_your_api_key' }
});
```

### Index Client Integration

```python
import httpx

class V402Client:
    def __init__(self, base_url, public_key=None):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {public_key}'} if public_key else {}
    
    async def discover_content(self, query, category=None, price_range=None):
        params = {'query': query}
        if category:
            params['category'] = category
        if price_range:
            params.update(price_range)
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/clients/discover',
                params=params,
                headers=self.headers
            )
            return response.json()
    
    async def access_content(self, product_id, payment_header=None):
        headers = self.headers.copy()
        if payment_header:
            headers['X-PAYMENT'] = payment_header
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/clients/access/{product_id}',
                headers=headers
            )
            return response

# Usage
client = V402Client('https://facilitator.v402.network/api/v1')
content = await client.discover_content('AI tutorials', category='education')
```

### Webhook Handler Example

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();

// Webhook endpoint
app.post('/webhooks/v402', express.raw({type: 'application/json'}), (req, res) => {
  const payload = req.body;
  const signature = req.headers['x-v402-signature'];
  const secret = 'your_webhook_secret';
  
  // Verify webhook signature
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
    
  if (signature !== `sha256=${expectedSignature}`) {
    return res.status(401).send('Invalid signature');
  }
  
  const event = JSON.parse(payload);
  
  // Handle different event types
  switch (event.type) {
    case 'payment.confirmed':
      console.log('Payment confirmed:', event.data);
      // Grant access to content
      break;
      
    case 'payment.failed':
      console.log('Payment failed:', event.data);
      // Handle failed payment
      break;
      
    case 'product.viewed':
      console.log('Product viewed:', event.data);
      // Track analytics
      break;
  }
  
  res.status(200).send('OK');
});
```

## 🚀 Getting Started

1. **Register Account**: Sign up at https://facilitator.v402.network
2. **Generate Key Pair**: Create blockchain key pair (use your wallet's public key)
3. **Test Integration**: Use staging environment first
4. **Configure Webhooks**: Set up real-time notifications
5. **Go Live**: Switch to production environment

## 📚 Additional Resources

- **Interactive API Explorer**: https://facilitator.v402.network/docs
- **Code Examples**: https://github.com/v402/examples
- **SDK Documentation**: https://docs.v402.network/sdks
- **Protocol Specification**: https://docs.v402.network/x402
- **Discord Community**: https://discord.gg/v402
- **Status Page**: https://status.v402.network

---

**🎯 Ready to monetize your content with v402? Start with our [Quick Start Guide](GETTING_STARTED.md) and join the future of web monetization!**
