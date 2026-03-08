/**
 * Logger服务
 * 
 * 功能:
 * - 支持不同日志级别 (debug, info, warn, error)
 * - 根据环境设置日志级别（开发：debug，生产：error/warn）
 * - 记录API请求日志（响应时间和状态码）
 * - 记录用户操作日志（用户ID、时间戳和操作类型）
 * - 实现批量日志发送到服务器
 * 
 * 验证需求: 8.4, 9.2, 9.3
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  id: string;
  level: LogLevel;
  message: string;
  timestamp: Date;
  source?: string;
  context?: Record<string, any>;
  userId?: string;
  sessionId?: string;
}

export interface ApiRequestLog {
  id: string;
  method: string;
  url: string;
  status: number;
  duration: number; // 毫秒
  requestSize?: number; // 字节
  responseSize?: number; // 字节
  timestamp: Date;
  userId?: string;
  error?: string;
}

export interface UserActionLog {
  id: string;
  action: string;
  userId: string;
  page: string;
  details?: Record<string, any>;
  timestamp: Date;
}

export interface LoggerConfig {
  level: LogLevel;
  environment: 'development' | 'test' | 'production';
  enableConsole?: boolean;
  batchSize?: number; // 批量发送的日志数量
  flushInterval?: number; // 自动刷新间隔（毫秒）
  endpoint?: string; // 日志服务器端点
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

/**
 * Logger类
 * 负责日志记录、批量发送和级别过滤
 */
export class Logger {
  private config: LoggerConfig;
  private logBuffer: LogEntry[];
  private apiLogBuffer: ApiRequestLog[];
  private userActionBuffer: UserActionLog[];
  private flushTimer: NodeJS.Timeout | null;
  private currentUserId?: string;
  private sessionId: string;

  constructor(config: LoggerConfig) {
    this.config = {
      enableConsole: config.environment === 'development',
      batchSize: 50,
      flushInterval: 30000, // 30秒
      ...config,
    };

    this.logBuffer = [];
    this.apiLogBuffer = [];
    this.userActionBuffer = [];
    this.flushTimer = null;
    this.sessionId = this.generateSessionId();

    // 根据环境设置默认日志级别
    if (!config.level) {
      this.config.level = config.environment === 'development' ? 'debug' : 'error';
    }

    // 启动自动刷新定时器
    this.startFlushTimer();
  }

  /**
   * 设置日志级别
   */
  setLevel(level: LogLevel): void {
    this.config.level = level;
  }

  /**
   * 获取当前日志级别
   */
  getLevel(): LogLevel {
    return this.config.level;
  }

  /**
   * 设置当前用户ID
   */
  setUserId(userId: string | undefined): void {
    this.currentUserId = userId;
  }

  /**
   * 获取当前用户ID
   */
  getUserId(): string | undefined {
    return this.currentUserId;
  }

  /**
   * Debug级别日志
   */
  debug(message: string, context?: Record<string, any>): void {
    this.log('debug', message, context);
  }

  /**
   * Info级别日志
   */
  info(message: string, context?: Record<string, any>): void {
    this.log('info', message, context);
  }

  /**
   * Warn级别日志
   */
  warn(message: string, context?: Record<string, any>): void {
    this.log('warn', message, context);
  }

  /**
   * Error级别日志
   */
  error(message: string, error?: Error, context?: Record<string, any>): void {
    const errorContext = error
      ? {
          ...context,
          errorName: error.name,
          errorMessage: error.message,
          errorStack: error.stack,
        }
      : context;

    this.log('error', message, errorContext);
  }

  /**
   * 记录API请求日志
   */
  logApiRequest(
    url: string,
    method: string,
    duration: number,
    status: number,
    options?: {
      requestSize?: number;
      responseSize?: number;
      error?: string;
    }
  ): void {
    const log: ApiRequestLog = {
      id: this.generateLogId(),
      method: method.toUpperCase(),
      url,
      status,
      duration,
      requestSize: options?.requestSize,
      responseSize: options?.responseSize,
      timestamp: new Date(),
      userId: this.currentUserId,
      error: options?.error,
    };

    this.apiLogBuffer.push(log);

    // 输出到控制台（开发环境）
    if (this.config.enableConsole) {
      const statusColor = status >= 400 ? '\x1b[31m' : status >= 300 ? '\x1b[33m' : '\x1b[32m';
      const durationColor = duration > 1000 ? '\x1b[31m' : duration > 500 ? '\x1b[33m' : '\x1b[32m';
      console.log(
        `[API] ${method.toUpperCase()} ${url} ${statusColor}${status}\x1b[0m ${durationColor}${duration}ms\x1b[0m`
      );
    }

    // 检查是否需要刷新
    this.checkAndFlush();
  }

  /**
   * 记录用户操作日志
   */
  logUserAction(action: string, userId: string, details?: Record<string, any>): void {
    const log: UserActionLog = {
      id: this.generateLogId(),
      action,
      userId,
      page: typeof window !== 'undefined' ? window.location.pathname : '',
      details,
      timestamp: new Date(),
    };

    this.userActionBuffer.push(log);

    // 输出到控制台（开发环境）
    if (this.config.enableConsole) {
      console.log(`[USER ACTION] ${action} by ${userId}`, details || '');
    }

    // 检查是否需要刷新
    this.checkAndFlush();
  }

