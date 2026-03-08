/**
 * LoadingStatecomponent单元test
 * 
 * testcontent:
 * - 不同变体的render
 * - 不同大小的render
 * - load文本show
 * - 全屏模式
 * - 自定义颜色
 * - 骨架屏行数
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingState } from '../LoadingState';

describe('LoadingState', () => {
  describe('Rendering', () => {
    it('should render spinner variant by default', () => {
      render(<LoadingState />);
      
      const container = screen.getByTestId('loading-state');
      expect(container).toBeInTheDocument();
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toBeInTheDocument();
    });

    it('should render dots variant', () => {
      render(<LoadingState variant="dots" />);
      
      const dots = screen.getByTestId('loading-dots');
      expect(dots).toBeInTheDocument();
    });

    it('should render skeleton variant', () => {
      render(<LoadingState variant="skeleton" />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      expect(skeleton).toBeInTheDocument();
    });

    it('should render with loading text', () => {
      const text = 'Loading data...';
      render(<LoadingState text={text} />);
      
      const loadingText = screen.getByTestId('loading-text');
      expect(loadingText).toHaveTextContent(text);
    });

    it('should not render text when not provided', () => {
      render(<LoadingState />);
      
      const loadingText = screen.queryByTestId('loading-text');
      expect(loadingText).not.toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('should render small size', () => {
      render(<LoadingState size="small" />);
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toHaveStyle({ width: '24px', height: '24px' });
    });

    it('should render medium size by default', () => {
      render(<LoadingState />);
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toHaveStyle({ width: '40px', height: '40px' });
    });

    it('should render large size', () => {
      render(<LoadingState size="large" />);
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toHaveStyle({ width: '64px', height: '64px' });
    });
  });

  describe('Fullscreen Mode', () => {
    it('should render in fullscreen mode', () => {
      render(<LoadingState fullscreen />);
      
      const container = screen.getByTestId('loading-state');
      expect(container).toHaveStyle({
        position: 'fixed',
        top: '0',
        left: '0',
        right: '0',
        bottom: '0',
      });
    });

    it('should not be fullscreen by default', () => {
      render(<LoadingState />);
      
      const container = screen.getByTestId('loading-state');
      expect(container).not.toHaveStyle({ position: 'fixed' });
    });
  });

  describe('Customization', () => {
    it('should apply custom className', () => {
      const className = 'custom-loading';
      render(<LoadingState className={className} />);
      
      const container = screen.getByTestId('loading-state');
      expect(container).toHaveClass(className);
    });

    it('should apply custom color', () => {
      const color = '#ff0000';
      render(<LoadingState color={color} />);
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toHaveStyle({ borderTop: `4px solid ${color}` });
    });

    it('should render custom number of skeleton lines', () => {
      const lines = 5;
      render(<LoadingState variant="skeleton" skeletonLines={lines} />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      const lineElements = skeleton.querySelectorAll('div');
      expect(lineElements).toHaveLength(lines);
    });

    it('should render default 3 skeleton lines', () => {
      render(<LoadingState variant="skeleton" />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      const lineElements = skeleton.querySelectorAll('div');
      expect(lineElements).toHaveLength(3);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<LoadingState />);
      
      const container = screen.getByTestId('loading-state');
      expect(container).toHaveAttribute('role', 'status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-busy', 'true');
    });

    it('should have accessible text when provided', () => {
      const text = 'Loading content';
      render(<LoadingState text={text} />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveTextContent(text);
    });
  });

  describe('Variants Rendering', () => {
    it('should render spinner with correct structure', () => {
      render(<LoadingState variant="spinner" />);
      
      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toHaveStyle({
        borderRadius: '50%',
      });
    });

    it('should render dots with three dots', () => {
      render(<LoadingState variant="dots" />);
      
      const dots = screen.getByTestId('loading-dots');
      const dotElements = dots.querySelectorAll('div');
      expect(dotElements).toHaveLength(3);
    });

    it('should render skeleton with proper structure', () => {
      render(<LoadingState variant="skeleton" skeletonLines={3} />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      const lines = skeleton.querySelectorAll('div');
      
      // Check that lines exist
      expect(lines.length).toBe(3);
      
      // Check that last line is shorter (70% width)
      const lastLine = lines[lines.length - 1];
      expect(lastLine).toHaveStyle({ width: '70%' });
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty text gracefully', () => {
      render(<LoadingState text="" />);
      
      const loadingText = screen.queryByTestId('loading-text');
      expect(loadingText).not.toBeInTheDocument();
    });

    it('should handle zero skeleton lines', () => {
      render(<LoadingState variant="skeleton" skeletonLines={0} />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      const lines = skeleton.querySelectorAll('div');
      expect(lines).toHaveLength(0);
    });

    it('should handle very large skeleton lines', () => {
      const lines = 100;
      render(<LoadingState variant="skeleton" skeletonLines={lines} />);
      
      const skeleton = screen.getByTestId('loading-skeleton');
      const lineElements = skeleton.querySelectorAll('div');
      expect(lineElements).toHaveLength(lines);
    });
  });
});
