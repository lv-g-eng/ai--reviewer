# Dependency Graph Visualization

## Overview

The Dependency Graph Visualization component provides an interactive, high-performance visualization of code dependencies with support for large graphs, circular dependency detection, and real-time updates.

## Features

### 1. Graph Rendering (Task 15.1)
- **D3.js Force-Directed Layout**: Uses `react-force-graph-2d` for smooth, physics-based graph rendering
- **Zoom Controls**: Supports zoom levels from 0.1x to 10x (Requirement 3.8)
- **Pan and Navigate**: Full pan support with mouse/touch gestures
- **Node Styling**: Color-coded nodes based on type and cycle severity
- **Edge Styling**: Weighted edges with directional arrows

### 2. Graph Virtualization (Task 15.2)
- **Automatic Virtualization**: Enables for graphs with >1000 nodes (Requirement 3.7)
- **Level-of-Detail (LOD) Rendering**: Three LOD levels (high, medium, low) based on distance from camera
- **Viewport Culling**: Only renders nodes within viewport bounds
- **Performance Monitoring**: Tracks FPS and adjusts quality dynamically
- **Adaptive LOD**: Automatically adjusts LOD distances based on performance
- **Graph Simplification**: Reduces node count while preserving important nodes
- **Node Clustering**: Groups nearby nodes for simplified rendering

### 3. Circular Dependency Highlighting (Task 15.3)
- **Automatic Detection**: Highlights nodes and edges involved in circular dependencies
- **Severity Levels**: Color-coded by severity (low=yellow, medium=orange, high=red) (Requirement 1.7)
- **Cycle Details**: Shows cycle path and involved nodes
- **Click-to-Expand**: Click on cycle to see full details
- **Tooltips**: Hover tooltips showing cycle information
- **Filter by Cycle**: Dropdown to focus on specific circular dependencies

### 4. Real-Time Updates (Task 15.4)
- **WebSocket Integration**: Connects to backend for live updates (Requirement 3.9)
- **Incremental Updates**: Updates graph as analysis progresses
- **Connection Status**: Visual indicator showing live connection status
- **Automatic Reconnection**: Reconnects automatically on disconnect

## Components

### DependencyGraphVisualization.tsx
Main visualization component with all features integrated.

**Props:**
```typescript
interface DependencyGraphVisualizationProps {
  projectId?: string;        // Project ID for loading graph data
  analysisId?: string;        // Analysis ID for specific analysis
  className?: string;         // Additional CSS classes
  websocketUrl?: string;      // WebSocket URL for real-time updates
}
```

**Usage:**
```tsx
import DependencyGraphVisualization from '@/components/visualizations/DependencyGraphVisualization';

// Basic usage
<DependencyGraphVisualization analysisId="analysis-123" />

// With real-time updates
<DependencyGraphVisualization 
  analysisId="analysis-123"
  websocketUrl="ws://localhost:8000/ws/analysis/123"
/>
```

### GraphVirtualization.ts
Utility functions for graph virtualization and performance optimization.

**Key Functions:**
- `shouldEnableVirtualization(nodeCount)`: Determines if virtualization should be enabled
- `virtualizeNodes(nodes, camera, zoom, width, height)`: Applies virtualization to nodes
- `virtualizeLinks(links, visibleNodeIds)`: Filters links based on visible nodes
- `simplifyGraph(nodes, links, maxNodes)`: Reduces graph complexity
- `clusterNodes(nodes, clusterDistance)`: Groups nearby nodes
- `AdaptiveLODController`: Monitors performance and adjusts quality

**Usage:**
```typescript
import { virtualizeNodes, AdaptiveLODController } from './GraphVirtualization';

// Virtualize nodes
const virtualizedNodes = virtualizeNodes(
  nodes,
  cameraX,
  cameraY,
  zoom,
  width,
  height
);

// Use adaptive LOD
const lodController = new AdaptiveLODController();
lodController.startFrame();
// ... render frame ...
const metrics = lodController.endFrame();
console.log(`FPS: ${metrics.fps}`);
```

## Performance

### Requirements Met
- **Requirement 1.8**: Renders interactive dependency graphs within 5 seconds for graphs with <1000 nodes ✓
- **Requirement 3.7**: Implements virtualization for graphs with >1000 nodes ✓
- **Requirement 3.8**: Supports zoom levels from 0.1x to 10x ✓
- **Requirement 3.9**: Implements real-time updates via WebSocket ✓

### Performance Characteristics
- **Small Graphs (<1000 nodes)**: Full rendering, all nodes visible, high LOD
- **Medium Graphs (1000-5000 nodes)**: Virtualization enabled, viewport culling, adaptive LOD
- **Large Graphs (>5000 nodes)**: Aggressive virtualization, node clustering, graph simplification

### Optimization Techniques
1. **Viewport Culling**: Only renders nodes within visible area
2. **Level-of-Detail**: Reduces detail for distant nodes
3. **Node Clustering**: Groups nearby nodes at low LOD
4. **Graph Simplification**: Removes low-importance nodes
5. **Adaptive Quality**: Adjusts rendering quality based on FPS
6. **Incremental Updates**: Updates graph progressively during analysis

## Testing

