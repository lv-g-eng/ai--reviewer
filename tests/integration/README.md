# Integration Tests

This directory contains comprehensive integration tests for the AI-Powered Code Review Platform.

## Overview

The integration tests verify that all components of the system work together correctly:

- **Authentication Flow**: User registration, login, and protected route access
- **Project Management**: CRUD operations for projects
- **Code Review Features**: Code submission and review result retrieval
- **Performance Requirements**: Response time and concurrent request handling
- **Error Handling**: Graceful handling of various error conditions
- **Database Operations**: Data persistence and constraint validation

## Test Structure

### `full-stack-integration.test.ts`

The main integration test file that includes:

- **ServiceManager**: Manages starting/stopping backend and frontend services
- **ApiClient**: HTTP client for making API requests with authentication
- **Test Suites**: Organized test cases covering all major functionality

## Running Tests

### Prerequisites

1. Ensure all dependencies are installed:
   ```bash
   npm install
   ```

2. Make sure the database is running (PostgreSQL, Redis, Neo4j)

3. Ensure no other services are running on the test ports (3000, 8000)

### Running Integration Tests

From the root directory:

```bash
# Run integration tests
npm run test:integration

# Or use the helper scripts
./scripts/run-integration-tests.sh    # Linux/Mac
./scripts/run-integration-tests.bat   # Windows
```

### Test Configuration

Test configuration is defined in `TEST_CONFIG`:

```typescript
const TEST_CONFIG = {
  frontend_url: 'http://localhost:3000',
  backend_url: 'http://localhost:8000',
  api_gateway_url: 'http://localhost:3000',
  websocket_url: 'ws://localhost:3000/ws',
  test_timeout: 60000,
  startup_timeout: 30000,
};
```

## Test Data

The tests use predefined test data:

- **Test User**: `test@example.com` with password `TestPassword123!`
- **Test Project**: "Integration Test Project" for testing project operations

## Service Management

The `ServiceManager` class handles:

- Starting backend and frontend services
- Health checks to ensure services are ready
- Graceful shutdown of all services after tests

## Performance Assertions

The tests include performance requirements:

- API responses must be under 500ms
- Concurrent requests (10 simultaneous) must complete within 2 seconds

## Error Scenarios

Tests cover various error conditions:

- Invalid authentication credentials
- 404 errors for non-existent endpoints
- Invalid JSON payloads
- Database constraint violations

## Cleanup

Tests automatically clean up:

- Test projects created during testing
- User sessions and authentication tokens
- Any temporary data created

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Database connection**: Verify database services are running
3. **Service startup timeout**: Increase `startup_timeout` if services take longer to start
4. **Authentication failures**: Check that the auth service is properly configured

### Debug Mode

To run tests with verbose output:

```bash
npm run test:integration -- --verbose
```

### Individual Test Suites

To run specific test suites:

```bash
# Run only authentication tests
npm run test:integration -- --testNamePattern="Authentication Flow"

# Run only performance tests
npm run test:integration -- --testNamePattern="Performance Requirements"
```

## Contributing

When adding new integration tests:

1. Follow the existing test structure
2. Use the `ApiClient` for HTTP requests
3. Include proper cleanup in test teardown
4. Add performance assertions where appropriate
5. Test both success and error scenarios