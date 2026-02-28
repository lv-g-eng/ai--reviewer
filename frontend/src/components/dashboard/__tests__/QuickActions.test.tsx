/**
 * Unit tests for QuickActions component
 * Tests rendering and button interactions
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { QuickActions } from '../QuickActions';

describe('QuickActions', () => {
  it('should render component title and description', () => {
    render(<QuickActions />);

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Common tasks and shortcuts')).toBeInTheDocument();
  });

  it('should render all action buttons', () => {
    render(<QuickActions />);

    expect(screen.getByText('Add New Project')).toBeInTheDocument();
    expect(screen.getByText('View All Reviews')).toBeInTheDocument();
    expect(screen.getByText('Architecture Overview')).toBeInTheDocument();
    expect(screen.getByText('View Critical Issues')).toBeInTheDocument();
  });

  it('should render buttons with correct icons', () => {
    const { container } = render(<QuickActions />);

    // Check that SVG icons are present
    const buttons = container.querySelectorAll('button');
    expect(buttons).toHaveLength(4);

    buttons.forEach(button => {
      const svg = button.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  it('should render buttons with outline variant', () => {
    const { container } = render(<QuickActions />);

    const buttons = container.querySelectorAll('button');
    buttons.forEach(button => {
      expect(button.className).toContain('outline');
    });
  });

  it('should render buttons with full width', () => {
    const { container } = render(<QuickActions />);

    const buttons = container.querySelectorAll('button');
    buttons.forEach(button => {
      expect(button.className).toContain('w-full');
    });
  });

  it('should render buttons with left-aligned content', () => {
    const { container } = render(<QuickActions />);

    const buttons = container.querySelectorAll('button');
    buttons.forEach(button => {
      expect(button.className).toContain('justify-start');
    });
  });

  it('should be clickable', () => {
    render(<QuickActions />);

    const addProjectButton = screen.getByText('Add New Project');
    fireEvent.click(addProjectButton);

    // Button should be clickable (no error thrown)
    expect(addProjectButton).toBeInTheDocument();
  });

  it('should render in correct order', () => {
    const { container } = render(<QuickActions />);

    const buttons = Array.from(container.querySelectorAll('button')).map(
      btn => btn.textContent
    );

    expect(buttons).toEqual([
      'Add New Project',
      'View All Reviews',
      'Architecture Overview',
      'View Critical Issues',
    ]);
  });

  it('should have proper spacing between buttons', () => {
    const { container } = render(<QuickActions />);

    const cardContent = container.querySelector('.space-y-2');
    expect(cardContent).toBeInTheDocument();
  });
});
