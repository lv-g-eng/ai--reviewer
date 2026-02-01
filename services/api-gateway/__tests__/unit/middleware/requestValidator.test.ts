/**
 * Unit tests for Request Validator Middleware
 */

import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import {
  validateRequest,
  validateBody,
  validateQuery,
  validateParams,
} from '../../../src/middleware/requestValidator';

// Mock logger
jest.mock('../../../src/utils/logger', () => ({
  logger: {
    warn: jest.fn(),
    info: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('Request Validator Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let jsonMock: jest.Mock;
  let statusMock: jest.Mock;

  beforeEach(() => {
    // Reset mocks before each test
    jsonMock = jest.fn();
    statusMock = jest.fn().mockReturnValue({ json: jsonMock });

    mockRequest = {
      body: {},
      query: {},
      params: {},
      headers: {},
      method: 'GET',
    } as Partial<Request>;

    // Set path separately to avoid TypeScript readonly error
    Object.defineProperty(mockRequest, 'path', {
      value: '/test',
      writable: true,
    });

    mockResponse = {
      status: statusMock,
      json: jsonMock,
    };

    mockNext = jest.fn();
  });

  describe('validateRequest', () => {
    it('should pass validation with valid data', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string(),
          age: z.number(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { name: 'John', age: 30 };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(statusMock).not.toHaveBeenCalled();
    });

    it('should fail validation with invalid data', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string(),
          age: z.number(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { name: 'John', age: 'invalid' }; // age should be number

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Validation Error',
          message: expect.any(String),
          details: expect.arrayContaining([
            expect.objectContaining({
              field: expect.stringContaining('age'),
              message: expect.any(String),
            }),
          ]),
        })
      );
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should transform data according to schema', async () => {
      const schema = z.object({
        body: z.object({}).optional(),
        query: z.object({
          page: z.string().transform((val) => parseInt(val, 10)),
        }),
        params: z.object({}).optional(),
      });

      mockRequest.query = { page: '5' };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockRequest.query).toEqual({ page: 5 });
      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should include correlation ID in error response', async () => {
      const schema = z.object({
        body: z.object({
          email: z.string().email(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { email: 'invalid-email' };
      mockRequest.headers = { 'x-correlation-id': 'test-correlation-id' };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          correlationId: 'test-correlation-id',
        })
      );
    });

    it('should include timestamp and path in error response', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string().min(3),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { name: 'ab' }; // too short
      Object.defineProperty(mockRequest, 'path', {
        value: '/api/v1/test',
        writable: true,
      });

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamp: expect.any(String),
          path: '/api/v1/test',
        })
      );
    });

    it('should validate all parts: body, query, and params', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string(),
        }),
        query: z.object({
          page: z.string(),
        }),
        params: z.object({
          id: z.string(),
        }),
      });

      mockRequest.body = { name: 'John' };
      mockRequest.query = { page: '1' };
      mockRequest.params = { id: '123' };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should pass non-Zod errors to next middleware', async () => {
      const schema = z.object({
        body: z.object({}).optional(),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      // Mock parseAsync to throw a non-Zod error
      const error = new Error('Non-Zod error');
      jest.spyOn(schema, 'parseAsync').mockRejectedValue(error);

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith(error);
      expect(statusMock).not.toHaveBeenCalled();
    });
  });

  describe('validateBody', () => {
    it('should validate only request body', async () => {
      const schema = z.object({
        name: z.string(),
        email: z.string().email(),
      });

      mockRequest.body = { name: 'John', email: 'john@example.com' };

      const middleware = validateBody(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(statusMock).not.toHaveBeenCalled();
    });

    it('should fail validation for invalid body', async () => {
      const schema = z.object({
        name: z.string(),
        email: z.string().email(),
      });

      mockRequest.body = { name: 'John', email: 'invalid-email' };

      const middleware = validateBody(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Validation Error',
          message: 'Invalid request body.',
        })
      );
    });
  });

  describe('validateQuery', () => {
    it('should validate only query parameters', async () => {
      const schema = z.object({
        page: z.string(),
        limit: z.string(),
      });

      mockRequest.query = { page: '1', limit: '10' };

      const middleware = validateQuery(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(statusMock).not.toHaveBeenCalled();
    });

    it('should fail validation for invalid query', async () => {
      const schema = z.object({
        page: z.string().regex(/^\d+$/),
      });

      mockRequest.query = { page: 'invalid' };

      const middleware = validateQuery(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Validation Error',
          message: 'Invalid query parameters.',
        })
      );
    });
  });

  describe('validateParams', () => {
    it('should validate only route parameters', async () => {
      const schema = z.object({
        id: z.string().regex(/^[0-9a-fA-F]{24}$/),
      });

      mockRequest.params = { id: '507f1f77bcf86cd799439011' };

      const middleware = validateParams(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
      expect(statusMock).not.toHaveBeenCalled();
    });

    it('should fail validation for invalid params', async () => {
      const schema = z.object({
        id: z.string().regex(/^[0-9a-fA-F]{24}$/),
      });

      mockRequest.params = { id: 'invalid-id' };

      const middleware = validateParams(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(400);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Validation Error',
          message: 'Invalid route parameters.',
        })
      );
    });
  });

  describe('Error formatting', () => {
    it('should format multiple validation errors', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string().min(3),
          email: z.string().email(),
          age: z.number().positive(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = {
        name: 'ab', // too short
        email: 'invalid', // invalid email
        age: -5, // negative
      };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          details: expect.arrayContaining([
            expect.objectContaining({
              field: expect.stringContaining('name'),
            }),
            expect.objectContaining({
              field: expect.stringContaining('email'),
            }),
            expect.objectContaining({
              field: expect.stringContaining('age'),
            }),
          ]),
        })
      );
    });

    it('should include error codes in details', async () => {
      const schema = z.object({
        body: z.object({
          email: z.string().email(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { email: 'invalid' };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          details: expect.arrayContaining([
            expect.objectContaining({
              code: expect.any(String),
            }),
          ]),
        })
      );
    });
  });

  describe('Edge cases', () => {
    it('should handle empty body', async () => {
      const schema = z.object({
        body: z.object({}).optional(),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = {};

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should handle missing optional fields', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string(),
          description: z.string().optional(),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = { name: 'John' };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should handle nested object validation', async () => {
      const schema = z.object({
        body: z.object({
          user: z.object({
            name: z.string(),
            address: z.object({
              city: z.string(),
              zip: z.string(),
            }),
          }),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = {
        user: {
          name: 'John',
          address: {
            city: 'New York',
            zip: '10001',
          },
        },
      };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalledWith();
    });

    it('should format nested field paths correctly', async () => {
      const schema = z.object({
        body: z.object({
          user: z.object({
            email: z.string().email(),
          }),
        }),
        query: z.object({}).optional(),
        params: z.object({}).optional(),
      });

      mockRequest.body = {
        user: {
          email: 'invalid',
        },
      };

      const middleware = validateRequest(schema);
      await middleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          details: expect.arrayContaining([
            expect.objectContaining({
              field: 'body.user.email',
            }),
          ]),
        })
      );
    });
  });
});
