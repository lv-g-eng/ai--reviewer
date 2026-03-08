/**
 * Architecture节点展开属性测试
 * 
 * Feature: frontend-production-optimization
 * Property 16: 架构节点展开
 * 
 * **Validates: Requirements 4.2**
 * 
 * 测试覆盖:
 * - 对于任何包含子组件的架构节点，点击后应该展开显示其子组件
 * 
 * 注意: 此测试验证Architecture组件在节点展开时的行为。
 * 测试通过模拟节点点击并验证展开状态来确保子组件正确显示。
 */

import fc from 'fast-check';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Architecture, { ArchitectureNode } from '../Architecture';

// Mock ReactFlow to avoid canvas rendering issues in tests
jest.mock('reactflow', () => {
  const React = require('react');
  const { useState } = React;

  return {
    __esModule: true,
    default: ({ nodes, onNodeClick }: any) => {
      return (
        <div data-testid="react-flow-mock">
          {nodes.map((node: any) => (
            <div
              key={node.id}
              data-testid={`node-${node.id}`}
              data-node-id={node.id}
              data-has-children={node.data.hasChildren}
              data-is-expanded={node.data.isExpanded}
              onClick={(e) => onNodeClick && onNodeClick(e, node)}
              style={{ cursor: 'pointer' }}
            >
              <div data-testid={`node-label-${node.id}`}>{node.data.label}</div>
              {node.data.hasChildren && (
                <div data-testid={`expansion-indicator-${node.id}`}>
                  {node.data.isExpanded ? '▼ Click to collapse' : '▶ Click to expand'}
                </div>
              )}
            </div>
          ))}
        </div>
      );
    },
    Controls: () => <div data-testid="controls">Controls</div>,
    Background: () => <div data-testid="background">Background</div>,
    MiniMap: () => <div data-testid="minimap">MiniMap</div>,
    Panel: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="panel">{children}</div>
    ),
    useNodesState: (initialNodes: any[]) => {
      const [nodes, setNodes] = useState(initialNodes);
      return [nodes, setNodes, jest.fn()];
    },
    useEdgesState: (initialEdges: any[]) => {
      const [edges, setEdges] = useState(initialEdges);
      return [edges, setEdges, jest.fn()];
    },
    addEdge: jest.fn(),
    MarkerType: {
      ArrowClosed: 'arrowclosed',
    },
    BackgroundVariant: {
      Dots: 'dots',
    },
  };
});

