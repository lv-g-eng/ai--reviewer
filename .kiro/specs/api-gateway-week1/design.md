# API Gateway Week 1 Implementation - Design

**Feature**: Complete API Gateway Implementation  
**Version**: 1.0  
**Last Updated**: January 20, 2026

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Incoming Request                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Security Middleware (Helmet, CORS)           │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Rate Limiting (Redis-backed)                 │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Request Logging (Correlation ID)             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Authentication (JWT Validation)              │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Request Validation (Zod Schemas)             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Circuit Breaker (Opossum)                    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Service Proxy (HTTP Proxy Middleware)        │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Response Transformation                      │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Error Handling                               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Response Logging                             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Outgoing Response                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
services/api-gateway/
├── src/
│   ├── index.ts                    # Main application entry
│   ├── types.d.ts                  # TypeScript type definitions
│   ├── config/
│   │   └── index.ts                # Configuration management
│   ├── middleware/
│   │   ├── auth.ts                 # JWT authentication
│   │   ├── errorHandler.ts         # Global error handling
│   │   ├── rateLimiter.ts          # Rate limiting (NEW)
│   │   ├── circuitBreaker.ts       # Circuit breaker (NEW)
│   │   ├── requestValidator.ts     # Request validation (NEW)
│   │   ├── requestLogger.ts        # Request logging (NEW)
│   │   └── responseLogger.ts       # Response logging (NEW)
│   ├── routes/
│   │   ├── index.ts                # Main router
│   │   ├── health.ts               # Health check
│   │   ├── projects.routes.ts      # Projects routes (NEW)
│   │   ├── reviews.routes.ts       # Reviews routes (NEW)
│   │   ├── architecture.routes.ts  # Architecture routes (NEW)
│   │   ├── queue.routes.ts         # Queue routes (NEW)
│   │   ├── admin.routes.ts         # Admin routes (NEW)
│   │   └── webhooks.ts             # Webhook routes
│   ├── schemas/
│   │   ├── projects.schema.ts      # Project validation schemas (NEW)
│   │   ├── reviews.schema.ts       # Review validation schemas (NEW)
│   │   └── common.schema.ts        # Common validation schemas (NEW)
│   ├── services/
│   │   ├── serviceProxy.ts         # Service proxy logic (NEW)
│   │   └── serviceRegistry.ts      # Service discovery (NEW)
│   └── utils/
│       ├── logger.ts               # Winston logger
│       ├── correlationId.ts        # Correlation ID generator (NEW)
│       └── errorCodes.ts           # Error code definitions (NEW)
├── __tests__/
│   ├── unit/
│   │   ├── middleware/
│   │   ├── routes/
│   │   └── services/
│   ├── integration/
│   │   └── api.test.ts
│   └── property/
│       └── validation.property.test.ts
├── package.json
├── tsconfig.json
├── Dockerfile
└── README.md
```

---

## 🔧 Component Design

### 1. Rate Limiter Middleware

```typescript
// src/middleware/rateLimiter.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export const apiLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:api:',
  }),
  windowMs: 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  message: {
    error: 'Too many requests',
    message: 'Please try again later',
    retryAfter: 60,
  },
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => req.path === '/health',
});

export const authLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:auth:',
  }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: {
    error: 'Too many authentication attempts',
    message: 'Please try again in 15 minutes',
    retryAfter: 900,
  },
  skipSuccessfulRequests: true,
});
```

### 2. Circuit Breaker

```typescript
// src/middleware/circuitBreaker.ts
import CircuitBreaker from 'opossum';
import { logger } from '../utils/logger';

interface CircuitBreakerOptions {
  timeout: number;
  errorThresholdPercentage: number;
  resetTimeout: number;
}

const defaultOptions: CircuitBreakerOptions = {
  timeout: 3000, // 3 seconds
  errorThresholdPercentage: 50,
  resetTimeout: 30000, // 30 seconds
};

