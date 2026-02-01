import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';
import { config } from '../config';
import { logger } from '../utils/logger';

/**
 * Create a Redis client with standard configuration
 */
const createRedisClient = (clientName: string = 'rate-limiter') => {
  const redis = new Redis(config.redis.url, {
    enableOfflineQueue: false,
    maxRetriesPerRequest: 3,
    retryStrategy: (times: number) => {
      if (times > 3) {
        logger.error(
          `Redis connection failed after 3 retries for ${clientName}`
        );
        return null; // Stop retrying
      }
      return Math.min(times * 100, 3000); // Exponential backoff
    },
  });

  // Handle Redis connection events
  redis.on('connect', () => {
    logger.info(`Redis connected for ${clientName}`);
  });

  redis.on('error', (err) => {
    logger.error(`Redis connection error for ${clientName}:`, err);
  });

  redis.on('close', () => {
    logger.warn(`Redis connection closed for ${clientName}`);
  });

  return redis;
};

/**
 * API Rate Limiter
 * Limits general API requests to 100 per minute per user/IP
 */
export const apiLimiter = rateLimit({
  store: new RedisStore({
    // @ts-expect-error - RedisStore types are not fully compatible with ioredis
    client: createRedisClient('api-rate-limiter'),
    prefix: 'rl:api:',
  }),
  windowMs: 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  message: {
    error: 'Too many requests',
    message: 'You have exceeded the rate limit. Please try again later.',
    retryAfter: 60,
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  skip: (req) => {
    // Skip rate limiting for health check endpoint
    return req.path === '/health';
  },
  keyGenerator: (req) => {
    // Use user ID if authenticated, otherwise use IP address
    const userId = (req as any).user?.id;
    return userId ? `user:${userId}` : `ip:${req.ip}`;
  },
  handler: (req, res) => {
    logger.warn('Rate limit exceeded', {
      ip: req.ip,
      path: req.path,
      userId: (req as any).user?.id,
    });
    res.status(429).json({
      error: 'Too many requests',
      message: 'You have exceeded the rate limit. Please try again later.',
      retryAfter: 60,
    });
  },
});

/**
 * Authentication Rate Limiter
 * Limits authentication requests to 5 per 15 minutes
 * More restrictive to prevent brute force attacks
 */
export const authLimiter = rateLimit({
  store: new RedisStore({
    // @ts-expect-error - RedisStore types are not fully compatible with ioredis
    client: createRedisClient('auth-rate-limiter'),
    prefix: 'rl:auth:',
  }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per 15 minutes
  message: {
    error: 'Too many authentication attempts',
    message:
      'You have exceeded the authentication rate limit. Please try again in 15 minutes.',
    retryAfter: 900,
  },
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: true, // Don't count successful requests
  keyGenerator: (req) => {
    // Use IP address for auth rate limiting
    return `auth:${req.ip}`;
  },
  handler: (req, res) => {
    logger.warn('Auth rate limit exceeded', {
      ip: req.ip,
      path: req.path,
    });
    res.status(429).json({
      error: 'Too many authentication attempts',
      message:
        'You have exceeded the authentication rate limit. Please try again in 15 minutes.',
      retryAfter: 900,
    });
  },
});

/**
 * Custom rate limiter factory
 * Creates a rate limiter with custom configuration
 */
export const createRateLimiter = (options: {
  windowMs: number;
  max: number;
  prefix: string;
  message?: string;
}) => {
  // Create a unique Redis client for this rate limiter to avoid store reuse
  const redisClient = createRedisClient(
    `custom-rate-limiter-${options.prefix.replace(/[^a-zA-Z0-9]/g, '-')}`
  );

  return rateLimit({
    store: new RedisStore({
      // @ts-expect-error - RedisStore types are not fully compatible with ioredis
      client: redisClient,
      prefix: options.prefix,
    }),
    windowMs: options.windowMs,
    max: options.max,
    message: {
      error: 'Too many requests',
      message: options.message || 'Rate limit exceeded',
      retryAfter: Math.floor(options.windowMs / 1000),
    },
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req) => {
      const userId = (req as any).user?.id;
      return userId ? `user:${userId}` : `ip:${req.ip}`;
    },
  });
};

// Export the createRedisClient function for testing and cleanup
export { createRedisClient };
