# API Gateway - Troubleshooting Guide

> Quick reference for diagnosing and fixing common issues with the API Gateway

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Startup Issues](#startup-issues)
3. [Authentication Problems](#authentication-problems)
4. [Rate Limiting Issues](#rate-limiting-issues)
5. [Circuit Breaker Problems](#circuit-breaker-problems)
6. [Performance Issues](#performance-issues)
7. [Logging Issues](#logging-issues)
8. [Service Communication](#service-communication)
9. [Debugging Tips](#debugging-tips)
10. [Emergency Procedures](#emergency-procedures)

---

## Quick Diagnostics

### Health Check Commands

```bash
# Check gateway health
curl http://localhost:3000/health

# Check all services
curl http://localhost:3000/health | jq '.services'

# Check Redis connection
redis-cli -u $REDIS_URL ping

# Check logs for errors
tail -f logs/error.log | head -20
```

### Common Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Validation error, malformed JSON |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Invalid endpoint or resource |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Application error |
| 503 | Service Unavailable | Circuit breaker open, service down |

---

## Startup Issues

### Gateway Won't Start

**Symptom**: Server fails to start or crashes immediately

**Possible Causes**:
1. Port already in use
2. Missing environment variables
3. Redis not accessible
4. Invalid configuration

**Diagnostic Steps**:
```bash
# 1. Check if port is in use
lsof -i :3000
# Windows: netstat -ano | findstr :3000

# 2. Verify environment variables
cat .env
node -e "require('dotenv').config(); console.log(process.env)"

# 3. Test Redis connection
redis-cli ping
# Or: redis-cli -u $REDIS_URL ping

# 4. Check logs
tail -f logs/error.log

# 5. Validate configuration
npm run build
```

**Solutions**:
```bash
# Kill process using port 3000
kill -9 $(lsof -t -i:3000)
# Windows: taskkill /PID <PID> /F

# Create .env from example
cp .env.example .env
# Edit .env with correct values

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Verify configuration
npm run build
```

### Missing Dependencies

**Symptom**: Module not found errors

**Solution**:
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Rebuild TypeScript
npm run build
```

### Configuration Errors

**Symptom**: "Configuration validation failed" on startup

**Common Issues**:
- Missing required environment variables
- Invalid URLs
- Invalid JWT secret format

**Solution**:
```bash
# Check required variables
echo "Required variables:"
echo "PORT: $PORT"
echo "JWT_SECRET: ${JWT_SECRET:0:10}..."
echo "REDIS_URL: $REDIS_URL"
echo "AUTH_SERVICE_URL: $AUTH_SERVICE_URL"

# Validate URLs
curl -I $AUTH_SERVICE_URL/health
curl -I $CODE_REVIEW_ENGINE_URL/health
```

---

## Authentication Problems

### All Requests Return 401 Unauthorized

**Symptom**: Every authenticated request fails with 401

**Possible Causes**:
1. Invalid JWT secret
2. Expired tokens
3. Missing Authorization header
4. Token format incorrect

**Diagnostic Steps**:
```bash
# 1. Verify JWT secret is set
echo $JWT_SECRET

# 2. Decode token to check expiration
# Visit https://jwt.io and paste your token

# 3. Test with curl
curl -v -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/v1/projects

# 4. Check auth middleware logs
tail -f logs/combined.log | grep -i auth
```

**Solutions**:
```bash
# Set JWT secret
export JWT_SECRET="your-secret-key"

# Get a fresh token from auth service
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Verify token format (should be: Bearer <token>)
# Correct: Authorization: Bearer eyJhbGc...
# Wrong: Authorization: eyJhbGc...
```

### Token Expired Errors

**Symptom**: `TOKEN_EXPIRED` error

**Solution**:
```bash
# Increase token expiration time
JWT_EXPIRES_IN=7d  # 7 days

# Or get a new token
# Login again to get fresh token
```

### Forbidden (403) Errors

**Symptom**: Authenticated but getting 403 Forbidden

**Cause**: Insufficient permissions for the requested resource

**Solution**:
```bash
# Check user roles in token
# Decode token at https://jwt.io

# Admin endpoints require admin role
# Verify user has correct role in auth service
```

---

## Rate Limiting Issues

### Rate Limiting Not Working

**Symptom**: Requests not being rate limited

**Possible Causes**:
1. Redis not connected
2. Incorrect Redis URL
3. Rate limiter disabled

**Diagnostic Steps**:
```bash
# 1. Check Redis connection
redis-cli -u $REDIS_URL ping
# Expected: PONG

# 2. Check Redis keys
redis-cli -u $REDIS_URL keys "rl:*"

# 3. Check rate limit logs
tail -f logs/combined.log | grep -i "rate limit"

# 4. Test rate limiting
for i in {1..110}; do
  curl http://localhost:3000/api/v1/projects
done
# Should get 429 after 100 requests
```

**Solutions**:
```bash
# Fix Redis connection
REDIS_URL=redis://localhost:6379

# Restart Redis
docker restart redis

# Verify rate limit configuration
echo $RATE_LIMIT_MAX
echo $RATE_LIMIT_WINDOW_MS
```

### Too Aggressive Rate Limiting

**Symptom**: Legitimate users getting rate limited

**Solution**:
```bash
# Increase rate limits
RATE_LIMIT_MAX=500
RATE_LIMIT_WINDOW_MS=900000  # 15 minutes

# Or implement per-user rate limiting
# (requires code changes)
```

### Rate Limit Not Resetting

**Symptom**: Rate limit persists after window expires

**Solution**:
```bash
# Clear Redis rate limit keys
redis-cli -u $REDIS_URL --scan --pattern "rl:*" | xargs redis-cli -u $REDIS_URL DEL

# Or restart Redis
docker restart redis
```

---

## Circuit Breaker Problems

### Circuit Breaker Always Open

**Symptom**: All requests fail with "Service Unavailable"

**Possible Causes**:
1. Backend service is down
2. Too many errors triggered circuit breaker
3. Circuit breaker timeout too low

**Diagnostic Steps**:
```bash
# 1. Check backend service health
curl http://localhost:3001/health
curl http://localhost:3002/health
# ... check all services

# 2. Check circuit breaker logs
tail -f logs/combined.log | grep -i circuit

# 3. Check circuit breaker state
# Look for "Circuit breaker opened" messages
```

**Solutions**:
```bash
# 1. Start backend services
docker-compose up -d

# 2. Wait for circuit breaker to reset (default: 60 seconds)
# Or restart gateway to reset immediately
npm run dev

# 3. Adjust circuit breaker settings
CIRCUIT_BREAKER_TIMEOUT=15000
CIRCUIT_BREAKER_ERROR_THRESHOLD=60
CIRCUIT_BREAKER_RESET_TIMEOUT=30000
```

### Circuit Breaker Not Opening

**Symptom**: Gateway keeps trying failed service

**Solution**:
```bash
# Lower error threshold
CIRCUIT_BREAKER_ERROR_THRESHOLD=30

# Reduce volume threshold
CIRCUIT_BREAKER_VOLUME_THRESHOLD=5
```

---

## Performance Issues

### High Response Times

**Symptom**: Slow API responses (>1 second)

**Diagnostic Steps**:
```bash
# 1. Run performance tests
npm run test:performance

# 2. Check response time logs
tail -f logs/combined.log | grep -i "response time"

# 3. Profile with autocannon
npx autocannon -c 10 -d 30 http://localhost:3000/api/v1/projects

# 4. Check backend service performance
curl -w "@curl-format.txt" http://localhost:3001/api/projects
```

**Solutions**:
```bash
# 1. Increase backend service resources
# 2. Enable response caching (if applicable)
# 3. Optimize database queries in backend services
# 4. Add load balancing for backend services

# Check for memory leaks
npm run test:performance:memory
```

### High Memory Usage

**Symptom**: Gateway consuming excessive memory (>512MB)

**Diagnostic Steps**:
```bash
# 1. Check memory usage
ps aux | grep node

# 2. Run memory profiling
npm run test:performance:memory

# 3. Check for memory leaks
node --inspect dist/index.js
# Open chrome://inspect in Chrome
```

**Solutions**:
```bash
# 1. Restart gateway periodically
# 2. Limit request body size (already set to 10mb)
# 3. Check for memory leaks in custom code
# 4. Increase container memory limits if needed
```

### High CPU Usage

**Symptom**: CPU usage consistently >80%

**Solutions**:
```bash
# 1. Scale horizontally (multiple instances)
# 2. Optimize validation schemas
# 3. Check for infinite loops in middleware
# 4. Profile with Node.js profiler
```

---

## Logging Issues

### No Logs Appearing

**Symptom**: Logs not being written

**Diagnostic Steps**:
```bash
# 1. Check log level
echo $LOG_LEVEL

# 2. Check log directory
ls -la logs/

# 3. Check file permissions
ls -la logs/combined.log

# 4. Check Winston configuration
cat src/utils/logger.ts
```

**Solutions**:
```bash
# Set appropriate log level
LOG_LEVEL=debug

# Create logs directory
mkdir -p logs

# Fix permissions
chmod 755 logs
chmod 644 logs/*.log

# Enable file logging
LOG_TO_FILE=true
```

### Logs Too Verbose

**Symptom**: Too many log messages

**Solution**:
```bash
# Reduce log level
LOG_LEVEL=warn  # or error

# In production, use warn or error only
NODE_ENV=production
LOG_LEVEL=warn
```

### Missing Correlation IDs

**Symptom**: Logs don't have correlation IDs

**Solution**:
```bash
# Verify correlation ID middleware is first
# Check src/index.ts - correlationIdMiddleware should be early

# Check logs for X-Correlation-ID header
curl -v http://localhost:3000/api/v1/projects
```

---

## Service Communication

### Cannot Reach Backend Services

**Symptom**: "Service Unavailable" errors

**Diagnostic Steps**:
```bash
# 1. Check service URLs
echo $AUTH_SERVICE_URL
echo $CODE_REVIEW_ENGINE_URL
# ... check all service URLs

# 2. Test connectivity
curl http://localhost:3001/health
curl http://localhost:3002/health

# 3. Check Docker network (if using Docker)
docker network inspect bridge

# 4. Check firewall rules
# Ensure ports 3001-3005 are accessible
```

**Solutions**:
```bash
# Start backend services
docker-compose up -d

# Update service URLs
AUTH_SERVICE_URL=http://auth-service:3001
# Use service names in Docker network

# Check service logs
docker logs auth-service
docker logs code-review-engine
```

### Proxy Errors

**Symptom**: "Proxy error" in logs

**Solutions**:
```bash
# 1. Verify target service is running
# 2. Check service URL format (include http://)
# 3. Verify network connectivity
# 4. Check for SSL/TLS issues (use http in dev)
```

---

## Debugging Tips

### Enable Debug Mode

```bash
# Set debug log level
LOG_LEVEL=debug
DEBUG_MODE=true

# Restart gateway
npm run dev
```

### View Real-Time Logs

```bash
# All logs
tail -f logs/combined.log

# Errors only
tail -f logs/error.log

# Filter by correlation ID
tail -f logs/combined.log | grep "550e8400-e29b-41d4-a716-446655440000"

# Filter by endpoint
tail -f logs/combined.log | grep "/api/v1/projects"
```

### Test Specific Endpoints

```bash
# Health check
curl http://localhost:3000/health

# With authentication
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:3000/api/v1/projects

# With verbose output
curl -v -H "Authorization: Bearer TOKEN" \
  http://localhost:3000/api/v1/projects

# POST request
curl -X POST http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","repositoryUrl":"https://github.com/test/repo"}'
```

### Check Service Health

```bash
# Create health check script
cat > check-health.sh << 'EOF'
#!/bin/bash
services=(
  "http://localhost:3000/health"
  "http://localhost:3001/health"
  "http://localhost:3002/health"
  "http://localhost:3003/health"
  "http://localhost:3004/health"
  "http://localhost:3005/health"
)

for service in "${services[@]}"; do
  echo "Checking $service"
  curl -s $service | jq .
done
EOF

chmod +x check-health.sh
./check-health.sh
```

### Monitor Redis

```bash
# Monitor Redis commands
redis-cli monitor

# Check Redis info
redis-cli info

# Check memory usage
redis-cli info memory

# List all keys
redis-cli keys "*"
```

### Use Node.js Inspector

```bash
# Start with inspector
node --inspect dist/index.js

# Or in development
node --inspect -r ts-node/register src/index.ts

# Open chrome://inspect in Chrome
# Click "inspect" under your process
```

---

## Common Error Messages

### "EADDRINUSE: address already in use"
**Solution**: Port 3000 is in use. Kill the process or change PORT.

### "Redis connection refused"
**Solution**: Start Redis or check REDIS_URL.

### "JWT secret not configured"
**Solution**: Set JWT_SECRET in .env.

### "Service Unavailable"
**Solution**: Backend service is down or circuit breaker is open.

### "Validation Error"
**Solution**: Check request body/params against schema.

### "Rate Limit Exceeded"
**Solution**: Wait for rate limit window to reset or increase limits.

---

## Getting Help

If you're still experiencing issues:

1. **Check Logs**: `logs/error.log` and `logs/combined.log`
2. **Run Tests**: `npm test` to verify functionality
3. **Check Configuration**: Verify all environment variables
4. **Review Documentation**: [README.md](../README.md)
5. **GitHub Issues**: Report bugs with logs and steps to reproduce
6. **Team Support**: Contact #api-gateway on Slack

---

## Emergency Procedures

### Production Outage Response

**Step 1: Immediate Assessment**
```bash
# Check gateway health
curl https://api.example.com/health

# Check all instances
kubectl get pods -n api-gateway
# Or: docker ps | grep api-gateway

# Check load balancer
curl -I https://api.example.com
```

**Step 2: Quick Fixes**
```bash
# Restart gateway instances
kubectl rollout restart deployment/api-gateway -n api-gateway
# Or: docker-compose restart api-gateway

# Clear Redis cache if needed
redis-cli -u $REDIS_URL FLUSHALL

# Check circuit breaker status
tail -f logs/combined.log | grep -i circuit
```

**Step 3: Escalation**
- Contact on-call engineer
- Update status page
- Notify stakeholders

### Circuit Breaker Emergency Reset

```bash
# Force close all circuit breakers (emergency only)
curl -X POST http://localhost:3000/admin/circuit-breaker/reset \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Or restart gateway to reset circuit breakers
kubectl rollout restart deployment/api-gateway
```

### Rate Limit Emergency Bypass

```bash
# Temporarily increase rate limits (emergency only)
redis-cli -u $REDIS_URL DEL "rl:*"

# Or set emergency rate limits
export RATE_LIMIT_MAX=1000
export RATE_LIMIT_WINDOW_MS=60000
```

### Memory Leak Emergency

```bash
# Check memory usage
kubectl top pods -n api-gateway
# Or: docker stats api-gateway

# Restart high-memory instances
kubectl delete pod <pod-name> -n api-gateway

# Scale up temporarily
kubectl scale deployment api-gateway --replicas=6 -n api-gateway
```

---

## Getting Help

### Internal Support

1. **Check Logs**: `logs/error.log` and `logs/combined.log`
2. **Run Tests**: `npm test` to verify functionality
3. **Check Configuration**: Verify all environment variables
4. **Review Documentation**: [README.md](../README.md)

### External Support

1. **GitHub Issues**: Report bugs with logs and steps to reproduce
2. **Team Support**: Contact #api-gateway on Slack
3. **On-Call**: Page on-call engineer for production issues
4. **Vendor Support**: Contact Redis/AWS support for infrastructure issues

### Information to Provide

When reporting issues, include:
- **Correlation ID** from error response
- **Timestamp** of the issue
- **Request details** (method, path, headers)
- **Error logs** with stack trace
- **Environment** (dev/staging/prod)
- **Steps to reproduce**

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0
