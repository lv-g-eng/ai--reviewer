/**
 * Optimized Query Hook
 * 
 * Advanced query optimization with intelligent caching, request batching,
 * field selection, and performance monitoring.
 */

import { useQuery, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { useCallback, useMemo, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api-client-enhanced';

interface OptimizedQueryOptions<T> {
  queryKey: string[];
  queryFn?: () => Promise<T>;
  endpoint?: string;
  fields?: string[];
  include?: string[];
  exclude?: string[];
  staleTime?: number;
  cacheTime?: number;
  enabled?: boolean;
  priority?: 'high' | 'normal' | 'low';
  realtime?: boolean;
  batchable?: boolean;
  retryOnMount?: boolean;
  backgroundRefetch?: boolean;
  optimisticUpdates?: boolean;
}

interface QueryMetrics {
  queryKey: string;
  duration: number;
  cacheHit: boolean;
  dataSize: number;
  timestamp: number;
  source: 'cache' | 'network' | 'background';
}

// Global query metrics store
const queryMetrics: QueryMetrics[] = [];
const MAX_METRICS = 1000;

// Request deduplication map
const pendingRequests = new Map<string, Promise<any>>();

// Batch request queue
interface BatchRequest {
  queryKey: string[];
  resolve: (data: any) => void;
  reject: (error: any) => void;
  timestamp: number;
}

const batchQueue = new Map<string, BatchRequest[]>();
let batchTimeout: NodeJS.Timeout | null = null;

// Execute batch requests
const executeBatch = async (endpoint: string) => {
  const requests = batchQueue.get(endpoint) || [];
  batchQueue.delete(endpoint);
  
  if (requests.length === 0) return;
  
  try {
    // Group requests by similar parameters
    const groupedRequests = groupBatchRequests(requests);
    
    for (const group of groupedRequests) {
      const batchPayload = group.map(req => ({
        queryKey: req.queryKey,
        timestamp: req.timestamp
      }));
      
      const results = await apiClient.post(`${endpoint}/batch`, batchPayload);
      
      // Resolve individual requests
      group.forEach((request, index) => {
        request.resolve(results[index]);
      }ueryClient]);

  return {
    ...query,
    optimisticUpdate,
    prefetch,
  };
}

// Specialized hooks for common use cases
export function useOptimizedProjects(params?: Record<string, any>) {
  return useOptimizedQuery('projects', {
    endpoint: '/api/v1/projects',
    params,
    staleTime: 2 * 60 * 1000, // 2 minutes for frequently changing data
    backgroundRefetch: true,
    optimisticUpdates: true,
  });
}

export function useOptimizedProject(projectId: string) {
  return useOptimizedQuery(['project', projectId], {
    endpoint: `/api/v1/projects/${projectId}`,
    staleTime: 5 * 60 * 1000, // 5 minutes for less frequently changing data
    enabled: !!projectId,
  });
}

export function useOptimizedReviews(projectId: string, params?: Record<string, any>) {
  return useOptimizedQuery(['reviews', projectId], {
    endpoint: `/api/v1/projects/${projectId}/reviews`,
    params,
    staleTime: 1 * 60 * 1000, // 1 minute for real-time data
    backgroundRefetch: true,
    enabled: !!projectId,
  });
}

export function useOptimizedLibraries(searchQuery?: string) {
  return useOptimizedQuery(['libraries', searchQuery || ''], {
    endpoint: '/api/v1/libraries',
    params: searchQuery ? { search: searchQuery } : undefined,
    staleTime: 10 * 60 * 1000, // 10 minutes for stable data
    enabled: !!searchQuery,
  });
}