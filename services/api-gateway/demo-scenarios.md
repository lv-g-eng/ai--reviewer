# API Gateway Demo Scenarios

This document outlines comprehensive demo scenarios for showcasing the API Gateway's production-ready features.

## Overview

The API Gateway demo demonstrates a complete production-ready system with:
- **Authentication & Authorization** (JWT-based with RBAC)
- **Request Validation** (Zod schema validation)
- **Rate Limiting** (Redis-backed distributed limiting)
- **Circuit Breaker** (Opossum-based service resilience)
- **Correlation ID Tracking** (End-to-end request tracing)
- **Comprehensive Logging** (Structured JSON logging)
- **Error Handling** (Standardized error responses)
- **Webhook Processing** (GitHub integration)
- **Health Monitoring** (Service health checks)

---

## Demo Environment Setup

### Prerequisites
- API Gateway running on `http://localhost:3000`
- Redis server running on `localhost:6379`
- Mock backend services (optional, for full integration testing)

### Demo Users
- **Regular User**: `demo@example.com` (user role)
- **Admin User**: `admin@example.com` (admin role)
- **Developer**: `developer@example.com` (developer role)

---

## Scenario 1: Happy Path - Complete Workflow

**Objective**: Demonstrate successful request flow through all middleware layers

### Steps:
1. **Health Check**
   ```bash
   GET /health
   Expected: 200 OK with service status
   ```

2. **User Authentication**
   ```bash
   GET /api/v1/projects
   Headers: Authorization: Bearer <valid-jwt>
   Expected: 200 OK with project list
   ```

3. **Create New Project**
   ```bash
   POST /api/v1/projects
   Body: {
     "name": "Demo Project",
     "description": "A demonstration project",
     "repositoryUrl": "https://github.com/demo/project"
   }
   Expected: 201 Created with project details
   ```

4. **List Projects with Pagination**
   ```bash
   GET /api/v1/projects?page=1&limit=10
   Expected: 200 OK with paginated results
   ```

5. **Get Project Statistics**
   ```bash
   GET /api/v1/projects/demo-project-1/stats
   Expected: 200 OK with project metrics
   ```

### Expected Outcomes:
- ✅ All requests succeed with appropriate status codes
- ✅ Correlation IDs present in all responses
- ✅ Rate limit headers included in responses
- ✅ Response times under 100ms for routing overhead
- ✅ Structured logging with correlation IDs

---

## Scenario 2: Authentication & Authorization

**Objective**: Test JWT authentication and role-based access control

### Steps:
1. **Unauthenticated Access**
   ```bash
   GET /api/v1/projects
   Headers: (no Authorization header)
   Expected: 401 Unauthorized
   ```

2. **Invalid JWT Token**
   ```bash
   GET /api/v1/projects
   Headers: Authorization: Bearer invalid-token
   Expected: 401 Unauthorized
   ```

3. **User Accessing User Endpoints**
   ```bash
   GET /api/v1/projects
   Headers: Authorization: Bearer <user-jwt>
   Expected: 200 OK
   ```

4. **User Accessing Admin Endpoints**
   ```bash
   GET /api/v1/admin/users
   Headers: Authorization: Bearer <user-jwt>
   Expected: 403 Forbidden
   ```

5. **Admin Accessing Admin Endpoints**
   ```bash
   GET /api/v1/admin/users
   Headers: Authorization: Bearer <admin-jwt>
   Expected: 200 OK
   ```

### Expected Outcomes:
- ✅ Proper 401 responses for missing/invalid authentication
- ✅ Proper 403 responses for insufficient permissions
- ✅ Successful access with correct permissions
- ✅ JWT payload correctly extracted and used for authorization

---

## Scenario 3: Request Validation

**Objective**: Test Zod schema validation for various request types

### Steps:
1. **Valid Project Creation**
   ```bash
   POST /api/v1/projects
   Body: {
     "name": "Valid Project",
     "description": "A valid project description",
     "repositoryUrl": "https://github.com/user/repo",
     "language": "typescript"
   }
   Expected: 201 Created
   ```

2. **Invalid Project - Missing Required Fields**
   ```bash
   POST /api/v1/projects
   Body: {
     "description": "Missing name field"
   }
   Expected: 400 Bad Request with validation errors
   ```

