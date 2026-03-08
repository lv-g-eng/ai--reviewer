/**
 * 任务自动重试调度器
 * 
 * 实现失败任务的自动重试机制
 * - 重试延迟: 5分钟、15分钟、30分钟
 * - 最多重试3次
 * 
 * 验证需求: 5.2
 */

import { AnalysisTask } from '../pages/AnalysisQueue';

/**
 * 重试延迟配置（毫秒）
 */
export const RETRY_DELAYS = [
  5 * 60 * 1000,  // 5分钟
  15 * 60 * 1000, // 15分钟
  30 * 60 * 1000, // 30分钟
];

/**
 * 重试调度信息
 */
export interface RetrySchedule {
  /** 任务ID */
  taskId: string;
  /** 当前重试次数 */
  retryCount: number;
  /** 下次重试时间 */
  nextRetryTime: Date;
  /** 重试延迟（毫秒） */
  retryDelay: number;
}

/**
 * 任务重试调度器
 */
export class TaskRetryScheduler {
  private retrySchedules: Map<string, RetrySchedule> = new Map();
  private retryTimers: Map<string, NodeJS.Timeout> = new Map();
  private onRetryCallback?: (taskId: string) => void;

  /**
   * 设置重试回调函数
   * 
   * @param callback - 当任务需要重试时调用的回调函数
   */
  setRetryCallback(callback: (taskId: string) => void): void {
    this.onRetryCallback = callback;
  }

  /**
   * 调度失败任务的重试
   * 
   * @param task - 失败的任务
   * @returns 重试调度信息，如果不应该重试则返回null
   */
  scheduleRetry(task: AnalysisTask): RetrySchedule | null {
    // 检查是否已达到最大重试次数
    if (task.retryCount >= task.maxRetries) {
      return null;
    }

    // 检查任务状态是否为失败
    if (task.status !== 'failed') {
      return null;
    }

    // 计算重试延迟
    const retryDelay = this.getRetryDelay(task.retryCount);
    const nextRetryTime = new Date(Date.now() + retryDelay);

    // 创建重试调度信息
    const schedule: RetrySchedule = {
      taskId: task.id,
      retryCount: task.retryCount,
      nextRetryTime,
      retryDelay,
    };

    // 保存调度信息
    this.retrySchedules.set(task.id, schedule);

    // 清除旧的定时器（如果存在）
    this.clearRetryTimer(task.id);

    // 设置新的重试定时器
    const timer = setTimeout(() => {
      this.executeRetry(task.id);
    }, retryDelay);

    this.retryTimers.set(task.id, timer);

    return schedule;
  }

  /**
   * 获取重试延迟
   * 
   * @param retryCount - 当前重试次数
   * @returns 重试延迟（毫秒）
   */
  getRetryDelay(retryCount: number): number {
    // 使用预定义的重试延迟
    if (retryCount < RETRY_DELAYS.length) {
      return RETRY_DELAYS[retryCount];
    }
    // 如果超出预定义延迟，使用最后一个延迟
    return RETRY_DELAYS[RETRY_DELAYS.length - 1];
  }

  /**
   * 执行重试
   * 
   * @param taskId - 任务ID
   */
  private executeRetry(taskId: string): void {
    // 移除调度信息和定时器
    this.retrySchedules.delete(taskId);
    this.retryTimers.delete(taskId);

    // 调用重试回调
    if (this.onRetryCallback) {
      this.onRetryCallback(taskId);
    }
  }

  /**
   * 清除任务的重试定时器
   * 
   * @param taskId - 任务ID
   */
  clearRetryTimer(taskId: string): void {
    const timer = this.retryTimers.get(taskId);
    if (timer) {
      clearTimeout(timer);
      this.retryTimers.delete(taskId);
    }
  }

  /**
   * 取消任务的重试调度
   * 
   * @param taskId - 任务ID
   */
  cancelRetry(taskId: string): void {
    this.clearRetryTimer(taskId);
    this.retrySchedules.delete(taskId);
  }

  /**
   * 获取任务的重试调度信息
   * 
   * @param taskId - 任务ID
   * @returns 重试调度信息，如果不存在则返回null
   */
  getRetrySchedule(taskId: string): RetrySchedule | null {
    return this.retrySchedules.get(taskId) || null;
  }

  /**
   * 获取所有重试调度信息
   * 
   * @returns 所有重试调度信息的数组
   */
  getAllRetrySchedules(): RetrySchedule[] {
    return Array.from(this.retrySchedules.values());
  }

  /**
   * 检查任务是否已调度重试
   * 
   * @param taskId - 任务ID
   * @returns 是否已调度重试
   */
  isScheduled(taskId: string): boolean {
    return this.retrySchedules.has(taskId);
  }

  /**
   * 获取距离下次重试的剩余时间
   * 
   * @param taskId - 任务ID
   * @returns 剩余时间（毫秒），如果未调度则返回null
   */
  getTimeUntilRetry(taskId: string): number | null {
    const schedule = this.retrySchedules.get(taskId);
    if (!schedule) {
      return null;
    }

    const now = Date.now();
    const retryTime = schedule.nextRetryTime.getTime();
    return Math.max(0, retryTime - now);
  }

  /**
   * 格式化重试延迟为可读字符串
   * 
   * @param delayMs - 延迟时间（毫秒）
   * @returns 格式化的字符串
   */
  formatRetryDelay(delayMs: number): string {
    const minutes = Math.floor(delayMs / (60 * 1000));
    if (minutes < 60) {
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
    const hours = Math.floor(minutes / 60);
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  }

  /**
   * 清理所有重试调度
   */
  clearAll(): void {
    // 清除所有定时器
    for (const timer of this.retryTimers.values()) {
      clearTimeout(timer);
    }
    this.retryTimers.clear();
    this.retrySchedules.clear();
  }

  /**
   * 获取重试状态描述
   * 
   * @param task - 任务
   * @returns 重试状态描述
   */
  getRetryStatusText(task: AnalysisTask): string {
    if (task.status !== 'failed') {
      return '';
    }

    if (task.retryCount >= task.maxRetries) {
      return 'Max retries reached';
    }

    const schedule = this.getRetrySchedule(task.id);
    if (schedule) {
      const timeUntil = this.getTimeUntilRetry(task.id);
      if (timeUntil !== null) {
        const minutes = Math.ceil(timeUntil / (60 * 1000));
        return `Retry in ${minutes} minute${minutes !== 1 ? 's' : ''}`;
      }
    }

    return 'Retry scheduled';
  }
}

/**
 * 创建任务重试调度器实例
 * 
 * @returns 任务重试调度器实例
 */
export function createTaskRetryScheduler(): TaskRetryScheduler {
  return new TaskRetryScheduler();
}
