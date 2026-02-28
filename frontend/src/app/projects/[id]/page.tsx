'use client'

import { useParams, useRouter } from 'next/navigation'
import { MainLayout } from '@/components/layout/main-layout'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  GitBranch,
  Settings,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  GitPullRequest,
  Activity,
  ArrowLeft,
  User
} from 'lucide-react'
import { useProject, useProjectPullRequests } from '@/hooks/useProjects'
import HealthMetrics from '@/components/projects/HealthMetrics'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string
  
  const { data: project, isLoading } = useProject(projectId)
  const { data: pullRequestsData = [] } = useProjectPullRequests(projectId)
  const pullRequests = Array.isArray(pullRequestsData) ? pullRequestsData : []

  // Mock health metrics - these would come from analysis results in production
  const healthMetrics = {
    codeQuality: 88,
    securityRating: 95,
    architectureHealth: 90,
    testCoverage: 75,
  }

  const overallHealth = Math.round(
    (healthMetrics.codeQuality + 
     healthMetrics.securityRating + 
     healthMetrics.architectureHealth + 
     healthMetrics.testCoverage) / 4
  )

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (isLoading) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-12 w-3/4" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      </MainLayout>
    )
  }

  if (!project) {
    return (
      <MainLayout>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Project not found</h3>
            <Button onClick={() => router.push('/projects')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Projects
            </Button>
          </CardContent>
        </Card>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <PageHeader
          title={project.name}
          description={project.description || 'No description'}
          actions={
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push('/projects')}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <Button onClick={() => router.push(`/projects/${project.id}/settings`)}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
            </div>
          }
        />

        {/* Project Overview Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Health</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getHealthScoreColor(overallHealth)}`}>
                {overallHealth}%
              </div>
              <p className="text-xs text-muted-foreground">
                Based on 4 metrics
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pull Requests</CardTitle>
              <GitPullRequest className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pullRequests.length}</div>
              <p className="text-xs text-muted-foreground">
                Total analyzed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Language</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{project.language || 'N/A'}</div>
              <p className="text-xs text-muted-foreground">
                Primary language
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Owner</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium truncate">{project.owner_id}</div>
              <p className="text-xs text-muted-foreground">
                Project owner
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabbed Content */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="reviews">Reviews</TabsTrigger>
            <TabsTrigger value="architecture">Architecture</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {/* Health Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Architectural Health Metrics</CardTitle>
                <CardDescription>Real-time analysis of code quality, security, and architecture</CardDescription>
              </CardHeader>
              <CardContent>
                <HealthMetrics {...healthMetrics} />
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Project Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Repository</p>
                    <div className="flex items-center mt-1">
                      <GitBranch className="mr-2 h-4 w-4" />
                      <p className="text-sm truncate">{project.github_repo_url || 'No repository'}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Status</p>
                    <Badge className="mt-1" variant="success">
                      Active
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Created</p>
                    <div className="flex items-center mt-1">
                      <Clock className="mr-2 h-4 w-4" />
                      <p className="text-sm">{new Date(project.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                    <div className="flex items-center mt-1">
                      <Clock className="mr-2 h-4 w-4" />
                      <p className="text-sm">{new Date(project.updated_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Analysis Results</CardTitle>
                  <CardDescription>Latest code review and analysis findings</CardDescription>
                </CardHeader>
                <CardContent>
                  {pullRequests.length > 0 ? (
                    <div className="space-y-4">
                      {pullRequests.slice(0, 3).map((pr: any) => (
                        <div key={pr.id} className="flex items-start space-x-4">
                          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <GitPullRequest className="h-5 w-5 text-primary" />
                          </div>
                          <div className="flex-1 space-y-1">
                            <p className="text-sm font-medium">
                              PR #{pr.github_pr_number}: {pr.title}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {pr.status} • {new Date(pr.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          {pr.risk_score && (
                            <Badge variant={pr.risk_score > 70 ? 'destructive' : pr.risk_score > 40 ? 'warning' : 'success'}>
                              Risk: {pr.risk_score}
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No analysis results yet</p>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest updates and changes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pullRequests.length > 0 ? (
                    pullRequests.slice(0, 5).map((pr: any) => (
                      <div key={pr.id} className="flex items-start space-x-4">
                        <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <CheckCircle className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="text-sm font-medium">
                            PR #{pr.github_pr_number}: {pr.title}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {pr.files_changed} files • +{pr.lines_added} -{pr.lines_deleted} • {new Date(pr.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant="success">{pr.status}</Badge>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No recent activity</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reviews">
            <Card>
              <CardHeader>
                <CardTitle>Pull Request Reviews</CardTitle>
                <CardDescription>Review history and pending reviews</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Pull request review list will be displayed here
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="architecture">
            <Card>
              <CardHeader>
                <CardTitle>Architecture Analysis</CardTitle>
                <CardDescription>Dependency graph and architectural insights</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Architecture visualization will be displayed here
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="metrics">
            <Card>
              <CardHeader>
                <CardTitle>Detailed Metrics</CardTitle>
                <CardDescription>Comprehensive quality and performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Detailed metrics and charts will be displayed here
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
