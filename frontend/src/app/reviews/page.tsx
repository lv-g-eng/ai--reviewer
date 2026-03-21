'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/main-layout';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Search,
  GitPullRequest,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Activity,
  ExternalLink,
} from 'lucide-react';
import { useProjects, useProjectPullRequests } from '@/hooks/useProjects';
import type { Project, PullRequest } from '@/hooks/useProjects';

// Component to render Pull Request list for a project
function ProjectPRList({ project }: { project: Project }) {
  const router = useRouter();
  const { data: pullRequestsData = [], isLoading } = useProjectPullRequests(project.id, 'all');
  const pullRequests: PullRequest[] = Array.isArray(pullRequestsData) ? pullRequestsData : [];

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (pullRequests.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground text-sm">
        此项目暂无 Pull Request
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
      case 'merged':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'rejected':
      case 'closed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'analyzing':
        return <Activity className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'approved':
      case 'merged':
        return 'success' as const;
      case 'rejected':
      case 'closed':
        return 'destructive' as const;
      case 'analyzing':
        return 'default' as const;
      default:
        return 'outline' as const;
    }
  };

  return (
    <div className="space-y-3">
      {pullRequests.map((pr) => (
        <div
          key={pr.id}
          className="flex items-start justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
          onClick={() => router.push(`/projects/${project.id}`)}
        >
          <div className="flex items-start gap-3 flex-1">
            {getStatusIcon(pr.status)}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-sm font-semibold truncate">
                  PR #{pr.github_pr_number}: {pr.title}
                </h4>
                <Badge variant={getStatusBadgeVariant(pr.status)}>
                  {pr.status}
                </Badge>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>{pr.files_changed} files</span>
                <span className="text-green-600">+{pr.lines_added}</span>
                <span className="text-red-600">-{pr.lines_deleted}</span>
                <span>{pr.branch_name}</span>
                <span>
                  <Clock className="inline h-3 w-3 mr-1" />
                  {new Date(pr.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          {pr.risk_score !== null && pr.risk_score !== undefined && (
            <Badge
              variant={pr.risk_score > 70 ? 'destructive' : pr.risk_score > 40 ? 'warning' : 'success'}
            >
              Risk: {pr.risk_score}
            </Badge>
          )}
        </div>
      ))}
    </div>
  );
}

export default function ReviewsPage() {
  const { data: projects = [], isLoading } = useProjects();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredProjects = useMemo(() => {
    return (Array.isArray(projects) ? projects : []).filter((project: Project) => {
      if (searchTerm) {
        return project.name.toLowerCase().includes(searchTerm.toLowerCase());
      }
      return true;
    });
  }, [projects, searchTerm]);

  return (
    <MainLayout>
      <div className="space-y-6">
        <PageHeader
          title="Pull Requests"
          description="查看和管理所有项目的 Pull Request 审查"
        />

        {/* Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索项目..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="状态筛选" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部状态</SelectItem>
              <SelectItem value="pending">待审查</SelectItem>
              <SelectItem value="approved">已通过</SelectItem>
              <SelectItem value="rejected">已拒绝</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-40 w-full" />
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <GitPullRequest className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">暂无项目</h3>
              <p className="text-sm text-muted-foreground">
                请先在项目页面中添加项目
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {filteredProjects.map((project: Project) => (
              <Card key={project.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <GitPullRequest className="h-5 w-5" />
                        {project.name}
                      </CardTitle>
                      <CardDescription>
                        {project.github_repo_url ? (
                          <a
                            href={project.github_repo_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 hover:underline"
                          >
                            {project.github_repo_url.replace('https://github.com/', '')}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          '未关联仓库'
                        )}
                      </CardDescription>
                    </div>
                    <Badge variant={project.language ? 'outline' : 'secondary'}>
                      {project.language || 'Unknown'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <ProjectPRList project={project} />
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
