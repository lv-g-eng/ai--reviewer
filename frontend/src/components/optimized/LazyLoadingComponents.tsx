/**
 * Optimized Lazy Loading Components
 * 
 * Advanced lazy loading with error boundaries, loading states,
 * and intelligent preloading for better user experience.
 */

import React, { Suspense, lazy, useEffect, useState, useCallback } from 'react';
import { ErrorBoundary } from '@/components/ErrorBoundary';

// Lazy load heavy visualization components
// Note: These components are commented out as they don't exist yet
// Uncomment when the components are implemented

/*
const D3ArchitectureGraph = lazy(() => 
  import('../visualizations/D3ArchitectureGraph').then(module => ({
    default: module.D3ArchitectureGraph
  }))
);

const ReactFlowDiagram = lazy(() => 
  import('../visualizations/ReactFlowDiagram').then(module => ({
    default: module.ReactFlowDiagram
  }))
);

const RechartsAnalytics = lazy(() => 
  import('../analytics/RechartsAnalytics').then(module => ({
    default: module.RechartsAnalytics
  }))
);

const CodeEditor = lazy(() => 
  import('../editor/CodeEditor').then(module => ({
    default: module.CodeEditor
  }))
);
*/

// Loading components with skeleton UI
const GraphLoadingSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="h-96 bg-gray-200 rounded-lg mb-4"></div>
    <div className="flex space-x-4">
      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
    </div>
  </div>
);

const AnalyticsLoadingSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
      ))}
    </div>
    <div className="h-64 bg-gray-200 rounded-lg"></div>
  </div>
);

const EditorLoadingSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="h-8 bg-gray-200 rounded mb-2"></div>
    <div className="h-96 bg-gray-200 rounded-lg"></div>
  </div>
);

// Error fallback components
const GraphErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({ 
  error, 
  resetErrorBoundary 
}) => (
  <div className="p-6 border border-red-200 rounded-lg bg-red-50">
    <h3 className="text-lg font-semibold text-red-800 mb-2">
      Failed to load visualization
    </h3>
    <p className="text-red-600 mb-4">
      {error.message || 'An error occurred while loading the graph component.'}
    </p>
    <button
      onClick={resetErrorBoundary}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    >
      Try Again
    </button>
  </div>
);

const AnalyticsErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({ 
  error, 
  resetErrorBoundary 
}) => (
  <div className="p-6 border border-red-200 rounded-lg bg-red-50">
    <h3 className="text-lg font-semibold text-red-800 mb-2">
      Failed to load analytics
    </h3>
    <p className="text-red-600 mb-4">
      {error.message || 'An error occurred while loading the analytics component.'}
    </p>
    <button
      onClick={resetErrorBoundary}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    >
      Retry
    </button>
  </div>
);

// Preloading hook for intelligent component preloading
// Commented out until components are implemented
/*
const useComponentPreloader = () => {
  const [preloadedComponents, setPreloadedComponents] = useState<Set<string>>(new Set());
  
  const preloadComponent = useCallback(async (componentName: string) => {
    if (preloadedComponents.has(componentName)) {
      return;
    }
    
    try {
      switch (componentName) {
        case 'D3ArchitectureGraph':
          await import('../visualizations/D3ArchitectureGraph');
          break;
        case 'ReactFlowDiagram':
          await import('../visualizations/ReactFlowDiagram');
          break;
        case 'RechartsAnalytics':
          await import('../analytics/RechartsAnalytics');
          break;
        case 'CodeEditor':
          await import('../editor/CodeEditor');
          break;
      }
      
      setPreloadedComponents(prev => new Set([...prev, componentName]));
    } catch (error) {
      console.warn(`Failed to preload component ${componentName}:`, error);
    }
  }, [preloadedComponents]);
  
  return { preloadComponent, preloadedComponents };
};
*/

// Placeholder hook
const useComponentPreloader = () => {
  const preloadComponent = useCallback(async (componentName: string) => {
    console.log(`Preload requested for ${componentName} but components not yet implemented`);
  }, []);
  
  return { preloadComponent, preloadedComponents: new Set<string>() };
};

