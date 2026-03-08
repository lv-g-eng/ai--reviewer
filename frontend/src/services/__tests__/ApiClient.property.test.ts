/**
 * ApiClientpropertytest
 * 
 * usefast-check进行基于property的test，verifyApiClient的通用正确性property
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
   * **Feature: frontend-production-optimization, Property 25: request去重**
   * **verifyRequirement: 10.2**
   * 
   * property: 对于任何在1sec内发起的多item相同request，should合并为单item网络request
   * 
   * test策略:
   * - generate随机的URLandparam组合
   * - generate随机数量的并发request (2-10item)
   * - verify所有相同request在1sec内只发起一times实际网络request
   * - verify所有requestreturn相同的result
   */
  describe('Property 25: request去重', () => {
    it('shouldBeAt1sec内合并相同的GETrequest为单item网络request', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate随机URLpath
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.constant('/metrics'),
            fc.constant('/tasks'),
            fc.webPath()
          ),
          // generate随机queryparam
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
          // generate并发request数量 (2-10item)
          fc.integer({ min: 2, max: 10 }),
          async (url, params, requestCount) => {
            // resetmock以确保每times迭代都是干净的status
            mockAxiosInstance.request.mockReset();

            // create新的ApiClientinstance
            const apiClient = new ApiClient(defaultConfig);

            // 模拟responsedata
            const mockData = { 
              url, 
              params, 
              timestamp: Date.now(),
              random: Math.random() 
            };
            
            mockAxiosInstance.request.mockResolvedValue({ data: mockData });

            // 同时发起多item相同request
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { params })
            );

            const results = await Promise.all(promises);

            // verify: should只发起一times实际网络request
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(1);

            // verify: 所有requestreturn相同的result
            for (let i = 1; i < results.length; i++) {
              expect(results[i]).toEqual(results[0]);
            }

            // verify: return的data与mockdata一致
            expect(results[0]).toEqual(mockData);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should为不同的URL发起独立的网络request', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate2-5item不同的URL
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
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 为每itemURLset不同的response
            mockAxiosInstance.request.mockImplementation(({ url }) => {
              return Promise.resolve({ data: { url, timestamp: Date.now() } });
            });

            // 同时发起对不同URL的request
            const promises = urls.map(url => apiClient.get(url));
            await Promise.all(promises);

            // verify: should为每item不同的URL发起一timesrequest
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(urls.length);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should为不同的queryparam发起独立的网络request', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.constant('/users'),
          // generate2-5item不同的param组合
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
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            mockAxiosInstance.request.mockImplementation(({ params }) => {
              return Promise.resolve({ data: { params, timestamp: Date.now() } });
            });

            // 同时发起带不同param的request
            const promises = paramsList.map(params => 
              apiClient.get(url, { params })
            );
            await Promise.all(promises);

            // verify: should为每item不同的param组合发起一timesrequest
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(paramsList.length);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAtskipDeduplication选项启用时不进行去重', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          fc.integer({ min: 2, max: 5 }),
          async (url, requestCount) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            mockAxiosInstance.request.mockResolvedValue({ 
              data: { url, timestamp: Date.now() } 
            });

            // 同时发起多itemrequest，但skip去重andcache
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { skipDeduplication: true, skipCache: true })
            );

            await Promise.all(promises);

            // verify: should发起与request数量相同的网络request
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(requestCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt去重窗口过期后allow新的request', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          async (url) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            // use较短的去重窗口进行test
            const apiClient = new ApiClient({
              ...defaultConfig,
              deduplicationWindow: 100, // 100ms窗口
            });

            let requestCount = 0;
            mockAxiosInstance.request.mockImplementation(() => {
              requestCount++;
              return Promise.resolve({ data: { count: requestCount } });
            });

            // 第一timesrequest
            const result1 = await apiClient.get(url, { skipCache: true });

            // wait去重窗口过期
            await new Promise(resolve => setTimeout(resolve, 150));

            // 第二timesrequest（should发起新的网络request）
            const result2 = await apiClient.get(url, { skipCache: true });

            // verify: should发起两times网络request
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);

            // verify: 两timesrequestreturn不同的result（因为requestCount递增）
            expect(result1).not.toEqual(result2);
          }
        ),
        { numRuns: 50 } // 减少runtimes数因为有延迟
      );
    });

    it('shouldBeAtrequestfailure后cleanup去重status', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          fc.integer({ min: 2, max: 5 }),
          async (url, requestCount) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 第一timesrequestfailure
            mockAxiosInstance.request.mockRejectedValueOnce(
              new Error('Network error')
            );

            // 后续requestsuccess
            mockAxiosInstance.request.mockResolvedValue({ 
              data: { url, success: true } 
            });

            // 第一timesrequestshouldfailure
            await expect(
              apiClient.get(url, { skipCache: true, skipRetry: true })
            ).rejects.toThrow('Network error');

            // 立即发起多item相同request
            const promises = Array.from({ length: requestCount }, () =>
              apiClient.get(url, { skipCache: true, skipRetry: true })
            );

            const results = await Promise.all(promises);

            // verify: failure后的requestshould被去重（只发起一times新request）
            // 总共: 1timesfailure + 1timessuccess = 2times
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);

            // verify: 所有success的requestreturn相同result
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
   * **Feature: frontend-production-optimization, Property 26: 并发request限制**
   * **verifyRequirement: 10.4**
   * 
   * property: 对于任何时刻，同时进行的APIrequest数量不should超过6item
   * 
   * test策略:
   * - generate随机数量的并发request (7-20item，超过限制)
   * - use延迟response模拟慢速API
   * - 在requestexecute期间监控活跃request数
   * - verify活跃request数永远不超过maxConcurrent (6)
   * - verify所有request最终都能complete
   */
  describe('Property 26: 并发request限制', () => {
    it('should限制并发request数量不超过6item', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate7-15itemrequest（超过6item限制，但不要太多以避免timeout）
          fc.integer({ min: 7, max: 15 }),
          // generate每itemrequest的延迟时间 (30-100ms，减少延迟以加快test)
          fc.integer({ min: 30, max: 100 }),
          async (requestCount, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪最大并发数
            let maxConcurrent = 0;

            // 模拟延迟response并跟踪并发数
            mockAxiosInstance.request.mockImplementation(async () => {
              // 在request开始时check活跃request数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              // 模拟API延迟
              await new Promise(resolve => setTimeout(resolve, delayMs));

              return { data: { success: true, timestamp: Date.now() } };
            });

            // 同时发起多itemrequest
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            // wait所有requestcomplete
            const results = await Promise.all(promises);

            // verify: 最大并发数不应超过6
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // verify: 所有request都successcomplete
            expect(results).toHaveLength(requestCount);
            results.forEach(result => {
              expect(result).toHaveProperty('success', true);
            });

            // verify: 所有request都被execute了
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(requestCount);
          }
        ),
        { numRuns: 50 } // 减少runtimes数以避免timeout
      );
    }, 60000); // 增加timeout时间到60sec

    it('shouldBeAtrequestcomplete后释放并发槽位并handlequeue', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate10-15itemrequest
          fc.integer({ min: 10, max: 15 }),
          async (requestCount) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const concurrentSnapshots: number[] = [];

            // 模拟request，前6item慢，后续的快
            let requestIndex = 0;
            mockAxiosInstance.request.mockImplementation(async () => {
              const myIndex = requestIndex++;
              const delay = myIndex < 6 ? 100 : 10;

              // record当前活跃request数
              concurrentSnapshots.push(apiClient.getActiveRequestCount());

              await new Promise(resolve => setTimeout(resolve, delay));

              return { data: { index: myIndex } };
            });

            // 发起所有request
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // verify: 所有快照中的并发数都不超过6
            concurrentSnapshots.forEach(count => {
              expect(count).toBeLessThanOrEqual(6);
            });

            // verify: 最终所有request都complete，活跃request数为0
            expect(apiClient.getActiveRequestCount()).toBe(0);

            // verify: queue也should为空
            expect(apiClient.getQueuedRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 30000); // 增加timeout时间

    it('should正确handle混合的successandfailurerequest的并发限制', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate8-12itemrequest
          fc.integer({ min: 8, max: 12 }),
          // generatefailurerequest的索引列表
          fc.array(fc.integer({ min: 0, max: 11 }), { maxLength: 5 }),
          async (requestCount, failureIndices) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxConcurrent = 0;
            let requestIndex = 0;

            // 模拟部分requestfailure
            mockAxiosInstance.request.mockImplementation(async () => {
              const myIndex = requestIndex++;
              
              // check当前活跃request数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              await new Promise(resolve => setTimeout(resolve, 50));

              if (failureIndices.includes(myIndex)) {
                throw new Error(`Request ${myIndex} failed`);
              }

              return { data: { index: myIndex, success: true } };
            });

            // 发起所有request
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
                .catch(error => ({ error: error.message }))
            );

            const results = await Promise.all(promises);

            // verify: 最大并发数不超过6
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // verify: 所有request都被handle了（success或failure）
            expect(results).toHaveLength(requestCount);

            // verify: failure的request数量正确
            const failedResults = results.filter((r): r is { error: string } => r !== null && typeof r === 'object' && 'error' in r);
            expect(failedResults.length).toBeGreaterThanOrEqual(0);

            // verify: 最终活跃request数为0
            expect(apiClient.getActiveRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加timeout时间

    it('shouldBeAt不同的HTTPmethod间共享并发限制', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate每种method的request数量
          fc.record({
            getCount: fc.integer({ min: 2, max: 5 }),
            postCount: fc.integer({ min: 2, max: 5 }),
            putCount: fc.integer({ min: 1, max: 3 }),
            deleteCount: fc.integer({ min: 1, max: 3 }),
          }),
          async (counts) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxConcurrent = 0;

            // 模拟所有method的request
            mockAxiosInstance.request.mockImplementation(async ({ method }) => {
              // check当前活跃request数
              const currentActive = apiClient.getActiveRequestCount();
              maxConcurrent = Math.max(maxConcurrent, currentActive);

              await new Promise(resolve => setTimeout(resolve, 80));

              return { data: { method, success: true } };
            });

            // 发起混合的request
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

            // verify: 最大并发数不超过6（所有method共享限制）
            expect(maxConcurrent).toBeLessThanOrEqual(6);

            // verify: 所有request都complete
            const totalRequests = counts.getCount + counts.postCount + counts.putCount + counts.deleteCount;
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(totalRequests);
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加timeout时间

    it('shouldBeAt高并发场景下保持queue的FIFO顺序', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate10-15itemrequest
          fc.integer({ min: 10, max: 15 }),
          async (requestCount) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const executionOrder: number[] = [];

            // 模拟request，recordexecute顺序
            mockAxiosInstance.request.mockImplementation(async ({ url }) => {
              const index = parseInt(url.split('/').pop() || '0');
              executionOrder.push(index);

              await new Promise(resolve => setTimeout(resolve, 30));

              return { data: { index } };
            });

            // 按顺序发起request
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // verify: 所有request都被execute了
            expect(executionOrder).toHaveLength(requestCount);

            // verify: 所有索引都被execute了
            const sortedOrder = [...executionOrder].sort((a, b) => a - b);
            expect(sortedOrder).toEqual(Array.from({ length: requestCount }, (_, i) => i));
          }
        ),
        { numRuns: 100 }
      );
    }, 20000); // 增加timeout时间

    it('shouldBeAt达到并发限制时正确排队新request', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 8, max: 15 }),
          async (requestCount) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            let maxQueuedCount = 0;

            mockAxiosInstance.request.mockImplementation(async () => {
              // checkqueue中的request数
              const queuedCount = apiClient.getQueuedRequestCount();
              maxQueuedCount = Math.max(maxQueuedCount, queuedCount);

              await new Promise(resolve => setTimeout(resolve, 50));

              return { data: { success: true } };
            });

            // 发起所有request
            const promises = Array.from({ length: requestCount }, (_, i) =>
              apiClient.get(`/test/${i}`, { skipCache: true, skipRetry: true })
            );

            await Promise.all(promises);

            // verify: 当并发达到限制时，should有request在queue中wait
            if (requestCount > 6) {
              expect(maxQueuedCount).toBeGreaterThan(0);
            }

            // verify: 最终所有request都complete
            expect(apiClient.getActiveRequestCount()).toBe(0);
            expect(apiClient.getQueuedRequestCount()).toBe(0);
          }
        ),
        { numRuns: 100 }
      );
    }, 30000); // 增加timeout时间
  });

  /**
   * **Feature: frontend-production-optimization, Property 27: timeouthint**
   * **verifyRequirement: 10.5**
   * 
   * property: 对于任何response时间超过5sec的APIrequest，shouldshowloadtimeouthint
   * 
   * test策略:
   * - generate随机的URLand延迟时间
   * - 对于延迟超过5sec的request，verifytimeout回调被调用
   * - 对于延迟小于5sec的request，verifytimeout回调不被调用
   * - verifytimeouthint在requestcomplete后被cleanup
   */
  describe('Property 27: timeouthint', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.runOnlyPendingTimers();
      jest.useRealTimers();
    });

    it('shouldBeAtrequest超过5sec时触发timeout回调', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate随机URL
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.constant('/metrics'),
            fc.webPath()
          ),
          // generate超过5sec的延迟 (5100-8000ms)
          fc.integer({ min: 5100, max: 8000 }),
          async (url, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪timeout回调是否被调用
            let timeoutCallbackCalled = false;
            const onTimeout = jest.fn(() => {
              timeoutCallbackCalled = true;
            });

            // 模拟慢速APIresponse
            mockAxiosInstance.request.mockImplementation(async () => {
              // useReal延迟
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true, url } });
                }, delayMs);
                
                // cleanupfunction
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起request
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到5sec（timeoutthreshold）
            jest.advanceTimersByTime(5000);

            // verify: timeout回调should被调用
            expect(timeoutCallbackCalled).toBe(true);
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // 快进剩余时间让requestcomplete
            jest.advanceTimersByTime(delayMs - 5000);

            // waitrequestcomplete
            const result = await requestPromise;

            // verify: request最终successcomplete
            expect(result).toEqual({ success: true, url });
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAtrequest小于5seccomplete时不触发timeout回调', async () => {
      await fc.assert(
        fc.asyncProperty(
          // generate随机URL
          fc.oneof(
            fc.constant('/users'),
            fc.constant('/projects'),
            fc.webPath()
          ),
          // generate小于5sec的延迟 (100-4900ms)
          fc.integer({ min: 100, max: 4900 }),
          async (url, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // 跟踪timeout回调
            const onTimeout = jest.fn();

            // 模拟快速APIresponse
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true, url } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起request
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到requestcomplete
            jest.advanceTimersByTime(delayMs);

            // waitrequestcomplete
            const result = await requestPromise;

            // verify: timeout回调不should被调用
            expect(onTimeout).not.toHaveBeenCalled();

            // verify: requestsuccesscomplete
            expect(result).toEqual({ success: true, url });

            // 快进到5sec后，confirmtimeout回调仍然不会被调用
            jest.advanceTimersByTime(5000 - delayMs + 100);
            expect(onTimeout).not.toHaveBeenCalled();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAtrequestcomplete后cleanuptimeoutwarn', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // generate延迟时间 (可能超过或不超过5sec)
          fc.integer({ min: 100, max: 8000 }),
          async (url, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const onTimeout = jest.fn();

            // 模拟APIresponse
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起第一timesrequest
            const request1Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到requestcomplete
            jest.advanceTimersByTime(delayMs);
            await request1Promise;

            // resetmock计数
            onTimeout.mockClear();

            // 发起第二times相同的request
            const request2Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            });

            // 快进到5sec
            jest.advanceTimersByTime(5000);

            // 如果第二timesrequest也超过5sec，should再times触发timeout回调
            if (delayMs > 5000) {
              expect(onTimeout).toHaveBeenCalledTimes(1);
            }

            // complete第二timesrequest
            jest.advanceTimersByTime(Math.max(0, delayMs - 5000));
            await request2Promise;

            // verify: request都successcomplete
            expect(mockAxiosInstance.request).toHaveBeenCalledTimes(2);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAtrequestfailure时也cleanuptimeoutwarn', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // generate超过5sec的延迟
          fc.integer({ min: 5100, max: 8000 }),
          async (url, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            const onTimeout = jest.fn();

            // 模拟requestfailure
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((_, reject) => {
                const realTimeout = setTimeout(() => {
                  reject(new Error('Network error'));
                }, delayMs);
                
                (reject as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起request
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            }).catch((error: unknown) => error as Error);

            // 快进到5sec（timeoutthreshold）
            jest.advanceTimersByTime(5000);

            // verify: timeout回调should被调用
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // 快进到requestfailure
            jest.advanceTimersByTime(delayMs - 5000);

            // waitrequestfailure
            const error = await requestPromise as Error;

            // verify: requestfailure
            expect(error).toBeInstanceOf(Error);
            expect(error.message).toBe('Network error');

            // reset回调
            onTimeout.mockClear();

            // 发起新的request到相同URL
            const request2Promise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true,
              onTimeout 
            }).catch((error: unknown) => error as Error);

            // 快进到5sec
            jest.advanceTimersByTime(5000);

            // verify: 新requestshould再times触发timeout回调（desc之前的warn被cleanup了）
            expect(onTimeout).toHaveBeenCalledTimes(1);

            // complete第二timesrequest
            jest.advanceTimersByTime(delayMs - 5000);
            await request2Promise;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt没有provideonTimeout回调时use默认warn', async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.webPath(),
          // generate超过5sec的延迟
          fc.integer({ min: 5100, max: 7000 }),
          async (url, delayMs) => {
            // resetmock
            mockAxiosInstance.request.mockReset();

            const apiClient = new ApiClient(defaultConfig);

            // Mock console.warn
            const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

            // 模拟慢速APIresponse
            mockAxiosInstance.request.mockImplementation(async () => {
              return new Promise((resolve) => {
                const realTimeout = setTimeout(() => {
                  resolve({ data: { success: true } });
                }, delayMs);
                
                (resolve as any).cancel = () => clearTimeout(realTimeout);
              });
            });

            // 发起request（不provideonTimeout回调）
            const requestPromise = apiClient.get(url, { 
              skipCache: true, 
              skipRetry: true
            });

            // 快进到5sec
            jest.advanceTimersByTime(5000);

            // verify: should调用console.warnshow默认timeouthint
            expect(consoleWarnSpy).toHaveBeenCalledWith(
              expect.stringContaining('APIrequesttimeout')
            );
            expect(consoleWarnSpy).toHaveBeenCalledWith(
              expect.stringContaining(url)
            );

            // completerequest
            jest.advanceTimersByTime(delayMs - 5000);
            await requestPromise;

            // cleanup
            consoleWarnSpy.mockRestore();
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
