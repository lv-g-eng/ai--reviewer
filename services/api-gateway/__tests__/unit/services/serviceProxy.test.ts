import { Request, Response } from 'express';
import { createServiceProxy, createProxyForService, createMultipleProxies, ServiceProxyConfig } from '../../../src/services/serviceProxy';
import { serviceRegistry } from '../../../src/services/serviceRegistry';

// Mock http-proxy-middleware
jest.mock('http-proxy-middleware', () => ({
  createProxyMiddleware: jest.fn((options) => {
    // Return a mock middleware function that captures the options
    const middleware = jest.fn((req: Request, res: Response, next: Function) => {
      // Simulate proxy behavior
      if (options.onProxyReq) {
        const proxyReq = {
          setHeader: jest.fn(),
        };
        options.onProxyReq(proxyReq, req, res);
      }
      next();
    });
    (middleware as any).options = options;
    return middleware;
  }),
}));

// Mock logger
jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock service registry
jest.mock('../../../src/services/serviceRegistry', () => ({
  serviceRegistry: {
    getService: jest.fn(),
  },
}));

import { logger } from '../../../src/utils/logger';
import { createProxyMiddleware } from 'http-proxy-middleware';

describe('ServiceProxy', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockRequest = {
      headers: {},
      path: '/api/test',
      method: 'GET',
    };

    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis(),
      headersSent: false,
    };

    mockNext = jest.fn();
  });

  describe('createServiceProxy', () => {
    it('should create a proxy with basic configuration', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      const proxy = createServiceProxy(config);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          target: 'http://test:3000',
          changeOrigin: true,
          timeout: 30000,
        })
      );
      expect(proxy).toBeDefined();
    });

    it('should create a proxy with custom configuration', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
        pathRewrite: { '^/api': '' },
        timeout: 5000,
        changeOrigin: false,
      };

      createServiceProxy(config);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          target: 'http://test:3000',
          changeOrigin: false,
          pathRewrite: { '^/api': '' },
          timeout: 5000,
        })
      );
    });

    it('should use default timeout if not specified', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 30000,
        })
      );
    });

    it('should use default changeOrigin if not specified', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          changeOrigin: true,
        })
      );
    });
  });

  describe('onProxyReq - Correlation ID Forwarding', () => {
    it('should forward correlation ID to backend service', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyReq = {
        setHeader: jest.fn(),
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onProxyReq(mockProxyReq, mockRequest as Request);

      expect(mockProxyReq.setHeader).toHaveBeenCalledWith(
        'X-Correlation-ID',
        'test-correlation-id'
      );
    });

    it('should forward user ID if available', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyReq = {
        setHeader: jest.fn(),
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };
      (mockRequest as any).user = { id: 'user-123' };

      proxyOptions.onProxyReq(mockProxyReq, mockRequest as Request);

      expect(mockProxyReq.setHeader).toHaveBeenCalledWith('X-User-ID', 'user-123');
    });

    it('should log proxy request', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyReq = {
        setHeader: jest.fn(),
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onProxyReq(mockProxyReq, mockRequest as Request);

      expect(logger.debug).toHaveBeenCalledWith(
        'Proxying request to test-service',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          target: 'http://test:3000',
          path: '/api/test',
          method: 'GET',
        })
      );
    });

    it('should not fail if correlation ID is missing', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyReq = {
        setHeader: jest.fn(),
      };

      mockRequest.headers = {};

      expect(() => {
        proxyOptions.onProxyReq(mockProxyReq, mockRequest as Request);
      }).not.toThrow();
    });
  });

  describe('onProxyRes - Response Handling', () => {
    it('should log proxy response', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyRes = {
        statusCode: 200,
        headers: {},
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onProxyRes(mockProxyRes, mockRequest as Request);

      expect(logger.debug).toHaveBeenCalledWith(
        'Received response from test-service',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          statusCode: 200,
          path: '/api/test',
        })
      );
    });

    it('should forward correlation ID in response headers', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyRes = {
        statusCode: 200,
        headers: {},
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onProxyRes(mockProxyRes, mockRequest as Request);

      expect(mockProxyRes.headers['x-correlation-id']).toBe('test-correlation-id');
    });

    it('should not fail if correlation ID is missing', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyRes = {
        statusCode: 200,
        headers: {},
      };

      mockRequest.headers = {};

      expect(() => {
        proxyOptions.onProxyRes(mockProxyRes, mockRequest as Request);
      }).not.toThrow();
    });
  });

  describe('onError - Error Handling', () => {
    it('should log proxy errors', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const error = new Error('Connection refused');

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onError(error, mockRequest as Request, mockResponse as Response);

      expect(logger.error).toHaveBeenCalledWith(
        'Proxy error for test-service',
        expect.objectContaining({
          correlationId: 'test-correlation-id',
          error: 'Connection refused',
          path: '/api/test',
          method: 'GET',
        })
      );
    });

    it('should send 503 error response', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const error = new Error('Connection refused');

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };

      proxyOptions.onError(error, mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(503);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Service Unavailable',
          message: 'test-service service is currently unavailable',
          correlationId: 'test-correlation-id',
          path: '/api/test',
        })
      );
    });

    it('should not send response if headers already sent', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const error = new Error('Connection refused');

      mockResponse.headersSent = true;

      proxyOptions.onError(error, mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).not.toHaveBeenCalled();
      expect(mockResponse.json).not.toHaveBeenCalled();
    });

    it('should include timestamp in error response', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const error = new Error('Connection refused');

      proxyOptions.onError(error, mockRequest as Request, mockResponse as Response);

      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamp: expect.any(String),
        })
      );
    });
  });

  describe('createProxyForService', () => {
    it('should create proxy for registered service', () => {
      const mockService = {
        name: 'test-service',
        url: 'http://test:3000',
        healthCheckPath: '/health',
        timeout: 5000,
      };

      (serviceRegistry.getService as jest.Mock).mockReturnValue(mockService);

      const proxy = createProxyForService('test-service');

      expect(serviceRegistry.getService).toHaveBeenCalledWith('test-service');
      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          target: 'http://test:3000',
          timeout: 5000,
        })
      );
      expect(proxy).toBeDefined();
    });

    it('should create proxy with path rewrite', () => {
      const mockService = {
        name: 'test-service',
        url: 'http://test:3000',
        healthCheckPath: '/health',
        timeout: 5000,
      };

      (serviceRegistry.getService as jest.Mock).mockReturnValue(mockService);

      const pathRewrite = { '^/api': '' };
      createProxyForService('test-service', pathRewrite);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          pathRewrite,
        })
      );
    });

    it('should throw error if service not found', () => {
      (serviceRegistry.getService as jest.Mock).mockReturnValue(undefined);

      expect(() => {
        createProxyForService('non-existent-service');
      }).toThrow("Service 'non-existent-service' not found in registry");
    });
  });

  describe('createMultipleProxies', () => {
    it('should create proxies for multiple services', () => {
      const configs: ServiceProxyConfig[] = [
        {
          name: 'service1',
          target: 'http://service1:3000',
        },
        {
          name: 'service2',
          target: 'http://service2:3000',
        },
        {
          name: 'service3',
          target: 'http://service3:3000',
        },
      ];

      const proxies = createMultipleProxies(configs);

      expect(proxies.size).toBe(3);
      expect(proxies.has('service1')).toBe(true);
      expect(proxies.has('service2')).toBe(true);
      expect(proxies.has('service3')).toBe(true);
      expect(createProxyMiddleware).toHaveBeenCalledTimes(3);
    });

    it('should log proxy creation for each service', () => {
      const configs: ServiceProxyConfig[] = [
        {
          name: 'service1',
          target: 'http://service1:3000',
          timeout: 5000,
        },
      ];

      createMultipleProxies(configs);

      expect(logger.info).toHaveBeenCalledWith(
        'Created proxy for service1',
        expect.objectContaining({
          target: 'http://service1:3000',
          timeout: 5000,
        })
      );
    });

    it('should handle empty array', () => {
      const proxies = createMultipleProxies([]);

      expect(proxies.size).toBe(0);
    });

    it('should create proxies with different configurations', () => {
      const configs: ServiceProxyConfig[] = [
        {
          name: 'service1',
          target: 'http://service1:3000',
          timeout: 5000,
        },
        {
          name: 'service2',
          target: 'http://service2:3000',
          timeout: 10000,
          pathRewrite: { '^/api': '' },
        },
      ];

      const proxies = createMultipleProxies(configs);

      expect(proxies.size).toBe(2);
      expect(createProxyMiddleware).toHaveBeenCalledTimes(2);
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing user in request', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const mockProxyReq = {
        setHeader: jest.fn(),
      };

      mockRequest.headers = {
        'x-correlation-id': 'test-correlation-id',
      };
      // No user property

      expect(() => {
        proxyOptions.onProxyReq(mockProxyReq, mockRequest as Request);
      }).not.toThrow();
    });

    it('should handle error without stack trace', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      const proxyOptions = (createProxyMiddleware as jest.Mock).mock.calls[0][0];
      const error = new Error('Connection refused');
      delete error.stack;

      expect(() => {
        proxyOptions.onError(error, mockRequest as Request, mockResponse as Response);
      }).not.toThrow();
    });

    it('should handle proxy with no path rewrite', () => {
      const config: ServiceProxyConfig = {
        name: 'test-service',
        target: 'http://test:3000',
      };

      createServiceProxy(config);

      expect(createProxyMiddleware).toHaveBeenCalledWith(
        expect.objectContaining({
          pathRewrite: undefined,
        })
      );
    });
  });
});
