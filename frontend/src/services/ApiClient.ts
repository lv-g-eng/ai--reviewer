/**
 * ApiClient - 统一的API请求客户端
 * 
 * 功能:
 * - 支持GET/POST/PUT/DELETE请求
 * - 请求去重机制 (1秒内相同请求合并)
 * - 并发请求限制 (最多6个)
 * - 超时检测和提示 (5秒)
 * - 指数退避重试 (最多3次)
 * - GET请求缓存 (5分钟TTL)
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { retryWithBackoff, RetryOptions, DEFAULT_API_RETRY_OPTIONS } from '../utils/retryWithBackoff';

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  maxRetries: number;
  maxConcurrent: number;
  cacheTimeout: number; // 缓存有效期（毫秒）
  deduplicationWindow?: number; // 去重时间窗口（毫秒），默认1000ms
  retryOptions?: Partial<RetryOptions>; // 自定义重试配置
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

    // 合并默认重试配置和自定义配置
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
   * 设置请求和响应拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器 - 添加认证令牌
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

    // 响应拦截器 - 处理通用错误
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // 处理未授权访问
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
   * GET请求 - 自动缓存
   */
  async get<T>(url: string, options: RequestOptions = {}): Promise<T> {
    const cacheKey = this.generateCacheKey('GET', url, options.params);

    // 检查缓存
    if (!options.skipCache) {
      const cached = this.getFromCache<T>(cacheKey);
      if (cached !== null) {
        return cached;
      }
    }

    // 请求去重
    if (!options.skipDeduplication) {
      const deduplicated = await this.deduplicateRequest(cacheKey, () =>
        this.executeRequest<T>('GET', url, undefined, options)
      );

      // 缓存GET请求结果
      if (!options.skipCache) {
        this.setCache(cacheKey, deduplicated);
      }

      return deduplicated;
    }

    const result = await this.executeRequest<T>('GET', url, undefined, options);

    // 缓存GET请求结果
    if (!options.skipCache) {
      this.setCache(cacheKey, result);
    }

    return result;
  }

  /**
   * POST请求 - 不缓存
   */
  async post<T>(url: string, data: any, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('POST', url, data, options);
  }

  /**
   * PUT请求 - 不缓存
   */
  async put<T>(url: string, data: any, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('PUT', url, data, options);
  }

  /**
   * DELETE请求 - 不缓存
   */
  async delete<T>(url: string, options: RequestOptions = {}): Promise<T> {
    return this.executeRequest<T>('DELETE', url, undefined, options);
  }

  /**
   * 执行请求 - 包含并发控制、重试和超时处理
   */
  private async executeRequest<T>(
    method: string,
    url: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    // 并发控制 - 等待直到有可用的并发槽位
    if (this.activeRequests >= this.config.maxConcurrent) {
      await new Promise<void>((resolve) => {
        this.requestQueue.push(resolve);
      });
    }

    // 占用槽位
    this.activeRequests++;

    try {
      const requestFn = async (): Promise<T> => {
        // 设置超时监控
        const timeoutId = this.setupTimeoutWarning(url, options.onTimeout);

        try {
          const response: AxiosResponse<T> = await this.axiosInstance.request({
            method,
            url,
            data,
            ...options,
          });

          // 清除超时警告
          clearTimeout(timeoutId);
          this.timeoutWarnings.delete(url);

          return response.data;
        } catch (error) {
          // 清除超时警告
          clearTimeout(timeoutId);
          this.timeoutWarnings.delete(url);
          throw error;
        }
      };

      // 指数退避重试 - 使用工具函数
      if (!options.skipRetry) {
        return await retryWithBackoff(requestFn, this.retryOptions);
      }

      return await requestFn();
    } finally {
      // 请求完成（成功或失败），释放槽位
      this.activeRequests--;
      this.processQueue();
    }
  }

  /**
   * 处理请求队列
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
   * 请求去重 - 1秒内相同请求合并为单个请求
   */
  private async deduplicateRequest<T>(
    key: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const now = Date.now();
    const pending = this.pendingRequests.get(key);

    // 如果存在未完成的相同请求且在去重窗口内，返回该请求的Promise
    if (pending && now - pending.timestamp < this.config.deduplicationWindow!) {
      return pending.promise;
    }

    // 创建新请求
    const promise = fn().finally(() => {
      // 请求完成后清理
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, { promise, timestamp: now });

    return promise;
  }

  /**
   * 设置超时警告 - 5秒后显示超时提示
   */
  private setupTimeoutWarning(url: string, onTimeout?: () => void): NodeJS.Timeout {
    const timeoutDuration = 5000; // 5秒

    return setTimeout(() => {
      if (!this.timeoutWarnings.has(url)) {
        this.timeoutWarnings.add(url);

        // 调用自定义超时回调
        if (onTimeout) {
          onTimeout();
        } else {
          // 默认超时提示
          console.warn(`API请求超时: ${url} (超过${timeoutDuration / 1000}秒)`);

          // 在浏览器环境中显示提示
          if (typeof window !== 'undefined') {
            // 可以集成到通知系统
            // 这里简单地使用console.warn，实际应该使用UI通知组件
          }
        }
      }
    }, timeoutDuration);
  }

  /**
   * 生成缓存键
   */
  private generateCacheKey(method: string, url: string, params?: any): string {
    const paramsStr = params ? JSON.stringify(params) : '';
    return `${method}:${url}:${paramsStr}`;
  }

  /**
   * 从缓存获取数据
   */
  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    const now = Date.now();

    // 检查是否过期
    if (now > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * 设置缓存
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
   * 清除缓存
   */
  clearCache(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    // 清除匹配模式的缓存
    const keys = Array.from(this.cache.keys());
    keys.forEach((key) => {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * 获取缓存统计
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * 睡眠函数
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * 获取当前活跃请求数
   */
  getActiveRequestCount(): number {
    return this.activeRequests;
  }

  /**
   * 获取队列中等待的请求数
   */
  getQueuedRequestCount(): number {
    return this.requestQueue.length;
  }
}

// 创建默认实例的工厂函数
export function createDefaultApiClient(): ApiClient {
  const defaultConfig: ApiClientConfig = {
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    maxRetries: 3,
    maxConcurrent: 6,
    cacheTimeout: 5 * 60 * 1000, // 5分钟
    deduplicationWindow: 1000, // 1秒
  };

  return new ApiClient(defaultConfig);
}

// 默认实例 - 延迟初始化
let defaultInstance: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!defaultInstance) {
    defaultInstance = createDefaultApiClient();
  }
  return defaultInstance;
}

// 向后兼容的导出
export const apiClient = new Proxy({} as ApiClient, {
  get(target, prop) {
    return getApiClient()[prop as keyof ApiClient];
  },
});
