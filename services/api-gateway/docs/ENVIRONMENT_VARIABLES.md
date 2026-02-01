# API Gateway - Environment Variables Reference

> Complete reference for all environment variables used by the API Gateway

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Required Variables](#required-variables)
3. [Server Configuration](#server-configuration)
4. [Service URLs](#service-urls)
5. [Security Configuration](#security-configuration)
6. [Rate Limiting](#rate-limiting)
7. [Circuit Breaker](#circuit-breaker)
8. [Logging](#logging)
9. [Performance](#performance)
10. [Development](#development)
11. [Environment Examples](#environment-examples)

---

## Quick Reference

### Minimal Configuration

```bash
# Required for basic operation
PORT=3000
NODE_ENV=production
JWT_SECRET=your-super-secret-jwt-key
REDIS_URL=redis://localhost:6379

# Service URLs (all required)
AUTH_SERVICE_URL=http://localhost:3001
CODE_REVIEW_ENGINE_URL=http://localhost:3002
ARCHITECTURE_ANALYZER_URL=http://localhost:3003
AGENTIC_AI_URL=http://localhost:3004
PROJECT_MANAGER_URL=http://localhost:3005
```

### Production Checklist

- [ ] `JWT_SECRET` is strong and unique
- [ ] All service URLs use HTTPS
- [ ] `CORS_ALLOWED_ORIGINS` is restricted
- [ ] `LOG_LEVEL` is set to `warn` or `error`
- [ ] `TRUST_PROXY` is enabled if behind load balancer
- [ ] Rate limits are appropriate for production load

---

## Required Variables

These variables MUST be set for the gateway to start:

### PORT
- **Type**: Number
- **Default**: `3000`
- **Description**: Port number for the API Gateway server
- **Example**: `PORT=3000`
- **Production**: Use standard ports (80, 443, 8080)

### NODE_ENV
- **Type**: String
- **Default**: `development`
- **Options**: `development`, `staging`, `production`
- **Description**: Node environment affects logging, error handling, and optimizations
- **Example**: `NODE_ENV=production`

### JWT_SECRET
- **Type**: String
- **Required**: Yes
- **Description**: Secret key for JWT token verification
- **Security**: NEVER commit to version control
- **Generate**: `openssl rand -base64 32`
- **Example**: `JWT_SECRET=your-super-secret-key-here`
- **Production**: Must be strong and unique per environment

### REDIS_URL
- **Type**: String (URL)
- **Required**: Yes (for rate limiting)
- **Default**: `redis://localhost:6379`
- **Format**: `redis://[username:password@]host:port[/database]`
- **Examples**:
  - Local: `redis://localhost:6379`
  - With auth: `redis://:password@localhost:6379`
  - Remote: `redis://user:pass@redis.example.com:6379/0`

### Service URLs (All Required)

#### AUTH_SERVICE_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3001`
- **Description**: Authentication service URL
- **Example**: `AUTH_SERVICE_URL=https://auth.example.com`

#### CODE_REVIEW_ENGINE_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3002`
- **Description**: Code review engine service URL
- **Example**: `CODE_REVIEW_ENGINE_URL=https://review.example.com`

#### ARCHITECTURE_ANALYZER_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3003`
- **Description**: Architecture analyzer service URL
- **Example**: `ARCHITECTURE_ANALYZER_URL=https://arch.example.com`

#### AGENTIC_AI_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3004`
- **Description**: Agentic AI service URL
- **Example**: `AGENTIC_AI_URL=https://ai.example.com`

#### PROJECT_MANAGER_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3005`
- **Description**: Project manager service URL
- **Example**: `PROJECT_MANAGER_URL=https://projects.example.com`

---

## Server Configuration

### JWT_EXPIRES_IN
- **Type**: String (time)
- **Default**: `24h`
- **Format**: `<number><unit>` where unit is s, m, h, or d
- **Description**: JWT token expiration time
- **Examples**:
  - `JWT_EXPIRES_IN=30m` (30 minutes)
  - `JWT_EXPIRES_IN=1h` (1 hour)
  - `JWT_EXPIRES_IN=7d` (7 days)
- **Production**: Shorter expiration for better security

### CORS_ALLOWED_ORIGINS
- **Type**: String (comma-separated URLs)
- **Default**: `http://localhost:3000`
- **Description**: Allowed origins for CORS
- **Example**: `CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com`
- **Production**: List only trusted domains
- **Development**: Can include localhost

### TRUST_PROXY
- **Type**: Boolean
- **Default**: `false`
- **Description**: Trust proxy headers (X-Forwarded-For, etc.)
- **Example**: `TRUST_PROXY=true`
- **Production**: Set to `true` if behind reverse proxy/load balancer

---

## Security Configuration

### GITHUB_WEBHOOK_SECRET
- **Type**: String
- **Optional**: Yes
- **Description**: Secret for verifying GitHub webhook signatures
- **Example**: `GITHUB_WEBHOOK_SECRET=your-webhook-secret`
- **Security**: Keep secret, rotate regularly

### ENABLE_HELMET
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable Helmet security headers
- **Example**: `ENABLE_HELMET=true`
- **Production**: Always keep enabled

### ENABLE_CORS
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable Cross-Origin Resource Sharing
- **Example**: `ENABLE_CORS=true`

---

## Rate Limiting

### RATE_LIMIT_WINDOW_MS
- **Type**: Number (milliseconds)
- **Default**: `900000` (15 minutes)
- **Description**: Time window for rate limiting
- **Examples**:
  - 1 minute: `60000`
  - 15 minutes: `900000`
  - 1 hour: `3600000`

### RATE_LIMIT_MAX
- **Type**: Number
- **Default**: `100`
- **Description**: Maximum requests per IP within window
- **Recommendations**:
  - Low traffic: `50-100`
  - Medium traffic: `100-500`
  - High traffic: `500-1000`

### AUTH_RATE_LIMIT_WINDOW_MS
- **Type**: Number (milliseconds)
- **Default**: `900000` (15 minutes)
- **Description**: Stricter rate limit window for auth endpoints

### AUTH_RATE_LIMIT_MAX
- **Type**: Number
- **Default**: `5`
- **Description**: Lower limit for authentication to prevent brute force
- **Security**: Keep low to prevent attacks

---

## Circuit Breaker

### CIRCUIT_BREAKER_TIMEOUT
- **Type**: Number (milliseconds)
- **Default**: `10000` (10 seconds)
- **Description**: Maximum time to wait for service response
- **Recommendations**:
  - Fast services: `5000-10000`
  - Slow services: `15000-30000`

### CIRCUIT_BREAKER_ERROR_THRESHOLD
- **Type**: Number (percentage)
- **Default**: `50`
- **Range**: `0-100`
- **Description**: Error rate that triggers circuit breaker
- **Recommendations**:
  - Strict: `30-40`
  - Balanced: `50`
  - Lenient: `60-70`

### CIRCUIT_BREAKER_RESET_TIMEOUT
- **Type**: Number (milliseconds)
- **Default**: `60000` (1 minute)
- **Description**: Time before attempting to close circuit
- **Recommendations**:
  - Quick recovery: `30000`
  - Standard: `60000`
  - Slow recovery: `120000`

### CIRCUIT_BREAKER_VOLUME_THRESHOLD
- **Type**: Number
- **Default**: `10`
- **Description**: Minimum requests before circuit can open
- **Purpose**: Prevents opening on low traffic

---

## Logging

### LOG_LEVEL
- **Type**: String
- **Default**: `info`
- **Options**: `error`, `warn`, `info`, `http`, `verbose`, `debug`, `silly`
- **Description**: Controls log verbosity
- **Recommendations**:
  - Production: `warn` or `error`
  - Staging: `info`
  - Development: `debug`

### LOG_FORMAT
- **Type**: String
- **Default**: `json`
- **Options**: `json`, `simple`, `combined`
- **Description**: Log output format
- **Recommendations**:
  - Production: `json` (easier to parse)
  - Development: `simple` (easier to read)

### LOG_TO_FILE
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable file logging
- **Files**:
  - `logs/combined.log` - All logs
  - `logs/error.log` - Errors only

### LOG_DIR
- **Type**: String
- **Default**: `logs`
- **Description**: Directory for log files
- **Production**: Use absolute path like `/var/log/api-gateway`

---

## Performance

### MAX_REQUEST_BODY_SIZE
- **Type**: String
- **Default**: `10mb`
- **Format**: `<number><unit>` (b, kb, mb, gb)
- **Description**: Maximum request body size
- **Security**: Prevents memory exhaustion

### REQUEST_TIMEOUT
- **Type**: Number (milliseconds)
- **Default**: `30000` (30 seconds)
- **Description**: Maximum request processing time

### ENABLE_COMPRESSION
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable gzip compression for responses
- **Impact**: Reduces bandwidth, increases CPU usage

### ENABLE_CACHING
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable response caching (requires Redis)
- **Note**: Currently not implemented

### CACHE_TTL
- **Type**: Number (seconds)
- **Default**: `300` (5 minutes)
- **Description**: Cache time-to-live

---

## Development

### DEBUG_MODE
- **Type**: Boolean
- **Default**: `false`
- **Description**: Additional debug logging and error details
- **Usage**: Set to `true` only in development

### ENABLE_HOT_RELOAD
- **Type**: Boolean
- **Default**: `true`
- **Description**: Automatically restart on file changes (development only)

### MOCK_SERVICES
- **Type**: Boolean
- **Default**: `false`
- **Description**: Use mock services instead of real microservices (testing only)

---

## Environment Examples

### Development

```bash
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug
DEBUG_MODE=true

JWT_SECRET=dev-secret-key
JWT_EXPIRES_IN=24h

REDIS_URL=redis://localhost:6379

AUTH_SERVICE_URL=http://localhost:3001
CODE_REVIEW_ENGINE_URL=http://localhost:3002
ARCHITECTURE_ANALYZER_URL=http://localhost:3003
AGENTIC_AI_URL=http://localhost:3004
PROJECT_MANAGER_URL=http://localhost:3005

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100

ENABLE_HOT_RELOAD=true
MOCK_SERVICES=false
```

### Staging

```bash
NODE_ENV=staging
PORT=3000
LOG_LEVEL=info

JWT_SECRET=staging-strong-secret-key
JWT_EXPIRES_IN=2h

REDIS_URL=redis://:password@redis-staging.example.com:6379

AUTH_SERVICE_URL=https://auth-staging.example.com
CODE_REVIEW_ENGINE_URL=https://review-staging.example.com
ARCHITECTURE_ANALYZER_URL=https://arch-staging.example.com
AGENTIC_AI_URL=https://ai-staging.example.com
PROJECT_MANAGER_URL=https://projects-staging.example.com

CORS_ALLOWED_ORIGINS=https://app-staging.example.com

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=200

CIRCUIT_BREAKER_TIMEOUT=10000
CIRCUIT_BREAKER_ERROR_THRESHOLD=50
CIRCUIT_BREAKER_RESET_TIMEOUT=60000

TRUST_PROXY=true
ENABLE_COMPRESSION=true
```

### Production

```bash
NODE_ENV=production
PORT=3000
LOG_LEVEL=warn

JWT_SECRET=production-very-strong-secret-key
JWT_EXPIRES_IN=1h

REDIS_URL=redis://:strong-password@redis-cluster.example.com:6379

AUTH_SERVICE_URL=https://auth.example.com
CODE_REVIEW_ENGINE_URL=https://review.example.com
ARCHITECTURE_ANALYZER_URL=https://arch.example.com
AGENTIC_AI_URL=https://ai.example.com
PROJECT_MANAGER_URL=https://projects.example.com

CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=500

AUTH_RATE_LIMIT_WINDOW_MS=900000
AUTH_RATE_LIMIT_MAX=5

CIRCUIT_BREAKER_TIMEOUT=10000
CIRCUIT_BREAKER_ERROR_THRESHOLD=50
CIRCUIT_BREAKER_RESET_TIMEOUT=60000
CIRCUIT_BREAKER_VOLUME_THRESHOLD=10

LOG_FORMAT=json
LOG_TO_FILE=true
LOG_DIR=/var/log/api-gateway

TRUST_PROXY=true
ENABLE_COMPRESSION=true
ENABLE_HELMET=true
ENABLE_CORS=true

MAX_REQUEST_BODY_SIZE=10mb
REQUEST_TIMEOUT=30000
```

### Docker Compose

```bash
NODE_ENV=production
PORT=3000

JWT_SECRET=${JWT_SECRET}
REDIS_URL=redis://redis:6379

# Use Docker service names
AUTH_SERVICE_URL=http://auth-service:3001
CODE_REVIEW_ENGINE_URL=http://ai-service:3002
ARCHITECTURE_ANALYZER_URL=http://architecture-analyzer:3003
AGENTIC_AI_URL=http://ai-service:3004
PROJECT_MANAGER_URL=http://project-manager:3005

CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
```

---

## Validation

### Startup Validation

The gateway validates configuration on startup:

**Required Variables Checked**:
- `PORT`
- `NODE_ENV`
- `JWT_SECRET`
- `REDIS_URL`
- All `*_SERVICE_URL` variables

**Validation Errors**:
- Missing required variables → Fatal error
- Invalid values → Warning + default value
- Connection failures → Retry with backoff

### Runtime Validation

```bash
# Check current configuration
curl http://localhost:3000/admin/config
# (Admin endpoint, requires admin token)

# Validate service connectivity
curl http://localhost:3000/health
```

---

## Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   .env.*.local
   ```

2. **Use strong JWT secrets**
   ```bash
   # Generate secure secret
   openssl rand -base64 32
   ```

3. **Rotate secrets regularly**
   - JWT secrets: Every 90 days
   - Webhook secrets: Every 180 days

4. **Use different secrets per environment**
   - Development: Simple secrets OK
   - Staging: Strong secrets
   - Production: Very strong secrets

5. **Limit CORS origins**
   ```bash
   # Bad (development only)
   CORS_ALLOWED_ORIGINS=*
   
   # Good (production)
   CORS_ALLOWED_ORIGINS=https://app.example.com
   ```

6. **Enable rate limiting**
   - Always enable in production
   - Adjust limits based on usage patterns

7. **Use HTTPS in production**
   - All service URLs should use HTTPS
   - Enable `TRUST_PROXY` behind load balancer

---

## Troubleshooting

### Check Configuration

```bash
# View environment variables
printenv | grep -E '(PORT|NODE_ENV|JWT|REDIS|SERVICE)'

# Or in Node.js
node -e "require('dotenv').config(); console.log(process.env)"
```

### Validate Configuration

```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping

# Test service URLs
curl $AUTH_SERVICE_URL/health
curl $CODE_REVIEW_ENGINE_URL/health
```

### Common Issues

1. **"JWT secret not configured"**
   - Set `JWT_SECRET` in `.env`

2. **"Redis connection refused"**
   - Check `REDIS_URL`
   - Ensure Redis is running

3. **"Service Unavailable"**
   - Verify service URLs
   - Check service health

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0