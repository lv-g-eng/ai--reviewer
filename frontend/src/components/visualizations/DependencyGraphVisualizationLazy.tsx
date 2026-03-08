'use client';

/**
 * Lazy-loaded wrapper for DependencyGraphVisualization
 * 
 * This component implements lazy loading for the heavy dependency graph
 * visualization component, reducing initial bundle size.
 * 
 * Requirements: 10.9
 */

import dynamic from 'next/dynamic';
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

// Lazy load the DependencyGraphVisualization component
const DependencyGraphVisualization = dynamic(
  () => import('./DependencyGraphVisualization'),
  {
    loading: () => (
      <Card className="w-full">
        <CardContent className="p-8">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Loading dependency graph visualization...
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              This may take a moment for large graphs
            </p>
          </div>
        </CardContent>
      </Card>
    ),
    ssr: false, // Disable SSR for this component as it uses browser-only APIs
  }
);

interface DependencyGraphVisualizationLazyProps {
  projectId: string;
  analysisId?: string;
  className?: string;
  websocketUrl?: string;
}

export default function DependencyGraphVisualizationLazy(
  props: DependencyGraphVisualizationLazyProps
) {
  return <DependencyGraphVisualization {...props} />;
}
