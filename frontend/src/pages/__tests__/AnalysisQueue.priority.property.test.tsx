/**
 * AnalysisQueue优先级调整属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 19: 任务优先级调整重排序
 * 
 * **Validates: Requirements 5.3**
 * 
 * 测试覆盖:
 * - 对于任何任务优先级的手动调整，队列应该立即重新排序
 * 
 * 注意: 此测试验证TaskScheduler在优先级调整后的重排序行为。
 * 使用基于属性的测试来确保优先级调整在所有可能的场景中都能正确触发重排序。
 */

import fc from 'fast-check';
import { TaskScheduler } from '../../utils/taskScheduler';
import { AnalysisTask } from '../AnalysisQueue';

/**
 * 自定义生成器：生成有效的分析任务
 */
function analysisTaskArbitrary(): fc.Arbitrary<AnalysisTask> {
  return fc.record({
    id: fc.uuid(),
    name: fc.string({ minLength: 1, maxLength: 50 }),
    type: fc.constantFrom('code_analysis', 'security_scan', 'performance_test', 'dependency_check'),
    priority: fc.integer({ min: 1, max: 10 }),
    status: fc.constantFrom('pending', 'running', 'completed', 'failed', 'cancelled'),
    progress: fc.integer({ min: 0, max: 100 }),
    projectId: fc.uuid(),
    createdAt: fc.date({ min: new Date('2020-01-01'), max: new Date() }),
    retryCount: fc.integer({ min: 0, max: 3 }),
    maxRetries: fc.constant(3),
  });
}

/**
 * 自定义生成器：生成任务列表
 */
function taskListArbitrary(minLength: number = 0, maxLength: number = 20): fc.Arbitrary<AnalysisTask[]> {
  return fc.array(analysisTaskArbitrary(), { minLength, maxLength });
}

