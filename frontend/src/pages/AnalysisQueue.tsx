/**
 * AnalysisQueue页面组件
 * 
 * 功能:
 * - 展示分析任务队列
 * - 使用VirtualList支持50+任务的高性能渲染
 * - 显示任务状态、进度和优先级
 * - 支持任务优先级调整和手动操作
 * 
 * 验证需求: 5.5
 */

import React, { Component } from 'react';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { LoadingState } from '../components/LoadingState';
import { VirtualList } from '../components/VirtualList';
import { getApiClient } from '../services/ApiClient';
import { TaskScheduler, ScheduleResult } from '../utils/taskScheduler';
import { TaskRetryScheduler, RetrySchedule } from '../utils/taskRetryScheduler';
import '../styles/responsive.css';

export interface AnalysisQueueProps {
  /** 数据刷新间隔（毫秒），默认10秒 */
  refreshInterval?: number;
  /** VirtualList容器高度（像素），默认600 */
  listHeight?: number;
  /** 最大并发任务数，默认3 */
  maxConcurrent?: number;
}

export interface AnalysisTask {
  id: string;
  name: string;
  type: 'code_analysis' | 'security_scan' | 'performance_test' | 'dependency_check';
  priority: number; // 1-10，数字越大优先级越高
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  projectId: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  retryCount: number;
  maxRetries: number;
  estimatedDuration?: number; // 秒
  error?: {
    code: string;
    message: string;
    timestamp: Date;
  };
}

export interface AnalysisQueueState {
  tasks: AnalysisTask[];
  loading: boolean;
  error: Error | null;
  lastUpdate: Date | null;
  selectedTaskId: string | null;
  scheduleResult: ScheduleResult | null;
  retrySchedules: Map<string, RetrySchedule>;
}

/**
 * AnalysisQueue类组件
 * 实现任务队列展示和VirtualList集成
 */
export class AnalysisQueueComponent extends Component<AnalysisQueueProps, AnalysisQueueState> {
  private refreshTimer: NodeJS.Timeout | null = null;
  private mounted = false;
  private abortController: AbortController | null = null;
  private scheduler: TaskScheduler;
  private retryScheduler: TaskRetryScheduler;

  static defaultProps: Partial<AnalysisQueueProps> = {
    refreshInterval: 10000, // 默认10秒
    listHeight: 600,
    maxConcurrent: 3, // 默认最多3个并发任务
  };

  constructor(props: AnalysisQueueProps) {
    super(props);
    this.state = {
      tasks: [],
      loading: true,
      error: null,
      lastUpdate: null,
      selectedTaskId: null,
      scheduleResult: null,
      retrySchedules: new Map(),
    };
    
    // 初始化任务调度器
    this.scheduler = new TaskScheduler({ 
      maxConcurrent: props.maxConcurrent || 3,
    });

    // 初始化重试调度器
    this.retryScheduler = new TaskRetryScheduler();
    this.retryScheduler.setRetryCallback(this.handleTaskRetry);
  }

  /**
   * 组件挂载后开始数据加载
   */
  async componentDidMount(): Promise<void> {
    this.mounted = true;
    
    // 首次加载数据
    await this.fetchTasks();

    // 设置定时刷新
    if (this.props.refreshInterval && this.props.refreshInterval > 0) {
      this.refreshTimer = setInterval(() => {
        this.fetchTasks();
      }, this.props.refreshInterval);
    }
  }

  /**
   * 组件卸载时清理所有资源
   */
  componentWillUnmount(): void {
    this.mounted = false;
    
    // 清理定时器
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }

