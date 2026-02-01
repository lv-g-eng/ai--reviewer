/**
 * Request Validator Middleware
 *
 * Validates incoming requests using Zod schemas.
 * Validates request body, query parameters, and route parameters.
 * Returns 400 status code with formatted error messages for validation failures.
 */

import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { logger } from '../utils/logger';

/**
 * Validation error detail
 */
interface ValidationErrorDetail {
  field: string;
  message: string;
  code?: string;
}

/**
 * Validation error response
 */
interface ValidationErrorResponse {
  error: string;
  message: string;
  details: ValidationErrorDetail[];
  correlationId?: string;
  timestamp: string;
  path: string;
}

/**
 * Format Zod validation errors into user-friendly format
 *
 * @param error - Zod validation error
 * @returns Array of formatted error details
 */
function formatValidationErrors(error: ZodError): ValidationErrorDetail[] {
  return error.errors.map((err) => {
    // Build field path (e.g., "body.name", "query.page", "params.id")
    const field = err.path.join('.');

    // Get error message
    const message = err.message;

    // Get error code
    const code = err.code;

    return {
      field,
      message,
      code,
    };
  });
}

/**
 * Create validation middleware for a given schema
 *
 * @param schema - Zod schema to validate against
 * @returns Express middleware function
 *
 * @example
 * ```typescript
 * import { createProjectSchema } from '../schemas/projects.schema';
 *
 * router.post('/', validateRequest(createProjectSchema), (req, res) => {
 *   // Request is validated, safe to use req.body, req.query, req.params
 * });
 * ```
 */
export function validateRequest(schema: ZodSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validate request data against schema
      const validated = await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });

      // Replace request data with validated (and potentially transformed) data
      // This ensures type safety and applies any transformations defined in the schema
      if (validated.body !== undefined) {
        req.body = validated.body;
      }
      if (validated.query !== undefined) {
        req.query = validated.query;
      }
      if (validated.params !== undefined) {
        req.params = validated.params;
      }

      // Validation successful, proceed to next middleware
      next();
    } catch (error) {
      // Handle Zod validation errors
      if (error instanceof ZodError) {
        const correlationId = req.headers['x-correlation-id'] as
          | string
          | undefined;

        // Log validation failure
        logger.warn('Request validation failed', {
          correlationId,
          method: req.method,
          path: req.path,
          errors: error.errors,
          body: req.body,
          query: req.query,
          params: req.params,
        });

        // Format validation errors
        const details = formatValidationErrors(error);

        // Build error response
        const errorResponse: ValidationErrorResponse = {
          error: 'Validation Error',
          message:
            'Invalid request data. Please check the details and try again.',
          details,
          correlationId,
          timestamp: new Date().toISOString(),
          path: req.path,
        };

        // Return 400 Bad Request with error details
        return res.status(400).json(errorResponse);
      }

      // For non-Zod errors, pass to error handler
      next(error);
    }
  };
}

/**
 * Validate only request body
 *
 * @param schema - Zod schema for body validation
 * @returns Express middleware function
 */
export function validateBody(schema: ZodSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync(req.body);
      req.body = validated;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const correlationId = req.headers['x-correlation-id'] as
          | string
          | undefined;

        logger.warn('Request body validation failed', {
          correlationId,
          method: req.method,
          path: req.path,
          errors: error.errors,
        });

        const details = formatValidationErrors(error);
        const errorResponse: ValidationErrorResponse = {
          error: 'Validation Error',
          message: 'Invalid request body.',
          details,
          correlationId,
          timestamp: new Date().toISOString(),
          path: req.path,
        };

        return res.status(400).json(errorResponse);
      }
      next(error);
    }
  };
}

/**
 * Validate only query parameters
 *
 * @param schema - Zod schema for query validation
 * @returns Express middleware function
 */
export function validateQuery(schema: ZodSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync(req.query);
      req.query = validated;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const correlationId = req.headers['x-correlation-id'] as
          | string
          | undefined;

        logger.warn('Query parameter validation failed', {
          correlationId,
          method: req.method,
          path: req.path,
          errors: error.errors,
        });

        const details = formatValidationErrors(error);
        const errorResponse: ValidationErrorResponse = {
          error: 'Validation Error',
          message: 'Invalid query parameters.',
          details,
          correlationId,
          timestamp: new Date().toISOString(),
          path: req.path,
        };

        return res.status(400).json(errorResponse);
      }
      next(error);
    }
  };
}

/**
 * Validate only route parameters
 *
 * @param schema - Zod schema for params validation
 * @returns Express middleware function
 */
export function validateParams(schema: ZodSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const validated = await schema.parseAsync(req.params);
      req.params = validated;
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const correlationId = req.headers['x-correlation-id'] as
          | string
          | undefined;

        logger.warn('Route parameter validation failed', {
          correlationId,
          method: req.method,
          path: req.path,
          errors: error.errors,
        });

        const details = formatValidationErrors(error);
        const errorResponse: ValidationErrorResponse = {
          error: 'Validation Error',
          message: 'Invalid route parameters.',
          details,
          correlationId,
          timestamp: new Date().toISOString(),
          path: req.path,
        };

        return res.status(400).json(errorResponse);
      }
      next(error);
    }
  };
}

// Export types for use in other modules
export type { ValidationErrorDetail, ValidationErrorResponse };
