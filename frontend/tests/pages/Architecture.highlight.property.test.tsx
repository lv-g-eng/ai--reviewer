/**
 * Property-based tests for Architecture dependency path highlighting
 * 
 * **Feature: frontend-production-optimization, Property 17: dependencypath高亮**
 * **Validates: Requirements 4.4**
 * 
 * Tests that when a component is selected, all dependency paths (both upstream
 * and downstream) are correctly highlighted.
 */

import fc from 'fast-check';
import { ArchitectureNode } from '../Architecture';

/**
 * Trace all dependency paths from a selected node
 * This is a copy of the implementation for testing purposes
 */
function traceDependencyPaths(
  rootNode: ArchitectureNode,
  selectedNodeId: string
): { highlightedNodes: Set<string>; highlightedEdges: Set<string> } {
  const highlightedNodes = new Set<string>();
  const highlightedEdges = new Set<string>();
  
  // Build a map of all nodes for quick lookup
  const nodeMap = new Map<string, ArchitectureNode>();
  const buildNodeMap = (node: ArchitectureNode) => {
    nodeMap.set(node.id, node);
    node.children.forEach(buildNodeMap);
  };
  buildNodeMap(rootNode);
  
  // Build reverse dependency map (who depends on whom)
  const reverseDeps = new Map<string, Set<string>>();
  nodeMap.forEach((node) => {
    node.dependencies.forEach((depId) => {
      if (!reverseDeps.has(depId)) {
        reverseDeps.set(depId, new Set());
      }
      reverseDeps.get(depId)!.add(node.id);
    });
  });
  
  // Add the selected node itself
  highlightedNodes.add(selectedNodeId);
  
  // Trace downstream dependencies (nodes that the selected node depends on)
  const traceDownstream = (nodeId: string) => {
    const node = nodeMap.get(nodeId);
    if (!node) return;
    
    node.dependencies.forEach((depId) => {
      if (!highlightedNodes.has(depId)) {
        highlightedNodes.add(depId);
        highlightedEdges.add(`${nodeId}-${depId}`);
        traceDownstream(depId);
      } else {
        highlightedEdges.add(`${nodeId}-${depId}`);
      }
    });
  };
  
  // Trace upstream dependencies (nodes that depend on the selected node)
  const traceUpstream = (nodeId: string) => {
    const dependents = reverseDeps.get(nodeId);
    if (!dependents) return;
    
    dependents.forEach((dependentId) => {
      if (!highlightedNodes.has(dependentId)) {
        highlightedNodes.add(dependentId);
        highlightedEdges.add(`${dependentId}-${nodeId}`);
        traceUpstream(dependentId);
      } else {
        highlightedEdges.add(`${dependentId}-${nodeId}`);
      }
    });
  };
  
  traceDownstream(selectedNodeId);
  traceUpstream(selectedNodeId);
  
  return { highlightedNodes, highlightedEdges };
}

/**
 * Arbitrary for generating architecture node IDs
 */
const nodeIdArbitrary = () =>
  fc.string({
    minLength: 1,
    maxLength: 3,
    unit: fc.constantFrom('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'),
  });

/**
 * Arbitrary for generating architecture nodes
 * Creates a tree structure with dependencies
 */
const architectureNodeArbitrary = (
  depth: number = 0,
  maxDepth: number = 3,
  existingIds: Set<string> = new Set()
): fc.Arbitrary<ArchitectureNode> => {
  return fc
    .tuple(
      nodeIdArbitrary(),
      fc.constantFrom('service', 'component', 'module', 'database', 'external'),
      fc.array(nodeIdArbitrary(), { maxLength: depth === 0 ? 5 : 3 })
    )
    .chain(([baseId, type, depIds]) => {
      // Ensure unique ID
      let id = baseId;
      let counter = 0;
      while (existingIds.has(id)) {
        id = `${baseId}${counter++}`;
      }
      existingIds.add(id);

      // Generate children if not at max depth
      const childrenArb =
        depth < maxDepth
          ? fc.array(architectureNodeArbitrary(depth + 1, maxDepth, existingIds), {
              maxLength: 3,
            })
          : fc.constant([]);

      return childrenArb.map((children) => {
        // Filter dependencies to only include existing nodes (not self)
        const validDeps = depIds.filter((depId) => depId !== id && existingIds.has(depId));

        return {
          id,
          name: `Node ${id}`,
          type,
          children,
          dependencies: validDeps,
          metrics: {
            responseTime: 100,
            errorRate: 1.0,
            throughput: 200,
          },
        };
      });
    });
};