    // 取消所有进行中的请求
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    // 清理所有重试调度
    this.retryScheduler.clearAll();
  }

  /**
   * 获取任务队列数据
   */
  fetchTasks = async (): Promise<void> => {
    if (!this.mounted) {
      return;
    }

    this.abortController = new AbortController();

    try {
      // 只在首次加载时显示loading状态
      if (this.state.tasks.length === 0) {
        this.setState({ loading: true, error: null });
      }

      const apiClient = getApiClient();
      const tasks = await apiClient.get<AnalysisTask[]>('/analysis/queue');

      if (this.mounted) {
        // 使用调度器计算调度结果
        const scheduleResult = this.scheduler.schedule(tasks);
        
        // 为失败的任务调度重试
        this.scheduleRetriesForFailedTasks(tasks);

        // 获取所有重试调度信息
        const retrySchedules = new Map(
          this.retryScheduler.getAllRetrySchedules().map(s => [s.taskId, s])
        );
        
        this.setState({
          tasks,
          loading: false,
          error: null,
          lastUpdate: new Date(),
          scheduleResult,
          retrySchedules,
        });
      }
    } catch (error) {
      // 如果是取消错误，不更新状态
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }

      if (this.mounted) {
        this.setState({
          loading: false,
          error: error instanceof Error ? error : new Error('Failed to fetch tasks'),
        });
      }
    }
  };

  /**
   * 手动刷新数据
   */
  handleRefresh = (): void => {
    this.fetchTasks();
  };

  /**
   * 选择任务
   */
  handleSelectTask = (taskId: string): void => {
    this.setState({ selectedTaskId: taskId });
  };

  /**
   * 调整任务优先级
   * 验证需求: 5.3
   */
  handlePriorityChange = async (taskId: string, newPriority: number): Promise<void> => {
    try {
      const apiClient = getApiClient();
      
      // 调用API更新任务优先级
      await apiClient.put(`/analysis/queue/${taskId}/priority`, { priority: newPriority });
      
      // 立即更新本地状态以提供即时反馈
      this.setState(prevState => {
        const updatedTasks = prevState.tasks.map(task =>
          task.id === taskId ? { ...task, priority: newPriority } : task
        );
        
        // 重新计算调度结果
        const scheduleResult = this.scheduler.schedule(updatedTasks);
        
        return {
          tasks: updatedTasks,
          scheduleResult,
        };
      });
      
      // 刷新任务列表以确保与服务器同步
      await this.fetchTasks();
    } catch (error) {
      console.error('Failed to update task priority:', error);
      // 可以在这里添加错误提示
    }
  };

  /**
   * 增加任务优先级
   */
  handleIncreasePriority = (taskId: string, currentPriority: number): void => {
    const newPriority = Math.min(10, currentPriority + 1);
    if (newPriority !== currentPriority) {
      this.handlePriorityChange(taskId, newPriority);
    }
  };

  /**
   * 降低任务优先级
   */
  handleDecreasePriority = (taskId: string, currentPriority: number): void => {
    const newPriority = Math.max(1, currentPriority - 1);
    if (newPriority !== currentPriority) {
      this.handlePriorityChange(taskId, newPriority);
    }
  };

  /**
   * 为失败的任务调度重试
   */
  scheduleRetriesForFailedTasks = (tasks: AnalysisTask[]): void => {
    tasks.forEach(task => {
      if (task.status === 'failed' && task.retryCount < task.maxRetries) {
        // 如果任务还没有被调度重试，则调度它
        if (!this.retryScheduler.isScheduled(task.id)) {
          this.retryScheduler.scheduleRetry(task);
        }
      } else if (task.status !== 'failed') {
        // 如果任务不再是失败状态，取消重试调度
        this.retryScheduler.cancelRetry(task.id);
      }
    });
  };

  /**
   * 处理任务重试
   */
  handleTaskRetry = async (taskId: string): Promise<void> => {
    try {
      const apiClient = getApiClient();
      // 调用API重试任务
      await apiClient.post(`/analysis/queue/${taskId}/retry`, {});
      
      // 刷新任务列表
      await this.fetchTasks();
    } catch (error) {
      console.error('Failed to retry task:', error);
    }
  };

  /**
   * 获取按优先级排序的任务列表（用于显示）
   */
  getSortedTasks = (): AnalysisTask[] => {
    return this.scheduler.sortByPriority(this.state.tasks);
  };

  /**
   * 获取任务类型的显示文本
   */
  getTaskTypeText(type: AnalysisTask['type']): string {
    switch (type) {
      case 'code_analysis':
        return 'Code Analysis';
      case 'security_scan':
        return 'Security Scan';
      case 'performance_test':
        return 'Performance Test';
      case 'dependency_check':
        return 'Dependency Check';
      default:
        return 'Unknown';
    }
  }

  /**
   * 获取任务状态的颜色
   */
  getStatusColor(status: AnalysisTask['status']): string {
    switch (status) {
      case 'pending':
        return '#6b7280'; // gray
      case 'running':
        return '#0066cc'; // blue
      case 'completed':
        return '#22c55e'; // green
      case 'failed':
        return '#ef4444'; // red
      case 'cancelled':
        return '#f59e0b'; // amber
      default:
        return '#6b7280';
    }
  }

  /**
   * 获取任务状态的显示文本
   */
  getStatusText(status: AnalysisTask['status']): string {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return 'Unknown';
    }
  }

  /**
   * 获取优先级的显示文本
   */
  getPriorityText(priority: number): string {
    if (priority >= 8) return 'Critical';
    if (priority >= 6) return 'High';
    if (priority >= 4) return 'Medium';
    return 'Low';
  }

  /**
   * 获取优先级的颜色
   */
  getPriorityColor(priority: number): string {
    if (priority >= 8) return '#ef4444'; // red
    if (priority >= 6) return '#f59e0b'; // amber
    if (priority >= 4) return '#0066cc'; // blue
    return '#6b7280'; // gray
  }

  /**
   * 格式化时间
   */
  formatTime(date: Date | undefined): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleString();
  }

  /**
   * 格式化持续时间
   */
  formatDuration(seconds: number | undefined): string {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  }

  /**
   * 计算任务的预计完成时间
   * 验证需求: 5.4
   */
  calculateEstimatedCompletion(task: AnalysisTask): Date | null {
    // 只有运行中的任务才计算预计完成时间
    if (task.status !== 'running') {
      return null;
    }

    // 如果没有开始时间或预计持续时间，无法计算
    if (!task.startedAt || !task.estimatedDuration) {
      return null;
    }

    const startTime = new Date(task.startedAt).getTime();
    const now = Date.now();
    const elapsedSeconds = (now - startTime) / 1000;

    // 如果有进度信息，使用进度计算剩余时间
    if (task.progress > 0 && task.progress < 100) {
      const estimatedTotalSeconds = (elapsedSeconds / task.progress) * 100;
      const remainingSeconds = estimatedTotalSeconds - elapsedSeconds;
      return new Date(now + remainingSeconds * 1000);
    }

    // 否则使用预计持续时间
    const remainingSeconds = task.estimatedDuration - elapsedSeconds;
    if (remainingSeconds > 0) {
      return new Date(now + remainingSeconds * 1000);
    }

    return null;
  }

  /**
   * 格式化预计完成时间
   */
  formatEstimatedCompletion(estimatedCompletion: Date | null): string {
    if (!estimatedCompletion) {
      return 'N/A';
    }

    const now = Date.now();
    const completionTime = estimatedCompletion.getTime();
    const remainingMs = completionTime - now;

    // 如果已经过了预计时间
    if (remainingMs <= 0) {
      return 'Completing soon...';
    }

    const remainingSeconds = Math.floor(remainingMs / 1000);
    
    // 格式化剩余时间
    if (remainingSeconds < 60) {
      return `~${remainingSeconds}s`;
    } else if (remainingSeconds < 3600) {
      const minutes = Math.floor(remainingSeconds / 60);
      return `~${minutes}m`;
    } else {
      const hours = Math.floor(remainingSeconds / 3600);
      const minutes = Math.floor((remainingSeconds % 3600) / 60);
      return `~${hours}h ${minutes}m`;
    }
  }

  /**
   * 渲染单个任务项
   */
  renderTaskItem = (task: AnalysisTask): React.ReactNode => {
    const isSelected = this.state.selectedTaskId === task.id;
    const { scheduleResult, retrySchedules } = this.state;
    
    // 判断任务是否在待执行队列中
    const isScheduledToExecute = scheduleResult?.tasksToExecute.some(t => t.id === task.id) || false;

    // 获取重试调度信息
    const retrySchedule = retrySchedules.get(task.id);
    const retryStatusText = this.retryScheduler.getRetryStatusText(task);

    // 计算预计完成时间
    const estimatedCompletion = this.calculateEstimatedCompletion(task);

    // 只有pending和failed状态的任务可以调整优先级
    const canAdjustPriority = task.status === 'pending' || task.status === 'failed';

    return (
      <div
        style={{
          ...styles.taskItem,
          ...(isSelected ? styles.taskItemSelected : {}),
        }}
        onClick={() => this.handleSelectTask(task.id)}
        data-testid={`task-item-${task.id}`}
      >
        {/* 任务头部 */}
        <div style={styles.taskHeader}>
          <div style={styles.taskTitle}>
            <span style={styles.taskName}>{task.name}</span>
            <span style={styles.taskType}>{this.getTaskTypeText(task.type)}</span>
          </div>
          <div style={styles.taskMeta}>
            <span
              style={{
                ...styles.priorityBadge,
                backgroundColor: this.getPriorityColor(task.priority),
              }}
            >
              {this.getPriorityText(task.priority)} ({task.priority})
            </span>
            <span
              style={{
                ...styles.statusBadge,
                backgroundColor: this.getStatusColor(task.status),
              }}
              data-testid={`task-status-${task.id}`}
            >
              {this.getStatusText(task.status)}
            </span>
            {isScheduledToExecute && task.status === 'pending' && (
              <span style={styles.scheduledBadge}>
                ⏱️ Scheduled
              </span>
            )}
            {retrySchedule && (
              <span style={styles.retryBadge}>
                🔄 Retry {task.retryCount + 1}/{task.maxRetries}
              </span>
            )}
          </div>
        </div>

        {/* 优先级调整控件 */}
        {canAdjustPriority && (
          <div style={styles.priorityControls}>
            <span style={styles.priorityControlsLabel}>Adjust Priority:</span>
            <div style={styles.priorityButtons}>
              <button
                style={{
                  ...styles.priorityButton,
                  ...(task.priority >= 10 ? styles.priorityButtonDisabled : {}),
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  this.handleIncreasePriority(task.id, task.priority);
                }}
                disabled={task.priority >= 10}
                data-testid={`increase-priority-${task.id}`}
                title="Increase priority"
              >
                ▲
              </button>
              <span style={styles.priorityValue}>{task.priority}</span>
              <button
                style={{
                  ...styles.priorityButton,
                  ...(task.priority <= 1 ? styles.priorityButtonDisabled : {}),
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  this.handleDecreasePriority(task.id, task.priority);
                }}
                disabled={task.priority <= 1}
                data-testid={`decrease-priority-${task.id}`}
                title="Decrease priority"
              >
                ▼
              </button>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={task.priority}
              onChange={(e) => {
                e.stopPropagation();
                const newPriority = parseInt(e.target.value, 10);
                this.handlePriorityChange(task.id, newPriority);
              }}
              style={styles.prioritySlider}
              data-testid={`priority-slider-${task.id}`}
              title={`Set priority (1-10): ${task.priority}`}
            />
          </div>
        )}

        {/* 进度条和预计完成时间 */}
        {task.status === 'running' && (
          <>
            <div style={styles.progressContainer}>
              <div
                style={{
                  ...styles.progressBar,
                  width: `${task.progress}%`,
                }}
                data-testid={`task-progress-${task.id}`}
              />
              <span style={styles.progressText}>{task.progress}%</span>
            </div>
            {estimatedCompletion && (
              <div style={styles.estimatedCompletionContainer}>
                <span style={styles.estimatedCompletionLabel}>⏱️ Est. completion:</span>
                <span 
                  style={styles.estimatedCompletionValue}
                  data-testid={`task-estimated-completion-${task.id}`}
                >
                  {this.formatEstimatedCompletion(estimatedCompletion)}
                </span>
                <span style={styles.estimatedCompletionTime}>
                  ({estimatedCompletion.toLocaleTimeString()})
                </span>
              </div>
            )}
          </>
        )}

        {/* 重试状态信息 */}
        {retrySchedule && retryStatusText && (
          <div style={styles.retryInfo}>
            <span style={styles.retryIcon}>🔄</span>
            <span style={styles.retryText}>{retryStatusText}</span>
          </div>
        )}

        {/* 任务详情 */}
        <div style={styles.taskDetails}>
          <div style={styles.taskDetailItem}>
            <span style={styles.taskDetailLabel}>Created:</span>
            <span style={styles.taskDetailValue}>{this.formatTime(task.createdAt)}</span>
          </div>
          {task.startedAt && (
            <div style={styles.taskDetailItem}>
              <span style={styles.taskDetailLabel}>Started:</span>
              <span style={styles.taskDetailValue}>{this.formatTime(task.startedAt)}</span>
            </div>
          )}
          {task.estimatedDuration && (
            <div style={styles.taskDetailItem}>
              <span style={styles.taskDetailLabel}>Est. Duration:</span>
              <span style={styles.taskDetailValue}>{this.formatDuration(task.estimatedDuration)}</span>
            </div>
          )}
          {task.retryCount > 0 && (
            <div style={styles.taskDetailItem}>
              <span style={styles.taskDetailLabel}>Retries:</span>
              <span style={styles.taskDetailValue}>
                {task.retryCount} / {task.maxRetries}
              </span>
            </div>
          )}
        </div>

        {/* 错误信息 */}
        {task.error && (
          <div style={styles.errorInfo}>
            <span style={styles.errorIcon}>⚠️</span>
            <span style={styles.errorMessage}>{task.error.message}</span>
          </div>
        )}
      </div>
    );
  };

  render(): React.ReactNode {
    const { loading, error, tasks, lastUpdate, scheduleResult } = this.state;
    const { listHeight } = this.props;

    // 加载状态
    if (loading && tasks.length === 0) {
      return (
        <LoadingState
          variant="spinner"
          size="large"
          text="Loading analysis queue..."
          fullscreen={false}
        />
      );
    }

    // 错误状态
    if (error && tasks.length === 0) {
      return (
        <div style={styles.errorContainer}>
          <div style={styles.errorIcon}>⚠️</div>
          <h2 style={styles.errorTitle}>Failed to Load Analysis Queue</h2>
          <p style={styles.errorMessage}>{error.message}</p>
          <button onClick={this.handleRefresh} style={styles.retryButton}>
            Retry
          </button>
        </div>
      );
    }

    // 统计信息
    const pendingCount = tasks.filter(t => t.status === 'pending').length;
    const runningCount = tasks.filter(t => t.status === 'running').length;
    const completedCount = tasks.filter(t => t.status === 'completed').length;
    const failedCount = tasks.filter(t => t.status === 'failed').length;

    // 获取按优先级排序的任务列表
    const sortedTasks = this.getSortedTasks();

    // 主内容
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>Analysis Queue</h1>
          <div style={styles.headerActions}>
            {lastUpdate && (
              <span style={styles.lastUpdate}>
                Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            <button onClick={this.handleRefresh} style={styles.refreshButton}>
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* 统计卡片 */}
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{tasks.length}</div>
            <div style={styles.statLabel}>Total Tasks</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: '#6b7280' }}>{pendingCount}</div>
            <div style={styles.statLabel}>Pending</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: '#0066cc' }}>{runningCount}</div>
            <div style={styles.statLabel}>Running</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: '#22c55e' }}>{completedCount}</div>
            <div style={styles.statLabel}>Completed</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statValue, color: '#ef4444' }}>{failedCount}</div>
            <div style={styles.statLabel}>Failed</div>
          </div>
        </div>

        {/* 调度信息 */}
        {scheduleResult && (
          <div style={styles.scheduleInfo}>
            <div style={styles.scheduleInfoItem}>
              <span style={styles.scheduleInfoLabel}>Max Concurrent:</span>
              <span style={styles.scheduleInfoValue}>{this.scheduler.getConfig().maxConcurrent}</span>
            </div>
            <div style={styles.scheduleInfoItem}>
              <span style={styles.scheduleInfoLabel}>Available Slots:</span>
              <span style={styles.scheduleInfoValue}>{scheduleResult.availableSlots}</span>
            </div>
            <div style={styles.scheduleInfoItem}>
              <span style={styles.scheduleInfoLabel}>Scheduled to Execute:</span>
              <span style={styles.scheduleInfoValue}>{scheduleResult.tasksToExecute.length}</span>
            </div>
            <div style={styles.scheduleInfoItem}>
              <span style={styles.scheduleInfoLabel}>Waiting:</span>
              <span style={styles.scheduleInfoValue}>{scheduleResult.waitingTasks.length}</span>
            </div>
          </div>
        )}

        {/* 任务列表 */}
        <div style={styles.listContainer}>
          <div style={styles.listHeader}>
            <h2 style={styles.listTitle}>Tasks ({tasks.length}) - Sorted by Priority</h2>
          </div>

          {tasks.length === 0 ? (
            <div style={styles.emptyState}>
              <div style={styles.emptyIcon}>📋</div>
              <p style={styles.emptyText}>No tasks in the queue</p>
            </div>
          ) : (
            <VirtualList
              items={sortedTasks}
              height={listHeight!}
              itemHeight={220}
              renderItem={this.renderTaskItem}
              className="analysis-queue-list"
            />
          )}
        </div>

        {/* 显示后台刷新错误 */}
        {error && tasks.length > 0 && (
          <div style={styles.backgroundErrorBanner}>
            ⚠️ Failed to refresh data: {error.message}
          </div>
        )}
      </div>
    );
  }
}

