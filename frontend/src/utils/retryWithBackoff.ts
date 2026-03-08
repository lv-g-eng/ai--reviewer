/**
 * retryWithBackoff - 指数退避重试工具函数
 * 
 * 实现指数退避算法，用于在失败时自动重试操作。
 * 支持可配置的重试次数、延迟时间和退避因子。
 * 
 * 使用场景:
 * - API请求失败重试
 * - 网络操作重试
 * - 任何需要容错的异步操作
 * 
 * @example
 * ```typescript
 * const result = await retryWithBackoff(
 *   () => fetch('/api/data'),
 *   {
 *     maxRetries: 3,
 *     initialDelay: 1000,
 *     maxDelay: 10000,
 *     factor: 2,
 *     shouldRetry: (error) => error.status >= 500
 *   }
 * );
 * ```
 */

/**
 * 重试选项配置
 */
export interface RetryOptions {
  /** 最大重试次数 */
  maxRetries: number;
  /** 初始延迟时间（毫秒） */
  initialDelay: number;
  /** 最大延迟时间（毫秒） */
  maxDelay: number;
  /** 退避因子（每次重试延迟时间的倍数） */
  factor: number;
  /** 自定义判断是否应该重试的函数 */
  shouldRetry?: (error: Error) => boolean;
}

/**
 * 默认的重试判断函数
 * 对于网络错误和5xx服务器错误进行重试
 */
function defaultShouldRetry(error: any): boolean {
  // 网络错误
  if (error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND' || error.code === 'ETIMEDOUT') {
    return true;
  }

  // 5xx服务器错误
  if (error.response?.status >= 500 && error.response?.status < 600) {
    return true;
  }

  // 429 Too Many Requests
  if (error.response?.status === 429) {
    return true;
  }

  // 不重试客户端错误 (4xx) 和认证错误
  if (error.response?.status >= 400 && error.response?.status < 500) {
    return false;
  }

  // 默认重试未知错误
  return true;
}

/**
 * 使用指数退避策略重试异步操作
 * 
 * @param fn - 要执行的异步函数
 * @param options - 重试配置选项
 * @returns Promise<T> - 函数执行结果
 * @throws 如果所有重试都失败，抛出最后一次的错误
 * 
 * @example
 * ```typescript
 * // 基本使用
 * const data = await retryWithBackoff(
 *   () => apiClient.get('/data'),
 *   { maxRetries: 3, initialDelay: 1000, maxDelay: 10000, factor: 2 }
 * );
 * 
 * // 自定义重试条件
 * const data = await retryWithBackoff(
 *   () => apiClient.get('/data'),
 *   {
 *     maxRetries: 3,
 *     initialDelay: 1000,
 *     maxDelay: 10000,
 *     factor: 2,
 *     shouldRetry: (error) => error.message.includes('timeout')
 *   }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxRetries, initialDelay, maxDelay, factor, shouldRetry = defaultShouldRetry } = options;

  let lastError: Error;
  let attempt = 0;

  while (attempt <= maxRetries) {
    try {
      // 尝试执行函数
      return await fn();
    } catch (error: any) {
      lastError = error;

      // 检查是否应该重试
      if (!shouldRetry(error)) {
        throw error;
      }

      // 如果已达到最大重试次数，抛出错误
      if (attempt >= maxRetries) {
        throw error;
      }

      // 计算延迟时间: initialDelay * (factor ^ attempt)
      const delay = Math.min(initialDelay * Math.pow(factor, attempt), maxDelay);

      // 添加随机抖动 (±10%) 以避免重试风暴
      const jitter = delay * 0.1 * (Math.random() * 2 - 1);
      const actualDelay = Math.max(0, delay + jitter);

      // 等待后重试
      await sleep(actualDelay);

      attempt++;
    }
  }

  // 理论上不会到达这里，但为了类型安全
  throw lastError!;
}

/**
 * 睡眠函数
 * @param ms - 睡眠时间（毫秒）
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 创建预配置的重试函数
 * 
 * @param options - 重试配置选项
 * @returns 返回一个已配置好的重试函数
 * 
 * @example
 * ```typescript
 * const retryApi = createRetryFunction({
 *   maxRetries: 3,
 *   initialDelay: 1000,
 *   maxDelay: 10000,
 *   factor: 2
 * });
 * 
 * const data = await retryApi(() => apiClient.get('/data'));
 * ```
 */
export function createRetryFunction(options: RetryOptions) {
  return <T>(fn: () => Promise<T>): Promise<T> => {
    return retryWithBackoff(fn, options);
  };
}

/**
 * 默认的API重试配置
 * 符合需求 10.3: 最多重试3次，使用指数退避策略
 */
export const DEFAULT_API_RETRY_OPTIONS: RetryOptions = {
  maxRetries: 3,
  initialDelay: 1000, // 1秒
  maxDelay: 10000, // 10秒
  factor: 2, // 每次延迟翻倍: 1s, 2s, 4s
};

/**
 * 任务队列重试配置
 * 符合需求 5.2: 在5分钟、15分钟、30分钟后重试
 */
export const TASK_QUEUE_RETRY_OPTIONS: RetryOptions = {
  maxRetries: 3,
  initialDelay: 5 * 60 * 1000, // 5分钟
  maxDelay: 30 * 60 * 1000, // 30分钟
  factor: 3, // 5分钟, 15分钟, 30分钟 (实际: 5min, 15min, 45min，需要调整)
};

// 调整任务队列配置以精确匹配需求
export const TASK_QUEUE_RETRY_OPTIONS_EXACT: RetryOptions = {
  maxRetries: 3,
  initialDelay: 5 * 60 * 1000, // 5分钟
  maxDelay: 30 * 60 * 1000, // 30分钟
  factor: 3, // 使用自定义延迟计算
  shouldRetry: (error: any) => {
    // 任务失败总是重试
    return true;
  },
};

/**
 * 为任务队列创建精确延迟的重试函数
 * 延迟时间: 5分钟、15分钟、30分钟
 */
export async function retryTaskWithExactDelays<T>(
  fn: () => Promise<T>,
  delays: number[] = [5 * 60 * 1000, 15 * 60 * 1000, 30 * 60 * 1000]
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= delays.length; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;

      // 如果是最后一次尝试，抛出错误
      if (attempt >= delays.length) {
        throw error;
      }

      // 使用精确的延迟时间
      await sleep(delays[attempt]);
    }
  }

  throw lastError!;
}
