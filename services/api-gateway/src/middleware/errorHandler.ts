import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import {
  ErrorCode,
  getErrorCodeFromStatus,
  isRetryableError,
} from '../utils/errorCodes';
import { extractCorrelationId } from '../utils/correlationId';

/**
 * Extended Error interface with additional API Gateway properties
 */
export interface ApiError extends Error {
  statusCode?: number;
  code?: string;
  errorCode?: ErrorCode;
  retryable?: boolean;
  details?: any;
}

/**
 * Standardized error response format
 */
export interface ErrorResponse {
  error: string;
  message: string;
  code: string;
  correlationId: string;
  timestamp: string;
  path: string;
  retryable: boolean;
  details?: any;
  stack?: string;
}

/**
 * Enhanced error handler middleware
 *
 * Features:
 * - Standardized error response format
 * - Error codes for different error types
 * - Correlation ID in error responses
 * - Stack traces hidden in production
 * - Comprehensive error logging
 *
 * @param error - Error object
 * @param req - Express request
 * @param res - Express response
 * @param next - Express next function
 */
export const errorHandler = (
  error: ApiError,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  // Extract correlation ID from request
  const correlationId = extractCorrelationId(req) || 'unknown';

  // Determine status code
  const statusCode = error.statusCode || 500;

  // Determine error code
  let errorCode: ErrorCode;
  if (error.errorCode) {
    errorCode = error.errorCode;
  } else if (error.code) {
    errorCode = error.code as ErrorCode;
  } else {
    errorCode = getErrorCodeFromStatus(statusCode);
  }

  // Determine if error is retryable
  const retryable =
    error.retryable !== undefined
      ? error.retryable
      : isRetryableError(errorCode);

  // Log error with full context
  logger.error('API Gateway Error:', {
    correlationId,
    error: error.message,
    errorCode,
    statusCode,
    stack: error.stack,
    url: req.url,
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
    retryable,
    details: error.details,
  });

  // Build standardized error response
  const errorResponse: ErrorResponse = {
    error: errorCode,
    message: error.message || 'An unexpected error occurred',
    code: errorCode,
    correlationId,
    timestamp: new Date().toISOString(),
    path: req.path,
    retryable,
  };

  // Add details if present
  if (error.details) {
    errorResponse.details = error.details;
  }

  // Include stack trace only in development mode
  const isProduction =
    process.env.NODE_ENV === 'production' || !process.env.NODE_ENV;
  if (!isProduction && error.stack) {
    errorResponse.stack = error.stack;
  }

  // Send error response
  res.status(statusCode).json(errorResponse);
};

/**
 * Create a standardized API error
 *
 * @param message - Error message
 * @param statusCode - HTTP status code
 * @param errorCode - Error code
 * @param details - Additional error details
 * @returns ApiError instance
 */
export const createApiError = (
  message: string,
  statusCode: number = 500,
  errorCode?: ErrorCode,
  details?: any
): ApiError => {
  const error = new Error(message) as ApiError;
  error.statusCode = statusCode;
  error.errorCode = errorCode || getErrorCodeFromStatus(statusCode);
  error.details = details;
  error.retryable = isRetryableError(error.errorCode);

  return error;
};

/**
 * Create a validation error
 *
 * @param message - Error message
 * @param details - Validation error details
 * @returns ApiError instance
 */
export const createValidationError = (
  message: string,
  details?: any
): ApiError => {
  return createApiError(message, 400, ErrorCode.VALIDATION_ERROR, details);
};

/**
 * Create an unauthorized error
 *
 * @param message - Error message
 * @returns ApiError instance
 */
export const createUnauthorizedError = (
  message: string = 'Unauthorized'
): ApiError => {
  return createApiError(message, 401, ErrorCode.UNAUTHORIZED);
};

/**
 * Create a forbidden error
 *
 * @param message - Error message
 * @returns ApiError instance
 */
export const createForbiddenError = (
  message: string = 'Forbidden'
): ApiError => {
  return createApiError(message, 403, ErrorCode.FORBIDDEN);
};

/**
 * Create a not found error
 *
 * @param message - Error message
 * @param resource - Resource type
 * @returns ApiError instance
 */
export const createNotFoundError = (
  message: string = 'Resource not found',
  resource?: string
): ApiError => {
  return createApiError(
    message,
    404,
    ErrorCode.NOT_FOUND,
    resource ? { resource } : undefined
  );
};

/**
 * Create a rate limit error
 *
 * @param message - Error message
 * @param retryAfter - Seconds until retry is allowed
 * @returns ApiError instance
 */
export const createRateLimitError = (
  message: string = 'Too many requests',
  retryAfter?: number
): ApiError => {
  return createApiError(
    message,
    429,
    ErrorCode.RATE_LIMIT_EXCEEDED,
    retryAfter ? { retryAfter } : undefined
  );
};

/**
 * Create a service unavailable error
 *
 * @param message - Error message
 * @param serviceName - Name of unavailable service
 * @returns ApiError instance
 */
export const createServiceUnavailableError = (
  message: string = 'Service unavailable',
  serviceName?: string
): ApiError => {
  return createApiError(
    message,
    503,
    ErrorCode.SERVICE_UNAVAILABLE,
    serviceName ? { service: serviceName } : undefined
  );
};
