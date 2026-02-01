# API Gateway Middleware

This directory contains middleware functions used throughout the API Gateway.

## Request Validator

The `requestValidator.ts` middleware provides request validation using Zod schemas.

### Features

- ✅ Validates request body, query parameters, and route parameters
- ✅ Formats validation errors in a user-friendly way
- ✅ Returns 400 status code for validation failures
- ✅ Passes validated (and transformed) data to the next middleware
- ✅ Includes correlation ID in error responses
- ✅ Logs validation failures for debugging

### Usage

#### Basic Usage

```typescript
import { validateRequest } from '../middleware/requestValidator';
import { createProjectSchema } from '../schemas/projects.schema';

router.post('/', validateRequest(createProjectSchema), (req, res) => {
  // Request is validated, safe to use req.body, req.query, req.params
  const { name, description } = req.body;
  // ...
});
```

#### Validate Only Body

```typescript
import { validateBody } from '../middleware/requestValidator';
import { createProjectBodySchema } from '../schemas/projects.schema';

router.post('/', validateBody(createProjectBodySchema), (req, res) => {
  // Only body is validated
});
```

#### Validate Only Query Parameters

```typescript
import { validateQuery } from '../middleware/requestValidator';
import { listProjectsQuerySchema } from '../schemas/projects.schema';

router.get('/', validateQuery(listProjectsQuerySchema), (req, res) => {
  // Only query parameters are validated
});
```

#### Validate Only Route Parameters

```typescript
import { validateParams } from '../middleware/requestValidator';
import { idParamSchema } from '../schemas/common.schema';

router.get('/:id', validateParams(idParamSchema), (req, res) => {
  // Only route parameters are validated
});
```

### Error Response Format

When validation fails, the middleware returns a 400 status code with the following JSON structure:

```json
{
  "error": "Validation Error",
  "message": "Invalid request data. Please check the details and try again.",
  "details": [
    {
      "field": "body.email",
      "message": "Invalid email format",
      "code": "invalid_string"
    },
    {
      "field": "query.page",
      "message": "Expected number, received string",
      "code": "invalid_type"
    }
  ],
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-20T10:30:00.000Z",
  "path": "/api/v1/projects"
}
```

### Schema Definition

Schemas should be defined using Zod and follow this structure:

```typescript
import { z } from 'zod';

// For validateRequest (validates all parts)
export const createProjectSchema = z.object({
  body: z.object({
    name: z.string().min(1).max(100),
    description: z.string().optional(),
  }),
  query: z.object({}).optional(),
  params: z.object({}).optional(),
});

// For validateBody (validates only body)
export const createProjectBodySchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
});
```

### Data Transformation

Zod schemas can transform data during validation. The middleware applies these transformations:

```typescript
const schema = z.object({
  query: z.object({
    page: z.string().transform((val) => parseInt(val, 10)),
    limit: z.string().transform((val) => parseInt(val, 10)),
  }),
});

// Before validation: req.query = { page: "5", limit: "10" }
// After validation:  req.query = { page: 5, limit: 10 }
```

### Logging

The middleware logs validation failures with the following information:

- Correlation ID (if present)
- HTTP method and path
- Validation errors
- Request body, query, and params (for debugging)

Example log:

```json
{
  "level": "warn",
  "message": "Request validation failed",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/v1/projects",
  "errors": [
    {
      "code": "invalid_type",
      "expected": "string",
      "received": "number",
      "path": ["body", "name"],
      "message": "Expected string, received number"
    }
  ]
}
```

### Best Practices

1. **Always validate user input**: Use validation middleware on all routes that accept user input
2. **Use specific schemas**: Create specific schemas for each endpoint rather than reusing generic ones
3. **Provide helpful error messages**: Use `.describe()` in schemas to provide context
4. **Transform data early**: Use Zod transformations to convert string query params to numbers, dates, etc.
5. **Keep schemas DRY**: Reuse common schemas from `common.schema.ts`

### Testing

The middleware is thoroughly tested in `__tests__/unit/middleware/requestValidator.test.ts`:

- ✅ Valid data passes validation
- ✅ Invalid data fails with 400 status
- ✅ Data transformations are applied
- ✅ Correlation IDs are included in errors
- ✅ Multiple validation errors are formatted correctly
- ✅ Nested object validation works
- ✅ Non-Zod errors are passed to error handler

Run tests:

```bash
npm test -- requestValidator.test.ts
```

### Related Files

- `src/schemas/` - Zod validation schemas
- `src/utils/logger.ts` - Logger for validation failures
- `__tests__/unit/middleware/requestValidator.test.ts` - Unit tests
