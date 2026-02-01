# API Gateway - Testing Guide

> Comprehensive guide for testing the API Gateway

---

## Table of Contents

1. [Test Overview](#test-overview)
2. [Running Tests](#running-tests)
3. [Unit Tests](#unit-tests)
4. [Integration Tests](#integration-tests)
5. [Property-Based Tests](#property-based-tests)
6. [Performance Tests](#performance-tests)
7. [Manual Testing](#manual-testing)
8. [Test Coverage](#test-coverage)
9. [Writing Tests](#writing-tests)

---

## Test Overview

### Test Statistics

- **Total Tests**: 409 passing
- **Test Coverage**: 95%
- **Test Types**: Unit, Integration, Property-Based, Performance

### Test Structure

```
__tests__/
├── unit/                    # Unit tests (350+ tests)
│   ├── middleware/          # Middleware tests
│   ├── services/            # Service tests
│   ├── routes/              # Route tests
│   ├── schemas/             # Schema validation tests
│   └── utils/               # Utility tests
├── integration/             # Integration tests (50+ tests)
│   ├── api.test.ts          # Full API flow tests
│   └── health.test.ts       # Health check tests
├── property/                # Property-based tests (9 tests)
│   └── validation.property.test.ts
└── performance/             # Performance tests
    ├── load-test.ts         # Load testing
    ├── memory-test.ts       # Memory profiling
    └── run-all.ts           # Run all performance tests
```

---

## Running Tests

### All Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm run test:watch
```

### Specific Test Types

```bash
# Unit tests only
npm test -- __tests__/unit

# Integration tests only
npm test -- __tests__/integration

# Property-based tests only
npm run test:property

# Performance tests
npm run test:performance
```

### Specific Test Files

```bash
# Single file
npm test -- errorHandler.test.ts

# Multiple files
npm test -- errorHandler.test.ts rateLimiter.test.ts

# Pattern matching
npm test -- --testNamePattern="Circuit Breaker"
```

### Test Options

```bash
# Verbose output
npm test -- --verbose

# Silent mode
npm test -- --silent

# Update snapshots
npm test -- --updateSnapshot

# Run tests in band (sequential)
npm test -- --runInBand

# Bail after first failure
npm test -- --bail
```

---

## Unit Tests

Unit tests verify individual components in isolation.

### Middleware Tests

**Location**: `__tests__/unit/middleware/`

**Coverage**:
- Error handler
- Rate limiter
- Request validator
- Circuit breaker
- Request/response loggers
- Authentication

**Example**:
```typescript
describe('Error Handler', () => {
  it('should handle validation errors', () => {
    const error = new ValidationError('Invalid input');
    const response = errorHandler(error, req, res, next);
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});
```

### Schema Tests

**Location**: `__tests__/unit/schemas/`

**Coverage**:
- Common schemas
- Project schemas
- Review schemas
- Architecture schemas
- Admin schemas

**Example**:
```typescript
describe('Project Schema', () => {
  it('should validate valid project data', () => {
    const data = {
      name: 'Test Project',
      repositoryUrl: 'https://github.com/user/repo'
    };
    const result = createProjectSchema.safeParse(data);
    expect(result.success).toBe(true);
  });
});
```

### Service Tests

**Location**: `__tests__/unit/services/`

**Coverage**:
- Service registry
- Service proxy
- Health checks

### Route Tests

**Location**: `__tests__/unit/routes/`

**Coverage**:
- Route registration
- Route handlers
- Middleware application

---

## Integration Tests

Integration tests verify complete request flows.

### API Integration Tests

**Location**: `__tests__/integration/api.test.ts`

**Coverage**:
- Complete request flow
- Authentication flow
- Rate limiting behavior
- Circuit breaker behavior
- Error handling
- Correlation ID propagation

**Example**:
```typescript
describe('API Integration', () => {
  it('should handle complete request flow', async () => {
    const response = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);
    
    expect(response.body).toHaveProperty('data');
    expect(response.headers).toHaveProperty('x-correlation-id');
  });
});
```

### Health Check Tests

**Location**: `__tests__/integration/health.test.ts`

**Coverage**:
- Health endpoint
- Service health checks
- Redis connectivity

---

## Property-Based Tests

Property-based tests verify properties that should always hold true.

**Location**: `__tests__/property/validation.property.test.ts`

**Library**: fast-check

**Coverage**:
- Validation properties
- Rate limiter properties
- Circuit breaker properties

**Example**:
```typescript
describe('Validation Properties', () => {
  it('should always reject invalid URLs', () => {
    fc.assert(
      fc.property(fc.string(), (str) => {
        if (!isValidUrl(str)) {
          const result = urlSchema.safeParse(str);
          return !result.success;
        }
        return true;
      })
    );
  });
});
```

### Running Property Tests

```bash
# Run all property tests
npm run test:property

# Run with more iterations
npm test -- --testNamePattern="Property" --maxWorkers=1
```

---

## Performance Tests

Performance tests verify the gateway meets performance requirements.

### Load Testing

**Location**: `__tests__/performance/load-test.ts`

**Tool**: autocannon

**Metrics**:
- Requests per second
- Average latency
- P95/P99 latency
- Error rate

**Run**:
```bash
npm run test:performance:load
```

**Expected Results**:
- Throughput: >1000 req/s
- Avg latency: <50ms
- P95 latency: <100ms
- Error rate: <1%

### Memory Testing

**Location**: `__tests__/performance/memory-test.ts`

**Metrics**:
- Heap usage
- External memory
- Memory leaks

**Run**:
```bash
npm run test:performance:memory
```

**Expected Results**:
- Heap usage: <512MB
- No memory leaks
- Stable memory over time

### All Performance Tests

```bash
npm run test:performance
```

---

## Manual Testing

### Using cURL

#### Health Check
```bash
curl http://localhost:3000/health
```

#### Authenticated Request
```bash
# Get token first
TOKEN=$(curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Make authenticated request
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/v1/projects
```

#### Test Rate Limiting
```bash
# Send 110 requests quickly
for i in {1..110}; do
  curl http://localhost:3000/api/v1/projects
done
# Should get 429 after 100 requests
```

#### Test Validation
```bash
# Invalid request (missing required fields)
curl -X POST http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
# Should get 400 validation error
```

### Using Postman

1. **Import Collection**: Create Postman collection with all endpoints
2. **Set Environment**: Configure base URL and token
3. **Run Tests**: Execute collection with tests
4. **Monitor**: Use Postman monitors for continuous testing

### Using HTTPie

```bash
# Install HTTPie
pip install httpie

# Health check
http GET http://localhost:3000/health

# Authenticated request
http GET http://localhost:3000/api/v1/projects \
  Authorization:"Bearer $TOKEN"

# POST request
http POST http://localhost:3000/api/v1/projects \
  Authorization:"Bearer $TOKEN" \
  name="Test Project" \
  repositoryUrl="https://github.com/test/repo"
```

---

## Test Coverage

### View Coverage Report

```bash
# Generate coverage report
npm test -- --coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Coverage Targets

- **Overall**: >80% (Current: 95%)
- **Statements**: >80%
- **Branches**: >75%
- **Functions**: >80%
- **Lines**: >80%

### Coverage by Component

| Component | Coverage |
|-----------|----------|
| Middleware | 98% |
| Services | 95% |
| Routes | 92% |
| Schemas | 100% |
| Utils | 96% |

### Improving Coverage

```bash
# Find uncovered lines
npm test -- --coverage --coverageReporters=text

# Focus on specific file
npm test -- --coverage --collectCoverageFrom="src/middleware/errorHandler.ts"
```

---

## Writing Tests

### Test Structure

```typescript
describe('Component Name', () => {
  // Setup
  beforeAll(() => {
    // Runs once before all tests
  });

  beforeEach(() => {
    // Runs before each test
  });

  afterEach(() => {
    // Runs after each test
  });

  afterAll(() => {
    // Runs once after all tests
  });

  describe('Feature', () => {
    it('should do something', () => {
      // Arrange
      const input = 'test';

      // Act
      const result = doSomething(input);

      // Assert
      expect(result).toBe('expected');
    });
  });
});
```

### Best Practices

1. **Use Descriptive Names**
   ```typescript
   // Good
   it('should return 400 when name is missing')
   
   // Bad
   it('test validation')
   ```

2. **Test One Thing**
   ```typescript
   // Good
   it('should validate email format')
   it('should validate email length')
   
   // Bad
   it('should validate email')
   ```

3. **Use AAA Pattern**
   - Arrange: Set up test data
   - Act: Execute the code
   - Assert: Verify results

4. **Mock External Dependencies**
   ```typescript
   jest.mock('../services/serviceProxy');
   ```

5. **Clean Up After Tests**
   ```typescript
   afterEach(() => {
     jest.clearAllMocks();
   });
   ```

### Example Test

```typescript
import request from 'supertest';
import { app } from '../src/index';

describe('Projects API', () => {
  let token: string;

  beforeAll(async () => {
    // Get auth token
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'password' });
    token = response.body.token;
  });

  describe('GET /api/v1/projects', () => {
    it('should return list of projects', async () => {
      const response = await request(app)
        .get('/api/v1/projects')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body).toHaveProperty('data');
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body).toHaveProperty('pagination');
    });

    it('should return 401 without token', async () => {
      await request(app)
        .get('/api/v1/projects')
        .expect(401);
    });

    it('should support pagination', async () => {
      const response = await request(app)
        .get('/api/v1/projects?page=1&limit=10')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body.pagination.page).toBe(1);
      expect(response.body.pagination.limit).toBe(10);
    });
  });
});
```

---

## Continuous Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Troubleshooting Tests

### Tests Failing

```bash
# Run with verbose output
npm test -- --verbose

# Run single test
npm test -- --testNamePattern="specific test name"

# Debug test
node --inspect-brk node_modules/.bin/jest --runInBand
```

### Slow Tests

```bash
# Find slow tests
npm test -- --verbose | grep -E "PASS|FAIL"

# Run in parallel
npm test -- --maxWorkers=4
```

### Flaky Tests

```bash
# Run test multiple times
npm test -- --testNamePattern="flaky test" --runInBand --repeat=10
```

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0
