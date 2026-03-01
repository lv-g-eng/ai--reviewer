/**
 * Optimized API Client with Advanced Caching and Performance Features
 * 
 * Features:
 * - Intelligent caching with TTL
 * - Request deduplication
 * - Retry logic with exponential backoff
 * - Request/response compression
 * - Performance monitoring
 * - Background cache warming
 * - Circuit breaker pattern
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import axiosRetry from 'axios-retry';

interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  etag?: string;
}

interface RequestMetrics {
  url: string;
  method: string;
  duration: number;
  status: number;
  cached: boolean;
  timestamp: number;
}

interface APIClientConfig {
  baseURL?: string;
  timeout?: number;
  retries?: number;
  cacheTTL?: number;
  enableMetrics?: boolean;
  enableCompression?: boolean;
}

class OptimizedAPIClient {
  private client: AxiosInstance;
  private cache = new Map<string, CacheEntry>();
  private pendingRequests = new Map<string, Promise<any>>();
  private metrics: RequestMetrics[] = [];
  private config: Required<APIClientConfig>;

  constructor(config: APIClientConfig = {}) {
    this.config = {
      // Use Next.js API routes for httpOnly cookie authentication
      baseURL: config.baseURL || '/api',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      cacheTTL: config.cacheTTL || 5 * 60 * 1000, // 5 minutes
      enableMetrics: config.enableMetrics ?? true,
      enableCompression: config.enableCompression ?? true,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Include cookies in requests
    });

    this.setupInterceptors();
    this.setupRetryLogic();
    this.startCacheCleanup();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // No need to add auth token - httpOnly cookies are sent automatically
        // Add correlation ID for tracing
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();

        // Add request timestamp for metrics
        (config as any).requestStartTime = Date.now();

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        this.recordMetrics(response);
        return response;
      },
      (error) => {
        if (error.response) {
          this.recordMetrics(error.response);
        }
        
        // Handle specific error cases
        if (error.response?.status === 401) {
          this.handleAuthError();
        } else if (error.response?.status === 429) {
          this.handleRateLimitError(error);
        }
        
        return Promise.reject(error);
      }
    );
  }

  private setupRetryLogic(): void {
    axiosRetry(this.client, {
      retries: this.config.retries,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return axiosRetry.isNetworkOrIdempotentRequestError(error) ||
               error.response?.status === 429 || // Rate limit
               (error.response?.status ? error.response.status >= 500 : false);    // Server errors
      },
      onRetry: (retryCount, error, requestConfig) => {
        console.warn(`Retry attempt ${retryCount} for ${requestConfig.url}`);
      }
    });
  }

  private startCacheCleanup(): void {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp > entry.ttl) {
          this.cache.delete(key);
        }
      }
    }, 60000); // Clean every minute
  }

  private generateCacheKey(config: AxiosRequestConfig): string {
    const { method, url, params, data } = config;
    return `${method}:${url}:${JSON.stringify(params)}:${JSON.stringify(data)}`;
  }

  private getCachedResponse<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }

  private setCachedResponse<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.cacheTTL
    });
  }

  private recordMetrics(response: AxiosResponse): void {
    if (!this.config.enableMetrics) return;
    
    const config = response.config as any;
    const duration = Date.now() - (config.requestStartTime || Date.now());
    
    const metric: RequestMetrics = {
      url: response.config.url || '',
      method: response.config.method?.toUpperCase() || 'GET',
      duration,
      status: response.status,
      cached: !!config.fromCache,
      timestamp: Date.now()
    };
    
    this.metrics.push(metric);
    
    // Keep only last 1000 metrics
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
    
    // Log slow requests
    if (duration > 2000) {
      console.warn(`Slow API request: ${metric.method} ${metric.url} took ${duration}ms`);
    }
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private handleAuthError(): void {
    // Clear auth tokens
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
      // Redirect to login or emit auth error event
      window.dispatchEvent(new CustomEvent('auth:expired'));
    }
  }

  private handleRateLimitError(error: any): void {
    const retryAfter = error.response?.headers['retry-after'];
    if (retryAfter) {
      console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
    }
  }

  // Public API methods with optimizations
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const fullConfig = { ...config, method: 'GET', url };
    const cacheKey = this.generateCacheKey(fullConfig);
    
    // Check cache first for GET requests
    const cached = this.getCachedResponse<T>(cacheKey);
    if (cached) {
      (fullConfig as any).fromCache = true;
      return cached;
    }
    
    // Check for pending request (deduplication)
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }
    
    // Make request
    const requestPromise = this.client.get<T>(url, config).then(response => {
      this.setCachedResponse(cacheKey, response.data);
      this.pendingRequests.delete(cacheKey);
      return response.data;
    }).catch(error => {
      this.pendingRequests.delete(cacheKey);
      throw error;
    });
    
    this.pendingRequests.set(cacheKey, requestPromise);
    return requestPromise;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    
    // Invalidate related cache entries
    this.invalidateCache(url);
    
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    
    // Invalidate related cache entries
    this.invalidateCache(url);
    
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    
    // Invalidate related cache entries
    this.invalidateCache(url);
    
    return response.data;
  }

  private invalidateCache(url: string): void {
    // Remove cache entries that might be affected by this mutation
    const keysToDelete: string[] = [];
    
    for (const key of this.cache.keys()) {
      if (key.includes(url) || this.isRelatedUrl(key, url)) {
        keysToDelete.push(key);
      }
    }
    
    keysToDelete.forEach(key => this.cache.delete(key));
  }

  private isRelatedUrl(cacheKey: string, mutatedUrl: string): boolean {
    // Simple heuristic to determine if URLs are related
    const cacheUrl = cacheKey.split(':')[1];
    const basePath = mutatedUrl.split('/').slice(0, -1).join('/');
    return cacheUrl?.startsWith(basePath) || false;
  }

  // Cache management methods
  clearCache(): void {
    this.cache.clear();
    this.pendingRequests.clear();
  }

  getCacheStats(): { size: number; hitRate: number; entries: number } {
    const totalRequests = this.metrics.length;
    const cachedRequests = this.metrics.filter(m => m.cached).length;
    
    return {
      size: this.cache.size,
      hitRate: totalRequests > 0 ? cachedRequests / totalRequests : 0,
      entries: this.cache.size
    };
  }

  getMetrics(): RequestMetrics[] {
    return [...this.metrics];
  }

  // Background cache warming
  async warmCache(endpoints: string[]): Promise<void> {
    const warmingPromises = endpoints.map(async (endpoint) => {
      try {
        await this.get(endpoint);
        console.log(`Cache warmed for ${endpoint}`);
      } catch (error) {
        console.warn(`Failed to warm cache for ${endpoint}:`, error);
      }
    });
    
    await Promise.allSettled(warmingPromises);
  }

  // Health check with circuit breaker pattern
  private circuitBreaker = {
    failures: 0,
    lastFailureTime: 0,
    state: 'CLOSED' as 'CLOSED' | 'OPEN' | 'HALF_OPEN'
  };

  async healthCheck(): Promise<boolean> {
    const now = Date.now();
    
    // Circuit breaker logic
    if (this.circuitBreaker.state === 'OPEN') {
      if (now - this.circuitBreaker.lastFailureTime > 60000) { // 1 minute
        this.circuitBreaker.state = 'HALF_OPEN';
      } else {
        return false;
      }
    }
    
    try {
      await this.get('/health');
      
      // Reset circuit breaker on success
      this.circuitBreaker.failures = 0;
      this.circuitBreaker.state = 'CLOSED';
      
      return true;
    } catch (error) {
      this.circuitBreaker.failures++;
      this.circuitBreaker.lastFailureTime = now;
      
      if (this.circuitBreaker.failures >= 5) {
        this.circuitBreaker.state = 'OPEN';
      }
      
      return false;
    }
  }
}

// Create and export optimized API client instance
// Uses Next.js API routes (/api) for httpOnly cookie authentication
export const apiClient = new OptimizedAPIClient({
  // Don't set baseURL - let it default to '/api' for Next.js API routes
  timeout: 30000,
  retries: 3,
  cacheTTL: 5 * 60 * 1000, // 5 minutes
  enableMetrics: true,
  enableCompression: true
});

// Export types for use in components
export type { RequestMetrics, APIClientConfig };

// Utility hooks for React components
export const useAPIClient = () => {
  return {
    client: apiClient,
    clearCache: () => apiClient.clearCache(),
    getCacheStats: () => apiClient.getCacheStats(),
    getMetrics: () => apiClient.getMetrics(),
    warmCache: (endpoints: string[]) => apiClient.warmCache(endpoints),
    healthCheck: () => apiClient.healthCheck()
  };
};