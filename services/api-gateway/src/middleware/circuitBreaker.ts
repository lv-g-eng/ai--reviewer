import CircuitBreaker from 'opossum';
import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

/**
 * Circuit Breaker Options
 */
export interface CircuitBreakerOptions {
  timeout: number; // Request timeout in ms
  errorThresholdPercentage: number; // Error rate to open circuit (%)
  resetTimeout: number; // Time before attempting half-open (ms)
  rollingCountTimeout: number; // Time window for error calculation (ms)
  rollingCountBuckets: number; // Number of buckets in rolling window
  name: string; // Circuit breaker name for logging
}

/**
 * Default circuit breaker options
 */
const defaultOptions: Omit<CircuitBreakerOptions, 'name'> = {
  timeout: 3000, // 3 seconds
  errorThresholdPercentage: 50, // 50% error rate
  resetTimeout: 30000, // 30 seconds
  rollingCountTimeout: 10000, // 10 seconds
  rollingCountBuckets: 10, // 10 buckets
};

/**
 * Circuit breaker registry to store breakers by service name
 */
const circuitBreakers = new Map<string, CircuitBreaker>();

/**
 * Create a circuit breaker for a service
 *
 * @param serviceCall - The function to wrap with circuit breaker
 * @param serviceName - Name of the service for logging
 * @param options - Circuit breaker configuration options
 * @returns Circuit breaker instance
 */
export const createCircuitBreaker = <T extends any[], R>(
  serviceCall: (...args: T) => Promise<R>,
  serviceName: string,
  options: Partial<CircuitBreakerOptions> = {}
): CircuitBreaker<T, R> => {
  // Check if breaker already exists
  if (circuitBreakers.has(serviceName)) {
    return circuitBreakers.get(serviceName) as CircuitBreaker<T, R>;
  }

  const breakerOptions = {
    ...defaultOptions,
    name: serviceName,
    ...options,
  };

  const breaker = new CircuitBreaker<T, R>(serviceCall, breakerOptions);

  // Event: Circuit opened (too many failures)
  breaker.on('open', () => {
    logger.error(`Circuit breaker OPENED for ${serviceName}`, {
      service: serviceName,
      state: 'OPEN',
      errorThreshold: breakerOptions.errorThresholdPercentage,
    });
  });

  // Event: Circuit half-opened (testing if service recovered)
  breaker.on('halfOpen', () => {
    logger.warn(`Circuit breaker HALF-OPEN for ${serviceName}`, {
      service: serviceName,
      state: 'HALF_OPEN',
    });
  });

  // Event: Circuit closed (service recovered)
  breaker.on('close', () => {
    logger.info(`Circuit breaker CLOSED for ${serviceName}`, {
      service: serviceName,
      state: 'CLOSED',
    });
  });

  // Event: Request succeeded
  breaker.on('success', (_result) => {
    logger.debug(`Circuit breaker success for ${serviceName}`, {
      service: serviceName,
      state: breaker.opened
        ? 'OPEN'
        : breaker.halfOpen
          ? 'HALF_OPEN'
          : 'CLOSED',
    });
  });

  // Event: Request failed
  breaker.on('failure', (error) => {
    logger.error(`Circuit breaker failure for ${serviceName}`, {
      service: serviceName,
      state: breaker.opened
        ? 'OPEN'
        : breaker.halfOpen
          ? 'HALF_OPEN'
          : 'CLOSED',
      error: error.message,
    });
  });

  // Event: Request timed out
  breaker.on('timeout', () => {
    logger.error(`Circuit breaker timeout for ${serviceName}`, {
      service: serviceName,
      timeout: breakerOptions.timeout,
    });
  });

  // Event: Circuit rejected request (circuit is open)
  breaker.on('reject', () => {
    logger.warn(`Circuit breaker rejected request for ${serviceName}`, {
      service: serviceName,
      state: 'OPEN',
      message: 'Service is currently unavailable',
    });
  });

  // Event: Fallback executed
  breaker.on('fallback', (_result) => {
    logger.info(`Circuit breaker fallback executed for ${serviceName}`, {
      service: serviceName,
    });
  });

  // Store breaker in registry
  circuitBreakers.set(serviceName, breaker);

  return breaker;
};

/**
 * Get an existing circuit breaker by service name
 *
 * @param serviceName - Name of the service
 * @returns Circuit breaker instance or undefined
 */
export const getCircuitBreaker = (
  serviceName: string
): CircuitBreaker | undefined => {
  return circuitBreakers.get(serviceName);
};

/**
 * Get circuit breaker stats for a service
 *
 * @param serviceName - Name of the service
 * @returns Circuit breaker statistics
 */
export const getCircuitBreakerStats = (serviceName: string) => {
  const breaker = circuitBreakers.get(serviceName);
  if (!breaker) {
    return null;
  }

  return {
    name: serviceName,
    state: breaker.opened ? 'OPEN' : breaker.halfOpen ? 'HALF_OPEN' : 'CLOSED',
    stats: breaker.stats,
  };
};

/**
 * Get all circuit breaker stats
 *
 * @returns Array of circuit breaker statistics
 */
export const getAllCircuitBreakerStats = () => {
  const stats: any[] = [];
  circuitBreakers.forEach((breaker, serviceName) => {
    stats.push({
      name: serviceName,
      state: breaker.opened
        ? 'OPEN'
        : breaker.halfOpen
          ? 'HALF_OPEN'
          : 'CLOSED',
      stats: breaker.stats,
    });
  });
  return stats;
};

/**
 * Express middleware to handle circuit breaker errors
 *
 * This middleware catches circuit breaker errors and returns appropriate responses
 */
export const circuitBreakerErrorHandler = (
  err: any,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Check if error is from circuit breaker
  if (err.code === 'EOPENBREAKER') {
    const correlationId = req.headers['x-correlation-id'];

    logger.error('Circuit breaker is open', {
      correlationId,
      path: req.path,
      method: req.method,
    });

    return res.status(503).json({
      error: 'Service Unavailable',
      message:
        'The requested service is temporarily unavailable. Please try again later.',
      code: 'SERVICE_UNAVAILABLE',
      correlationId,
      timestamp: new Date().toISOString(),
      path: req.path,
    });
  }

  // Check if error is from timeout
  if (err.code === 'ETIMEDOUT' || err.message?.includes('timed out')) {
    const correlationId = req.headers['x-correlation-id'];

    logger.error('Request timeout', {
      correlationId,
      path: req.path,
      method: req.method,
    });

    return res.status(504).json({
      error: 'Gateway Timeout',
      message: 'The request took too long to process. Please try again.',
      code: 'GATEWAY_TIMEOUT',
      correlationId,
      timestamp: new Date().toISOString(),
      path: req.path,
    });
  }

  // Pass to next error handler
  next(err);
};

/**
 * Reset all circuit breakers (useful for testing)
 */
export const resetAllCircuitBreakers = () => {
  circuitBreakers.forEach((breaker) => {
    breaker.close();
  });
  circuitBreakers.clear();
};
