/**
 * Lazy-loaded visualization components
 * 
 * This module exports lazy-loaded versions of heavy visualization components
 * to reduce initial bundle size and improve performance.
 * 
 * Usage:
 * ```tsx
 * import { DependencyGraphVisualizationLazy } from '@/components/visualizations/lazy';
 * 
 * function MyComponent() {
 *   return <DependencyGraphVisualizationLazy projectId="123" />;
 * }
 * ```
 * 
 * Requirements: 10.9
 */

export { default as DependencyGraphVisualizationLazy } from './DependencyGraphVisualizationLazy';
export { default as ArchitectureGraphLazy } from './ArchitectureGraphLazy';
export { default as Neo4jGraphVisualizationLazy } from './Neo4jGraphVisualizationLazy';
