/**
 * Error codes for API Gateway
 *
 * These codes provide consistent error identification across the API
 */

export enum ErrorCode {
  // General errors (1xxx)
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',

  // Validation errors (2xxx)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_REQUEST = 'INVALID_REQUEST',
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD',
  INVALID_FORMAT = 'INVALID_FORMAT',

  // Authentication errors (3xxx)
  UNAUTHORIZED = 'UNAUTHORIZED',
  INVALID_TOKEN = 'INVALID_TOKEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  MISSING_TOKEN = 'MISSING_TOKEN',

  // Authorization errors (4xxx)
  FORBIDDEN = 'FORBIDDEN',
  INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS',

  // Resource errors (5xxx)
  NOT_FOUND = 'NOT_FOUND',
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RESOURCE_ALREADY_EXISTS = 'RESOURCE_ALREADY_EXISTS',

  // Rate limiting errors (6xxx)
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  TOO_MANY_REQUESTS = 'TOO_MANY_REQUESTS',

  // Service errors (7xxx)
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  CIRCUIT_BREAKER_OPEN = 'CIRCUIT_BREAKER_OPEN',
  SERVICE_TIMEOUT = 'SERVICE_TIMEOUT',
  PROXY_ERROR = 'PROXY_ERROR',

  // External service errors (8xxx)
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  UPSTREAM_ERROR = 'UPSTREAM_ERROR',
}

/**
 * Map HTTP status codes to error codes
 */
export const statusCodeToErrorCode: Record<number, ErrorCode> = {
  400: ErrorCode.INVALID_REQUEST,
  401: ErrorCode.UNAUTHORIZED,
  403: ErrorCode.FORBIDDEN,
  404: ErrorCode.NOT_FOUND,
  409: ErrorCode.CONFLICT,
  429: ErrorCode.RATE_LIMIT_EXCEEDED,
  500: ErrorCode.INTERNAL_ERROR,
  502: ErrorCode.UPSTREAM_ERROR,
  503: ErrorCode.SERVICE_UNAVAILABLE,
  504: ErrorCode.SERVICE_TIMEOUT,
};

/**
 * Get error code from HTTP status code
 *
 * @param statusCode - HTTP status code
 * @returns Error code
 */
export const getErrorCodeFromStatus = (statusCode: number): ErrorCode => {
  return statusCodeToErrorCode[statusCode] || ErrorCode.UNKNOWN_ERROR;
};

/**
 * Check if error is retryable based on error code
 *
 * @param code - Error code
 * @returns True if error is retryable
 */
export const isRetryableError = (code: ErrorCode): boolean => {
  const retryableCodes = [
    ErrorCode.SERVICE_UNAVAILABLE,
    ErrorCode.SERVICE_TIMEOUT,
    ErrorCode.CIRCUIT_BREAKER_OPEN,
    ErrorCode.UPSTREAM_ERROR,
  ];

  return retryableCodes.includes(code);
};
