import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { extractCorrelationId } from '../utils/correlationId';

/**
 * Response logger middleware
 *
 * Logs outgoing responses with:
 * - Correlation ID
 * - HTTP method
 * - Request path
 * - Status code
 * - Response time
 * - Content length
 */
export const responseLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const correlationId = extractCorrelationId(req);
  const startTime = (req as any).startTime || Date.now();

  // Capture the original res.json and res.send methods
  const originalJson = res.json.bind(res);
  const originalSend = res.send.bind(res);

  // Override res.json to log response
  res.json = function (body: any) {
    logResponse(req, res, startTime, correlationId, body);
    return originalJson(body);
  };

  // Override res.send to log response
  res.send = function (body: any) {
    logResponse(req, res, startTime, correlationId, body);
    return originalSend(body);
  };

  // Also log when response finishes (for cases where json/send aren't called)
  res.on('finish', () => {
    // Only log if we haven't already logged (json/send not called)
    if (!(res as any)._responseLogged) {
      logResponse(req, res, startTime, correlationId);
    }
  });

  next();
};

/**
 * Log response details
 *
 * @param req - Express request object
 * @param res - Express response object
 * @param startTime - Request start time
 * @param correlationId - Request correlation ID
 * @param body - Response body (optional)
 */
const logResponse = (
  req: Request,
  res: Response,
  startTime: number,
  correlationId: string | undefined,
  body?: any
) => {
  // Prevent duplicate logging
  if ((res as any)._responseLogged) {
    return;
  }
  (res as any)._responseLogged = true;

  const duration = Date.now() - startTime;
  const statusCode = res.statusCode;
  const contentLength = res.getHeader('content-length');

  // Determine log level based on status code
  const logLevel = getLogLevel(statusCode);

  // Base log data
  const logData: any = {
    correlationId,
    method: req.method,
    path: req.path,
    url: req.originalUrl,
    statusCode,
    duration,
    contentLength,
    timestamp: new Date().toISOString(),
  };

  // Add user ID if available
  const userId = (req as any).user?.id || (req as any).user?.userId;
  if (userId) {
    logData.userId = userId;
  }

  // Log response
  logger.log(logLevel, 'Outgoing response', logData);

  // Log response body for errors (4xx, 5xx)
  if (statusCode >= 400 && body) {
    logger.debug('Response body', {
      correlationId,
      statusCode,
      body: sanitizeResponseBody(body),
    });
  }

  // Log slow requests (> 1 second)
  if (duration > 1000) {
    logger.warn('Slow request detected', {
      correlationId,
      method: req.method,
      path: req.path,
      duration,
      threshold: 1000,
    });
  }
};

/**
 * Get log level based on status code
 *
 * @param statusCode - HTTP status code
 * @returns Log level string
 */
const getLogLevel = (statusCode: number): string => {
  if (statusCode >= 500) {
    return 'error';
  } else if (statusCode >= 400) {
    return 'warn';
  } else if (statusCode >= 300) {
    return 'info';
  } else {
    return 'info';
  }
};

/**
 * Sanitize response body to remove sensitive data
 *
 * @param body - Response body
 * @returns Sanitized body
 */
const sanitizeResponseBody = (body: any): any => {
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
      sanitized[key] = sanitizeResponseBody(sanitized[key]);
    }
  }

  return sanitized;
};

/**
 * Response time logger middleware
 *
 * Adds X-Response-Time header to responses
 */
export const responseTimeLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const startTime = Date.now();
  (req as any).startTime = startTime;

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    // Don't set headers after response is sent
    logger.debug('Response completed', {
      correlationId: req.headers['x-correlation-id'],
      duration: `${duration}ms`
    });
  });

  next();
};

/**
 * Status code logger middleware
 *
 * Logs status code distribution for monitoring
 */
export const statusCodeLogger = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  res.on('finish', () => {
    const correlationId = extractCorrelationId(req);
    const statusCode = res.statusCode;
    const statusCategory = Math.floor(statusCode / 100);

    logger.debug('Status code', {
      correlationId,
      statusCode,
      statusCategory: `${statusCategory}xx`,
      path: req.path,
      method: req.method,
    });
  });

  next();
};
