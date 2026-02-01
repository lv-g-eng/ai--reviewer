import {
  requestLogger,
  requestMetadataLogger,
} from '../../../src/middleware/requestLogger';
import { Request, Response, NextFunction } from 'express';
import { logger } from '../../../src/utils/logger';

// Mock logger
jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    debug: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  },
}));

describe('Request Logger Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: jest.Mock;

  beforeEach(() => {
    mockReq = {
      method: 'GET',
      path: '/api/test',
      originalUrl: '/api/test?param=value',
      query: { param: 'value' },
      headers: {
        'x-correlation-id': 'test-correlation-id',
        'user-agent': 'test-agent',
      },
      ip: '127.0.0.1',
      body: {},
    };
    mockRes = {
      on: jest.fn(),
    };
    mockNext = jest.fn();

    // Clear mock calls
    jest.clearAllMocks();
  });

  describe('requestLogger', () => {
    it('should log incoming request with correlation ID', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          method: 'GET',
          path: '/api/test',
          url: '/api/test?param=value',
        })
      );
    });

    it('should log query parameters if present', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          query: { param: 'value' },
        })
      );
    });

    it('should not log query parameters if empty', () => {
      mockReq.query = {};

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          query: undefined,
        })
      );
    });

    it('should log IP address', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          ip: '127.0.0.1',
        })
      );
    });

    it('should log user agent', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          userAgent: 'test-agent',
        })
      );
    });

    it('should log user ID if authenticated', () => {
      (mockReq as any).user = { id: 'user-123' };

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.info).toHaveBeenCalledWith(
        'Incoming request',
        expect.objectContaining({
          userId: 'user-123',
        })
      );
    });

    it('should log request body for POST requests', () => {
      mockReq.method = 'POST';
      mockReq.body = { data: 'test' };

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request body',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          body: { data: 'test' },
        })
      );
    });

    it('should not log request body for GET requests', () => {
      mockReq.method = 'GET';
      mockReq.body = { data: 'test' };

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).not.toHaveBeenCalledWith(
        'Request body',
        expect.anything()
      );
    });

    it('should sanitize sensitive data in request body', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        username: 'testuser',
        password: 'secret123',
        token: 'secret-token',
      };

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request body',
        expect.objectContaining({
          body: {
            username: 'testuser',
            password: '***REDACTED***',
            token: '***REDACTED***',
          },
        })
      );
    });

    it('should sanitize nested sensitive data', () => {
      mockReq.method = 'POST';
      mockReq.body = {
        user: {
          username: 'testuser',
          password: 'secret123',
        },
      };

      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request body',
        expect.objectContaining({
          body: {
            user: {
              username: 'testuser',
              password: '***REDACTED***',
            },
          },
        })
      );
    });

    it('should store start time on request', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect((mockReq as any).startTime).toBeDefined();
      expect(typeof (mockReq as any).startTime).toBe('number');
    });

    it('should call next middleware', () => {
      requestLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });
  });

  describe('requestMetadataLogger', () => {
    it('should log request metadata', () => {
      mockReq.headers = {
        'x-correlation-id': 'test-correlation-id',
        'content-type': 'application/json',
        'content-length': '100',
        'accept': 'application/json',
      };

      requestMetadataLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request metadata',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          contentType: 'application/json',
          contentLength: '100',
          accept: 'application/json',
        })
      );
    });

    it('should log authorization type for Bearer token', () => {
      mockReq.headers = {
        'x-correlation-id': 'test-correlation-id',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
      };

      requestMetadataLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request metadata',
        expect.objectContaining({
          authType: 'Bearer',
          tokenPreview: 'eyJhbGciOi...',
        })
      );
    });

    it('should log authorization type for other auth methods', () => {
      mockReq.headers = {
        'x-correlation-id': 'test-correlation-id',
        'authorization': 'Basic dXNlcjpwYXNz',
      };

      requestMetadataLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request metadata',
        expect.objectContaining({
          authType: 'Other',
        })
      );
    });

    it('should log referer and origin if present', () => {
      mockReq.headers = {
        'x-correlation-id': 'test-correlation-id',
        'referer': 'https://example.com',
        'origin': 'https://example.com',
      };

      requestMetadataLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(logger.debug).toHaveBeenCalledWith(
        'Request metadata',
        expect.objectContaining({
          referer: 'https://example.com',
          origin: 'https://example.com',
        })
      );
    });

    it('should call next middleware', () => {
      requestMetadataLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });
  });
});
