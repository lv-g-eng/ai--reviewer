# API Gateway Demo Setup Guide

This guide provides step-by-step instructions for setting up and running the API Gateway demo.

## Prerequisites

### System Requirements
- Node.js 18.x or higher
- Redis 6.x or higher
- PowerShell (for demo scripts)
- Git (for repository access)

### Environment Setup
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd services/api-gateway
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with appropriate values
   ```

## Demo Environment Setup

### 1. Start Redis Server
```bash
# Option 1: Docker (Recommended)
docker run -d --name redis-demo -p 6379:6379 redis:7-alpine

# Option 2: Local Redis
redis-server

# Verify Redis is running
redis-cli ping
# Expected response: PONG
```

### 2. Configure Environment Variables
Create or update `.env` file:
```env
# Server Configuration
PORT=3000
NODE_ENV=development

# JWT Configuration (demo purposes)
JWT_SECRET=demo-secret-key-change-in-production

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Service URLs (mock services for demo)
AUTH_SERVICE_URL=http://localhost:3001
CODE_REVIEW_ENGINE_URL=http://localhost:3002
ARCHITECTURE_ANALYZER_URL=http://localhost:3003
AGENTIC_AI_URL=http://localhost:3004
PROJECT_MANAGER_URL=http://localhost:3005

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=info
```

### 3. Start API Gateway
```bash
# Development mode (with hot reload)
npm run dev

# Production mode
npm run build
npm start

# Verify API Gateway is running
curl http://localhost:3000/health
```

### 4. Optional: Start Mock Backend Services
For full integration testing, you can start mock backend services:

```bash
# Start mock service (simple HTTP server)
node mock-service.js
```

## Demo Execution

### Pre-Demo Checklist
- [ ] Redis server running and accessible
- [ ] API Gateway running on port 3000
- [ ] Environment variables configured
- [ ] Demo scripts executable
- [ ] Log files accessible for monitoring
- [ ] Network connectivity verified

### Running the Demo

#### Option 1: Automated Demo Script
```bash
# Run comprehensive demo
./demo-script.ps1

# Expected output: Complete feature demonstration
```

#### Option 2: Manual Demo Steps
```bash
# 1. Health Check
curl http://localhost:3000/health

# 2. Test Authentication
curl -H "Authorization: Bearer demo-token" \
     http://localhost:3000/api/v1/projects

# 3. Test Rate Limiting
for i in {1..20}; do
  curl http://localhost:3000/api/v1/projects &
done

# 4. Test Validation
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer demo-token" \
     -d '{"name":"Demo Project","description":"Test"}' \
     http://localhost:3000/api/v1/projects
```

#### Option 3: Test Demo Flow
```bash
# Validate demo flow before presentation
./test-demo-flow.ps1

# Expected: All tests should pass
```

### Monitoring During Demo

#### Real-time Logs
```bash
# Monitor all logs
tail -f logs/combined.log

# Monitor error logs only
tail -f logs/error.log

# Filter by correlation ID
tail -f logs/combined.log | grep "correlation-id-here"
```

#### Health Monitoring
```bash
# Check system health
curl http://localhost:3000/health

# Monitor Redis connection
redis-cli ping

# Check process status
ps aux | grep node
```

## Demo Scenarios

### Scenario 1: Basic Functionality
1. Health check verification
2. Authentication testing
3. Basic API endpoint access
4. Response format validation

### Scenario 2: Security Features
1. Unauthenticated access (should fail)
2. Invalid JWT token (should fail)
3. Role-based access control
4. CORS policy enforcement

### Scenario 3: Resilience Features
1. Rate limiting demonstration
2. Circuit breaker testing
3. Error handling showcase
4. Recovery mechanisms

### Scenario 4: Observability
1. Correlation ID tracking
2. Structured logging
3. Performance metrics
4. Health monitoring

## Troubleshooting

### Common Issues

#### API Gateway Won't Start
**Symptoms**: Server fails to start, port binding errors
**Solutions**:
```bash
# Check if port 3000 is in use
lsof -i :3000
netstat -tulpn | grep :3000

# Kill process using port 3000
kill -9 $(lsof -t -i:3000)

