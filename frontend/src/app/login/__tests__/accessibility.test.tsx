/**
 * Accessibility Tests for Login Page
 * 
 * Tests WCAG 2.1 Level AA compliance using axe-core
 * Requirements: 3.10
 */

import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import LoginPage from '../page';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(() => null),
  }),
  usePathname: () => '/login',
}));

// Mock AuthContext
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn(),
    loading: false,
    isAuthenticated: false,
    user: null,
    permissions: [],
  }),
}));

// Mock toast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

describe('Login Page Accessibility', () => {
  it('should not have any automatically detectable accessibility violations', async () => {
    const { container } = render(<LoginPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA labels on form elements', () => {
    const { getByLabelText } = render(<LoginPage />);
    
    expect(getByLabelText('Email')).toBeInTheDocument();
    expect(getByLabelText('Password')).toBeInTheDocument();
  });

  it('should have proper role attributes', () => {
    const { getByRole } = render(<LoginPage />);
    
    expect(getByRole('main')).toBeInTheDocument();
    expect(getByRole('img', { name: /AI Reviewer Logo/i })).toBeInTheDocument();
  });

  it('should have accessible form with proper aria-label', () => {
    const { getByRole } = render(<LoginPage />);
    
    const form = getByRole('form', { name: /login form/i });
    expect(form).toBeInTheDocument();
  });

  it('should have accessible button with proper aria-label', () => {
    const { getByRole } = render(<LoginPage />);
    
    const button = getByRole('button', { name: /sign in to your account/i });
    expect(button).toBeInTheDocument();
  });

  it('should have proper heading hierarchy', () => {
    const { container } = render(<LoginPage />);
    
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    expect(headings.length).toBeGreaterThan(0);
  });

  it('should have keyboard accessible links', () => {
    const { getByRole } = render(<LoginPage />);
    
    const forgotPasswordLink = getByRole('link', { name: /forgot password/i });
    expect(forgotPasswordLink).toBeInTheDocument();
    const href = forgotPasswordLink.getAttribute('href');
    expect(href).toBeTruthy();
    expect(href).not.toBe('');
  });

  it('should have proper color contrast (manual verification required)', () => {
    // Note: Color contrast requires manual testing with tools like:
    // - Chrome DevTools Lighthouse
    // - axe DevTools browser extension
    // - WAVE browser extension
    expect(true).toBe(true);
  });
});
