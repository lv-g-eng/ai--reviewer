/**
 * AnalysisQueue优先级调整propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 19: task优先级调整重sort
 * 
 * **Validates: Requirements 5.3**
 * 
 * testCoverage:
 * - 对于任何task优先级的手动调整，queueshould立即重新sort
 * 
 * note: testVerifiesTaskScheduler在优先级调整后的重sort行为。
 * use基于property的test来确保优先级调整在所有可能的场景中都能正确触发重sort。
 */

import fc from 'fast-check';
import { TaskScheduler } from '../../utils/taskScheduler';
import { AnalysisTask } from '../AnalysisQueue';

/**
 * customGenerator：generate有效的analyzetask
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
 * customGenerator：generatetask列表
 */
function taskListArbitrary(minLength: number = 0, maxLength: number = 20): fc.Arbitrary<AnalysisTask[]> {
  return fc.array(analysisTaskArbitrary(), { minLength, maxLength });
}

describe('Property 19: task优先级调整重sort', () => {
  describe('优先级调整后立即重sort', () => {
    it('shouldBeAt优先级调整后立即重新sorttaskqueue', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(2, 20),
          fc.integer({ min: 0, max: 19 }),
          fc.integer({ min: 1, max: 10 }),
          (initialTasks, taskIndex, newPriority) => {
            // 确保至少有一itemtask可以调整
            if (initialTasks.length === 0) return;
            
            // 选择一item有效的task索引
            const validIndex = taskIndex % initialTasks.length;
            const taskToAdjust = initialTasks[validIndex];
            
            // 只testpending或failedstatus的task（可以调整优先级）
            if (taskToAdjust.status !== 'pending' && taskToAdjust.status !== 'failed') {
              return;
            }
            
            // 如果新优先级与当前优先级相同，skip
            if (taskToAdjust.priority === newPriority) {
              return;
            }

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // record调整前的task顺序
            const beforeAdjustment = scheduler.sortByPriority(initialTasks);
            const beforeOrder = beforeAdjustment.map(t => t.id);

            // create调整后的task列表
            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // get调整后的task顺序
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterOrder = afterAdjustment.map(t => t.id);

            // verify：task列表should按新的优先级重新sort
            for (let i = 0; i < afterAdjustment.length - 1; i++) {
              const current = afterAdjustment[i];
              const next = afterAdjustment[i + 1];
              
              // 高优先级shouldBeAt前
              if (current.priority !== next.priority) {
                expect(current.priority).toBeGreaterThanOrEqual(next.priority);
              } else {
                // 优先级相同时，早create的shouldBeAt前（FIFO）
                const currentTime = new Date(current.createdAt).getTime();
                const nextTime = new Date(next.createdAt).getTime();
                expect(currentTime).toBeLessThanOrEqual(nextTime);
              }
            }

            // verify：调整后的taskshouldBeAt正确的位置
            const adjustedTaskInAfter = afterAdjustment.find(t => t.id === taskToAdjust.id);
            expect(adjustedTaskInAfter).toBeDefined();
            expect(adjustedTaskInAfter!.priority).toBe(newPriority);

            // verify：如果优先级发生了实质性变化，顺序可能改变
            const priorityChanged = taskToAdjust.priority !== newPriority;
            
            if (priorityChanged) {
              // check是否有task的优先级在调整前后与目标task的相对位置发生变化
              const shouldChangePosition = initialTasks.some(t => {
                if (t.id === taskToAdjust.id) return false;
                
                const beforePriority = taskToAdjust.priority;
                const afterPriority = newPriority;
                
                // 如果目标task的优先级跨越了其他task的优先级，位置should改变
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

    it('shouldBeAt增加优先级后将task向前移动', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 3, max: 10 }),
          fc.integer({ min: 1, max: 8 }),
          (taskCount, initialPriority) => {
            // create一组task，其中一itemtask优先级较低
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? initialPriority : initialPriority + 2, // 第一itemtask优先级较低
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // record调整前的位置
            const beforeAdjustment = scheduler.sortByPriority(tasks);
            const beforePosition = beforeAdjustment.findIndex(t => t.id === 'task-0');

            // 增加第一itemtask的优先级到最高
            const newPriority = initialPriority + 3;
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // get调整后的位置
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterPosition = afterAdjustment.findIndex(t => t.id === 'task-0');

            // verify：taskshould向前移动（位置索引变小）
            expect(afterPosition).toBeLessThan(beforePosition);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt降低优先级后将task向后移动', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 3, max: 10 }),
          fc.integer({ min: 4, max: 10 }), // 确保有足够的空间降低优先级
          (taskCount, initialPriority) => {
            // create一组task，其中一itemtask优先级较高
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? initialPriority : initialPriority - 2, // 第一itemtask优先级较高
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // record调整前的位置
            const beforeAdjustment = scheduler.sortByPriority(tasks);
            const beforePosition = beforeAdjustment.findIndex(t => t.id === 'task-0');

            // 降低第一itemtask的优先级到最低
            const newPriority = Math.max(1, initialPriority - 3);
            
            // 确保新优先级确实比其他task低
            if (newPriority >= initialPriority - 2) {
              return; // skip这itemtest用例，因为优先级没有实质性降低
            }
            
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // get调整后的位置
            const afterAdjustment = scheduler.sortByPriority(adjustedTasks);
            const afterPosition = afterAdjustment.findIndex(t => t.id === 'task-0');

            // verify：taskshould向后移动（位置索引变大）
            expect(afterPosition).toBeGreaterThan(beforePosition);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt优先级调整后保持sort不variable', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(2, 15),
          fc.integer({ min: 0, max: 14 }),
          fc.integer({ min: 1, max: 10 }),
          (initialTasks, taskIndex, newPriority) => {
            // 确保至少有一itemtask可以调整
            if (initialTasks.length === 0) return;
            
            // 选择一item有效的task索引
            const validIndex = taskIndex % initialTasks.length;
            const taskToAdjust = initialTasks[validIndex];
            
            // 只testpendingstatus的task
            if (taskToAdjust.status !== 'pending') {
              return;
            }

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            // create调整后的task列表
            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // get调整后的task顺序
            const sortedTasks = scheduler.sortByPriority(adjustedTasks);

            // verifysort不variable：
            // 1. 高优先级task在前
            // 2. 相同优先级时，早create的在前
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

            // verify：调整后的taskshouldBeAt正确的位置
            const adjustedTaskIndex = sortedTasks.findIndex(t => t.id === taskToAdjust.id);
            expect(adjustedTaskIndex).toBeGreaterThanOrEqual(0);
            
            const adjustedTask = sortedTasks[adjustedTaskIndex];
            expect(adjustedTask.priority).toBe(newPriority);

            // verify：调整后的task前面的所有task优先级should >= 它的优先级
            for (let i = 0; i < adjustedTaskIndex; i++) {
              expect(sortedTasks[i].priority).toBeGreaterThanOrEqual(newPriority);
            }

            // verify：调整后的task后面的所有task优先级should <= 它的优先级
            for (let i = adjustedTaskIndex + 1; i < sortedTasks.length; i++) {
              expect(sortedTasks[i].priority).toBeLessThanOrEqual(newPriority);
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('调度resultupdate', () => {
    it('shouldBeAt优先级调整后update调度result', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 5 }),
          fc.integer({ min: 3, max: 10 }),
          (maxConcurrent, taskCount) => {
            // create一组pendingtask
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

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent });

            // record调整前的调度result
            const beforeSchedule = scheduler.schedule(tasks);
            expect(beforeSchedule).not.toBeNull();

            // 选择一itemtask并调整其优先级
            const taskToAdjust = tasks[0];
            const newPriority = 10; // set为最高优先级

            const adjustedTasks = tasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            // get调整后的调度result
            const afterSchedule = scheduler.schedule(adjustedTasks);
            expect(afterSchedule).not.toBeNull();

            // verify：调度resultshould已update
            expect(afterSchedule).toBeDefined();
            
            // verify：tasksToExecuteshouldcontain最高优先级的task
            if (afterSchedule.tasksToExecute.length > 0) {
              // 调整后的taskshouldBeAt待executequeue的前面（如果有可用槽位）
              const adjustedTaskInQueue = afterSchedule.tasksToExecute.find(
                t => t.id === taskToAdjust.id
              );
              
              if (adjustedTaskInQueue) {
                // 如果调整后的task在待executequeue中，它should是最高优先级的
                expect(adjustedTaskInQueue.priority).toBe(10);
              }
            }

            // verify：调度result的task总数should等于pendingtask数
            const pendingCount = adjustedTasks.filter(t => t.status === 'pending').length;
            const scheduledCount = afterSchedule.tasksToExecute.length + afterSchedule.waitingTasks.length;
            expect(scheduledCount).toBe(pendingCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt优先级调整后正确updatetasksToExecute', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 3 }),
          fc.integer({ min: 5, max: 10 }),
          (maxConcurrent, taskCount) => {
            // create一组pendingtask，第一itemtask优先级最低
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: i === 0 ? 1 : 5, // 第一itemtask优先级最低
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent });

            // record调整前的tasksToExecute
            const beforeSchedule = scheduler.schedule(tasks);
            const beforeTasksToExecute = beforeSchedule.tasksToExecute;
            
            // 第一itemtask不shouldBeAt待executequeue中（因为优先级最低）
            const task0InBefore = beforeTasksToExecute.some(t => t.id === 'task-0');

            // 将第一itemtask的优先级提升到最高
            const newPriority = 10;
            const adjustedTasks = tasks.map(t =>
              t.id === 'task-0' ? { ...t, priority: newPriority } : t
            );

            // get调整后的tasksToExecute
            const afterSchedule = scheduler.schedule(adjustedTasks);
            const afterTasksToExecute = afterSchedule.tasksToExecute;

            // verify：调整后的taskshouldBeAt待executequeue中（如果有可用槽位）
            if (afterTasksToExecute.length > 0) {
              const task0InAfter = afterTasksToExecute.some(t => t.id === 'task-0');
              
              // 如果有可用槽位，优先级最高的taskshouldBeAt待executequeue中
              if (afterTasksToExecute.length <= maxConcurrent) {
                expect(task0InAfter).toBe(true);
              }
              
              // 如果task在待executequeue中，它should是第一item（优先级最高）
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
    it('should正确handle优先级调整到边界value', () => {
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

            // create调度器
            const scheduler = new TaskScheduler({ maxConcurrent: 3 });

            const adjustedTasks = initialTasks.map(t =>
              t.id === taskToAdjust.id ? { ...t, priority: newPriority } : t
            );

            const sortedTasks = scheduler.sortByPriority(adjustedTasks);

            // verify：sort仍然正确
            for (let i = 0; i < sortedTasks.length - 1; i++) {
              const current = sortedTasks[i];
              const next = sortedTasks[i + 1];
              
              if (current.priority !== next.priority) {
                expect(current.priority).toBeGreaterThanOrEqual(next.priority);
              }
            }

            // verify：边界valuetask的位置
            const adjustedTaskIndex = sortedTasks.findIndex(t => t.id === taskToAdjust.id);
            
            if (newPriority === 10) {
              // 最高优先级shouldBeAt最前面（或与其他最高优先级task一起）
              const firstPriority = sortedTasks[0].priority;
              expect(firstPriority).toBe(10);
            } else if (newPriority === 1) {
              // 最低优先级shouldBeAt最后面（或与其他最低优先级task一起）
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
