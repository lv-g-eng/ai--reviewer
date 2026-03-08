/**
 * ErrorBoundarypropertytest
 * 
 * Feature: frontend-production-optimization
 * Property 6: error边界捕获
 * 
 * **Validates: Requirements 1.3**
 * 
 * testCoverage:
 * - 对于任何component内发生的error，ErrorBoundaryshould捕获error并show降级UI，而不是导致整item应用崩溃
 */

import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import fc from 'fast-check';
import { ErrorBoundary } from '../ErrorBoundary';
import { getErrorMonitor, resetErrorMonitor, MonitorConfig } from '../../services/ErrorMonitor';

describe('Property 6: error边界捕获', () => {
  let consoleErrorSpy: jest.SpyInstance;

  beforeAll(() => {
    // 抑制React的errorlogoutput
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

  // customGenerator：generateerror消息
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

  // customGenerator：generateerrortype
  const errorTypeArbitrary = () =>
    fc.constantFrom(
      Error,
      TypeError,
      ReferenceError,
      RangeError,
      SyntaxError
    );

  // customGenerator：generate会抛出error的component
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

  it('should捕获所有type的componenterror并show降级UI', () => {
    fc.assert(
      fc.property(
        throwingComponentArbitrary(),
        ({ errorMessage, ErrorType, componentName }) => {
          // create会抛出特定error的component
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };
          ThrowingComponent.displayName = componentName;

          // render包裹在ErrorBoundary中的component
          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // verify降级UI被show（requirement1.3）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // verify原始componentcontent没有被render
            expect(screen.queryByText('Normal content')).not.toBeInTheDocument();

            // verifyerrorhandlebutton存在
            expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/reload page/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/report issue/i)[0]).toBeInTheDocument();
          } finally {
            // cleanupDOM
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should为所有捕获的error上报到ErrorMonitor', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        errorTypeArbitrary(),
        (errorMessage, ErrorType) => {
          const monitor = getErrorMonitor();
          const captureErrorSpy = jest.spyOn(monitor, 'captureError');

          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // verifyerror被上报到ErrorMonitor（requirement1.3）
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

  it('shouldBeAt捕获error后不影response用的其他部分', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, siblingContent) => {
          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // rendercontainerrorcomponentand正常component的应用
          const { unmount } = render(
            <div>
              <div data-testid="sibling">{siblingContent}</div>
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            </div>
          );

          try {
            // verify降级UI被show
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // verify兄弟component仍然正常render（requirement1.3 - 不导致整item应用崩溃）
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

  it('should为嵌套的ErrorBoundary正确隔离error', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, outerContent) => {
          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // render嵌套的ErrorBoundary
          const { unmount } = render(
            <ErrorBoundary>
              <div data-testid="outer-content">{outerContent}</div>
              <ErrorBoundary>
                <ThrowingComponent />
              </ErrorBoundary>
            </ErrorBoundary>
          );

          try {
            // verify内部ErrorBoundary捕获了error
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // verify外部ErrorBoundary的content仍然正常show（requirement1.3）
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

  it('shouldBeAtrender生命周期的任何阶段捕获error', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.constantFrom('constructor', 'render', 'componentDidMount'),
        (errorMessage, lifecyclePhase) => {
          // create在不同生命周期阶段抛出error的component
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
            // verifyerror被捕获并show降级UI（requirement1.3）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldBeAtuse自定义fallback时正确传递errorinfo', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        (errorMessage, customMessage) => {
          // create会抛出error的component
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
            // verify自定义fallback被show（requirement1.3）
            const fallbacks = container.querySelectorAll('[data-testid="custom-fallback"]');
            expect(fallbacks.length).toBeGreaterThan(0);
            const fallback = fallbacks[fallbacks.length - 1];
            expect(fallback).toBeInTheDocument();
            // verifycontain两部分content
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

  it('should为所有errortypeprovide一致的errorhandle', () => {
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
          // test多item不同的errorconfig
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
              // verify所有errortype都被一致地handle（requirement1.3）
              expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
              expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
            } finally {
              // cleanup
              unmount();
            }
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('shouldBeAterror发生时保持应用status的完整性', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.record({
          count: fc.integer({ min: 0, max: 100 }),
          name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
          isActive: fc.boolean(),
        }),
        (errorMessage, appState) => {
          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // create带有status的应用
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
            // verifyerror被捕获
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // verify应用status没有被破坏（requirement1.3 - 不导致整item应用崩溃）
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

  it('shouldBeAt捕获error后allowuser继续use应用的其他feature', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        fc.array(fc.string({ minLength: 1, maxLength: 30 }).filter(s => s.trim().length > 0), { minLength: 1, maxLength: 5 }),
        (errorMessage, menuItems) => {
          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          // rendercontainnavmenuanderrorcomponent的应用
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
            // verifyerror被捕获
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();

            // verifynavmenu仍然可用（requirement1.3 - allowuser继续use应用的其他部分）
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

  it('should为所有捕获的error调用onError回调', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        errorTypeArbitrary(),
        (errorMessage, ErrorType) => {
          const onError = jest.fn();

          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new ErrorType(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary onError={onError}>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // verifyonError回调被调用（requirement1.3）
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

  it('shouldBeAtErrorMonitor未初始化时仍然show降级UI', () => {
    fc.assert(
      fc.property(
        errorMessageArbitrary(),
        (errorMessage) => {
          // resetErrorMonitor使其未初始化
          resetErrorMonitor();

          // create会抛出error的component
          const ThrowingComponent: React.FC = () => {
            throw new Error(errorMessage);
          };

          const { unmount } = render(
            <ErrorBoundary>
              <ThrowingComponent />
            </ErrorBoundary>
          );

          try {
            // verify即使ErrorMonitor未初始化，降级UI仍然show（requirement1.3 - 健壮性）
            expect(screen.getAllByText(/something went wrong/i)[0]).toBeInTheDocument();
            expect(screen.getAllByText(/try again/i)[0]).toBeInTheDocument();
          } finally {
            unmount();
            // 重新初始化ErrorMonitor以供后续testuse
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
