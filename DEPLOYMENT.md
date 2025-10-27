# v402 Deployment Guide

This guide covers deploying v402 components in production environments.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+ (recommended for production)
- RPC access to blockchain network
- SSL certificates for HTTPS
- Domain names configured

## Facilitator Deployment

### Configuration

Create a production `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# Blockchain
NETWORK=base
RPC_URL=https://mainnet.base.org
PRIVATE_KEY=<your-private-key>
CHAIN_ID=8453

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/v402

# Security
API_KEY=<strong-random-key>
ENABLE_RATE_LIMIT=true
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Deployment

1. **Build Docker Image**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY v402_facilitator/pyproject.toml .
COPY x402 ./x402
RUN pip install --no-cache-dir -e .

# Copy application
COPY v402_facilitator ./v402_facilitator

# Run
CMD ["uvicorn", "v402_facilitator.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

2. **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  facilitator:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: v402
      POSTGRES_USER: v402user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - facilitator
    restart: unless-stopped

volumes:
  postgres_data:
```

3. **Deploy**

```bash
docker-compose up -d
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: v402-facilitator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: v402-facilitator
  template:
    metadata:
      labels:
        app: v402-facilitator
    spec:
      containers:
      - name: facilitator
        image: your-registry/v402-facilitator:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: v402-secrets
              key: database-url
        - name: PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: v402-secrets
              key: private-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: v402-facilitator
spec:
  selector:
    app: v402-facilitator
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Systemd Service

```ini
# /etc/systemd/system/v402-facilitator.service
[Unit]
Description=v402 Facilitator Service
After=network.target postgresql.service

[Service]
Type=simple
User=v402
WorkingDirectory=/opt/v402
Environment="PATH=/opt/v402/venv/bin"
EnvironmentFile=/opt/v402/.env
ExecStart=/opt/v402/venv/bin/uvicorn v402_facilitator.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable v402-facilitator
sudo systemctl start v402-facilitator
sudo systemctl status v402-facilitator
```

## Content Provider Deployment

### Simple Deployment

For a FastAPI content provider:

```bash
# Install
pip install -e ./v402_content_provider

# Run with uvicorn
uvicorn your_app:app --host 0.0.0.0 --port 8001 --workers 4
```

### With Nginx

```nginx
# /etc/nginx/sites-available/content-provider
upstream content_provider {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name content.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name content.example.com;

    ssl_certificate /etc/ssl/certs/content.example.com.crt;
    ssl_certificate_key /etc/ssl/private/content.example.com.key;

    location / {
        proxy_pass http://content_provider;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Important: Don't modify these headers
        proxy_pass_header X-PAYMENT;
        proxy_pass_header X-PAYMENT-RESPONSE;
    }
}
```

## Database Setup

### PostgreSQL Initialization

```sql
-- Create database
CREATE DATABASE v402;

-- Create user
CREATE USER v402user WITH PASSWORD 'strong_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE v402 TO v402user;

-- Connect to database
\c v402

-- Create tables (done automatically by application)
-- But you can also run migrations manually
```

### Migrations

```bash
# Install alembic
pip install alembic

# Initialize migrations
cd v402_facilitator
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Security Hardening

### 1. Private Key Management

**Use Secret Management**:
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id v402/private-key

# HashiCorp Vault
vault kv get secret/v402/private-key

# Kubernetes Secrets
kubectl create secret generic v402-secrets \
  --from-literal=private-key=$PRIVATE_KEY
```

### 2. Network Security

```bash
# Firewall rules (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# Or iptables
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 3. Rate Limiting

```python
# In facilitator config
ENABLE_RATE_LIMIT=true
RATE_LIMIT_PER_MINUTE=100
```

### 4. API Authentication

```python
# Add API key middleware
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401)
```

## Monitoring

### Prometheus Metrics

```python
# Add to facilitator
from prometheus_client import Counter, Histogram, generate_latest

payment_counter = Counter('payments_total', 'Total payments processed')
settlement_duration = Histogram('settlement_duration_seconds', 'Settlement duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana Dashboard

Import the provided `grafana-dashboard.json` for monitoring:
- Request rate
- Payment success rate
- Settlement time
- Error rate
- Database performance

### Logging

```python
# Structured logging
import structlog

logger = structlog.get_logger()
logger.info("payment_verified", payer=payer, amount=amount)
```

### Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Docker healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Backup and Recovery

### Database Backups

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U v402user v402 > /backups/v402_$DATE.sql
# Compress
gzip /backups/v402_$DATE.sql
# Upload to S3
aws s3 cp /backups/v402_$DATE.sql.gz s3://my-backups/v402/
# Keep only last 30 days
find /backups -name "v402_*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/v402/backup.sh
```

### Disaster Recovery

1. **Document RPC endpoints**: Keep backup RPC providers
2. **Key Recovery**: Store encrypted backups of private keys
3. **Database Replication**: Set up PostgreSQL replication
4. **Multi-Region**: Deploy across multiple regions

## Performance Tuning

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_transactions_payer ON transactions(payer);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_discovery_resource ON discovery_resources(resource);

-- Vacuum and analyze
VACUUM ANALYZE transactions;
VACUUM ANALYZE discovery_resources;
```

### Connection Pooling

```python
# In database.py
engine = create_async_engine(
    database_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching

```python
# Add Redis caching
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://localhost")

# Cache verification results
await redis.setex(f"verify:{nonce}", 300, "verified")
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check connection string
   - Verify PostgreSQL is running
   - Check network connectivity

2. **RPC Errors**
   - Verify RPC URL is correct
   - Check API rate limits
   - Try backup RPC provider

3. **Settlement Failures**
   - Check gas price
   - Verify sufficient ETH for gas
   - Check nonce management

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m v402_facilitator.main
```

### Logs Location

```bash
# Systemd
journalctl -u v402-facilitator -f

# Docker
docker logs -f v402-facilitator

# File
tail -f /var/log/v402/facilitator.log
```

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use Nginx, HAProxy, or cloud load balancer
2. **Database**: Use PostgreSQL with read replicas
3. **Cache Layer**: Add Redis for frequently accessed data
4. **CDN**: Cache static content

### Vertical Scaling

- Increase CPU/RAM
- Use faster storage (SSD/NVMe)
- Optimize database queries
- Profile and optimize hot paths

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -e . --upgrade

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart v402-facilitator
```

### Monitoring Checklist

- [ ] Check error rates
- [ ] Monitor payment success rate
- [ ] Check database size
- [ ] Verify backup completion
- [ ] Check disk space
- [ ] Monitor RPC health
- [ ] Review security logs

## Cost Optimization

1. **RPC Costs**: Use rate limiting, cache results
2. **Database**: Optimize queries, add indexes
3. **Compute**: Right-size instances
4. **Network**: Use CDN for static content
5. **Storage**: Implement data lifecycle policies

## Support

For deployment issues:
- Check logs first
- Review configuration
- Consult documentation
- Open issue on GitHub