/**
 * AnalysisQueue组件 - 使用ErrorBoundary包裹
 */
export const AnalysisQueue: React.FC<AnalysisQueueProps> = (props) => {
  return (
    <ErrorBoundary>
      <AnalysisQueueComponent {...props} />
    </ErrorBoundary>
  );
};

// 样式定义
const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '24px',
    maxWidth: '1400px',
    margin: '0 auto',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  lastUpdate: {
    fontSize: '14px',
    color: '#6b7280',
  },
  refreshButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#0066cc',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  },
  scheduleInfo: {
    display: 'flex',
    gap: '24px',
    padding: '16px 24px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #bae6fd',
    borderRadius: '8px',
    marginBottom: '24px',
  },
  scheduleInfoItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  scheduleInfoLabel: {
    fontSize: '12px',
    color: '#0369a1',
    fontWeight: '500',
  },
  scheduleInfoValue: {
    fontSize: '18px',
    color: '#0c4a6e',
    fontWeight: '600',
  },
  statCard: {
    padding: '16px',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    textAlign: 'center',
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '4px',
  },
  statLabel: {
    fontSize: '14px',
    color: '#6b7280',
  },
  listContainer: {
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    overflow: 'hidden',
  },
  listHeader: {
    padding: '16px 24px',
    borderBottom: '1px solid #e5e7eb',
    backgroundColor: '#f9fafb',
  },
  listTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    margin: 0,
  },
  taskItem: {
    padding: '16px 24px',
    borderBottom: '1px solid #e5e7eb',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    backgroundColor: '#fff',
  },
  taskItemSelected: {
    backgroundColor: '#eff6ff',
  },
  taskHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  taskTitle: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  taskName: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
  },
  taskType: {
    fontSize: '14px',
    color: '#6b7280',
  },
  taskMeta: {
    display: 'flex',
    gap: '8px',
  },
  priorityBadge: {
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#fff',
    borderRadius: '12px',
  },
  priorityControls: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    marginBottom: '12px',
  },
  priorityControlsLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
  },
  priorityButtons: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  priorityButton: {
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#fff',
    backgroundColor: '#0066cc',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  priorityButtonDisabled: {
    backgroundColor: '#d1d5db',
    cursor: 'not-allowed',
  },
  priorityValue: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    minWidth: '24px',
    textAlign: 'center',
  },
  prioritySlider: {
    flex: 1,
    height: '6px',
    borderRadius: '3px',
    outline: 'none',
    cursor: 'pointer',
  },
  statusBadge: {
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#fff',
    borderRadius: '12px',
  },
  scheduledBadge: {
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#0066cc',
    backgroundColor: '#eff6ff',
    border: '1px solid #0066cc',
    borderRadius: '12px',
  },
  retryBadge: {
    padding: '4px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#f59e0b',
    backgroundColor: '#fffbeb',
    border: '1px solid #f59e0b',
    borderRadius: '12px',
  },
  retryInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#eff6ff',
    border: '1px solid #93c5fd',
    borderRadius: '6px',
    marginBottom: '12px',
  },
  retryIcon: {
    fontSize: '16px',
  },
  retryText: {
    fontSize: '14px',
    color: '#1e40af',
    fontWeight: '500',
  },
  progressContainer: {
    position: 'relative',
    height: '24px',
    backgroundColor: '#e5e7eb',
    borderRadius: '4px',
    marginBottom: '12px',
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#0066cc',
    transition: 'width 0.3s ease',
  },
  progressText: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    fontSize: '12px',
    fontWeight: '600',
    color: '#1f2937',
  },
  estimatedCompletionContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #bae6fd',
    borderRadius: '6px',
    marginBottom: '12px',
  },
  estimatedCompletionLabel: {
    fontSize: '14px',
    color: '#0369a1',
    fontWeight: '500',
  },
  estimatedCompletionValue: {
    fontSize: '14px',
    color: '#0c4a6e',
    fontWeight: '600',
  },
  estimatedCompletionTime: {
    fontSize: '12px',
    color: '#0369a1',
  },
  taskDetails: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '8px',
    marginBottom: '8px',
  },
  taskDetailItem: {
    display: 'flex',
    gap: '8px',
    fontSize: '14px',
  },
  taskDetailLabel: {
    color: '#6b7280',
    fontWeight: '500',
  },
  taskDetailValue: {
    color: '#1f2937',
  },
  errorInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#fef3c7',
    border: '1px solid #fbbf24',
    borderRadius: '6px',
    marginTop: '8px',
  },
  errorIcon: {
    fontSize: '16px',
  },
  errorMessage: {
    fontSize: '14px',
    color: '#92400e',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 20px',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '16px',
  },
  emptyText: {
    fontSize: '16px',
    color: '#6b7280',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 20px',
    textAlign: 'center',
  },
  errorTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
  },
  retryButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#0066cc',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  backgroundErrorBanner: {
    marginTop: '24px',
    padding: '12px 16px',
    backgroundColor: '#fef3c7',
    border: '1px solid #fbbf24',
    borderRadius: '6px',
    color: '#92400e',
    fontSize: '14px',
  },
};

export default AnalysisQueue;
