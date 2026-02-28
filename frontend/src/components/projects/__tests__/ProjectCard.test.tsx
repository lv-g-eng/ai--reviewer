/**
 * Unit tests for ProjectCard component
 * Tests rendering, user interactions, and menu actions
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProjectCard from '../ProjectCard';
import { useSyncProject, useDeleteProject } from '@/hooks/useProjects';
import type { ReactNode } from 'react';

// Mock lucide-react
jest.mock('lucide-react');

// Mock Next.js Link
jest.mock('next/link', () => {
  return ({ children, href }: { children: ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

// Mock the hooks
jest.mock('@/hooks/useProjects', () => ({
  useSyncProject: jest.fn(),
  useDeleteProject: jest.fn(),
}));

const mockUseSyncProject = useSyncProject as jest.MockedFunction<typeof useSyncProject>;
const mockUseDeleteProject = useDeleteProject as jest.MockedFunction<typeof useDeleteProject>;

const mockProject = {
  id: '1',
  name: 'Test Project',
  description: 'Test project description',
  github_repo_url: 'https://github.com/test/repo',
  owner_id: 'user1',
  language: 'TypeScript',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

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

describe('ProjectCard', () => {
  const mockSyncMutate = jest.fn();
  const mockDeleteMutate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseSyncProject.mockReturnValue({
      mutate: mockSyncMutate,
      isPending: false,
    } as any);
    mockUseDeleteProject.mockReturnValue({
      mutate: mockDeleteMutate,
    } as any);
  });

  it('should render project information', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Test project description')).toBeInTheDocument();
    expect(screen.getByText('test/repo')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });

  it('should render "No description" when description is null', () => {
    const projectWithoutDesc = { ...mockProject, description: null };
    render(<ProjectCard project={projectWithoutDesc} />, { wrapper: createWrapper() });

    expect(screen.getByText('No description')).toBeInTheDocument();
  });

  it('should render project link with correct href', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const link = screen.getByText('Test Project').closest('a');
    expect(link).toHaveAttribute('href', '/projects/1');
  });

  it('should render GitHub repository link', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const githubLink = screen.getByText('test/repo').closest('a');
    expect(githubLink).toHaveAttribute('href', 'https://github.com/test/repo');
    expect(githubLink).toHaveAttribute('target', '_blank');
    expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('should display formatted update date', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    // Check that date is displayed (format may vary by locale)
    expect(screen.getByText(/1\/15\/2024/)).toBeInTheDocument();
  });

  it('should show menu when clicking more button', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    expect(screen.getByText('Sync with GitHub')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('should close menu when clicking outside', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    expect(screen.getByText('Sync with GitHub')).toBeInTheDocument();

    // Click the overlay
    const overlay = document.querySelector('.fixed.inset-0');
    fireEvent.click(overlay!);

    expect(screen.queryByText('Sync with GitHub')).not.toBeInTheDocument();
  });

  it('should call sync mutation when clicking Sync', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const syncButton = screen.getByText('Sync with GitHub');
    fireEvent.click(syncButton);

    expect(mockSyncMutate).toHaveBeenCalledWith('1');
  });

  it('should show spinning icon when syncing', () => {
    mockUseSyncProject.mockReturnValue({
      mutate: mockSyncMutate,
      isPending: true,
    } as any);

    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const syncButton = screen.getByText('Sync with GitHub');
    const icon = syncButton.querySelector('.animate-spin');
    expect(icon).toBeInTheDocument();
  });

  it('should disable sync button when syncing', () => {
    mockUseSyncProject.mockReturnValue({
      mutate: mockSyncMutate,
      isPending: true,
    } as any);

    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const syncButton = screen.getByText('Sync with GitHub').closest('button');
    expect(syncButton).toBeDisabled();
  });

  it('should navigate to settings when clicking Settings', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const settingsLink = screen.getByText('Settings').closest('a');
    expect(settingsLink).toHaveAttribute('href', '/projects/1/settings');
  });

  it('should show confirmation dialog when clicking Delete', () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);

    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete "Test Project"?');

    confirmSpy.mockRestore();
  });

  it('should call delete mutation when confirmed', () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);

    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(mockDeleteMutate).toHaveBeenCalledWith('1');

    confirmSpy.mockRestore();
  });

  it('should not call delete mutation when cancelled', () => {
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);

    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    const moreButton = screen.getByRole('button', { name: '' });
    fireEvent.click(moreButton);

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(mockDeleteMutate).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('should render health status indicator', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: createWrapper() });

    expect(screen.getByText('Healthy')).toBeInTheDocument();
  });

  it('should not render language tag when language is null', () => {
    const projectWithoutLang = { ...mockProject, language: null };
    render(<ProjectCard project={projectWithoutLang} />, { wrapper: createWrapper() });

    expect(screen.queryByText('TypeScript')).not.toBeInTheDocument();
  });
});