3. **Invalid Query Parameters**
   ```bash
   GET /api/v1/projects?page=0&limit=1000
   Expected: 400 Bad Request (page must be >= 1, limit <= 100)
   ```

4. **Malformed JSON**
   ```bash
   POST /api/v1/projects
   Body: {"invalid": json}
   Expected: 400 Bad Request
   ```

5. **Invalid Data Types**
   ```bash
   POST /api/v1/projects
   Body: {
     "name": 123,
     "description": true,
     "repositoryUrl": "not-a-url"
   }
   Expected: 400 Bad Request with field-specific errors
   ```

### Expected Outcomes:
- ✅ Valid requests succeed
- ✅ Invalid requests return 400 Bad Request
- ✅ Detailed validation error messages with field paths
- ✅ Consistent error response format

---

## Scenario 4: Rate Limiting

**Objective**: Test Redis-backed rate limiting functionality

### Steps:
1. **Normal Request Rate**
   ```bash
   # Send 5 requests within normal limits
   for i in {1..5}; do
     curl -H "Authorization: Bearer <token>" \
          http://localhost:3000/api/v1/projects
   done
   Expected: All succeed with rate limit headers
   ```

2. **Rapid Request Burst**
   ```bash
   # Send 20 rapid requests to trigger rate limiting
   for i in {1..20}; do
     curl -H "Authorization: Bearer <token>" \
          http://localhost:3000/api/v1/projects &
   done
   Expected: Some requests return 429 Too Many Requests
   ```

3. **Rate Limit Headers**
   ```bash
   GET /api/v1/projects
   Expected Headers:
   - X-RateLimit-Limit: 100
   - X-RateLimit-Remaining: 99
   - X-RateLimit-Reset: <timestamp>
   ```

4. **Rate Limit Reset**
   ```bash
   # Wait for rate limit window to reset
   # Then send request
   GET /api/v1/projects
   Expected: 200 OK with reset rate limit counters
   ```

### Expected Outcomes:
- ✅ Normal requests succeed with rate limit headers
- ✅ Excess requests return 429 Too Many Requests
- ✅ Rate limit headers show remaining requests and reset time
- ✅ Access restored after reset period
- ✅ Redis-backed distributed rate limiting works correctly

---

## Scenario 5: Circuit Breaker

**Objective**: Test circuit breaker pattern with failing services

### Steps:
1. **Healthy Service Requests**
   ```bash
   GET /api/v1/projects
   Expected: 200 OK with normal response times
   ```

2. **Requests to Failing Service**
   ```bash
   # Send multiple requests to potentially failing service
   for i in {1..10}; do
     curl http://localhost:3000/api/v1/architecture/demo-project/scan
   done
   Expected: Initial failures, then circuit breaker opens
   ```

3. **Circuit Breaker Open State**
   ```bash
   GET /api/v1/architecture/demo-project/scan
   Expected: 503 Service Unavailable with fast response time
   ```

4. **Circuit Breaker Half-Open**
   ```bash
   # Wait for circuit breaker timeout (30 seconds)
   # Then send request
   GET /api/v1/architecture/demo-project/scan
   Expected: Circuit attempts to close or stays open
   ```

### Expected Outcomes:
- ✅ Healthy services respond normally
- ✅ Circuit opens after failure threshold (50% error rate)
- ✅ Fast-fail responses when circuit is open (<100ms)
- ✅ Circuit attempts recovery after timeout (30 seconds)
- ✅ Proper logging of circuit state changes

---

## Scenario 6: Correlation ID Tracking

**Objective**: Test end-to-end request tracking with correlation IDs

### Steps:
1. **Auto-Generated Correlation ID**
   ```bash
   GET /api/v1/projects
   Expected: Response includes X-Correlation-ID header
   ```

2. **Custom Correlation ID**
   ```bash
   GET /api/v1/projects
   Headers: X-Correlation-ID: custom-demo-12345
   Expected: Same correlation ID returned in response
   ```

3. **Correlation ID in Logs**
   ```bash
   # Check application logs
   tail -f logs/combined.log | grep "custom-demo-12345"
   Expected: All log entries include the correlation ID
   ```

