'use client'

import { useEffect, useState } from 'react'
import { RouteGuard } from '@/components/auth/RouteGuard'
import { MainLayout } from '@/components/layout/main-layout'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  FolderGit2,
  GitPullRequest,
  AlertTriangle,
  TrendingUp,
  Plus,
  Eye,
  Network
} from 'lucide-react'

import dynamic from 'next/dynamic'

const RecentActivity = dynamic(() => import('@/components/dashboard/RecentActivity').then(mod => mod.RecentActivity), {
  loading: () => <Skeleton className="h-[400px] w-full" />,
  ssr: false
})

const QuickActions = dynamic(() => import('@/components/dashboard/QuickActions').then(mod => mod.QuickActions), {
  loading: () => <Skeleton className="h-[300px] w-full" />,
  ssr: false
})

interface DashboardStats {
  totalProjects: number
  pendingReviews: number
  criticalIssues: number
  architectureHealthScore: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStats({
        totalProjects: 12,
        pendingReviews: 5,
        criticalIssues: 3,
        architectureHealthScore: 85,
      })
      setIsLoading(false)
    }, 1000)
  }, [])

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <RouteGuard>
      <MainLayout>
        <div className="space-y-6">
          <PageHeader
            title="Dashboard"
            description="Welcome back! Here's an overview of your projects and reviews."
            actions={
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Project
              </Button>
            }
          />

        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {isLoading ? (
            <>
              {[...Array(4)].map((_, i) => (
                <Card key={i}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-4" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-8 w-16 mb-2" />
                    <Skeleton className="h-3 w-32" />
                  </CardContent>
                </Card>
              ))}
            </>
          ) : (
            <>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Projects
                  </CardTitle>
                  <FolderGit2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.totalProjects}</div>
                  <p className="text-xs text-muted-foreground">
                    +2 from last month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Pending Reviews
                  </CardTitle>
                  <GitPullRequest className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.pendingReviews}</div>
                  <p className="text-xs text-muted-foreground">
                    Requires attention
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Critical Issues
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-destructive">
                    {stats?.criticalIssues}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Needs immediate action
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Architecture Health
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getHealthScoreColor(stats?.architectureHealthScore || 0)}`}>
                    {stats?.architectureHealthScore}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    +5% from last week
                  </p>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Recent Activity and Quick Actions - Lazy Loaded */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <RecentActivity isLoading={isLoading} />
          <QuickActions />
        </div>
      </div>
    </MainLayout>
    </RouteGuard>
  )
}
