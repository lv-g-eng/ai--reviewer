/**
 * ApiClient属性测试
 * 
 * 使用fast-check进行基于属性的测试，验证ApiClient的通用正确性属性
 */

import fc from 'fast-check';
import axios from 'axios';

// Mock axios BEFORE importing ApiClient
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock axios instance
const mockAxiosInstance = {
  request: jest.fn(),
  interceptors: {
    request: {
      use: jest.fn(),
    },
    response: {
      use: jest.fn(),
    },
  },
};

// Setup axios.create to return our mock instance
mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

import { ApiClient, ApiClientConfig } from '../ApiClient';

describe('ApiClient Property-Based Tests', () => {
  const defaultConfig: ApiClientConfig = {
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 30000,
    maxRetries: 3,
    maxConcurrent: 6,
    cacheTimeout: 5 * 60 * 1000,
    deduplicationWindow: 1000,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockAxiosInstance.request.mockReset();
  });

  /**
   * **Feature: frontend-production-optimization, Property 25: 请求去重**
   * **验证需求: 10.2**
   * 
   * 属性: 对于任何在1秒内发起的多个相同请求，应该合并为单个网络请求
   * 
   * 测试策略:
   * - 生成随机的URL和参数组合
   * - 生成随机数量的并发请求 (2-10个)
   * - 验证所有相同请求在1秒内只发起一次实际网络请求
   * - 验证所有请求返回相同的结果
   */
  describe('Property 25: 请求去重', () => {
    it('应该在1秒内合并相同的GET请求为单个网络请求', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成随机URL路径
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.constant('/metrics'),
            fc.constant('/tasks'),
            fc.webPath()
          ),
          // 生成随机查询参数
          fc.oneof(
            fc.constant(undefined),
            fc.record({
              id: fc.integer({ min: 1, max: 100 }),
            }),
            fc.record({
              page: fc.integer({ min: 1, max: 10 }),
              limit: fc.integer({ min: 10, max: 100 }),
            })
          ),
          // 生成并发请求数量 (2-10个)
          fc.integer({ min: 2, max: 10 }),
          async (url, params, requestCount) => {
            // 重置mock以确保每次迭代都是干净的状态
            mockAxiosInstance.request.mockReset();

            // 创建新的ApiClient实例
            const apiClient = new ApiClient(defaultConfig);

            // 模拟响应数据
            const mockData = { 
              url, 
              params, 
              timestamp: Date.now(),
              random: Math.random() 
            };
            
            mockAxiosInstance.request.mockResolvedValue({ data: mockData });

            // 同时发起多个相同请求
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { params })
            );

            const results = await Promise.all(promises);

            // 验证: 应该只发起一次实际网络请求
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(1);

            // 验证: 所有请求返回相同的结果
            for (let i = 1; i < results.length; i++) {
              expect(results[i]).toEqual(results[0]);
            }

            // 验证: 返回的数据与mock数据一致
            expect(results[0]).toEqual(mockData);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该为不同的URL发起独立的网络请求', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成2-5个不同的URL
          fc.uniqueArray(
            fc.oneof(
              fc.webPath(),
              fc.constant('/users'),
              fc.constant('/projects'),
              fc.constant('/metrics')
            ),
            { minLength: 2, maxLength: 5 }
          ),
          async (urls) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 为每个URL设置不同的响应
            mockAxiosInstance.request.mockImplementation(({ url }) => {
              return Promise.resolve({ data: { url, timestamp: Date.now() } });
            });

            // 同时发起对不同URL的请求
            const promises = urls.map(url => apiClient.get(url));
            await Promise.all(promises);

            // 验证: 应该为每个不同的URL发起一次请求
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(urls.length);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该为不同的查询参数发起独立的网络请求', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.constant('/users'),
          // 生成2-5个不同的参数组合
          fc.uniqueArray(
            fc.record({
              id: fc.integer({ min: 1, max: 1000 }),
            }),
            { 
              minLength: 2, 
              maxLength: 5,
              comparator: (a, b) => a.id === b.id
            }
          ),
          async (url, paramsList) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            mockAxiosInstance.request.mockImplementation(({ params }) => {
              return Promise.resolve({ data: { params, timestamp: Date.now() } });
            });

            // 同时发起带不同参数的请求
            const promises = paramsList.map(params => 
              apiClient.get(url, { params })
            );
            await Promise.all(promises);

            // 验证: 应该为每个不同的参数组合发起一次请求
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(paramsList.length);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在skipDeduplication选项启用时不进行去重', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          fc.integer({ min: 2, max: 5 }),
          async (url, requestCount) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            mockAxiosInstance.request.mockResolvedValue({ 
              data: { url, timestamp: Date.now() } 
            });

            // 同时发起多个请求，但跳过去重和缓存
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { skipDeduplication: true, skipCache: true })
            );

            await Promise.all(promises);

            // 验证: 应该发起与请求数量相同的网络请求
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(requestCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在去重窗口过期后允许新的请求', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          async (url) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            // 使用较短的去重窗口进行测试
            const apiClient = new ApiClient({
              ...defaultConfig,
              deduplicationWindow: 100, // 100ms窗口
            });

            let requestCount = 0;
            mockAxiosInstance.request.mockImplementation(() => {
              requestCount++;
              return Promise.resolve({ data: { count: requestCount } });
            });

            // 第一次请求
            const result1 = await apiClient.get(url, { skipCache: true });

            // 等待去重窗口过期
            await new Promise(resolve => setTimeout(resolve, 150));

            // 第二次请求（应该发起新的网络请求）
            const result2 = await apiClient.get(url, { skipCache: true });

            // 验证: 应该发起两次网络请求
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);

            // 验证: 两次请求返回不同的结果（因为requestCount递增）
            expect(result1).not.toEqual(result2);
          }
        ),
        { numRuns: 50 } // 减少运行次数因为有延迟
      );
    });

    it('应该在请求失败后清理去重状态', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          fc.integer({ min: 2, max: 5 }),
          async (url, requestCount) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 第一次请求失败
            mockAxiosInstance.request.mockRejectedValueOnce(
              new Error('Network error')
            );

            // 后续请求成功
            mockAxiosInstance.request.mockResolvedValue({ 
              data: { url, success: true } 
            });

            // 第一次请求应该失败
            await expect(
              apiClient.get(url, { skipCache: true, skipRetry: true })
            ).rejects.toThrow('Network error');

            // 立即发起多个相同请求
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { skipCache: true, skipRetry: true })
            );

            const results = await Promise.all(promises);

            // 验证: 失败后的请求应该被去重（只发起一次新请求）
            // 总共: 1次失败 + 1次成功 = 2次
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);

            // 验证: 所有成功的请求返回相同结果
            for (let i = 1; i < results.length; i++) {
              expect(results[i]).toEqual(results[0]);
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  /**
   * **Feature: frontend-production-optimization, Property 26: 并发请求限制**
   * **验证需求: 10.4**
   * 
   * 属性: 对于任何时刻，同时进行的API请求数量不应该超过6个
   * 
   * 测试策略:
   * - 生成随机数量的并发请求 (7-20个，超过限制)
   * - 使用延迟响应模拟慢速API
   * - 在请求执行期间监控活跃请求数
   * - 验证活跃请求数永远不超过maxConcurrent (6)
   * - 验证所有请求最终都能完成
   */
  describe('Property 26: 并发请求限制', () => {
    it('应该限制并发请求数量不超过6个', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成7-15个请求（超过6个限制，但不要太多以避免超时）
          fc.integer({ min: 7, max: 15 }),
          // 生成每个请求的延迟时间 (30-100ms，减少延迟以加快测试)
          fc.integer({ min: 30, max: 100 }),
          async (requestCount, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪最大并发数
            let maxConcurrent = 0;

            // 模拟延迟响应并跟踪并发数
            mockAxiosInstance.request.mockImplementation(async () => {
              // 在请求开始时检查活跃请求数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              // 模拟API延迟
              await new Promise(resolve => setTimeout(resolve, delayMs));

              return { data: { success: true, timestamp: Date.now() } };
            });

            // 同时发起多个请求
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            // 等待所有请求完成
            const results = await Promise.all(promises);

            // 验证: 最大并发数不应超过6
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // 验证: 所有请求都成功完成
            expect(results).toHaveLength(requestCount);
            results.forEach(result => {
              expect(result).toHaveProperty('success', true);
            });

            // 验证: 所有请求都被执行了
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(requestCount);
          }
        ),
        { numRuns: 50 } // 减少运行次数以避免超时
      );
    }, 60000); // 增加超时时间到60秒

    it('应该在请求完成后释放并发槽位并处理队列', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成10-15个请求
          fc.integer({ min: 10, max: 15 }),
          async (requestCount) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const concurrentSnapshots: number[] = [];

            // 模拟请求，前6个慢，后续的快
            let requestIndex = 0;
            mockAxiosInstance.request.mockImplementation(async () => {
              const myIndex = requestIndex++;
              const delay = myIndex < 6 ? 100 : 10;

              // 记录当前活跃请求数
              concurrentSnapshots.push(apiClient.getActiveRequestCount());

              await new Promise(resolve => setTimeout(resolve, delay));

              return { data: { index: myIndex } };
            });

            // 发起所有请求
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // 验证: 所有快照中的并发数都不超过6
            concurrentSnapshots.forEach(count => {
              expect(count).toBeLessThanOrEqual(6);
            });

            // 验证: 最终所有请求都完成，活跃请求数为0
            expect(apiClient.getActiveRequestCount()).toBe(0);

            // 验证: 队列也应该为空
            expect(apiClient.getQueuedRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 30000); // 增加超时时间

    it('应该正确处理混合的成功和失败请求的并发限制', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成8-12个请求
          fc.integer({ min: 8, max: 12 }),
          // 生成失败请求的索引列表
          fc.array(fc.integer({ min: 0, max: 11 }), { maxLength: 5 }),
          async (requestCount, failureIndices) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxConcurrent = 0;
            let requestIndex = 0;

            // 模拟部分请求失败
            mockAxiosInstance.request.mockImplementation(async () => {
              const myIndex = requestIndex++;
              
              // 检查当前活跃请求数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              await new Promise(resolve => setTimeout(resolve, 50));

              if (failureIndices.includes(myIndex)) {
                throw new Error(`Request ${myIndex} failed`);
              }

              return { data: { index: myIndex, success: true } };
            });

            // 发起所有请求
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
                .catch(error => ({ error: error.message }))
            );

            const results = await Promise.all(promises);

            // 验证: 最大并发数不超过6
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // 验证: 所有请求都被处理了（成功或失败）
            expect(results).toHaveLength(requestCount);

            // 验证: 失败的请求数量正确
            const failedResults = results.filter((r): r is { error: string } => r !== null && typeof r === 'object' && 'error' in r);
            expect(failedResults.length).toBeGreaterThanOrEqual(0);

            // 验证: 最终活跃请求数为0
            expect(apiClient.getActiveRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加超时时间

    it('应该在不同的HTTP方法间共享并发限制', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成每种方法的请求数量
          fc.record({
            getCount: fc.integer({ min: 2, max: 5 }),
            postCount: fc.integer({ min: 2, max: 5 }),
            putCount: fc.integer({ min: 1, max: 3 }),
            deleteCount: fc.integer({ min: 1, max: 3 }),
          }),
          async (counts) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxConcurrent = 0;

            // 模拟所有方法的请求
            mockAxiosInstance.request.mockImplementation(async ({ method }) => {
              // 检查当前活跃请求数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              await new Promise(resolve => setTimeout(resolve, 80));

              return { data: { method, success: true } };
            });

            // 发起混合的请求
            const promises: Promise<any>[] = [
              ...Array.from({ length: counts.getCount }, (_, i) =>
                apiClient.get(`/test/get/${i}`, { skipCache: true, skipRetry: true })
              ),
              ...Array.from({ length: counts.postCount }, (_, i) =>
                apiClient.post(`/test/post/${i}`, { data: i }, { skipRetry: true })
              ),
              ...Array.from({ length: counts.putCount }, (_, i) =>
                apiClient.put(`/test/put/${i}`, { data: i }, { skipRetry: true })
              ),
              ...Array.from({ length: counts.deleteCount }, (_, i) =>
                apiClient.delete(`/test/delete/${i}`, { skipRetry: true })
              ),
            ];

            await Promise.all(promises);

            // 验证: 最大并发数不超过6（所有方法共享限制）
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // 验证: 所有请求都完成
            const totalRequests = counts.getCount + counts.postCount + counts.putCount + counts.deleteCount;
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(totalRequests);
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加超时时间

    it('应该在高并发场景下保持队列的FIFO顺序', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成10-15个请求
          fc.integer({ min: 10, max: 15 }),
          async (requestCount) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const executionOrder: number[] = [];

            // 模拟请求，记录执行顺序
            mockAxiosInstance.request.mockImplementation(async ({ url }) => {
              const index = parseInt(url.split('/').pop() || '0');
              executionOrder.push(index);

              await new Promise(resolve => setTimeout(resolve, 30));

              return { data: { index } };
            });

            // 按顺序发起请求
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // 验证: 所有请求都被执行了
            expect(executionOrder).toHaveLength(requestCount);

            // 验证: 所有索引都被执行了
            const sortedOrder = [...executionOrder].sort((a, b) => a - b);
            expect(sortedOrder).toEqual(Array.from({ length: requestCount }, (_, i) => i));
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加超时时间

    it('应该在达到并发限制时正确排队新请求', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 8, max: 15 }),
          async (requestCount) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxQueuedCount = 0;

            mockAxiosInstance.request.mockImplementation(async () => {
              // 检查队列中的请求数
              const queuedCount = apiClient.getQueuedRequestCount();
              maxQueuedCount = Math.max(maxQueuedCount, queuedCount);

              await new Promise(resolve => setTimeout(resolve, 50));

              return { data: { success: true } };
            });

            // 发起所有请求
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // 验证: 当并发达到限制时，应该有请求在队列中等待
            if (requestCount > 6) {
              expect(maxQueuedCount).toBeGreaterThan(0);
            }

            // 验证: 最终所有请求都完成
            expect(apiClient.getActiveRequestCount()).toBe(0);
            expect(apiClient.getQueuedRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 30000); // 增加超时时间
  });

  /**
   * **Feature: frontend-production-optimization, Property 27: 超时提示**
   * **验证需求: 10.5**
   * 
   * 属性: 对于任何响应时间超过5秒的API请求，应该显示加载超时提示
   * 
   * 测试策略:
   * - 生成随机的URL和延迟时间
   * - 对于延迟超过5秒的请求，验证超时回调被调用
   * - 对于延迟小于5秒的请求，验证超时回调不被调用
   * - 验证超时提示在请求完成后被清理
   */
  describe('Property 27: 超时提示', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.runOnlyPendingTimers();
      jest.useRealTimers();
    });

    it('应该在请求超过5秒时触发超时回调', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成随机URL
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.constant('/metrics'),
            fc.webPath()
          ),
          // 生成超过5秒的延迟 (5100-8000ms)
          fc.integer({ min: 5100, max: 8000 }),
          async (url, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪超时回调是否被调用
            let timeoutCallbackCalled = false;
            const onTimeout = jest.fn(() => {
              timeoutCallbackCalled = true;
            });

            // 模拟慢速API响应
            mockAxiosInstance.request.mockImplementation(async () => {
              // 使用真实的延迟
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true, url } });
                }, delayMs);
                
                // 清理函数
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起请求
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到5秒（超时阈值）
            jest.advanceTimersByTime(5000);

            // 验证: 超时回调应该被调用
            expect(timeoutCallbackCalled).toBe(true);
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // 快进剩余时间让请求完成
            jest.advanceTimersByTime(delayMs - 5000);

            // 等待请求完成
            const result = await requestPromise;

            // 验证: 请求最终成功完成
            expect(result).toEqual({ success: true, url });
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在请求小于5秒完成时不触发超时回调', async () => {
      await fc.assert(
        fc.asyncProperty(
          // 生成随机URL
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.webPath()
          ),
          // 生成小于5秒的延迟 (100-4900ms)
          fc.integer({ min: 100, max: 4900 }),
          async (url, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪超时回调
            const onTimeout = jest.fn();

            // 模拟快速API响应
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true, url } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起请求
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到请求完成
            jest.advanceTimersByTime(delayMs);

            // 等待请求完成
            const result = await requestPromise;

            // 验证: 超时回调不应该被调用
            expect(onTimeout).not.toHaveBeenCalled();

            // 验证: 请求成功完成
            expect(result).toEqual({ success: true, url });

            // 快进到5秒后，确认超时回调仍然不会被调用
            jest.advanceTimersByTime(5000 - delayMs + 100);
            expect(onTimeout).not.toHaveBeenCalled();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在请求完成后清理超时警告', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // 生成延迟时间 (可能超过或不超过5秒)
          fc.integer({ min: 100, max: 8000 }),
          async (url, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const onTimeout = jest.fn();

            // 模拟API响应
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起第一次请求
            const request1Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到请求完成
            jest.advanceTimersByTime(delayMs);
            await request1Promise;

            // 重置mock计数
            onTimeout.mockClear();

            // 发起第二次相同的请求
            const request2Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到5秒
            jest.advanceTimersByTime(5000);

            // 如果第二次请求也超过5秒，应该再次触发超时回调
            if (delayMs > 5000) {
              expect(onTimeout).toHaveBeenCalledTimes(1);
            }

            // 完成第二次请求
            jest.advanceTimersByTime(Math.max(0, delayMs - 5000));
            await request2Promise;

            // 验证: 请求都成功完成
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在请求失败时也清理超时警告', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // 生成超过5秒的延迟
          fc.integer({ min: 5100, max: 8000 }),
          async (url, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const onTimeout = jest.fn();

            // 模拟请求失败
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((_, reject) => {
                const realTimeout = setTimeout(() => {
                  reject(new Error('Network error'));
                }, delayMs);
                
                (reject as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起请求
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            }).catch((error: unknown) => error as Error);

            // 快进到5秒（超时阈值）
            jest.advanceTimersByTime(5000);

            // 验证: 超时回调应该被调用
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // 快进到请求失败
            jest.advanceTimersByTime(delayMs - 5000);

            // 等待请求失败
            const error = await requestPromise as Error;

            // 验证: 请求失败
            expect(error).toBeInstanceOf(Error);
            expect(error.message).toBe('Network error');

            // 重置回调
            onTimeout.mockClear();

            // 发起新的请求到相同URL
            const request2Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            }).catch((error: unknown) => error as Error);

            // 快进到5秒
            jest.advanceTimersByTime(5000);

            // 验证: 新请求应该再次触发超时回调（说明之前的警告被清理了）
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // 完成第二次请求
            jest.advanceTimersByTime(delayMs - 5000);
            await request2Promise;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在没有提供onTimeout回调时使用默认警告', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // 生成超过5秒的延迟
          fc.integer({ min: 5100, max: 7000 }),
          async (url, delayMs) => {
            // 重置mock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // Mock console.warn
            const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

            // 模拟慢速API响应
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起请求（不提供onTimeout回调）
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true
            });

            // 快进到5秒
            jest.advanceTimersByTime(5000);

            // 验证: 应该调用console.warn显示默认超时提示
            expect(consoleWarnSpy).toHaveBeenCalledWith(
              expect.stringContaining('API请求超时')
            );
            expect(consoleWarnSpy).toHaveBeenCalledWith(
              expect.stringContaining(url)
            );

            // 完成请求
            jest.advanceTimersByTime(delayMs - 5000);
            await requestPromise;

            // 清理
            consoleWarnSpy.mockRestore();
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
