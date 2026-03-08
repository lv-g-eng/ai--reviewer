/**
 * Logger服务单元测试
 */

import { Logger, LoggerConfig, LogLevel } from '../Logger';

describe('Logger', () => {
  let logger: Logger;
  let consoleDebugSpy: jest.SpyInstance;
  let consoleInfoSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;
  let consoleLogSpy: jest.SpyInstance;

  beforeEach(() => {
    // Mock console methods
    consoleDebugSpy = jest.spyOn(console, 'debug').mockImplementation();
    consoleInfoSpy = jest.spyOn(console, 'info').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

    // Create logger with test config
    const config: LoggerConfig = {
      level: 'debug',
      environment: 'test',
      enableConsole: true,
      batchSize: 10,
      flushInterval: 60000, // 1分钟，避免测试期间自动刷新
    };

    logger = new Logger(config);
  });

  afterEach(() => {
    logger.destroy();
    jest.restoreAllMocks();
  });

  describe('日志级别过滤', () => {
    it('应该根据环境设置默认日志级别', () => {
      const devLogger = new Logger({
        level: 'debug',
        environment: 'development',
      });
      expect(devLogger.getLevel()).toBe('debug');

      const prodLogger = new Logger({
        level: 'error',
        environment: 'production',
      });
      expect(prodLogger.getLevel()).toBe('error');

      devLogger.destroy();
      prodLogger.destroy();
    });

    it('应该只记录大于等于当前级别的日志', () => {
      logger.setLevel('warn');

      logger.debug('debug message');
      logger.info('info message');
      logger.warn('warn message');
      logger.error('error message');

      // debug和info不应该被记录
      expect(consoleDebugSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();

      // warn和error应该被记录
      expect(consoleWarnSpy).toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('应该在生产环境只记录error和warn', () => {
      const prodLogger = new Logger({
        level: 'error',
        environment: 'production',
        enableConsole: true,
      });

      prodLogger.debug('debug message');
      prodLogger.info('info message');
      prodLogger.warn('warn message');
      prodLogger.error('error message');

      // 只有error应该被记录（warn级别低于error）
      expect(consoleDebugSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleWarnSpy).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalled();

      prodLogger.destroy();
    });
  });

  describe('日志记录方法', () => {
    it('应该记录debug日志', () => {
      logger.debug('test debug message', { key: 'value' });

      expect(consoleDebugSpy).toHaveBeenCalled();
      const call = consoleDebugSpy.mock.calls[0];
      expect(call[1]).toBe('test debug message');
      expect(call[2]).toEqual({ key: 'value' });
    });

    it('应该记录info日志', () => {
      logger.info('test info message');

      expect(consoleInfoSpy).toHaveBeenCalled();
      const call = consoleInfoSpy.mock.calls[0];
      expect(call[1]).toBe('test info message');
    });

    it('应该记录warn日志', () => {
      logger.warn('test warn message');

      expect(consoleWarnSpy).toHaveBeenCalled();
      const call = consoleWarnSpy.mock.calls[0];
      expect(call[1]).toBe('test warn message');
    });

    it('应该记录error日志并包含错误堆栈', () => {
      const error = new Error('test error');
      logger.error('test error message', error, { extra: 'data' });

      expect(consoleErrorSpy).toHaveBeenCalled();
      const call = consoleErrorSpy.mock.calls[0];
      expect(call[1]).toBe('test error message');
      expect(call[2]).toMatchObject({
        extra: 'data',
        errorName: 'Error',
        errorMessage: 'test error',
      });
      expect(call[2].errorStack).toBeDefined();
    });
  });

  describe('API请求日志', () => {
    it('应该记录API请求的响应时间和状态码', () => {
      logger.logApiRequest('/api/users', 'GET', 250, 200);

      expect(consoleLogSpy).toHaveBeenCalled();
      const call = consoleLogSpy.mock.calls[0];
      expect(call[0]).toContain('GET');
      expect(call[0]).toContain('/api/users');
      expect(call[0]).toContain('200');
      expect(call[0]).toContain('250ms');
    });

    it('应该记录失败的API请求', () => {
      logger.logApiRequest('/api/users', 'POST', 1500, 500, {
        error: 'Internal Server Error',
      });

      expect(consoleLogSpy).toHaveBeenCalled();
      const call = consoleLogSpy.mock.calls[0];
      expect(call[0]).toContain('POST');
      expect(call[0]).toContain('500');
      expect(call[0]).toContain('1500ms');
    });

    it('应该记录请求和响应大小', () => {
      logger.logApiRequest('/api/data', 'POST', 300, 201, {
        requestSize: 1024,
        responseSize: 2048,
      });

      const buffer = logger.getBufferStatus();
      expect(buffer.apiLogs).toBe(1);
    });
  });

  describe('用户操作日志', () => {
    it('应该记录用户操作包含用户ID、时间戳和操作类型', () => {
      logger.logUserAction('button_click', 'user123', {
        buttonId: 'submit-btn',
        page: '/dashboard',
      });

      expect(consoleLogSpy).toHaveBeenCalled();
      const call = consoleLogSpy.mock.calls[0];
      expect(call[0]).toContain('button_click');
      expect(call[0]).toContain('user123');
      expect(call[1]).toEqual({
        buttonId: 'submit-btn',
        page: '/dashboard',
      });
    });

    it('应该记录关键操作', () => {
      logger.logUserAction('project_delete', 'user456', {
        projectId: 'proj-789',
        projectName: 'Test Project',
      });

      const buffer = logger.getBufferStatus();
      expect(buffer.userActions).toBe(1);
    });
  });

  describe('批量日志发送', () => {
    it('应该在达到批量大小时自动刷新', async () => {
      const flushSpy = jest.spyOn(logger, 'flushLogs');

      // 添加10条日志（等于batchSize）
      for (let i = 0; i < 10; i++) {
        logger.info(`message ${i}`);
      }

      expect(flushSpy).toHaveBeenCalled();
    });

    it('应该清空缓冲区', async () => {
      logger.info('test message 1');
      logger.info('test message 2');
      logger.logApiRequest('/api/test', 'GET', 100, 200);

      let buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(2);
      expect(buffer.apiLogs).toBe(1);

      await logger.flushLogs();

      buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(0);
      expect(buffer.apiLogs).toBe(0);
    });

    it('应该在没有日志时不执行刷新', async () => {
      const result = await logger.flushLogs();
      expect(result).toBeUndefined();
    });
  });

  describe('用户上下文', () => {
    it('应该设置和获取用户ID', () => {
      logger.setUserId('user123');
      expect(logger.getUserId()).toBe('user123');
    });

    it('应该在日志中包含用户ID', () => {
      logger.setUserId('user456');
      logger.info('test message');

      const buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(1);
    });

    it('应该在API日志中包含用户ID', () => {
      logger.setUserId('user789');
      logger.logApiRequest('/api/test', 'GET', 100, 200);

      const buffer = logger.getBufferStatus();
      expect(buffer.apiLogs).toBe(1);
    });
  });

  describe('缓冲区管理', () => {
    it('应该返回正确的缓冲区状态', () => {
      logger.info('log 1');
      logger.info('log 2');
      logger.logApiRequest('/api/test', 'GET', 100, 200);
      logger.logUserAction('click', 'user123');

      const status = logger.getBufferStatus();
      expect(status.logs).toBe(2);
      expect(status.apiLogs).toBe(1);
      expect(status.userActions).toBe(1);
      expect(status.total).toBe(4);
    });
  });

  describe('定时器管理', () => {
    it('应该在销毁时停止定时器并刷新日志', async () => {
      logger.info('test message');

      const flushSpy = jest.spyOn(logger, 'flushLogs');
      await logger.destroy();

      expect(flushSpy).toHaveBeenCalled();
    });

    it('应该能够停止和重启定时器', () => {
      logger.stopFlushTimer();
      // 定时器已停止，不会自动刷新

      logger.info('test message');
      const buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(1);
    });
  });

  describe('控制台输出', () => {
    it('应该在开发环境启用控制台输出', () => {
      const devLogger = new Logger({
        level: 'debug',
        environment: 'development',
        enableConsole: true,
      });

      devLogger.info('test message');
      expect(consoleInfoSpy).toHaveBeenCalled();

      devLogger.destroy();
    });

    it('应该在生产环境禁用控制台输出', () => {
      const prodLogger = new Logger({
        level: 'error',
        environment: 'production',
        enableConsole: false,
      });

      prodLogger.error('test error');
      expect(consoleErrorSpy).not.toHaveBeenCalled();

      prodLogger.destroy();
    });
  });

  describe('边缘情况', () => {
    it('应该处理没有上下文的日志', () => {
      logger.info('message without context');
      expect(consoleInfoSpy).toHaveBeenCalled();
    });

    it('应该处理没有错误对象的error日志', () => {
      logger.error('error without error object');
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('应该处理空字符串消息', () => {
      logger.info('');
      expect(consoleInfoSpy).toHaveBeenCalled();
    });

    it('应该处理大量日志', () => {
      for (let i = 0; i < 100; i++) {
        logger.info(`message ${i}`);
      }

      // 应该触发多次刷新
      const buffer = logger.getBufferStatus();
      expect(buffer.total).toBeLessThan(100);
    });
  });
});
