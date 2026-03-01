'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { MainLayout } from '@/components/layout/main-layout'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Plus, 
  Search, 
  Grid3x3, 
  List, 
  GitBranch,
  Clock,
  AlertTriangle,
  CheckCircle,
  Settings
} from 'lucide-react'
import { useProjects } from '@/hooks/useProjects'
import { AddProjectModal } from '@/components/projects/add-project-modal'
import { useToast } from '@/hooks/use-toast'

function ProjectsPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const { data: projects = [], isLoading } = useProjects()
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Handle GitHub connection success/error from URL params
  useEffect(() => {
    const githubConnected = searchParams.get('github_connected')
    const error = searchParams.get('error')
    const errorDescription = searchParams.get('error_description')
    const errorDetail = searchParams.get('error_detail')

    if (githubConnected === 'true') {
      console.log('[Projects Page] GitHub connected successfully')
      toast({
        title: 'GitHub Connected',
        description: 'Your GitHub account has been connected successfully',
      })
      // Reopen the modal to continue adding project
      setShowCreateModal(true)
    } else if (error) {
      console.error('[Projects Page] GitHub connection error:', error)
      console.error('[Projects Page] Error detail:', errorDetail || errorDescription)
      
      // Show detailed error message
      const errorMsg = errorDetail || errorDescription || 'Failed to connect GitHub account'
      
      toast({
        variant: 'destructive',
        title: 'GitHub Connection Failed',
        description: errorMsg,
        duration: 10000, // Show for 10 seconds
      })
    }

    // Clean up URL params
    if (githubConnected || error) {
      const url = new URL(window.location.href)
      url.searchParams.delete('github_connected')
      url.searchParams.delete('error')
      url.searchParams.delete('error_description')
      url.searchParams.delete('error_detail')
      window.history.replaceState({}, '', url.toString())
    }
  }, [searchParams, toast])

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getHealthScoreBadge = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'destructive'
  }

  const filteredProjects = projects
    .filter(project => {
      const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (project.description?.toLowerCase() || '').includes(searchTerm.toLowerCase())
      return matchesSearch
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'recent':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        default:
          return 0
      }
    })

  return (
    <MainLayout>
      <div className="space-y-6" role="main" aria-labelledby="projects-title">
        <PageHeader
          title="Projects"
          description="Manage and monitor your code repositories"
          actions={
            <Button onClick={() => setShowCreateModal(true)} aria-label="Add new project">
              <Plus className="mr-2 h-4 w-4" aria-hidden="true" />
              Add Project
            </Button>
          }
        />

        <AddProjectModal 
          open={showCreateModal} 
          onClose={() => setShowCreateModal(false)} 
        />

        {/* Filters and Controls */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4" role="search" aria-label="Project filters">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <Input
                    placeholder="Search projects..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9"
                    aria-label="Search projects by name or description"
                  />
                </div>
              </div>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full md:w-[180px]" aria-label="Sort projects by">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="recent">Recently Updated</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex gap-2" role="group" aria-label="View mode">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                  aria-label="Grid view"
                  aria-pressed={viewMode === 'grid'}
                >
                  <Grid3x3 className="h-4 w-4" aria-hidden="true" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                  aria-label="List view"
                  aria-pressed={viewMode === 'list'}
                >
                  <List className="h-4 w-4" aria-hidden="true" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Projects Grid/List */}
        {isLoading ? (
          <div className={viewMode === 'grid' ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3' : 'space-y-4'}>
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <GitBranch className="h-12 w-12 text-muted-foreground mb-4" aria-hidden="true" />
              <h3 className="text-lg font-semibold mb-2">No projects found</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {searchTerm ? 'Try adjusting your search' : 'Get started by adding your first project'}
              </p>
              <Button onClick={() => setShowCreateModal(true)} aria-label="Add your first project">
                <Plus className="mr-2 h-4 w-4" aria-hidden="true" />
                Add Project
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div 
            className={viewMode === 'grid' ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3' : 'space-y-4'}
            role="list"
            aria-label="Projects list"
          >
            {filteredProjects.map((project) => (
              <Card 
                key={project.id} 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/projects/${project.id}`)}
                role="listitem"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    router.push(`/projects/${project.id}`);
                  }
                }}
                aria-label={`Project: ${project.name}`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{project.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {project.description || 'No description'}
                      </CardDescription>
                    </div>
                    <Badge variant="success">
                      Active
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <GitBranch className="mr-2 h-4 w-4" aria-hidden="true" />
                    <span className="truncate">{project.github_repo_url || 'No repository'}</span>
                  </div>

                  {project.language && (
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{project.language}</Badge>
                    </div>
                  )}

                  <div className="flex items-center text-xs text-muted-foreground pt-2 border-t">
                    <Clock className="mr-1 h-3 w-3" aria-hidden="true" />
                    <time dateTime={project.updated_at}>
                      Updated: {new Date(project.updated_at).toLocaleDateString()}
                    </time>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      router.push(`/projects/${project.id}`)
                    }}
                    aria-label={`View details for ${project.name}`}
                  >
                    View Details
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      router.push(`/projects/${project.id}/settings`)
                    }}
                    aria-label={`Settings for ${project.name}`}
                  >
                    <Settings className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  )
}

export default function ProjectsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProjectsPageContent />
    </Suspense>
  )
}