export const createCircuitBreaker = (
  serviceCall: Function,
  serviceName: string,
  options: Partial<CircuitBreakerOptions> = {}
) => {
  const breaker = new CircuitBreaker(serviceCall, {
    ...defaultOptions,
    ...options,
  });

  breaker.on('open', () => {
    logger.error(`Circuit breaker opened for ${serviceName}`);
  });

  breaker.on('halfOpen', () => {
    logger.warn(`Circuit breaker half-open for ${serviceName}`);
  });

  breaker.on('close', () => {
    logger.info(`Circuit breaker closed for ${serviceName}`);
  });

  breaker.on('failure', (error) => {
    logger.error(`Circuit breaker failure for ${serviceName}:`, error);
  });

  return breaker;
};
```

### 3. Request Validator

```typescript
// src/middleware/requestValidator.ts
import { Request, Response, NextFunction } from 'express';
import { z, ZodSchema } from 'zod';
import { logger } from '../utils/logger';

export const validateRequest = (schema: ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });

      // Replace request data with validated data
      req.body = validated.body || req.body;
      req.query = validated.query || req.query;
      req.params = validated.params || req.params;

      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        logger.warn('Request validation failed', {
          correlationId: req.headers['x-correlation-id'],
          errors: error.errors,
        });

        return res.status(400).json({
          error: 'Validation failed',
          message: 'Invalid request data',
          details: error.errors.map((err) => ({
            field: err.path.join('.'),
            message: err.message,
          })),
        });
      }

      next(error);
    }
  };
};
```

### 4. Request Logger

```typescript
// src/middleware/requestLogger.ts
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export const requestLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Generate correlation ID
  const correlationId = req.headers['x-correlation-id'] || uuidv4();
  req.headers['x-correlation-id'] = correlationId as string;

  // Log request
  const startTime = Date.now();
  logger.info('Incoming request', {
    correlationId,
    method: req.method,
    path: req.path,
    query: req.query,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
  });

  // Log response
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    logger.info('Outgoing response', {
      correlationId,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration,
    });
  });

  next();
};
```

### 5. Service Proxy

```typescript
// src/services/serviceProxy.ts
import { createProxyMiddleware } from 'http-proxy-middleware';
import { createCircuitBreaker } from '../middleware/circuitBreaker';
import { logger } from '../utils/logger';

interface ServiceConfig {
  name: string;
  target: string;
  pathRewrite?: Record<string, string>;
  timeout?: number;
}

export const createServiceProxy = (config: ServiceConfig) => {
  const proxy = createProxyMiddleware({
    target: config.target,
    changeOrigin: true,
    pathRewrite: config.pathRewrite,
    timeout: config.timeout || 30000,
    onProxyReq: (proxyReq, req) => {
      // Forward correlation ID
      const correlationId = req.headers['x-correlation-id'];
      if (correlationId) {
        proxyReq.setHeader('X-Correlation-ID', correlationId as string);
      }

      logger.debug(`Proxying request to ${config.name}`, {
        correlationId,
        target: config.target,
        path: req.path,
      });
    },
    onProxyRes: (proxyRes, req) => {
      const correlationId = req.headers['x-correlation-id'];
      logger.debug(`Received response from ${config.name}`, {
        correlationId,
        statusCode: proxyRes.statusCode,
      });
    },
    onError: (err, req, res) => {
      const correlationId = req.headers['x-correlation-id'];
      logger.error(`Proxy error for ${config.name}`, {
        correlationId,
        error: err.message,
      });

      if (!res.headersSent) {
        res.status(503).json({
          error: 'Service unavailable',
          message: `${config.name} is currently unavailable`,
          correlationId,
        });
      }
    },
  });

  return proxy;
};
```

---

## 🔄 Request Flow

### 1. Successful Request Flow

```
Client Request
    ↓
Security Middleware (Helmet, CORS)
    ↓
Rate Limiter (Check Redis)
    ↓
Request Logger (Generate Correlation ID)
    ↓
Authentication (Validate JWT)
    ↓
Request Validator (Validate with Zod)
    ↓
Circuit Breaker (Check Service Health)
    ↓
