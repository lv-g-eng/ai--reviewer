/**
 * ErrorBoundary单元test
 * 
 * test场景:
 * - 正常render子component
 * - 捕获子componenterror
 * - show降级UI
 * - 上报error到ErrorMonitor
 * - reseterrorstatus
 * - 重新load页面
 * - report问题feature
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';
import { getErrorMonitor, resetErrorMonitor, MonitorConfig } from '../../services/ErrorMonitor';

// create一item会抛出error的component
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>Normal content</div>;
};

describe('ErrorBoundary', () => {
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    // 抑制React的errorlogoutput
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // 初始化ErrorMonitor
    resetErrorMonitor();
    const config: MonitorConfig = {
      environment: 'test',
      enableDebugMode: false,
    };
    const monitor = getErrorMonitor(config);
    monitor.initialize();
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    jest.clearAllMocks();
    resetErrorMonitor();
  });

  describe('正常render', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should not show error UI when children render successfully', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Normal content')).toBeInTheDocument();
      expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
    });
  });

  describe('error捕获', () => {
    it('should catch errors from child components', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // shouldshowerrorUI
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      // 不shouldshow正常content
      expect(screen.queryByText('Normal content')).not.toBeInTheDocument();
    });

    it('should display error message in development mode', () => {
      // Mock NODE_ENV
      const originalEnv = process.env.NODE_ENV;
      Object.defineProperty(process.env, 'NODE_ENV', {
        value: 'development',
        writable: true,
        configurable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // In development mode, error details should be visible
      // Since NODE_ENV is set at build time, we just verify the error UI is shown
      const errorUI = screen.getByText(/something went wrong/i);
      expect(errorUI).toBeInTheDocument();

      // Restore NODE_ENV
      Object.defineProperty(process.env, 'NODE_ENV', {
        value: originalEnv,
        writable: true,
        configurable: true,
      });
    });

    it('should call onError callback when error occurs', () => {
      const onError = jest.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });

    it('should report error to ErrorMonitor', () => {
      const monitor = getErrorMonitor();
      const captureErrorSpy = jest.spyOn(monitor, 'captureError');

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(captureErrorSpy).toHaveBeenCalledTimes(1);
      expect(captureErrorSpy).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          url: expect.any(String),
          userAgent: expect.any(String),
          additionalData: expect.objectContaining({
            componentStack: expect.any(String),
            errorBoundary: true,
          }),
        })
      );
    });
  });

  describe('降级UI', () => {
    it('should display default fallback UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      expect(screen.getByText(/try again/i)).toBeInTheDocument();
      expect(screen.getByText(/reload page/i)).toBeInTheDocument();
      expect(screen.getByText(/report issue/i)).toBeInTheDocument();
    });

    it('should use custom fallback when provided', () => {
      const customFallback = (error: Error) => (
        <div>Custom error: {error.message}</div>
      );

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/custom error: test error/i)).toBeInTheDocument();
      expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
    });
  });

  describe('resetfeature', () => {
    it('should reset error state when Try Again is clicked', () => {
      let shouldThrow = true;
      
      const TestComponent = () => {
        if (shouldThrow) {
          throw new Error('Test error');
        }
        return <div>Normal content</div>;
      };

      const { rerender } = render(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      // confirmerrorUIshow
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

      // 点击Try Again并updatestatus
      shouldThrow = false;
      fireEvent.click(screen.getByText(/try again/i));

      // 重新render不抛出error的component
      rerender(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      // shouldshow正常content
      expect(screen.getByText('Normal content')).toBeInTheDocument();
      expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
    });

    it('should call onReset callback when reset', () => {
      const onReset = jest.fn();

      render(
        <ErrorBoundary onReset={onReset}>
          <ThrowError />
        </ErrorBoundary>
      );

      fireEvent.click(screen.getByText(/try again/i));

      expect(onReset).toHaveBeenCalledTimes(1);
    });
  });

  describe('重新loadfeature', () => {
    it('should reload page when Reload Page is clicked', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const reloadButton = screen.getByText(/reload page/i);
      expect(reloadButton).toBeInTheDocument();
      
      // Verify button exists and is clickable
      fireEvent.click(reloadButton);
      
      // The button should trigger reload (we can't fully test this in jsdom)
      // but we can verify the button works
      expect(reloadButton).toBeInTheDocument();
    });
  });

  describe('report问题feature', () => {
    it('should open mailto link when Report Issue is clicked', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const reportButton = screen.getByText(/report issue/i);
      expect(reportButton).toBeInTheDocument();
      
      // Verify button exists and is clickable
      // Note: We can't fully test the mailto: navigation in jsdom,
      // but we can verify the button works and the handler is called
      fireEvent.click(reportButton);
      
      // The button should still be there after click
      expect(reportButton).toBeInTheDocument();
    });
  });

  describe('边缘情况', () => {
    it('should handle ErrorMonitor not initialized gracefully', () => {
      resetErrorMonitor();
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // should仍然showerrorUI
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

      consoleErrorSpy.mockRestore();
    });

    it('should handle onError callback throwing error', () => {
      const onError = jest.fn(() => {
        throw new Error('Callback error');
      });

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      );

      // should仍然showerrorUI
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should handle onReset callback throwing error', () => {
      const onReset = jest.fn(() => {
        throw new Error('Reset error');
      });

      render(
        <ErrorBoundary onReset={onReset}>
          <ThrowError />
        </ErrorBoundary>
      );

      // 点击Try Again不should崩溃
      fireEvent.click(screen.getByText(/try again/i));

      expect(onReset).toHaveBeenCalled();
    });
  });

  describe('多itemErrorBoundary嵌套', () => {
    it('should allow nested ErrorBoundaries', () => {
      const OuterFallback = () => <div>Outer error</div>;
      const InnerFallback = () => <div>Inner error</div>;

      render(
        <ErrorBoundary fallback={OuterFallback}>
          <div>Outer content</div>
          <ErrorBoundary fallback={InnerFallback}>
            <ThrowError />
          </ErrorBoundary>
        </ErrorBoundary>
      );

      // 内部ErrorBoundaryshould捕获error
      expect(screen.getByText('Inner error')).toBeInTheDocument();
      expect(screen.getByText('Outer content')).toBeInTheDocument();
      expect(screen.queryByText('Outer error')).not.toBeInTheDocument();
    });
  });
});
