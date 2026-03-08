/**
 * Loggerservice单元test
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
      flushInterval: 60000, // 1min，避免test期间自动refresh
    };

    logger = new Logger(config);
  });

  afterEach(() => {
    logger.destroy();
    jest.restoreAllMocks();
  });

  describe('log级别filter', () => {
    it('should根据envset默认log级别', () => {
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

    it('should只record大于等于当前级别的log', () => {
      logger.setLevel('warn');

      logger.debug('debug message');
      logger.info('info message');
      logger.warn('warn message');
      logger.error('error message');

      // debugandinfo不should被record
      expect(consoleDebugSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();

      // warnanderrorshould被record
      expect(consoleWarnSpy).toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('shouldBeAtprodenv只recorderrorandwarn', () => {
      const prodLogger = new Logger({
        level: 'error',
        environment: 'production',
        enableConsole: true,
      });

      prodLogger.debug('debug message');
      prodLogger.info('info message');
      prodLogger.warn('warn message');
      prodLogger.error('error message');

      // 只有errorshould被record（warn级别低于error）
      expect(consoleDebugSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleWarnSpy).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalled();

      prodLogger.destroy();
    });
  });

  describe('logrecordmethod', () => {
    it('shouldrecorddebuglog', () => {
      logger.debug('test debug message', { key: 'value' });

      expect(consoleDebugSpy).toHaveBeenCalled();
      const call = consoleDebugSpy.mock.calls[0];
      expect(call[1]).toBe('test debug message');
      expect(call[2]).toEqual({ key: 'value' });
    });

    it('shouldrecordinfolog', () => {
      logger.info('test info message');

      expect(consoleInfoSpy).toHaveBeenCalled();
      const call = consoleInfoSpy.mock.calls[0];
      expect(call[1]).toBe('test info message');
    });

    it('shouldrecordwarnlog', () => {
      logger.warn('test warn message');

      expect(consoleWarnSpy).toHaveBeenCalled();
      const call = consoleWarnSpy.mock.calls[0];
      expect(call[1]).toBe('test warn message');
    });

    it('shouldrecorderrorlog并containerror堆栈', () => {
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

  describe('APIrequestlog', () => {
    it('shouldrecordAPIrequest的response时间andstatus码', () => {
      logger.logApiRequest('/api/users', 'GET', 250, 200);

      expect(consoleLogSpy).toHaveBeenCalled();
      const call = consoleLogSpy.mock.calls[0];
      expect(call[0]).toContain('GET');
      expect(call[0]).toContain('/api/users');
      expect(call[0]).toContain('200');
      expect(call[0]).toContain('250ms');
    });

    it('shouldrecordfailure的APIrequest', () => {
      logger.logApiRequest('/api/users', 'POST', 1500, 500, {
        error: 'Internal Server Error',
      });

      expect(consoleLogSpy).toHaveBeenCalled();
      const call = consoleLogSpy.mock.calls[0];
      expect(call[0]).toContain('POST');
      expect(call[0]).toContain('500');
      expect(call[0]).toContain('1500ms');
    });

    it('shouldrecordrequestandresponse大小', () => {
      logger.logApiRequest('/api/data', 'POST', 300, 201, {
        requestSize: 1024,
        responseSize: 2048,
      });

      const buffer = logger.getBufferStatus();
      expect(buffer.apiLogs).toBe(1);
    });
  });

  describe('user操作log', () => {
    it('shouldrecorduser操作containuserID、时间戳and操作type', () => {
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

    it('shouldrecord关键操作', () => {
      logger.logUserAction('project_delete', 'user456', {
        projectId: 'proj-789',
        projectName: 'Test Project',
      });

      const buffer = logger.getBufferStatus();
      expect(buffer.userActions).toBe(1);
    });
  });

  describe('批量log发送', () => {
    it('shouldBeAt达到批量大hour自动refresh', async () => {
      const flushSpy = jest.spyOn(logger, 'flushLogs');

      // add10条log（等于batchSize）
      for (let i = 0; i < 10; i++) {
        logger.info(`message ${i}`);
      }

      expect(flushSpy).toHaveBeenCalled();
    });

    it('should清空缓冲区', async () => {
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

    it('shouldBeAt没有log时不executerefresh', async () => {
      const result = await logger.flushLogs();
      expect(result).toBeUndefined();
    });
  });

  describe('user上下文', () => {
    it('shouldsetandgetuserID', () => {
      logger.setUserId('user123');
      expect(logger.getUserId()).toBe('user123');
    });

    it('shouldBeAtlog中containuserID', () => {
      logger.setUserId('user456');
      logger.info('test message');

      const buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(1);
    });

    it('shouldBeAtAPIlog中containuserID', () => {
      logger.setUserId('user789');
      logger.logApiRequest('/api/test', 'GET', 100, 200);

      const buffer = logger.getBufferStatus();
      expect(buffer.apiLogs).toBe(1);
    });
  });

  describe('缓冲区管理', () => {
    it('shouldreturn正确的缓冲区status', () => {
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
    it('shouldBeAt销毁时stop定时器并refreshlog', async () => {
      logger.info('test message');

      const flushSpy = jest.spyOn(logger, 'flushLogs');
      await logger.destroy();

      expect(flushSpy).toHaveBeenCalled();
    });

    it('should能够stopandrestart定时器', () => {
      logger.stopFlushTimer();
      // 定时器已stop，不会自动refresh

      logger.info('test message');
      const buffer = logger.getBufferStatus();
      expect(buffer.logs).toBe(1);
    });
  });

  describe('控制台output', () => {
    it('shouldBeAtdevenv启用控制台output', () => {
      const devLogger = new Logger({
        level: 'debug',
        environment: 'development',
        enableConsole: true,
      });

      devLogger.info('test message');
      expect(consoleInfoSpy).toHaveBeenCalled();

      devLogger.destroy();
    });

    it('shouldBeAtprodenv禁用控制台output', () => {
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
    it('shouldhandle没有上下文的log', () => {
      logger.info('message without context');
      expect(consoleInfoSpy).toHaveBeenCalled();
    });

    it('shouldhandle没有errorobject的errorlog', () => {
      logger.error('error without error object');
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('shouldhandle空字符串消息', () => {
      logger.info('');
      expect(consoleInfoSpy).toHaveBeenCalled();
    });

    it('shouldhandle大量log', () => {
      for (let i = 0; i < 100; i++) {
        logger.info(`message ${i}`);
      }

      // should触发多timesrefresh
      const buffer = logger.getBufferStatus();
      expect(buffer.total).toBeLessThan(100);
    });
  });
});
