/**
 * ErrorBoundary属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 6: 错误边界捕获
 * 
 * **Validates: Requirements 1.3**
 * 
 * 测试覆盖:
 * - 对于任何组件内发生的错误，ErrorBoundary应该捕获错误并显示降级UI，而不是导致整个应用崩溃
 */

import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import fc from 'fast-check';
import { ErrorBoundary } from '../ErrorBoundary';
import { getErrorMonitor, resetErrorMonitor, MonitorConfig } from '../../services/ErrorMonitor';

describe('Property 6: 错误边界捕获', () => {
  let consoleErrorSpy: jest.SpyInstance;

  beforeAll(() => {
    // 抑制React的错误日志输出
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  beforeEach(() => {
    // 初始化ErrorMonitor
    resetErrorMonitor();
    const config: MonitorConfig = {
      environment: 'test',
      enableDebugMode: false,
    };
    const monitor = getErrorMonitor(config);
    monitor.initialize();
  });

  afterEach(() => {
    jest.clearAllMocks();
    resetErrorMonitor();
  });

  afterAll(() => {
    consoleErrorSpy.mockRestore();
  });

  // 自定义生成器：生成错误消息
  const errorMessageArbitrary = () =>
    fc.oneof(
      fc.string({ minLength: 1, maxLength: 200 }).filter(s => s.trim().length > 0),
      fc.constantFrom(
        'Network error',
        'Failed to fetch',
        'Timeout exceeded',
        'Invalid response',
        'Permission denied',
        'Resource not found',
        'Unexpected token',
        'Cannot read property',
        'undefined is not a function',
        'Maximum call stack size exceeded'
      )
    );

  // 自定义生成器：生成错误类型
  const errorTypeArbitrary = () =>
    fc.constantFrom(
      Error,
      TypeError,
      ReferenceError,
      RangeError,
      SyntaxError
    );

  // 自定义生成器：生成会抛出错误的组件
  const throwingComponentArbitrary = () =>
    fc.record({
      errorMessage: errorMessageArbitrary(),
      ErrorType: errorTypeArbitrary(),
      componentName: fc.constantFrom(
        'UserProfile',
        'Dashboard',
        'DataTable',
        'ChartWidget',
        'FormInput',
        'NavigationMenu'
      ),
    });

  it('应该捕获所有类型的组件错误并显示降级UI', () => {
    fc.assert(
      fc.property(
        throwingComponentArbitrary(),
        ({ errorMessage, ErrorType, componentName }) => {
          // 创建会抛出特定错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };
          ThrowingComponent.displayName = componentName;

          // 渲染包裹在ErrorBoundary中的组件
          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // 验证降级UI被显示（需求1.3）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // 验证原始组件内容没有被渲染
            expect(screen.queryByText('Normal content')).not.toBeInTheDocument();

            // 验证错误处理按钮存在
            expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/reload page/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/report issue/i)[0]).toBeInTheDocument();
          } finally {
            // 清理DOM
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有捕获的错误上报到ErrorMonitor', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        errorTypeArbitrary(),
        (errorMessage, ErrorType) => {
          const monitor = getErrorMonitor();
          const captureErrorSpy = jest.spyOn(monitor, 'captureError');

          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // 验证错误被上报到ErrorMonitor（需求1.3）
            expect(captureErrorSpy).toHaveBeenCalledTimes(1);
            expect(captureErrorSpy).toHaveBeenCalledWith(
              expect.any(ErrorType),
              expect.objectContaining({
                url: expect.any(String),
                userAgent: expect.any(String),
                timestamp: expect.any(Date),
                additionalData: expect.objectContaining({
                  componentStack: expect.any(String),
                  errorBoundary: true,
                }),
              })
            );
          } finally {
            captureErrorSpy.mockRestore();
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在捕获错误后不影响应用的其他部分', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, siblingContent) => {
          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // 渲染包含错误组件和正常组件的应用
          const { unmount } = render(
            <div>
              <div data-testid="sibling">{siblingContent}</div>
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            </div>
          );

          try {
            // 验证降级UI被显示
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // 验证兄弟组件仍然正常渲染（需求1.3 - 不导致整个应用崩溃）
            const sibling = screen.getByTestId('sibling');
            expect(sibling).toBeInTheDocument();
            expect(sibling.textContent).toBe(siblingContent);
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为嵌套的ErrorBoundary正确隔离错误', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, outerContent) => {
          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // 渲染嵌套的ErrorBoundary
          const { unmount } = render(
            <ErrorBoundary>
              <div data-testid="outer-content">{outerContent}</div>
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            </ErrorBoundary>
          );

          try {
            // 验证内部ErrorBoundary捕获了错误
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // 验证外部ErrorBoundary的内容仍然正常显示（需求1.3）
            const outerElement = screen.getByTestId('outer-content');
            expect(outerElement).toBeInTheDocument();
            expect(outerElement.textContent).toBe(outerContent);
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在渲染生命周期的任何阶段捕获错误', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.constantFrom('constructor', 'render', 'componentDidMount'),
        (errorMessage, lifecyclePhase) => {
          // 创建在不同生命周期阶段抛出错误的组件
          class LifecycleErrorComponent extends React.Component<{}, { shouldError: boolean }> {
            constructor(props: {}) {
              super(props);
              this.state = { shouldError: false };
              if (lifecyclePhase === 'constructor') {
                throw new Error(errorMessage);
              }
            }

            componentDidMount() {
              if (lifecyclePhase === 'componentDidMount') {
                throw new Error(errorMessage);
              }
            }

            render() {
              if (lifecyclePhase === 'render') {
                throw new Error(errorMessage);
              }
              return <div>Component content</div>;
            }
          }

          const { unmount } = render(
            <ErrorBoundary>
              <LifecycleErrorComponent />
            </ErrorBoundary>
          );

          try {
            // 验证错误被捕获并显示降级UI（需求1.3）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在使用自定义fallback时正确传递错误信息', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, customMessage) => {
          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // 自定义fallback
          const customFallback = (error: Error) => (
            <div data-testid="custom-fallback">
              {customMessage}: {error.message}
            </div>
          );

          const { unmount, container } = render(
            <ErrorBoundary fallback={customFallback}>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // 验证自定义fallback被显示（需求1.3）
            const fallbacks = container.querySelectorAll('[data-testid="custom-fallback"]');
            expect(fallbacks.length).toBeGreaterThan(0);
            const fallback = fallbacks[fallbacks.length - 1];
            expect(fallback).toBeInTheDocument();
            // 验证包含两部分内容
            expect(fallback.textContent).toContain(customMessage);
            expect(fallback.textContent).toContain(errorMessage);
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有错误类型提供一致的错误处理', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            errorMessage: errorMessageArbitrary(),
            ErrorType: errorTypeArbitrary(),
          }),
          { minLength: 1, maxLength: 5 }
        ),
        (errorConfigs) => {
          // 测试多个不同的错误配置
          errorConfigs.forEach(({ errorMessage, ErrorType }) => {
            const ThrowingComponent: React.FC = () => {
              throw new ErrorType(errorMessage);
            };

            const { unmount } = render(
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            );

            try {
              // 验证所有错误类型都被一致地处理（需求1.3）
              expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
              expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
            } finally {
              // 清理
              unmount();
            }
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在错误发生时保持应用状态的完整性', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.record({
          count: fc.integer({ min: 0, max: 100 }),
          name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
          isActive: fc.boolean(),
        }),
        (errorMessage, appState) => {
          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // 创建带有状态的应用
          const AppWithState: React.FC = () => {
            const [state] = React.useState(appState);
            return (
              <div>
                <div data-testid="app-state">
                  {JSON.stringify(state)}
                </div>
                <ErrorBoundary>
                  <ThrowingComponent />
                </ErrorBoundary>
              </div>
            );
          };

          const { unmount } = render(<AppWithState />);

          try {
            // 验证错误被捕获
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // 验证应用状态没有被破坏（需求1.3 - 不导致整个应用崩溃）
            const stateElement = screen.getByTestId('app-state');
            expect(stateElement).toBeInTheDocument();
            expect(stateElement.textContent).toBe(JSON.stringify(appState));
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在捕获错误后允许用户继续使用应用的其他功能', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.array(fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0), { minLength: 1, maxLength: 5 }),
        (errorMessage, menuItems) => {
          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // 渲染包含导航菜单和错误组件的应用
          const { unmount } = render(
            <div>
              <nav data-testid="navigation">
                {menuItems.map((item, index) => (
                  <button key={index} data-testid={`menu-item-${index}`}>
                    {item}
                  </button>
                ))}
              </nav>
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            </div>
          );

          try {
            // 验证错误被捕获
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // 验证导航菜单仍然可用（需求1.3 - 允许用户继续使用应用的其他部分）
            expect(screen.getByTestId('navigation')).toBeInTheDocument();
            menuItems.forEach((item, index) => {
              const menuItem = screen.getByTestId(`menu-item-${index}`);
              expect(menuItem).toBeInTheDocument();
              expect(menuItem.textContent).toBe(item);
            });
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该为所有捕获的错误调用onError回调', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        errorTypeArbitrary(),
        (errorMessage, ErrorType) => {
          const onError = jest.fn();

          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary onError={onError}>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // 验证onError回调被调用（需求1.3）
            expect(onError).toHaveBeenCalledTimes(1);
            expect(onError).toHaveBeenCalledWith(
              expect.any(ErrorType),
              expect.objectContaining({
                componentStack: expect.any(String),
              })
            );
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('应该在ErrorMonitor未初始化时仍然显示降级UI', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        (errorMessage) => {
          // 重置ErrorMonitor使其未初始化
          resetErrorMonitor();

          // 创建会抛出错误的组件
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // 验证即使ErrorMonitor未初始化，降级UI仍然显示（需求1.3 - 健壮性）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
          } finally {
            unmount();
            // 重新初始化ErrorMonitor以供后续测试使用
            const config: MonitorConfig = {
              environment: 'test',
              enableDebugMode: false,
            };
            const monitor = getErrorMonitor(config);
            monitor.initialize();
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
