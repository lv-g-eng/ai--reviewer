/**
 * Enhanced API Client for Production Environment
 * 
 * Features:
 * - Axios with axios-retry for automatic retries
 * - Exponential backoff strategy (max 3 retries)
 * - 30-second timeout
 * - Automatic authentication token injection
 * - Unified error handling and logging
 * - Support for GET, POST, PUT, DELETE methods
 * 
 * Requirements: 2.5, 4.4, 4.7
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError, AxiosResponse } from 'axios';
import axiosRetry, { exponentialDelay } from 'axios-retry';

/**
 * Configuration options for the API client
 */
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  retryConfig?: {
    retries: number;
    retryDelay: (retryCount: number, error: AxiosError) => number;
    retryCondition: (error: AxiosError) => boolean;
  };
}

/**
 * Standardized API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

/**
 * Standardized API error structure
 */
export interface ApiError {
  message: string;
  code: string;
  status: number;
  details?: unknown;
}

/**
 * Enhanced API Client class
 * 
 * Provides a unified HTTP client for all API requests with:
 * - Automatic retry with exponential backoff
 * - Authentication token management
 * - Comprehensive error handling
 * - Request/response logging
 */
export class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor(config: ApiClientConfig) {
    const {
      baseURL,
      timeout = 30000, // Default 30 seconds
      retryConfig = {
        retries: 3,
        retryDelay: exponentialDelay,
        retryCondition: this.defaultRetryCondition,
      },
    } = config;

    // Create axios instance with base configuration
    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Configure axios-retry with exponential backoff
    axiosRetry(this.client, {
      retries: retryConfig.retries,
      retryDelay: retryConfig.retryDelay,
      retryCondition: retryConfig.retryCondition,
      onRetry: (retryCount, error, requestConfig) => {
        console.warn(
          `[API Client] Retry attempt ${retryCount} for ${requestConfig.method?.toUpperCase()} ${requestConfig.url}`,
          {
            error: error.message,
            status: error.response?.status,
          }
        );
      },
    });

    // Setup request and response interceptors
    this.setupInterceptors();
  }

  /**
   * Default retry condition
   * Retries on network errors, timeouts, and 5xx server errors
   */
  private defaultRetryCondition(error: AxiosError): boolean {
    // Retry on network errors (no response)
    if (!error.response) {
      return true;
    }

    // Retry on 5xx server errors
    if (error.response.status >= 500 && error.response.status <= 599) {
      return true;
    }

    // Retry on 429 (rate limit) errors
    if (error.response.status === 429) {
      return true;
    }

    // Don't retry on client errors (4xx except 429)
    return false;
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor - automatically add authentication token
    this.client.interceptors.request.use(
      (config) => {
        // Add authentication token if available
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        } else {
          // Try to get token from localStorage
          if (typeof window !== 'undefined') {
            const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
            if (token) {
              config.headers.Authorization = `Bearer ${token}`;
            }
          }
        }

        // Add correlation ID for request tracing
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();

        // Log request
        this.logRequest(config);

        return config;
      },
      (error) => {
        console.error('[API Client] Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor - unified error handling
    this.client.interceptors.response.use(
      (response) => {
        // Log successful response
        this.logResponse(response);
        return response;
      },
      (error: AxiosError) => {
        // Log error response
        this.logError(error);

        // Handle specific error cases
        if (error.response?.status === 401) {
          this.handleAuthenticationError(error);
        } else if (error.response?.status === 403) {
          this.handleAuthorizationError(error);
        } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          this.handleTimeoutError(error);
        } else if (!error.response) {
          this.handleNetworkError(error);
        }

        return Promise.reject(this.transformError(error));
      }
    );
  }

  /**
   * Generate a unique correlation ID for request tracing
   */
  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Log outgoing request
   */
  private logRequest(config: AxiosRequestConfig): void {
    console.log(`[API Client] ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      headers: this.sanitizeHeaders(config.headers),
    });
  }

  /**
   * Log successful response
   */
  private logResponse(response: AxiosResponse): void {
    console.log(
      `[API Client] ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`,
      {
        status: response.status,
        statusText: response.statusText,
      }
    );
  }

  /**
   * Log error response
   */
  private logError(error: AxiosError): void {
    console.error(
      `[API Client] ${error.config?.method?.toUpperCase()} ${error.config?.url} - Error`,
      {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      }
    );
  }

  /**
   * Sanitize headers for logging (remove sensitive information)
   */
  private sanitizeHeaders(headers: any): Record<string, string> {
    if (!headers) return {};

    const sanitized: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      if (key.toLowerCase() === 'authorization') {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = String(value);
      }
    }
    return sanitized;
  }

  /**
   * Handle authentication errors (401)
   */
  private handleAuthenticationError(error: AxiosError): void {
    console.warn('[API Client] Authentication error - token may be expired');
    
    // Clear stored tokens
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('token');
      
      // Optionally redirect to login page
      // window.location.href = '/auth/signin';
    }
  }

  /**
   * Handle authorization errors (403)
   */
  private handleAuthorizationError(error: AxiosError): void {
    console.warn('[API Client] Authorization error - insufficient permissions');
  }

  /**
   * Handle timeout errors
   */
  private handleTimeoutError(error: AxiosError): void {
    console.error('[API Client] Request timeout - server took too long to respond');
  }

  /**
   * Handle network errors
   */
  private handleNetworkError(error: AxiosError): void {
    console.error('[API Client] Network error - unable to reach server');
  }

  /**
   * Transform axios error to standardized ApiError
   */
  private transformError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      return {
        message: this.extractErrorMessage(error.response.data),
        code: error.code || 'SERVER_ERROR',
        status: error.response.status,
        details: error.response.data,
      };
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // Request timeout
      return {
        message: 'Request timeout - server took too long to respond',
        code: 'TIMEOUT_ERROR',
        status: 0,
        details: { originalError: error.message },
      };
    } else {
      // Network error or other
      return {
        message: error.message || 'Network error - unable to reach server',
        code: error.code || 'NETWORK_ERROR',
        status: 0,
        details: { originalError: error.message },
      };
    }
  }

  /**
   * Extract error message from response data
   */
  private extractErrorMessage(data: any): string {
    if (typeof data === 'string') {
      return data;
    }
    if (data && typeof data === 'object') {
      return data.message || data.error || data.detail || 'An error occurred';
    }
    return 'An error occurred';
  }

  /**
   * Set authentication token
   */
  public setAuthToken(token: string): void {
    this.authToken = token;
    
    // Also store in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  /**
   * Clear authentication token
   */
  public clearAuthToken(): void {
    this.authToken = null;
    
    // Also clear from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('token');
    }
  }

  /**
   * GET request
   */
  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get<T>(url, config);
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  /**
   * POST request
   */
  public async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.client.post<T>(url, data, config);
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  /**
   * PUT request
   */
  public async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.client.put<T>(url, data, config);
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  /**
   * DELETE request
   */
  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete<T>(url, config);
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }
}

/**
 * Create default API client instance
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClientEnhanced = new ApiClient({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  retryConfig: {
    retries: 3,
    retryDelay: exponentialDelay,
    retryCondition: (error: AxiosError) => {
      // Retry on network errors, timeouts, and 5xx errors
      if (!error.response) return true;
      if (error.response.status >= 500) return true;
      if (error.response.status === 429) return true;
      return false;
    },
  },
});

// Export for convenience
export default apiClientEnhanced;
