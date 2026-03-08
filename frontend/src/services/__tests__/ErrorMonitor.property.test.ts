/**
 * ErrorMonitorpropertytest
 * 
 * Feature: frontend-production-optimization
 * Property 8: error监控上报
 * 
 * **Validates: Requirements 9.1, 9.4**
 * 
 * testCoverage:
 * - 对于任何未捕获的error，should将contain完整上下文（userinfo、浏览器info、页面URL、error堆栈）的errorreport发送到监控service
 */

import fc from 'fast-check';
import { ErrorMonitor, MonitorConfig, ErrorReport } from '../ErrorMonitor';

describe('Property 8: error监控上报', () => {
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

  // customGenerator：generateerrorobject
  const errorArbitrary = () =>
    fc.record({
      message: fc.string({ minLength: 1, maxLength: 200 }),
      name: fc.constantFrom('Error', 'TypeError', 'ReferenceError', 'NetworkError', 'ValidationError'),
    }).map(({ message, name }) => {
      const error = new Error(message);
      error.name = name;
      return error;
    });

  // customGenerator：generateerror上下文
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

  // customGenerator：generate监控config
  const monitorConfigArbitrary = () =>
    fc.record({
      environment: fc.constantFrom('development', 'test', 'production'),
      enableDebugMode: fc.boolean(),
      sampleRate: fc.option(fc.double({ min: 0, max: 1 }), { nil: undefined }),
    });

  it('should为所有errorgeneratecontain完整上下文的errorreport', () => {
    fc.assert(
      fc.property(
        monitorConfigArbitrary(),
        errorArbitrary(),
        errorContextArbitrary(),
        (config, error, context) => {
          // createErrorMonitorinstance
          const errorMonitor = new ErrorMonitor({
            ...config,
            enableDebugMode: true, // 强制启用调试模式以便捕获output
          });
          errorMonitor.initialize();

          // 捕获error
          errorMonitor.captureError(error, context);

          // verifyerror被record
          expect(consoleErrorSpy).toHaveBeenCalled();

          // getrecord的errorreport
          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          expect(lastCall[0]).toBe('[ErrorMonitor]');

          const errorReport: ErrorReport = lastCall[1];

          // verifyerrorreportcontain所有必需field（requirement9.1, 9.4）
          expect(errorReport).toMatchObject({
            id: expect.stringMatching(/^error_\d+_[a-z0-9]+$/),
            type: expect.stringMatching(/^(network|validation|authorization|server|client|unknown)$/),
            message: error.message,
            stack: expect.any(String),
            timestamp: expect.any(Date),
          });

          // verifyerror上下文contain完整info（requirement9.4）
          expect(errorReport.context).toMatchObject({
            url: expect.any(String),
            userAgent: expect.any(String),
            timestamp: expect.any(Date),
          });

          // 如果provide了userId，shouldcontain在上下文中
          if (context.userId) {
            expect(errorReport.context.userId).toBe(context.userId);
          }

          // 如果provide了additionalData，shouldcontain在上下文中
          if (context.additionalData) {
            expect(errorReport.context.additionalData).toEqual(context.additionalData);
          }

          // verifyURLanduserAgent被正确set
          expect(errorReport.context.url).toBe(context.url);
          expect(errorReport.context.userAgent).toBe(context.userAgent);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should为所有errorgenerate唯一的errorID', () => {
    fc.assert(
      fc.property(
        fc.array(errorArbitrary(), { minLength: 2, maxLength: 10 }),
        (errors) => {
          const errorMonitor = new ErrorMonitor({
            environment: 'test',
            enableDebugMode: true,
          });
          errorMonitor.initialize();

          // 捕获所有error
          errors.forEach(error => errorMonitor.captureError(error));

          // get所有errorID
          const errorIds = consoleErrorSpy.mock.calls
            .filter(call => call[0] === '[ErrorMonitor]')
            .map(call => call[1].id);

          // verify所有ID都是唯一的
          const uniqueIds = new Set(errorIds);
          expect(uniqueIds.size).toBe(errorIds.length);

          // verify所有ID都符合format
          errorIds.forEach(id => {
            expect(id).toMatch(/^error_\d+_[a-z0-9]+$/);
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should正确分class所有type的error', () => {
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

  it('shouldBeAtsetuser上下文后将userinfocontain在errorreport中', () => {
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

          // setuser上下文
          errorMonitor.setUser(user);

          // 捕获error（不provideuserId）
          errorMonitor.captureError(error);

          const calls = consoleErrorSpy.mock.calls;
          const lastCall = calls[calls.length - 1];
          const errorReport: ErrorReport = lastCall[1];

          // verifyuserID被contain在errorreport中
          expect(errorReport.context.userId).toBe(user.id);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldsupportbeforeSend钩子修改或filtererrorreport', () => {
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

          // verifybeforeSend被调用
          expect(beforeSend).toHaveBeenCalled();

          if (shouldReport) {
            // should上报，且消息被修改
            expect(consoleErrorSpy).toHaveBeenCalledWith(
              '[ErrorMonitor]',
              expect.objectContaining({
                message: 'Modified: ' + error.message,
              })
            );
          } else {
            // 不should上报
            expect(consoleErrorSpy.mock.calls.length).toBe(initialCallCount);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldBeAterrorreport中contain完整的error堆栈', () => {
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

          // verify堆栈存在且是字符串（requirement9.4）
          if (error.stack) {
            expect(errorReport.stack).toBe(error.stack);
            expect(typeof errorReport.stack).toBe('string');
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldBeAterrorreport中contain浏览器info（userAgent）', () => {
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

          // verify浏览器info被contain（requirement9.4）
          expect(errorReport.context.userAgent).toBe(context.userAgent);
          expect(typeof errorReport.context.userAgent).toBe('string');
          expect(errorReport.context.userAgent.length).toBeGreaterThan(0);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldBeAterrorreport中contain页面URL', () => {
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

          // verify页面URL被contain（requirement9.4）
          expect(errorReport.context.url).toBe(context.url);
          expect(typeof errorReport.context.url).toBe('string');
          expect(errorReport.context.url.length).toBeGreaterThan(0);
        }
      ),
      { numRuns: 100 }
    );
  });
});
