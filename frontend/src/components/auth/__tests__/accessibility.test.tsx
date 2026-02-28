/**
 * Accessibility Tests for RouteGuard Component
 * 
 * Tests WCAG 2.1 Level AA compliance using axe-core
 * Requirements: 3.10
 */

import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { RouteGuard } from '../RouteGuard';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/dashboard',
}));

// Mock AuthContext
const mockUseAuth = jest.fn();
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}));

describe('RouteGuard Accessibility', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should not have accessibility violations when loading', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
      permissions: [],
    });

    const { container } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible loading state with proper role', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
      permissions: [],
    });

    const { getByRole } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    const loadingStatus = getByRole('status');
    expect(loadingStatus).toBeInTheDocument();
    expect(loadingStatus).toHaveAttribute('aria-live', 'polite');
  });

  it('should have screen reader text for loading state', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
      permissions: [],
    });

    const { container } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    const srText = container.querySelector('.sr-only');
    expect(srText).toBeInTheDocument();
    expect(srText?.textContent).toContain('Loading authentication status');
  });

  it('should have decorative loading icon', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
      permissions: [],
    });

    const { container } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    const icon = container.querySelector('svg');
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });

  it('should not have accessibility violations when authenticated', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', email: 'test@example.com', role: 'user' },
      loading: false,
      isAuthenticated: true,
      permissions: ['read'],
    });

    const { container } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should render protected content when authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', email: 'test@example.com', role: 'user' },
      loading: false,
      isAuthenticated: true,
      permissions: ['read'],
    });

    const { getByText } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    expect(getByText('Protected Content')).toBeInTheDocument();
  });

  it('should not render content when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      permissions: [],
    });

    const { queryByText } = render(
      <RouteGuard>
        <div>Protected Content</div>
      </RouteGuard>
    );

    expect(queryByText('Protected Content')).not.toBeInTheDocument();
  });
});
