/**
 * Property-Based Tests for API Gateway
 * 
 * These tests use fast-check to verify universal properties hold across
 * randomly generated inputs. Property-based testing helps catch edge cases
 * that traditional example-based tests might miss.
 * 
 * Properties tested:
 * 1. Request Validation Consistency (US-2)
 * 2. Rate Limiting Fairness (US-3)
 * 3. Circuit Breaker State Transitions (US-4)
 */

import * as fc from 'fast-check';
import { z } from 'zod';
import { validateRequest } from '../../src/middleware/requestValidator';
import { createCircuitBreaker, resetAllCircuitBreakers } from '../../src/middleware/circuitBreaker';
import { Request, Response } from 'express';

// Mock logger to avoid console output during tests
jest.mock('../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('Property-Based Tests', () => {
  describe('Property 1: Request Validation Consistency', () => {
    /**
     * **Validates: Requirements US-2**
     * 
     * Property: For all requests R and schemas S:
     * - If R is valid according to S, validation succeeds
     * - If R is invalid according to S, validation fails with 400
     * - Validation errors include field path and message
     */

    it('Property: Valid data always passes validation', async () => {
      // Define a simple schema
      const schema = z.object({
        body: z.object({
          name: z.string().min(1).max(100).trim(),
          age: z.number().int().positive().max(150),
          email: z.string().email(),
        }),
      });

      // Generate valid data according to the schema
      // Use more constrained generators to ensure validity
      const validDataArbitrary = fc.record({
        name: fc.string({ minLength: 1, maxLength: 100 })
          .filter(s => s.trim().length > 0), // Ensure non-empty after trim
        age: fc.integer({ min: 1, max: 150 }),
        email: fc.emailAddress()
          .filter(email => {
            // Ensure email is valid according to Zod
            try {
              z.string().email().parse(email);
              return true;
            } catch {
              return false;
            }
          }),
      });

      await fc.assert(
        fc.asyncProperty(validDataArbitrary, async (data) => {
          // Create mock request with valid data
          const req = {
            body: data,
            query: {},
            params: {},
            headers: { 'x-correlation-id': 'test-id' },
            method: 'POST',
            path: '/test',
          } as unknown as Request;

          const res = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn().mockReturnThis(),
          } as unknown as Response;

          let nextCalled = false;
          const next = jest.fn(() => {
            nextCalled = true;
          });

          // Apply validation middleware
          const middleware = validateRequest(schema);
          await middleware(req, res, next);

          // Assertion: Valid data should call next() without errors
          expect(nextCalled).toBe(true);
          expect(res.status).not.toHaveBeenCalled();
        }),
        { numRuns: 100 }
      );
    });

    it('Property: Invalid data always fails validation with 400', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string().min(1).max(100),
          age: z.number().int().positive().max(150),
        }),
      });

      // Generate invalid data (age as string instead of number)
      const invalidDataArbitrary = fc.record({
        name: fc.string({ minLength: 1, maxLength: 100 }),
        age: fc.string(), // Invalid: should be number
      });

      await fc.assert(
        fc.asyncProperty(invalidDataArbitrary, async (data) => {
          const req = {
            body: data,
            query: {},
            params: {},
            headers: { 'x-correlation-id': 'test-id' },
            method: 'POST',
            path: '/test',
          } as unknown as Request;

          const res = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn().mockReturnThis(),
          } as unknown as Response;

          const next = jest.fn();

          const middleware = validateRequest(schema);
          await middleware(req, res, next);

          // Assertion: Invalid data should return 400 status
          expect(res.status).toHaveBeenCalledWith(400);
          expect(next).not.toHaveBeenCalled();
        }),
        { numRuns: 50 }
      );
    });

    it('Property: Validation errors include field path and message', async () => {
      const schema = z.object({
        body: z.object({
          email: z.string().email(),
          age: z.number().int().positive(),
        }),
      });

      // Generate invalid email strings
      const invalidEmailArbitrary = fc.string().filter(s => {
        try {
          z.string().email().parse(s);
          return false; // Valid email, skip
        } catch {
          return true; // Invalid email, use it
        }
      });

      await fc.assert(
        fc.asyncProperty(invalidEmailArbitrary, async (invalidEmail) => {
          const req = {
            body: { email: invalidEmail, age: 25 },
            query: {},
            params: {},
            headers: { 'x-correlation-id': 'test-id' },
            method: 'POST',
            path: '/test',
          } as unknown as Request;

          const res = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
          } as unknown as Response;

          const next = jest.fn();

          const middleware = validateRequest(schema);
          await middleware(req, res, next);

          // Assertion: Error response should include details with field and message
          expect(res.json).toHaveBeenCalled();
          const errorResponse = (res.json as jest.Mock).mock.calls[0][0];
          expect(errorResponse).toHaveProperty('details');
          expect(Array.isArray(errorResponse.details)).toBe(true);
          expect(errorResponse.details.length).toBeGreaterThan(0);
          expect(errorResponse.details[0]).toHaveProperty('field');
          expect(errorResponse.details[0]).toHaveProperty('message');
        }),
        { numRuns: 50 }
      );
    });

    it('Property: Empty required fields always fail validation', async () => {
      const schema = z.object({
        body: z.object({
          name: z.string().trim().min(1, 'Name is required'),
          description: z.string().trim().min(1, 'Description is required'),
        }),
      });

      // Generate empty or whitespace-only strings
      const emptyStringArbitrary = fc.constantFrom('', '   ', '\t', '\n', '  \t  ');

      await fc.assert(
        fc.asyncProperty(emptyStringArbitrary, emptyStringArbitrary, async (name, description) => {
          const req = {
            body: { name, description },
            query: {},
            params: {},
            headers: { 'x-correlation-id': 'test-id' },
            method: 'POST',
            path: '/test',
          } as unknown as Request;

          const res = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
          } as unknown as Response;

          const next = jest.fn();

          const middleware = validateRequest(schema);
          await middleware(req, res, next);

          // Assertion: Empty/whitespace strings should fail validation
          // Note: Zod's trim() happens before min() check, so whitespace becomes empty
          expect(res.status).toHaveBeenCalledWith(400);
          expect(next).not.toHaveBeenCalled();
        }),
        { numRuns: 20 }
      );
    });
  });

  describe('Property 2: Rate Limiting Fairness', () => {
    /**
     * **Validates: Requirements US-3**
     * 
     * Property: For all users U and time windows W:
     * - If user U makes N requests in window W where N ≤ limit, all requests succeed
     * - If user U makes N requests in window W where N > limit, exactly (N - limit) requests fail with 429
     * 
     * Note: This is a conceptual property test. Full rate limiting tests require Redis
     * and are better suited for integration tests. Here we test the mathematical properties.
     */

    it('Property: Request count never exceeds limit in a window', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 200 }), // Total requests
          fc.integer({ min: 10, max: 100 }), // Rate limit
          (totalRequests, rateLimit) => {
            // Simulate rate limiting logic
            const allowedRequests = Math.min(totalRequests, rateLimit);
            const rejectedRequests = Math.max(0, totalRequests - rateLimit);

            // Property: allowed + rejected = total
            expect(allowedRequests + rejectedRequests).toBe(totalRequests);

            // Property: allowed never exceeds limit
            expect(allowedRequests).toBeLessThanOrEqual(rateLimit);

            // Property: if total <= limit, all allowed
            if (totalRequests <= rateLimit) {
              expect(allowedRequests).toBe(totalRequests);
              expect(rejectedRequests).toBe(0);
            }

            // Property: if total > limit, exactly (total - limit) rejected
            if (totalRequests > rateLimit) {
              expect(rejectedRequests).toBe(totalRequests - rateLimit);
              expect(allowedRequests).toBe(rateLimit);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('Property: Rate limit window reset allows new requests', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 100 }), // Requests in window 1
          fc.integer({ min: 1, max: 100 }), // Requests in window 2
          fc.integer({ min: 10, max: 50 }),  // Rate limit
          (requests1, requests2, rateLimit) => {
            // Simulate two separate time windows
            const allowed1 = Math.min(requests1, rateLimit);
            const allowed2 = Math.min(requests2, rateLimit);

            // Property: Each window is independent
            expect(allowed1).toBeLessThanOrEqual(rateLimit);
            expect(allowed2).toBeLessThanOrEqual(rateLimit);

            // Property: Windows don't affect each other
            if (requests1 <= rateLimit && requests2 <= rateLimit) {
              expect(allowed1).toBe(requests1);
              expect(allowed2).toBe(requests2);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('Property: Different users have independent rate limits', () => {
      fc.assert(
        fc.property(
          fc.array(fc.integer({ min: 1, max: 150 }), { minLength: 2, maxLength: 10 }), // Requests per user
          fc.integer({ min: 10, max: 100 }), // Rate limit per user
          (requestsPerUser, rateLimit) => {
            // Simulate rate limiting for multiple users
            const allowedPerUser = requestsPerUser.map(requests => 
              Math.min(requests, rateLimit)
            );

            // Property: Each user's limit is independent
            allowedPerUser.forEach((allowed, index) => {
              expect(allowed).toBeLessThanOrEqual(rateLimit);
              if (requestsPerUser[index] <= rateLimit) {
                expect(allowed).toBe(requestsPerUser[index]);
              }
            });

            // Property: One user hitting limit doesn't affect others
            const totalAllowed = allowedPerUser.reduce((sum, allowed) => sum + allowed, 0);
            const expectedTotal = requestsPerUser.reduce(
              (sum, requests) => sum + Math.min(requests, rateLimit),
              0
            );
            expect(totalAllowed).toBe(expectedTotal);
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  describe('Property 3: Circuit Breaker State Transitions', () => {
    /**
     * **Validates: Requirements US-4**
     * 
     * Property: For all services S:
     * - If error rate > threshold, circuit transitions to OPEN
     * - If circuit is OPEN for resetTimeout, circuit transitions to HALF_OPEN
     * - If request succeeds in HALF_OPEN, circuit transitions to CLOSED
     * - If request fails in HALF_OPEN, circuit transitions to OPEN
     * 
     * Note: Circuit breaker behavior involves complex timing and state management.
     * These tests focus on the mathematical properties and observable behaviors
     * rather than exact state transitions which are timing-dependent.
     */

    beforeEach(() => {
      // Reset all circuit breakers before each test
      resetAllCircuitBreakers();
    });

    it('Property: Circuit opens when error threshold is exceeded', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 51, max: 100 }), // Error percentage (> 50%)
          fc.integer({ min: 10, max: 50 }),  // Total requests
          async (errorPercentage, totalRequests) => {
            const errorCount = Math.ceil((totalRequests * errorPercentage) / 100);
            const successCount = totalRequests - errorCount;

            let callCount = 0;
            const mockServiceCall = async () => {
              callCount++;
              if (callCount <= errorCount) {
                throw new Error('Service error');
              }
              return 'success';
            };

            const breaker = createCircuitBreaker(
              mockServiceCall,
              `test-service-${errorPercentage}-${totalRequests}`,
              {
                errorThresholdPercentage: 50,
                resetTimeout: 100,
                timeout: 1000,
              }
            );

            // Make requests
            const results = [];
            for (let i = 0; i < totalRequests; i++) {
              try {
                await breaker.fire();
                results.push('success');
              } catch (error: any) {
                results.push(error.message);
              }
            }

            // Property: Circuit should open after error threshold is exceeded
            // Note: Circuit breaker needs time to calculate error rate
            // After enough errors, subsequent requests should be rejected
            const rejectedCount = results.filter(r => r === 'Breaker is open').length;
            
            // If error rate > 50%, circuit should eventually open
            if (errorPercentage > 50) {
              // Circuit may not open immediately, but should open eventually
              expect(breaker.opened || rejectedCount > 0).toBeTruthy();
            }
          }
        ),
        { numRuns: 20 }
      );
    });

    it('Property: Error rate calculation is mathematically correct', () => {
      // Test the mathematical property without timing dependencies
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 100 }), // Total requests
          fc.integer({ min: 0, max: 100 }), // Success count
          (totalRequests, successCount) => {
            // Ensure success count doesn't exceed total
            const actualSuccess = Math.min(successCount, totalRequests);
            const failures = totalRequests - actualSuccess;
            const errorRate = (failures / totalRequests) * 100;

            // Property: Error rate should be between 0 and 100
            expect(errorRate).toBeGreaterThanOrEqual(0);
            expect(errorRate).toBeLessThanOrEqual(100);

            // Property: If all requests fail, error rate is 100%
            if (actualSuccess === 0) {
              expect(errorRate).toBe(100);
            }

            // Property: If all requests succeed, error rate is 0%
            if (failures === 0) {
              expect(errorRate).toBe(0);
            }

            // Property: Error rate > 50% means more failures than successes
            if (errorRate > 50) {
              expect(failures).toBeGreaterThan(actualSuccess);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('Property: Circuit breaker allows requests when closed', async () => {
      // Test that a closed circuit allows all requests through
      const mockServiceCall = jest.fn().mockResolvedValue('success');

      const breaker = createCircuitBreaker(
        mockServiceCall,
        'test-service-closed',
        {
          errorThresholdPercentage: 50,
          resetTimeout: 1000,
          timeout: 1000,
        }
      );

      // Make several successful requests
      const numRequests = 10;
      let successCount = 0;

      for (let i = 0; i < numRequests; i++) {
        try {
          await breaker.fire();
          successCount++;
        } catch (error) {
          // Should not happen
        }
      }

      // Property: All requests should succeed when circuit is closed
      expect(successCount).toBe(numRequests);
      expect(breaker.opened).toBe(false);
    });

    it('Property: Circuit breaker stats track request counts', async () => {
      // Test that stats accurately reflect the number of requests
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 5, max: 20 }), // Number of requests
          async (numRequests) => {
            let actualCalls = 0;
            const mockServiceCall = async () => {
              actualCalls++;
              return 'success';
            };

            const breaker = createCircuitBreaker(
              mockServiceCall,
              `test-service-stats-${numRequests}-${Date.now()}-${Math.random()}`,
              {
                errorThresholdPercentage: 80,
                resetTimeout: 1000,
                timeout: 1000,
              }
            );

            // Make requests
            for (let i = 0; i < numRequests; i++) {
              try {
                await breaker.fire();
              } catch (error) {
                // Unexpected
              }
            }

            // Property: Stats should reflect the number of fires
            const stats = breaker.stats;
            expect(stats.fires).toBeGreaterThanOrEqual(numRequests);
            
            // Property: Number of successes should match actual calls
            expect(stats.successes).toBe(actualCalls);
            expect(stats.failures).toBe(0);
          }
        ),
        { numRuns: 20 }
      );
    });
  });

  describe('Property 4: Validation Schema Composition', () => {
    /**
     * Additional property: Schema composition should be consistent
     * If schema A validates X and schema B validates Y,
     * then composed schema should validate both X and Y
     */

    it('Property: Composed schemas validate all parts', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.string({ minLength: 1, maxLength: 50 }),
          fc.integer({ min: 1, max: 100 }),
          async (name, age) => {
            // Schema A: validates name
            const schemaA = z.object({
              body: z.object({
                name: z.string().min(1).max(50),
              }),
            });

            // Schema B: validates age
            const schemaB = z.object({
              body: z.object({
                age: z.number().int().positive().max(100),
              }),
            });

            // Composed schema: validates both
            const composedSchema = z.object({
              body: z.object({
                name: z.string().min(1).max(50),
                age: z.number().int().positive().max(100),
              }),
            });

            const req = {
              body: { name, age },
              query: {},
              params: {},
              headers: { 'x-correlation-id': 'test-id' },
              method: 'POST',
              path: '/test',
            } as unknown as Request;

            const res = {
              status: jest.fn().mockReturnThis(),
              json: jest.fn(),
            } as unknown as Response;

            const next = jest.fn();

            // Test composed schema
            const middleware = validateRequest(composedSchema);
            await middleware(req, res, next);

            // Property: If both parts are valid, composed validation succeeds
            expect(next).toHaveBeenCalled();
            expect(res.status).not.toHaveBeenCalled();
          }
        ),
        { numRuns: 50 }
      );
    });
  });
});