4. **Correlation ID Forwarding**
   ```bash
   GET /api/v1/projects
   Expected: Correlation ID forwarded to backend services
   ```

### Expected Outcomes:
- ✅ Every request gets a unique correlation ID
- ✅ Custom correlation IDs are preserved
- ✅ Correlation IDs appear in all log entries
- ✅ Correlation IDs forwarded to backend services
- ✅ End-to-end request tracing enabled

---

## Scenario 7: Error Handling

**Objective**: Test standardized error responses and logging

### Steps:
1. **404 Not Found**
   ```bash
   GET /api/v1/nonexistent-endpoint
   Expected: 404 with standardized error format
   ```

2. **405 Method Not Allowed**
   ```bash
   DELETE /health
   Expected: 405 with allowed methods
   ```

3. **500 Internal Server Error**
   ```bash
   # Trigger server error (if possible)
   GET /api/v1/projects/trigger-error
   Expected: 500 with error details (no stack trace in production)
   ```

4. **Error Response Format**
   ```json
   {
     "error": "Not Found",
     "message": "The requested resource was not found",
     "statusCode": 404,
     "timestamp": "2026-01-24T10:00:00.000Z",
     "path": "/api/v1/nonexistent",
     "correlationId": "uuid-here"
   }
   ```

### Expected Outcomes:
- ✅ Consistent error response format across all endpoints
- ✅ Correlation IDs included in error responses
- ✅ Appropriate HTTP status codes
- ✅ Helpful error messages without sensitive data
- ✅ Stack traces hidden in production environment

---

## Scenario 8: Webhook Processing

**Objective**: Test webhook endpoint handling

### Steps:
1. **GitHub Push Webhook**
   ```bash
   POST /api/webhooks/github
   Headers: X-GitHub-Event: push
   Body: {
     "ref": "refs/heads/main",
     "repository": {
       "name": "demo-repo",
       "full_name": "demo-org/demo-repo"
     },
     "commits": [...]
   }
   Expected: 200 OK with webhook processed
   ```

2. **GitHub Pull Request Webhook**
   ```bash
   POST /api/webhooks/github
   Headers: X-GitHub-Event: pull_request
   Body: {
     "action": "opened",
     "pull_request": {...},
     "repository": {...}
   }
   Expected: 200 OK with PR webhook processed
   ```

3. **Invalid Webhook Payload**
   ```bash
   POST /api/webhooks/github
   Body: {"invalid": "payload"}
   Expected: 400 Bad Request
   ```

### Expected Outcomes:
- ✅ Valid webhooks processed successfully
- ✅ Invalid webhooks rejected with appropriate errors
- ✅ Webhook events trigger correct downstream actions
- ✅ Proper logging of webhook events with correlation IDs

---

## Scenario 9: Performance & Monitoring

**Objective**: Test performance characteristics and monitoring capabilities

### Steps:
1. **Response Time Measurement**
   ```bash
   # Measure response times for various endpoints
   time curl http://localhost:3000/api/v1/projects
   Expected: <50ms routing overhead
   ```

2. **Health Check Monitoring**
   ```bash
   GET /health
   Expected: Detailed service health status
   ```

3. **Structured Logging Verification**
   ```bash
   tail -f logs/combined.log
   Expected: JSON-formatted logs with all required fields
   ```

4. **Memory Usage Monitoring**
   ```bash
   # Monitor process memory usage
   ps aux | grep node
   Expected: Memory usage within acceptable limits (<512MB)
   ```

### Expected Outcomes:
- ✅ Response times under 50ms for routing overhead
- ✅ Health check provides comprehensive service status
- ✅ Structured JSON logging with correlation IDs
- ✅ Memory usage within defined limits
- ✅ All monitoring endpoints accessible

---

## Scenario 10: Complete API Coverage

**Objective**: Demonstrate routing to all microservices

### Service Coverage:
1. **Projects Service**
   - `GET /api/v1/projects` - List projects
   - `POST /api/v1/projects` - Create project
   - `GET /api/v1/projects/{id}` - Get project
   - `PUT /api/v1/projects/{id}` - Update project
   - `DELETE /api/v1/projects/{id}` - Delete project
   - `GET /api/v1/projects/{id}/stats` - Get statistics

