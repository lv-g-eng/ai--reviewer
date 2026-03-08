/**
 * ErrorMonitor属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 8: 错误监控上报
 * 
 * **Validates: Requirements 9.1, 9.4**
 * 
 * 测试覆盖:
 * - 对于任何未捕获的错误，应该将包含完整上下文（用户信息、浏览器信息、页面URL、错误堆栈）的错误报告发送到监控服务
 */

import fc from 'fast-check';
import { ErrorMonitor, MonitorConfig, ErrorReport } from '../ErrorMonitor';

describe('Property 8: 错误监控上报', () => {
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleLogSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleLogSpy.mockRestore();
  });

  // 自定义生成器：生成错误对象
  const errorArbitrary = () =>
    fc.record({
      message: fc.string({ minLength: 1, maxLength: 200 }),
      name: fc.constantFrom('Error', 'TypeError', 'ReferenceError', 'NetworkError', 'ValidationError'),
    }).map(({ message, name }) => {
      const error = new Error(message);
      error.name = name;
      return error;
    });

  // 自定义生成器：生成错误上下文
  const errorContextArbitrary = () =>
    fc.record({
      userId: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
      url: fc.webUrl(),
      userAgent: fc.constantFrom(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
      ),
      additionalData: fc.option(
        fc.dictionary(fc.string({ minLength: 1, maxLength: 20 }), fc.anything()),
        { nil: undefined }
      ),
    });

  // 自定义生成器：生成监控配置
  const monitorConfigArbitrary = () =>
    fc.record({
      environment: fc.constantFrom('development', 'test', 'production'),
      enableDebugMode: fc.boolean(),
      sampleRate: fc.option(fc.double({ min: 0, max: 1 }), { nil: undefined }),
    });

  it('应该为所有错误生成包含完整上下文的错误报告', () => {
    fc.assert(
      fc.property(
        monitorConfigArbitrary(),
        errorArbitrary(),
        errorContextArbitrary(),
        (config, error, context) => {
          // 创建ErrorMonitor实例
          const errorMonitor = new ErrorMonitor({
            ...config,
            enableDebugMode: true, // 强制启用调试模式以便捕获输出
          });
          errorMonitor.initialize();

          // 捕获错误
          errorMonitor.captureError(error, context);

          // 验证错误被记录
          expect(consoleErrorSpy).toHaveBeenCalled();

          // 获取记录的错误报告
          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          expect(lastCall[0]).toBe('[ErrorMonitor]');

          const errorReport: ErrorReport = lastCall[1];

          // 验证错误报告包含所有必需字段（需求9.1, 9.4）
          expect(errorReport).toMatchObject({
            id: expect.stringMatching(/^error_\d+_[a-z0-9]+$/),
            type: expect.stringMatching(/^(network|validation|authorization|server|client|unknown)$/),
            message: error.message,
            stack: expect.any(String),
            timestamp: expect.any(Date),
          });

          // 验证错误上下文包含完整信息（需求9.4）
          expect(errorReport.context).toMatchObject({
            url: expect.any(String),
            userAgent: expect.any(String),
            timestamp: expect.any(Date),
          });

          // 如果提供了userId，应该包含在上下文中
          if (context.userId) {
            expect(errorReport.context.userId).toBe(context.userId);
          }

          // 如果提供了additionalData，应该包含在上下文中
          if (context.additionalData) {
            expect(errorReport.context.additionalData).toEqual(context.additionalData);
          }

          // 验证URL和userAgent被正确设置
          expect(errorReport.context.url).toBe(context.url);
          expect(errorReport.context.userAgent).toBe(context.userAgent);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有错误生成唯一的错误ID', () => {
    fc.assert(
      fc.property(
        fc.array(errorArbitrary(), { minLength: 2, maxLength: 10 }),
        (errors) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          // 捕获所有错误
          errors.forEach(error => errorMonitor.captureError(error));

          // 获取所有错误ID
          const errorIds = consoleErrorSpy.mock.calls
            .filter(call => call[0] === '[ErrorMonitor]')
            .map(call => call[1].id);

          // 验证所有ID都是唯一的
          const uniqueIds = new Set(errorIds);
          expect(uniqueIds.size).toBe(errorIds.length);

          // 验证所有ID都符合格式
          errorIds.forEach(id => {
            expect(id).toMatch(/^error_\d+_[a-z0-9]+$/);
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该正确分类所有类型的错误', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          { message: 'Network error occurred', expectedType: 'network' },
          { message: 'Fetch failed', expectedType: 'network' },
          { message: 'Request timeout', expectedType: 'network' },
          { message: 'Validation failed', expectedType: 'validation' },
          { message: 'Invalid input', expectedType: 'validation' },
          { message: 'Unauthorized access', expectedType: 'authorization' },
          { message: '401 error', expectedType: 'authorization' },
          { message: '403 Forbidden', expectedType: 'authorization' },
          { message: '500 Internal Server Error', expectedType: 'server' },
          { message: 'Server error', expectedType: 'server' },
          { message: 'Some random error', expectedType: 'unknown' }
        ),
        ({ message, expectedType }) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          const error = new Error(message);
          errorMonitor.captureError(error);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          expect(errorReport.type).toBe(expectedType);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在设置用户上下文后将用户信息包含在错误报告中', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string({ minLength: 1, maxLength: 50 }),
          email: fc.option(fc.emailAddress(), { nil: undefined }),
          username: fc.option(fc.string({ minLength: 1, maxLength: 30 }), { nil: undefined }),
        }),
        errorArbitrary(),
        (user, error) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          // 设置用户上下文
          errorMonitor.setUser(user);

          // 捕获错误（不提供userId）
          errorMonitor.captureError(error);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          // 验证用户ID被包含在错误报告中
          expect(errorReport.context.userId).toBe(user.id);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该支持beforeSend钩子修改或过滤错误报告', () => {
    fc.assert(
      fc.property(
        errorArbitrary(),
        fc.boolean(),
        (error, shouldReport) => {
          const beforeSend = jest.fn((report: ErrorReport) => {
            if (shouldReport) {
              return {
                ...report,
                message: 'Modified: ' + report.message,
              };
            }
            return null; // 不上报
          });

          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
            beforeSend,
          });
          errorMonitor.initialize();

          const initialCallCount = consoleErrorSpy.mock.calls.length;
          errorMonitor.captureError(error);

          // 验证beforeSend被调用
          expect(beforeSend).toHaveBeenCalled();

          if (shouldReport) {
            // 应该上报，且消息被修改
            expect(consoleErrorSpy).toHaveBeenCalledWith(
              '[ErrorMonitor]',
              expect.objectContaining({
                message: 'Modified: ' + error.message,
              })
            );
          } else {
            // 不应该上报
            expect(consoleErrorSpy.mock.calls.length).toBe(initialCallCount);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在错误报告中包含完整的错误堆栈', () => {
    fc.assert(
      fc.property(
        errorArbitrary(),
        (error) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          errorMonitor.captureError(error);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          // 验证堆栈存在且是字符串（需求9.4）
          if (error.stack) {
            expect(errorReport.stack).toBe(error.stack);
            expect(typeof errorReport.stack).toBe('string');
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在错误报告中包含浏览器信息（userAgent）', () => {
    fc.assert(
      fc.property(
        errorArbitrary(),
        errorContextArbitrary(),
        (error, context) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          errorMonitor.captureError(error, context);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          // 验证浏览器信息被包含（需求9.4）
          expect(errorReport.context.userAgent).toBe(context.userAgent);
          expect(typeof errorReport.context.userAgent).toBe('string');
          expect(errorReport.context.userAgent.length).toBeGreaterThan(0);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在错误报告中包含页面URL', () => {
    fc.assert(
      fc.property(
        errorArbitrary(),
        errorContextArbitrary(),
        (error, context) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          errorMonitor.captureError(error, context);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          // 验证页面URL被包含（需求9.4）
          expect(errorReport.context.url).toBe(context.url);
          expect(typeof errorReport.context.url).toBe('string');
          expect(errorReport.context.url.length).toBeGreaterThan(0);
        }
      ),
      { numRuns: 100 }
    );
  });
});
