# API Gateway Routes

This directory contains all route definitions for the API Gateway. Each route file handles a specific domain and forwards requests to the appropriate microservice.

## Route Files

### 1. Projects Routes (`projects.routes.ts`)
Handles project management operations.

**Base Path**: `/api/v1/projects`  
**Target Service**: Project Manager (`project-manager`)

**Endpoints**:
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create a new project
- `GET /api/v1/projects/:id` - Get project details
- `PUT /api/v1/projects/:id` - Update project
- `DELETE /api/v1/projects/:id` - Delete project
- `GET /api/v1/projects/:id/stats` - Get project statistics

### 2. Reviews Routes (`reviews.routes.ts`)
Handles code review operations.

**Base Path**: `/api/v1/reviews`  
**Target Service**: Code Review Engine (`code-review`)

**Endpoints**:
- `GET /api/v1/reviews` - List all reviews
- `POST /api/v1/reviews` - Create a new review
- `GET /api/v1/reviews/:id` - Get review details
- `PUT /api/v1/reviews/:id` - Update review
- `DELETE /api/v1/reviews/:id` - Delete review
- `POST /api/v1/reviews/:id/comments` - Add comment to review

### 3. Architecture Routes (`architecture.routes.ts`)
Handles architecture analysis operations.

**Base Path**: `/api/v1/architecture`  
**Target Service**: Architecture Analyzer (`architecture`)

**Endpoints**:
- `GET /api/v1/architecture/:projectId` - Get architecture overview
- `POST /api/v1/architecture/:projectId/scan` - Trigger architecture scan
- `GET /api/v1/architecture/:projectId/graph` - Get architecture graph data
- `GET /api/v1/architecture/:projectId/drift` - Get architecture drift analysis

### 4. Queue Routes (`queue.routes.ts`)
Handles asynchronous task queue operations.

**Base Path**: `/api/v1/queue`  
**Target Service**: Agentic AI (`agentic-ai`)

**Endpoints**:
- `GET /api/v1/queue` - List queue items
- `GET /api/v1/queue/:id` - Get queue item details
- `POST /api/v1/queue/:id/retry` - Retry failed queue item
- `DELETE /api/v1/queue/:id` - Cancel queue item

### 5. Admin Routes (`admin.routes.ts`)
Handles administrative operations.

**Base Path**: `/api/v1/admin`  
**Target Service**: Auth Service (`auth`)

**Endpoints**:
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/audit-logs` - Get audit logs
- `GET /api/v1/admin/settings` - Get system settings
- `PUT /api/v1/admin/settings` - Update system settings

### 6. Webhook Routes (`webhooks.ts`)
Handles webhook callbacks from external services.

**Base Path**: `/api/webhooks`

**Endpoints**:
- `POST /api/webhooks/github` - GitHub webhook handler
- `POST /api/webhooks/gitlab` - GitLab webhook handler

### 7. Health Routes (`health.ts`)
Health check endpoint for monitoring.

**Base Path**: `/health`

**Endpoints**:
- `GET /health` - Get API Gateway health status

## Architecture

### Request Flow

```
Client Request
    ↓
API Gateway (Express)
    ↓
Route Handler (e.g., projects.routes.ts)
    ↓
Service Proxy (createProxyForService)
    ↓
Service Registry (lookup service URL)
    ↓
HTTP Proxy Middleware
    ↓
Backend Microservice
    ↓
Response back to client
```

### Path Rewriting

Each route file uses path rewriting to transform the API Gateway path to the backend service path:

**Example for Projects**:
- Gateway receives: `GET /api/v1/projects/123`
- Path rewrite rule: `^/api/v1/projects` → `/api/projects`
- Backend receives: `GET /api/projects/123`

This allows the API Gateway to use versioned paths (`/v1/`) while backend services use simpler paths.

## Service Proxy Features

All routes use the `createProxyForService` function which provides:

1. **Correlation ID Forwarding**: Automatically forwards `X-Correlation-ID` header
2. **User Context**: Forwards user ID from authentication middleware
3. **Error Handling**: Returns 503 Service Unavailable when backend is down
4. **Logging**: Logs all proxy requests and responses
5. **Timeout Management**: Configurable timeout per service (default 30s)

## Adding New Routes

To add a new route file:

1. **Create the route file** in `src/routes/`:
   ```typescript
   import { Router } from 'express';
   import { createProxyForService } from '../services/serviceProxy';
   import { logger } from '../utils/logger';

   const router = Router();

   const myServiceProxy = createProxyForService('my-service', {
     '^/api/v1/myservice': '/api/myservice',
   });

   router.get('/', myServiceProxy);
   router.post('/', myServiceProxy);

   logger.info('My service routes initialized');

   export { router as myServiceRoutes };
   ```

2. **Register the service** in `src/services/serviceRegistry.ts`:
   ```typescript
   this.registerService({
     name: 'my-service',
     url: config.services.myService,
     healthCheckPath: '/health',
     timeout: 5000,
   });
   ```

3. **Add to main router** in `src/routes/index.ts`:
   ```typescript
   import { myServiceRoutes } from './myservice.routes';
   
   router.use('/v1/myservice', myServiceRoutes);
   ```

4. **Add configuration** in `src/config/index.ts`:
   ```typescript
   services: {
     myService: process.env.MY_SERVICE_URL || 'http://localhost:3006',
   }
   ```

## Testing

Each route file should have corresponding tests:

- **Unit Tests**: Test route registration and structure
- **Integration Tests**: Test end-to-end request flow with mock services
- **Property Tests**: Test validation and error handling

Example test location: `__tests__/unit/routes/myservice.routes.test.ts`

## Middleware

Routes can use middleware for:

- **Authentication**: `authMiddleware` - Validates JWT tokens
- **Authorization**: `requireRole('admin')` - Checks user roles
- **Validation**: `validateRequest(schema)` - Validates request data
- **Rate Limiting**: `rateLimiter` - Limits request rate
- **Circuit Breaker**: Automatically applied via service proxy

## Error Handling

All routes use standardized error responses:

```json
{
  "error": "Service Unavailable",
  "message": "Project Manager service is currently unavailable",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-20T10:00:00.000Z",
  "path": "/api/v1/projects"
}
```

## Monitoring

All routes are automatically monitored with:

- Request/response logging
- Performance metrics (response time)
- Error tracking
- Correlation IDs for distributed tracing

## Best Practices

1. **Use Path Rewriting**: Keep gateway paths versioned, backend paths simple
2. **Document Endpoints**: Add JSDoc comments for each route
3. **Handle Errors**: Let the service proxy handle errors gracefully
4. **Log Initialization**: Log when routes are initialized
5. **Export Named**: Use named exports for better IDE support
6. **Keep Routes Thin**: Routes should only handle routing, not business logic
7. **Use Service Registry**: Always use `createProxyForService` for consistency

## Related Documentation

- [Service Proxy Documentation](../services/README.md)
- [Service Registry Documentation](../services/serviceRegistry.ts)
- [API Gateway Design](.kiro/specs/api-gateway-week1/design.md)
- [API Gateway Requirements](.kiro/specs/api-gateway-week1/requirements.md)