### Test Coverage
- **DependencyGraphVisualization.test.tsx**: 28 tests covering all features
- **GraphVirtualization.test.ts**: 42 tests covering virtualization utilities

### Running Tests
```bash
# Run all visualization tests
npm test -- visualizations

# Run specific test file
npm test -- DependencyGraphVisualization.test.tsx
npm test -- GraphVirtualization.test.ts

# Run with coverage
npm test -- --coverage visualizations
```

### Test Categories
1. **Basic Rendering**: Component rendering, statistics display
2. **Zoom Controls**: Zoom in/out, reset view, zoom range validation
3. **Circular Dependencies**: Detection, highlighting, severity badges, cycle details
4. **Search and Filtering**: Node search, cycle filtering
5. **Real-Time Updates**: WebSocket connection, incremental updates
6. **Node Interaction**: Click handling, details display
7. **Export/Import**: Data export, graph refresh
8. **Performance**: Render time validation, large graph handling

## Data Format

### Node Format
```typescript
interface GraphNode {
  id: string;                    // Unique node identifier
  name: string;                  // Display name
  type: 'file' | 'class' | 'function' | 'module';
  size: number;                  // Visual size
  complexity?: number;           // Code complexity metric
  inCycle?: boolean;             // Part of circular dependency
  cycleSeverity?: 'low' | 'medium' | 'high';
  cycleDetails?: string[];       // Nodes in the cycle
  x?: number;                    // X position (set by layout)
  y?: number;                    // Y position (set by layout)
}
```

### Link Format
```typescript
interface GraphLink {
  source: string | GraphNode;    // Source node ID or object
  target: string | GraphNode;    // Target node ID or object
  type: 'depends' | 'calls' | 'implements';
  weight: number;                // Link strength
  inCycle?: boolean;             // Part of circular dependency
  cycleSeverity?: 'low' | 'medium' | 'high';
}
```

### Circular Dependency Format
```typescript
interface CircularDependency {
  id: string;                    // Unique cycle identifier
  nodes: string[];               // Node IDs in the cycle
  severity: 'low' | 'medium' | 'high';
  description: string;           // Human-readable description
}
```

## WebSocket Protocol

### Connection
```typescript
const ws = new WebSocket('ws://localhost:8000/ws/analysis/{analysisId}');
```

### Message Types

#### Analysis Progress
```json
{
  "type": "analysis_progress",
  "nodes": [/* new/updated nodes */],
  "links": [/* new/updated links */],
  "circularDependencies": [/* detected cycles */]
}
```

#### Analysis Complete
```json
{
  "type": "analysis_complete",
  "graph": {
    "nodes": [/* all nodes */],
    "links": [/* all links */],
    "circularDependencies": [/* all cycles */]
  }
}
```

## Customization

### Styling
The component uses Tailwind CSS and can be customized via the `className` prop:

```tsx
<DependencyGraphVisualization 
  className="h-screen w-full"
  analysisId="123"
/>
```

### Colors
Node and edge colors are defined in the component and can be customized:

```typescript
// Node colors by severity
const getNodeColor = (node: GraphNode) => {
  if (!node.inCycle) return '#3b82f6'; // Blue
  switch (node.cycleSeverity) {
    case 'high': return '#ef4444';     // Red
    case 'medium': return '#f59e0b';   // Orange
    case 'low': return '#eab308';      // Yellow
  }
};
```

### Virtualization Config
Virtualization behavior can be customized:

```typescript
const config: VirtualizationConfig = {
  nodeThreshold: 1000,           // Enable virtualization above this
  viewportPadding: 200,          // Extra space around viewport
  lodDistances: {
    high: 500,                   // High detail distance
    medium: 1000,                // Medium detail distance
    low: 2000                    // Low detail distance
  }
};
```

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Touch gestures supported

## Dependencies

- `react-force-graph-2d`: Force-directed graph rendering
- `d3`: Data visualization utilities
- `lucide-react`: Icons
- `@/components/ui/*`: UI components (Card, Button, Input, Badge, Label)

## Future Enhancements

1. **Graph Layouts**: Additional layout algorithms (hierarchical, circular, tree)
2. **Node Grouping**: Manual grouping and collapsing of nodes
3. **Path Highlighting**: Highlight paths between selected nodes
4. **Export Formats**: Export to PNG, SVG, PDF
5. **Minimap**: Overview minimap for large graphs
6. **Time-based Visualization**: Animate graph changes over time
7. **3D Visualization**: Optional 3D rendering for very large graphs
8. **Collaborative Features**: Multi-user viewing and annotation

## Troubleshooting

### Graph Not Rendering
- Check that `analysisId` or `projectId` is provided
- Verify data format matches expected schema
- Check browser console for errors

### Poor Performance
- Ensure virtualization is enabled for large graphs
- Check FPS in browser dev tools
- Reduce graph complexity with simplification

### WebSocket Not Connecting
- Verify `websocketUrl` is correct
- Check network connectivity
- Ensure backend WebSocket server is running
- Check browser console for connection errors

### Circular Dependencies Not Showing
- Verify `circularDependencies` data is provided
- Check that `highlightCycles` is enabled
- Ensure nodes have `inCycle` property set

## Support

For issues or questions:
1. Check this README
2. Review test files for usage examples
3. Check component source code comments
4. File an issue in the project repository
