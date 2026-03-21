'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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
  ExternalLink,
} from 'lucide-react';
import { useProjects, useProjectAnalytics } from '@/hooks/useProjects';
import type { Project } from '@/hooks/useProjects';

// Architecture card per project
function ProjectArchCard({ project }: { project: Project }) {
  const router = useRouter();
  const { data: analytics, isLoading } = useProjectAnalytics(project.id);

  const healthMetrics = analytics?.metrics || null;
  const depStats = analytics?.dependency_stats || null;

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthLabel = (score: number) => {
    if (score >= 80) return 'Healthy';
    if (score >= 60) return 'Warning';
    return 'Critical';
  };

  const getHealthBadgeVariant = (score: number) => {
    if (score >= 80) return 'success' as const;
    if (score >= 60) return 'warning' as const;
    return 'destructive' as const;
  };

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push(`/projects/${project.id}`)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Network className="h-5 w-5" />
              {project.name}
            </CardTitle>
            <CardDescription>
              {project.github_repo_url ? (
                <span className="flex items-center gap-1">
                  {project.github_repo_url.replace('https://github.com/', '')}
                </span>
              ) : (
                '未关联仓库'
              )}
            </CardDescription>
          </div>
          {healthMetrics ? (
            <Badge variant={getHealthBadgeVariant(healthMetrics.architecture_health)}>
              {getHealthLabel(healthMetrics.architecture_health)}
            </Badge>
          ) : (
            <Badge variant="secondary">分析中</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ) : healthMetrics ? (
          <div className="space-y-4">
            {/* Health Score Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className={`text-xl font-bold ${getHealthColor(healthMetrics.architecture_health)}`}>
                  {healthMetrics.architecture_health}%
                </p>
                <p className="text-xs text-muted-foreground">架构健康</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className={`text-xl font-bold ${getHealthColor(healthMetrics.code_quality)}`}>
                  {healthMetrics.code_quality}%
                </p>
                <p className="text-xs text-muted-foreground">代码质量</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className={`text-xl font-bold ${getHealthColor(healthMetrics.security_rating)}`}>
                  {healthMetrics.security_rating}%
                </p>
                <p className="text-xs text-muted-foreground">安全评分</p>
              </div>
              <div className="text-center p-3 bg-muted rounded-lg">
                <p className={`text-xl font-bold ${getHealthColor(healthMetrics.test_coverage)}`}>
                  {healthMetrics.test_coverage}%
                </p>
                <p className="text-xs text-muted-foreground">测试覆盖</p>
              </div>
            </div>

            {/* Dependency Stats */}
            {depStats && (
              <div className="flex items-center gap-4 text-sm">
                <span className="flex items-center gap-1">
                  <Code className="h-3 w-3" />
                  {depStats.total} 依赖
                </span>
                {depStats.circular > 0 && (
                  <span className="text-red-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {depStats.circular} 循环
                  </span>
                )}
                {depStats.outdated > 0 && (
                  <span className="text-yellow-600 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {depStats.outdated} 过时
                  </span>
                )}
              </div>
            )}

            {/* Language */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <GitBranch className="h-3 w-3" />
              语言: {project.language || 'Unknown'}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <Activity className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">分析中...</p>
              <p className="text-xs text-muted-foreground mt-1">首次分析可能需要一些时间</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function ArchitecturePage() {
  const { data: projects = [], isLoading } = useProjects();
  const projectList: Project[] = Array.isArray(projects) ? projects : [];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Network className="h-8 w-8" />
              Architecture Analysis
            </h1>
            <p className="text-muted-foreground mt-1">
              Analyze and monitor code architecture health across all projects
            </p>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">总项目数</p>
                <p className="text-2xl font-bold">{projectList.length}</p>
              </div>
              <Network className="h-8 w-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">已关联仓库</p>
                <p className="text-2xl font-bold">
                  {projectList.filter(p => p.github_repo_url).length}
                </p>
              </div>
              <GitBranch className="h-8 w-8 text-muted-foreground" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">活跃项目</p>
                <p className="text-2xl font-bold">
                  {projectList.filter(p => p.is_active).length}
                </p>
              </div>
              <Activity className="h-8 w-8 text-muted-foreground" />
            </div>
          </Card>
        </div>

        {/* Project Architecture Cards */}
        {isLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        ) : projectList.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Network className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">暂无项目</h3>
              <p className="text-sm text-muted-foreground">
                请先在项目页面中添加项目以开始架构分析
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {projectList.map((project) => (
              <ProjectArchCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
