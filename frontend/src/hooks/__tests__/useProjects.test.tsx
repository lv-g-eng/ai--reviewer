/**
 * Unit tests for useProjects hooks
 * Tests React Query hooks for project management
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProjects, useProject, useSyncProject, useCreateProject, useDeleteProject } from '../useProjects';
import { apiClient } from '@/lib/api-client';
import type { ReactNode } from 'react';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

const mockProject = {
  id: '1',
  name: 'Test Project',
  description: 'Test Description',
  github_repo_url: 'https://github.com/test/repo',
  owner_id: 'user1',
  language: 'TypeScript',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

describe('useProjects', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch all projects successfully', async () => {
    const projects = [mockProject];
    mockApiClient.get.mockResolvedValueOnce(projects);

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(projects);
    expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/rbac/projects');
  });

  it('should handle fetch error', async () => {
    const error = new Error('Failed to fetch');
    mockApiClient.get.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeTruthy();
  });

  it('should show loading state initially', () => {
    mockApiClient.get.mockImplementation(() => new Promise(() => {}));

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);
  });
});

describe('useProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch single project successfully', async () => {
    mockApiClient.get.mockResolvedValueOnce(mockProject);

    const { result } = renderHook(() => useProject('1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockProject);
    expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/rbac/projects/1');
  });

  it('should not fetch when projectId is empty', () => {
    const { result } = renderHook(() => useProject(''), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe('idle');
    expect(mockApiClient.get).not.toHaveBeenCalled();
  });

  it('should handle 404 error', async () => {
    const error = new Error('Project not found');
    mockApiClient.get.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useProject('999'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useSyncProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should sync project successfully', async () => {
    mockApiClient.post.mockResolvedValueOnce({ success: true });

    const { result } = renderHook(() => useSyncProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApiClient.post).toHaveBeenCalledWith('/github/projects/1/sync');
  });

  it('should handle sync error', async () => {
    const error = new Error('Sync failed');
    mockApiClient.post.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useSyncProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isError).toBe(true));
  });

  it('should show pending state during sync', async () => {
    mockApiClient.post.mockImplementation(() => new Promise(() => {}));

    const { result } = renderHook(() => useSyncProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isPending).toBe(true));
  });
});

describe('useCreateProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should create project successfully', async () => {
    const newProject = {
      name: 'New Project',
      description: 'New Description',
      github_repo_url: 'https://github.com/test/new',
    };

    mockApiClient.post.mockResolvedValueOnce({ ...mockProject, ...newProject });

    const { result } = renderHook(() => useCreateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate(newProject);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/rbac/projects', newProject);
  });

  it('should handle validation error', async () => {
    const error = new Error('Invalid project data');
    mockApiClient.post.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useCreateProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ name: '' });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

describe('useDeleteProject', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should delete project successfully', async () => {
    mockApiClient.delete.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApiClient.delete).toHaveBeenCalledWith('/api/v1/rbac/projects/1');
  });

  it('should handle delete error', async () => {
    const error = new Error('Delete failed');
    mockApiClient.delete.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useDeleteProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isError).toBe(true));
  });

  it('should handle 403 forbidden error', async () => {
    const error = new Error('Forbidden');
    mockApiClient.delete.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useDeleteProject(), {
      wrapper: createWrapper(),
    });

    result.current.mutate('1');

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
