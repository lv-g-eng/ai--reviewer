/**
 * Logger属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 37: API请求日志记录
 * 
 * **Validates: Requirements 9.2**
 * 
 * 测试覆盖:
 * - 对于任何API请求，应该记录包含响应时间和状态码的日志
 */

import fc from 'fast-check';
import { Logger, LoggerConfig, ApiRequestLog, UserActionLog } from '../Logger';

describe('Property 37: API请求日志记录', () => {
  let consoleLogSpy: jest.SpyInstance;
  let consoleDebugSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation();
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
    consoleDebugSpy.mockRestore();
  });

  // 自定义生成器：生成HTTP方法
  const httpMethodArbitrary = () =>
    fc.constantFrom('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS');

  // 自定义生成器：生成HTTP状态码
  const httpStatusArbitrary = () =>
    fc.constantFrom(
      200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 422, 429, 500, 502, 503, 504
    );

  // 自定义生成器：生成响应时间（毫秒）
  const durationArbitrary = () =>
    fc.integer({ min: 1, max: 10000 });

  // 自定义生成器：生成URL
  const urlArbitrary = () =>
    fc.oneof(
      fc.webUrl(),
      fc.string({ minLength: 1, maxLength: 100 }).map(path => `/api/${path}`),
      fc.string({ minLength: 1, maxLength: 50 }).map(path => `/v1/${path}`)
    );

  // 自定义生成器：生成Logger配置
  const loggerConfigArbitrary = () =>
    fc.record({
      level: fc.constantFrom('debug', 'info', 'warn', 'error'),
      environment: fc.constantFrom('development', 'test', 'production'),
      enableConsole: fc.boolean(),
      batchSize: fc.integer({ min: 10, max: 100 }),
      flushInterval: fc.integer({ min: 1000, max: 60000 }),
    });

  it('应该为所有API请求记录包含响应时间和状态码的日志', () => {
    fc.assert(
      fc.property(
        loggerConfigArbitrary(),
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        (config, url, method, duration, status) => {
          // 创建Logger实例
          const logger = new Logger({
            ...config,
            enableConsole: true, // 强制启用控制台输出以便验证
          });

          // 记录API请求
          logger.logApiRequest(url, method, duration, status);

          // 获取缓冲区状态
          const bufferStatus = logger.getBufferStatus();

          // 验证API日志被添加到缓冲区（需求9.2）
          expect(bufferStatus.apiLogs).toBeGreaterThan(0);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有API请求生成包含必需字段的日志条目', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        (url, method, duration, status) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          // 记录API请求
          logger.logApiRequest(url, method, duration, status);

          // 通过反射访问私有缓冲区来验证日志内容
          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          expect(apiLogBuffer.length).toBeGreaterThan(0);

          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证日志包含所有必需字段（需求9.2）
          expect(lastLog).toMatchObject({
            id: expect.stringMatching(/^log_\d+_[a-z0-9]+$/),
            method: method.toUpperCase(),
            url: url,
            status: status,
            duration: duration,
            timestamp: expect.any(Date),
          });

          // 验证响应时间和状态码被正确记录
          expect(lastLog.duration).toBe(duration);
          expect(lastLog.status).toBe(status);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有API请求生成唯一的日志ID', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            url: urlArbitrary(),
            method: httpMethodArbitrary(),
            duration: durationArbitrary(),
            status: httpStatusArbitrary(),
          }),
          { minLength: 2, maxLength: 20 }
        ),
        (requests) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 1000,
          });

          // 记录所有API请求
          requests.forEach(({ url, method, duration, status }) => {
            logger.logApiRequest(url, method, duration, status);
          });

          // 获取所有日志ID
          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const logIds = apiLogBuffer.map(log => log.id);

          // 验证所有ID都是唯一的
          const uniqueIds = new Set(logIds);
          expect(uniqueIds.size).toBe(logIds.length);

          // 验证所有ID都符合格式
          logIds.forEach(id => {
            expect(id).toMatch(/^log_\d+_[a-z0-9]+$/);
          });

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该正确记录HTTP方法（转换为大写）', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        fc.constantFrom('get', 'post', 'put', 'delete', 'patch', 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'),
        durationArbitrary(),
        httpStatusArbitrary(),
        (url, method, duration, status) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logApiRequest(url, method, duration, status);

          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证方法被转换为大写
          expect(lastLog.method).toBe(method.toUpperCase());

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在API日志中包含可选的请求和响应大小', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        fc.option(fc.integer({ min: 0, max: 1000000 }), { nil: undefined }),
        fc.option(fc.integer({ min: 0, max: 10000000 }), { nil: undefined }),
        (url, method, duration, status, requestSize, responseSize) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logApiRequest(url, method, duration, status, {
            requestSize,
            responseSize,
          });

          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证可选字段被正确记录
          if (requestSize !== undefined) {
            expect(lastLog.requestSize).toBe(requestSize);
          }
          if (responseSize !== undefined) {
            expect(lastLog.responseSize).toBe(responseSize);
          }

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在API日志中包含错误信息（如果提供）', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        fc.constantFrom(400, 401, 403, 404, 500, 502, 503),
        fc.option(fc.string({ minLength: 1, maxLength: 200 }), { nil: undefined }),
        (url, method, duration, status, errorMessage) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logApiRequest(url, method, duration, status, {
            error: errorMessage,
          });

          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证错误信息被正确记录
          if (errorMessage !== undefined) {
            expect(lastLog.error).toBe(errorMessage);
          }

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在API日志中包含当前用户ID（如果已设置）', () => {
    fc.assert(
      fc.property(
        fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        (userId, url, method, duration, status) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          // 设置用户ID（如果提供）
          if (userId !== undefined) {
            logger.setUserId(userId);
          }

          logger.logApiRequest(url, method, duration, status);

          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证用户ID被包含在日志中
          if (userId !== undefined) {
            expect(lastLog.userId).toBe(userId);
          } else {
            expect(lastLog.userId).toBeUndefined();
          }

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在达到批量大小时触发日志刷新', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 5, max: 20 }),
        (batchSize) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: batchSize,
            flushInterval: 60000, // 长时间间隔，避免自动刷新
          });

          // 记录足够多的API请求以触发刷新
          for (let i = 0; i < batchSize; i++) {
            logger.logApiRequest(`/api/test/${i}`, 'GET', 100, 200);
          }

          // 验证缓冲区在达到批量大小后被清空
          const bufferStatus = logger.getBufferStatus();
          expect(bufferStatus.total).toBeLessThan(batchSize);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有API请求记录时间戳', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        (url, method, duration, status) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          const beforeTimestamp = new Date();
          logger.logApiRequest(url, method, duration, status);
          const afterTimestamp = new Date();

          const apiLogBuffer = (logger as any).apiLogBuffer as ApiRequestLog[];
          const lastLog = apiLogBuffer[apiLogBuffer.length - 1];

          // 验证时间戳在合理范围内
          expect(lastLog.timestamp).toBeInstanceOf(Date);
          expect(lastLog.timestamp.getTime()).toBeGreaterThanOrEqual(beforeTimestamp.getTime());
          expect(lastLog.timestamp.getTime()).toBeLessThanOrEqual(afterTimestamp.getTime());

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在开发环境中输出API请求日志到控制台', () => {
    fc.assert(
      fc.property(
        urlArbitrary(),
        httpMethodArbitrary(),
        durationArbitrary(),
        httpStatusArbitrary(),
        (url, method, duration, status) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'development',
            enableConsole: true,
            batchSize: 100,
          });

          logger.logApiRequest(url, method, duration, status);

          // 验证控制台输出被调用
          expect(consoleLogSpy).toHaveBeenCalled();

          // 验证输出包含关键信息
          const logCall = consoleLogSpy.mock.calls.find(call => 
            call[0].includes('[API]') && 
            call[0].includes(method.toUpperCase()) &&
            call[0].includes(url)
          );
          expect(logCall).toBeDefined();

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });
});


