/**
 * Project API hooks using React Query
 * Uses optimized API client with caching and retry logic
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client-optimized';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  github_repo_url: string;
  owner_id: string;
  language: string | null;
  created_at: string;
  updated_at: string;
}

export interface PullRequest {
  id: string;
  project_id: string;
  github_pr_number: number;
  title: string;
  description: string | null;
  branch_name: string;
  commit_sha: string;
  status: string;
  risk_score: number | null;
  files_changed: number;
  lines_added: number;
  lines_deleted: number;
  created_at: string;
  analyzed_at: string | null;
}

export interface ProjectMetrics {
  code_quality: number;
  security_rating: number;
  architecture_health: number;
  test_coverage: number;
  overall_health: number;
}

export interface ProjectAnalytics {
  project_id: string;
  metrics: ProjectMetrics;
  total_prs: number;
  reviewed_prs: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  medium_issues: number;
  low_issues: number;
  architecture_violations: number;
  recent_reviews: any[];
}

/**
 * Fetch all projects
 */
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      return apiClient.get<Project[]>('/rbac/projects');
    },
  });
}

/**
 * Fetch single project
 */
export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId],
    queryFn: async () => {
      return apiClient.get<Project>(`/rbac/projects/${projectId}`);
    },
    enabled: !!projectId,
  });
}

/**
 * Fetch project pull requests
 */
export function useProjectPullRequests(projectId: string, state: string = 'all') {
  return useQuery({
    queryKey: ['projects', projectId, 'pulls', state],
    queryFn: async () => {
      return apiClient.get(`/github/projects/${projectId}/pulls`, {
        params: { state },
      });
    },
    enabled: !!projectId,
  });
}

/**
 * Fetch project analytics (AI 审查数据)
 */
export function useProjectAnalytics(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'analytics'],
    queryFn: async () => {
      return apiClient.get<ProjectAnalytics>(`/projects/${projectId}/analytics`);
    },
    enabled: !!projectId,
  });
}

/**
 * Sync project with GitHub
 */
export function useSyncProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectId: string) => {
      return apiClient.post(`/github/projects/${projectId}/sync`);
    },
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}

/**
 * Create new project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Project>) => {
      return apiClient.post<Project>('/rbac/projects', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Delete project
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (projectId: string) => {
      await apiClient.delete(`/rbac/projects/${projectId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Fetch project branches for architecture visualization
 */
export function useProjectBranches(projectId: string) {
  return useQuery({
    queryKey: ['architecture', projectId, 'branches'],
    queryFn: async () => {
      return apiClient.get<BranchInfo[]>(`/architecture/${projectId}/branches`);
    },
    enabled: !!projectId,
  });
}

/**
 * Fetch branch architecture data
 */
export function useBranchArchitecture(projectId: string, branchId: string) {
  return useQuery({
    queryKey: ['architecture', projectId, 'branches', branchId],
    queryFn: async () => {
      return apiClient.get<BranchArchitecture>(`/architecture/${projectId}/branches/${branchId}/architecture`);
    },
    enabled: !!(projectId && branchId),
  });
}

/**
 * Trigger code review for a PR
 */
export function useTriggerCodeReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { pr_id: string; force?: boolean }) => {
      return apiClient.post('/code-review/trigger', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export interface BranchInfo {
  id: string;
  name: string;
  last_commit: string;
  last_commit_date: string;
  author: string;
  components_count: number;
  complexity: number;
  health_status: 'healthy' | 'warning' | 'critical';
  circular_dependencies: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  health: 'healthy' | 'warning' | 'critical';
  complexity: number;
  position: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  is_circular?: boolean;
}

export interface BranchArchitecture {
  branch_info: BranchInfo;
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: {
    total_components: number;
    total_dependencies: number;
    circular_dependencies: number;
    avg_complexity: number;
    violations_count: number;
    critical_violations: number;
    high_violations: number;
  };
}
