import { v4 as uuidv4 } from 'uuid';
import { Request, Response, NextFunction } from 'express';

/**
 * Correlation ID header name
 */
export const CORRELATION_ID_HEADER = 'x-correlation-id';

/**
 * Generate a new correlation ID
 *
 * @returns UUID v4 string
 */
export const generateCorrelationId = (): string => {
  return uuidv4();
};

/**
 * Get correlation ID from request headers or generate a new one
 *
 * @param req - Express request object
 * @returns Correlation ID string
 */
export const getOrCreateCorrelationId = (req: Request): string => {
  const existingId = req.headers[CORRELATION_ID_HEADER];

  if (existingId && typeof existingId === 'string') {
    return existingId;
  }

  return generateCorrelationId();
};

/**
 * Express middleware to add correlation ID to requests
 *
 * This middleware:
 * 1. Checks if request already has a correlation ID
 * 2. Generates a new one if not present
 * 3. Adds it to request headers
 * 4. Adds it to response headers
 */
export const correlationIdMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Get or create correlation ID
  const correlationId = getOrCreateCorrelationId(req);

  // Add to request headers
  req.headers[CORRELATION_ID_HEADER] = correlationId;

  // Add to response headers
  res.setHeader(CORRELATION_ID_HEADER, correlationId);

  next();
};

/**
 * Extract correlation ID from request
 *
 * @param req - Express request object
 * @returns Correlation ID string or undefined
 */
export const extractCorrelationId = (req: Request): string | undefined => {
  const id = req.headers[CORRELATION_ID_HEADER];
  return typeof id === 'string' ? id : undefined;
};
