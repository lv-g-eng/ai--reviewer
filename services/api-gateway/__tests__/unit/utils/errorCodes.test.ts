import {
  ErrorCode,
  getErrorCodeFromStatus,
  isRetryableError,
  statusCodeToErrorCode,
} from '../../../src/utils/errorCodes';

describe('Error Codes Utility', () => {
  describe('ErrorCode enum', () => {
    it('should have all required error codes', () => {
      expect(ErrorCode.INTERNAL_ERROR).toBe('INTERNAL_ERROR');
      expect(ErrorCode.VALIDATION_ERROR).toBe('VALIDATION_ERROR');
      expect(ErrorCode.UNAUTHORIZED).toBe('UNAUTHORIZED');
      expect(ErrorCode.FORBIDDEN).toBe('FORBIDDEN');
      expect(ErrorCode.NOT_FOUND).toBe('NOT_FOUND');
      expect(ErrorCode.RATE_LIMIT_EXCEEDED).toBe('RATE_LIMIT_EXCEEDED');
      expect(ErrorCode.SERVICE_UNAVAILABLE).toBe('SERVICE_UNAVAILABLE');
      expect(ErrorCode.CIRCUIT_BREAKER_OPEN).toBe('CIRCUIT_BREAKER_OPEN');
    });
  });

  describe('statusCodeToErrorCode mapping', () => {
    it('should map 400 to INVALID_REQUEST', () => {
      expect(statusCodeToErrorCode[400]).toBe(ErrorCode.INVALID_REQUEST);
    });

    it('should map 401 to UNAUTHORIZED', () => {
      expect(statusCodeToErrorCode[401]).toBe(ErrorCode.UNAUTHORIZED);
    });

    it('should map 403 to FORBIDDEN', () => {
      expect(statusCodeToErrorCode[403]).toBe(ErrorCode.FORBIDDEN);
    });

    it('should map 404 to NOT_FOUND', () => {
      expect(statusCodeToErrorCode[404]).toBe(ErrorCode.NOT_FOUND);
    });

    it('should map 409 to CONFLICT', () => {
      expect(statusCodeToErrorCode[409]).toBe(ErrorCode.CONFLICT);
    });

    it('should map 429 to RATE_LIMIT_EXCEEDED', () => {
      expect(statusCodeToErrorCode[429]).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
    });

    it('should map 500 to INTERNAL_ERROR', () => {
      expect(statusCodeToErrorCode[500]).toBe(ErrorCode.INTERNAL_ERROR);
    });

    it('should map 502 to UPSTREAM_ERROR', () => {
      expect(statusCodeToErrorCode[502]).toBe(ErrorCode.UPSTREAM_ERROR);
    });

    it('should map 503 to SERVICE_UNAVAILABLE', () => {
      expect(statusCodeToErrorCode[503]).toBe(ErrorCode.SERVICE_UNAVAILABLE);
    });

    it('should map 504 to SERVICE_TIMEOUT', () => {
      expect(statusCodeToErrorCode[504]).toBe(ErrorCode.SERVICE_TIMEOUT);
    });
  });

  describe('getErrorCodeFromStatus', () => {
    it('should return correct error code for known status codes', () => {
      expect(getErrorCodeFromStatus(400)).toBe(ErrorCode.INVALID_REQUEST);
      expect(getErrorCodeFromStatus(401)).toBe(ErrorCode.UNAUTHORIZED);
      expect(getErrorCodeFromStatus(404)).toBe(ErrorCode.NOT_FOUND);
      expect(getErrorCodeFromStatus(500)).toBe(ErrorCode.INTERNAL_ERROR);
      expect(getErrorCodeFromStatus(503)).toBe(ErrorCode.SERVICE_UNAVAILABLE);
    });

    it('should return UNKNOWN_ERROR for unmapped status codes', () => {
      expect(getErrorCodeFromStatus(418)).toBe(ErrorCode.UNKNOWN_ERROR); // I'm a teapot
      expect(getErrorCodeFromStatus(999)).toBe(ErrorCode.UNKNOWN_ERROR);
      expect(getErrorCodeFromStatus(200)).toBe(ErrorCode.UNKNOWN_ERROR); // Success code
    });

    it('should handle edge cases', () => {
      expect(getErrorCodeFromStatus(0)).toBe(ErrorCode.UNKNOWN_ERROR);
      expect(getErrorCodeFromStatus(-1)).toBe(ErrorCode.UNKNOWN_ERROR);
      expect(getErrorCodeFromStatus(1000)).toBe(ErrorCode.UNKNOWN_ERROR);
    });
  });

  describe('isRetryableError', () => {
    it('should return true for retryable error codes', () => {
      expect(isRetryableError(ErrorCode.SERVICE_UNAVAILABLE)).toBe(true);
      expect(isRetryableError(ErrorCode.SERVICE_TIMEOUT)).toBe(true);
      expect(isRetryableError(ErrorCode.CIRCUIT_BREAKER_OPEN)).toBe(true);
      expect(isRetryableError(ErrorCode.UPSTREAM_ERROR)).toBe(true);
    });

    it('should return false for non-retryable error codes', () => {
      expect(isRetryableError(ErrorCode.VALIDATION_ERROR)).toBe(false);
      expect(isRetryableError(ErrorCode.UNAUTHORIZED)).toBe(false);
      expect(isRetryableError(ErrorCode.FORBIDDEN)).toBe(false);
      expect(isRetryableError(ErrorCode.NOT_FOUND)).toBe(false);
      expect(isRetryableError(ErrorCode.RATE_LIMIT_EXCEEDED)).toBe(false);
      expect(isRetryableError(ErrorCode.INTERNAL_ERROR)).toBe(false);
    });

    it('should handle all error codes consistently', () => {
      // Test that function doesn't throw for any error code
      Object.values(ErrorCode).forEach((code) => {
        expect(() => isRetryableError(code)).not.toThrow();
        expect(typeof isRetryableError(code)).toBe('boolean');
      });
    });
  });

  describe('Error code categories', () => {
    it('should have general error codes (1xxx)', () => {
      expect(ErrorCode.INTERNAL_ERROR).toBeDefined();
      expect(ErrorCode.UNKNOWN_ERROR).toBeDefined();
    });

    it('should have validation error codes (2xxx)', () => {
      expect(ErrorCode.VALIDATION_ERROR).toBeDefined();
      expect(ErrorCode.INVALID_REQUEST).toBeDefined();
      expect(ErrorCode.MISSING_REQUIRED_FIELD).toBeDefined();
      expect(ErrorCode.INVALID_FORMAT).toBeDefined();
    });

    it('should have authentication error codes (3xxx)', () => {
      expect(ErrorCode.UNAUTHORIZED).toBeDefined();
      expect(ErrorCode.INVALID_TOKEN).toBeDefined();
      expect(ErrorCode.TOKEN_EXPIRED).toBeDefined();
      expect(ErrorCode.MISSING_TOKEN).toBeDefined();
    });

    it('should have authorization error codes (4xxx)', () => {
      expect(ErrorCode.FORBIDDEN).toBeDefined();
      expect(ErrorCode.INSUFFICIENT_PERMISSIONS).toBeDefined();
    });

    it('should have resource error codes (5xxx)', () => {
      expect(ErrorCode.NOT_FOUND).toBeDefined();
      expect(ErrorCode.RESOURCE_NOT_FOUND).toBeDefined();
      expect(ErrorCode.CONFLICT).toBeDefined();
      expect(ErrorCode.RESOURCE_ALREADY_EXISTS).toBeDefined();
    });

    it('should have rate limiting error codes (6xxx)', () => {
      expect(ErrorCode.RATE_LIMIT_EXCEEDED).toBeDefined();
      expect(ErrorCode.TOO_MANY_REQUESTS).toBeDefined();
    });

    it('should have service error codes (7xxx)', () => {
      expect(ErrorCode.SERVICE_UNAVAILABLE).toBeDefined();
      expect(ErrorCode.CIRCUIT_BREAKER_OPEN).toBeDefined();
      expect(ErrorCode.SERVICE_TIMEOUT).toBeDefined();
      expect(ErrorCode.PROXY_ERROR).toBeDefined();
    });

    it('should have external service error codes (8xxx)', () => {
      expect(ErrorCode.EXTERNAL_SERVICE_ERROR).toBeDefined();
      expect(ErrorCode.UPSTREAM_ERROR).toBeDefined();
    });
  });
});