/**
 * Logger属性测试 - 用户操作日志
 * 
 * Feature: frontend-production-optimization
 * Property 38: 用户操作日志记录
 * 
 * **Validates: Requirements 9.3**
 * 
 * 测试覆盖:
 * - 对于任何关键用户操作，应该记录包含用户ID、时间戳和操作类型的日志
 */

describe('Property 38: 用户操作日志记录', () => {
  let consoleLogSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
  });

  // 自定义生成器：生成用户ID
  const userIdArbitrary = () =>
    fc.oneof(
      fc.uuid(),
      fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
      fc.integer({ min: 1, max: 999999 }).map(n => `user_${n}`)
    );

  // 自定义生成器：生成操作类型
  const actionArbitrary = () =>
    fc.oneof(
      fc.constantFrom(
        'login',
        'logout',
        'create_project',
        'delete_project',
        'update_project',
        'approve_pr',
        'reject_pr',
        'submit_analysis',
        'export_data',
        'change_settings'
      ),
      fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0)
    );

  // 自定义生成器：生成操作详情
  const detailsArbitrary = () =>
    fc.option(
      fc.record({
        projectId: fc.option(fc.uuid(), { nil: undefined }),
        prId: fc.option(fc.integer({ min: 1, max: 10000 }), { nil: undefined }),
        targetId: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
        metadata: fc.option(fc.object(), { nil: undefined }),
      }),
      { nil: undefined }
    );

  it('应该为所有用户操作记录包含用户ID、时间戳和操作类型的日志', () => {
    fc.assert(
      fc.property(
        userIdArbitrary(),
        actionArbitrary(),
        detailsArbitrary(),
        (userId, action, details) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          // 记录用户操作
          logger.logUserAction(action, userId, details);

          // 通过反射访问私有缓冲区来验证日志内容
          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          expect(userActionBuffer.length).toBeGreaterThan(0);

          const lastLog = userActionBuffer[userActionBuffer.length - 1];

          // 验证日志包含所有必需字段（需求9.3）
          expect(lastLog).toMatchObject({
            id: expect.stringMatching(/^log_\d+_[a-z0-9]+$/),
            action: action,
            userId: userId,
            timestamp: expect.any(Date),
          });

          // 验证用户ID、时间戳和操作类型被正确记录
          expect(lastLog.userId).toBe(userId);
          expect(lastLog.action).toBe(action);
          expect(lastLog.timestamp).toBeInstanceOf(Date);

          // 验证详情被正确记录（如果提供）
          if (details !== undefined) {
            expect(lastLog.details).toEqual(details);
          }

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有用户操作生成唯一的日志ID', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            userId: userIdArbitrary(),
            action: actionArbitrary(),
            details: detailsArbitrary(),
          }),
          { minLength: 2, maxLength: 20 }
        ),
        (userActions) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 1000,
          });

          // 记录所有用户操作
          userActions.forEach(({ userId, action, details }) => {
            logger.logUserAction(action, userId, details);
          });

          // 获取所有日志ID
          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const logIds = userActionBuffer.map(log => log.id);

          // 验证所有ID都是唯一的
          const uniqueIds = new Set(logIds);
          expect(uniqueIds.size).toBe(logIds.length);

          // 验证所有ID都符合格式
          logIds.forEach(id => {
            expect(id).toMatch(/^log_\d+_[a-z0-9]+$/);
          });

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有用户操作记录时间戳', () => {
    fc.assert(
      fc.property(
        userIdArbitrary(),
        actionArbitrary(),
        detailsArbitrary(),
        (userId, action, details) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          const beforeTimestamp = new Date();
          logger.logUserAction(action, userId, details);
          const afterTimestamp = new Date();

          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const lastLog = userActionBuffer[userActionBuffer.length - 1];

          // 验证时间戳在合理范围内
          expect(lastLog.timestamp).toBeInstanceOf(Date);
          expect(lastLog.timestamp.getTime()).toBeGreaterThanOrEqual(beforeTimestamp.getTime());
          expect(lastLog.timestamp.getTime()).toBeLessThanOrEqual(afterTimestamp.getTime());

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在用户操作日志中包含当前页面路径', () => {
    fc.assert(
      fc.property(
        userIdArbitrary(),
        actionArbitrary(),
        detailsArbitrary(),
        (userId, action, details) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logUserAction(action, userId, details);

          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const lastLog = userActionBuffer[userActionBuffer.length - 1];

          // 验证页面路径被记录（在测试环境中可能为空字符串）
          expect(lastLog.page).toBeDefined();
          expect(typeof lastLog.page).toBe('string');

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在开发环境中输出用户操作日志到控制台', () => {
    fc.assert(
      fc.property(
        userIdArbitrary(),
        actionArbitrary(),
        detailsArbitrary(),
        (userId, action, details) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'development',
            enableConsole: true,
            batchSize: 100,
          });

          logger.logUserAction(action, userId, details);

          // 验证控制台输出被调用
          expect(consoleLogSpy).toHaveBeenCalled();

          // 验证输出包含关键信息
          const logCall = consoleLogSpy.mock.calls.find(call => 
            call[0].includes('[USER ACTION]') && 
            call[0].includes(action) &&
            call[0].includes(userId)
          );
          expect(logCall).toBeDefined();

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在达到批量大小时触发用户操作日志刷新', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 5, max: 20 }),
        (batchSize) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: batchSize,
            flushInterval: 60000, // 长时间间隔，避免自动刷新
          });

          // 记录足够多的用户操作以触发刷新
          for (let i = 0; i < batchSize; i++) {
            logger.logUserAction(`action_${i}`, `user_${i}`);
          }

          // 验证缓冲区在达到批量大小后被清空
          const bufferStatus = logger.getBufferStatus();
          expect(bufferStatus.total).toBeLessThan(batchSize);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该正确处理包含特殊字符的用户ID和操作类型', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 50 }),
        fc.string({ minLength: 1, maxLength: 100 }),
        (userId, action) => {
          // 跳过空白字符串
          if (userId.trim().length === 0 || action.trim().length === 0) {
            return true;
          }

          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logUserAction(action, userId);

          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const lastLog = userActionBuffer[userActionBuffer.length - 1];

          // 验证特殊字符被正确保存
          expect(lastLog.userId).toBe(userId);
          expect(lastLog.action).toBe(action);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该支持在用户操作日志中包含复杂的详情对象', () => {
    fc.assert(
      fc.property(
        userIdArbitrary(),
        actionArbitrary(),
        fc.object({ maxDepth: 2 }),
        (userId, action, details) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 100,
          });

          logger.logUserAction(action, userId, details);

          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const lastLog = userActionBuffer[userActionBuffer.length - 1];

          // 验证详情对象被正确记录
          expect(lastLog.details).toEqual(details);

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为不同用户的相同操作创建独立的日志条目', () => {
    fc.assert(
      fc.property(
        fc.array(userIdArbitrary(), { minLength: 2, maxLength: 10 }),
        actionArbitrary(),
        (userIds, action) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 1000,
          });

          // 多个用户执行相同操作
          userIds.forEach(userId => {
            logger.logUserAction(action, userId);
          });

          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];

          // 验证为每个用户创建了独立的日志条目
          expect(userActionBuffer.length).toBe(userIds.length);

          // 验证每个日志条目的用户ID正确
          userActionBuffer.forEach((log, index) => {
            expect(log.userId).toBe(userIds[index]);
            expect(log.action).toBe(action);
          });

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在混合日志类型时正确维护用户操作日志缓冲区', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.oneof(
            fc.record({
              type: fc.constant('userAction' as const),
              userId: userIdArbitrary(),
              action: actionArbitrary(),
            }),
            fc.record({
              type: fc.constant('apiRequest' as const),
              url: fc.webUrl(),
              method: fc.constantFrom('GET', 'POST', 'PUT', 'DELETE'),
              duration: fc.integer({ min: 1, max: 5000 }),
              status: fc.integer({ min: 200, max: 599 }),
            })
          ),
          { minLength: 5, maxLength: 20 }
        ),
        (logs) => {
          const logger = new Logger({
            level: 'debug',
            environment: 'test',
            enableConsole: false,
            batchSize: 1000,
          });

          // 记录混合类型的日志
          logs.forEach(log => {
            if (log.type === 'userAction') {
              logger.logUserAction(log.action, log.userId);
            } else {
              logger.logApiRequest(log.url, log.method, log.duration, log.status);
            }
          });

          // 验证用户操作日志数量正确
          const userActionBuffer = (logger as any).userActionBuffer as UserActionLog[];
          const expectedUserActionCount = logs.filter(l => l.type === 'userAction').length;
          expect(userActionBuffer.length).toBe(expectedUserActionCount);

          // 验证所有用户操作日志都包含必需字段
          userActionBuffer.forEach(log => {
            expect(log.id).toMatch(/^log_\d+_[a-z0-9]+$/);
            expect(log.userId).toBeDefined();
            expect(log.action).toBeDefined();
            expect(log.timestamp).toBeInstanceOf(Date);
          });

          // 清理
          logger.stopFlushTimer();
        }
      ),
      { numRuns: 100 }
    );
  });
});