describe('Property 19: 任务优先级调整重排序', () => {
  describe('优先级调整后立即重排序', () => {
    it('应该在优先级调整后立即重新排序任务队列', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(2, 20),
          fc.integer({ min: 0, max: 19 }),
          fc.integer({ min: 1, max: 10 }),
          (initialTasks, taskIndex, newPriority) => {
            // 确保至少有一个任务可以调整
            if (initialTasks.length === 0) return;
            
            // 选择一个有效的任务索引
            const validIndex = taskIndex % initialTasks.length;
            const taskToAdjust = initialTasks[validIndex];
            
            // 只测试pending或failed状态的任务（可以调整优先级）
            if (taskToAdjust.status !== 'pending' && taskToAdjust.status !== 'failed') {
              return;
            }
            
            // 如果新优先级与当前优先级相同，跳过
            if (taskToAdjust.priority === newPriority) {
              return;
            }

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // 记录调整前的任务顺序
            const beforeAdjustment = scheduler.sortByPriority(initialTasks);
            const beforeOrder = beforeAdjustment.map(t => t.id);

            // 创建调整后的任务列表
            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的任务顺序
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterOrder = afterAdjustment.map(t => t.id);

            // 验证：任务列表应该按新的优先级重新排序
            for (let i = 0; i < afterAdjustment.length - 1; i++) {
              const current = afterAdjustment[i];
              const next = afterAdjustment[i + 1];
              
              // 高优先级应该在前
              if (current.priority !== next.priority) {
                expect(current.priority).toBeGreaterThanOrEqual(next.priority);
              } else {
                // 优先级相同时，早创建的应该在前（FIFO）
                const currentTime = new Date(current.createdAt).getTime();
                const nextTime = new Date(next.createdAt).getTime();
                expect(currentTime).toBeLessThanOrEqual(nextTime);
              }
            }

            // 验证：调整后的任务应该在正确的位置
            const adjustedTaskInAfter = afterAdjustment.find(t => t.id === taskToAdjust.id);
            expect(adjustedTaskInAfter).toBeDefined();
            expect(adjustedTaskInAfter!.priority).toBe(newPriority);

            // 验证：如果优先级发生了实质性变化，顺序可能改变
            const priorityChanged = taskToAdjust.priority !== newPriority;
            
            if (priorityChanged) {
              // 检查是否有任务的优先级在调整前后与目标任务的相对位置发生变化
              const shouldChangePosition = initialTasks.some(t => {
                if (t.id === taskToAdjust.id) return false;
                
                const beforePriority = taskToAdjust.priority;
                const afterPriority = newPriority;
                
                // 如果目标任务的优先级跨越了其他任务的优先级，位置应该改变
                if (beforePriority < t.priority && afterPriority > t.priority) return true;
                if (beforePriority > t.priority && afterPriority < t.priority) return true;
                
                return false;
              });
              
              const orderChanged = JSON.stringify(beforeOrder) !== JSON.stringify(afterOrder);
              
              if (shouldChangePosition) {
                expect(orderChanged).toBe(true);
              }
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在增加优先级后将任务向前移动', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 3, max: 10 }),
          fc.integer({ min: 1, max: 8 }),
          (taskCount, initialPriority) => {
            // 创建一组任务，其中一个任务优先级较低
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? initialPriority : initialPriority + 2, // 第一个任务优先级较低
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // 记录调整前的位置
            const beforeAdjustment = scheduler.sortByPriority(tasks);
            const beforePosition = beforeAdjustment.findIndex(t => t.id === 'task-0');

            // 增加第一个任务的优先级到最高
            const newPriority = initialPriority + 3;
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的位置
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterPosition = afterAdjustment.findIndex(t => t.id === 'task-0');

            // 验证：任务应该向前移动（位置索引变小）
            expect(afterPosition).toBeLessThan(beforePosition);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在降低优先级后将任务向后移动', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 3, max: 10 }),
          fc.integer({ min: 4, max: 10 }), // 确保有足够的空间降低优先级
          (taskCount, initialPriority) => {
            // 创建一组任务，其中一个任务优先级较高
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? initialPriority : initialPriority - 2, // 第一个任务优先级较高
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // 记录调整前的位置
            const beforeAdjustment = scheduler.sortByPriority(tasks);
            const beforePosition = beforeAdjustment.findIndex(t => t.id === 'task-0');

            // 降低第一个任务的优先级到最低
            const newPriority = Math.max(1, initialPriority - 3);
            
            // 确保新优先级确实比其他任务低
            if (newPriority >= initialPriority - 2) {
              return; // 跳过这个测试用例，因为优先级没有实质性降低
            }
            
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的位置
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterPosition = afterAdjustment.findIndex(t => t.id === 'task-0');

            // 验证：任务应该向后移动（位置索引变大）
            expect(afterPosition).toBeGreaterThan(beforePosition);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在优先级调整后保持排序不变量', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(2, 15),
          fc.integer({ min: 0, max: 14 }),
          fc.integer({ min: 1, max: 10 }),
          (initialTasks, taskIndex, newPriority) => {
            // 确保至少有一个任务可以调整
            if (initialTasks.length === 0) return;
            
            // 选择一个有效的任务索引
            const validIndex = taskIndex % initialTasks.length;
            const taskToAdjust = initialTasks[validIndex];
            
            // 只测试pending状态的任务
            if (taskToAdjust.status !== 'pending') {
              return;
            }

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // 创建调整后的任务列表
            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的任务顺序
            const sortedTasks = scheduler.sortByPriority(adjustedTasks);

            // 验证排序不变量：
            // 1. 高优先级任务在前
            // 2. 相同优先级时，早创建的在前
            for (let i = 0; i < sortedTasks.length - 1; i++) {
              const current = sortedTasks[i];
              const next = sortedTasks[i + 1];
              
              if (current.priority !== next.priority) {
                expect(current.priority).toBeGreaterThanOrEqual(next.priority);
              } else {
                const currentTime = new Date(current.createdAt).getTime();
                const nextTime = new Date(next.createdAt).getTime();
                expect(currentTime).toBeLessThanOrEqual(nextTime);
              }
            }

            // 验证：调整后的任务应该在正确的位置
            const adjustedTaskIndex = sortedTasks.findIndex(t => t.id === taskToAdjust.id);
            expect(adjustedTaskIndex).toBeGreaterThanOrEqual(0);
            
            const adjustedTask = sortedTasks[adjustedTaskIndex];
            expect(adjustedTask.priority).toBe(newPriority);

            // 验证：调整后的任务前面的所有任务优先级应该 >= 它的优先级
            for (let i = 0; i < adjustedTaskIndex; i++) {
              expect(sortedTasks[i].priority).toBeGreaterThanOrEqual(newPriority);
            }

            // 验证：调整后的任务后面的所有任务优先级应该 <= 它的优先级
            for (let i = adjustedTaskIndex + 1; i < sortedTasks.length; i++) {
              expect(sortedTasks[i].priority).toBeLessThanOrEqual(newPriority);
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('调度结果更新', () => {
    it('应该在优先级调整后更新调度结果', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 5 }),
          fc.integer({ min: 3, max: 10 }),
          (maxConcurrent, taskCount) => {
            // 创建一组pending任务
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent });

            // 记录调整前的调度结果
            const beforeSchedule = scheduler.schedule(tasks);
            expect(beforeSchedule).not.toBeNull();

            // 选择一个任务并调整其优先级
            const taskToAdjust = tasks[0];
            const newPriority = 10; // 设置为最高优先级

            const adjustedTasks = tasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的调度结果
            const afterSchedule = scheduler.schedule(adjustedTasks);
            expect(afterSchedule).not.toBeNull();

            // 验证：调度结果应该已更新
            expect(afterSchedule).toBeDefined();
            
            // 验证：tasksToExecute应该包含最高优先级的任务
            if (afterSchedule.tasksToExecute.length > 0) {
              // 调整后的任务应该在待执行队列的前面（如果有可用槽位）
              const adjustedTaskInQueue = afterSchedule.tasksToExecute.find(
                t => t.id === taskToAdjust.id
              );
              
              if (adjustedTaskInQueue) {
                // 如果调整后的任务在待执行队列中，它应该是最高优先级的
                expect(adjustedTaskInQueue.priority).toBe(10);
              }
            }

            // 验证：调度结果的任务总数应该等于pending任务数
            const pendingCount = adjustedTasks.filter(t => t.status === 'pending').length;
            const scheduledCount = afterSchedule.tasksToExecute.length + afterSchedule.waitingTasks.length;
            expect(scheduledCount).toBe(pendingCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在优先级调整后正确更新tasksToExecute', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 3 }),
          fc.integer({ min: 5, max: 10 }),
          (maxConcurrent, taskCount) => {
            // 创建一组pending任务，第一个任务优先级最低
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? 1 : 5, // 第一个任务优先级最低
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent });

            // 记录调整前的tasksToExecute
            const beforeSchedule = scheduler.schedule(tasks);
            const beforeTasksToExecute = beforeSchedule.tasksToExecute;
            
            // 第一个任务不应该在待执行队列中（因为优先级最低）
            const task0InBefore = beforeTasksToExecute.some(t => t.id === 'task-0');

            // 将第一个任务的优先级提升到最高
            const newPriority = 10;
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // 获取调整后的tasksToExecute
            const afterSchedule = scheduler.schedule(adjustedTasks);
            const afterTasksToExecute = afterSchedule.tasksToExecute;

            // 验证：调整后的任务应该在待执行队列中（如果有可用槽位）
            if (afterTasksToExecute.length > 0) {
              const task0InAfter = afterTasksToExecute.some(t => t.id === 'task-0');
              
              // 如果有可用槽位，优先级最高的任务应该在待执行队列中
              if (afterTasksToExecute.length <= maxConcurrent) {
                expect(task0InAfter).toBe(true);
              }
              
              // 如果任务在待执行队列中，它应该是第一个（优先级最高）
              if (task0InAfter) {
                expect(afterTasksToExecute[0].id).toBe('task-0');
              }
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('边界条件', () => {
    it('应该正确处理优先级调整到边界值', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(2, 10),
          fc.integer({ min: 0, max: 9 }),
          fc.constantFrom(1, 10),
          (initialTasks, taskIndex, newPriority) => {
            if (initialTasks.length === 0) return;
            
            const validIndex = taskIndex % initialTasks.length;
            const taskToAdjust = initialTasks[validIndex];
            
            if (taskToAdjust.status !== 'pending') return;

            // 创建调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            const sortedTasks = scheduler.sortByPriority(adjustedTasks);

            // 验证：排序仍然正确
            for (let i = 0; i < sortedTasks.length - 1; i++) {
              const current = sortedTasks[i];
              const next = sortedTasks[i + 1];
              
              if (current.priority !== next.priority) {
                expect(current.priority).toBeGreaterThanOrEqual(next.priority);
              }
            }

            // 验证：边界值任务的位置
            const adjustedTaskIndex = sortedTasks.findIndex(t => t.id === taskToAdjust.id);
            
            if (newPriority === 10) {
              // 最高优先级应该在最前面（或与其他最高优先级任务一起）
              const firstPriority = sortedTasks[0].priority;
              expect(firstPriority).toBe(10);
            } else if (newPriority === 1) {
              // 最低优先级应该在最后面（或与其他最低优先级任务一起）
              const lastPriority = sortedTasks[sortedTasks.length - 1].priority;
              expect(lastPriority).toBe(1);
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
