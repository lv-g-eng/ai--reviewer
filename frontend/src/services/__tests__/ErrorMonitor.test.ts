/**
 * ErrorMonitor单元测试
 * 
 * 测试覆盖:
 * - 初始化和配置
 * - 错误捕获和上报
 * - 消息捕获
 * - 用户上下文设置
 * - 错误率监控（5分钟窗口，10%阈值）
 * - 告警触发机制
 * - 全局错误处理
 * - 错误分类
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
    // 重置单例
    resetErrorMonitor();
    
    // Mock console方法
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
    it('应该成功初始化', () => {
      errorMonitor.initialize();
      
      // 初始化后应该能够捕获错误
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('应该支持初始化时传入配置', () => {
      errorMonitor.initialize({
        dsn: 'https://test@sentry.io/123',
        sampleRate: 0.5,
      });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('未初始化时捕获错误应该显示警告', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('错误捕获', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('应该捕获并记录错误', () => {
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

    it('应该包含错误堆栈', () => {
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({
          stack: expect.any(String),
        })
      );
    });

    it('应该包含错误上下文', () => {
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

    it('应该使用当前用户ID作为默认userId', () => {
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

    it('应该生成唯一的错误ID', () => {
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

    it('应该支持beforeSend钩子', () => {
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

    it('beforeSend返回null时应该不上报错误', () => {
      const beforeSend = jest.fn(() => null);
      
      errorMonitor.initialize({ beforeSend });
      
      const error = new Error('Test error');
      errorMonitor.captureError(error);
      
      expect(beforeSend).toHaveBeenCalled();
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('错误分类', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('应该识别网络错误', () => {
      const error = new Error('Network error occurred');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'network' })
      );
    });

    it('应该识别验证错误', () => {
      const error = new Error('Validation failed');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'validation' })
      );
    });

    it('应该识别授权错误', () => {
      const error = new Error('Unauthorized access');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'authorization' })
      );
    });

    it('应该识别服务器错误', () => {
      const error = new Error('500 Internal Server Error');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'server' })
      );
    });

    it('应该识别客户端错误', () => {
      const error = new TypeError('Cannot read property of undefined');
      errorMonitor.captureError(error);
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[ErrorMonitor]',
        expect.objectContaining({ type: 'client' })
      );
    });

    it('应该将未知错误分类为unknown', () => {
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

    it('应该捕获info级别消息', () => {
      errorMonitor.captureMessage('Info message', 'info');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] INFO: Info message'
      );
    });

    it('应该捕获warning级别消息', () => {
      errorMonitor.captureMessage('Warning message', 'warning');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] WARNING: Warning message'
      );
    });

    it('应该捕获error级别消息', () => {
      errorMonitor.captureMessage('Error message', 'error');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] ERROR: Error message'
      );
    });

    it('默认应该使用info级别', () => {
      errorMonitor.captureMessage('Default message');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        '[ErrorMonitor] INFO: Default message'
      );
    });

    it('未初始化时应该显示警告', () => {
      const uninitializedMonitor = new ErrorMonitor(defaultConfig);
      uninitializedMonitor.captureMessage('Test message');
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('用户上下文', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('应该设置用户上下文', () => {
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

    it('应该支持清除用户上下文', () => {
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

    it('未初始化时设置用户应该显示警告', () => {
      const uninitializedMonitor = new ErrorMonitor(defaultConfig);
      uninitializedMonitor.setUser({ id: 'user123' });
      
      expect(consoleWarnSpy).toHaveBeenCalledWith('ErrorMonitor not initialized');
    });
  });

  describe('错误率监控', () => {
    beforeEach(() => {
      errorMonitor.initialize();
    });

    it('应该正确计算错误率', () => {
      // 记录10个请求，其中2个失败
      for (let i = 0; i < 8; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(false);
      }
      
      const errorRate = errorMonitor.getErrorRate();
      expect(errorRate).toBe(0.2); // 20%
    });

    it('没有请求时错误率应该为0', () => {
      const errorRate = errorMonitor.getErrorRate();
      expect(errorRate).toBe(0);
    });

    it('应该在错误率超过10%时触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // 记录10个请求，其中2个失败（20%错误率）
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

    it('错误率低于10%时不应该触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // 记录10个请求，其中1个失败（10%错误率，刚好等于阈值）
      for (let i = 0; i < 9; i++) {
        errorMonitor.recordRequest(true);
      }
      errorMonitor.recordRequest(false);
      
      expect(alertCallback).not.toHaveBeenCalled();
    });

    it('请求数少于10时不应该触发告警', () => {
      const alertCallback = jest.fn();
      errorMonitor.onAlert(alertCallback);
      
      // 记录5个请求，其中3个失败（60%错误率，但样本太小）
      for (let i = 0; i < 2; i++) {
        errorMonitor.recordRequest(true);
      }
      for (let i = 0; i < 3; i++) {
        errorMonitor.recordRequest(false);
      }
      
      expect(alertCallback).not.toHaveBeenCalled();
    });

    it('应该在5分钟后重置错误率窗口', () => {
      jest.useFakeTimers();
      
      // 记录一些错误
      for (let i = 0; i < 10; i++) {
        errorMonitor.recordRequest(false);
      }
      
      let stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(10);
      expect(stats.totalRequests).toBe(10);
      
      // 前进5分钟
      jest.advanceTimersByTime(5 * 60 * 1000 + 1);
      
      // 窗口应该被重置
      stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(0);
      expect(stats.totalRequests).toBe(0);
      
      jest.useRealTimers();
    });

    it('触发告警后不应该立即重置窗口', () => {
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
      
      // 窗口不应该被重置，但alertTriggered标志应该被设置
      const stats = errorMonitor.getErrorStats();
      expect(stats.errorCount).toBe(2);
      expect(stats.totalRequests).toBe(10);
      expect(stats.alertTriggered).toBe(true);
    });

    it('应该支持多个告警回调', () => {
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

    it('应该能够清除告警回调', () => {
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

    it('告警回调抛出错误不应该影响其他回调', () => {
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
    it('应该返回同一个实例', () => {
      const instance1 = getErrorMonitor(defaultConfig);
      const instance2 = getErrorMonitor();
      
      expect(instance1).toBe(instance2);
    });

    it('首次调用时必须提供配置', () => {
      expect(() => getErrorMonitor()).toThrow('ErrorMonitor config is required');
    });

    it('应该能够重置单例', () => {
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

    it('应该处理没有堆栈的错误', () => {
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

    it('应该处理空的additionalData', () => {
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

    it('应该处理非调试模式', () => {
      const prodMonitor = new ErrorMonitor({
        environment: 'production',
        enableDebugMode: false,
      });
      prodMonitor.initialize();
      
      const error = new Error('Test error');
      prodMonitor.captureError(error);
      
      // 非调试模式下不应该输出到控制台
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });
});
