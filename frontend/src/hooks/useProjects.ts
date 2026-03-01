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
