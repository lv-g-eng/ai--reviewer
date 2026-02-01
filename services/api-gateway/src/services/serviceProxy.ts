import { createProxyMiddleware, Options } from 'http-proxy-middleware';
import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { serviceRegistry } from './serviceRegistry';
import {
  createCircuitBreaker,
  getCircuitBreaker,
} from '../middleware/circuitBreaker';
import axios from 'axios';

/**
 * Service proxy configuration
 */
export interface ServiceProxyConfig {
  name: string;
  target: string;
  pathRewrite?: Record<string, string>;
  timeout?: number;
  changeOrigin?: boolean;
  useCircuitBreaker?: boolean; // Enable circuit breaker for this service
}

/**
 * Create a proxy middleware for a specific service
 *
 * This function creates an HTTP proxy that forwards requests to backend microservices.
 * It handles:
 * - Correlation ID forwarding
 * - Request/response logging
 * - Error handling
 * - Timeout configuration
 * - Circuit breaker integration (optional)
 *
 * @param config - Service proxy configuration
 * @returns Express middleware for proxying requests
 */
export const createServiceProxy = (config: ServiceProxyConfig) => {
  // Create circuit breaker if enabled
  if (config.useCircuitBreaker !== false) {
    // Create a circuit breaker for this service
    const serviceCall = async (url: string, options: any) => {
      const response = await axios({
        url,
        method: options.method,
        headers: options.headers,
        data: options.data,
        timeout: config.timeout || 30000,
      });
      return response;
    };

    createCircuitBreaker(serviceCall, config.name, {
      timeout: config.timeout || 30000,
      errorThresholdPercentage: 50,
      resetTimeout: 30000,
    });
  }

  const proxyOptions: Options = {
    target: config.target,
    changeOrigin:
      config.changeOrigin !== undefined ? config.changeOrigin : true,
    pathRewrite: config.pathRewrite,
    timeout: config.timeout || 30000, // 30 seconds default

    /**
     * Intercept proxy request to add correlation ID and log
     */
    onProxyReq: (proxyReq, req: Request) => {
      // Forward correlation ID to backend service
      const correlationId = req.headers['x-correlation-id'];
      if (correlationId) {
        proxyReq.setHeader('X-Correlation-ID', correlationId as string);
      }

      // Forward user ID if available (from auth middleware)
      const userId = (req as any).user?.id;
      if (userId) {
        proxyReq.setHeader('X-User-ID', userId);
      }

      logger.debug(`Proxying request to ${config.name}`, {
        correlationId,
        target: config.target,
        path: req.path,
        method: req.method,
        userId,
      });
    },

    /**
     * Intercept proxy response to log
     */
    onProxyRes: (proxyRes, req: Request) => {
      const correlationId = req.headers['x-correlation-id'];

      logger.debug(`Received response from ${config.name}`, {
        correlationId,
        statusCode: proxyRes.statusCode,
        path: req.path,
      });

      // Forward correlation ID in response headers
      if (correlationId) {
        proxyRes.headers['x-correlation-id'] = correlationId as string;
      }
    },

    /**
     * Handle proxy errors
     */
    onError: (err: Error, req: Request, res: Response) => {
      const correlationId = req.headers['x-correlation-id'];

      logger.error(`Proxy error for ${config.name}`, {
        correlationId,
        error: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method,
      });

      // Only send response if headers haven't been sent yet
      if (!res.headersSent) {
        res.status(503).json({
          error: 'Service Unavailable',
          message: `${config.name} service is currently unavailable`,
          correlationId,
          timestamp: new Date().toISOString(),
          path: req.path,
        });
      }
    },
  };

  return createProxyMiddleware(proxyOptions);
};

/**
 * Create a proxy for a registered service by name
 *
 * This is a convenience function that looks up the service in the registry
 * and creates a proxy with the appropriate configuration.
 *
 * @param serviceName - Name of the service in the registry
 * @param pathRewrite - Optional path rewrite rules
 * @returns Express middleware for proxying requests
 * @throws Error if service is not found in registry
 */
export const createProxyForService = (
  serviceName: string,
  pathRewrite?: Record<string, string>
) => {
  const service = serviceRegistry.getService(serviceName);

  if (!service) {
    throw new Error(`Service '${serviceName}' not found in registry`);
  }

  return createServiceProxy({
    name: service.name,
    target: service.url,
    pathRewrite,
    timeout: service.timeout,
  });
};

/**
 * Create proxies for multiple services
 *
 * @param serviceConfigs - Array of service proxy configurations
 * @returns Map of service names to proxy middlewares
 */
export const createMultipleProxies = (
  serviceConfigs: ServiceProxyConfig[]
): Map<string, ReturnType<typeof createServiceProxy>> => {
  const proxies = new Map();

  for (const config of serviceConfigs) {
    const proxy = createServiceProxy(config);
    proxies.set(config.name, proxy);

    logger.info(`Created proxy for ${config.name}`, {
      target: config.target,
      timeout: config.timeout,
    });
  }

  return proxies;
};

/**
 * Circuit breaker middleware wrapper
 *
 * Wraps a service proxy with circuit breaker protection.
 * If the circuit is open, requests are rejected immediately without hitting the service.
 *
 * @param serviceName - Name of the service
 * @param proxyMiddleware - The proxy middleware to wrap
 * @returns Wrapped middleware with circuit breaker
 */
export const withCircuitBreaker = (
  serviceName: string,
  proxyMiddleware: ReturnType<typeof createProxyMiddleware>
) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    const breaker = getCircuitBreaker(serviceName);

    if (!breaker) {
      // No circuit breaker configured, use proxy directly
      return proxyMiddleware(req, res, next);
    }

    // Check if circuit is open
    if (breaker.opened) {
      const correlationId = req.headers['x-correlation-id'];

      logger.warn(`Circuit breaker is open for ${serviceName}`, {
        correlationId,
        path: req.path,
        method: req.method,
      });

      return res.status(503).json({
        error: 'Service Unavailable',
        message: `${serviceName} service is temporarily unavailable due to repeated failures`,
        code: 'CIRCUIT_OPEN',
        correlationId,
        timestamp: new Date().toISOString(),
        path: req.path,
      });
    }

    // Circuit is closed or half-open, proceed with proxy
    proxyMiddleware(req, res, next);
  };
};

/**
 * Get circuit breaker health status for all services
 *
 * @returns Object with circuit breaker status for each service
 */
export const getCircuitBreakerHealth = () => {
  const health: Record<string, any> = {};

  // Get all registered services
  const services = serviceRegistry.getAllServices();

  for (const service of services) {
    const breaker = getCircuitBreaker(service.name);

    if (breaker) {
      health[service.name] = {
        state: breaker.opened
          ? 'OPEN'
          : breaker.halfOpen
            ? 'HALF_OPEN'
            : 'CLOSED',
        stats: breaker.stats,
      };
    } else {
      health[service.name] = {
        state: 'NO_BREAKER',
        message: 'Circuit breaker not configured',
      };
    }
  }

  return health;
};