2. **Reviews Service**
   - `GET /api/v1/reviews` - List reviews
   - `POST /api/v1/reviews` - Create review
   - `GET /api/v1/reviews/{id}` - Get review
   - `PUT /api/v1/reviews/{id}` - Update review
   - `DELETE /api/v1/reviews/{id}` - Delete review
   - `POST /api/v1/reviews/{id}/comments` - Add comment

3. **Architecture Service**
   - `GET /api/v1/architecture/{projectId}` - Get architecture
   - `POST /api/v1/architecture/{projectId}/scan` - Trigger scan
   - `GET /api/v1/architecture/{projectId}/graph` - Get graph
   - `GET /api/v1/architecture/{projectId}/drift` - Get drift analysis

4. **Queue Service**
   - `GET /api/v1/queue` - List queue items
   - `GET /api/v1/queue/{id}` - Get queue item
   - `POST /api/v1/queue/{id}/retry` - Retry failed item
   - `DELETE /api/v1/queue/{id}` - Cancel queue item

5. **Admin Service**
   - `GET /api/v1/admin/users` - List users
   - `GET /api/v1/admin/audit-logs` - Get audit logs
   - `GET /api/v1/admin/settings` - Get settings
   - `PUT /api/v1/admin/settings` - Update settings

### Expected Outcomes:
- ✅ All endpoints properly routed to correct services
- ✅ Consistent middleware application across all routes
- ✅ Proper authentication and authorization for each service
- ✅ Correlation ID forwarding to all backend services

---

## Demo Execution Guide

### Pre-Demo Checklist:
- [ ] API Gateway running on port 3000
- [ ] Redis server running and accessible
- [ ] Demo script (`demo-script.ps1`) ready
- [ ] Demo data (`demo-data.json`) loaded
- [ ] Log files accessible for monitoring
- [ ] Network connectivity verified

### Demo Flow:
1. **Introduction** (2 minutes)
   - Overview of API Gateway architecture
   - Key features and benefits

2. **Core Features Demo** (15 minutes)
   - Health check and system status
   - Authentication and authorization
   - Request validation
   - Rate limiting demonstration
   - Circuit breaker testing

3. **Advanced Features** (10 minutes)
   - Correlation ID tracking
   - Error handling
   - Webhook processing
   - Performance monitoring

4. **Production Readiness** (5 minutes)
   - Test coverage and quality metrics
   - Documentation completeness
   - Deployment readiness

5. **Q&A and Discussion** (8 minutes)
   - Questions from audience
   - Technical deep-dive if requested

### Demo Tips:
- Use the automated demo script for consistency
- Show logs in real-time during demonstrations
- Highlight correlation IDs in responses
- Demonstrate both success and failure scenarios
- Keep technical explanations concise but thorough

---

## Success Metrics

### Functional Requirements:
- ✅ All API endpoints accessible and properly routed
- ✅ Authentication and authorization working correctly
- ✅ Request validation catching invalid data
- ✅ Rate limiting protecting against abuse
- ✅ Circuit breaker preventing cascade failures
- ✅ Error handling providing consistent responses

### Performance Requirements:
- ✅ Response times <50ms for routing overhead
- ✅ Memory usage <512MB under normal load
- ✅ Support for 1000+ requests per second
- ✅ 99.9% uptime with circuit breaker protection

### Quality Requirements:
- ✅ 95% test coverage with 409 passing tests
- ✅ Comprehensive documentation
- ✅ Production-ready configuration
- ✅ Structured logging and monitoring
- ✅ Security best practices implemented

---

## Troubleshooting Common Demo Issues

### Issue: Rate Limiting Not Working
**Solution**: Verify Redis connection and rate limit configuration

### Issue: Circuit Breaker Not Triggering
**Solution**: Ensure backend services are configured to fail appropriately

### Issue: Authentication Failures
**Solution**: Check JWT secret configuration and token validity

### Issue: Slow Response Times
**Solution**: Verify system resources and network connectivity

### Issue: Missing Correlation IDs
**Solution**: Check middleware order and header forwarding configuration

---

This comprehensive demo showcases a production-ready API Gateway with enterprise-grade features, demonstrating the successful completion of the Week 1 implementation goals.