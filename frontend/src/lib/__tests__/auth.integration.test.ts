/**
 * Integration Tests for Authentication Flow
 * 
 * Tests the complete authentication flow from frontend to backend,
 * including session management, token handling, and error scenarios
 * across component boundaries.
 */

import {
  authenticateUser,
  getBackendUrl,
  getLoginUrl,
  getUserDetailsUrl,
  type LoginCredentials,
} from '../auth';

// Mock fetch globally
global.fetch = jest.fn();

describe('Integration Tests: Authentication Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  describe('Complete Authentication Flow', () => {
    it('should complete full authentication flow with valid credentials', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'Password123',
      };

      const mockAuthResponse = {
        access_token: 'mock-access-token-12345',
        refresh_token: 'mock-refresh-token-67890',
        token_type: 'Bearer',
      };

      const mockUserResponse = {
        id: 'user-123',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'user',
        is_active: true,
      };

      // Mock the fetch calls
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockAuthResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockUserResponse,
        });

      // Execute authentication
      const user = await authenticateUser(credentials);

      // Verify the complete flow
      expect(global.fetch).toHaveBeenCalledTimes(2);

      // Verify login request
      const loginCall = (global.fetch as jest.Mock).mock.calls[0];
      expect(loginCall[0]).toBe(getLoginUrl());
      expect(loginCall[1].method).toBe('POST');
      expect(loginCall[1].headers['Content-Type']).toBe('application/json');
      expect(JSON.parse(loginCall[1].body)).toEqual(credentials);

      // Verify user details request
      const userDetailsCall = (global.fetch as jest.Mock).mock.calls[1];
      expect(userDetailsCall[0]).toBe(getUserDetailsUrl());
      expect(userDetailsCall[1].headers.Authorization).toBe('Bearer mock-access-token-12345');

      // Verify user object
      expect(user).toEqual({
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        full_name: 'Test User',
        role: 'user',
        is_active: true,
        accessToken: 'mock-access-token-12345',
        refreshToken: 'mock-refresh-token-67890',
      });
    });

    it('should handle authentication failure at login step', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'WrongPassword',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(authenticateUser(credentials)).rejects.toMatchObject({
        type: 'credentials',
        message: 'Invalid credentials',
        statusCode: 401,
      });

      // Should only call login endpoint, not user details
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should handle authentication failure at user details step', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'Password123',
      };

      const mockAuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockAuthResponse,
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: async () => ({ detail: 'Internal server error' }),
        });

      await expect(authenticateUser(credentials)).rejects.toMatchObject({
        type: 'server',
        message: 'Failed to fetch user details',
        statusCode: 500,
      });

      // Should call both endpoints
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Session Management', () => {
    it('should properly format user data for session storage', async () => {
      const mockAuthResponse = {
        access_token: 'token-abc',
        refresh_token: 'refresh-xyz',
      };

      const mockUserResponse = {
        id: '123',
        email: 'user@example.com',
        full_name: 'John Doe',
        role: 'admin',
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

      const user = await authenticateUser({
        email: 'user@example.com',
        password: 'password',
      });

      // Verify all required session fields are present
      expect(user).toHaveProperty('id');
      expect(user).toHaveProperty('email');
      expect(user).toHaveProperty('name');
      expect(user).toHaveProperty('role');
      expect(user).toHaveProperty('accessToken');
      expect(user).toHaveProperty('refreshToken');

      // Verify data types
      expect(typeof user.id).toBe('string');
      expect(typeof user.email).toBe('string');
      expect(typeof user.name).toBe('string');
      expect(typeof user.accessToken).toBe('string');
    });

    it('should handle missing full_name by deriving from email', async () => {
      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
      };

      const mockUserResponse = {
        id: '123',
        email: 'testuser@example.com',
        // full_name is missing
        role: 'user',
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

      const user = await authenticateUser({
        email: 'testuser@example.com',
        password: 'password',
      });

      // Should derive name from email
      expect(user.name).toBe('testuser');
    });
  });

  describe('Token Handling', () => {
    it('should include access token in user details request', async () => {
      const mockAuthResponse = {
        access_token: 'specific-access-token',
        refresh_token: 'specific-refresh-token',
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      const userDetailsCall = (global.fetch as jest.Mock).mock.calls[1];
      expect(userDetailsCall[1].headers.Authorization).toBe('Bearer specific-access-token');
    });

    it('should return both access and refresh tokens', async () => {
      const mockAuthResponse = {
        access_token: 'access-123',
        refresh_token: 'refresh-456',
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      const user = await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      expect(user.accessToken).toBe('access-123');
      expect(user.refreshToken).toBe('refresh-456');
    });

    it('should handle missing refresh token gracefully', async () => {
      const mockAuthResponse = {
        access_token: 'access-only',
        // refresh_token is missing
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      const user = await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      expect(user.accessToken).toBe('access-only');
      expect(user.refreshToken).toBeUndefined();
    });
  });

  describe('Error Scenarios Across Components', () => {
    it('should handle network timeout gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network request timed out')
      );

      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'network',
        message: 'Network request timed out',
      });
    });

    it('should handle malformed JSON response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Unexpected token in JSON');
        },
      });

      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'network',
      });
    });

    it('should handle backend server unavailable', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('ECONNREFUSED')
      );

      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'network',
        message: 'ECONNREFUSED',
      });
    });

    it('should handle 500 server errors with proper error type', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Database connection failed' }),
      });

      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'server',
        statusCode: 500,
      });
    });

    it('should handle 401 unauthorized with proper error type', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'credentials',
        statusCode: 401,
      });
    });
  });

  describe('Backend URL Configuration', () => {
    it('should use correct backend URL from environment', async () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.production.com';

      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      const loginCall = (global.fetch as jest.Mock).mock.calls[0];
      expect(loginCall[0]).toBe('https://api.production.com/api/v1/auth/login');
    });

    it('should fall back to default URL when not configured', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      delete process.env.BACKEND_URL;

      const backendUrl = getBackendUrl();
      expect(backendUrl).toBe('http://localhost:8000');
    });
  });

  describe('Request/Response Flow', () => {
    it('should send correct headers in login request', async () => {
      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      const loginCall = (global.fetch as jest.Mock).mock.calls[0];
      expect(loginCall[1].method).toBe('POST');
      expect(loginCall[1].headers['Content-Type']).toBe('application/json');
    });

    it('should send correct body in login request', async () => {
      const credentials = {
        email: 'specific@example.com',
        password: 'SpecificPassword123',
      };

      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
      };

      const mockUserResponse = {
        id: '123',
        email: 'specific@example.com',
        role: 'user',
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

      await authenticateUser(credentials);

      const loginCall = (global.fetch as jest.Mock).mock.calls[0];
      const body = JSON.parse(loginCall[1].body);
      expect(body).toEqual(credentials);
    });

    it('should not include credentials in user details request', async () => {
      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
      };

      const mockUserResponse = {
        id: '123',
        email: 'test@example.com',
        role: 'user',
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

      await authenticateUser({
        email: 'test@example.com',
        password: 'password',
      });

      const userDetailsCall = (global.fetch as jest.Mock).mock.calls[1];
      expect(userDetailsCall[1].body).toBeUndefined();
      expect(userDetailsCall[1].method).toBeUndefined(); // GET is default
    });
  });

  describe('Data Validation', () => {
    it('should reject empty email', async () => {
      await expect(
        authenticateUser({
          email: '',
          password: 'password',
        })
      ).rejects.toMatchObject({
        type: 'validation',
        message: 'Email and password are required',
      });

      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should reject empty password', async () => {
      await expect(
        authenticateUser({
          email: 'test@example.com',
          password: '',
        })
      ).rejects.toMatchObject({
        type: 'validation',
        message: 'Email and password are required',
      });

      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should reject both empty credentials', async () => {
      await expect(
        authenticateUser({
          email: '',
          password: '',
        })
      ).rejects.toMatchObject({
        type: 'validation',
      });

      expect(global.fetch).not.toHaveBeenCalled();
    });
  });
});
