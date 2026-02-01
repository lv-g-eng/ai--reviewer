# API Gateway - Configuration Guide

> Complete reference for configuring the API Gateway

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Server Configuration](#server-configuration)
3. [Service URLs](#service-urls)
4. [Security Configuration](#security-configuration)
5. [Rate Limiting](#rate-limiting)
6. [Circuit Breaker](#circuit-breaker)
7. [Logging](#logging)
8. [Performance Tuning](#performance-tuning)

---

## Environment Variables

All configuration is done through environment variables defined in `.env` file.

### Quick Setup

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

---

## Server Configuration

### PORT
- **Type**: Number
- **Default**: `3000`
- **Description**: Port number for the API Gateway server
- **Example**: `PORT=3000`

### NODE_ENV
- **Type**: String
- **Default**: `development`
- **Options**: `development`, `staging`, `production`
- **Description**: Node environment affects logging, error handling, and optimizations
- **Example**: `NODE_ENV=production`

**Environment-Specific Behavior**:
- **Development**: Verbose logging, stack traces in errors, hot reload
- **Staging**: Info logging, limited stack traces, performance monitoring
- **Production**: Warn/error logging only, no stack traces, optimized performance

---

## Service URLs

Configure URLs for all backend microservices.

### AUTH_SERVICE_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3001`
- **Description**: Authentication service URL
- **Example**: `AUTH_SERVICE_URL=http://auth-service:3001`

### CODE_REVIEW_ENGINE_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3002`
- **Description**: Code review engine service URL
- **Example**: `CODE_REVIEW_ENGINE_URL=http://review-service:3002`

### ARCHITECTURE_ANALYZER_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3003`
- **Description**: Architecture analyzer service URL
- **Example**: `ARCHITECTURE_ANALYZER_URL=http://arch-service:3003`

### AGENTIC_AI_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3004`
- **Description**: Agentic AI service URL
- **Example**: `AGENTIC_AI_URL=http://ai-service:3004`

### PROJECT_MANAGER_URL
- **Type**: String (URL)
- **Default**: `http://localhost:3005`
- **Description**: Project manager service URL
- **Example**: `PROJECT_MANAGER_URL=http://project-service:3005`

**Docker Compose Example**:
```bash
# Use service names instead of localhost
AUTH_SERVICE_URL=http://auth-service:3001
CODE_REVIEW_ENGINE_URL=http://ai-service:3002
```

---

## Security Configuration

### JWT_SECRET
- **Type**: String
- **Required**: Yes
- **Description**: Secret key for JWT token verification
- **Security**: NEVER commit to version control
- **Generate**: `openssl rand -base64 32`
- **Example**: `JWT_SECRET=your-super-secret-key-here`

⚠️ **CRITICAL**: Change this in production!

### JWT_EXPIRES_IN
- **Type**: String (time)
- **Default**: `24h`
- **Format**: `<number><unit>` where unit is s, m, h, or d
- **Description**: JWT token expiration time
- **Examples**:
  - `JWT_EXPIRES_IN=30m` (30 minutes)
  - `JWT_EXPIRES_IN=1h` (1 hour)
  - `JWT_EXPIRES_IN=7d` (7 days)

### CORS_ALLOWED_ORIGINS
- **Type**: String (comma-separated URLs)
- **Default**: `http://localhost:3000`
- **Description**: Allowed origins for CORS
- **Example**: `CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com`

**Production**: List only trusted domains
**Development**: Can include localhost

### GITHUB_WEBHOOK_SECRET
- **Type**: String
- **Optional**: Yes
- **Description**: Secret for verifying GitHub webhook signatures
- **Example**: `GITHUB_WEBHOOK_SECRET=your-webhook-secret`

---

## Rate Limiting

Rate limiting protects services from abuse using Redis.

### REDIS_URL
- **Type**: String (URL)
- **Required**: Yes (for rate limiting)
- **Default**: `redis://localhost:6379`
- **Format**: `redis://[username:password@]host:port[/database]`
- **Examples**:
  - Local: `redis://localhost:6379`
  - With auth: `redis://:password@localhost:6379`
  - Remote: `redis://user:pass@redis.example.com:6379/0`

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

**Example Configuration**:
```bash
# Allow 500 requests per hour
RATE_LIMIT_WINDOW_MS=3600000
RATE_LIMIT_MAX=500
```

---

## Circuit Breaker

Circuit breaker prevents cascade failures.

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

**Example Configuration**:
```bash
# Aggressive circuit breaker
CIRCUIT_BREAKER_TIMEOUT=5000
CIRCUIT_BREAKER_ERROR_THRESHOLD=30
CIRCUIT_BREAKER_RESET_TIMEOUT=30000
CIRCUIT_BREAKER_VOLUME_THRESHOLD=5
```

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

**Log Level Hierarchy**:
```
error < warn < info < http < verbose < debug < silly
```

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

**Example Configuration**:
```bash
# Production logging
NODE_ENV=production
LOG_LEVEL=warn
LOG_FORMAT=json
LOG_TO_FILE=true
LOG_DIR=/var/log/api-gateway
```

---

## Performance Tuning

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

## Configuration Examples

### Development

```bash
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug

JWT_SECRET=dev-secret-key
JWT_EXPIRES_IN=24h

REDIS_URL=redis://localhost:6379

AUTH_SERVICE_URL=http://localhost:3001
CODE_REVIEW_ENGINE_URL=http://localhost:3002
ARCHITECTURE_ANALYZER_URL=http://localhost:3003
AGENTIC_AI_URL=http://localhost:3004
PROJECT_MANAGER_URL=http://localhost:3005

CORS_ALLOWED_ORIGINS=http://localhost:3000

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100
```

### Production

```bash
NODE_ENV=production
PORT=3000
LOG_LEVEL=warn

JWT_SECRET=<strong-random-secret>
JWT_EXPIRES_IN=1h

REDIS_URL=redis://:password@redis.prod.example.com:6379

AUTH_SERVICE_URL=https://auth.example.com
CODE_REVIEW_ENGINE_URL=https://review.example.com
ARCHITECTURE_ANALYZER_URL=https://arch.example.com
AGENTIC_AI_URL=https://ai.example.com
PROJECT_MANAGER_URL=https://projects.example.com

CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=500

CIRCUIT_BREAKER_TIMEOUT=10000
CIRCUIT_BREAKER_ERROR_THRESHOLD=50
CIRCUIT_BREAKER_RESET_TIMEOUT=60000

TRUST_PROXY=true
ENABLE_COMPRESSION=true
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
```

---

## Configuration Validation

The gateway validates configuration on startup:

```typescript
// Required variables
- PORT
- NODE_ENV
- JWT_SECRET
- REDIS_URL
- All *_SERVICE_URL variables

// Optional variables have defaults
```

**Startup Errors**:
- Missing required variables → Fatal error
- Invalid values → Warning + default value
- Connection failures → Retry with backoff

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
   - Enable TRUST_PROXY behind load balancer

---

## Troubleshooting Configuration

### Check Current Configuration

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