// Optimized lazy component wrappers
// Commented out until components are implemented
/*
interface LazyArchitectureGraphProps {
  data: any;
  onNodeClick?: (node: any) => void;
  preload?: boolean;
}

export const LazyArchitectureGraph: React.FC<LazyArchitectureGraphProps> = ({ 
  preload = false, 
  ...props 
}) => {
  const { preloadComponent } = useComponentPreloader();
  
  useEffect(() => {
    if (preload) {
      preloadComponent('D3ArchitectureGraph');
    }
  }, [preload, preloadComponent]);
  
  return (
    <ErrorBoundary FallbackComponent={GraphErrorFallback}>
      <Suspense fallback={<GraphLoadingSkeleton />}>
        <D3ArchitectureGraph {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

interface LazyFlowDiagramProps {
  nodes: any[];
  edges: any[];
  onNodesChange?: (changes: any[]) => void;
  preload?: boolean;
}

export const LazyFlowDiagram: React.FC<LazyFlowDiagramProps> = ({ 
  preload = false, 
  ...props 
}) => {
  const { preloadComponent } = useComponentPreloader();
  
  useEffect(() => {
    if (preload) {
      preloadComponent('ReactFlowDiagram');
    }
  }, [preload, preloadComponent]);
  
  return (
    <ErrorBoundary FallbackComponent={GraphErrorFallback}>
      <Suspense fallback={<GraphLoadingSkeleton />}>
        <ReactFlowDiagram {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};
*/

interface LazyAnalyticsProps {
  data: any[];
  chartType?: 'line' | 'bar' | 'pie' | 'area';
  preload?: boolean;
}

export const LazyAnalytics: React.FC<LazyAnalyticsProps> = ({ 
  preload = false, 
  ...props 
}) => {
  const { preloadComponent } = useComponentPreloader();
  
  useEffect(() => {
    if (preload) {
      preloadComponent('RechartsAnalytics');
    }
  }, [preload, preloadComponent]);
  
  return (
    <ErrorBoundary FallbackComponent={AnalyticsErrorFallback}>
      <Suspense fallback={<AnalyticsLoadingSkeleton />}>
        <RechartsAnalytics {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

interface LazyCodeEditorProps {
  code: string;
  language: string;
  onChange?: (code: string) => void;
  preload?: boolean;
}

export const LazyCodeEditor: React.FC<LazyCodeEditorProps> = ({ 
  preload = false, 
  ...props 
}) => {
  const { preloadComponent } = useComponentPreloader();
  
  useEffect(() => {
    if (preload) {
      preloadComponent('CodeEditor');
    }
  }, [preload, preloadComponent]);
  
  return (
    <ErrorBoundary FallbackComponent={AnalyticsErrorFallback}>
      <Suspense fallback={<EditorLoadingSkeleton />}>
        <CodeEditor {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

// Intelligent preloader component
interface ComponentPreloaderProps {
  components: string[];
  trigger?: 'hover' | 'visible' | 'idle';
  delay?: number;
}

export const ComponentPreloader: React.FC<ComponentPreloaderProps> = ({
  components,
  trigger = 'idle',
  delay = 2000
}) => {
  const { preloadComponent } = useComponentPreloader();
  
  useEffect(() => {
    if (trigger === 'idle') {
      const timeoutId = setTimeout(() => {
        components.forEach(component => {
          preloadComponent(component);
        });
      }, delay);
      
      return () => clearTimeout(timeoutId);
    }
  }, [components, trigger, delay, preloadComponent]);
  
  return null; // This component doesn't render anything
};

// Route-based preloader
export const RoutePreloader: React.FC<{ route: string }> = ({ route }) => {
  const componentMap: Record<string, string[]> = {
    '/dashboard': ['RechartsAnalytics'],
    '/projects': ['D3ArchitectureGraph', 'ReactFlowDiagram'],
    '/analysis': ['D3ArchitectureGraph', 'RechartsAnalytics'],
    '/editor': ['CodeEditor'],
    '/visualization': ['D3ArchitectureGraph', 'ReactFlowDiagram']
  };
  
  const componentsToPreload = componentMap[route] || [];
  
  return (
    <ComponentPreloader 
      components={componentsToPreload}
      trigger="idle"
      delay={1000}
    />
  );
};

// Performance monitoring hook
export const useComponentLoadingMetrics = () => {
  const [metrics, setMetrics] = useState<Record<string, number>>({});
  
  const recordLoadTime = useCallback((componentName: string, loadTime: number) => {
    setMetrics(prev => ({
      ...prev,
      [componentName]: loadTime
    }));
    
    // Log to analytics if available
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'component_load_time', {
        component_name: componentName,
        load_time: loadTime,
        event_category: 'performance'
      });
    }
  }, []);
  
  return { metrics, recordLoadTime };
};