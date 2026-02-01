# API Gateway - Production Deployment Guide

This guide covers deploying the API Gateway to production using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Redis instance (for rate limiting)
- Access to backend microservices

## Quick Start

### 1. Environment Setup

Copy the production environment template:
```bash
cp .env.production.example .env.production
```

Edit `.env.production` with your actual values:
```bash
# Required - Generate strong secrets
JWT_SECRET=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
NEO4J_PASSWORD=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)

# Required - Set your domain
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Optional - API keys for external services
OPENAI_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
```

### 2. Build and Deploy

Build the production image:
```bash
docker-compose -f docker-compose.yml --env-file .env.production build api-gateway
```

Start all services:
```bash
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

### 3. Verify Deployment

Check service health:
```bash
# Check all services
docker-compose ps

# Check API Gateway logs
docker-compose logs api-gateway

# Test health endpoint
curl http://localhost:3000/health
```

Expected health response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T10:00:00Z",
  "services": {
    "redis": "connected",
    "auth": "healthy",
    "projects": "healthy",
    "reviews": "healthy",
    "architecture": "healthy"
  }
}
```

## Production Configuration

### Environment Variables

#### Required Variables
- `JWT_SECRET` - Strong secret for JWT tokens (32+ characters)
- `POSTGRES_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password
- `NEO4J_PASSWORD` - Neo4j password
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins

#### Security Settings
```bash
NODE_ENV=production
LOG_LEVEL=warn
TRUST_PROXY=true
ENABLE_HELMET=true
ENABLE_CORS=true
```

#### Performance Settings
```bash
RATE_LIMIT_MAX=500
CIRCUIT_BREAKER_TIMEOUT=10000
ENABLE_COMPRESSION=true
MAX_REQUEST_BODY_SIZE=10mb
```

### Resource Limits

The API Gateway is configured with:
- **Memory**: 512MB limit, 256MB reservation
- **CPU**: 0.5 cores limit, 0.25 cores reservation

Adjust in `docker-compose.yml` if needed:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

## Monitoring

### Health Checks

The API Gateway includes built-in health checks:
- **Endpoint**: `GET /health`
- **Docker**: Automatic health check every 30s
- **Timeout**: 10s
- **Retries**: 3

### Logging

Logs are written to:
- **Container**: stdout/stderr (JSON format)
- **Host**: `./services/api-gateway/logs/`

View logs:
```bash
# Real-time logs
docker-compose logs -f api-gateway

# Last 100 lines
docker-compose logs --tail=100 api-gateway

# Logs from host
tail -f services/api-gateway/logs/combined.log
```

### Metrics

Monitor these key metrics:
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Circuit breaker state
- Rate limit hits

## Scaling

### Horizontal Scaling

Run multiple API Gateway instances:
```bash
docker-compose up -d --scale api-gateway=3
```

Use a load balancer (nginx, HAProxy) to distribute traffic.

### Vertical Scaling

Increase resource limits:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '2.0'
```

## Security

### HTTPS Setup

Use a reverse proxy (nginx, Traefik) for HTTPS:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Rules

Restrict access to:
- Port 3000: Only from load balancer
- Database ports: Only from application containers
- Redis port: Only from application containers

### Secret Management

Use Docker secrets or external secret management:
```yaml
secrets:
  jwt_secret:
    external: true
  postgres_password:
    external: true

services:
  api-gateway:
    secrets:
      - jwt_secret
      - postgres_password
```

## Backup and Recovery

### Database Backup

Backup PostgreSQL:
```bash
docker-compose exec postgres pg_dump -U postgres ai_code_review > backup.sql
```

### Configuration Backup

Backup important files:
- `.env.production`
- `docker-compose.yml`
- SSL certificates
- Application logs

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose logs api-gateway

# Check configuration
docker-compose config

# Verify environment variables
docker-compose exec api-gateway env | grep -E '(JWT|REDIS|SERVICE)'
```

#### 2. High Memory Usage
```bash
# Check memory usage
docker stats api-gateway

# Increase memory limit
# Edit docker-compose.yml resources.limits.memory
```

#### 3. Rate Limiting Issues
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check rate limit configuration
curl -I http://localhost:3000/health
# Look for X-RateLimit-* headers
```

#### 4. Circuit Breaker Tripping
```bash
# Check service health
curl http://localhost:3001/health  # auth-service
curl http://localhost:3002/health  # code-review-engine

# Check circuit breaker logs
docker-compose logs api-gateway | grep -i circuit
```

### Debug Mode

Enable debug logging:
```bash
# Temporary
docker-compose exec api-gateway sh -c 'LOG_LEVEL=debug npm start'

# Permanent
# Edit .env.production: LOG_LEVEL=debug
docker-compose restart api-gateway
```

## Performance Tuning

### Rate Limiting

Adjust based on traffic patterns:
```bash
# High traffic
RATE_LIMIT_MAX=1000
RATE_LIMIT_WINDOW_MS=60000  # 1 minute

# Low traffic
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=900000  # 15 minutes
```

### Circuit Breaker

Tune for service reliability:
```bash
# Strict (fail fast)
CIRCUIT_BREAKER_ERROR_THRESHOLD=30
CIRCUIT_BREAKER_RESET_TIMEOUT=30000

# Lenient (more tolerant)
CIRCUIT_BREAKER_ERROR_THRESHOLD=70
CIRCUIT_BREAKER_RESET_TIMEOUT=120000
```

### Connection Pooling

Optimize for your backend services:
```bash
# High throughput
REQUEST_TIMEOUT=10000
MAX_REQUEST_BODY_SIZE=50mb

# Low latency
REQUEST_TIMEOUT=5000
MAX_REQUEST_BODY_SIZE=1mb
```

## Maintenance

### Updates

1. Build new image:
```bash
docker-compose build api-gateway
```

2. Rolling update:
```bash
docker-compose up -d --no-deps api-gateway
```

3. Verify deployment:
```bash
curl http://localhost:3000/health
```

### Log Rotation

Configure log rotation:
```bash
# Add to crontab
0 0 * * * docker-compose exec api-gateway logrotate /etc/logrotate.conf
```

### Cleanup

Remove old images:
```bash
docker image prune -f
docker system prune -f
```

## Support

For issues and questions:
- Check logs: `docker-compose logs api-gateway`
- Review configuration: `docker-compose config`
- Test connectivity: `curl http://localhost:3000/health`
- Monitor resources: `docker stats`

---

**Last Updated**: January 22, 2026  
**Version**: 1.0.0