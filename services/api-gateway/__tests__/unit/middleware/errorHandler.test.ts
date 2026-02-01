import { Request, Response, NextFunction } from 'express';
import {
  errorHandler,
  ApiError,
  createApiError,
  createValidationError,
  createUnauthorizedError,
  createForbiddenError,
  createNotFoundError,
  createRateLimitError,
  createServiceUnavailableError,
} from '../../../src/middleware/errorHandler';
import { ErrorCode } from '../../../src/utils/errorCodes';
import { logger } from '../../../src/utils/logger';

// Mock dependencies
jest.mock('../../../src/utils/logger');
jest.mock('../../../src/utils/correlationId', () => ({
  extractCorrelationId: jest.fn((req: Request) => req.headers['x-correlation-id'] || 'test-correlation-id'),
}));

describe('Error Handler Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let jsonMock: jest.Mock;
  let statusMock: jest.Mock;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup mock request
    mockRequest = {
      path: '/api/v1/test',
      url: '/api/v1/test?param=value',
      method: 'GET',
      ip: '127.0.0.1',
      headers: {
        'user-agent': 'test-agent',
        'x-correlation-id': 'test-correlation-id',
      },
    };

    // Setup mock response
    jsonMock = jest.fn();
    statusMock = jest.fn().mockReturnValue({ json: jsonMock });
    mockResponse = {
      status: statusMock,
    };

    // Setup mock next
    mockNext = jest.fn();
  });

  describe('Basic Error Handling', () => {
    it('should handle basic error with default values', () => {
      const error = new Error('Test error') as ApiError;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(500);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: ErrorCode.INTERNAL_ERROR,
          message: 'Test error',
          code: ErrorCode.INTERNAL_ERROR,
          correlationId: 'test-correlation-id',
          path: '/api/v1/test',
          retryable: false,
        })
      );
    });

    it('should use custom status code when provided', () => {
      const error = new Error('Not found') as ApiError;
      error.statusCode = 404;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(statusMock).toHaveBeenCalledWith(404);
      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: ErrorCode.NOT_FOUND,
          message: 'Not found',
        })
      );
    });

    it('should use custom error code when provided', () => {
      const error = new Error('Validation failed') as ApiError;
      error.statusCode = 400;
      error.errorCode = ErrorCode.VALIDATION_ERROR;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          error: ErrorCode.VALIDATION_ERROR,
          code: ErrorCode.VALIDATION_ERROR,
        })
      );
    });
  });

  describe('Correlation ID', () => {
    it('should include correlation ID from request headers', () => {
      const error = new Error('Test error') as ApiError;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          correlationId: 'test-correlation-id',
        })
      );
    });

    it('should use "unknown" when correlation ID is not available', () => {
      const { extractCorrelationId } = require('../../../src/utils/correlationId');
      extractCorrelationId.mockReturnValueOnce(undefined);

      const error = new Error('Test error') as ApiError;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          correlationId: 'unknown',
        })
      );
    });
  });

  describe('Error Details', () => {
    it('should include error details when provided', () => {
      const error = new Error('Validation failed') as ApiError;
      error.statusCode = 400;
      error.details = {
        field: 'email',
        reason: 'Invalid format',
      };

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          details: {
            field: 'email',
            reason: 'Invalid format',
          },
        })
      );
    });

    it('should not include details field when not provided', () => {
      const error = new Error('Test error') as ApiError;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response.details).toBeUndefined();
    });
  });

  describe('Stack Traces', () => {
    const originalEnv = process.env.NODE_ENV;

    afterEach(() => {
      process.env.NODE_ENV = originalEnv;
    });

    it('should include stack trace in development mode', () => {
      process.env.NODE_ENV = 'development';

      const error = new Error('Test error') as ApiError;
      error.stack = 'Error: Test error\n    at test.ts:10:5';

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          stack: expect.stringContaining('Error: Test error'),
        })
      );
    });

    it('should hide stack trace in production mode', () => {
      process.env.NODE_ENV = 'production';

      const error = new Error('Test error') as ApiError;
      error.stack = 'Error: Test error\n    at test.ts:10:5';

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response.stack).toBeUndefined();
    });

    it('should hide stack trace when NODE_ENV is not set (defaults to production)', () => {
      delete process.env.NODE_ENV;

      const error = new Error('Test error') as ApiError;
      error.stack = 'Error: Test error\n    at test.ts:10:5';

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response.stack).toBeUndefined();
    });
  });

  describe('Retryable Errors', () => {
    it('should mark service unavailable errors as retryable', () => {
      const error = new Error('Service unavailable') as ApiError;
      error.statusCode = 503;
      error.errorCode = ErrorCode.SERVICE_UNAVAILABLE;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          retryable: true,
        })
      );
    });

    it('should mark validation errors as non-retryable', () => {
      const error = new Error('Validation failed') as ApiError;
      error.statusCode = 400;
      error.errorCode = ErrorCode.VALIDATION_ERROR;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          retryable: false,
        })
      );
    });

    it('should respect explicit retryable flag', () => {
      const error = new Error('Custom error') as ApiError;
      error.statusCode = 500;
      error.retryable = true;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(jsonMock).toHaveBeenCalledWith(
        expect.objectContaining({
          retryable: true,
        })
      );
    });
  });

  describe('Error Logging', () => {
    it('should log error with full context', () => {
      const error = new Error('Test error') as ApiError;
      error.statusCode = 500;
      error.stack = 'Error stack trace';

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      expect(logger.error).toHaveBeenCalledWith(
        'API Gateway Error:',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          error: 'Test error',
          statusCode: 500,
          url: '/api/v1/test?param=value',
          method: 'GET',
          path: '/api/v1/test',
          ip: '127.0.0.1',
          userAgent: 'test-agent',
        })
      );
    });
  });

  describe('Response Format', () => {
    it('should return standardized error response format', () => {
      const error = new Error('Test error') as ApiError;
      error.statusCode = 400;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response).toHaveProperty('error');
      expect(response).toHaveProperty('message');
      expect(response).toHaveProperty('code');
      expect(response).toHaveProperty('correlationId');
      expect(response).toHaveProperty('timestamp');
      expect(response).toHaveProperty('path');
      expect(response).toHaveProperty('retryable');
    });

    it('should include ISO 8601 timestamp', () => {
      const error = new Error('Test error') as ApiError;

      errorHandler(error, mockRequest as Request, mockResponse as Response, mockNext);

      const response = jsonMock.mock.calls[0][0];
      expect(response.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });
});