# Use different port
PORT=3001 npm start
```

#### Redis Connection Issues
**Symptoms**: Rate limiting not working, Redis connection errors
**Solutions**:
```bash
# Verify Redis is running
redis-cli ping

# Check Redis logs
docker logs redis-demo

# Test Redis connection
redis-cli -u $REDIS_URL ping

# Restart Redis
docker restart redis-demo
```

#### Authentication Failures
**Symptoms**: All requests return 401 Unauthorized
**Solutions**:
```bash
# Check JWT secret configuration
echo $JWT_SECRET

# Verify token format
# Use online JWT decoder to validate token structure

# Check authentication middleware
tail -f logs/combined.log | grep -i auth
```

#### Rate Limiting Not Working
**Symptoms**: No rate limiting enforcement
**Solutions**:
```bash
# Verify Redis connection
redis-cli ping

# Check rate limit configuration
echo $RATE_LIMIT_MAX
echo $RATE_LIMIT_WINDOW_MS

# Monitor Redis keys
redis-cli keys "rl:*"
```

#### Circuit Breaker Issues
**Symptoms**: Circuit breaker not opening/closing
**Solutions**:
```bash
# Check backend service connectivity
curl http://localhost:3001/health

# Monitor circuit breaker logs
tail -f logs/combined.log | grep -i circuit

# Verify circuit breaker configuration
```

### Performance Issues

#### Slow Response Times
**Symptoms**: Response times >100ms
**Solutions**:
```bash
# Monitor system resources
top
htop

# Check memory usage
free -h

# Profile application
node --inspect dist/index.js
```

#### High Memory Usage
**Symptoms**: Memory usage >512MB
**Solutions**:
```bash
# Monitor memory usage
ps aux | grep node

# Check for memory leaks
npm run test:performance:memory

# Restart application
npm restart
```

## Demo Best Practices

### Preparation
1. **Test Everything**: Run complete demo flow before presentation
2. **Backup Plans**: Have fallback scenarios for technical issues
3. **Time Management**: Practice timing for each demo section
4. **Audience Engagement**: Prepare for questions and interactions

### During Demo
1. **Start Simple**: Begin with basic functionality
2. **Show Failures**: Demonstrate error handling and resilience
3. **Explain Context**: Provide background for each feature
4. **Monitor Logs**: Show real-time logging during operations

### After Demo
1. **Gather Feedback**: Collect questions and suggestions
2. **Document Issues**: Note any problems encountered
3. **Follow Up**: Provide additional information if requested
4. **Plan Next Steps**: Discuss deployment and next phases

## Demo Data

### Test Users
- **Regular User**: `demo@example.com` (user role)
- **Admin User**: `admin@example.com` (admin role)
- **Developer**: `developer@example.com` (developer role)

### Sample Projects
- **E-Commerce Platform**: TypeScript/NestJS project
- **Mobile Banking App**: React Native/Expo project
- **AI Analytics Dashboard**: Python/FastAPI project

### Test Scenarios
- Valid and invalid request payloads
- Authentication and authorization scenarios
- Rate limiting and circuit breaker triggers
- Error handling demonstrations

## Success Criteria

### Functional Validation
- [ ] All API endpoints accessible
- [ ] Authentication working correctly
- [ ] Request validation catching errors
- [ ] Rate limiting enforcing limits
- [ ] Circuit breaker protecting services
- [ ] Error handling providing consistent responses

### Performance Validation
- [ ] Response times <50ms for routing
- [ ] Memory usage <512MB
- [ ] Support for concurrent requests
- [ ] Proper resource cleanup

### Quality Validation
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Configuration validated
- [ ] Security measures active

## Contact and Support

### Demo Support
- **Technical Issues**: Check troubleshooting section
- **Questions**: Refer to documentation
- **Escalation**: Contact development team

### Resources
- [README.md](./README.md) - Complete project documentation
- [API Documentation](./docs/API_DOCUMENTATION.md) - Endpoint reference
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md) - Detailed issue resolution

---

**Setup Status**: Ready for Demo
**Last Updated**: January 24, 2026
**Version**: 1.0.0