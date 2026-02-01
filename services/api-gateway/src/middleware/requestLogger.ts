import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { extractCorrelationId } from '../utils/correlationId';

/**
 * Request logger middleware
 *
 * Logs incoming requests with:
 * - Correlation ID
 * - HTTP method
 * - Request path
 * - Query parameters
 * - IP address
 * - User agent
 * - User ID (if authenticated)
 */
export const requestLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = extractCorrelationId(req);
  const startTime = Date.now();

  // Extract user ID from request (if authenticated)
  const userId = (req as any).user?.id || (req as any).user?.userId;

  // Log incoming request
  logger.info('Incoming request', {
    correlationId,
    method: req.method,
    path: req.path,
    url: req.originalUrl,
    query: Object.keys(req.query).length > 0 ? req.query : undefined,
    ip: req.ip || req.socket.remoteAddress,
    userAgent: req.headers['user-agent'],
    userId,
    timestamp: new Date().toISOString(),
  });

  // Log request body for non-GET requests (excluding sensitive data)
  if (req.method !== 'GET' && req.body && Object.keys(req.body).length > 0) {
    const sanitizedBody = sanitizeRequestBody(req.body);
    logger.debug('Request body', {
      correlationId,
      body: sanitizedBody,
    });
  }

  // Store start time for response logging
  (req as any).startTime = startTime;

  next();
};

/**
 * Sanitize request body to remove sensitive data
 *
 * @param body - Request body object
 * @returns Sanitized body object
 */
const sanitizeRequestBody = (body: any): any => {
  if (!body || typeof body !== 'object') {
    return body;
  }

  const sensitiveFields = [
    'password',
    'token',
    'secret',
    'apiKey',
    'api_key',
    'accessToken',
    'access_token',
    'refreshToken',
    'refresh_token',
    'creditCard',
    'credit_card',
    'ssn',
    'socialSecurityNumber',
  ];

  const sanitized = { ...body };

  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '***REDACTED***';
    }
  }

  // Recursively sanitize nested objects
  for (const key in sanitized) {
    if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
      sanitized[key] = sanitizeRequestBody(sanitized[key]);
    }
  }

  return sanitized;
};

/**
 * Request metadata logger middleware
 *
 * Logs additional request metadata:
 * - Content type
 * - Content length
 * - Accept header
 * - Authorization header (sanitized)
 */
export const requestMetadataLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = extractCorrelationId(req);

  const metadata: any = {
    correlationId,
    contentType: req.headers['content-type'],
    contentLength: req.headers['content-length'],
    accept: req.headers['accept'],
    referer: req.headers['referer'],
    origin: req.headers['origin'],
  };

  // Log authorization header (sanitized)
  if (req.headers['authorization']) {
    const authHeader = req.headers['authorization'];
    if (authHeader.startsWith('Bearer ')) {
      metadata.authType = 'Bearer';
      metadata.tokenPreview = authHeader.substring(7, 17) + '...';
    } else {
      metadata.authType = 'Other';
    }
  }

  logger.debug('Request metadata', metadata);

  next();
};
