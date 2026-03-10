/**
 * Type-safe test utilities and mock types
 */
import { ReactNode } from 'react';

// Mock component props types
export interface MockVirtualListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  height?: number;
  itemHeight?: number;
}

export interface MockErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export interface MockLoadingStateProps {
  text?: string;
  size?: 'small' | 'medium' | 'large';
}

export interface MockOfflineIndicatorProps {
  isOnline?: boolean;
}

// Project-related types
export interface MockProject {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  createdAt: string;
  updatedAt: string;
  owner: {
    id: string;
    name: string;
    email: string;
  };
}

export interface MockUseProjectsReturn {
  data: MockProject[] | undefined;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  hasNextPage?: boolean;
  fetchNextPage?: () => Promise<void>;
  isFetchingNextPage?: boolean;
}

// Query client mock types
export interface MockQueryClientOptions {
  defaultOptions?: {
    queries?: {
      retry?: boolean | number;
      staleTime?: number;
      cacheTime?: number;
    };
  };
}

// Test render options
export interface RenderWithProvidersOptions {
  queryClient?: MockQueryClientOptions;
  initialEntries?: string[];
}

// User event types
export interface MockUserEvent {
  click: (element: Element) => Promise<void>;
  type: (element: Element, text: string) => Promise<void>;
  clear: (element: Element) => Promise<void>;
  selectOptions: (element: Element, values: string | string[]) => Promise<void>;
  keyboard: (text: string) => Promise<void>;
}

// Mock function types
export type MockFunction<T extends (...args: any[]) => any> = jest.MockedFunction<T>;

// Component test props
export interface ComponentTestProps {
  testId?: string;
  className?: string;
  'data-testid'?: string;
}

// Error types for testing
export interface MockError extends Error {
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
}

// API response types
export interface MockApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  errors?: string[];
}

export interface MockPaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Form validation types
export interface MockFormErrors {
  [field: string]: string | string[] | undefined;
}

export interface MockFormState<T> {
  values: T;
  errors: MockFormErrors;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

// Test utilities
export const createMockProject = (overrides: Partial<MockProject> = {}): MockProject => ({
  id: 'test-project-1',
  name: 'Test Project',
  description: 'A test project for unit testing',
  status: 'active',
  createdAt: '2026-03-10T12:00:00Z',
  updatedAt: '2026-03-10T12:00:00Z',
  owner: {
    id: 'test-user-1',
    name: 'Test User',
    email: 'test@example.com'
  },
  ...overrides
});

export const createMockProjects = (count: number): MockProject[] => {
  return Array.from({ length: count }, (_, index) =>
    createMockProject({
      id: `test-project-${index + 1}`,
      name: `Test Project ${index + 1}`,
      owner: {
        id: `test-user-${index + 1}`,
        name: `Test User ${index + 1}`,
        email: `test${index + 1}@example.com`
      }
    })
  );
};

export const createMockError = (message: string, code?: string, status?: number): MockError => {
  const error = new Error(message) as MockError;
  if (code) error.code = code;
  if (status) error.status = status;
  return error;
};

// Type guards
export const isValidProject = (project: unknown): project is MockProject => {
  return (
    typeof project === 'object' &&
    project !== null &&
    'id' in project &&
    'name' in project &&
    'status' in project &&
    typeof (project as MockProject).id === 'string' &&
    typeof (project as MockProject).name === 'string'
  );
};

// Mock implementations
export const createMockUseProjects = (
  returnValue: Partial<MockUseProjectsReturn> = {}
): MockFunction<() => MockUseProjectsReturn> => {
  return jest.fn(() => ({
    data: undefined,
    isLoading: false,
    error: null,
    refetch: jest.fn().mockResolvedValue(undefined),
    hasNextPage: false,
    fetchNextPage: jest.fn().mockResolvedValue(undefined),
    isFetchingNextPage: false,
    ...returnValue
  }));
};