Service Proxy (Forward to Microservice)
    ↓
Microservice Processing
    ↓
Response Transformation
    ↓
Response Logger
    ↓
Client Response (200 OK)
```

### 2. Rate Limited Request Flow

```
Client Request
    ↓
Security Middleware
    ↓
Rate Limiter (Limit Exceeded)
    ↓
Response Logger
    ↓
Client Response (429 Too Many Requests)
```

### 3. Circuit Open Request Flow

```
Client Request
    ↓
... (middleware chain)
    ↓
Circuit Breaker (Circuit Open)
    ↓
Error Handler
    ↓
Response Logger
    ↓
Client Response (503 Service Unavailable)
```

---

## 📊 Data Models

### Error Response Format

```typescript
interface ErrorResponse {
  error: string;           // Error type
  message: string;         // Human-readable message
  correlationId: string;   // Request correlation ID
  timestamp: string;       // ISO 8601 timestamp
  path: string;           // Request path
  details?: any;          // Additional error details
}
```

### Success Response Format

```typescript
interface SuccessResponse<T> {
  data: T;                // Response data
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test each middleware in isolation
- Mock dependencies (Redis, services)
- Test error scenarios
- Test edge cases

### Integration Tests
- Test complete request flow
- Test service integration
- Test error propagation
- Test rate limiting behavior

### Property-Based Tests
- Test validation with random inputs
- Test rate limiter with various patterns
- Test circuit breaker state transitions

---

## 📈 Performance Considerations

### Optimization Strategies
1. **Connection Pooling**: Reuse HTTP connections to services
2. **Response Caching**: Cache GET requests in Redis
3. **Compression**: Enable gzip compression
4. **Keep-Alive**: Enable HTTP keep-alive
5. **Async Processing**: Use async/await throughout

### Monitoring Metrics
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Circuit breaker state
- Rate limit hits

---

## 🔒 Security Considerations

### Authentication
- JWT token validation
- Token expiration check
- Refresh token support

### Authorization
- Role-based access control
- Resource-level permissions
- API key validation

### Data Protection
- No sensitive data in logs
- Sanitize error messages
- Encrypt data in transit

---

## 🚀 Deployment Strategy

### Environment Variables
```env
PORT=3000
NODE_ENV=production
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
CORS_ORIGINS=https://app.example.com
LOG_LEVEL=info
PROJECTS_SERVICE_URL=http://projects:3001
REVIEWS_SERVICE_URL=http://reviews:3002
ARCHITECTURE_SERVICE_URL=http://architecture:3003
```

### Health Check
```typescript
GET /health
Response: {
  status: 'healthy',
  timestamp: '2026-01-20T10:00:00Z',
  services: {
    redis: 'connected',
    projects: 'healthy',
    reviews: 'healthy',
    architecture: 'healthy'
  }
}
```

---

## ✅ Correctness Properties

### Property 1: Rate Limiting Fairness
**Validates**: Requirements US-3

For all users U and time windows W:
- If user U makes N requests in window W where N ≤ limit, all requests succeed
- If user U makes N requests in window W where N > limit, exactly (N - limit) requests fail with 429

### Property 2: Circuit Breaker State Transitions
**Validates**: Requirements US-4

For all services S:
- If error rate > threshold, circuit transitions to OPEN
- If circuit is OPEN for resetTimeout, circuit transitions to HALF_OPEN
- If request succeeds in HALF_OPEN, circuit transitions to CLOSED
- If request fails in HALF_OPEN, circuit transitions to OPEN

### Property 3: Request Validation Consistency
**Validates**: Requirements US-2

For all requests R and schemas S:
- If R is valid according to S, validation succeeds
- If R is invalid according to S, validation fails with 400
- Validation errors include field path and message

---

## 📝 Documentation

- API documentation generated with Swagger
- Architecture diagrams in Mermaid
- Configuration examples
- Troubleshooting guide
- Performance tuning guide

---

**Design Status**: ✅ Ready for Implementation  
**Next Step**: Create tasks.md and begin implementation
