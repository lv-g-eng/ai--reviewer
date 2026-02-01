# Validation Schemas

This directory contains Zod validation schemas for API Gateway request validation.

## Overview

The schemas are organized by domain and provide comprehensive validation for:
- Request bodies
- Query parameters
- Route parameters

## Files

### `common.schema.ts`
Common validation schemas used across multiple endpoints:
- **ObjectId validation**: MongoDB ObjectId format (24-char hex)
- **UUID validation**: Standard UUID v4 format
- **Date validation**: ISO 8601 datetime strings
- **Pagination**: Page-based and cursor-based pagination
- **Search**: Text search query parameters
- **Sorting**: Sort order and field validation
- **Common types**: Email, URL, tags, metadata, etc.

### `projects.schema.ts`
Validation schemas for Projects API endpoints:
- `createProjectSchema` - POST /api/v1/projects
- `listProjectsSchema` - GET /api/v1/projects
- `getProjectSchema` - GET /api/v1/projects/:id
- `updateProjectSchema` - PUT /api/v1/projects/:id
- `deleteProjectSchema` - DELETE /api/v1/projects/:id
- `getProjectStatsSchema` - GET /api/v1/projects/:id/stats

### `reviews.schema.ts`
Validation schemas for Reviews API endpoints:
- `createReviewSchema` - POST /api/v1/reviews
- `listReviewsSchema` - GET /api/v1/reviews
- `getReviewSchema` - GET /api/v1/reviews/:id
- `updateReviewSchema` - PUT /api/v1/reviews/:id
- `deleteReviewSchema` - DELETE /api/v1/reviews/:id
- `addCommentSchema` - POST /api/v1/reviews/:id/comments
- `getReviewCommentsSchema` - GET /api/v1/reviews/:id/comments
- `getReviewStatsSchema` - GET /api/v1/reviews/:id/stats

## Usage

### Basic Usage

```typescript
import { validateRequest } from '../middleware/requestValidator';
import { createProjectSchema } from '../schemas';

// Apply validation middleware to route
router.post('/projects', validateRequest(createProjectSchema), createProject);
```

### Schema Structure

Each complete request schema has the following structure:

```typescript
const exampleSchema = z.object({
  params: z.object({ /* route parameters */ }),
  query: z.object({ /* query parameters */ }),
  body: z.object({ /* request body */ }),
});
```

### Type Inference

TypeScript types can be inferred from schemas:

```typescript
import { CreateProjectBody, ListProjectsQuery } from '../schemas';

// Use inferred types in your handlers
const createProject = (req: Request<{}, {}, CreateProjectBody>) => {
  // req.body is fully typed
};
```

## Validation Features

### Automatic Transformations
- String to number conversion for pagination parameters
- Boolean string conversion ("true"/"false" → boolean)
- Trimming whitespace from strings
- Default values for optional fields

### Comprehensive Error Messages
- Field-level validation errors
- Clear error messages for each validation rule
- Path information for nested fields

### Security Features
- Maximum length validation to prevent DoS
- Format validation (email, URL, ObjectId, UUID)
- Integer and positive number validation
- Enum validation for controlled values

## Examples

### Pagination
```typescript
// Query: ?page=2&limit=20
// Validated and transformed to: { page: 2, limit: 20 }
```

### Project Creation
```typescript
// Request body:
{
  "name": "My Project",
  "description": "A sample project",
  "repositoryUrl": "https://github.com/user/repo",
  "repositoryProvider": "github",
  "branch": "main",
  "settings": {
    "autoReview": true,
    "minCoverageThreshold": 80
  }
}
```

### Review Filtering
```typescript
// Query: ?projectId=507f1f77bcf86cd799439011&status=completed&page=1&limit=10
// Validated and transformed with proper types
```

## Adding New Schemas

When adding new schemas:

1. **Create domain-specific file** (e.g., `users.schema.ts`)
2. **Import common schemas** for reusability
3. **Define individual schemas** for params, query, body
4. **Combine into complete schemas** for each endpoint
5. **Export types** for TypeScript inference
6. **Update index.ts** to export new schemas
7. **Document in this README**

Example:

```typescript
// users.schema.ts
import { z } from 'zod';
import { objectIdSchema, paginationSchema } from './common.schema';

export const createUserBodySchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export const createUserSchema = z.object({
  body: createUserBodySchema,
  query: z.object({}).optional(),
  params: z.object({}).optional(),
});

export type CreateUserBody = z.infer<typeof createUserBodySchema>;
```

## Best Practices

1. **Reuse common schemas** - Don't duplicate validation logic
2. **Provide clear descriptions** - Use `.describe()` for documentation
3. **Set reasonable limits** - Prevent DoS with max lengths
4. **Use enums** - For controlled value sets
5. **Transform data** - Convert strings to proper types
6. **Export types** - Enable TypeScript inference
7. **Test schemas** - Write unit tests for validation logic

## Testing

Schemas should be tested to ensure:
- Valid data passes validation
- Invalid data fails with appropriate errors
- Transformations work correctly
- Edge cases are handled

Example test:

```typescript
import { createProjectBodySchema } from '../schemas';

describe('createProjectBodySchema', () => {
  it('should validate valid project data', () => {
    const validData = {
      name: 'Test Project',
      repositoryUrl: 'https://github.com/test/repo',
    };
    
    const result = createProjectBodySchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should reject invalid repository URL', () => {
    const invalidData = {
      name: 'Test Project',
      repositoryUrl: 'not-a-url',
    };
    
    const result = createProjectBodySchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });
});
```

## Related Files

- `src/middleware/requestValidator.ts` - Middleware that uses these schemas
- `src/routes/*.routes.ts` - Route files that apply validation
- `__tests__/unit/schemas/` - Schema unit tests

## References

- [Zod Documentation](https://zod.dev/)
- [API Gateway Design Document](../../../../.kiro/specs/api-gateway-week1/design.md)
- [API Gateway Requirements](../../../../.kiro/specs/api-gateway-week1/requirements.md)
