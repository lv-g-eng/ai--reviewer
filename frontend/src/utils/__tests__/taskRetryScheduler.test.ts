/**
 * 任务重试调度器单元测试
 */

import { TaskRetryScheduler, RETRY_DELAYS } from '../taskRetryScheduler';
import { AnalysisTask } from '../../pages/AnalysisQueue';

// 创建模拟任务
function createMockTask(overrides?: Partial<AnalysisTask>): AnalysisTask {
  return {
    id: 'task-1',
    name: 'Test Task',
    type: 'code_analysis',
    priority: 5,
    status: 'failed',
    progress: 0,
    projectId: 'project-1',
    createdAt: new Date(),
    retryCount: 0,
    maxRetries: 3,
    ...overrides,
  };
}

describe('TaskRetryScheduler', () => {
  let scheduler: TaskRetryScheduler;

  beforeEach(() => {
    scheduler = new TaskRetryScheduler();
    jest.useFakeTimers();
  });

  afterEach(() => {
    scheduler.clearAll();
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  describe('scheduleRetry', () => {
    it('should schedule retry for failed task', () => {
      const task = createMockTask({ status: 'failed', retryCount: 0 });
      const schedule = scheduler.scheduleRetry(task);

      expect(schedule).not.toBeNull();
      expect(schedule?.taskId).toBe(task.id);
      expect(schedule?.retryCount).toBe(0);
      expect(schedule?.retryDelay).toBe(RETRY_DELAYS[0]); // 5分钟
    });

    it('should not schedule retry if max retries reached', () => {
      const task = createMockTask({ status: 'failed', retryCount: 3, maxRetries: 3 });
      const schedule = scheduler.scheduleRetry(task);

      expect(schedule).toBeNull();
    });

    it('should not schedule retry for non-failed task', () => {
      const task = createMockTask({ status: 'pending', retryCount: 0 });
      const schedule = scheduler.scheduleRetry(task);

      expect(schedule).toBeNull();
    });

    it('should use correct retry delay based on retry count', () => {
      // 第一次重试 - 5分钟
      const task1 = createMockTask({ retryCount: 0 });
      const schedule1 = scheduler.scheduleRetry(task1);
      expect(schedule1?.retryDelay).toBe(RETRY_DELAYS[0]);

      // 第二次重试 - 15分钟
      const task2 = createMockTask({ id: 'task-2', retryCount: 1 });
      const schedule2 = scheduler.scheduleRetry(task2);
      expect(schedule2?.retryDelay).toBe(RETRY_DELAYS[1]);

      // 第三次重试 - 30分钟
      const task3 = createMockTask({ id: 'task-3', retryCount: 2 });
      const schedule3 = scheduler.scheduleRetry(task3);
      expect(schedule3?.retryDelay).toBe(RETRY_DELAYS[2]);
    });

    it('should call retry callback after delay', () => {
      const callback = jest.fn();
      scheduler.setRetryCallback(callback);

      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      // 回调不应该立即被调用
      expect(callback).not.toHaveBeenCalled();

      // 快进到重试时间
      jest.advanceTimersByTime(RETRY_DELAYS[0]);

      // 回调应该被调用
      expect(callback).toHaveBeenCalledWith(task.id);
    });

    it('should replace existing retry schedule', () => {
      const task = createMockTask({ retryCount: 0 });
      
      // 第一次调度
      const schedule1 = scheduler.scheduleRetry(task);
      expect(schedule1?.retryDelay).toBe(RETRY_DELAYS[0]);

      // 第二次调度（模拟重试次数增加）
      const updatedTask = { ...task, retryCount: 1 };
      const schedule2 = scheduler.scheduleRetry(updatedTask);
      expect(schedule2?.retryDelay).toBe(RETRY_DELAYS[1]);

      // 应该只有一个调度
      expect(scheduler.getAllRetrySchedules().length).toBe(1);
    });
  });

  describe('getRetryDelay', () => {
    it('should return correct delay for each retry count', () => {
      expect(scheduler.getRetryDelay(0)).toBe(5 * 60 * 1000); // 5分钟
      expect(scheduler.getRetryDelay(1)).toBe(15 * 60 * 1000); // 15分钟
      expect(scheduler.getRetryDelay(2)).toBe(30 * 60 * 1000); // 30分钟
    });

    it('should return last delay for retry count beyond defined delays', () => {
      expect(scheduler.getRetryDelay(3)).toBe(30 * 60 * 1000); // 30分钟
      expect(scheduler.getRetryDelay(10)).toBe(30 * 60 * 1000); // 30分钟
    });
  });

  describe('cancelRetry', () => {
    it('should cancel scheduled retry', () => {
      const callback = jest.fn();
      scheduler.setRetryCallback(callback);

      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      // 取消重试
      scheduler.cancelRetry(task.id);

      // 快进时间
      jest.advanceTimersByTime(RETRY_DELAYS[0]);

      // 回调不应该被调用
      expect(callback).not.toHaveBeenCalled();
      expect(scheduler.getRetrySchedule(task.id)).toBeNull();
    });
  });

  describe('getRetrySchedule', () => {
    it('should return retry schedule for scheduled task', () => {
      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      const schedule = scheduler.getRetrySchedule(task.id);
      expect(schedule).not.toBeNull();
      expect(schedule?.taskId).toBe(task.id);
    });

    it('should return null for non-scheduled task', () => {
      const schedule = scheduler.getRetrySchedule('non-existent');
      expect(schedule).toBeNull();
    });
  });

  describe('isScheduled', () => {
    it('should return true for scheduled task', () => {
      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      expect(scheduler.isScheduled(task.id)).toBe(true);
    });

    it('should return false for non-scheduled task', () => {
      expect(scheduler.isScheduled('non-existent')).toBe(false);
    });
  });

  describe('getTimeUntilRetry', () => {
    it('should return correct time until retry', () => {
      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      const timeUntil = scheduler.getTimeUntilRetry(task.id);
      expect(timeUntil).toBeGreaterThan(0);
      expect(timeUntil).toBeLessThanOrEqual(RETRY_DELAYS[0]);
    });

    it('should return null for non-scheduled task', () => {
      const timeUntil = scheduler.getTimeUntilRetry('non-existent');
      expect(timeUntil).toBeNull();
    });

    it('should decrease as time passes', () => {
      const task = createMockTask({ retryCount: 0 });
      scheduler.scheduleRetry(task);

      const timeUntil1 = scheduler.getTimeUntilRetry(task.id);
      
      // 快进1分钟
      jest.advanceTimersByTime(60 * 1000);
      
      const timeUntil2 = scheduler.getTimeUntilRetry(task.id);
      
      expect(timeUntil2).toBeLessThan(timeUntil1!);
    });
  });

  describe('formatRetryDelay', () => {
    it('should format minutes correctly', () => {
      expect(scheduler.formatRetryDelay(5 * 60 * 1000)).toBe('5 minutes');
      expect(scheduler.formatRetryDelay(1 * 60 * 1000)).toBe('1 minute');
      expect(scheduler.formatRetryDelay(15 * 60 * 1000)).toBe('15 minutes');
    });

    it('should format hours correctly', () => {
      expect(scheduler.formatRetryDelay(60 * 60 * 1000)).toBe('1 hour');
      expect(scheduler.formatRetryDelay(120 * 60 * 1000)).toBe('2 hours');
    });
  });

  describe('getRetryStatusText', () => {
    it('should return empty string for non-failed task', () => {
      const task = createMockTask({ status: 'pending' });
      expect(scheduler.getRetryStatusText(task)).toBe('');
    });

    it('should return max retries message when limit reached', () => {
      const task = createMockTask({ status: 'failed', retryCount: 3, maxRetries: 3 });
      expect(scheduler.getRetryStatusText(task)).toBe('Max retries reached');
    });

    it('should return retry countdown for scheduled task', () => {
      const task = createMockTask({ status: 'failed', retryCount: 0 });
      scheduler.scheduleRetry(task);

      const statusText = scheduler.getRetryStatusText(task);
      expect(statusText).toMatch(/Retry in \d+ minutes?/);
    });
  });

  describe('clearAll', () => {
    it('should clear all retry schedules and timers', () => {
      const callback = jest.fn();
      scheduler.setRetryCallback(callback);

      // 调度多个任务
      const task1 = createMockTask({ id: 'task-1', retryCount: 0 });
      const task2 = createMockTask({ id: 'task-2', retryCount: 0 });
      scheduler.scheduleRetry(task1);
      scheduler.scheduleRetry(task2);

      expect(scheduler.getAllRetrySchedules().length).toBe(2);

      // 清理所有
      scheduler.clearAll();

      expect(scheduler.getAllRetrySchedules().length).toBe(0);

      // 快进时间
      jest.advanceTimersByTime(RETRY_DELAYS[0]);

      // 回调不应该被调用
      expect(callback).not.toHaveBeenCalled();
    });
  });

  describe('getAllRetrySchedules', () => {
    it('should return all scheduled retries', () => {
      const task1 = createMockTask({ id: 'task-1', retryCount: 0 });
      const task2 = createMockTask({ id: 'task-2', retryCount: 1 });
      
      scheduler.scheduleRetry(task1);
      scheduler.scheduleRetry(task2);

      const schedules = scheduler.getAllRetrySchedules();
      expect(schedules.length).toBe(2);
      expect(schedules.map(s => s.taskId)).toContain('task-1');
      expect(schedules.map(s => s.taskId)).toContain('task-2');
    });

    it('should return empty array when no retries scheduled', () => {
      const schedules = scheduler.getAllRetrySchedules();
      expect(schedules).toEqual([]);
    });
  });

  describe('integration test', () => {
    it('should handle complete retry workflow', () => {
      const callback = jest.fn();
      scheduler.setRetryCallback(callback);

      // 创建失败的任务
      const task = createMockTask({ 
        id: 'task-1', 
        status: 'failed', 
        retryCount: 0,
        maxRetries: 3,
      });

      // 第一次重试调度 - 5分钟
      const schedule1 = scheduler.scheduleRetry(task);
      expect(schedule1?.retryDelay).toBe(5 * 60 * 1000);
      expect(scheduler.isScheduled(task.id)).toBe(true);

      // 快进5分钟
      jest.advanceTimersByTime(5 * 60 * 1000);
      expect(callback).toHaveBeenCalledWith(task.id);
      expect(scheduler.isScheduled(task.id)).toBe(false);

      // 第二次重试调度 - 15分钟
      callback.mockClear();
      const task2 = { ...task, retryCount: 1 };
      const schedule2 = scheduler.scheduleRetry(task2);
      expect(schedule2?.retryDelay).toBe(15 * 60 * 1000);

      // 快进15分钟
      jest.advanceTimersByTime(15 * 60 * 1000);
      expect(callback).toHaveBeenCalledWith(task.id);

      // 第三次重试调度 - 30分钟
      callback.mockClear();
      const task3 = { ...task, retryCount: 2 };
      const schedule3 = scheduler.scheduleRetry(task3);
      expect(schedule3?.retryDelay).toBe(30 * 60 * 1000);

      // 快进30分钟
      jest.advanceTimersByTime(30 * 60 * 1000);
      expect(callback).toHaveBeenCalledWith(task.id);

      // 达到最大重试次数，不应该再调度
      const task4 = { ...task, retryCount: 3 };
      const schedule4 = scheduler.scheduleRetry(task4);
      expect(schedule4).toBeNull();
    });
  });
});
