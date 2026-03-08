/**
 * Integration tests for ApiClient retry mechanism
 * 
 * 验证需求:
 * - 需求 10.3: API请求失败时使用指数退避策略重试，最多重试3次
 */

import { ApiClient, ApiClientConfig } from '../ApiClient';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient Retry Integration', () => {
  let apiClient: ApiClient;
  let mockAxiosInstance: any;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();

    // 创建mock axios实例
    mockAxiosInstance = {
      request: jest.fn(),
      interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() },
      },
    };

    mockedAxios.create.mockReturnValue(mockAxiosInstance);

    const config: ApiClientConfig = {
      baseURL: 'http://localhost:8000/api/v1',
      timeout: 30000,
      maxRetries: 3,
      maxConcurrent: 6,
      cacheTimeout: 5 * 60 * 1000,
    };

    apiClient = new ApiClient(config);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('指数退避重试机制', () => {
    it('应该在网络错误时使用指数退避重试', async () => {
      const networkError: any = new Error('Network Error');
      networkError.code = 'ECONNABORTED';

      // 前2次失败，第3次成功
      mockAxiosInstance.request
        .mockRejectedValueOnce(networkError)
        .mockRejectedValueOnce(networkError)
        .mockResolvedValue({ data: { success: true } });

      const promise = apiClient.get('/test');

      // 运行所有定时器以完成重试
      await jest.runAllTimersAsync();

      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(3);
    });

    it('应该在5xx错误时使用指数退避重试', async () => {
      const serverError: any = new Error('Internal Server Error');
      serverError.response = { status: 500 };

      // 前2次失败，第3次成功
      mockAxiosInstance.request
        .mockRejectedValueOnce(serverError)
        .mockRejectedValueOnce(serverError)
        .mockResolvedValue({ data: { success: true } });

      const promise = apiClient.get('/test');

      await jest.runAllTimersAsync();

      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(3);
    });

    it('应该在429错误时使用指数退避重试', async () => {
      const rateLimitError: any = new Error('Too Many Requests');
      rateLimitError.response = { status: 429 };

      mockAxiosInstance.request
        .mockRejectedValueOnce(rateLimitError)
        .mockResolvedValue({ data: { success: true } });

      const promise = apiClient.get('/test');

      await jest.runAllTimersAsync();

      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);
    });

    it('应该在最多重试3次后抛出错误', async () => {
      const networkError: any = new Error('Persistent Network Error');
      networkError.code = 'ETIMEDOUT';

      mockAxiosInstance.request.mockRejectedValue(networkError);

      const promise = apiClient.get('/test');

      await jest.runAllTimersAsync();

      await expect(promise).rejects.toThrow('Persistent Network Error');
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(4); // 1 initial + 3 retries
    });

    it('应该不重试4xx客户端错误', async () => {
      const clientError: any = new Error('Bad Request');
      clientError.response = { status: 400 };

      mockAxiosInstance.request.mockRejectedValue(clientError);

      const promise = apiClient.get('/test');

      await jest.runAllTimersAsync();

      await expect(promise).rejects.toThrow('Bad Request');
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(1); // No retries
    });

    it('应该支持自定义重试配置', async () => {
      const customConfig: ApiClientConfig = {
        baseURL: 'http://localhost:8000/api/v1',
        timeout: 30000,
        maxRetries: 2, // 只重试2次
        maxConcurrent: 6,
        cacheTimeout: 5 * 60 * 1000,
        retryOptions: {
          initialDelay: 500,
          maxDelay: 5000,
          factor: 3,
        },
      };

      const customClient = new ApiClient(customConfig);

      const networkError: any = new Error('Network Error');
      networkError.code = 'ECONNABORTED';

      mockAxiosInstance.request.mockRejectedValue(networkError);

      const promise = customClient.get('/test');

      await jest.runAllTimersAsync();

      await expect(promise).rejects.toThrow('Network Error');
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(3); // 1 initial + 2 retries
    });
  });

  describe('重试与缓存集成', () => {
    it('应该在重试成功后缓存结果', async () => {
      const networkError: any = new Error('Network Error');
      networkError.code = 'ECONNABORTED';

      mockAxiosInstance.request
        .mockRejectedValueOnce(networkError)
        .mockResolvedValue({ data: { cached: true } });

      // 第一次请求（会重试）
      const promise1 = apiClient.get('/test');
      await jest.runAllTimersAsync();
      const result1 = await promise1;

      expect(result1).toEqual({ cached: true });
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);

      // 第二次请求应该使用缓存
      const result2 = await apiClient.get('/test');

      expect(result2).toEqual({ cached: true });
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2); // 没有新请求
    });
  });

  describe('重试与并发控制集成', () => {
    it('应该在重试时遵守并发限制', async () => {
      const networkError: any = new Error('Network Error');
      networkError.code = 'ECONNABORTED';

      // 所有请求都会失败并重试
      mockAxiosInstance.request.mockRejectedValue(networkError);

      // 发起多个请求
      const promises = [
        apiClient.post('/test1', {}),
        apiClient.post('/test2', {}),
        apiClient.post('/test3', {}),
      ];

      await jest.runAllTimersAsync();

      // 所有请求都应该失败
      await expect(Promise.all(promises)).rejects.toThrow();

      // 每个请求应该重试3次（1 initial + 3 retries = 4 calls per request）
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(12); // 3 requests * 4 calls
    });
  });

  describe('skipRetry选项', () => {
    it('应该支持跳过重试', async () => {
      const networkError: any = new Error('Network Error');
      networkError.code = 'ECONNABORTED';

      mockAxiosInstance.request.mockRejectedValue(networkError);

      const promise = apiClient.get('/test', { skipRetry: true });

      await jest.runAllTimersAsync();

      await expect(promise).rejects.toThrow('Network Error');
      expect(mockAxiosInstance.request).toHaveBeenCalledTimes(1); // No retries
    });
  });
});
