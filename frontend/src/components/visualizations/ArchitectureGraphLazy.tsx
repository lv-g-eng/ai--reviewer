'use client';

/**
 * Lazy-loaded wrapper for ArchitectureGraph
 * 
 * This component implements lazy loading for the architecture graph
 * visualization component, reducing initial bundle size.
 * 
 * Requirements: 10.9
 */

import dynamic from 'next/dynamic';
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

// Lazy load the ArchitectureGraph component
const ArchitectureGraph = dynamic(
  () => import('./ArchitectureGraph'),
  {
    loading: () => (
      <Card className="w-full">
        <CardContent className="p-8">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Loading architecture graph...
            </p>
          </div>
        </CardContent>
      </Card>
    ),
    ssr: false,
  }
);

export default ArchitectureGraph;
