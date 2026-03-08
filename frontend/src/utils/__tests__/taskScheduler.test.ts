/**
 * 任务调度器单元测试
 */

import { TaskScheduler, createTaskScheduler, ScheduleResult } from '../taskScheduler';
import { AnalysisTask } from '../../pages/AnalysisQueue';

/**
 * 创建测试用的任务
 */
function createMockTask(overrides: Partial<AnalysisTask>): AnalysisTask {
  return {
    id: `task-${Math.random()}`,
    name: 'Test Task',
    type: 'code_analysis',
    priority: 5,
    status: 'pending',
    progress: 0,
    projectId: 'project-1',
    createdAt: new Date(),
    retryCount: 0,
    maxRetries: 3,
    ...overrides,
  };
}

describe('TaskScheduler', () => {
  describe('schedule', () => {
    it('should schedule high priority tasks first', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 2 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 3, status: 'pending' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-3', priority: 5, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.tasksToExecute).toHaveLength(2);
      expect(result.tasksToExecute[0].id).toBe('task-2'); // priority 8
      expect(result.tasksToExecute[1].id).toBe('task-3'); // priority 5
      expect(result.waitingTasks).toHaveLength(1);
      expect(result.waitingTasks[0].id).toBe('task-1'); // priority 3
    });

    it('should respect maxConcurrent limit', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 2 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 5, status: 'running' }),
        createMockTask({ id: 'task-2', priority: 5, status: 'running' }),
        createMockTask({ id: 'task-3', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-4', priority: 7, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.runningCount).toBe(2);
      expect(result.availableSlots).toBe(0);
      expect(result.tasksToExecute).toHaveLength(0);
      expect(result.waitingTasks).toHaveLength(2);
    });

    it('should schedule tasks when slots become available', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 5, status: 'running' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-3', priority: 6, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.runningCount).toBe(1);
      expect(result.availableSlots).toBe(2);
      expect(result.tasksToExecute).toHaveLength(2);
      expect(result.tasksToExecute[0].id).toBe('task-2'); // priority 8
      expect(result.tasksToExecute[1].id).toBe('task-3'); // priority 6
    });

    it('should use FIFO for tasks with same priority', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const now = new Date();
      const tasks: AnalysisTask[] = [
        createMockTask({ 
          id: 'task-1', 
          priority: 5, 
          status: 'pending',
          createdAt: new Date(now.getTime() + 2000), // created later
        }),
        createMockTask({ 
          id: 'task-2', 
          priority: 5, 
          status: 'pending',
          createdAt: new Date(now.getTime()), // created first
        }),
        createMockTask({ 
          id: 'task-3', 
          priority: 5, 
          status: 'pending',
          createdAt: new Date(now.getTime() + 1000), // created middle
        }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.tasksToExecute).toHaveLength(3);
      expect(result.tasksToExecute[0].id).toBe('task-2'); // earliest
      expect(result.tasksToExecute[1].id).toBe('task-3'); // middle
      expect(result.tasksToExecute[2].id).toBe('task-1'); // latest
    });

    it('should return empty tasksToExecute when resources unavailable', () => {
      const scheduler = new TaskScheduler({ 
        maxConcurrent: 3,
        checkResourceAvailability: () => false,
      });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-2', priority: 7, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.tasksToExecute).toHaveLength(0);
      expect(result.waitingTasks).toHaveLength(2);
      expect(result.availableSlots).toBe(0);
    });

    it('should handle empty task list', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const result = scheduler.schedule([]);

      expect(result.tasksToExecute).toHaveLength(0);
      expect(result.waitingTasks).toHaveLength(0);
      expect(result.runningCount).toBe(0);
      expect(result.availableSlots).toBe(3);
    });

    it('should only schedule pending tasks', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 8, status: 'completed' }),
        createMockTask({ id: 'task-2', priority: 7, status: 'failed' }),
        createMockTask({ id: 'task-3', priority: 6, status: 'pending' }),
        createMockTask({ id: 'task-4', priority: 5, status: 'cancelled' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.tasksToExecute).toHaveLength(1);
      expect(result.tasksToExecute[0].id).toBe('task-3');
    });
  });

  describe('sortByPriority', () => {
    it('should sort tasks by priority descending', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 3 }),
        createMockTask({ id: 'task-2', priority: 8 }),
        createMockTask({ id: 'task-3', priority: 5 }),
        createMockTask({ id: 'task-4', priority: 10 }),
      ];

      const sorted = scheduler.sortByPriority(tasks);

      expect(sorted[0].priority).toBe(10);
      expect(sorted[1].priority).toBe(8);
      expect(sorted[2].priority).toBe(5);
      expect(sorted[3].priority).toBe(3);
    });

    it('should not mutate original array', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 3 }),
        createMockTask({ id: 'task-2', priority: 8 }),
      ];

      const originalOrder = tasks.map(t => t.id);
      scheduler.sortByPriority(tasks);

      expect(tasks.map(t => t.id)).toEqual(originalOrder);
    });
  });

  describe('getNextTask', () => {
    it('should return highest priority pending task', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 3, status: 'pending' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-3', priority: 5, status: 'running' }),
      ];

      const nextTask = scheduler.getNextTask(tasks);

      expect(nextTask).not.toBeNull();
      expect(nextTask!.id).toBe('task-2');
      expect(nextTask!.priority).toBe(8);
    });

    it('should return null when no tasks can be scheduled', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 1 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 5, status: 'running' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'pending' }),
      ];

      const nextTask = scheduler.getNextTask(tasks);

      expect(nextTask).toBeNull();
    });

    it('should return null when no pending tasks', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 5, status: 'completed' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'failed' }),
      ];

      const nextTask = scheduler.getNextTask(tasks);

      expect(nextTask).toBeNull();
    });
  });

  describe('updateConfig', () => {
    it('should update maxConcurrent', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      
      scheduler.updateConfig({ maxConcurrent: 5 });

      expect(scheduler.getConfig().maxConcurrent).toBe(5);
    });

    it('should update checkResourceAvailability', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 3 });
      const checkFn = () => false;
      
      scheduler.updateConfig({ checkResourceAvailability: checkFn });

      expect(scheduler.getConfig().checkResourceAvailability).toBe(checkFn);
    });

    it('should preserve other config values', () => {
      const checkFn = () => true;
      const scheduler = new TaskScheduler({ 
        maxConcurrent: 3,
        checkResourceAvailability: checkFn,
      });
      
      scheduler.updateConfig({ maxConcurrent: 5 });

      const config = scheduler.getConfig();
      expect(config.maxConcurrent).toBe(5);
      expect(config.checkResourceAvailability).toBe(checkFn);
    });
  });

  describe('createTaskScheduler', () => {
    it('should create scheduler with default maxConcurrent', () => {
      const scheduler = createTaskScheduler();
      
      expect(scheduler.getConfig().maxConcurrent).toBe(3);
    });

    it('should create scheduler with custom maxConcurrent', () => {
      const scheduler = createTaskScheduler(5);
      
      expect(scheduler.getConfig().maxConcurrent).toBe(5);
    });
  });

  describe('complex scheduling scenarios', () => {
    it('should handle mixed priority and status tasks', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 2 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 10, status: 'running' }),
        createMockTask({ id: 'task-2', priority: 9, status: 'pending' }),
        createMockTask({ id: 'task-3', priority: 8, status: 'completed' }),
        createMockTask({ id: 'task-4', priority: 7, status: 'pending' }),
        createMockTask({ id: 'task-5', priority: 6, status: 'failed' }),
        createMockTask({ id: 'task-6', priority: 5, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.runningCount).toBe(1);
      expect(result.availableSlots).toBe(1);
      expect(result.tasksToExecute).toHaveLength(1);
      expect(result.tasksToExecute[0].id).toBe('task-2'); // highest priority pending
      expect(result.waitingTasks).toHaveLength(2);
      expect(result.waitingTasks[0].id).toBe('task-4'); // priority 7
      expect(result.waitingTasks[1].id).toBe('task-6'); // priority 5
    });

    it('should schedule all pending tasks when enough slots', () => {
      const scheduler = new TaskScheduler({ maxConcurrent: 10 });
      
      const tasks: AnalysisTask[] = [
        createMockTask({ id: 'task-1', priority: 5, status: 'pending' }),
        createMockTask({ id: 'task-2', priority: 8, status: 'pending' }),
        createMockTask({ id: 'task-3', priority: 3, status: 'pending' }),
      ];

      const result = scheduler.schedule(tasks);

      expect(result.tasksToExecute).toHaveLength(3);
      expect(result.waitingTasks).toHaveLength(0);
      expect(result.availableSlots).toBe(10);
    });
  });
});
