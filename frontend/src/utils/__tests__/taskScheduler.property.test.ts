/**
 * task调度器propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 18: task优先级调度
 * 
 * **Validates: Requirements 5.1**
 * 
 * testCoverage:
 * - 对于任何taskqueue，高优先级taskshouldBeAt低优先级task之前execute（在资源可用的情况下）
 * 
 * note: testVerifiesTaskScheduler在各种input条件下的调度正确性。
 * use基于property的test来确保调度算法在所有可能的task组合中都能正确工作。
 */

import fc from 'fast-check';
import { TaskScheduler, SchedulerConfig } from '../taskScheduler';
import { AnalysisTask } from '../../pages/AnalysisQueue';

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

/**
 * customGenerator：generate调度器config
 */
function schedulerConfigArbitrary(): fc.Arbitrary<SchedulerConfig> {
  return fc.record({
    maxConcurrent: fc.integer({ min: 1, max: 10 }),
    checkResourceAvailability: fc.option(fc.constant(() => true), { nil: undefined }),
  });
}

describe('Property 18: task优先级调度', () => {
  describe('核心调度property', () => {
    it('should始终按优先级降序return待executetask', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // verify：tasksToExecuteshould按优先级降序排列
            for (let i = 0; i < result.tasksToExecute.length - 1; i++) {
              const current = result.tasksToExecute[i];
              const next = result.tasksToExecute[i + 1];
              
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
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should只调度pendingstatus的task', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // verify：所有tasksToExecute都should是pendingstatus
            for (const task of result.tasksToExecute) {
              expect(task.status).toBe('pending');
            }

            // verify：所有waitingTasks都should是pendingstatus
            for (const task of result.waitingTasks) {
              expect(task.status).toBe('pending');
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should遵守maxConcurrent限制', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // 计算当前run的task数
            const runningCount = tasks.filter(t => t.status === 'running').length;
            
            // verify：tasksToExecute数量不应超过可用槽位
            const availableSlots = Math.max(0, config.maxConcurrent - runningCount);
            expect(result.tasksToExecute.length).toBeLessThanOrEqual(availableSlots);
            
            // verify：runningCountshould正确
            expect(result.runningCount).toBe(runningCount);
            
            // verify：availableSlotsshould正确
            expect(result.availableSlots).toBe(Math.max(0, config.maxConcurrent - runningCount));
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt资源不可用时不调度任何task', () => {
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

            // verify：当资源不可用时，不should调度任何task
            expect(result.tasksToExecute).toHaveLength(0);
            expect(result.availableSlots).toBe(0);
            
            // verify：所有pendingtask都shouldBeAtwaitingTasks中
            const pendingTasks = tasks.filter(t => t.status === 'pending');
            expect(result.waitingTasks.length).toBe(pendingTasks.length);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('优先级调度正确性', () => {
    it('should优先调度高优先级task', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 10 }),
          fc.integer({ min: 5, max: 30 }),
          (maxConcurrent, taskCount) => {
            // create具有不同优先级的task
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: Math.floor(Math.random() * 10) + 1,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(Date.now() + i * 1000), // 确保不同的create时间
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            if (result.tasksToExecute.length > 0) {
              // verify：第一item待executetaskshould是所有pendingtask中优先级最高的
              const pendingTasks = tasks.filter(t => t.status === 'pending');
              const maxPriority = Math.max(...pendingTasks.map(t => t.priority));
              
              expect(result.tasksToExecute[0].priority).toBe(maxPriority);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('shouldBeAt优先级相同时useFIFO顺序', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 2, max: 10 }),
          fc.integer({ min: 3, max: 20 }),
          fc.integer({ min: 1, max: 10 }),
          (maxConcurrent, taskCount, samePriority) => {
            // create具有相同优先级但不同create时间的task
            const now = Date.now();
            const tasks: AnalysisTask[] = Array.from({ length: taskCount }, (_, i) => ({
              id: `task-${i}`,
              name: `Task ${i}`,
              type: 'code_analysis' as const,
              priority: samePriority,
              status: 'pending' as const,
              progress: 0,
              projectId: 'project-1',
              createdAt: new Date(now + i * 1000), // 递增的create时间
              retryCount: 0,
              maxRetries: 3,
            }));

            const scheduler = new TaskScheduler({ maxConcurrent });
            const result = scheduler.schedule(tasks);

            // verify：相同优先级的taskshould按create时间sort
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

    it('shouldBeAt有可用槽位时调度最高优先级的pendingtask', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 5 }),
          fc.integer({ min: 0, max: 3 }),
          fc.integer({ min: 1, max: 10 }),
          (maxConcurrent, runningCount, pendingCount) => {
            // 确保runningtask不超过maxConcurrent
            const actualRunningCount = Math.min(runningCount, maxConcurrent);
            
            // createrunningtask
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

            // creatependingtask
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
            
            // verify：调度的task数should等于min(availableSlots, pendingCount)
            const expectedScheduledCount = Math.min(availableSlots, pendingCount);
            expect(result.tasksToExecute.length).toBe(expectedScheduledCount);
            
            // verify：如果有调度的task，它们should是最高优先级的
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
    it('should正确handle空task列表', () => {
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

    it('should正确handle所有task都在run的情况', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10 }),
          fc.integer({ min: 1, max: 20 }),
          (maxConcurrent, taskCount) => {
            // create所有runningstatus的task
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

    it('should正确handle所有task都已complete的情况', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          fc.integer({ min: 1, max: 20 }),
          (config, taskCount) => {
            // create所有completedstatus的task
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

    it('should正确handlemaxConcurrent为1的情况', () => {
      fc.assert(
        fc.property(
          taskListArbitrary(0, 50),
          (tasks) => {
            const scheduler = new TaskScheduler({ maxConcurrent: 1 });
            const result = scheduler.schedule(tasks);

            // verify：最多只能调度1itemtask
            expect(result.tasksToExecute.length).toBeLessThanOrEqual(1);
            
            // verify：如果有pendingtask且没有runningtask，should调度1item
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

  describe('不variableverify', () => {
    it('tasksToExecuteandwaitingTasks的总数should等于pendingtask数', () => {
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

    it('不should有duplicate的taskID在result中', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(0, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const result = scheduler.schedule(tasks);

            // verifytasksToExecute中没有duplicateID
            const executeIds = result.tasksToExecute.map(t => t.id);
            const uniqueExecuteIds = new Set(executeIds);
            expect(executeIds.length).toBe(uniqueExecuteIds.size);

            // verifywaitingTasks中没有duplicateID
            const waitingIds = result.waitingTasks.map(t => t.id);
            const uniqueWaitingIds = new Set(waitingIds);
            expect(waitingIds.length).toBe(uniqueWaitingIds.size);

            // verifytasksToExecuteandwaitingTasks之间没有duplicateID
            const allIds = [...executeIds, ...waitingIds];
            const uniqueAllIds = new Set(allIds);
            expect(allIds.length).toBe(uniqueAllIds.size);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('sortByPriorityshould不改变原数组', () => {
      fc.assert(
        fc.property(
          schedulerConfigArbitrary(),
          taskListArbitrary(1, 50),
          (config, tasks) => {
            const scheduler = new TaskScheduler(config);
            const originalIds = tasks.map(t => t.id);
            
            scheduler.sortByPriority(tasks);
            
            // verify：原数组的顺序不should改变
            const afterIds = tasks.map(t => t.id);
            expect(afterIds).toEqual(originalIds);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('getNextTaskshouldreturn最高优先级的pendingtask或null', () => {
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

  describe('configupdate', () => {
    it('updateConfigshould正确updateconfig', () => {
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

    it('部分configupdateshould保留未update的value', () => {
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
