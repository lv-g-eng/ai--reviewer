/**
 * Property-Based Tests for Authentication Service
 * 
 * Feature: nextauth-backend-integration
 * 
 * These tests validate universal properties that should hold true across
 * all valid inputs using property-based testing with fast-check.
 * Minimum 100 iterations per property test.
 */

import * as fc from 'fast-check';
import {
  getBackendUrl,
  validateEnvironmentConfig,
  getAuthUrl,
  getLoginUrl,
  getUserDetailsUrl,
  authenticateUser,
  createAuthError,
  getUserFriendlyErrorMessage,
  handleAuthError,
  isValidEmail,
  isValidPassword,
  validateCredentials,
  type AuthError,
  type LoginCredentials,
} from '../auth';

// Mock fetch globally
global.fetch = jest.fn();

describe('Property-Based Tests: Authentication Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.NODE_ENV = 'test';
  });

  /**
   * Property 1: Authentication URL Correctness
   * 
   * For any authentication request, the system should route the request to
   * the backend API URL constructed from the NEXT_PUBLIC_API_URL environment
   * variable, ensuring all authentication attempts reach the correct backend endpoint.
   * 
   * Validates: Requirements 1.1, 1.3, 3.1
   */
  describe('Property 1: Authentication URL Correctness', () => {
    it('should always construct valid URLs from environment variables', () => {
      fc.assert(
        fc.property(
          fc.webUrl({ withFragments: false, withQueryParameters: false }),
          fc.constantFrom('/api/v1/auth/login', '/api/v1/auth/me', '/api/v1/auth/logout'),
          (backendUrl, endpoint) => {
            // Set environment variable
            process.env.NEXT_PUBLIC_API_URL = backendUrl;
            
            // Construct URL
            const fullUrl = getAuthUrl(endpoint);
            
            // Properties that should always hold
            expect(fullUrl).toContain(endpoint);
            expect(fullUrl).toMatch(/^https?:\/\//); // Valid HTTP(S) URL
            expect(fullUrl).not.toContain('//api'); // No double slashes
            expect(fullUrl).not.toContain('undefined');
            expect(fullUrl).not.toContain('null');
            
            // URL should be parseable
            expect(() => new URL(fullUrl)).not.toThrow();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always produce consistent URLs for the same inputs', () => {
      fc.assert(
        fc.property(
          fc.webUrl({ withFragments: false, withQueryParameters: false }),
          fc.constantFrom('/api/v1/auth/login', '/api/v1/auth/me'),
          (backendUrl, endpoint) => {
            process.env.NEXT_PUBLIC_API_URL = backendUrl;
            
            const url1 = getAuthUrl(endpoint);
            const url2 = getAuthUrl(endpoint);
            
            // Idempotency: same inputs should produce same outputs
            expect(url1).toBe(url2);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle various URL formats correctly', () => {
      fc.assert(
        fc.property(
          fc.webUrl({ withFragments: false, withQueryParameters: false }),
          fc.boolean(), // with or without trailing slash
          (baseUrl, withTrailingSlash) => {
            const backendUrl = withTrailingSlash ? `${baseUrl}/` : baseUrl;
            process.env.NEXT_PUBLIC_API_URL = backendUrl;
            
            const loginUrl = getLoginUrl();
            const userUrl = getUserDetailsUrl();
            
            // Should not have double slashes (except in protocol)
            expect(loginUrl.replace(/^https?:\/\//, '')).not.toContain('//');
            expect(userUrl.replace(/^https?:\/\//, '')).not.toContain('//');
            
            // Should end with correct endpoints
            expect(loginUrl).toMatch(/\/api\/v1\/auth\/login$/);
            expect(userUrl).toMatch(/\/api\/v1\/auth\/me$/);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 2: Environment Variable Configuration
   * 
   * For any NextAuth configuration loading, the system should correctly read
   * and apply NEXT_PUBLIC_API_URL, NEXTAUTH_URL, and NEXTAUTH_SECRET environment
   * variables to the authentication configuration.
   * 
   * Validates: Requirements 2.1, 2.2, 2.3
   */
  describe('Property 2: Environment Variable Configuration', () => {
    it('should always validate environment configuration consistently', () => {
      fc.assert(
        fc.property(
          fc.option(fc.string({ minLength: 32 }), { nil: undefined }), // NEXTAUTH_SECRET
          fc.option(fc.webUrl(), { nil: undefined }), // NEXTAUTH_URL
          (secret, url) => {
            process.env.NEXTAUTH_SECRET = secret;
            process.env.NEXTAUTH_URL = url;
            
            const result = validateEnvironmentConfig();
            
            // Properties that should always hold
            expect(typeof result.valid).toBe('boolean');
            expect(Array.isArray(result.errors)).toBe(true);
            
            // If valid, should have no errors
            if (result.valid) {
              expect(result.errors).toHaveLength(0);
            }
            
            // If invalid, should have at least one error
            if (!result.valid) {
              expect(result.errors.length).toBeGreaterThan(0);
            }
            
            // Errors should be strings
            result.errors.forEach(error => {
              expect(typeof error).toBe('string');
              expect(error.length).toBeGreaterThan(0);
            });
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always prefer NEXT_PUBLIC_API_URL over BACKEND_URL', () => {
      fc.assert(
        fc.property(
          fc.webUrl(),
          fc.webUrl(),
          (publicUrl, backendUrl) => {
            process.env.NEXT_PUBLIC_API_URL = publicUrl;
            process.env.BACKEND_URL = backendUrl;
            
            const result = getBackendUrl();
            
            // Should always return NEXT_PUBLIC_API_URL when both are set
            expect(result).toBe(publicUrl);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always return a valid URL even with missing env vars', () => {
      fc.assert(
        fc.property(
          fc.boolean(),
          fc.boolean(),
          (hasPublicUrl, hasBackendUrl) => {
            process.env.NEXT_PUBLIC_API_URL = hasPublicUrl ? 'http://api.example.com' : '';
            process.env.BACKEND_URL = hasBackendUrl ? 'http://backend.example.com' : '';
            
            const result = getBackendUrl();
            
            // Should always return a valid URL
            expect(result).toBeTruthy();
            expect(result).toMatch(/^https?:\/\//);
            expect(() => new URL(result)).not.toThrow();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 4: Authentication Response Handling
   * 
   * For any backend authentication response (success or failure), the frontend
   * should properly parse the response and establish the correct session state
   * or error state.
   * 
   * Validates: Requirements 3.2, 3.3
   */
  describe('Property 4: Authentication Response Handling', () => {
    it('should always handle successful authentication responses correctly', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.emailAddress(),
          fc.string({ minLength: 8 }),
          fc.uuid(),
          fc.string({ minLength: 20 }),
          fc.string({ minLength: 20 }),
          fc.constantFrom('user', 'admin', 'viewer'),
          async (email, password, userId, accessToken, refreshToken, role) => {
            const mockAuthResponse = {
              access_token: accessToken,
              refresh_token: refreshToken,
            };
            
            const mockUserResponse = {
              id: userId,
              email: email,
              full_name: 'Test User',
              role: role,
              is_active: true,
            };
            
            (global.fetch as jest.Mock)
              .mockResolvedValueOnce({
                ok: true,
                json: async () => mockAuthResponse,
              })
              .mockResolvedValueOnce({
                ok: true,
                json: async () => mockUserResponse,
              });
            
            const user = await authenticateUser({ email, password });
            
            // Properties that should always hold for successful auth
            expect(user.id).toBe(userId);
            expect(user.email).toBe(email);
            expect(user.accessToken).toBe(accessToken);
            expect(user.refreshToken).toBe(refreshToken);
            expect(user.role).toBe(role);
            expect(typeof user.name).toBe('string');
            expect(user.name.length).toBeGreaterThan(0);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always throw appropriate errors for failed authentication', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.emailAddress(),
          fc.string({ minLength: 8 }),
          fc.integer({ min: 400, max: 599 }),
          fc.string(),
          async (email, password, statusCode, errorMessage) => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
              ok: false,
              status: statusCode,
              json: async () => ({ detail: errorMessage }),
            });
            
            await expect(authenticateUser({ email, password })).rejects.toMatchObject({
              type: expect.stringMatching(/^(credentials|server|network)$/),
              message: expect.any(String),
            });
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 5: Error Handling and Messaging
   * 
   * For any authentication error (configuration, network, or credentials),
   * the system should provide clear, specific error messages and handle
   * the error gracefully without crashing.
   * 
   * Validates: Requirements 1.4, 3.4, 4.2, 4.3
   */
  describe('Property 5: Error Handling and Messaging', () => {
    it('should always create valid error objects', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('configuration', 'network', 'credentials', 'server', 'validation'),
          fc.string({ minLength: 1 }),
          fc.option(fc.integer({ min: 100, max: 599 }), { nil: undefined }),
          fc.option(fc.string(), { nil: undefined }),
          (type, message, statusCode, details) => {
            const error = createAuthError(type, message, statusCode, details);
            
            // Properties that should always hold
            expect(error.type).toBe(type);
            expect(error.message).toBe(message);
            expect(error.statusCode).toBe(statusCode);
            expect(error.details).toBe(details);
            expect(error instanceof Error).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always return user-friendly error messages', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('configuration', 'network', 'credentials', 'server', 'validation'),
          fc.string({ minLength: 1 }),
          (type, message) => {
            const error = createAuthError(type, message);
            const friendlyMessage = getUserFriendlyErrorMessage(error);
            
            // Properties that should always hold
            expect(typeof friendlyMessage).toBe('string');
            expect(friendlyMessage.length).toBeGreaterThan(0);
            expect(friendlyMessage).not.toContain('undefined');
            expect(friendlyMessage).not.toContain('null');
            
            // Should not expose technical details (except for validation)
            if (type !== 'validation') {
              expect(friendlyMessage).not.toBe(message);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always handle any error type gracefully', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            fc.constant(new Error('Test error')),
            fc.constant(createAuthError('network', 'Network error')),
            fc.constant('string error'),
            fc.constant(null),
            fc.constant(undefined),
            fc.constant({ custom: 'error' })
          ),
          (error) => {
            const handled = handleAuthError(error);
            
            // Should always return a valid AuthError
            expect(handled.type).toMatch(/^(configuration|network|credentials|server|validation)$/);
            expect(typeof handled.message).toBe('string');
            expect(handled.message.length).toBeGreaterThan(0);
            expect(handled instanceof Error).toBe(true);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Property 6: Development Logging
   * 
   * For any authentication operation when NODE_ENV is set to development,
   * the system should provide detailed logging and debugging information.
   * 
   * Validates: Requirements 4.1, 4.4
   */
  describe('Property 6: Development Logging', () => {
    it('should log in development mode but not in production', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('development', 'production', 'test'),
          fc.webUrl(),
          (nodeEnv, backendUrl) => {
            process.env.NODE_ENV = nodeEnv;
            process.env.NEXT_PUBLIC_API_URL = backendUrl;
            
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
            
            getBackendUrl();
            
            if (nodeEnv === 'development') {
              // Should log in development
              expect(consoleSpy).toHaveBeenCalled();
            } else {
              // Should not log in production/test
              expect(consoleSpy).not.toHaveBeenCalled();
            }
            
            consoleSpy.mockRestore();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Additional Property: Email Validation Consistency
   * 
   * Email validation should be consistent and follow standard email format rules.
   */
  describe('Additional Property: Email Validation', () => {
    it('should consistently validate email formats', () => {
      fc.assert(
        fc.property(
          fc.emailAddress(),
          (email) => {
            const isValid = isValidEmail(email);
            
            // Valid emails should always pass
            expect(isValid).toBe(true);
            
            // Should be idempotent
            expect(isValidEmail(email)).toBe(isValid);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reject invalid email formats', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            fc.constant(''),
            fc.constant('invalid'),
            fc.constant('@example.com'),
            fc.constant('user@'),
            fc.string().filter(s => !s.includes('@'))
          ),
          (invalidEmail) => {
            const isValid = isValidEmail(invalidEmail);
            
            // Invalid emails should always fail
            expect(isValid).toBe(false);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Additional Property: Password Validation Consistency
   * 
   * Password validation should consistently enforce security requirements.
   */
  describe('Additional Property: Password Validation', () => {
    it('should consistently validate password strength', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 8 })
            .filter(s => /[A-Z]/.test(s) && /[a-z]/.test(s) && /[0-9]/.test(s)),
          (password) => {
            const result = isValidPassword(password);
            
            // Strong passwords should pass
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
            
            // Should be idempotent
            const result2 = isValidPassword(password);
            expect(result2.valid).toBe(result.valid);
            expect(result2.errors).toEqual(result.errors);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should always return consistent error messages for weak passwords', () => {
      fc.assert(
        fc.property(
          fc.string({ maxLength: 7 }),
          (weakPassword) => {
            const result = isValidPassword(weakPassword);
            
            // Weak passwords should fail
            expect(result.valid).toBe(false);
            expect(result.errors.length).toBeGreaterThan(0);
            
            // All errors should be strings
            result.errors.forEach(error => {
              expect(typeof error).toBe('string');
              expect(error.length).toBeGreaterThan(0);
            });
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * Additional Property: Credentials Validation Consistency
   * 
   * Credentials validation should consistently check both email and password.
   */
  describe('Additional Property: Credentials Validation', () => {
    it('should consistently validate complete credentials', () => {
      fc.assert(
        fc.property(
          fc.emailAddress(),
          fc.string({ minLength: 1 }),
          (email, password) => {
            const result = validateCredentials({ email, password });
            
            // Properties that should always hold
            expect(typeof result.valid).toBe('boolean');
            expect(Array.isArray(result.errors)).toBe(true);
            
            // If valid, no errors
            if (result.valid) {
              expect(result.errors).toHaveLength(0);
            }
            
            // If invalid, at least one error
            if (!result.valid) {
              expect(result.errors.length).toBeGreaterThan(0);
            }
            
            // Should be idempotent
            const result2 = validateCredentials({ email, password });
            expect(result2.valid).toBe(result.valid);
            expect(result2.errors).toEqual(result.errors);
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
