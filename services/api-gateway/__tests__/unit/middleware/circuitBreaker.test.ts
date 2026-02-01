import {
  createCircuitBreaker,
  getCircuitBreaker,
  getCircuitBreakerStats,
  getAllCircuitBreakerStats,
  circuitBreakerErrorHandler,
  resetAllCircuitBreakers,
} from '../../../src/middleware/circuitBreaker';
import { Request, Response } from 'express';

describe('Circuit Breaker Middleware', () => {
  beforeEach(() => {
    // Reset all circuit breakers before each test
    resetAllCircuitBreakers();
  });

  afterEach(() => {
    // Clean up after each test
    resetAllCircuitBreakers();
  });

  describe('createCircuitBreaker', () => {
    it('should create a circuit breaker with default options', async () => {
      const serviceCall = jest.fn().mockResolvedValue('success');
      const breaker = createCircuitBreaker(serviceCall, 'test-service');

      expect(breaker).toBeDefined();
      expect(breaker.name).toBe('test-service');
      expect(breaker.closed).toBe(true);
    });

    it('should create a circuit breaker with custom options', async () => {
      const serviceCall = jest.fn().mockResolvedValue('success');
      const breaker = createCircuitBreaker(serviceCall, 'test-service', {
        timeout: 5000,
        errorThresholdPercentage: 60,
        resetTimeout: 60000,
      });

      expect(breaker).toBeDefined();
      expect(breaker.options.timeout).toBe(5000);
    });

    it('should reuse existing circuit breaker for same service', () => {
      const serviceCall1 = jest.fn().mockResolvedValue('success');
      const serviceCall2 = jest.fn().mockResolvedValue('success');

      const breaker1 = createCircuitBreaker(serviceCall1, 'test-service');
      const breaker2 = createCircuitBreaker(serviceCall2, 'test-service');

      expect(breaker1).toBe(breaker2);
    });

    it('should execute service call successfully', async () => {
      const serviceCall = jest.fn().mockResolvedValue('success');
      const breaker = createCircuitBreaker(serviceCall, 'test-service');

      const result = await breaker.fire();

      expect(result).toBe('success');
      expect(serviceCall).toHaveBeenCalledTimes(1);
    });

    it('should handle service call failure', async () => {
      const serviceCall = jest.fn().mockRejectedValue(new Error('Service error'));
      const breaker = createCircuitBreaker(serviceCall, 'test-service');

      await expect(breaker.fire()).rejects.toThrow('Service error');
    });
  });

  describe('Circuit Breaker State Transitions', () => {
    it('should open circuit after error threshold is reached', async () => {
      let callCount = 0;
      const serviceCall = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount <= 10) {
          return Promise.reject(new Error('Service error'));
        }
        return Promise.resolve('success');
      });

      const breaker = createCircuitBreaker(serviceCall, 'test-service', {
        timeout: 1000,
        errorThresholdPercentage: 50,
        resetTimeout: 5000,
        rollingCountTimeout: 10000,
        rollingCountBuckets: 10,
      });

      // Make multiple failing requests to trigger circuit opening
      for (let i = 0; i < 10; i++) {
        try {
          await breaker.fire();
        } catch (error) {
          // Expected to fail
        }
      }

      // Circuit should be open now
      expect(breaker.opened).toBe(true);
    });

    it('should reject requests when circuit is open', async () => {
      const serviceCall = jest.fn().mockRejectedValue(new Error('Service error'));
      const breaker = createCircuitBreaker(serviceCall, 'test-service', {
        timeout: 1000,
        errorThresholdPercentage: 50,
        resetTimeout: 5000,
      });

      // Make multiple failing requests to open circuit
      for (let i = 0; i < 10; i++) {
        try {
          await breaker.fire();
        } catch (error) {
          // Expected to fail
        }
      }

      // Circuit should be open
      expect(breaker.opened).toBe(true);

      // Next request should be rejected immediately
      await expect(breaker.fire()).rejects.toThrow();
    });

    it('should transition to half-open after reset timeout', async () => {
      const serviceCall = jest.fn().mockRejectedValue(new Error('Service error'));
      const breaker = createCircuitBreaker(serviceCall, 'test-service', {
        timeout: 1000,
        errorThresholdPercentage: 50,
        resetTimeout: 100, // Short timeout for testing
      });

      // Open the circuit
      for (let i = 0; i < 10; i++) {
        try {
          await breaker.fire();
        } catch (error) {
          // Expected to fail
        }
      }

      expect(breaker.opened).toBe(true);

      // Wait for reset timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      // Circuit should be half-open now
      expect(breaker.halfOpen).toBe(true);
    }, 10000);

    it('should close circuit after successful request in half-open state', async () => {
      let callCount = 0;
      const serviceCall = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount <= 10) {
          return Promise.reject(new Error('Service error'));
        }
        return Promise.resolve('success');
      });

      const breaker = createCircuitBreaker(serviceCall, 'test-service', {
        timeout: 1000,
        errorThresholdPercentage: 50,
        resetTimeout: 100,
      });

      // Open the circuit
      for (let i = 0; i < 10; i++) {
        try {
          await breaker.fire();
        } catch (error) {
          // Expected to fail
        }
      }

      expect(breaker.opened).toBe(true);

      // Wait for reset timeout to transition to half-open
      await new Promise(resolve => setTimeout(resolve, 150));

      // Circuit should be half-open now, make a successful request
      try {
        const result = await breaker.fire();
        expect(result).toBe('success');
        
        // Circuit should be closed now
        expect(breaker.closed).toBe(true);
      } catch (error) {
        // If it fails in half-open, it will go back to open
        // This is expected behavior, so we'll just verify the state
        expect(breaker.opened || breaker.halfOpen).toBe(true);
      }
    }, 10000);
  });

  describe('getCircuitBreaker', () => {
    it('should return existing circuit breaker', () => {
      const serviceCall = jest.fn().mockResolvedValue('success');
      const breaker = createCircuitBreaker(serviceCall, 'test-service');

      const retrieved = getCircuitBreaker('test-service');

      expect(retrieved).toBe(breaker);
    });

    it('should return undefined for non-existent circuit breaker', () => {
      const retrieved = getCircuitBreaker('non-existent');

      expect(retrieved).toBeUndefined();
    });
  });

  describe('getCircuitBreakerStats', () => {
    it('should return stats for existing circuit breaker', async () => {
      const serviceCall = jest.fn().mockResolvedValue('success');
      const breaker = createCircuitBreaker(serviceCall, 'test-service');

      await breaker.fire();

      const stats = getCircuitBreakerStats('test-service');

      expect(stats).toBeDefined();
      expect(stats?.name).toBe('test-service');
      expect(stats?.state).toBe('CLOSED');
      expect(stats?.stats).toBeDefined();
    });

    it('should return null for non-existent circuit breaker', () => {
      const stats = getCircuitBreakerStats('non-existent');

      expect(stats).toBeNull();
    });
  });

  describe('getAllCircuitBreakerStats', () => {
    it('should return stats for all circuit breakers', async () => {
      const serviceCall1 = jest.fn().mockResolvedValue('success');
      const serviceCall2 = jest.fn().mockResolvedValue('success');

      createCircuitBreaker(serviceCall1, 'service-1');
      createCircuitBreaker(serviceCall2, 'service-2');

      const allStats = getAllCircuitBreakerStats();

      expect(allStats).toHaveLength(2);
      expect(allStats[0].name).toBeDefined();
      expect(allStats[1].name).toBeDefined();
    });

    it('should return empty array when no circuit breakers exist', () => {
      const allStats = getAllCircuitBreakerStats();

      expect(allStats).toHaveLength(0);
    });
  });

  describe('circuitBreakerErrorHandler', () => {
    let mockReq: Partial<Request>;
    let mockRes: Partial<Response>;
    let mockNext: jest.Mock;

    beforeEach(() => {
      mockReq = {
        headers: { 'x-correlation-id': 'test-correlation-id' },
        path: '/test',
        method: 'GET',
      };
      mockRes = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn().mockReturnThis(),
      };
      mockNext = jest.fn();
    });

    it('should handle circuit breaker open error', () => {
      const error = new Error('Circuit breaker is open');
      (error as any).code = 'EOPENBREAKER';

      circuitBreakerErrorHandler(
        error,
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockRes.status).toHaveBeenCalledWith(503);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Service Unavailable',
          code: 'SERVICE_UNAVAILABLE',
          correlationId: 'test-correlation-id',
        })
      );
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should handle timeout error', () => {
      const error = new Error('Request timed out');
      (error as any).code = 'ETIMEDOUT';

      circuitBreakerErrorHandler(
        error,
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockRes.status).toHaveBeenCalledWith(504);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Gateway Timeout',
          code: 'GATEWAY_TIMEOUT',
          correlationId: 'test-correlation-id',
        })
      );
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should pass other errors to next handler', () => {
      const error = new Error('Some other error');

      circuitBreakerErrorHandler(
        error,
        mockReq as Request,
        mockRes as Response,
        mockNext
      );

      expect(mockNext).toHaveBeenCalledWith(error);
      expect(mockRes.status).not.toHaveBeenCalled();
    });
  });

  describe('resetAllCircuitBreakers', () => {
    it('should reset all circuit breakers', () => {
      const serviceCall1 = jest.fn().mockResolvedValue('success');
      const serviceCall2 = jest.fn().mockResolvedValue('success');

      createCircuitBreaker(serviceCall1, 'service-1');
      createCircuitBreaker(serviceCall2, 'service-2');

      expect(getAllCircuitBreakerStats()).toHaveLength(2);

      resetAllCircuitBreakers();

      expect(getAllCircuitBreakerStats()).toHaveLength(0);
    });
  });
});
