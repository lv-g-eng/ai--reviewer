# Service Registry

The Service Registry manages the configuration and discovery of all backend microservices in the API Gateway.

## Features

- **Service Registration**: Register and manage microservice configurations
- **Service Discovery**: Retrieve service URLs and configurations by name
- **Health Checking**: Monitor the health status of all registered services
- **Health Caching**: Cache health check results to reduce overhead
- **System Health**: Get overall system health status

## Usage

### Basic Usage

```typescript
import { serviceRegistry } from './services/serviceRegistry';

// Get a service URL
const authUrl = serviceRegistry.getServiceUrl('auth');

// Check if a service is registered
if (serviceRegistry.hasService('auth')) {
  // Service exists
}

// Get service configuration
const service = serviceRegistry.getService('auth');
console.log(service?.url, service?.healthCheckPath);
```

### Health Checks

```typescript
// Check health of a specific service
const health = await serviceRegistry.checkServiceHealth('auth');
console.log(health.status); // 'healthy' | 'unhealthy' | 'unknown'
console.log(health.responseTime); // Response time in ms

// Check health of all services
const allHealth = await serviceRegistry.checkAllServicesHealth();

// Get overall system health
const systemHealth = await serviceRegistry.getSystemHealth();
console.log(systemHealth.status); // 'healthy' | 'degraded' | 'unhealthy'
```

### Registering Custom Services

```typescript
import { ServiceRegistry } from './services/serviceRegistry';

const registry = new ServiceRegistry();

// Register a new service
registry.registerService({
  name: 'custom-service',
  url: 'http://custom:3000',
  healthCheckPath: '/health',
  timeout: 5000,
});
```

## Service Configuration

Each service requires the following configuration:

```typescript
interface ServiceConfig {
  name: string;              // Unique service identifier
  url: string;               // Base URL of the service
  healthCheckPath: string;   // Path to health check endpoint
  timeout?: number;          // Request timeout in ms (default: 5000)
}
```

## Health Status

Health check results include:

```typescript
interface ServiceHealth {
  name: string;                              // Service name
  status: 'healthy' | 'unhealthy' | 'unknown'; // Health status
  url: string;                               // Service URL
  lastChecked: Date;                         // Last check timestamp
  responseTime?: number;                     // Response time in ms
  error?: string;                            // Error message if unhealthy
}
```

## Default Services

The following services are registered by default:

1. **auth** - Authentication service
2. **code-review** - Code review engine
3. **architecture** - Architecture analyzer
4. **agentic-ai** - Agentic AI service
5. **project-manager** - Project management service

## Environment Variables

Service URLs are configured via environment variables:

- `AUTH_SERVICE_URL` - Authentication service URL
- `CODE_REVIEW_ENGINE_URL` - Code review engine URL
- `ARCHITECTURE_ANALYZER_URL` - Architecture analyzer URL
- `AGENTIC_AI_URL` - Agentic AI service URL
- `PROJECT_MANAGER_URL` - Project manager service URL

## System Health Status

The system health status is determined by the health of all services:

- **healthy**: All services are healthy
- **degraded**: Some services are unhealthy
- **unhealthy**: All services are unhealthy

## Testing

The service registry includes comprehensive unit tests:

```bash
npm test -- serviceRegistry.test.ts
```

## Integration with Health Endpoint

The service registry is integrated with the `/health` endpoint to provide real-time service status:

```bash
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-20T10:00:00Z",
  "service": "api-gateway",
  "version": "1.0.0",
  "services": [
    {
      "name": "auth",
      "status": "healthy",
      "url": "http://auth:3001",
      "responseTime": 45,
      "lastChecked": "2026-01-20T10:00:00Z"
    },
    // ... other services
  ]
}
```

## Error Handling

The service registry handles various error scenarios:

- **Connection refused**: Service is down or unreachable
- **Timeout**: Service is slow or unresponsive
- **Unknown service**: Service is not registered
- **Invalid response**: Service returned unexpected response

All errors are logged and included in the health status response.
