/**
 * ApiClient - 统一的APIrequest客户端
 * 
 * feature:
 * - supportGET/POST/PUT/DELETErequest
 * - request去重机制 (1sec内相同request合并)
 * - 并发request限制 (最多6item)
 * - timeout检测andhint (5sec)
 * - 指数退避retry (最多3times)
 * - GETrequestcache (5minTTL)
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { retryWithBackoff, RetryOptions, DEFAULT_API_RETRY_OPTIONS } from '../utils/retryWithBackoff';

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  maxRetries: number;
  maxConcurrent: number;
  cacheTimeout: number; // cache有效期（ms）
  deduplicationWindow?: number; // 去重时间窗口（ms），默认1000ms
  retryOptions?: Partial<RetryOptions>; // 自定义retryconfig
}

export interface RequestOptions extends AxiosRequestConfig {
  skipCache?: boolean;
  skipRetry?: boolean;
  skipDeduplication?: boolean;
  onTimeout?: () => void;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

interface PendingRequest {
  promise: Promise<any>;
  timestamp: number;
}

export class ApiClient {
  private axiosInstance: AxiosInstance;
  private config: ApiClientConfig;
  private cache: Map<string, CacheEntry<any>>;
  private pendingRequests: Map<string, PendingRequest>;
  private activeRequests: number;
  private requestQueue: Array<() => void>;
  private timeoutWarnings: Set<string>;
  private retryOptions: RetryOptions;

  constructor(config: ApiClientConfig) {
    this.config = {
      deduplicationWindow: 1000,
      ...config,
    };

    // 合并默认retryconfigand自定义config
    this.retryOptions = {
      ...DEFAULT_API_RETRY_OPTIONS,
      maxRetries: config.maxRetries,
      ...config.retryOptions,
    };

    this.axiosInstance = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.cache = new Map();
    this.pendingRequests = new Map();
    this.activeRequests = 0;
    this.requestQueue = [];
    this.timeoutWarnings = new Set();

    this.setupInterceptors();
  }

  /**
   * setrequestandresponse拦截器
   */
  private setupInterceptors(): void {
    // request拦截器 - addauth令牌
    this.axiosInstance.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('token');
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // response拦截器 - handle通用error
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // handle未authorize访问
          if (typeof window !== 'undefined') {
            localStorage.removeItem('token');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * GETrequest - 自动cache
   */
  async get<T>(url: string, options: RequestOptions = {}): Promise<T> {
    const cacheKey = this.generateCacheKey('GET', url, options.params);

    // checkcache
    if (!options.skipCache) {
      const cached = this.getFromCache<T>(cacheKey);
      if (cached !== null) {
        return cached;
      }
    }

    // request去重
    if (!options.skipDeduplication) {
      const deduplicated = await this.deduplicateRequest(cacheKey, () =>
        this.executeRequest<T>('GET', url, undefined, options)
      );

      // cacheGETrequestresult
      if (!options.skipCache) {
        this.setCache(cacheKey, deduplicated);
      }

      return deduplicated;
    }

    const result = await this.executeRequest<T>('GET', url, undefined, options);

    // cacheGETrequestresult
    if (!options.skipCache) {
      this.setCache(cacheKey, result);
    }

    return result;
  }

  /**
   * POSTrequest - 不cache
   */
  async post<T>(url: string, data: any, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('POST', url, data, options);
  }

  /**
   * PUTrequest - 不cache
   */
  async put<T>(url: string, data: any, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('PUT', url, data, options);
  }

  /**
   * DELETErequest - 不cache
   */
  async delete<T>(url: string, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('DELETE', url, undefined, options);
  }

  /**
   * executerequest - contain并发控制、retryandtimeouthandle
   */
  private async executeRequest<T>(
    method: string,
    url: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    // 并发控制 - wait直到有可用的并发槽位
    if (this.activeRequests >= this.config.maxConcurrent) {
      await new Promise<void>((resolve) => {
        this.requestQueue.push(resolve);
      });
    }

    // 占用槽位
    this.activeRequests++;

    try {
      const requestFn = async (): Promise<T> => {
        // settimeout监控
        const timeoutId = this.setupTimeoutWarning(url, options.onTimeout);

        try {
          const response: AxiosResponse<T> = await this.axiosInstance.request({
            method,
            url,
            data,
            ...options,
          });

          // 清除timeoutwarn
          clearTimeout(timeoutId);
          this.timeoutWarnings.delete(url);

          return response.data;
        } catch (error) {
          // 清除timeoutwarn
          clearTimeout(timeoutId);
          this.timeoutWarnings.delete(url);
          throw error;
        }
      };

      // 指数退避retry - use工具function
      if (!options.skipRetry) {
        return await retryWithBackoff(requestFn, this.retryOptions);
      }

      return await requestFn();
    } finally {
      // requestcomplete（success或failure），释放槽位
      this.activeRequests--;
      this.processQueue();
    }
  }

  /**
   * handlerequestqueue
   */
  private processQueue(): void {
    if (this.requestQueue.length > 0 && this.activeRequests < this.config.maxConcurrent) {
      const resolve = this.requestQueue.shift();
      if (resolve) {
        resolve();
      }
    }
  }

  /**
   * request去重 - 1sec内相同request合并为单itemrequest
   */
  private async deduplicateRequest<T>(
    key: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const now = Date.now();
    const pending = this.pendingRequests.get(key);

    // 如果存在未complete的相同request且在去重窗口内，return该request的Promise
    if (pending && now - pending.timestamp < this.config.deduplicationWindow!) {
      return pending.promise;
    }

    // create新request
    const promise = fn().finally(() => {
      // requestcomplete后cleanup
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, { promise, timestamp: now });

    return promise;
  }

  /**
   * settimeoutwarn - 5sec后showtimeouthint
   */
  private setupTimeoutWarning(url: string, onTimeout?: () => void): NodeJS.Timeout {
    const timeoutDuration = 5000; // 5sec

    return setTimeout(() => {
      if (!this.timeoutWarnings.has(url)) {
        this.timeoutWarnings.add(url);

        // 调用自定义timeout回调
        if (onTimeout) {
          onTimeout();
        } else {
          // 默认timeouthint
          console.warn(`APIrequesttimeout: ${url} (超过${timeoutDuration / 1000}sec)`);

          // 在浏览器env中showhint
          if (typeof window !== 'undefined') {
            // 可以integration到通知system
            // 这里简单地useconsole.warn，实际shoulduseUI通知component
          }
        }
      }
    }, timeoutDuration);
  }

  /**
   * generatecache键
   */
  private generateCacheKey(method: string, url: string, params?: any): string {
    const paramsStr = params ? JSON.stringify(params) : '';
    return `${method}:${url}:${paramsStr}`;
  }

  /**
   * 从cachegetdata
   */
  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    const now = Date.now();

    // check是否过期
    if (now > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * setcache
   */
  private setCache<T>(key: string, data: T): void {
    const now = Date.now();
    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt: now + this.config.cacheTimeout,
    };

    this.cache.set(key, entry);
  }

  /**
   * 清除cache
   */
  clearCache(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // 清除匹配模式的cache
    const keys = Array.from(this.cache.keys());
    keys.forEach((key) => {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * getcache统计
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * 睡眠function
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * get当前活跃request数
   */
  getActiveRequestCount(): number {
    return this.activeRequests;
  }

  /**
   * getqueue中wait的request数
   */
  getQueuedRequestCount(): number {
    return this.requestQueue.length;
  }
}

// create默认instance的工厂function
export function createDefaultApiClient(): ApiClient {
  const defaultConfig: ApiClientConfig = {
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    maxRetries: 3,
    maxConcurrent: 6,
    cacheTimeout: 5 * 60 * 1000, // 5min
    deduplicationWindow: 1000, // 1sec
  };

  return new ApiClient(defaultConfig);
}

// 默认instance - 延迟初始化
let defaultInstance: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!defaultInstance) {
    defaultInstance = createDefaultApiClient();
  }
  return defaultInstance;
}

// 向后兼容的export
export const apiClient = new Proxy({} as ApiClient, {
  get(target, prop) {
    return getApiClient()[prop as keyof ApiClient];
  },
});
