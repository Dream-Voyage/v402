# 🚀 Getting Started with v402

Welcome to v402, the next-generation framework for content monetization and micropayments! This guide will help you get up and running quickly.

## 📋 Table of Contents

1. [What is v402?](#what-is-v402)
2. [Quick Setup](#quick-setup)
3. [Choose Your Path](#choose-your-path)
4. [Complete Examples](#complete-examples)
5. [Next Steps](#next-steps)

## 🤔 What is v402?

v402 is a comprehensive framework that enables seamless micropayments for content access across the web. Built on the x402 protocol, it provides:

- **Multi-chain payment support** (Ethereum, Base, Polygon, Solana, BSC)
- **Automatic payment handling** for 402 Payment Required responses
- **SDKs for multiple languages** (Python, Go, Java, Rust)
- **Frontend components** (React, Vue, Web Components)
- **Enterprise-grade infrastructure** with monitoring and scaling

## ⚡ Quick Setup

### 1. Prerequisites

- **Node.js 16+** (for JavaScript components)
- **Docker & Docker Compose** (for full stack setup)
- **Web3 Wallet** (MetaMask, WalletConnect, etc.)
- **Private Key** for signing transactions

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/v402/v402-framework.git
cd v402-framework

# Copy environment template
cp .env.example .env

# Edit your configuration
nano .env
```

### 3. Environment Configuration

```bash
# .env file
V402_PRIVATE_KEY=0x1234567890abcdef...  # Your wallet private key
V402_FACILITATOR_URL=https://facilitator.v402.network

# Optional: Custom RPC endpoints
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_KEY
BASE_RPC=https://mainnet.base.org
POLYGON_RPC=https://polygon-rpc.com

# Optional: Custom configuration
V402_MAX_AMOUNT=1000000000000000000  # 1 ETH in wei
V402_AUTO_PAY=true
```

### 4. Start the Stack

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f facilitator
```

**🎉 Your v402 stack is now running!**

- **Facilitator**: http://localhost:8080
- **Example Frontend**: http://localhost:3000
- **Monitoring**: http://localhost:3001 (Grafana)
- **Metrics**: http://localhost:9091 (Prometheus)

## 🛤️ Choose Your Path

### Path A: I want to accept payments (Content Provider)

**Perfect for:** Content creators, API providers, SaaS platforms

```javascript
// Add to your website
import { V402PaymentButton } from '@v402/provider/react';

function PremiumContent() {
  return (
    <V402PaymentButton
      resourceId="premium-article-123"
      description="Access Premium Article"
      amount="500000000000000000" // 0.5 ETH
      onPaymentSuccess={(result) => {
        console.log('Payment received!', result);
        // Unlock content
      }}
    />
  );
}
```

**→ [Content Provider Setup Guide](./docs/content-provider-setup.md)**

### Path B: I want to make payments (Index/AI Platform)

**Perfect for:** AI platforms, search engines, data aggregators

```python
# Python example
from v402_client import AsyncV402Client, ClientSettings

async def fetch_premium_content():
    settings = ClientSettings(
        private_key="0x...",
        auto_pay=True,
        max_amount_per_request="1000000000000000000"
    )
    
    async with AsyncV402Client(settings) as client:
        response = await client.get("https://example.com/premium")
        return response.text()
```

**→ [Index Client Setup Guide](./docs/index-client-setup.md)**

### Path C: I want to build both (Full Platform)

**Perfect for:** Marketplaces, multi-sided platforms, enterprise solutions

```bash
# Clone the complete example
git clone https://github.com/v402/blog-platform-example.git
cd blog-platform-example
docker-compose up
```

**→ [Full Platform Tutorial](./examples/end_to_end/blog_platform/)**

## 📚 Complete Examples

### 1. Simple Blog with Paywall

```bash
cd examples/end_to_end/blog_platform
docker-compose up
```

**Features:**
- User registration and authentication
- Free and premium articles
- Automatic payment processing
- Revenue analytics dashboard

**Tech Stack:** Next.js + FastAPI + PostgreSQL

### 2. API Marketplace

```bash
cd examples/end_to_end/api_marketplace
docker-compose up
```

**Features:**
- API provider registration
- Pay-per-call pricing
- Usage analytics
- Rate limiting with payment bypass

**Tech Stack:** React + Go + Redis

### 3. Video Streaming Platform

```bash
cd examples/end_to_end/video_platform
docker-compose up
```

**Features:**
- Pay-per-view videos
- Subscription tiers
- Real-time payment verification
- Content delivery optimization

**Tech Stack:** Vue.js + Java Spring Boot + MongoDB

## 🔧 Language-Specific Quick Starts

### Python 🐍

```bash
pip install v402-client

# Basic usage
python examples/python/basic_client.py
```

### Go 🐹

```bash
go mod download
go run examples/go/basic_client.go
```

### Java ☕

```bash
mvn install
mvn exec:java -Dexec.mainClass="BasicClient"
```

### Rust 🦀

```bash
cargo build --release
cargo run --example basic_client
```

### JavaScript 🌐

```bash
npm install @v402/provider
# See examples/javascript/ for framework-specific examples
```

## 🎯 Common Use Cases

### 1. Content Monetization
- **Newspapers & Blogs**: Premium articles behind paywall
- **Educational Platforms**: Course access and materials
- **Research Papers**: Academic publication access
- **Creative Content**: Art, music, video access

### 2. API Monetization
- **Data APIs**: Weather, financial, social media data
- **AI Services**: Image recognition, language processing
- **Utility APIs**: PDF generation, email sending
- **Real-time Feeds**: Market data, news feeds

### 3. Digital Services
- **Cloud Storage**: Pay-per-GB storage
- **Computing Resources**: On-demand processing
- **Communication**: Premium messaging features
- **Analytics**: Advanced reporting and insights

## 📊 Monitoring Your Deployment

Access your monitoring dashboard at http://localhost:3001:

- **Payment Volume**: Track successful transactions
- **Revenue Analytics**: Monitor earnings by content/API
- **Error Rates**: Identify and fix payment issues
- **Performance Metrics**: Optimize response times

**Default Credentials:**
- Username: `admin`
- Password: `v402admin`

## 🔐 Security Checklist

Before going to production:

- [ ] **Secure your private keys** (use hardware wallets or KMS)
- [ ] **Enable HTTPS** with valid certificates
- [ ] **Set up monitoring** and alerting
- [ ] **Configure rate limiting** to prevent abuse
- [ ] **Test payment flows** on testnets first
- [ ] **Backup your data** regularly
- [ ] **Review logs** for suspicious activity

## 🆘 Troubleshooting

### Common Issues

**❌ "Provider not initialized"**
```bash
# Check if facilitator is running
curl http://localhost:8080/health

# Check your private key format
echo $V402_PRIVATE_KEY | wc -c  # Should be 66 characters
```

**❌ "Payment failed" errors**
```bash
# Check your wallet balance
# Verify network connectivity
# Check RPC endpoint status
```

**❌ "Connection timeout"**
```bash
# Check Docker container status
docker-compose ps

# Check network connectivity
docker network ls
```

### Get Help

- 📖 **Documentation**: [Full API Reference](./docs/api/)
- 💬 **Discord**: [Join our community](https://discord.gg/v402)
- 🐛 **Issues**: [GitHub Issues](https://github.com/v402/v402-framework/issues)
- 📧 **Email**: support@v402.network

## 🎉 Next Steps

Once you have the basics working:

1. **🔨 Customize the UI** - Modify themes and styles to match your brand
2. **⚡ Optimize Performance** - Configure caching and connection pooling
3. **📈 Add Analytics** - Integrate with your existing analytics platform
4. **🔗 Multi-chain Setup** - Add support for additional blockchain networks
5. **🛡️ Production Hardening** - Implement security best practices
6. **🚀 Scale Up** - Set up load balancing and horizontal scaling

**Ready to revolutionize content monetization? Let's build the future of the open web together! 🌐💰**

---

**💡 Pro Tip**: Start with the examples that match your use case, then gradually customize to fit your specific needs. The v402 framework is designed to scale from simple prototypes to enterprise-grade deployments.