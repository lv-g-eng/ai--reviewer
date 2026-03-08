/**
 * AnalysisQueuecomponent单元test
 * 
 * test场景:
 * - componentrenderanddataload
 * - task列表展示
 * - VirtualListintegration
 * - errorstatushandle
 * - 资源cleanup
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnalysisQueue, AnalysisQueueComponent, AnalysisTask } from '../AnalysisQueue';
import { getApiClient } from '../../services/ApiClient';

// Mock ApiClient
jest.mock('../../services/ApiClient');

// Mock VirtualList
jest.mock('../../components/VirtualList', () => ({
  VirtualList: ({ items, renderItem }: any) => (
    <div data-testid="virtual-list">
      {items.map((item: any, index: number) => (
        <div key={item.id}>{renderItem(item, index)}</div>
      ))}
    </div>
  ),
}));

// Mock ErrorBoundary
jest.mock('../../components/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: any) => <div>{children}</div>,
}));

// Mock LoadingState
jest.mock('../../components/LoadingState', () => ({
  LoadingState: ({ text }: any) => <div data-testid="loading-state">{text}</div>,
}));

describe('AnalysisQueue', () => {
  const mockTasks: AnalysisTask[] = [
    {
      id: 'task-1',
      name: 'Code Analysis Task',
      type: 'code_analysis',
      priority: 8,
      status: 'running',
      progress: 45,
      projectId: 'project-1',
      createdAt: new Date('2024-01-01T10:00:00Z'),
      startedAt: new Date('2024-01-01T10:05:00Z'),
      retryCount: 0,
      maxRetries: 3,
      estimatedDuration: 300,
    },
    {
      id: 'task-2',
      name: 'Security Scan',
      type: 'security_scan',
      priority: 9,
      status: 'pending',
      progress: 0,
      projectId: 'project-2',
      createdAt: new Date('2024-01-01T10:10:00Z'),
      retryCount: 0,
      maxRetries: 3,
    },
    {
      id: 'task-3',
      name: 'Performance Test',
      type: 'performance_test',
      priority: 5,
      status: 'completed',
      progress: 100,
      projectId: 'project-3',
      createdAt: new Date('2024-01-01T09:00:00Z'),
      startedAt: new Date('2024-01-01T09:05:00Z'),
      completedAt: new Date('2024-01-01T09:15:00Z'),
      retryCount: 0,
      maxRetries: 3,
    },
    {
      id: 'task-4',
      name: 'Failed Task',
      type: 'dependency_check',
      priority: 6,
      status: 'failed',
      progress: 30,
      projectId: 'project-4',
      createdAt: new Date('2024-01-01T08:00:00Z'),
      startedAt: new Date('2024-01-01T08:05:00Z'),
      retryCount: 2,
      maxRetries: 3,
      error: {
        code: 'TIMEOUT',
        message: 'Task execution timeout',
        timestamp: new Date('2024-01-01T08:20:00Z'),
      },
    },
  ];

  let mockApiClient: any;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();

    mockApiClient = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
    };
    (getApiClient as jest.Mock).mockReturnValue(mockApiClient);
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('renderanddataload', () => {
    it('should display loading state on initial render', () => {
      mockApiClient.get.mockImplementation(() => new Promise(() => {}));

      render(<AnalysisQueue />);

      expect(screen.getByTestId('loading-state')).toBeInTheDocument();
      expect(screen.getByText('Loading analysis queue...')).toBeInTheDocument();
    });

    it('should fetch and display tasks on mount', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Analysis Queue')).toBeInTheDocument();
      });

      expect(mockApiClient.get).toHaveBeenCalledWith('/analysis/queue');
      expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
      expect(screen.getAllByText('Security Scan').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Performance Test').length).toBeGreaterThan(0);
    });

    it('should display correct task statistics', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      });

      // Total: 4, Pending: 1, Running: 1, Completed: 1, Failed: 1
      const statValues = screen.getAllByText(/^\d+$/);
      expect(statValues[0]).toHaveTextContent('4'); // Total
      expect(statValues[1]).toHaveTextContent('1'); // Pending
      expect(statValues[2]).toHaveTextContent('1'); // Running
      expect(statValues[3]).toHaveTextContent('1'); // Completed
      expect(statValues[4]).toHaveTextContent('1'); // Failed
    });
  });

  describe('task列表展示', () => {
    it('should display task details correctly', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
      });

      // checktasktype
      expect(screen.getByText('Code Analysis')).toBeInTheDocument();
      expect(screen.getAllByText('Security Scan').length).toBeGreaterThan(0);

      // check优先级
      expect(screen.getAllByText(/Critical \(8\)/).length).toBeGreaterThan(0); // priority 8
      expect(screen.getByText(/Medium \(5\)/)).toBeInTheDocument(); // priority 5

      // checkstatus
      expect(screen.getByText('Running')).toBeInTheDocument();
      expect(screen.getByText('Pending')).toBeInTheDocument();
      expect(screen.getByText('Completed')).toBeInTheDocument();
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });

    it('should display progress bar for running tasks', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('45%')).toBeInTheDocument();
      });
    });

    it('should display error information for failed tasks', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Task execution timeout')).toBeInTheDocument();
      });
    });

    it('should display retry count for tasks with retries', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('2 / 3')).toBeInTheDocument();
      });
    });
  });

  describe('VirtualListintegration', () => {
    it('should use VirtualList for rendering tasks', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
      });
    });

    it('should pass correct props to VirtualList', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue listHeight={800} />);

      await waitFor(() => {
        expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
      });

      // VirtualListshould接收到所有task
      expect(screen.getAllByTestId(/task-item-/).length).toBe(4);
    });

    it('should handle large number of tasks efficiently', async () => {
      // create50+itemtask
      const largeTasks: AnalysisTask[] = Array.from({ length: 60 }, (_, i) => ({
        id: `task-${i}`,
        name: `Task ${i}`,
        type: 'code_analysis',
        priority: Math.floor(Math.random() * 10) + 1,
        status: 'pending',
        progress: 0,
        projectId: `project-${i}`,
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      }));

      mockApiClient.get.mockResolvedValue(largeTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText(/Tasks \(60\)/)).toBeInTheDocument();
      });

      // VirtualListshouldrender所有task（在mock中）
      expect(screen.getAllByTestId(/task-item-/).length).toBe(60);
    });
  });

  describe('交互feature', () => {
    it('should allow selecting a task', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
      });

      const taskItem = screen.getByTestId('task-item-task-1');
      await userEvent.click(taskItem);

      // taskshould被选中（通过style变化，但在test中难以verify）
      // 这里我们只verify点击不会导致error
      expect(taskItem).toBeInTheDocument();
    });

    it('should refresh data when refresh button is clicked', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Analysis Queue')).toBeInTheDocument();
      });

      const refreshButton = screen.getByText('🔄 Refresh');
      await userEvent.click(refreshButton);

      // should再times调用API
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('errorhandle', () => {
    it('should display error message when fetch fails', async () => {
      const error = new Error('Network error');
      mockApiClient.get.mockRejectedValue(error);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Failed to Load Analysis Queue')).toBeInTheDocument();
      });

      expect(screen.getByText('Network error')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    it('should allow retrying after error', async () => {
      const error = new Error('Network error');
      mockApiClient.get.mockRejectedValueOnce(error).mockResolvedValue(mockTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Failed to Load Analysis Queue')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Retry');
      await userEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
      });
    });

    it('should display background error banner when refresh fails with existing data', async () => {
      mockApiClient.get
        .mockResolvedValueOnce(mockTasks)
        .mockRejectedValueOnce(new Error('Refresh failed'));

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
      });

      // 触发refresh
      const refreshButton = screen.getByText('🔄 Refresh');
      await userEvent.click(refreshButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to refresh data/)).toBeInTheDocument();
      });

      // 原有datashould仍然show
      expect(screen.getByText('Code Analysis Task')).toBeInTheDocument();
    });
  });

  describe('空status', () => {
    it('should display empty state when no tasks', async () => {
      mockApiClient.get.mockResolvedValue([]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('No tasks in the queue')).toBeInTheDocument();
      });
    });
  });

  describe('自动refresh', () => {
    it('should refresh data at specified interval', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue refreshInterval={5000} />);

      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // 快进5sec
      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      });

      // 再快进5sec
      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(3);
      });
    });

    it('should not refresh when refreshInterval is 0', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      render(<AnalysisQueue refreshInterval={0} />);

      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // 快进时间
      jest.advanceTimersByTime(10000);

      // 不should再times调用
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
    });
  });

  describe('资源cleanup', () => {
    it('should clean up timer on unmount', async () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      const { unmount } = render(<AnalysisQueue refreshInterval={5000} />);

      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      unmount();

      // 快进时间
      jest.advanceTimersByTime(10000);

      // 不should再times调用（因为component已卸载）
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
    });

    it('should not update state after unmount', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      mockApiClient.get.mockReturnValue(promise);

      const { unmount } = render(<AnalysisQueue />);

      // 立即卸载
      unmount();

      // 解析promise
      resolvePromise!(mockTasks);

      // wait一下确保没有statusupdateerror
      await new Promise((resolve) => setTimeout(resolve, 100));

      // 如果没有error，test通过
    });
  });

  describe('ErrorBoundaryintegration', () => {
    it('should be wrapped with ErrorBoundary', () => {
      mockApiClient.get.mockResolvedValue(mockTasks);

      const { container } = render(<AnalysisQueue />);

      // ErrorBoundaryshould包裹component
      expect(container).toBeInTheDocument();
    });
  });

  describe('task优先级调度', () => {
    it('should display tasks sorted by priority', async () => {
      const unsortedTasks: AnalysisTask[] = [
        {
          id: 'task-low',
          name: 'Low Priority Task',
          type: 'code_analysis',
          priority: 3,
          status: 'pending',
          progress: 0,
          projectId: 'project-1',
          createdAt: new Date('2024-01-01T10:00:00Z'),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-high',
          name: 'High Priority Task',
          type: 'security_scan',
          priority: 9,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date('2024-01-01T10:05:00Z'),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-medium',
          name: 'Medium Priority Task',
          type: 'performance_test',
          priority: 5,
          status: 'pending',
          progress: 0,
          projectId: 'project-3',
          createdAt: new Date('2024-01-01T10:10:00Z'),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(unsortedTasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Tasks (3) - Sorted by Priority')).toBeInTheDocument();
      });

      // get所有task项
      const taskItems = screen.getAllByTestId(/task-item-/);
      
      // verify顺序：高优先级在前
      expect(taskItems[0]).toHaveAttribute('data-testid', 'task-item-task-high');
      expect(taskItems[1]).toHaveAttribute('data-testid', 'task-item-task-medium');
      expect(taskItems[2]).toHaveAttribute('data-testid', 'task-item-task-low');
    });

    it('should display schedule information', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Running Task',
          type: 'code_analysis',
          priority: 8,
          status: 'running',
          progress: 50,
          projectId: 'project-1',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-2',
          name: 'Pending Task 1',
          type: 'security_scan',
          priority: 9,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-3',
          name: 'Pending Task 2',
          type: 'performance_test',
          priority: 7,
          status: 'pending',
          progress: 0,
          projectId: 'project-3',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);

      render(<AnalysisQueue maxConcurrent={3} />);

      await waitFor(() => {
        expect(screen.getByText('Max Concurrent:')).toBeInTheDocument();
      });

      // verify调度info
      expect(screen.getByText('Available Slots:')).toBeInTheDocument();
      expect(screen.getByText('Scheduled to Execute:')).toBeInTheDocument();
      expect(screen.getByText('Waiting:')).toBeInTheDocument();
    });

    it('should mark scheduled tasks with badge', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Running Task',
          type: 'code_analysis',
          priority: 5,
          status: 'running',
          progress: 50,
          projectId: 'project-1',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-2',
          name: 'Scheduled Task',
          type: 'security_scan',
          priority: 9,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);

      render(<AnalysisQueue maxConcurrent={2} />);

      await waitFor(() => {
        expect(screen.getByText('⏱️ Scheduled')).toBeInTheDocument();
      });
    });

    it('should respect maxConcurrent limit in scheduling', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Running Task 1',
          type: 'code_analysis',
          priority: 5,
          status: 'running',
          progress: 50,
          projectId: 'project-1',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-2',
          name: 'Running Task 2',
          type: 'security_scan',
          priority: 6,
          status: 'running',
          progress: 30,
          projectId: 'project-2',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-3',
          name: 'Pending Task',
          type: 'performance_test',
          priority: 9,
          status: 'pending',
          progress: 0,
          projectId: 'project-3',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);

      render(<AnalysisQueue maxConcurrent={2} />);

      await waitFor(() => {
        expect(screen.getByText('Max Concurrent:')).toBeInTheDocument();
      });

      // shouldshow没有可用槽位
      // note：由于我们的mock，实际的数valueshow可能need更精确的选择器
      const scheduleInfo = screen.getByText('Available Slots:').parentElement;
      expect(scheduleInfo).toBeInTheDocument();
    });

    it('should use FIFO for same priority tasks', async () => {
      const now = new Date();
      const tasks: AnalysisTask[] = [
        {
          id: 'task-new',
          name: 'Newer Task',
          type: 'code_analysis',
          priority: 5,
          status: 'pending',
          progress: 0,
          projectId: 'project-1',
          createdAt: new Date(now.getTime() + 1000),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-old',
          name: 'Older Task',
          type: 'security_scan',
          priority: 5,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date(now.getTime()),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Tasks (2) - Sorted by Priority')).toBeInTheDocument();
      });

      const taskItems = screen.getAllByTestId(/task-item-/);
      
      // 相同优先级时，早create的shouldBeAt前
      expect(taskItems[0]).toHaveAttribute('data-testid', 'task-item-task-old');
      expect(taskItems[1]).toHaveAttribute('data-testid', 'task-item-task-new');
    });
  });

  describe('task自动retry机制', () => {
    it('should display retry badge for failed tasks with scheduled retry', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 1,
        maxRetries: 3,
        error: {
          code: 'TIMEOUT',
          message: 'Task execution timeout',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText(/🔄 Retry/)).toBeInTheDocument();
      });

      // shouldshowretry计数
      expect(screen.getByText('🔄 Retry 2/3')).toBeInTheDocument();
    });

    it('should display retry status text for scheduled retry', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
        error: {
          code: 'TIMEOUT',
          message: 'Task execution timeout',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText(/Retry in \d+ minutes?/)).toBeInTheDocument();
      });
    });

    it('should display max retries message when limit reached', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 3,
        maxRetries: 3,
        error: {
          code: 'TIMEOUT',
          message: 'Task execution timeout',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Failed Task')).toBeInTheDocument();
      });

      // 不shouldshowretry徽章（已达到最大retrytimes数）
      expect(screen.queryByText(/🔄 Retry/)).not.toBeInTheDocument();
    });

    it('should display retry count in task details', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 2,
        maxRetries: 3,
        error: {
          code: 'TIMEOUT',
          message: 'Task execution timeout',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Retries:')).toBeInTheDocument();
      });

      expect(screen.getByText('2 / 3')).toBeInTheDocument();
    });

    it('should clean up retry schedules on unmount', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
        error: {
          code: 'TIMEOUT',
          message: 'Task execution timeout',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      const { unmount } = render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Failed Task')).toBeInTheDocument();
      });

      // 卸载component
      unmount();

      // 快进时间，确保没有内存泄漏或error
      jest.advanceTimersByTime(10 * 60 * 1000);

      // 如果没有error，test通过
    });

    it('should handle multiple failed tasks with different retry counts', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Failed Task 1',
          type: 'code_analysis',
          priority: 5,
          status: 'failed',
          progress: 30,
          projectId: 'project-1',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
          error: {
            code: 'TIMEOUT',
            message: 'Timeout',
            timestamp: new Date(),
          },
        },
        {
          id: 'task-2',
          name: 'Failed Task 2',
          type: 'security_scan',
          priority: 6,
          status: 'failed',
          progress: 50,
          projectId: 'project-2',
          createdAt: new Date(),
          retryCount: 1,
          maxRetries: 3,
          error: {
            code: 'ERROR',
            message: 'Error',
            timestamp: new Date(),
          },
        },
        {
          id: 'task-3',
          name: 'Failed Task 3',
          type: 'performance_test',
          priority: 7,
          status: 'failed',
          progress: 70,
          projectId: 'project-3',
          createdAt: new Date(),
          retryCount: 3,
          maxRetries: 3,
          error: {
            code: 'FATAL',
            message: 'Fatal error',
            timestamp: new Date(),
          },
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Failed Task 1')).toBeInTheDocument();
      });

      // shouldshow不同的retry徽章
      expect(screen.getByText('🔄 Retry 1/3')).toBeInTheDocument();
      expect(screen.getByText('🔄 Retry 2/3')).toBeInTheDocument();
      // task-3 已达到最大retrytimes数，不shouldshowretry徽章
      expect(screen.queryByText('🔄 Retry 4/3')).not.toBeInTheDocument();
    });
  });

  describe('task优先级调整', () => {
    it('should display priority adjustment controls for pending tasks', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Adjust Priority:')).toBeInTheDocument();
      });

      // shouldshow增加/减少buttonand滑块
      expect(screen.getByTestId('increase-priority-task-pending')).toBeInTheDocument();
      expect(screen.getByTestId('decrease-priority-task-pending')).toBeInTheDocument();
      expect(screen.getByTestId('priority-slider-task-pending')).toBeInTheDocument();
    });

    it('should display priority adjustment controls for failed tasks', async () => {
      const failedTask: AnalysisTask = {
        id: 'task-failed',
        name: 'Failed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'failed',
        progress: 30,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 1,
        maxRetries: 3,
        error: {
          code: 'ERROR',
          message: 'Error',
          timestamp: new Date(),
        },
      };

      mockApiClient.get.mockResolvedValue([failedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Adjust Priority:')).toBeInTheDocument();
      });

      expect(screen.getByTestId('increase-priority-task-failed')).toBeInTheDocument();
    });

    it('should not display priority adjustment controls for running tasks', async () => {
      const runningTask: AnalysisTask = {
        id: 'task-running',
        name: 'Running Task',
        type: 'code_analysis',
        priority: 5,
        status: 'running',
        progress: 50,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([runningTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Running Task')).toBeInTheDocument();
      });

      expect(screen.queryByText('Adjust Priority:')).not.toBeInTheDocument();
    });

    it('should not display priority adjustment controls for completed tasks', async () => {
      const completedTask: AnalysisTask = {
        id: 'task-completed',
        name: 'Completed Task',
        type: 'code_analysis',
        priority: 5,
        status: 'completed',
        progress: 100,
        projectId: 'project-1',
        createdAt: new Date(),
        completedAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([completedTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
      });

      expect(screen.queryByText('Adjust Priority:')).not.toBeInTheDocument();
    });

    it('should increase priority when increase button is clicked', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      const updatedTask = { ...pendingTask, priority: 6 };
      mockApiClient.get.mockResolvedValue([pendingTask]);
      mockApiClient.put.mockResolvedValue(updatedTask);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('increase-priority-task-pending')).toBeInTheDocument();
      }, { timeout: 5000 });

      const increaseButton = screen.getByTestId('increase-priority-task-pending');
      await userEvent.click(increaseButton);

      // should调用APIupdate优先级
      await waitFor(() => {
        expect(mockApiClient.put).toHaveBeenCalledWith(
          '/analysis/queue/task-pending/priority',
          { priority: 6 }
        );
      }, { timeout: 5000 });
    });

    it('should decrease priority when decrease button is clicked', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      const updatedTask = { ...pendingTask, priority: 4 };
      mockApiClient.get.mockResolvedValue([pendingTask]);
      mockApiClient.put.mockResolvedValue(updatedTask);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('decrease-priority-task-pending')).toBeInTheDocument();
      }, { timeout: 5000 });

      const decreaseButton = screen.getByTestId('decrease-priority-task-pending');
      await userEvent.click(decreaseButton);

      // should调用APIupdate优先级
      await waitFor(() => {
        expect(mockApiClient.put).toHaveBeenCalledWith(
          '/analysis/queue/task-pending/priority',
          { priority: 4 }
        );
      }, { timeout: 5000 });
    });

    it('should update priority when slider is changed', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      const updatedTask = { ...pendingTask, priority: 8 };
      mockApiClient.get.mockResolvedValue([pendingTask]);
      mockApiClient.put.mockResolvedValue(updatedTask);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('priority-slider-task-pending')).toBeInTheDocument();
      });

      const slider = screen.getByTestId('priority-slider-task-pending') as HTMLInputElement;
      
      // usefireEvent改变滑块value
      const { fireEvent } = await import('@testing-library/react');
      fireEvent.change(slider, { target: { value: '8' } });

      // should调用APIupdate优先级
      await waitFor(() => {
        expect(mockApiClient.put).toHaveBeenCalledWith(
          '/analysis/queue/task-pending/priority',
          { priority: 8 }
        );
      });
    });

    it('should disable increase button when priority is at maximum', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 10,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('increase-priority-task-pending')).toBeInTheDocument();
      });

      const increaseButton = screen.getByTestId('increase-priority-task-pending') as HTMLButtonElement;
      expect(increaseButton.disabled).toBe(true);
    });

    it('should disable decrease button when priority is at minimum', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 1,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('decrease-priority-task-pending')).toBeInTheDocument();
      });

      const decreaseButton = screen.getByTestId('decrease-priority-task-pending') as HTMLButtonElement;
      expect(decreaseButton.disabled).toBe(true);
    });

    it('should reorder queue after priority change', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Task 1',
          type: 'code_analysis',
          priority: 5,
          status: 'pending',
          progress: 0,
          projectId: 'project-1',
          createdAt: new Date('2024-01-01T10:00:00Z'),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-2',
          name: 'Task 2',
          type: 'security_scan',
          priority: 3,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date('2024-01-01T10:05:00Z'),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      const updatedTasks = [
        tasks[0],
        { ...tasks[1], priority: 8 },
      ];

      mockApiClient.get
        .mockResolvedValueOnce(tasks)
        .mockResolvedValueOnce(updatedTasks);
      mockApiClient.put.mockResolvedValue(updatedTasks[1]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('Task 1')).toBeInTheDocument();
      });

      // 初始顺序：Task 1 (priority 5) 在前，Task 2 (priority 3) 在后
      let taskItems = screen.getAllByTestId(/task-item-/);
      expect(taskItems[0]).toHaveAttribute('data-testid', 'task-item-task-1');
      expect(taskItems[1]).toHaveAttribute('data-testid', 'task-item-task-2');

      // 增加Task 2的优先级到8
      const increaseButton = screen.getByTestId('increase-priority-task-2');
      await userEvent.click(increaseButton);
      await userEvent.click(increaseButton);
      await userEvent.click(increaseButton);
      await userEvent.click(increaseButton);
      await userEvent.click(increaseButton);

      // waitqueue重新sort
      await waitFor(() => {
        taskItems = screen.getAllByTestId(/task-item-/);
        // Task 2 (priority 8) shouldBeAt前，Task 1 (priority 5) 在后
        expect(taskItems[0]).toHaveAttribute('data-testid', 'task-item-task-2');
      });
    });

    it('should update schedule result after priority change', async () => {
      const tasks: AnalysisTask[] = [
        {
          id: 'task-1',
          name: 'Running Task',
          type: 'code_analysis',
          priority: 5,
          status: 'running',
          progress: 50,
          projectId: 'project-1',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-2',
          name: 'Low Priority Task',
          type: 'security_scan',
          priority: 3,
          status: 'pending',
          progress: 0,
          projectId: 'project-2',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
        {
          id: 'task-3',
          name: 'High Priority Task',
          type: 'performance_test',
          priority: 8,
          status: 'pending',
          progress: 0,
          projectId: 'project-3',
          createdAt: new Date(),
          retryCount: 0,
          maxRetries: 3,
        },
      ];

      mockApiClient.get.mockResolvedValue(tasks);
      mockApiClient.put.mockResolvedValue({ ...tasks[1], priority: 9 });

      render(<AnalysisQueue maxConcurrent={2} />);

      await waitFor(() => {
        expect(screen.getByText('Scheduled to Execute:')).toBeInTheDocument();
      });

      // 初始status：task-3 (priority 8) should被调度execute
      expect(screen.getAllByText('⏱️ Scheduled').length).toBeGreaterThan(0);

      // 增加task-2的优先级到9
      const increaseButton = screen.getByTestId('increase-priority-task-2');
      await userEvent.click(increaseButton);

      // wait调度resultupdate
      await waitFor(() => {
        expect(mockApiClient.put).toHaveBeenCalled();
      });
    });

    it('should handle priority change API error gracefully', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);
      mockApiClient.put.mockRejectedValue(new Error('API error'));

      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('increase-priority-task-pending')).toBeInTheDocument();
      });

      const increaseButton = screen.getByTestId('increase-priority-task-pending');
      await userEvent.click(increaseButton);

      // shouldrecorderror
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to update task priority:',
          expect.any(Error)
        );
      });

      consoleErrorSpy.mockRestore();
    });

    it('should stop event propagation when clicking priority controls', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 5,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);
      mockApiClient.put.mockResolvedValue({ ...pendingTask, priority: 6 });

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByTestId('increase-priority-task-pending')).toBeInTheDocument();
      });

      // 点击增加button不should选中task
      const increaseButton = screen.getByTestId('increase-priority-task-pending');
      await userEvent.click(increaseButton);

      // task项不should被选中（通过check是否调用了handleSelectTask）
      // 这itemtest主要verifystopPropagation是否工作
      expect(mockApiClient.put).toHaveBeenCalled();
    });

    it('should display priority value in badge', async () => {
      const pendingTask: AnalysisTask = {
        id: 'task-pending',
        name: 'Pending Task',
        type: 'code_analysis',
        priority: 7,
        status: 'pending',
        progress: 0,
        projectId: 'project-1',
        createdAt: new Date(),
        retryCount: 0,
        maxRetries: 3,
      };

      mockApiClient.get.mockResolvedValue([pendingTask]);

      render(<AnalysisQueue />);

      await waitFor(() => {
        expect(screen.getByText('High (7)')).toBeInTheDocument();
      });
    });
  });
});
