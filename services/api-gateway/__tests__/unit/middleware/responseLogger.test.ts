import {
  responseLogger,
  responseTimeLogger,
  statusCodeLogger,
} from '../../../src/middleware/responseLogger';
import { Request, Response, NextFunction } from 'express';
import { logger } from '../../../src/utils/logger';

// Mock logger
jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    debug: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    log: jest.fn(),
  },
}));

describe('Response Logger Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: jest.Mock;

  beforeEach(() => {
    mockReq = {
      method: 'GET',
      path: '/api/test',
      originalUrl: '/api/test?param=value',
      headers: {
        'x-correlation-id': 'test-correlation-id',
      },
    };
    mockRes = {
      statusCode: 200,
      json: jest.fn(),
      send: jest.fn(),
      on: jest.fn(),
      getHeader: jest.fn(),
      setHeader: jest.fn(),
    };
    mockNext = jest.fn();

    // Clear mock calls
    jest.clearAllMocks();
  });

  describe('responseLogger', () => {
    it('should override res.json to log response', () => {
      const originalJson = mockRes.json;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockRes.json).not.toBe(originalJson);
    });

    it('should override res.send to log response', () => {
      const originalSend = mockRes.send;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockRes.send).not.toBe(originalSend);
    });

    it('should log response when res.json is called', () => {
      (mockReq as any).startTime = Date.now() - 100; // 100ms ago

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      const responseData = { message: 'success' };
      (mockRes.json as jest.Mock)(responseData);

      expect(logger.log).toHaveBeenCalledWith(
        'info',
        'Outgoing response',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          method: 'GET',
          path: '/api/test',
          statusCode: 200,
        })
      );
    });

    it('should log response when res.send is called', () => {
      (mockReq as any).startTime = Date.now() - 100;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.send as jest.Mock)('response body');

      expect(logger.log).toHaveBeenCalledWith(
        'info',
        'Outgoing response',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          method: 'GET',
          path: '/api/test',
          statusCode: 200,
        })
      );
    });

    it('should log response duration', () => {
      const startTime = Date.now() - 150;
      (mockReq as any).startTime = startTime;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ message: 'success' });

      expect(logger.log).toHaveBeenCalledWith(
        'info',
        'Outgoing response',
        expect.objectContaining({
          duration: expect.any(Number),
        })
      );

      const logCall = (logger.log as jest.Mock).mock.calls[0][2];
      expect(logCall.duration).toBeGreaterThanOrEqual(150);
    });

    it('should log user ID if available', () => {
      (mockReq as any).startTime = Date.now();
      (mockReq as any).user = { id: 'user-123' };

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ message: 'success' });

      expect(logger.log).toHaveBeenCalledWith(
        'info',
        'Outgoing response',
        expect.objectContaining({
          userId: 'user-123',
        })
      );
    });

    it('should use error log level for 5xx status codes', () => {
      (mockReq as any).startTime = Date.now();
      mockRes.statusCode = 500;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ error: 'Internal Server Error' });

      expect(logger.log).toHaveBeenCalledWith(
        'error',
        'Outgoing response',
        expect.anything()
      );
    });

    it('should use warn log level for 4xx status codes', () => {
      (mockReq as any).startTime = Date.now();
      mockRes.statusCode = 404;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ error: 'Not Found' });

      expect(logger.log).toHaveBeenCalledWith(
        'warn',
        'Outgoing response',
        expect.anything()
      );
    });

    it('should use info log level for 2xx status codes', () => {
      (mockReq as any).startTime = Date.now();
      mockRes.statusCode = 200;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ message: 'success' });

      expect(logger.log).toHaveBeenCalledWith(
        'info',
        'Outgoing response',
        expect.anything()
      );
    });

    it('should log response body for error responses', () => {
      (mockReq as any).startTime = Date.now();
      mockRes.statusCode = 400;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      const errorBody = { error: 'Bad Request', message: 'Invalid input' };
      (mockRes.json as jest.Mock)(errorBody);

      expect(logger.debug).toHaveBeenCalledWith(
        'Response body',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          statusCode: 400,
          body: errorBody,
        })
      );
    });

    it('should sanitize sensitive data in error response body', () => {
      (mockReq as any).startTime = Date.now();
      mockRes.statusCode = 401;

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      const errorBody = {
        error: 'Unauthorized',
        token: 'secret-token',
        password: 'secret-password',
      };
      (mockRes.json as jest.Mock)(errorBody);

      expect(logger.debug).toHaveBeenCalledWith(
        'Response body',
        expect.objectContaining({
          body: {
            error: 'Unauthorized',
            token: '***REDACTED***',
            password: '***REDACTED***',
          },
        })
      );
    });

    it('should log slow requests', () => {
      (mockReq as any).startTime = Date.now() - 1500; // 1.5 seconds ago

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ message: 'success' });

      expect(logger.warn).toHaveBeenCalledWith(
        'Slow request detected',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          method: 'GET',
          path: '/api/test',
          duration: expect.any(Number),
          threshold: 1000,
        })
      );
    });

    it('should not log duplicate responses', () => {
      (mockReq as any).startTime = Date.now();

      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      (mockRes.json as jest.Mock)({ message: 'success' });
      (mockRes.json as jest.Mock)({ message: 'success' });

      // Should only log once
      expect(logger.log).toHaveBeenCalledTimes(1);
    });

    it('should call next middleware', () => {
      responseLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });
  });

  describe('responseTimeLogger', () => {
    it('should store start time on request', () => {
      responseTimeLogger(mockReq as Request, mockRes as Response, mockNext);

      expect((mockReq as any).startTime).toBeDefined();
      expect(typeof (mockReq as any).startTime).toBe('number');
    });

    it('should add X-Response-Time header on finish', () => {
      const finishCallback = jest.fn();
      (mockRes.on as jest.Mock).mockImplementation((event, callback) => {
        if (event === 'finish') {
          finishCallback.mockImplementation(callback);
        }
      });

      responseTimeLogger(mockReq as Request, mockRes as Response, mockNext);

      // Simulate response finish
      finishCallback();

      expect(mockRes.setHeader).toHaveBeenCalledWith(
        'X-Response-Time',
        expect.stringMatching(/^\d+ms$/)
      );
    });

    it('should call next middleware', () => {
      responseTimeLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });
  });

  describe('statusCodeLogger', () => {
    it('should log status code on finish', () => {
      const finishCallback = jest.fn();
      (mockRes.on as jest.Mock).mockImplementation((event, callback) => {
        if (event === 'finish') {
          finishCallback.mockImplementation(callback);
        }
      });

      mockRes.statusCode = 200;

      statusCodeLogger(mockReq as Request, mockRes as Response, mockNext);

      // Simulate response finish
      finishCallback();

      expect(logger.debug).toHaveBeenCalledWith(
        'Status code',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          statusCode: 200,
          statusCategory: '2xx',
          path: '/api/test',
          method: 'GET',
        })
      );
    });

    it('should categorize 4xx status codes', () => {
      const finishCallback = jest.fn();
      (mockRes.on as jest.Mock).mockImplementation((event, callback) => {
        if (event === 'finish') {
          finishCallback.mockImplementation(callback);
        }
      });

      mockRes.statusCode = 404;

      statusCodeLogger(mockReq as Request, mockRes as Response, mockNext);

      finishCallback();

      expect(logger.debug).toHaveBeenCalledWith(
        'Status code',
        expect.objectContaining({
          statusCode: 404,
          statusCategory: '4xx',
        })
      );
    });

    it('should categorize 5xx status codes', () => {
      const finishCallback = jest.fn();
      (mockRes.on as jest.Mock).mockImplementation((event, callback) => {
        if (event === 'finish') {
          finishCallback.mockImplementation(callback);
        }
      });

      mockRes.statusCode = 500;

      statusCodeLogger(mockReq as Request, mockRes as Response, mockNext);

      finishCallback();

      expect(logger.debug).toHaveBeenCalledWith(
        'Status code',
        expect.objectContaining({
          statusCode: 500,
          statusCategory: '5xx',
        })
      );
    });

    it('should call next middleware', () => {
      statusCodeLogger(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalledTimes(1);
      expect(mockNext).toHaveBeenCalledWith();
    });
  });
});