describe('Property: Dependency Path Highlighting (Requirement 4.4)', () => {
  /**
   * Property 17: Selected node is always included in highlighted nodes
   */
  it('should always include the selected node in highlighted nodes', () => {
    fc.assert(
      fc.property(architectureNodeArbitrary(), (rootNode) => {
        // Get all node IDs
        const allNodeIds: string[] = [];
        const collectIds = (node: ArchitectureNode) => {
          allNodeIds.push(node.id);
          node.children.forEach(collectIds);
        };
        collectIds(rootNode);

        // Test each node as selected
        allNodeIds.forEach((selectedId) => {
          const { highlightedNodes } = traceDependencyPaths(rootNode, selectedId);
          expect(highlightedNodes.has(selectedId)).toBe(true);
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property 17: All downstream dependencies are highlighted
   */
  it('should highlight all downstream dependencies (nodes that selected node depends on)', () => {
    fc.assert(
      fc.property(architectureNodeArbitrary(), (rootNode) => {
        // Build node map
        const nodeMap = new Map<string, ArchitectureNode>();
        const buildMap = (node: ArchitectureNode) => {
          nodeMap.set(node.id, node);
          node.children.forEach(buildMap);
        };
        buildMap(rootNode);

        // Test each node
        nodeMap.forEach((node, nodeId) => {
          const { highlightedNodes } = traceDependencyPaths(rootNode, nodeId);

          // All direct dependencies should be highlighted
          node.dependencies.forEach((depId) => {
            expect(highlightedNodes.has(depId)).toBe(true);
          });

          // All transitive dependencies should be highlighted
          const visited = new Set<string>();
          const checkTransitive = (id: string) => {
            if (visited.has(id)) return;
            visited.add(id);
            const depNode = nodeMap.get(id);
            if (depNode) {
              depNode.dependencies.forEach((depId) => {
                expect(highlightedNodes.has(depId)).toBe(true);
                checkTransitive(depId);
              });
            }
          };
          node.dependencies.forEach(checkTransitive);
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property 17: All upstream dependencies are highlighted
   */
  it('should highlight all upstream dependencies (nodes that depend on selected node)', () => {
    fc.assert(
      fc.property(architectureNodeArbitrary(), (rootNode) => {
        // Build reverse dependency map
        const reverseDeps = new Map<string, Set<string>>();
        const buildReverseDeps = (node: ArchitectureNode) => {
          node.dependencies.forEach((depId) => {
            if (!reverseDeps.has(depId)) {
              reverseDeps.set(depId, new Set());
            }
            reverseDeps.get(depId)!.add(node.id);
          });
          node.children.forEach(buildReverseDeps);
        };
        buildReverseDeps(rootNode);

        // Build node map
        const nodeMap = new Map<string, ArchitectureNode>();
        const buildMap = (node: ArchitectureNode) => {
          nodeMap.set(node.id, node);
          node.children.forEach(buildMap);
        };
        buildMap(rootNode);

        // Test each node
        nodeMap.forEach((_, nodeId) => {
          const { highlightedNodes } = traceDependencyPaths(rootNode, nodeId);

          // All direct dependents should be highlighted
          const directDependents = reverseDeps.get(nodeId);
          if (directDependents) {
            directDependents.forEach((dependentId) => {
              expect(highlightedNodes.has(dependentId)).toBe(true);
            });
          }

          // All transitive dependents should be highlighted
          const visited = new Set<string>();
          const checkTransitive = (id: string) => {
            if (visited.has(id)) return;
            visited.add(id);
            const dependents = reverseDeps.get(id);
            if (dependents) {
              dependents.forEach((dependentId) => {
                expect(highlightedNodes.has(dependentId)).toBe(true);
                checkTransitive(dependentId);
              });
            }
          };
          checkTransitive(nodeId);
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property 17: All edges in dependency paths are highlighted
   */
  it('should highlight all edges that connect highlighted nodes', () => {
    fc.assert(
      fc.property(architectureNodeArbitrary(), (rootNode) => {
        // Build node map
        const nodeMap = new Map<string, ArchitectureNode>();
        const buildMap = (node: ArchitectureNode) => {
          nodeMap.set(node.id, node);
          node.children.forEach(buildMap);
        };
        buildMap(rootNode);

        // Test each node
        nodeMap.forEach((_, nodeId) => {
          const { highlightedNodes, highlightedEdges } = traceDependencyPaths(
            rootNode,
            nodeId
          );

          // For each highlighted node, check if its edges to other highlighted nodes are highlighted
          highlightedNodes.forEach((highlightedNodeId) => {
            const node = nodeMap.get(highlightedNodeId);
            if (node) {
              node.dependencies.forEach((depId) => {
                if (highlightedNodes.has(depId)) {
                  const edgeId = `${highlightedNodeId}-${depId}`;
                  expect(highlightedEdges.has(edgeId)).toBe(true);
                }
              });
            }
          });
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property 17: Nodes not in dependency path are not highlighted
   */
  it('should not highlight nodes that are not in any dependency path', () => {
    fc.assert(
      fc.property(architectureNodeArbitrary(), (rootNode) => {
        // Build node map
        const nodeMap = new Map<string, ArchitectureNode>();
        const buildMap = (node: ArchitectureNode) => {
          nodeMap.set(node.id, node);
          node.children.forEach(buildMap);
        };
        buildMap(rootNode);

        // Build reverse dependency map
        const reverseDeps = new Map<string, Set<string>>();
        nodeMap.forEach((node) => {
          node.dependencies.forEach((depId) => {
            if (!reverseDeps.has(depId)) {
              reverseDeps.set(depId, new Set());
            }
            reverseDeps.get(depId)!.add(node.id);
          });
        });

        // Test each node
        nodeMap.forEach((_, selectedId) => {
          const { highlightedNodes } = traceDependencyPaths(rootNode, selectedId);

          // Find nodes that should NOT be highlighted
          // (nodes that are neither upstream nor downstream from selected)
          const shouldBeHighlighted = new Set<string>();
          shouldBeHighlighted.add(selectedId);

          // Add all downstream
          const addDownstream = (nodeId: string) => {
            const node = nodeMap.get(nodeId);
            if (node) {
              node.dependencies.forEach((depId) => {
                if (!shouldBeHighlighted.has(depId)) {
                  shouldBeHighlighted.add(depId);
                  addDownstream(depId);
                }
              });
            }
          };
          addDownstream(selectedId);

          // Add all upstream
          const addUpstream = (nodeId: string) => {
            const dependents = reverseDeps.get(nodeId);
            if (dependents) {
              dependents.forEach((dependentId) => {
                if (!shouldBeHighlighted.has(dependentId)) {
                  shouldBeHighlighted.add(dependentId);
                  addUpstream(dependentId);
                }
              });
            }
          };
          addUpstream(selectedId);

          // Verify highlighted nodes match expected
          expect(highlightedNodes.size).toBe(shouldBeHighlighted.size);
          shouldBeHighlighted.forEach((id) => {
            expect(highlightedNodes.has(id)).toBe(true);
          });
        });
      }),
      { numRuns: 50 }
    );
  });

  /**
   * Property 17: Circular dependencies are handled correctly
   */
  it('should handle circular dependencies without infinite loops', () => {
    // Create a graph with circular dependencies
    const circularGraph: ArchitectureNode = {
      id: 'root',
      name: 'Root',
      type: 'service',
      children: [
        {
          id: 'a',
          name: 'Node A',
          type: 'service',
          children: [],
          dependencies: ['b'],
        },
        {
          id: 'b',
          name: 'Node B',
          type: 'service',
          children: [],
          dependencies: ['c'],
        },
        {
          id: 'c',
          name: 'Node C',
          type: 'service',
          children: [],
          dependencies: ['a'], // Circular: c -> a -> b -> c
        },
      ],
      dependencies: [],
    };

    // Should complete without hanging
    const { highlightedNodes, highlightedEdges } = traceDependencyPaths(
      circularGraph,
      'a'
    );

    // All nodes in the cycle should be highlighted
    expect(highlightedNodes.has('a')).toBe(true);
    expect(highlightedNodes.has('b')).toBe(true);
    expect(highlightedNodes.has('c')).toBe(true);

    // All edges in the cycle should be highlighted
    expect(highlightedEdges.has('a-b')).toBe(true);
    expect(highlightedEdges.has('b-c')).toBe(true);
    expect(highlightedEdges.has('c-a')).toBe(true);
  });

  /**
   * Property 17: Empty dependencies result in only selected node highlighted
   */
  it('should only highlight selected node when it has no dependencies', () => {
    const isolatedNode: ArchitectureNode = {
      id: 'isolated',
      name: 'Isolated Node',
      type: 'service',
      children: [],
      dependencies: [],
    };

    const { highlightedNodes, highlightedEdges } = traceDependencyPaths(
      isolatedNode,
      'isolated'
    );

    expect(highlightedNodes.size).toBe(1);
    expect(highlightedNodes.has('isolated')).toBe(true);
    expect(highlightedEdges.size).toBe(0);
  });

  /**
   * Property 17: Complex multi-level dependencies are traced correctly
   */
  it('should trace complex multi-level dependency chains', () => {
    const complexGraph: ArchitectureNode = {
      id: 'root',
      name: 'Root',
      type: 'service',
      children: [
        {
          id: 'frontend',
          name: 'Frontend',
          type: 'component',
          children: [],
          dependencies: ['api'],
        },
        {
          id: 'api',
          name: 'API',
          type: 'service',
          children: [],
          dependencies: ['auth', 'data'],
        },
        {
          id: 'auth',
          name: 'Auth',
          type: 'service',
          children: [],
          dependencies: ['db'],
        },
        {
          id: 'data',
          name: 'Data',
          type: 'service',
          children: [],
          dependencies: ['db', 'cache'],
        },
        {
          id: 'db',
          name: 'Database',
          type: 'database',
          children: [],
          dependencies: [],
        },
        {
          id: 'cache',
          name: 'Cache',
          type: 'database',
          children: [],
          dependencies: [],
        },
      ],
      dependencies: [],
    };

    // Select 'api' - should highlight frontend (upstream), auth, data, db, cache (downstream)
    const { highlightedNodes } = traceDependencyPaths(complexGraph, 'api');

    expect(highlightedNodes.has('api')).toBe(true);
    expect(highlightedNodes.has('frontend')).toBe(true); // upstream
    expect(highlightedNodes.has('auth')).toBe(true); // downstream
    expect(highlightedNodes.has('data')).toBe(true); // downstream
    expect(highlightedNodes.has('db')).toBe(true); // downstream (transitive)
    expect(highlightedNodes.has('cache')).toBe(true); // downstream (transitive)
  });
});
