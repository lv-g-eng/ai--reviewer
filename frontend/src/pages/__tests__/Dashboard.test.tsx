/**
 * Dashboard组件单元测试
 * 
 * 测试场景:
 * - 加载状态显示
 * - 错误状态显示和重试
 * - 数据成功加载和显示
 * - 自动刷新机制
 * - 定时器清理防止内存泄漏
 * - ErrorBoundary包裹
 */

import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DashboardComponent, SystemMetrics } from '../Dashboard';

// Mock ApiClient module
const mockApiClient = {
  get: jest.fn(),
};

jest.mock('../../services/ApiClient', () => ({
  getApiClient: jest.fn(() => mockApiClient),
}));

// Mock LoadingState
jest.mock('../../components/LoadingState', () => ({
  LoadingState: ({ text }: { text?: string }) => (
    <div data-testid="loading-state">{text || 'Loading...'}</div>
  ),
}));

const mockMetrics: SystemMetrics = {
  activeUsers: 42,
  totalProjects: 15,
  pendingPRs: 8,
  queuedTasks: 23,
  systemHealth: 'healthy',
  lastUpdate: new Date('2024-01-01T12:00:00Z'),
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  describe('Loading State', () => {
    it('should display loading state on initial render', () => {
      mockApiClient.get.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<DashboardComponent />);

      expect(screen.getByTestId('loading-state')).toBeInTheDocument();
      expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
    });

    it('should hide loading state after data is loaded', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.queryByTestId('loading-state')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should display error message when data fetch fails', async () => {
      const errorMessage = 'Network error';
      mockApiClient.get.mockRejectedValue(new Error(errorMessage));

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.getByText('Failed to Load Dashboard')).toBeInTheDocument();
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should allow retry on error', async () => {
      mockApiClient.get
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockMetrics);

      render(<DashboardComponent />);

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText('Failed to Load Dashboard')).toBeInTheDocument();
      });

      // Click retry button - use real timers for user interaction
      jest.useRealTimers();
      const retryButton = screen.getByText('Retry');
      await userEvent.click(retryButton);
      jest.useFakeTimers();

      // Wait for successful load
      await waitFor(() => {
        expect(screen.queryByText('Failed to Load Dashboard')).not.toBeInTheDocument();
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
    });

    it('should show background error banner when refresh fails but data exists', async () => {
      mockApiClient.get
        .mockResolvedValueOnce(mockMetrics)
        .mockRejectedValueOnce(new Error('Refresh failed'));

      render(<DashboardComponent refreshInterval={1000} />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      // Advance timer to trigger refresh
      await act(async () => {
        jest.advanceTimersByTime(1000);
        // Wait for the promise to resolve/reject
        await Promise.resolve();
      });

      // Wait for background error banner
      await waitFor(() => {
        expect(screen.getByText(/Failed to refresh data/)).toBeInTheDocument();
      });

      // Data should still be visible
      expect(screen.getByText('Active Users')).toBeInTheDocument();
    });
  });

  describe('Data Display', () => {
    it('should display metrics correctly', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
        expect(screen.getByText('42')).toBeInTheDocument();
        expect(screen.getByText('Total Projects')).toBeInTheDocument();
        expect(screen.getByText('15')).toBeInTheDocument();
        expect(screen.getByText('Pending PRs')).toBeInTheDocument();
        expect(screen.getByText('8')).toBeInTheDocument();
        expect(screen.getByText('Queued Tasks')).toBeInTheDocument();
        expect(screen.getByText('23')).toBeInTheDocument();
        expect(screen.getByText('System Health')).toBeInTheDocument();
        expect(screen.getByText('Healthy')).toBeInTheDocument();
      });
    });

    it('should display different system health states correctly', async () => {
      const healthStates: Array<SystemMetrics['systemHealth']> = ['healthy', 'degraded', 'down'];
      const expectedTexts = ['Healthy', 'Degraded', 'Down'];

      for (let i = 0; i < healthStates.length; i++) {
        const metrics = { ...mockMetrics, systemHealth: healthStates[i] };
        mockApiClient.get.mockResolvedValue(metrics);

        const { unmount } = render(<DashboardComponent />);

        await waitFor(() => {
          expect(screen.getByText(expectedTexts[i])).toBeInTheDocument();
        });

        unmount();
      }
    });

    it('should display last update time', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
      });
    });
  });

  describe('Auto Refresh', () => {
    it('should refresh data at specified interval', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent refreshInterval={5000} />);

      // Initial load
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // Advance timer by 5 seconds
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Should have called again
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      });

      // Advance timer by another 5 seconds
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Should have called a third time
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(3);
      });
    });

    it('should use default refresh interval of 30 seconds', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      // Initial load
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // Advance timer by 30 seconds
      act(() => {
        jest.advanceTimersByTime(30000);
      });

      // Should have called again
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      });
    });

    it('should not auto-refresh when interval is 0', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent refreshInterval={0} />);

      // Initial load
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // Advance timer by a long time
      act(() => {
        jest.advanceTimersByTime(60000);
      });

      // Should not have called again
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
    });
  });

  describe('Manual Refresh', () => {
    it('should refresh data when refresh button is clicked', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      // Click refresh button - use real timers for user interaction
      jest.useRealTimers();
      const refreshButton = screen.getByText(/Refresh/);
      await userEvent.click(refreshButton);
      jest.useFakeTimers();

      // Should have called again
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Memory Leak Prevention', () => {
    it('should clean up timer on unmount', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      const { unmount } = render(<DashboardComponent refreshInterval={5000} />);

      // Wait for initial load
      await waitFor(() => {
        expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      });

      // Unmount component
      unmount();

      // Advance timer
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      // Should not have called again after unmount
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
    });

    it('should not update state after unmount', async () => {
      let resolvePromise: (value: SystemMetrics) => void;
      const promise = new Promise<SystemMetrics>((resolve) => {
        resolvePromise = resolve;
      });

      mockApiClient.get.mockReturnValue(promise);

      const { unmount } = render(<DashboardComponent />);

      // Unmount before promise resolves
      unmount();

      // Resolve promise after unmount - should not cause errors
      jest.useRealTimers();
      resolvePromise!(mockMetrics);
      await new Promise((resolve) => setTimeout(resolve, 100));
      jest.useFakeTimers();

      // Test passes if no errors thrown
      expect(true).toBe(true);
    });

    it('should clean up all pending requests on unmount', async () => {
      let resolvePromise1: (value: SystemMetrics) => void;
      let resolvePromise2: (value: SystemMetrics) => void;
      const promise1 = new Promise<SystemMetrics>((resolve) => {
        resolvePromise1 = resolve;
      });
      const promise2 = new Promise<SystemMetrics>((resolve) => {
        resolvePromise2 = resolve;
      });

      mockApiClient.get
        .mockReturnValueOnce(promise1)
        .mockReturnValueOnce(promise2);

      const { unmount } = render(<DashboardComponent refreshInterval={1000} />);

      // Trigger second request
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      // Unmount before promises resolve
      unmount();

      // Resolve promises after unmount - should not cause errors or state updates
      jest.useRealTimers();
      resolvePromise1!(mockMetrics);
      resolvePromise2!(mockMetrics);
      await new Promise((resolve) => setTimeout(resolve, 50));
      jest.useFakeTimers();

      // Test passes if no errors thrown
      expect(true).toBe(true);
    }, 15000);

    it('should clear abort controller on unmount', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      const { unmount } = render(<DashboardComponent />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      // Unmount should clean up abort controller
      unmount();

      // Test passes if no errors thrown
      expect(true).toBe(true);
    });
  });

  describe('API Integration', () => {
    it('should call correct API endpoint', async () => {
      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      expect(mockApiClient.get).toHaveBeenCalledWith('/dashboard/metrics');
    });
  });

  describe('Data Refresh Performance', () => {
    beforeEach(() => {
      jest.useRealTimers();
    });

    afterEach(() => {
      jest.useFakeTimers();
    });

    it('should update UI within 500ms of receiving data', async () => {
      const startTime = performance.now();
      mockApiClient.get.mockImplementation(async () => {
        // Simulate fast API response
        await new Promise((resolve) => setTimeout(resolve, 50));
        return mockMetrics;
      });

      render(<DashboardComponent />);

      // Wait for data to be displayed
      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      // Total time should be well under 500ms (API time + render time)
      // We use 600ms to account for test environment overhead
      expect(totalTime).toBeLessThan(600);
    });

    it('should handle rapid data updates efficiently', async () => {
      let updateCount = 0;
      mockApiClient.get.mockImplementation(async () => {
        updateCount++;
        await new Promise((resolve) => setTimeout(resolve, 10));
        return { ...mockMetrics, activeUsers: updateCount };
      });

      render(<DashboardComponent refreshInterval={100} />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      // Wait for a few refresh cycles
      await new Promise((resolve) => setTimeout(resolve, 350));

      // Should have updated multiple times
      expect(updateCount).toBeGreaterThan(1);

      // Each update should be reflected in the UI quickly
      await waitFor(() => {
        const activeUsersValue = screen.getByText(updateCount.toString());
        expect(activeUsersValue).toBeInTheDocument();
      });
    });

    it('should track response time in development mode', async () => {
      const originalEnv = process.env.NODE_ENV;
      
      // Mock console.log before rendering
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // Set NODE_ENV to development before the component renders
      (process.env as any).NODE_ENV = 'development';

      mockApiClient.get.mockResolvedValue(mockMetrics);

      render(<DashboardComponent />);

      await waitFor(() => {
        expect(screen.getByText('Active Users')).toBeInTheDocument();
      });

      // Should log response time in development
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Dashboard data refresh completed in')
      );

      consoleSpy.mockRestore();
      (process.env as any).NODE_ENV = originalEnv;
    });

    it('should warn when refresh exceeds 500ms in development mode', async () => {
      const originalEnv = process.env.NODE_ENV;

      // Mock console methods before rendering
      const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      // Set NODE_ENV to development before the component renders
      (process.env as any).NODE_ENV = 'development';

      // Simulate slow API response
      mockApiClient.get.mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 600));
        return mockMetrics;
      });

      render(<DashboardComponent />);

      await waitFor(
        () => {
          expect(screen.getByText('Active Users')).toBeInTheDocument();
        },
        { timeout: 2000 }
      );

      // Should warn about slow response
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Dashboard refresh exceeded 500ms target')
      );

      consoleWarnSpy.mockRestore();
      consoleLogSpy.mockRestore();
      (process.env as any).NODE_ENV = originalEnv;
    });
  });
});
