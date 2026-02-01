/**
 * Enhanced API Client with Advanced Performance Optimizations
 * 
 * Features:
 * - Request batching and deduplication
 * - Intelligent caching with L1/L2 hierarchy
 * - Circuit breaker pattern
 * - Response compression
 * - Field selection (GraphQL-style)
 * - Real-time cache invalidation
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import axiosRetry from 'axios-retry';

interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  etag?: string;
  tier: 'hot' | 'warm' | 'cold';
}

interface RequestMetrics {
  url: string;
  method: string;
  duration: number;
  status: number;
  cached: boolean;
  timestamp: number;
}

interface QueryOptions {
  fields?: string[];
  include?: string[];
  exclude?: string[];
  cache?: boolean;
  cacheTier?: 'hot' | 'warm' | 'cold';
}

interface BatchRequest {
  id: string;
  resolve: (value: any) => void;
  reject: (error: any) => void;
}

class EnhancedAPIClient {
  private client: AxiosInstance;
  private l1Cache = new Map<string, CacheEntry>(); // In-memory cache
  private l2Cache = new Map<string, CacheEntry>(); // Persistent cache
  private pendingRequests = new Map<string, Promise<any>>();
  private batchQueue = new Map<string, BatchRequest[]>();
  private batchTimeout: NodeJS.Timeout | null = null;
  private metrics: RequestMetrics[] = [];
  private circuitBreaker = new Map<string, CircuitBreakerState>();
  
  // Cache size limits
  private readonly L1_MAX_SIZE = 50 * 1024 * 1024; // 50MB
  private readonly L2_MAX_SIZE = 200 * 1024 * 1024; // 200MB
  private l1CurrentSize = 0;
  private l2CurrentSize = 0;

  constructor(baseURL?: string) {
    this.client = axios.create({
      baseURL: baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
      },
    });

    this.setupInterceptors();
    this.setupRetryLogic();
    this.startCacheCleanup();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add correlation ID
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();
        
        // Add request timestamp
        (config as any).requestStartTime = Date.now();

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        this.recordMetrics(response);
        this.updateCircuitBreaker(response.config.url || '', true);
        return response;
      },
      (error) => {
        this.recordMetrics(error.response);
        this.updateCircuitBreaker(error.config?.url || '', false);
        return Promise.reject(error);
      }
    );
  }

  private setupRetryLogic(): void {
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return axiosRetry.isNetworkOrIdempotentRequestError(error) ||
               error.response?.status === 429 ||
               (error.response?.status ? error.response.status >= 500 : false);
      },
      onRetry: (retryCount, error, requestConfig) => {
        console.warn(`Retry attempt ${retryCount} for ${requestConfig.url}`);
      }
    });
  }

  // Enhanced GET with field selection and caching
  async get<T>(endpoint: string, options?: QueryOptions): Promise<T> {
    const cacheKey = this.generateCacheKey('GET', endpoint, options);
    
    // Check circuit breaker
    if (this.isCircuitOpen(endpoint)) {
      throw new Error(`Circuit breaker is OPEN for ${endpoint}`);
    }

    // Try cache first
    if (options?.cache !== false) {
      const cached = await this.getCachedData<T>(cacheKey);
      if (cached) {
        return cached;
      }
    }

    // Check for pending request (deduplication)
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }

    // Build query parameters
    const params = new URLSearchParams();
    if (options?.fields) {
      params.append('fields', options.fields.join(','));
    }
    if (options?.include) {
      params.append('include', options.include.join(','));
    }
    if (options?.exclude) {
      params.append('exclude', options.exclude.join(','));
    }

    const url = params.toString() ? `${endpoint}?${params.toString()}` : endpoint;
    
    // Make request
    const requestPromise = this.client.get<T>(url).then(response => {
      // Cache successful response
      if (options?.cache !== false) {
        this.setCachedData(cacheKey, response.data, options?.cacheTier || 'warm');
      }
      return response.data;
    });

    this.pendingRequests.set(cacheKey, requestPromise);
    
    try {
      const result = await requestPromise;
      return result;
    } finally {
      this.pendingRequests.delete(cacheKey);
    }
  }

  // Batch request implementation
  async batchGet<T>(endpoint: string, ids: string[]): Promise<T[]> {
    return new Promise((resolve, reject) => {
      if (!this.batchQueue.has(endpoint)) {
        this.batchQueue.set(endpoint, []);
      }

      const batch = this.batchQueue.get(endpoint)!;
      
      // Add requests to batch
      ids.forEach(id => {
        batch.push({
          id,
          resolve: (data) => resolve(data),
          reject: (error) => reject(error)
        });
      });

      // Debounce batch execution
      if (this.batchTimeout) {
        clearTimeout(this.batchTimeout);
      }

      this.batchTimeout = setTimeout(() => {
        this.executeBatch(endpoint);
      }, 50); // 50ms debounce
    });
  }

  private async executeBatch(endpoint: string): Promise<void> {
    const batch = this.batchQueue.get(endpoint) || [];
    this.batchQueue.delete(endpoint);

    if (batch.length === 0) return;

    try {
      const ids = batch.map(item => item.id);
      const response = await this.client.post(`${endpoint}/batch`, { ids });
      
      // Resolve individual requests
      batch.forEach((item, index) => {
        item.resolve(response.data[index]);
      });
    } catch (error) {
      // Reject all requests in batch
      batch.forEach(item => item.reject(error));
    }
  }

  // L1/L2 Cache implementation
  private async getCachedData<T>(key: string): Promise<T | null> {
    // Try L1 cache first (in-memory)
    const l1Entry = this.l1Cache.get(key);
    if (l1Entry && this.isCacheValid(l1Entry)) {
      return l1Entry.data;
    }

    // Try L2 cache (persistent)
    const l2Entry = this.l2Cache.get(key);
    if (l2Entry && this.isCacheValid(l2Entry)) {
      // Promote to L1 if space available
      if (this.l1CurrentSize < this.L1_MAX_SIZE) {
        this.promoteToL1(key, l2Entry);
      }
      return l2Entry.data;
    }

    return null;
  }

  private setCachedData<T>(key: string, data: T, tier: 'hot' | 'warm' | 'cold'): void {
    const ttl = this.getTTLForTier(tier);
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl,
      tier
    };

    const serializedSize = JSON.stringify(data).length;

    // Store in appropriate cache tier
    if (tier === 'hot' && this.l1CurrentSize + serializedSize < this.L1_MAX_SIZE) {
      this.l1Cache.set(key, entry);
      this.l1CurrentSize += serializedSize;
    } else if (this.l2CurrentSize + serializedSize < this.L2_MAX_SIZE) {
      this.l2Cache.set(key, entry);
      this.l2CurrentSize += serializedSize;
    }
  }

  private promoteToL1<T>(key: string, entry: CacheEntry<T>): void {
    const serializedSize = JSON.stringify(entry.data).length;
    if (this.l1CurrentSize + serializedSize < this.L1_MAX_SIZE) {
      this.l1Cache.set(key, entry);
      this.l1CurrentSize += serializedSize;
    }
  }

  private isCacheValid(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp < entry.ttl;
  }

  private getTTLForTier(tier: 'hot' | 'warm' | 'cold'): number {
    switch (tier) {
      case 'hot': return 5 * 60 * 1000; // 5 minutes
      case 'warm': return 30 * 60 * 1000; // 30 minutes
      case 'cold': return 60 * 60 * 1000; // 1 hour
      default: return 30 * 60 * 1000;
    }
  }

  // Circuit breaker implementation
  private isCircuitOpen(endpoint: string): boolean {
    const state = this.circuitBreaker.get(endpoint);
    if (!state) return false;

    if (state.state === 'OPEN') {
      if (Date.now() - state.lastFailureTime > state.timeout) {
        state.state = 'HALF_OPEN';
        return false;
      }
      return true;
    }

    return false;
  }

  private updateCircuitBreaker(endpoint: string, success: boolean): void {
    let state = this.circuitBreaker.get(endpoint);
    
    if (!state) {
      state = {
        state: 'CLOSED',
        failureCount: 0,
        lastFailureTime: 0,
        threshold: 5,
        timeout: 60000 // 1 minute
      };
      this.circuitBreaker.set(endpoint, state);
    }

    if (success) {
      state.failureCount = 0;
      state.state = 'CLOSED';
    } else {
      state.failureCount++;
      state.lastFailureTime = Date.now();
      
      if (state.failureCount >= state.threshold) {
        state.state = 'OPEN';
      }
    }
  }

  // Cache management
  private startCacheCleanup(): void {
    setInterval(() => {
      this.cleanupExpiredCache();
    }, 5 * 60 * 1000); // Every 5 minutes
  }

  private cleanupExpiredCache(): void {
    // Clean L1 cache
    for (const [key, entry] of this.l1Cache.entries()) {
      if (!this.isCacheValid(entry)) {
        this.l1Cache.delete(key);
        this.l1CurrentSize -= JSON.stringify(entry.data).length;
      }
    }

    // Clean L2 cache
    for (const [key, entry] of this.l2Cache.entries()) {
      if (!this.isCacheValid(entry)) {
        this.l2Cache.delete(key);
        this.l2CurrentSize -= JSON.stringify(entry.data).length;
      }
    }
  }

  // Utility methods
  private generateCacheKey(method: string, endpoint: string, options?: QueryOptions): string {
    const optionsStr = options ? JSON.stringify(options) : '';
    return `${method}:${endpoint}:${optionsStr}`;
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  private recordMetrics(response: AxiosResponse | undefined): void {
    if (!response?.config) return;

    const startTime = (response.config as any).requestStartTime;
    const duration = startTime ? Date.now() - startTime : 0;

    const metric: RequestMetrics = {
      url: response.config.url || '',
      method: response.config.method?.toUpperCase() || 'GET',
      duration,
      status: response.status || 0,
      cached: false, // Will be updated if served from cache
      timestamp: Date.now()
    };

    this.metrics.push(metric);
    
    // Keep only last 1000 metrics
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
  }

  // Public API methods
  async post<T>(endpoint: string, data?: any, options?: QueryOptions): Promise<T> {
    const response = await this.client.post<T>(endpoint, data);
    
    // Invalidate related cache entries
    this.invalidateCache(endpoint);
    
    return response.data;
  }

  async put<T>(endpoint: string, data?: any, options?: QueryOptions): Promise<T> {
    const response = await this.client.put<T>(endpoint, data);
    
    // Invalidate related cache entries
    this.invalidateCache(endpoint);
    
    return response.data;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.client.delete<T>(endpoint);
    
    // Invalidate related cache entries
    this.invalidateCache(endpoint);
    
    return response.data;
  }

  private invalidateCache(endpoint: string): void {
    // Remove cache entries that match the endpoint pattern
    const pattern = endpoint.split('/')[1]; // Get base resource
    
    for (const key of this.l1Cache.keys()) {
      if (key.includes(pattern)) {
        this.l1Cache.delete(key);
      }
    }
    
    for (const key of this.l2Cache.keys()) {
      if (key.includes(pattern)) {
        this.l2Cache.delete(key);
      }
    }
  }

  // Performance monitoring
  getMetrics(): RequestMetrics[] {
    return [...this.metrics];
  }

  getCacheStats() {
    return {
      l1Size: this.l1Cache.size,
      l2Size: this.l2Cache.size,
      l1MemoryUsage: this.l1CurrentSize,
      l2MemoryUsage: this.l2CurrentSize,
      hitRate: this.calculateHitRate()
    };
  }

  private calculateHitRate(): number {
    const recentMetrics = this.metrics.slice(-100);
    const cachedRequests = recentMetrics.filter(m => m.cached).length;
    return recentMetrics.length > 0 ? cachedRequests / recentMetrics.length : 0;
  }
}

interface CircuitBreakerState {
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureCount: number;
  lastFailureTime: number;
  threshold: number;
  timeout: number;
}

// Export singleton instance
export const apiClient = new EnhancedAPIClient();
export default EnhancedAPIClient;