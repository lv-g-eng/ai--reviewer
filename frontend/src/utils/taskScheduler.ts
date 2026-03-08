/**
 * 任务优先级调度器
 * 
 * 实现基于优先级和资源可用性的任务调度算法
 * 
 * 验证需求: 5.1
 */

import { AnalysisTask } from '../pages/AnalysisQueue';

/**
 * 调度器配置
 */
export interface SchedulerConfig {
  /** 最大并发任务数 */
  maxConcurrent: number;
  /** 资源可用性检查函数（可选） */
  checkResourceAvailability?: () => boolean;
}

/**
 * 调度结果
 */
export interface ScheduleResult {
  /** 应该执行的任务列表（按优先级排序） */
  tasksToExecute: AnalysisTask[];
  /** 等待中的任务列表 */
  waitingTasks: AnalysisTask[];
  /** 当前运行的任务数 */
  runningCount: number;
  /** 可用的执行槽位数 */
  availableSlots: number;
}

/**
 * 任务优先级调度器类
 * 
 * 根据任务优先级和资源可用性调度任务执行
 */
export class TaskScheduler {
  private config: SchedulerConfig;

  constructor(config: SchedulerConfig) {
    this.config = config;
  }

  /**
   * 调度任务
   * 
   * @param tasks - 所有任务列表
   * @returns 调度结果
   */
  schedule(tasks: AnalysisTask[]): ScheduleResult {
    // 统计当前运行的任务数
    const runningTasks = tasks.filter(t => t.status === 'running');
    const runningCount = runningTasks.length;

    // 计算可用的执行槽位
    const availableSlots = Math.max(0, this.config.maxConcurrent - runningCount);

    // 获取待处理的任务（pending状态）
    const pendingTasks = tasks.filter(t => t.status === 'pending');

    // 按优先级排序（高优先级在前）
    const sortedPendingTasks = this.sortByPriority(pendingTasks);

    // 检查资源可用性
    const resourcesAvailable = this.config.checkResourceAvailability
      ? this.config.checkResourceAvailability()
      : true;

    // 如果没有可用槽位或资源不可用，所有任务都等待
    if (availableSlots === 0 || !resourcesAvailable) {
      return {
        tasksToExecute: [],
        waitingTasks: sortedPendingTasks,
        runningCount,
        availableSlots: 0,
      };
    }

    // 选择应该执行的任务（取前N个高优先级任务）
    const tasksToExecute = sortedPendingTasks.slice(0, availableSlots);
    const waitingTasks = sortedPendingTasks.slice(availableSlots);

    return {
      tasksToExecute,
      waitingTasks,
      runningCount,
      availableSlots,
    };
  }

  /**
   * 按优先级排序任务
   * 
   * 排序规则：
   * 1. 优先级高的在前（priority降序）
   * 2. 优先级相同时，创建时间早的在前（FIFO）
   * 
   * @param tasks - 待排序的任务列表
   * @returns 排序后的任务列表
   */
  sortByPriority(tasks: AnalysisTask[]): AnalysisTask[] {
    return [...tasks].sort((a, b) => {
      // 首先按优先级降序排序（高优先级在前）
      if (a.priority !== b.priority) {
        return b.priority - a.priority;
      }

      // 优先级相同时，按创建时间升序排序（早创建的在前）
      const timeA = new Date(a.createdAt).getTime();
      const timeB = new Date(b.createdAt).getTime();
      return timeA - timeB;
    });
  }

  /**
   * 获取下一个应该执行的任务
   * 
   * @param tasks - 所有任务列表
   * @returns 下一个应该执行的任务，如果没有则返回null
   */
  getNextTask(tasks: AnalysisTask[]): AnalysisTask | null {
    const result = this.schedule(tasks);
    return result.tasksToExecute.length > 0 ? result.tasksToExecute[0] : null;
  }

  /**
   * 更新调度器配置
   * 
   * @param config - 新的配置（部分更新）
   */
  updateConfig(config: Partial<SchedulerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * 获取当前配置
   * 
   * @returns 当前调度器配置
   */
  getConfig(): SchedulerConfig {
    return { ...this.config };
  }
}

/**
 * 创建默认的任务调度器
 * 
 * @param maxConcurrent - 最大并发任务数，默认为3
 * @returns 任务调度器实例
 */
export function createTaskScheduler(maxConcurrent: number = 3): TaskScheduler {
  return new TaskScheduler({ maxConcurrent });
}
