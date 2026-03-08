/**
 * 任务调度器属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 18: 任务优先级调度
 * 
 * **Validates: Requirements 5.1**
 * 
 * 测试覆盖:
 * - 对于任何任务队列，高优先级任务应该在低优先级任务之前执行（在资源可用的情况下）
 * 
 * 注意: 此测试验证TaskScheduler在各种输入条件下的调度正确性。
 * 使用基于属性的测试来确保调度算法在所有可能的任务组合中都能正确工作。
 */

import fc from 'fast-check';
import { TaskScheduler, SchedulerConfig } from '../taskScheduler';
import { AnalysisTask } from '../../pages/AnalysisQueue';

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

/**
 * 自定义生成器：生成调度器配置
 */
function schedulerConfigArbitrary(): fc.Arbitrary<SchedulerConfig> {
  return fc.record({
    maxConcurrent: fc.integer({ min: 1, max: 10 }),
    checkResourceAvailability: fc.option(fc.constant(() => true), { nil: undefined }),
  });
}

describe('Property 18: 任务优先级调度', () => {
  describe('核心调度属性', () => {
    it('应该始终按优先级降序返回待执行任务', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 验证：tasksToExecute应该按优先级降序排列
            for (let i = 0; i < result.tasksToExecute.length - 1; i++) {
              const current = result.tasksToExecute[i];
              const next = result.tasksToExecute[i + 1];
              
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
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该只调度pending状态的任务', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 验证：所有tasksToExecute都应该是pending状态
            for (const task of result.tasksToExecute) {
              expect(task.status).toBe('pending');
            }

            // 验证：所有waitingTasks都应该是pending状态
            for (const task of result.waitingTasks) {
              expect(task.status).toBe('pending');
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该遵守maxConcurrent限制', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 计算当前运行的任务数
            const runningCount = tasks.filter(t => t.status === 'running').length;
            
            // 验证：tasksToExecute数量不应超过可用槽位
            const availableSlots = Math.max(0, config.maxConcurrent - runningCount);
            expect(result.tasksToExecute.length).toBeLessThanOrEqual(availableSlots);
            
            // 验证：runningCount应该正确
            expect(result.runningCount).toBe(runningCount);
            
            // 验证：availableSlots应该正确
            expect(result.availableSlots).toBe(Math.max(0, config.maxConcurrent - runningCount));
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在资源不可用时不调度任何任务', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10 }),
          taskListArbitrary(0, 50),
          (maxConcurrent, tasks) => {
            const config: SchedulerConfig = {
              maxConcurrent,
              checkResourceAvailability: () => false, // 资源不可用
            };
            
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 验证：当资源不可用时，不应该调度任何任务
            expect(result.tasksToExecute).toHaveLength(0);
            expect(result.availableSlots).toBe(0);
            
            // 验证：所有pending任务都应该在waitingTasks中
            const pendingTasks = tasks.filter(t => t.status === 'pending');
            expect(result.waitingTasks.length).toBe(pendingTasks.length);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('优先级调度正确性', () => {
    it('应该优先调度高优先级任务', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 10 }),
          fc.integer({ min: 5, max: 30 }),
          (maxConcurrent, taskCount) => {
            // 创建具有不同优先级的任务
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(Date.now() + i * 1000), // 确保不同的创建时间
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            if (result.tasksToExecute.length > 0) {
              // 验证：第一个待执行任务应该是所有pending任务中优先级最高的
              const pendingTasks = tasks.filter(t => t.status === 'pending');
              const maxPriority = Math.max(...pendingTasks.map(t => t.priority));
              
              expect(result.tasksToExecute[0].priority).toBe(maxPriority);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在优先级相同时使用FIFO顺序', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 10 }),
          fc.integer({ min: 3, max: 20 }),
          fc.integer({ min: 1, max: 10 }),
          (maxConcurrent, taskCount, samePriority) => {
            // 创建具有相同优先级但不同创建时间的任务
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: samePriority,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000), // 递增的创建时间
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            // 验证：相同优先级的任务应该按创建时间排序
            for (let i = 0; i < result.tasksToExecute.length - 1; i++) {
              const current = result.tasksToExecute[i];
              const next = result.tasksToExecute[i + 1];
              
              const currentTime = new Date(current.createdAt).getTime();
              const nextTime = new Date(next.createdAt).getTime();
              
              expect(currentTime).toBeLessThanOrEqual(nextTime);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该在有可用槽位时调度最高优先级的pending任务', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 5 }),
          fc.integer({ min: 0, max: 3 }),
          fc.integer({ min: 1, max: 10 }),
          (maxConcurrent, runningCount, pendingCount) => {
            // 确保running任务不超过maxConcurrent
            const actualRunningCount = Math.min(runningCount, maxConcurrent);
            
            // 创建running任务
            const runningTasks: AnalysisTask[] = Array.from({ length: actualRunningCount }, (_, i) => ({
              id: `running-${i}`,
              name: `Running Task ${i}`,
              type: 'code_analysis' as const,
              priority: 5,
              status: 'running' as const,
              progress: 50,
              projectId: 'project-1',
              createdAt: new Date(),
              retryCount: 0,
              maxRetries: 3,
            }));

            // 创建pending任务
            const pendingTasks: AnalysisTask[] = Array.from({ length: pendingCount }, (_, i) => ({
              id: `pending-${i}`,
              name: `Pending Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(Date.now() + i * 1000),
              retryCount: 0,
              maxRetries: 3,
            }));

            const tasks = [...runningTasks, ...pendingTasks];
            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            // 计算可用槽位
            const availableSlots = maxConcurrent - actualRunningCount;
            
            // 验证：调度的任务数应该等于min(availableSlots, pendingCount)
            const expectedScheduledCount = Math.min(availableSlots, pendingCount);
            expect(result.tasksToExecute.length).toBe(expectedScheduledCount);
            
            // 验证：如果有调度的任务，它们应该是最高优先级的
            if (result.tasksToExecute.length > 0 && pendingTasks.length > 0) {
              const sortedPending = [...pendingTasks].sort((a, b) => {
                if (a.priority !== b.priority) {
                  return b.priority - a.priority;
                }
                return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
              });
              
              for (let i = 0; i < result.tasksToExecute.length; i++) {
                expect(result.tasksToExecute[i].id).toBe(sortedPending[i].id);
              }
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('边界条件', () => {
    it('应该正确处理空任务列表', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          (config) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule([]);

            expect(result.tasksToExecute).toHaveLength(0);
            expect(result.waitingTasks).toHaveLength(0);
            expect(result.runningCount).toBe(0);
            expect(result.availableSlots).toBe(config.maxConcurrent);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该正确处理所有任务都在运行的情况', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10 }),
          fc.integer({ min: 1, max: 20 }),
          (maxConcurrent, taskCount) => {
            // 创建所有running状态的任务
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'running' as const,
              progress: 50,
              projectId: 'project-1',
              createdAt: new Date(),
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            expect(result.tasksToExecute).toHaveLength(0);
            expect(result.waitingTasks).toHaveLength(0);
            expect(result.runningCount).toBe(taskCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该正确处理所有任务都已完成的情况', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          fc.integer({ min: 1, max: 20 }),
          (config, taskCount) => {
            // 创建所有completed状态的任务
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'completed' as const,
              progress: 100,
              projectId: 'project-1',
              createdAt: new Date(),
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            expect(result.tasksToExecute).toHaveLength(0);
            expect(result.waitingTasks).toHaveLength(0);
            expect(result.runningCount).toBe(0);
            expect(result.availableSlots).toBe(config.maxConcurrent);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('应该正确处理maxConcurrent为1的情况', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(0, 50),
          (tasks) => {
            const scheduler = new TaskScheduler({ maxConcurrent: 1 });
            const result = scheduler.schedule(tasks);

            // 验证：最多只能调度1个任务
            expect(result.tasksToExecute.length).toBeLessThanOrEqual(1);
            
            // 验证：如果有pending任务且没有running任务，应该调度1个
            const pendingCount = tasks.filter(t => t.status === 'pending').length;
            const runningCount = tasks.filter(t => t.status === 'running').length;
            
            if (pendingCount > 0 && runningCount === 0) {
              expect(result.tasksToExecute.length).toBe(1);
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('不变量验证', () => {
    it('tasksToExecute和waitingTasks的总数应该等于pending任务数', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            const pendingCount = tasks.filter(t => t.status === 'pending').length;
            const totalScheduled = result.tasksToExecute.length + result.waitingTasks.length;
            
            expect(totalScheduled).toBe(pendingCount);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('不应该有重复的任务ID在结果中', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 验证tasksToExecute中没有重复ID
            const executeIds = result.tasksToExecute.map(t => t.id);
            const uniqueExecuteIds = new Set(executeIds);
            expect(executeIds.length).toBe(uniqueExecuteIds.size);

            // 验证waitingTasks中没有重复ID
            const waitingIds = result.waitingTasks.map(t => t.id);
            const uniqueWaitingIds = new Set(waitingIds);
            expect(waitingIds.length).toBe(uniqueWaitingIds.size);

            // 验证tasksToExecute和waitingTasks之间没有重复ID
            const allIds = [...executeIds, ...waitingIds];
            const uniqueAllIds = new Set(allIds);
            expect(allIds.length).toBe(uniqueAllIds.size);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('sortByPriority应该不改变原数组', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(1, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const originalIds = tasks.map(t => t.id);
            
            scheduler.sortByPriority(tasks);
            
            // 验证：原数组的顺序不应该改变
            const afterIds = tasks.map(t => t.id);
            expect(afterIds).toEqual(originalIds);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('getNextTask应该返回最高优先级的pending任务或null', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const nextTask = scheduler.getNextTask(tasks);

            const result = scheduler.schedule(tasks);
            
            if (result.tasksToExecute.length > 0) {
              expect(nextTask).not.toBeNull();
              expect(nextTask!.id).toBe(result.tasksToExecute[0].id);
            } else {
              expect(nextTask).toBeNull();
            }
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('配置更新', () => {
    it('updateConfig应该正确更新配置', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          schedulerConfigArbitrary(),
          (initialConfig, newConfig) => {
            const scheduler = new TaskScheduler(initialConfig);
            
            scheduler.updateConfig(newConfig);
            
            const currentConfig = scheduler.getConfig();
            expect(currentConfig.maxConcurrent).toBe(newConfig.maxConcurrent);
            if (newConfig.checkResourceAvailability) {
              expect(currentConfig.checkResourceAvailability).toBe(newConfig.checkResourceAvailability);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('部分配置更新应该保留未更新的值', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          fc.integer({ min: 1, max: 10 }),
          (initialConfig, newMaxConcurrent) => {
            const scheduler = new TaskScheduler(initialConfig);
            const originalCheckFn = initialConfig.checkResourceAvailability;
            
            scheduler.updateConfig({ maxConcurrent: newMaxConcurrent });
            
            const currentConfig = scheduler.getConfig();
            expect(currentConfig.maxConcurrent).toBe(newMaxConcurrent);
            expect(currentConfig.checkResourceAvailability).toBe(originalCheckFn);
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
