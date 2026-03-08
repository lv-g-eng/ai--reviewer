'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import MainLayout from '@/components/layout/main-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Network,
  GitBranch,
  AlertCircle,
  CheckCircle2,
  Clock,
  Code,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { useProjectBranches } from '@/hooks/useProjects';
import type { BranchInfo } from '@/hooks/useProjects';

export default function ArchitecturePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('project') || '';
  const [searchTerm, setSearchTerm] = useState('');

  const { data: branches = [], isLoading } = useProjectBranches(projectId);

  const filteredBranches = branches.filter((branch: BranchInfo) =>
    branch.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getHealthBadgeVariant = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'success' as const;
      case 'warning':
        return 'warning' as const;
      case 'critical':
        return 'destructive' as const;
      default:
        return 'default' as const;
    }
  };

  if (!projectId) {
    return (
      <MainLayout>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Project Selected</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Please select a project to view its architecture
            </p>
            <Button onClick={() => router.push('/projects')}>
              Go to Projects
            </Button>
          </CardContent>
        </Card>
      </MainLayout>
    );
  }

  if (isLoading) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-32 w-full" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-96 w-full" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Network className="h-8 w-8" />
              Architecture Visualization
            </h1>
            <p className="text-muted-foreground mt-1">
              View and analyze architecture for different branches
            </p>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Branches</CardTitle>
              <GitBranch className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{branches.length}</div>
              <p className="text-xs text-muted-foreground">Analyzed branches</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Healthy Branches</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {branches.filter((b: BranchInfo) => b.health_status === 'healthy').length}
              </div>
              <p className="text-xs text-muted-foreground">No critical issues</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Complexity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {branches.length > 0
                  ? Math.round(
                      branches.reduce((sum: number, b: BranchInfo) => sum + b.complexity, 0) /
                        branches.length
                    )
                  : 0}
              </div>
              <p className="text-xs text-muted-foreground">Across all branches</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Circular Dependencies</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {branches.reduce((sum: number, b: BranchInfo) => sum + b.circular_dependencies, 0)}
              </div>
              <p className="text-xs text-muted-foreground">Total detected</p>
            </CardContent>
          </Card>
        </div>

        {/* Search Bar */}
        <Card>
          <CardHeader>
            <CardTitle>Branches</CardTitle>
            <CardDescription>
              Click on a branch to view its architecture visualization
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <input
                type="text"
                placeholder="Search branches..."
                className="w-full px-4 py-2 border rounded-md"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Branches List */}
            {filteredBranches.length > 0 ? (
              <div className="space-y-4">
                {filteredBranches.map((branch: BranchInfo) => (
                  <Card key={branch.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <GitBranch className="h-5 w-5 text-primary" />
                          <h4 className="font-semibold text-lg">{branch.name}</h4>
                          <Badge variant={getHealthBadgeVariant(branch.health_status)}>
                            {branch.health_status}
                          </Badge>
                        </div>

                        <p className="text-sm text-muted-foreground mb-3">
                          {branch.last_commit}
                        </p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Components</p>
                            <p className="font-medium">{branch.components_count}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Complexity</p>
                            <p className="font-medium">{branch.complexity}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Circular Deps</p>
                            <p
                              className={`font-medium ${
                                branch.circular_dependencies > 0
                                  ? 'text-red-600'
                                  : 'text-green-600'
                              }`}
                            >
                              {branch.circular_dependencies}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Health</p>
                            <div className="flex items-center gap-1">
                              {getHealthIcon(branch.health_status)}
                            </div>
                          </div>
                        </div>

                        <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(branch.last_commit_date).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Code className="h-3 w-3" />
                            {branch.author}
                          </span>
                        </div>
                      </div>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => router.push(`/architecture/${branch.id}?project=${projectId}`)}
                      >
                        View Architecture
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <GitBranch className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Branches Found</h3>
                <p className="text-sm text-muted-foreground">
                  {searchTerm
                    ? 'Try adjusting your search term'
                    : 'Branches will appear here once they are analyzed'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}


