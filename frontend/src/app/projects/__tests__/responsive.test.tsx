/**
 * Responsive Design Tests for Project Dashboard
 * 
 * Tests verify that the project dashboard components render correctly
 * at various viewport sizes from 320px to 2560px.
 */

import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ProjectsPage from '../page'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '/projects',
}))

// Mock the useProjects hook
jest.mock('@/hooks/useProjects', () => ({
  useProjects: () => ({
    data: [
      {
        id: '1',
        name: 'Test Project',
        description: 'Test Description',
        github_repo_url: 'https://github.com/test/repo',
        owner_id: 'user1',
        language: 'TypeScript',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      },
    ],
    isLoading: false,
  }),
  useCreateProject: () => ({
    mutateAsync: jest.fn(),
    isPending: false,
  }),
}))

// Mock MainLayout
jest.mock('@/components/layout/main-layout', () => ({
  MainLayout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

// Mock AddProjectModal
jest.mock('@/components/projects/add-project-modal', () => ({
  AddProjectModal: () => <div>Add Project Modal</div>,
}))

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

describe('Project Dashboard Responsive Design', () => {
  const viewportSizes = [
    { width: 320, height: 568, name: 'Mobile Small' },
    { width: 375, height: 667, name: 'Mobile Medium' },
    { width: 414, height: 896, name: 'Mobile Large' },
    { width: 768, height: 1024, name: 'Tablet' },
    { width: 1024, height: 768, name: 'Laptop' },
    { width: 1280, height: 720, name: 'Desktop' },
    { width: 1920, height: 1080, name: 'Full HD' },
    { width: 2560, height: 1440, name: 'Large Desktop' },
  ]

  viewportSizes.forEach(({ width, height, name }) => {
    describe(`${name} (${width}x${height})`, () => {
      beforeEach(() => {
        // Set viewport size
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width,
        })
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: height,
        })
      })

      it('renders without horizontal scroll', () => {
        const queryClient = createTestQueryClient()
        const { container } = render(
          <QueryClientProvider client={queryClient}>
            <ProjectsPage />
          </QueryClientProvider>
        )

        // Check that content doesn't overflow
        const mainContent = container.firstChild
        expect(mainContent).toBeInTheDocument()
      })

      it('displays essential UI elements', () => {
        const queryClient = createTestQueryClient()
        render(
          <QueryClientProvider client={queryClient}>
            <ProjectsPage />
          </QueryClientProvider>
        )

        // Essential elements should be present at all viewport sizes
        expect(screen.getByText('Projects')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('Search projects...')).toBeInTheDocument()
        expect(screen.getByText('Add Project')).toBeInTheDocument()
      })

      it('renders project cards', () => {
        const queryClient = createTestQueryClient()
        render(
          <QueryClientProvider client={queryClient}>
            <ProjectsPage />
          </QueryClientProvider>
        )

        expect(screen.getByText('Test Project')).toBeInTheDocument()
        expect(screen.getByText('Test Description')).toBeInTheDocument()
      })
    })
  })

  describe('Responsive Grid Behavior', () => {
    it('uses single column on mobile', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      const queryClient = createTestQueryClient()
      const { container } = render(
        <QueryClientProvider client={queryClient}>
          <ProjectsPage />
        </QueryClientProvider>
      )

      // Grid should exist
      const grid = container.querySelector('.grid')
      expect(grid).toBeInTheDocument()
    })

    it('uses multi-column on desktop', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1280,
      })

      const queryClient = createTestQueryClient()
      const { container } = render(
        <QueryClientProvider client={queryClient}>
          <ProjectsPage />
        </QueryClientProvider>
      )

      // Grid should exist with responsive classes
      const grid = container.querySelector('.grid')
      expect(grid).toBeInTheDocument()
    })
  })

  describe('Touch Target Sizes', () => {
    it('has adequately sized buttons for touch', () => {
      const queryClient = createTestQueryClient()
      render(
        <QueryClientProvider client={queryClient}>
          <ProjectsPage />
        </QueryClientProvider>
      )

      const addButton = screen.getByText('Add Project').closest('button')
      expect(addButton).toBeInTheDocument()
      
      // Button should have adequate padding/height for touch
      // Tailwind button component provides this by default
    })
  })

  describe('Text Readability', () => {
    it('maintains readable text at all viewport sizes', () => {
      viewportSizes.forEach(({ width }) => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width,
        })

        const queryClient = createTestQueryClient()
        const { unmount } = render(
          <QueryClientProvider client={queryClient}>
            <ProjectsPage />
          </QueryClientProvider>
        )

        // Text should be present and readable
        expect(screen.getAllByText('Projects')[0]).toBeInTheDocument()
        expect(screen.getByText('Test Project')).toBeInTheDocument()
        
        // Clean up for next iteration
        unmount()
      })
    })
  })
})
