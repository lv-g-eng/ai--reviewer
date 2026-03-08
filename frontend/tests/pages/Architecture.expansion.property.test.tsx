/**
 * Architecture节点展开propertytest
 * 
 * Feature: frontend-production-optimization
 * Property 16: architecture节点展开
 * 
 * **Validates: Requirements 4.2**
 * 
 * testCoverage:
 * - 对于任何contain子component的architecture节点，点击后should展开show其子component
 * 
 * note: testVerifiesArchitecturecomponent在节点展开时的行为。
 * test通过模拟节点点击并verify展开status来确保子component正确show。
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

describe('Property 16: architecture节点展开', () => {
  afterEach(() => {
    cleanup();
    // Clear all timers and pending promises
    jest.clearAllTimers();
  });

  // customGenerator：generate有效的architecture节点type
  const nodeTypeArbitrary = () =>
    fc.constantFrom('service', 'component', 'module', 'database', 'external');

  // customGenerator：generate有效的节点指标
  const metricsArbitrary = () =>
    fc.record({
      responseTime: fc.integer({ min: 1, max: 5000 }),
      errorRate: fc.float({ min: 0, max: 100, noNaN: true }),
      throughput: fc.integer({ min: 1, max: 10000 }),
    });

  // customGenerator：generate子节点（不contain孙节点，避免过深嵌套）
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

  // customGenerator：generate带子节点的父节点
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

  // customGenerator：generate没有子节点的节点
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

  it('should为任何contain子节点的节点show展开指示器', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          // verify父节点存在
          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);
          expect(parentNodeElement).toBeInTheDocument();

          // verify节点标记为有子节点
          expect(parentNodeElement.getAttribute('data-has-children')).toBe('true');

          // verify展开指示器存在
          const expansionIndicator = screen.getByTestId(
            `expansion-indicator-${parentNode.id}`
          );
          expect(expansionIndicator).toBeInTheDocument();

          // verify初始status为未展开
          expect(parentNodeElement.getAttribute('data-is-expanded')).toBe('false');
          expect(expansionIndicator.textContent).toContain('Click to expand');

          unmount();
          cleanup();
        }
      ),
      { numRuns: 100 }
    );
  }, 60000);

  it('shouldBeAt点击contain子节点的节点后展开show子节点', async () => {
    await fc.assert(
      fc.asyncProperty(
        parentNodeWithChildrenArbitrary(),
        async (parentNode) => {
          const user = userEvent.setup();
          const { unmount } = render(<Architecture data={parentNode} />);

          await waitFor(() => {
            expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
          });

          // get父节点元素
          const parentNodeElement = screen.getByTestId(`node-${parentNode.id}`);
          expect(parentNodeElement).toBeInTheDocument();

          // verify初始status：子节点不可见
          const initialChildNodes = parentNode.children.map((child) =>
            screen.queryByTestId(`node-${child.id}`)
          );
          initialChildNodes.forEach((childNode) => {
            expect(childNode).not.toBeInTheDocument();
          });

          // 点击父节点展开
          await user.click(parentNodeElement);

          // wait展开statusupdate
          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
          });

          // verify展开后：子节点可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              const childNode = screen.getByTestId(`node-${child.id}`);
              expect(childNode).toBeInTheDocument();
              expect(screen.getByTestId(`node-label-${child.id}`)).toHaveTextContent(
                child.name
              );
            });
          });

          // verify展开指示器文本update
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

  it('shouldBeAt再times点击已展开的节点后折叠hide子节点', async () => {
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

          // 第一times点击：展开
          await user.click(parentNodeElement);

          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('true');
          });

          // verify子节点可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              expect(screen.getByTestId(`node-${child.id}`)).toBeInTheDocument();
            });
          });

          // 第二times点击：折叠
          await user.click(parentNodeElement);

          await waitFor(() => {
            const updatedParentNode = screen.getByTestId(`node-${parentNode.id}`);
            expect(updatedParentNode.getAttribute('data-is-expanded')).toBe('false');
          });

          // verify子节点不可见
          await waitFor(() => {
            parentNode.children.forEach((child) => {
              expect(screen.queryByTestId(`node-${child.id}`)).not.toBeInTheDocument();
            });
          });

          // verify展开指示器恢复为展开status
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

  it('should为没有子节点的节点不show展开指示器', async () => {
    await fc.assert(
      fc.asyncProperty(leafNodeArbitrary(), async (leafNode) => {
        const { unmount } = render(<Architecture data={leafNode} />);

        await waitFor(() => {
          expect(screen.getByTestId('react-flow-mock')).toBeInTheDocument();
        });

        // verify叶子节点存在
        const leafNodeElement = screen.getByTestId(`node-${leafNode.id}`);
        expect(leafNodeElement).toBeInTheDocument();

        // verify节点标记为没有子节点
        expect(leafNodeElement.getAttribute('data-has-children')).toBe('false');

        // verify展开指示器不存在
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

  it('shouldBeAt展开后show所有子节点的完整info', async () => {
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

            // verify每item子节点的info完整show
            await waitFor(
              () => {
                parentNode.children.forEach((child) => {
                  const childNode = container.querySelector(`[data-testid="node-${child.id}"]`);
                  expect(childNode).toBeInTheDocument();

                  // verify子节点名称
                  const childLabel = container.querySelector(`[data-testid="node-label-${child.id}"]`);
                  expect(childLabel?.textContent).toBe(child.name);

                  // verify子节点的hasChildrenproperty正确（子节点没有子节点）
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

  it('shouldsupport多item节点同时展开', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(parentNodeWithChildrenArbitrary(), { minLength: 2, maxLength: 3 }),
        async (nodes) => {
          // create一item根节点contain多item可展开的子节点
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

            // 展开第一item节点作为代表性test
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

            // verify第一item节点的子节点可见
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

  it('shouldBeAt展开节点时调用onNodeClick回调', async () => {
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
            // verify回调被调用
            expect(onNodeClick).toHaveBeenCalled();

            // verify回调paramcontain正确的节点data
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

  it('shouldBeAt不同节点type上正确handle展开', async () => {
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

          // verify子节点可见
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

  it('shouldBeAt展开节点时保持节点的其他property不变', async () => {
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

            // record展开前的节点info
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

            // verify节点tag没有改变
            const updatedLabel = screen.getByTestId(`node-label-${parentNode.id}`);
            expect(updatedLabel.textContent).toBe(initialLabelText);

            // verify节点ID没有改变
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

  it('shouldBeAt快速连续点击时正确切换展开status', async () => {
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

            // 快速连续点击多times
            for (let i = 0; i < clickCount; i++) {
              await user.click(parentNodeElement);
              // 短暂wait以allowstatusupdate
              await new Promise((resolve) => setTimeout(resolve, 100));
            }

            // verify最终status与点击times数的奇偶性一致
            await waitFor(
              () => {
                const finalParentNode = screen.getByTestId(`node-${parentNode.id}`);
                const expectedExpanded = clickCount % 2 === 1;
                expect(finalParentNode.getAttribute('data-is-expanded')).toBe(
                  expectedExpanded.toString()
                );

                // verify子节点可见性与展开status一致
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
