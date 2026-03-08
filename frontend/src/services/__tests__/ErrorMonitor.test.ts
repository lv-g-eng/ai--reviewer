/**
 * ErrorMonitor单元test
 * 
 * testCoverage:
 * - 初始化andconfig
 * - error捕获and上报
 * - 消息捕获
 * - user上下文set
 * - error率监控（5min窗口，10%threshold）
 * - 告警触发机制
 * - 全局errorhandle
 * - error分class
 */

import { ErrorMonitor, MonitorConfig, getErrorMonitor, resetErrorMonitor } from '../ErrorMonitor';

describe('ErrorMonitor', () => {
  let errorMonitor: ErrorMonitor;
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleLogSpy: jest.SpyInstance;

  const defaultConfig: MonitorConfig = {
    environment: 'test',
    enableDebugMode: true,
  };

  beforeEach(() => {
    // reset单例
    resetErrorMonitor();
    
    // Mock consolemethod
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

    errorMonitor = new ErrorMonitor(defaultConfig);
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleLogSpy.mockRestore();
  });

  describe('初始化', () => {
    it('shouldsuccess初始化', () => {
      errorMonitor.initialize();
      
      // 初始化后should能够捕获error
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('shouldsupport初始化时传入config', () => {
      errorMonitor.initialize({
        dsn: 'https://test@sentry.io/123',
        sampleRate: 0.5,
      });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('未初始化时捕获errorshouldshowwarn', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('error捕获', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('should捕获并recorderror', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          message: 'Test error',
          type: 'unknown',
        })
      );
    });

    it('shouldcontainerror堆栈', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          stack: expect.any(String),
        })
      );
    });

    it('shouldcontainerror上下文', () => {
      const error = new Error('Test error');
      const context = {
        userId: 'user123',
        url: 'https://example.com/page',
        userAgent: 'Mozilla/5.0',
        additionalData: { key: 'value' },
      };
      
      errorMonitor.captureError(error, context);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          context: expect.objectContaining({
            userId: 'user123',
            url: 'https://example.com/page',
            userAgent: 'Mozilla/5.0',
            additionalData: { key: 'value' },
          }),
        })
      );
    });

    it('shoulduse当前userID作为默认userId', () => {
      errorMonitor.setUser({ id: 'user456', email: 'test@example.com' });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          context: expect.objectContaining({
            userId: 'user456',
          }),
        })
      );
    });

    it('shouldgenerate唯一的errorID', () => {
      const error1 = new Error('Error 1');
      const error2 = new Error('Error 2');
      
      errorMonitor.captureError(error1);
      errorMonitor.captureError(error2);
      
      const calls = consoleErrorSpy.mock.calls;
      const id1 = calls[0][1].id;
      const id2 = calls[1][1].id;
      
      expect(id1).not.toBe(id2);
      expect(id1).toMatch(/^error_\d+_[a-z0-9]+$/);
    });

    it('shouldsupportbeforeSend钩子', () => {
      const beforeSend = jest.fn((report) => ({
        ...report,
        message: 'Modified: ' + report.message,
      }));
      
      errorMonitor.initialize({ beforeSend });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(beforeSend).toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          message: 'Modified: Test error',
        })
      );
    });

    it('beforeSendreturnnull时should不上报error', () => {
      const beforeSend = jest.fn(() => null);
      
      errorMonitor.initialize({ beforeSend });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(beforeSend).toHaveBeenCalled();
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('error分class', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('should识别网络error', () => {
      const error = new Error('Network error occurred');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'network' })
      );
    });

    it('should识别verifyerror', () => {
      const error = new Error('Validation failed');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'validation' })
      );
    });

    it('should识别authorizeerror', () => {
      const error = new Error('Unauthorized access');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'authorization' })
      );
    });

    it('should识别service器error', () => {
      const error = new Error('500 Internal Server Error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'server' })
      );
    });

    it('should识别客户端error', () => {
      const error = new TypeError('Cannot read property of undefined');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'client' })
      );
    });

    it('should将未知error分class为unknown', () => {
      const error = new Error('Some random error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'unknown' })
      );
    });
  });

  describe('消息捕获', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('should捕获info级别消息', () => {
      errorMonitor.captureMessage('Info message', 'info');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] INFO: Info message'
      );
    });

    it('should捕获warning级别消息', () => {
      errorMonitor.captureMessage('Warning message', 'warning');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] WARNING: Warning message'
      );
    });

    it('should捕获error级别消息', () => {
      errorMonitor.captureMessage('Error message', 'error');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] ERROR: Error message'
      );
    });

    it('默认shoulduseinfo级别', () => {
      errorMonitor.captureMessage('Default message');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] INFO: Default message'
      );
    });

    it('未初始化时shouldshowwarn', () => {
      const uninitializedMonitor = new ErrorMonitor(defaultConfig);
      uninitializedMonitor.captureMessage('Test message');
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('user上下文', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('shouldsetuser上下文', () => {
      errorMonitor.setUser({ id: 'user123', email: 'test@example.com' });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          context: expect.objectContaining({
            userId: 'user123',
          }),
        })
      );
    });

    it('shouldsupport清除user上下文', () => {
      errorMonitor.setUser({ id: 'user123' });
      errorMonitor.setUser(null);
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          context: expect.objectContaining({
            userId: undefined,
          }),
        })
      );
    });

    it('未初始化时setusershouldshowwarn', () => {
      const uninitializedMonitor = new ErrorMonitor(defaultConfig);
      uninitializedMonitor.setUser({ id: 'user123' });
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('error率监控', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('should正确计算error率', () => {
      // record10itemrequest，其中2itemfailure
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      const errorRate = errorMonitor.getErrorRate();
      expect(errorRate).toBe(0.2); // 20%
    });

    it('没有request时error率should为0', () => {
      const errorRate = errorMonitor.getErrorRate();
      expect(errorRate).toBe(0);
    });

    it('shouldBeAterror率超过10%时触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // record10itemrequest，其中2itemfailure（20%error率）
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(alertCallback).toHaveBeenCalledWith(
        expect.stringContaining('Error rate exceeded 10%')
      );
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor ALERT]',
        expect.stringContaining('Error rate exceeded 10%')
      );
    });

    it('error率低于10%时不should触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // record10itemrequest，其中1itemfailure（10%error率，刚好等于threshold）
      for (let i = 0; i < 9; i++) {
        errorMonitor.recordRequest(true);
      }
      errorMonitor.recordRequest(false);
      
      expect(alertCallback).not.toHaveBeenCalled();
    });

    it('request数少于10时不should触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // record5itemrequest，其中3itemfailure（60%error率，但样本太小）
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 3; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(alertCallback).not.toHaveBeenCalled();
    });

    it('shouldBeAt5min后reseterror率窗口', () => {
      jest.useFakeTimers();
      
      // record一些error
      for (let i = 0; i < 10; i++) {
        errorMonitor.recordRequest(false);
      }
      
      let stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(10);
      expect(stats.totalRequests).toBe(10);
      
      // 前进5min
      jest.advanceTimersByTime(5 * 60 * 1000 + 1);
      
      // 窗口should被reset
      stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(0);
      expect(stats.totalRequests).toBe(0);
      
      jest.useRealTimers();
    });

    it('触发告警后不should立即reset窗口', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // 触发告警
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(alertCallback).toHaveBeenCalled();
      
      // 窗口不should被reset，但alertTriggered标志should被set
      const stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(2);
      expect(stats.totalRequests).toBe(10);
      expect(stats.alertTriggered).toBe(true);
    });

    it('shouldsupport多item告警回调', () => {
      const callback1 = jest.fn();
      const callback2 = jest.fn();
      
      errorMonitor.onAlert(callback1);
      errorMonitor.onAlert(callback2);
      
      // 触发告警
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(callback1).toHaveBeenCalled();
      expect(callback2).toHaveBeenCalled();
    });

    it('should能够清除告警回调', () => {
      const callback = jest.fn();
      errorMonitor.onAlert(callback);
      errorMonitor.clearAlertCallbacks();
      
      // 触发告警
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(callback).not.toHaveBeenCalled();
    });

    it('告警回调抛出error不should影响其他回调', () => {
      const callback1 = jest.fn(() => {
        throw new Error('Callback error');
      });
      const callback2 = jest.fn();
      
      errorMonitor.onAlert(callback1);
      errorMonitor.onAlert(callback2);
      
      // 触发告警
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(callback1).toHaveBeenCalled();
      expect(callback2).toHaveBeenCalled();
    });
  });

  describe('单例模式', () => {
    it('shouldreturn同一iteminstance', () => {
      const instance1 = getErrorMonitor(defaultConfig);
      const instance2 = getErrorMonitor();
      
      expect(instance1).toBe(instance2);
    });

    it('首times调用时mustprovideconfig', () => {
      expect(() => getErrorMonitor()).toThrow('ErrorMonitor config is required');
    });

    it('should能够reset单例', () => {
      const instance1 = getErrorMonitor(defaultConfig);
      resetErrorMonitor();
      const instance2 = getErrorMonitor(defaultConfig);
      
      expect(instance1).not.toBe(instance2);
    });
  });

  describe('边缘情况', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('shouldhandle没有堆栈的error', () => {
      const error = new Error('Test error');
      delete error.stack;
      
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          message: 'Test error',
          stack: undefined,
        })
      );
    });

    it('shouldhandle空的additionalData', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error, { additionalData: {} });
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          context: expect.objectContaining({
            additionalData: {},
          }),
        })
      );
    });

    it('shouldhandle非调试模式', () => {
      const prodMonitor = new ErrorMonitor({
        environment: 'production',
        enableDebugMode: false,
      });
      prodMonitor.initialize();
      
      const error = new Error('Test error');
      prodMonitor.captureError(error);
      
      // 非调试模式下不shouldoutput到控制台
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });
});
