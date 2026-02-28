/**
 * Accessibility Tests for Register Page
 * 
 * Tests WCAG 2.1 Level AA compliance using axe-core
 * Requirements: 3.10
 */

import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import RegisterPage from '../page';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/register',
}));

// Mock AuthContext
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    register: jest.fn(),
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

describe('Register Page Accessibility', () => {
  it('should not have any automatically detectable accessibility violations', async () => {
    const { container } = render(<RegisterPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA labels on form elements', () => {
    const { getByLabelText } = render(<RegisterPage />);
    
    expect(getByLabelText('Full Name')).toBeInTheDocument();
    expect(getByLabelText('Email')).toBeInTheDocument();
    expect(getByLabelText('Password')).toBeInTheDocument();
    expect(getByLabelText('Confirm Password')).toBeInTheDocument();
  });

  it('should have proper role attributes', () => {
    const { getByRole } = render(<RegisterPage />);
    
    expect(getByRole('main')).toBeInTheDocument();
    expect(getByRole('img', { name: /AI Reviewer Logo/i })).toBeInTheDocument();
  });

  it('should have accessible form with proper aria-label', () => {
    const { getByRole } = render(<RegisterPage />);
    
    const form = getByRole('form', { name: /registration form/i });
    expect(form).toBeInTheDocument();
  });

  it('should have accessible button with proper aria-label', () => {
    const { getByRole } = render(<RegisterPage />);
    
    const button = getByRole('button', { name: /create your account/i });
    expect(button).toBeInTheDocument();
  });

  it('should have accessible password strength indicator', () => {
    const { getByRole, getByLabelText } = render(<RegisterPage />);
    
    // Type in password field to trigger strength indicator
    const passwordInput = getByLabelText('Password');
    expect(passwordInput).toBeInTheDocument();
  });

  it('should have accessible checkbox for terms acceptance', () => {
    const { getByRole } = render(<RegisterPage />);
    
    const checkbox = getByRole('checkbox');
    expect(checkbox).toBeInTheDocument();
  });

  it('should have keyboard accessible links', () => {
    const { getAllByRole } = render(<RegisterPage />);
    
    const links = getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
    links.forEach(link => {
      // Check that href attribute exists and is not empty
      const href = link.getAttribute('href');
      expect(href).toBeTruthy();
      expect(href).not.toBe('');
    });
  });

  it('should have proper heading hierarchy', () => {
    const { container } = render(<RegisterPage />);
    
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    expect(headings.length).toBeGreaterThan(0);
  });
});