describe('Error Factory Functions', () => {
  describe('createApiError', () => {
    it('should create error with all properties', () => {
      const error = createApiError('Test error', 400, ErrorCode.VALIDATION_ERROR, { field: 'email' });

      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(400);
      expect(error.errorCode).toBe(ErrorCode.VALIDATION_ERROR);
      expect(error.details).toEqual({ field: 'email' });
      expect(error.retryable).toBe(false);
    });

    it('should use default status code 500', () => {
      const error = createApiError('Test error');

      expect(error.statusCode).toBe(500);
    });

    it('should derive error code from status code when not provided', () => {
      const error = createApiError('Not found', 404);

      expect(error.errorCode).toBe(ErrorCode.NOT_FOUND);
    });
  });

  describe('createValidationError', () => {
    it('should create validation error with 400 status', () => {
      const error = createValidationError('Invalid input', { field: 'email' });

      expect(error.message).toBe('Invalid input');
      expect(error.statusCode).toBe(400);
      expect(error.errorCode).toBe(ErrorCode.VALIDATION_ERROR);
      expect(error.details).toEqual({ field: 'email' });
    });
  });

  describe('createUnauthorizedError', () => {
    it('should create unauthorized error with 401 status', () => {
      const error = createUnauthorizedError('Invalid token');

      expect(error.message).toBe('Invalid token');
      expect(error.statusCode).toBe(401);
      expect(error.errorCode).toBe(ErrorCode.UNAUTHORIZED);
    });

    it('should use default message', () => {
      const error = createUnauthorizedError();

      expect(error.message).toBe('Unauthorized');
    });
  });

  describe('createForbiddenError', () => {
    it('should create forbidden error with 403 status', () => {
      const error = createForbiddenError('Access denied');

      expect(error.message).toBe('Access denied');
      expect(error.statusCode).toBe(403);
      expect(error.errorCode).toBe(ErrorCode.FORBIDDEN);
    });

    it('should use default message', () => {
      const error = createForbiddenError();

      expect(error.message).toBe('Forbidden');
    });
  });

  describe('createNotFoundError', () => {
    it('should create not found error with 404 status', () => {
      const error = createNotFoundError('User not found', 'user');

      expect(error.message).toBe('User not found');
      expect(error.statusCode).toBe(404);
      expect(error.errorCode).toBe(ErrorCode.NOT_FOUND);
      expect(error.details).toEqual({ resource: 'user' });
    });

    it('should use default message', () => {
      const error = createNotFoundError();

      expect(error.message).toBe('Resource not found');
    });
  });

  describe('createRateLimitError', () => {
    it('should create rate limit error with 429 status', () => {
      const error = createRateLimitError('Too many requests', 60);

      expect(error.message).toBe('Too many requests');
      expect(error.statusCode).toBe(429);
      expect(error.errorCode).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
      expect(error.details).toEqual({ retryAfter: 60 });
    });

    it('should use default message', () => {
      const error = createRateLimitError();

      expect(error.message).toBe('Too many requests');
    });
  });

  describe('createServiceUnavailableError', () => {
    it('should create service unavailable error with 503 status', () => {
      const error = createServiceUnavailableError('Service down', 'projects-service');

      expect(error.message).toBe('Service down');
      expect(error.statusCode).toBe(503);
      expect(error.errorCode).toBe(ErrorCode.SERVICE_UNAVAILABLE);
      expect(error.details).toEqual({ service: 'projects-service' });
      expect(error.retryable).toBe(true);
    });

    it('should use default message', () => {
      const error = createServiceUnavailableError();

      expect(error.message).toBe('Service unavailable');
    });
  });
});