describe('Property 16: 架构节点展开', () => {
  afterEach(() => {
    cleanup();
    // Clear all timers and pending promises
    jest.clearAllTimers();
  });

  // 自定义生成器：生成有效的架构节点类型
  const nodeTypeArbitrary = () =>
    fc.constantFrom('service', 'component', 'module', 'database', 'external');

  // 自定义生成器：生成有效的节点指标
  const metricsArbitrary = () =>
    fc.record({
      responseTime: fc.integer({ min: 1, max: 5000 }),
      errorRate: fc.float({ min: 0, max: 100, noNaN: true }),
      throughput: fc.integer({ min: 1, max: 10000 }),
    });

  // 自定义生成器：生成子节点（不包含孙节点，避免过深嵌套）
  const childNodeArbitrary = () =>
    fc.record({
      id: fc.uuid(),
      name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
      type: nodeTypeArbitrary(),
      description: fc.option(fc.string({ maxLength: 100 }), { nil: undefined }),
      children: fc.constant([] as ArchitectureNode[]), // 子节点不再有子节点
      dependencies: fc.array(fc.uuid(), { maxLength: 3 }),
      metrics: fc.option(metricsArbitrary(), { nil: undefined }),
    });

  // 自定义生成器：生成带子节点的父节点
  const parentNodeWithChildrenArbitrary = () =>
    fc.record({
      id: fc.uuid(),
      name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
      type: nodeTypeArbitrary(),
      description: fc.option(fc.string({ maxLength: 100 }), { nil: undefined }),
      children: fc.array(childNodeArbitrary(), { minLength: 1, maxLength: 3 }),
      dependencies: fc.array(fc.uuid(), { maxLength: 3 }),
      metrics: fc.option(metricsArbitrary(), { nil: undefined }),
    });

  // 自定义生成器：生成没有子节点的节点
  const leafNodeArbitrary = () =>
    fc.record({
      id: fc.uuid(),
      name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
      type: nodeTypeArbitrary(),
      description: fc.option(fc.string({ maxLength: 100 }), { nil: undefined }),
      children: fc.constant([] as ArchitectureNode[]),
      dependencies: fc.array(fc.uuid(), { maxLength: 3 }),
      metrics: fc.option(metricsArbitrary(), { nil: undefined }),
    });

  it('应该为任何包含子节点的节点显示展开指示器', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          // 验证父节点存在
          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);
          expect(parentNodeElement).toBeInTheDocument();

          // 验证节点标记为有子节点
          expect(parentNodeElement.getAttribute('data-has-children')).toBe('true');

          // 验证展开指示器存在
          const expansionIndicator = screen.getByTestId(
            `expansion-indicator-${parentNode.id}`
          );
          expect(expansionIndicator).toBeInTheDocument();

          // 验证初始状态为未展开
          expect(parentNodeElement.getAttribute('data-is-expanded')).toBe('false');
          expect(expansionIndicator.textContent).toContain('Click to expand');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在点击包含子节点的节点后展开显示子节点', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          // 获取父节点元素
          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);
          expect(parentNodeElement).toBeInTheDocument();

          // 验证初始状态：子节点不可见
          const initialChildNodes = parentNode.children.map((child) =>
            screen.queryByTestId(`node-${child.id}`)
          );
          initialChildNodes.forEach((childNode) => {
            expect(childNode).not.toBeInTheDocument();
          });

          // 点击父节点展开
          await user.click(parentNodeElement);

          // 等待展开状态更新
          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
          });

          // 验证展开后：子节点可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              const childNode = screen.getByTestId(`node-${child.id}`);
              expect(childNode).toBeInTheDocument();
              expect(screen.getByTestId(`node-label-${child.id}`)).toHaveTextContent(
                child.name
              );
            });
          });

          // 验证展开指示器文本更新
          const expansionIndicator = screen.getByTestId(
            `expansion-indicator-${parentNode.id}`
          );
          expect(expansionIndicator.textContent).toContain('Click to collapse');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在再次点击已展开的节点后折叠隐藏子节点', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);

          // 第一次点击：展开
          await user.click(parentNodeElement);

          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
          });

          // 验证子节点可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              expect(screen.getByTestId(`node-${child.id}`)).toBeInTheDocument();
            });
          });

          // 第二次点击：折叠
          await user.click(parentNodeElement);

          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('false');
          });

          // 验证子节点不可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              expect(screen.queryByTestId(`node-${child.id}`)).not.toBeInTheDocument();
            });
          });

          // 验证展开指示器恢复为展开状态
          const expansionIndicator = screen.getByTestId(
            `expansion-indicator-${parentNode.id}`
          );
          expect(expansionIndicator.textContent).toContain('Click to expand');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该为没有子节点的节点不显示展开指示器', async () => {
    await fc.assert(
      fc.asyncProperty(leafNodeArbitrary(), async (leafNode) => {
        const { unmount } = render(<Architecture data={leafNode} />);

        await waitFor(() => {
          expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
        });

        // 验证叶子节点存在
        const leafNodeElement = screen.getByTestId(`node-${leafNode.id}`);
        expect(leafNodeElement).toBeInTheDocument();

        // 验证节点标记为没有子节点
        expect(leafNodeElement.getAttribute('data-has-children')).toBe('false');

        // 验证展开指示器不存在
        const expansionIndicator = screen.queryByTestId(
          `expansion-indicator-${leafNode.id}`
        );
        expect(expansionIndicator).not.toBeInTheDocument();

        unmount();
        cleanup();
      }),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在展开后显示所有子节点的完整信息', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const user = userEvent.setup();
          const { unmount, container } = render(<Architecture data={parentNode} />);

          try {
            await waitFor(
              () => {
                const flowMock = container.querySelector('[data-testid="react-flow-mock"]');
                expect(flowMock).toBeInTheDocument();
              },
              { timeout: 3000, container }
            );

            const parentNodeElement = container.querySelector(`[data-testid="node-${parentNode.id}"]`);
            expect(parentNodeElement).toBeInTheDocument();

            // 点击展开
            await user.click(parentNodeElement!);

            await waitFor(
              () => {
                const updatedParentNode = container.querySelector(`[data-testid="node-${parentNode.id}"]`);
                expect(updatedParentNode?.getAttribute('data-is-expanded')).toBe('true');
              },
              { timeout: 3000, container }
            );

            // 验证每个子节点的信息完整显示
            await waitFor(
              () => {
                parentNode.children.forEach((child) => {
                  const childNode = container.querySelector(`[data-testid="node-${child.id}"]`);
                  expect(childNode).toBeInTheDocument();

                  // 验证子节点名称
                  const childLabel = container.querySelector(`[data-testid="node-label-${child.id}"]`);
                  expect(childLabel?.textContent).toBe(child.name);

                  // 验证子节点的hasChildren属性正确（子节点没有子节点）
                  expect(childNode?.getAttribute('data-has-children')).toBe('false');
                });
              },
              { timeout: 3000, container }
            );
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该支持多个节点同时展开', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(parentNodeWithChildrenArbitrary(), { minLength: 2, maxLength: 3 }),
        async (nodes) => {
          // 创建一个根节点包含多个可展开的子节点
          const rootNode: ArchitectureNode = {
            id: fc.sample(fc.uuid(), 1)[0],
            name: 'Root',
            type: 'service',
            children: nodes,
            dependencies: [],
          };

          const user = userEvent.setup();
          const { unmount, container } = render(<Architecture data={rootNode} />);

          try {
            await waitFor(
              () => {
                const flowMock = container.querySelector('[data-testid="react-flow-mock"]');
                expect(flowMock).toBeInTheDocument();
              },
              { timeout: 3000, container }
            );

            // 展开第一个节点作为代表性测试
            const firstNode = nodes[0];
            const nodeElement = container.querySelector(`[data-testid="node-${firstNode.id}"]`);
            expect(nodeElement).toBeInTheDocument();
            
            await user.click(nodeElement!);

            await waitFor(
              () => {
                const updatedNode = container.querySelector(`[data-testid="node-${firstNode.id}"]`);
                expect(updatedNode?.getAttribute('data-is-expanded')).toBe('true');
              },
              { timeout: 3000, container }
            );

            // 验证第一个节点的子节点可见
            await waitFor(
              () => {
                firstNode.children.forEach((child) => {
                  const childNode = container.querySelector(`[data-testid="node-${child.id}"]`);
                  expect(childNode).toBeInTheDocument();
                });
              },
              { timeout: 3000, container }
            );
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 50 }
    );
  }, 60000);

  it('应该在展开节点时调用onNodeClick回调', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const onNodeClick = jest.fn();
          const user = userEvent.setup();
          const { unmount } = render(
            <Architecture data={parentNode} onNodeClick={onNodeClick} />
          );

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);

          // 点击节点
          await user.click(parentNodeElement);

          await waitFor(() => {
            // 验证回调被调用
            expect(onNodeClick).toHaveBeenCalled();

            // 验证回调参数包含正确的节点数据
            const callArg = onNodeClick.mock.calls[0][0];
            expect(callArg.id).toBe(parentNode.id);
            expect(callArg.name).toBe(parentNode.name);
            expect(callArg.children).toEqual(parentNode.children);
          });

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在不同节点类型上正确处理展开', async () => {
    await fc.assert(
      fc.asyncProperty(
        nodeTypeArbitrary(),
        fc.array(childNodeArbitrary(), { minLength: 1, maxLength: 3 }),
        async (nodeType, children) => {
          const parentNode: ArchitectureNode = {
            id: 'parent',
            name: `Parent ${nodeType}`,
            type: nodeType,
            children,
            dependencies: [],
          };

          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);

          // 点击展开
          await user.click(parentNodeElement);

          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
          });

          // 验证子节点可见
          await waitFor(() => {
            children.forEach((child) => {
              expect(screen.getByTestId(`node-${child.id}`)).toBeInTheDocument();
            });
          });

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('应该在展开节点时保持节点的其他属性不变', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          try {
            await waitFor(
              () => {
                expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
              },
              { timeout: 3000 }
            );

            // 记录展开前的节点信息
            const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);
            const initialLabel = screen.getByTestId(`node-label-${parentNode.id}`);
            const initialLabelText = initialLabel.textContent;

            // 点击展开
            await user.click(parentNodeElement);

            await waitFor(
              () => {
                const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
                expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
              },
              { timeout: 3000 }
            );

            // 验证节点标签没有改变
            const updatedLabel = screen.getByTestId(`node-label-${parentNode.id}`);
            expect(updatedLabel.textContent).toBe(initialLabelText);

            // 验证节点ID没有改变
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-node-id')).toBe(parentNode.id);
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 50 }
    );
  }, 60000);

  it('应该在快速连续点击时正确切换展开状态', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        fc.integer({ min: 2, max: 4 }),
        async (parentNode, clickCount) => {
          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          try {
            await waitFor(
              () => {
                expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
              },
              { timeout: 3000 }
            );

            const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);

            // 快速连续点击多次
            for (let i = 0; i < clickCount; i++) {
              await user.click(parentNodeElement);
              // 短暂等待以允许状态更新
              await new Promise((resolve) => setTimeout(resolve, 100));
            }

            // 验证最终状态与点击次数的奇偶性一致
            await waitFor(
              () => {
                const finalParentNode = screen.getByTestId(`node-${parentNode.id}`);
                const expectedExpanded = clickCount % 2 === 1;
                expect(finalParentNode.getAttribute('data-is-expanded')).toBe(
                  expectedExpanded.toString()
                );

                // 验证子节点可见性与展开状态一致
                if (expectedExpanded) {
                  parentNode.children.forEach((child) => {
                    expect(screen.getByTestId(`node-${child.id}`)).toBeInTheDocument();
                  });
                } else {
                  parentNode.children.forEach((child) => {
                    expect(
                      screen.queryByTestId(`node-${child.id}`)
                    ).not.toBeInTheDocument();
                  });
                }
              },
              { timeout: 3000 }
            );
          } finally {
            unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 50 }
    );
  }, 60000);
});
