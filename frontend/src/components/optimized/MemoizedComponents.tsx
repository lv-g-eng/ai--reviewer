/**
 * Memoized Components for Performance Optimization
 * 
 * This file contains React.memo optimized components to prevent
 * unnecessary re-renders and improve performance.
 */

import React, { memo, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

// Memoized project card component
interface ProjectCardProps {
  project: {
    id: number;
    name: string;
    description?: string;
    status: 'active' | 'inactive' | 'archived';
    owner_id: number;
    created_at: string;
    updated_at: string;
  };
  onSelect?: (projectId: number) => void;
  onEdit?: (projectId: number) => void;
  onDelete?: (projectId: number) => void;
}

export const MemoizedProjectCard = memo<ProjectCardProps>(({ 
  project, 
  onSelect, 
  onEdit, 
  onDelete 
}) => {
  const handleSelect = useCallback(() => {
    onSelect?.(project.id);
  }, [onSelect, project.id]);

  const handleEdit = useCallback(() => {
    onEdit?.(project.id);
  }, [onEdit, project.id]);

  const handleDelete = useCallback(() => {
    onDelete?.(project.id);
  }, [onDelete, project.id]);

  const statusColor = useMemo(() => {
    switch (project.status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-yellow-100 text-yellow-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, [project.status]);

  const formattedDate = useMemo(() => {
    return new Date(project.updated_at).toLocaleDateString();
  }, [project.updated_at]);

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={handleSelect}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold truncate">
            {project.name}
          </CardTitle>
          <Badge className={statusColor}>
            {project.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {project.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {project.description}
          </p>
        )}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Updated {formattedDate}</span>
          <div className="flex space-x-2">
            <Button variant="ghost" size="sm" onClick={handleEdit}>
              Edit
            </Button>
            <Button variant="ghost" size="sm" onClick={handleDelete}>
              Delete
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

MemoizedProjectCard.displayName = 'MemoizedProjectCard';

// Memoized review item component
interface ReviewItemProps {
  review: {
    id: number;
    title: string;
    status: 'pending' | 'in_progress' | 'completed' | 'rejected';
    score: number;
    created_at: string;
    findings: Array<{
      type: 'error' | 'warning' | 'info' | 'suggestion';
      severity: 'low' | 'medium' | 'high' | 'critical';
    }>;
  };
  onSelect?: (reviewId: number) => void;
}

export const MemoizedReviewItem = memo<ReviewItemProps>(({ review, onSelect }) => {
  const handleSelect = useCallback(() => {
    onSelect?.(review.id);
  }, [onSelect, review.id]);

  const statusColor = useMemo(() => {
    switch (review.status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }, [review.status]);

  const scoreColor = useMemo(() => {
    if (review.score >= 80) return 'text-green-600';
    if (review.score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  }, [review.score]);

  const criticalFindings = useMemo(() => {
    return review.findings.filter(f => f.severity === 'critical').length;
  }, [review.findings]);

  const formattedDate = useMemo(() => {
    return new Date(review.created_at).toLocaleDateString();
  }, [review.created_at]);

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={handleSelect}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold truncate">{review.title}</h3>
          <Badge className={statusColor}>
            {review.status.replace('_', ' ')}
          </Badge>
        </div>
        
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              Score: <span className={`font-semibold ${scoreColor}`}>{review.score}</span>
            </div>
            {criticalFindings > 0 && (
              <Badge variant="destructive" className="text-xs">
                {criticalFindings} critical
              </Badge>
            )}
          </div>
          <span className="text-xs text-gray-500">{formattedDate}</span>
        </div>

        <Progress value={review.score} className="h-2" />
      </CardContent>
    </Card>
  );
});

MemoizedReviewItem.displayName = 'MemoizedReviewItem';

// Memoized statistics card
interface StatsCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease';
  };
  icon?: React.ReactNode;
}

export const MemoizedStatsCard = memo<StatsCardProps>(({ 
  title, 
  value, 
  change, 
  icon 
}) => {
  const changeColor = useMemo(() => {
    if (!change) return '';
    return change.type === 'increase' ? 'text-green-600' : 'text-red-600';
  }, [change]);

  const formattedValue = useMemo(() => {
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return value;
  }, [value]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formattedValue}</div>
        {change && (
          <p className={`text-xs ${changeColor}`}>
            {change.type === 'increase' ? '+' : '-'}{Math.abs(change.value)}% from last month
          </p>
        )}
      </CardContent>
    </Card>
  );
});

MemoizedStatsCard.displayName = 'MemoizedStatsCard';

// Memoized library item
interface LibraryItemProps {
  library: {
    id: number;
    name: string;
    version: string;
    description?: string;
    security_score: number;
    popularity_score: number;
    maintenance_score: number;
  };
  onSelect?: (libraryId: number) => void;
}

export const MemoizedLibraryItem = memo<LibraryItemProps>(({ library, onSelect }) => {
  const handleSelect = useCallback(() => {
    onSelect?.(library.id);
  }, [onSelect, library.id]);

  const overallScore = useMemo(() => {
    return Math.round((library.security_score + library.popularity_score + library.maintenance_score) / 3);
  }, [library.security_score, library.popularity_score, library.maintenance_score]);

  const scoreColor = useMemo(() => {
    if (overallScore >= 80) return 'text-green-600';
    if (overallScore >= 60) return 'text-yellow-600';
    return 'text-red-600';
  }, [overallScore]);

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={handleSelect}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="font-semibold">{library.name}</h3>
            <p className="text-sm text-gray-600">v{library.version}</p>
          </div>
          <div className="text-right">
            <div className={`text-lg font-bold ${scoreColor}`}>
              {overallScore}
            </div>
            <div className="text-xs text-gray-500">Overall Score</div>
          </div>
        </div>

        {library.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {library.description}
          </p>
        )}

        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center">
            <div className="font-semibold">{library.security_score}</div>
            <div className="text-gray-500">Security</div>
          </div>
          <div className="text-center">
            <div className="font-semibold">{library.popularity_score}</div>
            <div className="text-gray-500">Popularity</div>
          </div>
          <div className="text-center">
            <div className="font-semibold">{library.maintenance_score}</div>
            <div className="text-gray-500">Maintenance</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

MemoizedLibraryItem.displayName = 'MemoizedLibraryItem';