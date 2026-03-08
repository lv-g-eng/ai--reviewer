/**
 * ErrorBoundary组件
 * 
 * 功能:
 * - 捕获React组件树中的错误
 * - 显示降级UI
 * - 集成ErrorMonitor上报错误
 * - 提供"重新加载"和"报告问题"功能
 * 
 * 验证需求: 1.3
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { getErrorMonitor } from '../services/ErrorMonitor';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: ErrorInfo, reset: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary类组件
 * 捕获子组件树中的JavaScript错误，记录错误并显示降级UI
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  /**
   * 当子组件抛出错误时调用
   */
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * 捕获错误并上报到监控服务
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 更新状态以包含errorInfo
    this.setState({
      errorInfo,
    });

    // 上报到ErrorMonitor
    try {
      const errorMonitor = getErrorMonitor();
      errorMonitor.captureError(error, {
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: new Date(),
        additionalData: {
          componentStack: errorInfo.componentStack,
          errorBoundary: true,
        },
      });
    } catch (monitorError) {
      // 如果ErrorMonitor未初始化或出错，至少输出到控制台
      console.error('Failed to report error to ErrorMonitor:', monitorError);
      console.error('Original error:', error, errorInfo);
    }

    // 调用自定义错误处理器
    if (this.props.onError) {
      try {
        this.props.onError(error, errorInfo);
      } catch (handlerError) {
        console.error('Error in onError handler:', handlerError);
      }
    }
  }

  /**
   * 重置错误状态，尝试重新渲染
   */
  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    // 调用自定义重置处理器
    if (this.props.onReset) {
      try {
        this.props.onReset();
      } catch (resetError) {
        console.error('Error in onReset handler:', resetError);
      }
    }
  };

  /**
   * 重新加载页面
   */
  handleReload = (): void => {
    window.location.reload();
  };

  /**
   * 报告问题（打开反馈表单或邮件）
   */
  handleReportIssue = (): void => {
    const { error, errorInfo } = this.state;
    
    // 构建问题报告内容
    const issueBody = encodeURIComponent(
      `## Error Report\n\n` +
      `**Error Message:** ${error?.message || 'Unknown error'}\n\n` +
      `**Stack Trace:**\n\`\`\`\n${error?.stack || 'No stack trace'}\n\`\`\`\n\n` +
      `**Component Stack:**\n\`\`\`\n${errorInfo?.componentStack || 'No component stack'}\n\`\`\`\n\n` +
      `**URL:** ${window.location.href}\n` +
      `**User Agent:** ${navigator.userAgent}\n` +
      `**Timestamp:** ${new Date().toISOString()}\n`
    );

    // 在实际应用中，这里可以：
    // 1. 打开内部问题跟踪系统
    // 2. 发送到支持邮箱
    // 3. 打开反馈表单
    // 这里使用mailto作为示例
    const mailtoLink = `mailto:support@example.com?subject=${encodeURIComponent('Error Report')}&body=${issueBody}`;
    window.location.href = mailtoLink;
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError && error) {
      // 如果提供了自定义fallback，使用它
      if (fallback && errorInfo) {
        return fallback(error, errorInfo, this.handleReset);
      }

      // 默认降级UI
      return (
        <div
          style={{
            padding: '40px 20px',
            maxWidth: '800px',
            margin: '0 auto',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          }}
        >
          <div
            style={{
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '8px',
              padding: '24px',
            }}
          >
            <h1
              style={{
                color: '#c33',
                fontSize: '24px',
                marginTop: 0,
                marginBottom: '16px',
              }}
            >
              ⚠️ Something went wrong
            </h1>
            
            <p
              style={{
                color: '#666',
                fontSize: '16px',
                lineHeight: '1.5',
                marginBottom: '24px',
              }}
            >
              We're sorry, but something unexpected happened. The error has been reported to our team.
            </p>

            {process.env.NODE_ENV === 'development' && (
              <details
                style={{
                  marginBottom: '24px',
                  padding: '16px',
                  backgroundColor: '#fff',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                }}
              >
                <summary
                  style={{
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    marginBottom: '8px',
                  }}
                >
                  Error Details (Development Only)
                </summary>
                <div
                  style={{
                    marginTop: '12px',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                  }}
                >
                  <p style={{ color: '#c33', fontWeight: 'bold' }}>
                    {error.message}
                  </p>
                  <pre
                    style={{
                      overflow: 'auto',
                      padding: '12px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '4px',
                      fontSize: '12px',
                      lineHeight: '1.4',
                    }}
                  >
                    {error.stack}
                  </pre>
                  {errorInfo?.componentStack && (
                    <>
                      <p style={{ fontWeight: 'bold', marginTop: '16px' }}>
                        Component Stack:
                      </p>
                      <pre
                        style={{
                          overflow: 'auto',
                          padding: '12px',
                          backgroundColor: '#f5f5f5',
                          borderRadius: '4px',
                          fontSize: '12px',
                          lineHeight: '1.4',
                        }}
                      >
                        {errorInfo.componentStack}
                      </pre>
                    </>
                  )}
                </div>
              </details>
            )}

            <div
              style={{
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
              }}
            >
              <button
                onClick={this.handleReset}
                style={{
                  padding: '12px 24px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#fff',
                  backgroundColor: '#0066cc',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = '#0052a3';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = '#0066cc';
                }}
              >
                Try Again
              </button>

              <button
                onClick={this.handleReload}
                style={{
                  padding: '12px 24px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#333',
                  backgroundColor: '#f0f0f0',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = '#e0e0e0';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = '#f0f0f0';
                }}
              >
                Reload Page
              </button>

              <button
                onClick={this.handleReportIssue}
                style={{
                  padding: '12px 24px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#333',
                  backgroundColor: '#f0f0f0',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = '#e0e0e0';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = '#f0f0f0';
                }}
              >
                Report Issue
              </button>
            </div>
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
