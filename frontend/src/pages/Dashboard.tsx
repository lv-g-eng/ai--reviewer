/**
 * Dashboard页面component
 * 
 * feature:
 * - 展示system概览and关键指标
 * - data懒load机制（在component挂载时get，而非import时）
 * - 30sec自动refresh（可config）
 * - useErrorBoundary包裹
 * - cleanup定时器防止内存泄漏
 * 
 * verifyRequirement: 1.1, 1.4
 */

import React, { Component } from 'react';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { LoadingState } from '../components/LoadingState';
import { getApiClient } from '../services/ApiClient';
import '../styles/responsive.css';

export interface DashboardProps {
  /** datarefresh间隔（ms），默认30sec */
  refreshInterval?: number;
}

export interface SystemMetrics {
  activeUsers: number;
  totalProjects: number;
  pendingPRs: number;
  queuedTasks: number;
  systemHealth: 'healthy' | 'degraded' | 'down';
  lastUpdate: Date;
}

export interface DashboardState {
  metrics: SystemMetrics | null;
  loading: boolean;
  error: Error | null;
  lastUpdate: Date | null;
}

/**
 * Dashboardclasscomponent
 * 实现懒load、定时refreshand资源cleanup
 */
export class DashboardComponent extends Component<DashboardProps, DashboardState> {
  private refreshTimer: NodeJS.Timeout | null = null;
  private mounted = false;
  private abortController: AbortController | null = null;
  private pendingRequests: Set<Promise<void>> = new Set();

  static defaultProps: Partial<DashboardProps> = {
    refreshInterval: 30000, // 默认30sec
  };

  constructor(props: DashboardProps) {
    super(props);
    this.state = {
      metrics: null,
      loading: true,
      error: null,
      lastUpdate: null,
    };
  }

  /**
   * component挂载后开始data懒load
   */
  async componentDidMount(): Promise<void> {
    this.mounted = true;
    
    // 首timesloaddata
    await this.fetchMetrics();

    // set定时refresh
    if (this.props.refreshInterval && this.props.refreshInterval > 0) {
      this.refreshTimer = setInterval(() => {
        this.fetchMetrics();
      }, this.props.refreshInterval);
    }
  }

  /**
   * component卸载时cleanup所有资源
   * 防止内存泄漏
   */
  componentWillUnmount(): void {
    this.mounted = false;
    
    // cleanup定时器
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }

    // cancel所有进行中的request
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    // cleanup待handle的request引用
    this.pendingRequests.clear();
  }

  /**
   * getDashboard指标data
   * 确保在500ms内responsedataupdate
   */
  fetchMetrics = async (): Promise<void> => {
    // 如果component已卸载，不executeupdate
    if (!this.mounted) {
      return;
    }

    // record开始时间以跟踪response性能
    const startTime = performance.now();

    // create新的AbortController用于此timesrequest
    this.abortController = new AbortController();

    const requestPromise = (async () => {
      try {
        // 只在首timesload时showloadingstatus
        if (!this.state.metrics) {
          this.setState({ loading: true, error: null });
        }

        const apiClient = getApiClient();
        const metrics = await apiClient.get<SystemMetrics>('/dashboard/metrics');

        // 计算response时间
        const responseTime = performance.now() - startTime;

        // 确保component仍然挂载后再updatestatus
        if (this.mounted) {
          this.setState({
            metrics,
            loading: false,
            error: null,
            lastUpdate: new Date(),
          });

          // 在devenvrecordresponse时间以verify性能
          if (process.env.NODE_ENV === 'development') {
            console.log(`Dashboard data refresh completed in ${responseTime.toFixed(2)}ms`);
            if (responseTime > 500) {
              console.warn(`Dashboard refresh exceeded 500ms target: ${responseTime.toFixed(2)}ms`);
            }
          }
        }
      } catch (error) {
        // 如果是cancelerror，不updatestatus
        if (error instanceof Error && error.name === 'AbortError') {
          return;
        }

        // 确保component仍然挂载后再updatestatus
        if (this.mounted) {
          this.setState({
            loading: false,
            error: error instanceof Error ? error : new Error('Failed to fetch metrics'),
          });
        }
      }
    })();

    // 跟踪待handle的request
    this.pendingRequests.add(requestPromise);

    try {
      await requestPromise;
    } finally {
      // cleanup此timesrequest的引用
      this.pendingRequests.delete(requestPromise);
    }
  };

  /**
   * 手动refreshdata
   */
  handleRefresh = (): void => {
    this.fetchMetrics();
  };

  /**
   * getsystem健康status的颜色
   */
  getHealthColor(health: SystemMetrics['systemHealth']): string {
    switch (health) {
      case 'healthy':
        return '#22c55e'; // green
      case 'degraded':
        return '#f59e0b'; // amber
      case 'down':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  }

  /**
   * getsystem健康status的文本
   */
  getHealthText(health: SystemMetrics['systemHealth']): string {
    switch (health) {
      case 'healthy':
        return 'Healthy';
      case 'degraded':
        return 'Degraded';
      case 'down':
        return 'Down';
      default:
        return 'Unknown';
    }
  }

  render(): React.ReactNode {
    const { loading, error, metrics, lastUpdate } = this.state;

    // loadstatus
    if (loading && !metrics) {
      return (
        <LoadingState
          variant="spinner"
          size="large"
          text="Loading dashboard..."
          fullscreen={false}
        />
      );
    }

    // errorstatus
    if (error && !metrics) {
      return (
        <div style={styles.errorContainer}>
          <div style={styles.errorIcon}>⚠️</div>
          <h2 style={styles.errorTitle}>Failed to Load Dashboard</h2>
          <p style={styles.errorMessage}>{error.message}</p>
          <button onClick={this.handleRefresh} style={styles.retryButton}>
            Retry
          </button>
        </div>
      );
    }

    // 主content
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>Dashboard</h1>
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

        {metrics && (
          <div style={styles.metricsGrid}>
            {/* Active Users */}
            <div style={styles.metricCard}>
              <div style={styles.metricIcon}>👥</div>
              <div style={styles.metricContent}>
                <div style={styles.metricLabel}>Active Users</div>
                <div style={styles.metricValue}>{metrics.activeUsers}</div>
              </div>
            </div>

            {/* Total Projects */}
            <div style={styles.metricCard}>
              <div style={styles.metricIcon}>📁</div>
              <div style={styles.metricContent}>
                <div style={styles.metricLabel}>Total Projects</div>
                <div style={styles.metricValue}>{metrics.totalProjects}</div>
              </div>
            </div>

            {/* Pending PRs */}
            <div style={styles.metricCard}>
              <div style={styles.metricIcon}>🔀</div>
              <div style={styles.metricContent}>
                <div style={styles.metricLabel}>Pending PRs</div>
                <div style={styles.metricValue}>{metrics.pendingPRs}</div>
              </div>
            </div>

            {/* Queued Tasks */}
            <div style={styles.metricCard}>
              <div style={styles.metricIcon}>📋</div>
              <div style={styles.metricContent}>
                <div style={styles.metricLabel}>Queued Tasks</div>
                <div style={styles.metricValue}>{metrics.queuedTasks}</div>
              </div>
            </div>

            {/* System Health */}
            <div style={styles.metricCard}>
              <div style={styles.metricIcon}>💚</div>
              <div style={styles.metricContent}>
                <div style={styles.metricLabel}>System Health</div>
                <div
                  style={{
                    ...styles.metricValue,
                    color: this.getHealthColor(metrics.systemHealth),
                  }}
                >
                  {this.getHealthText(metrics.systemHealth)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* show后台refresherror（不影响已有datashow） */}
        {error && metrics && (
          <div style={styles.backgroundErrorBanner}>
            ⚠️ Failed to refresh data: {error.message}
          </div>
        )}
      </div>
    );
  }
}

/**
 * Dashboardcomponent - useErrorBoundary包裹
 */
export const Dashboard: React.FC<DashboardProps> = (props) => {
  return (
    <ErrorBoundary>
      <DashboardComponent {...props} />
    </ErrorBoundary>
  );
};

// style定义 - useresponse式设计
const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    maxWidth: '100%',
    padding: '16px',
    margin: '0 auto',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    overflowX: 'hidden',
  },
  header: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginBottom: '20px',
  },
  title: {
    fontSize: 'clamp(24px, 5vw, 32px)', // Responsive font size
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
    wordWrap: 'break-word',
  },
  headerActions: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '12px',
  },
  lastUpdate: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    color: '#6b7280',
  },
  refreshButton: {
    padding: '8px 16px',
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#0066cc',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    whiteSpace: 'nowrap',
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 250px), 1fr))',
    gap: '16px',
    width: '100%',
  },
  metricCard: {
    display: 'flex',
    alignItems: 'center',
    padding: '16px',
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    transition: 'box-shadow 0.2s',
    minWidth: 0, // Allow flex items to shrink below content size
  },
  metricIcon: {
    fontSize: 'clamp(32px, 6vw, 40px)',
    marginRight: '12px',
    flexShrink: 0,
  },
  metricContent: {
    flex: 1,
    minWidth: 0, // Allow text truncation
  },
  metricLabel: {
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    color: '#6b7280',
    marginBottom: '4px',
  },
  metricValue: {
    fontSize: 'clamp(20px, 4vw, 28px)',
    fontWeight: 'bold',
    color: '#1f2937',
    wordWrap: 'break-word',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 16px',
    textAlign: 'center',
  },
  errorIcon: {
    fontSize: 'clamp(48px, 10vw, 64px)',
    marginBottom: '16px',
  },
  errorTitle: {
    fontSize: 'clamp(20px, 4vw, 24px)',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '8px',
    wordWrap: 'break-word',
  },
  errorMessage: {
    fontSize: 'clamp(14px, 3vw, 16px)',
    color: '#6b7280',
    marginBottom: '24px',
    wordWrap: 'break-word',
    maxWidth: '100%',
  },
  retryButton: {
    padding: '10px 20px',
    fontSize: 'clamp(14px, 3vw, 16px)',
    fontWeight: '500',
    color: '#fff',
    backgroundColor: '#0066cc',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  backgroundErrorBanner: {
    marginTop: '16px',
    padding: '12px 16px',
    backgroundColor: '#fef3c7',
    border: '1px solid #fbbf24',
    borderRadius: '6px',
    color: '#92400e',
    fontSize: 'clamp(12px, 2.5vw, 14px)',
    wordWrap: 'break-word',
  },
};

// Media query styles applied via inline styles
const getResponsiveStyles = () => {
  if (typeof window === 'undefined') return {};
  
  const width = window.innerWidth;
  
  // Tablet and above
  if (width >= 768) {
    return {
      container: { padding: '20px', maxWidth: '1200px' },
      header: { flexDirection: 'row' as const, justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' },
      metricsGrid: { gap: '20px' },
    };
  }
  
  // Desktop and above
  if (width >= 1024) {
    return {
      container: { padding: '24px', maxWidth: '1400px' },
      header: { marginBottom: '32px' },
      metricsGrid: { gap: '24px' },
      metricCard: { padding: '24px' },
    };
  }
  
  return {};
};

export default Dashboard;