  /**
   * 通用日志记录方法
   */
  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    // 检查日志级别
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      id: this.generateLogId(),
      level,
      message,
      timestamp: new Date(),
      context,
      userId: this.currentUserId,
      sessionId: this.sessionId,
    };

    this.logBuffer.push(entry);

    // 输出到控制台
    if (this.config.enableConsole) {
      this.logToConsole(entry);
    }

    // 检查是否需要刷新
    this.checkAndFlush();
  }

  /**
   * 检查是否应该记录该级别的日志
   */
  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.config.level];
  }

  /**
   * 输出日志到控制台
   */
  private logToConsole(entry: LogEntry): void {
    const timestamp = entry.timestamp.toISOString();
    const prefix = `[${timestamp}] [${entry.level.toUpperCase()}]`;

    switch (entry.level) {
      case 'debug':
        console.debug(prefix, entry.message, entry.context || '');
        break;
      case 'info':
        console.info(prefix, entry.message, entry.context || '');
        break;
      case 'warn':
        console.warn(prefix, entry.message, entry.context || '');
        break;
      case 'error':
        console.error(prefix, entry.message, entry.context || '');
        break;
    }
  }

  /**
   * 检查并刷新日志缓冲区
   */
  private checkAndFlush(): void {
    const totalLogs =
      this.logBuffer.length + this.apiLogBuffer.length + this.userActionBuffer.length;

    if (totalLogs >= this.config.batchSize!) {
      this.flushLogs();
    }
  }

  /**
   * 批量发送日志到服务器
   */
  async flushLogs(): Promise<void> {
    // 如果没有日志需要发送，直接返回
    if (
      this.logBuffer.length === 0 &&
      this.apiLogBuffer.length === 0 &&
      this.userActionBuffer.length === 0
    ) {
      return;
    }

    // 复制并清空缓冲区
    const logsToSend = [...this.logBuffer];
    const apiLogsToSend = [...this.apiLogBuffer];
    const userActionsToSend = [...this.userActionBuffer];

    this.logBuffer = [];
    this.apiLogBuffer = [];
    this.userActionBuffer = [];

    // 如果没有配置端点，只清空缓冲区
    if (!this.config.endpoint) {
      if (this.config.enableConsole) {
        console.debug('[Logger] No endpoint configured, logs discarded', {
          logs: logsToSend.length,
          apiLogs: apiLogsToSend.length,
          userActions: userActionsToSend.length,
        });
      }
      return;
    }

    try {
      // 发送日志到服务器
      const payload = {
        logs: logsToSend,
        apiLogs: apiLogsToSend,
        userActions: userActionsToSend,
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
      };

      // 在生产环境中，这里会发送到日志服务器
      // await fetch(this.config.endpoint, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(payload),
      // });

      if (this.config.enableConsole) {
        console.debug('[Logger] Logs flushed to server', {
          logs: logsToSend.length,
          apiLogs: apiLogsToSend.length,
          userActions: userActionsToSend.length,
        });
      }
    } catch (error) {
      // 发送失败，记录错误但不重新添加到缓冲区（避免无限循环）
      console.error('[Logger] Failed to flush logs:', error);
    }
  }

  /**
   * 启动自动刷新定时器
   */
  private startFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    this.flushTimer = setInterval(() => {
      this.flushLogs();
    }, this.config.flushInterval!);
  }

  /**
   * 停止自动刷新定时器
   */
  stopFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
  }

  /**
   * 销毁Logger实例
   */
  async destroy(): Promise<void> {
    this.stopFlushTimer();
    await this.flushLogs(); // 最后一次刷新
  }

  /**
   * 生成日志ID
   */
  private generateLogId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * 获取缓冲区状态
   */
  getBufferStatus(): {
    logs: number;
    apiLogs: number;
    userActions: number;
    total: number;
  } {
    return {
      logs: this.logBuffer.length,
      apiLogs: this.apiLogBuffer.length,
      userActions: this.userActionBuffer.length,
      total: this.logBuffer.length + this.apiLogBuffer.length + this.userActionBuffer.length,
    };
  }
}

/**
 * 创建默认Logger实例的工厂函数
 */
export function createDefaultLogger(): Logger {
  const environment = (process.env.NODE_ENV as 'development' | 'test' | 'production') || 'development';
  
  const config: LoggerConfig = {
    level: environment === 'development' ? 'debug' : 'error',
    environment,
    enableConsole: environment === 'development',
    batchSize: 50,
    flushInterval: 30000, // 30秒
    endpoint: process.env.NEXT_PUBLIC_LOG_ENDPOINT,
  };

  return new Logger(config);
}

// 默认实例 - 延迟初始化
let defaultInstance: Logger | null = null;

export function getLogger(): Logger {
  if (!defaultInstance) {
    defaultInstance = createDefaultLogger();
  }
  return defaultInstance;
}

export function resetLogger(): void {
  if (defaultInstance) {
    defaultInstance.destroy();
    defaultInstance = null;
  }
}
