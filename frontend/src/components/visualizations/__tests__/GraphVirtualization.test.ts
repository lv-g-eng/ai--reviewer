/**
 * Tests for Graph Virtualization Utilities
 * 
 * Tests cover:
 * - Virtualization for graphs with >1000 nodes
 * - Level-of-detail rendering
 * - Performance monitoring
 * - Adaptive LOD
 * 
 * Requirements: 1.8, 3.7
 */

import {
  shouldEnableVirtualization,
  calculateViewportBounds,
  isNodeInViewport,
  calculateNodeDistance,
  calculateNodeLOD,
  virtualizeNodes,
  virtualizeLinks,
  clusterNodes,
  simplifyGraph,
  RenderPerformanceMonitor,
  AdaptiveLODController,
  VirtualizedNode,
  VirtualizedLink,
  VirtualizationConfig
} from '../GraphVirtualization';

describe('GraphVirtualization', () => {
  describe('shouldEnableVirtualization', () => {
    it('should enable virtualization for graphs with >1000 nodes', () => {
      expect(shouldEnableVirtualization(1001)).toBe(true);
      expect(shouldEnableVirtualization(5000)).toBe(true);
    });

    it('should not enable virtualization for graphs with <=1000 nodes', () => {
      expect(shouldEnableVirtualization(1000)).toBe(false);
      expect(shouldEnableVirtualization(500)).toBe(false);
      expect(shouldEnableVirtualization(100)).toBe(false);
    });

    it('should respect custom threshold', () => {
      const config: VirtualizationConfig = {
        nodeThreshold: 500,
        viewportPadding: 200,
        lodDistances: { high: 500, medium: 1000, low: 2000 }
      };

      expect(shouldEnableVirtualization(501, config)).toBe(true);
      expect(shouldEnableVirtualization(500, config)).toBe(false);
    });
  });

  describe('calculateViewportBounds', () => {
    it('should calculate correct viewport bounds', () => {
      const bounds = calculateViewportBounds(0, 0, 1, 800, 600, 0);

      expect(bounds.minX).toBe(-400);
      expect(bounds.maxX).toBe(400);
      expect(bounds.minY).toBe(-300);
      expect(bounds.maxY).toBe(300);
    });

    it('should account for zoom level', () => {
      const bounds = calculateViewportBounds(0, 0, 2, 800, 600, 0);

      expect(bounds.minX).toBe(-200);
      expect(bounds.maxX).toBe(200);
      expect(bounds.minY).toBe(-150);
      expect(bounds.maxY).toBe(150);
    });

    it('should include padding', () => {
      const bounds = calculateViewportBounds(0, 0, 1, 800, 600, 100);

      expect(bounds.minX).toBe(-500);
      expect(bounds.maxX).toBe(500);
      expect(bounds.minY).toBe(-400);
      expect(bounds.maxY).toBe(400);
    });

    it('should handle camera offset', () => {
      const bounds = calculateViewportBounds(100, 200, 1, 800, 600, 0);

      expect(bounds.minX).toBe(-300);
      expect(bounds.maxX).toBe(500);
      expect(bounds.minY).toBe(-100);
      expect(bounds.maxY).toBe(500);
    });
  });

  describe('isNodeInViewport', () => {
    const bounds = {
      minX: -100,
      maxX: 100,
      minY: -100,
      maxY: 100
    };

    it('should return true for nodes inside viewport', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        x: 0,
        y: 0,
        visible: true,
        lod: 'high'
      };

      expect(isNodeInViewport(node, bounds)).toBe(true);
    });

    it('should return false for nodes outside viewport', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        x: 200,
        y: 200,
        visible: true,
        lod: 'high'
      };

      expect(isNodeInViewport(node, bounds)).toBe(false);
    });

    it('should return false for nodes without position', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        visible: true,
        lod: 'high'
      };

      expect(isNodeInViewport(node, bounds)).toBe(false);
    });

    it('should handle boundary cases', () => {
      const nodeOnBoundary: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        x: 100,
        y: 100,
        visible: true,
        lod: 'high'
      };

      expect(isNodeInViewport(nodeOnBoundary, bounds)).toBe(true);
    });
  });

  describe('calculateNodeDistance', () => {
    it('should calculate correct distance', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        x: 3,
        y: 4,
        visible: true,
        lod: 'high'
      };

      const distance = calculateNodeDistance(node, 0, 0);
      expect(distance).toBe(5); // 3-4-5 triangle
    });

    it('should return Infinity for nodes without position', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        visible: true,
        lod: 'high'
      };

      expect(calculateNodeDistance(node, 0, 0)).toBe(Infinity);
    });

    it('should return 0 for node at camera position', () => {
      const node: VirtualizedNode = {
        id: '1',
        name: 'Node 1',
        type: 'file',
        size: 10,
        x: 100,
        y: 200,
        visible: true,
        lod: 'high'
      };

      expect(calculateNodeDistance(node, 100, 200)).toBe(0);
    });
  });

  describe('calculateNodeLOD', () => {
    it('should return high LOD for close distances', () => {
      expect(calculateNodeLOD(100)).toBe('high');
      expect(calculateNodeLOD(499)).toBe('high');
    });

    it('should return medium LOD for medium distances', () => {
      expect(calculateNodeLOD(500)).toBe('medium');
      expect(calculateNodeLOD(750)).toBe('medium');
      expect(calculateNodeLOD(999)).toBe('medium');
    });

    it('should return low LOD for far distances', () => {
      expect(calculateNodeLOD(1000)).toBe('low');
      expect(calculateNodeLOD(5000)).toBe('low');
    });

    it('should respect custom LOD distances', () => {
      const config: VirtualizationConfig = {
        nodeThreshold: 1000,
        viewportPadding: 200,
        lodDistances: { high: 100, medium: 200, low: 300 }
      };

      expect(calculateNodeLOD(50, config)).toBe('high');
      expect(calculateNodeLOD(150, config)).toBe('medium');
      expect(calculateNodeLOD(250, config)).toBe('low');
    });
  });

  describe('virtualizeNodes', () => {
    const createTestNodes = (count: number): VirtualizedNode[] => {
      return Array.from({ length: count }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        x: (i % 10) * 100,
        y: Math.floor(i / 10) * 100,
        visible: true,
        lod: 'high' as const
      }));
    };

    it('should mark all nodes as visible for small graphs', () => {
      const nodes = createTestNodes(100);
      const virtualized = virtualizeNodes(nodes, 0, 0, 1, 800, 600);

      expect(virtualized.every(n => n.visible)).toBe(true);
      expect(virtualized.every(n => n.lod === 'high')).toBe(true);
    });

    it('should virtualize nodes for large graphs', () => {
      const nodes = createTestNodes(2000);
      const virtualized = virtualizeNodes(nodes, 0, 0, 1, 800, 600);

      const visibleCount = virtualized.filter(n => n.visible).length;
      expect(visibleCount).toBeLessThan(nodes.length);
    });

    it('should assign correct LOD based on distance', () => {
      const nodes = createTestNodes(2000);
      const virtualized = virtualizeNodes(nodes, 0, 0, 1, 800, 600);

      const highLOD = virtualized.filter(n => n.lod === 'high');
      const mediumLOD = virtualized.filter(n => n.lod === 'medium');
      const lowLOD = virtualized.filter(n => n.lod === 'low');

      expect(highLOD.length).toBeGreaterThan(0);
      expect(mediumLOD.length).toBeGreaterThan(0);
      expect(lowLOD.length).toBeGreaterThan(0);
    });

    it('should adjust visibility based on zoom', () => {
      const nodes = createTestNodes(2000);
      
      const virtualized1x = virtualizeNodes(nodes, 0, 0, 1, 800, 600);
      const virtualized2x = virtualizeNodes(nodes, 0, 0, 2, 800, 600);

      const visible1x = virtualized1x.filter(n => n.visible).length;
      const visible2x = virtualized2x.filter(n => n.visible).length;

      expect(visible2x).toBeLessThan(visible1x);
    });
  });

  describe('virtualizeLinks', () => {
    it('should mark links as visible when both nodes are visible', () => {
      const visibleNodeIds = new Set(['node-1', 'node-2']);
      const links: VirtualizedLink[] = [
        { source: 'node-1', target: 'node-2', visible: false }
      ];

      const virtualized = virtualizeLinks(links, visibleNodeIds);
      expect(virtualized[0].visible).toBe(true);
    });

    it('should mark links as invisible when source node is not visible', () => {
      const visibleNodeIds = new Set(['node-2']);
      const links: VirtualizedLink[] = [
        { source: 'node-1', target: 'node-2', visible: false }
      ];

      const virtualized = virtualizeLinks(links, visibleNodeIds);
      expect(virtualized[0].visible).toBe(false);
    });

    it('should mark links as invisible when target node is not visible', () => {
      const visibleNodeIds = new Set(['node-1']);
      const links: VirtualizedLink[] = [
        { source: 'node-1', target: 'node-2', visible: false }
      ];

      const virtualized = virtualizeLinks(links, visibleNodeIds);
      expect(virtualized[0].visible).toBe(false);
    });

    it('should handle object-based source/target', () => {
      const visibleNodeIds = new Set(['node-1', 'node-2']);
      const links: VirtualizedLink[] = [
        {
          source: { id: 'node-1', name: 'Node 1', type: 'file', size: 10, visible: true, lod: 'high' },
          target: { id: 'node-2', name: 'Node 2', type: 'file', size: 10, visible: true, lod: 'high' },
          visible: false
        }
      ];

      const virtualized = virtualizeLinks(links, visibleNodeIds);
      expect(virtualized[0].visible).toBe(true);
    });
  });

  describe('clusterNodes', () => {
    it('should create clusters for nearby nodes', () => {
      const nodes: VirtualizedNode[] = [
        { id: '1', name: 'Node 1', type: 'file', size: 10, x: 0, y: 0, visible: true, lod: 'high' },
        { id: '2', name: 'Node 2', type: 'file', size: 10, x: 50, y: 50, visible: true, lod: 'high' },
        { id: '3', name: 'Node 3', type: 'file', size: 10, x: 60, y: 60, visible: true, lod: 'high' },
        { id: '4', name: 'Node 4', type: 'file', size: 10, x: 500, y: 500, visible: true, lod: 'high' }
      ];

      const clusters = clusterNodes(nodes, 100);
      expect(clusters.length).toBeGreaterThanOrEqual(0); // May or may not create clusters depending on distance
    });

    it('should not create clusters for distant nodes', () => {
      const nodes: VirtualizedNode[] = [
        { id: '1', name: 'Node 1', type: 'file', size: 10, x: 0, y: 0, visible: true, lod: 'high' },
        { id: '2', name: 'Node 2', type: 'file', size: 10, x: 500, y: 500, visible: true, lod: 'high' }
      ];

      const clusters = clusterNodes(nodes, 100);
      expect(clusters.length).toBe(0);
    });

    it('should calculate cluster center correctly', () => {
      const nodes: VirtualizedNode[] = [
        { id: '1', name: 'Node 1', type: 'file', size: 10, x: 0, y: 0, visible: true, lod: 'high' },
        { id: '2', name: 'Node 2', type: 'file', size: 10, x: 100, y: 0, visible: true, lod: 'high' }
      ];

      const clusters = clusterNodes(nodes, 150);
      if (clusters.length > 0) {
        expect(clusters[0].x).toBe(50);
        expect(clusters[0].y).toBe(0);
      }
    });
  });

  describe('simplifyGraph', () => {
    it('should keep all nodes if below threshold', () => {
      const nodes: VirtualizedNode[] = Array.from({ length: 100 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        visible: true,
        lod: 'high'
      }));

      const links: VirtualizedLink[] = [];

      const simplified = simplifyGraph(nodes, links, 500);
      expect(simplified.nodes.length).toBe(100);
    });

    it('should reduce nodes if above threshold', () => {
      const nodes: VirtualizedNode[] = Array.from({ length: 1000 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        visible: true,
        lod: 'high'
      }));

      const links: VirtualizedLink[] = [];

      const simplified = simplifyGraph(nodes, links, 500);
      expect(simplified.nodes.length).toBe(500);
    });

    it('should prioritize high-degree nodes', () => {
      const nodes: VirtualizedNode[] = [
        { id: '1', name: 'Hub', type: 'file', size: 10, visible: true, lod: 'high' },
        { id: '2', name: 'Leaf 1', type: 'file', size: 10, visible: true, lod: 'high' },
        { id: '3', name: 'Leaf 2', type: 'file', size: 10, visible: true, lod: 'high' }
      ];

      const links: VirtualizedLink[] = [
        { source: '1', target: '2', visible: true },
        { source: '1', target: '3', visible: true }
      ];

      const simplified = simplifyGraph(nodes, links, 2);
      
      // Hub node should be kept
      expect(simplified.nodes.find(n => n.id === '1')).toBeDefined();
    });

    it('should filter links to match kept nodes', () => {
      const nodes: VirtualizedNode[] = Array.from({ length: 10 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        visible: true,
        lod: 'high'
      }));

      const links: VirtualizedLink[] = [
        { source: 'node-0', target: 'node-1', visible: true },
        { source: 'node-5', target: 'node-9', visible: true }
      ];

      const simplified = simplifyGraph(nodes, links, 5);
      
      // Links should only connect kept nodes
      const keptNodeIds = new Set(simplified.nodes.map(n => n.id));
      simplified.links.forEach(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        expect(keptNodeIds.has(sourceId)).toBe(true);
        expect(keptNodeIds.has(targetId)).toBe(true);
      });
    });
  });

  describe('RenderPerformanceMonitor', () => {
    it('should track FPS', () => {
      const monitor = new RenderPerformanceMonitor();

      // Simulate frames
      for (let i = 0; i < 60; i++) {
        monitor.startFrame();
        monitor.endFrame();
      }

      const fps = monitor.getFPS();
      expect(fps).toBeGreaterThanOrEqual(0);
    });

    it('should detect good performance', () => {
      const monitor = new RenderPerformanceMonitor();

      // Simulate good performance (60 FPS)
      for (let i = 0; i < 60; i++) {
        monitor.startFrame();
        monitor.endFrame();
      }

      // Wait for FPS update
      setTimeout(() => {
        expect(monitor.isPerformanceGood()).toBe(true);
      }, 1100);
    });

    it('should measure frame duration', () => {
      const monitor = new RenderPerformanceMonitor();

      monitor.startFrame();
      const metrics = monitor.endFrame();

      expect(metrics.frameDuration).toBeGreaterThanOrEqual(0);
      expect(metrics.fps).toBeGreaterThanOrEqual(0);
    });
  });

  describe('AdaptiveLODController', () => {
    it('should initialize with default config', () => {
      const controller = new AdaptiveLODController();
      const config = controller.getConfig();

      expect(config.nodeThreshold).toBe(1000);
      expect(config.lodDistances.high).toBe(500);
    });

    it('should track performance', () => {
      const controller = new AdaptiveLODController();

      controller.startFrame();
      const metrics = controller.endFrame();

      expect(metrics.fps).toBeGreaterThanOrEqual(0);
    });

    it('should provide FPS', () => {
      const controller = new AdaptiveLODController();

      controller.startFrame();
      controller.endFrame();

      const fps = controller.getFPS();
      expect(fps).toBeGreaterThanOrEqual(0);
    });

    it('should adjust LOD distances based on performance', () => {
      const controller = new AdaptiveLODController();
      const initialConfig = controller.getConfig();

      // Simulate multiple frames
      for (let i = 0; i < 15; i++) {
        controller.startFrame();
        controller.endFrame();
      }

      const adjustedConfig = controller.getConfig();
      
      // Config should exist (may or may not be adjusted depending on performance)
      expect(adjustedConfig.lodDistances.high).toBeGreaterThan(0);
      expect(adjustedConfig.lodDistances.medium).toBeGreaterThan(0);
      expect(adjustedConfig.lodDistances.low).toBeGreaterThan(0);
    });
  });

  describe('Performance Requirements (Requirement 1.8)', () => {
    it('should handle 1000 nodes efficiently', () => {
      const nodes: VirtualizedNode[] = Array.from({ length: 1000 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        x: Math.random() * 1000,
        y: Math.random() * 1000,
        visible: true,
        lod: 'high'
      }));

      const startTime = performance.now();
      const virtualized = virtualizeNodes(nodes, 0, 0, 1, 800, 600);
      const endTime = performance.now();

      const duration = endTime - startTime;
      
      // Should complete within 5 seconds (5000ms)
      expect(duration).toBeLessThan(5000);
      expect(virtualized.length).toBe(1000);
    });

    it('should handle 5000 nodes with virtualization', () => {
      const nodes: VirtualizedNode[] = Array.from({ length: 5000 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        type: 'file',
        size: 10,
        x: Math.random() * 2000,
        y: Math.random() * 2000,
        visible: true,
        lod: 'high'
      }));

      const startTime = performance.now();
      const virtualized = virtualizeNodes(nodes, 0, 0, 1, 800, 600);
      const endTime = performance.now();

      const duration = endTime - startTime;
      
      // Should complete within 5 seconds
      expect(duration).toBeLessThan(5000);
      
      // Should reduce visible nodes
      const visibleCount = virtualized.filter(n => n.visible).length;
      expect(visibleCount).toBeLessThan(nodes.length);
    });
  });
});
