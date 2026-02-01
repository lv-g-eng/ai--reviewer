/**
 * Unit Tests for Backend Status Component
 * 
 * Tests specific functionality of the BackendStatusBanner component.
 * 
 * Validates Requirements: 3.2, 3.3, 3.4, 3.5, 3.6
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BackendStatusBanner } from '@/components/common/backend-status';
import { BackendStatusProvider } from '@/contexts/BackendStatusContext';

// Mock fetch globally
global.fetch = jest.fn();

describe('Backend Status Component - Unit Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  it('should display banner when backend is offline', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    const bannerText = await screen.findByText(/Backend Not Available/i, {}, { timeout: 5000 });
    expect(bannerText).toBeInTheDocument();
    expect(screen.getByText(/backend server is currently unavailable/i)).toBeInTheDocument();
  });

  it('should not display banner when backend is online', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    }, { timeout: 5000 });

    expect(screen.queryByText(/Backend Not Available/i)).not.toBeInTheDocument();
  });

  it('should display retry button when backend is unavailable', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    await screen.findByText(/Backend Not Available/i, {}, { timeout: 5000 });

    const retryButton = screen.getByRole('button', { name: /Retry/i });
    expect(retryButton).toBeInTheDocument();
    expect(retryButton).not.toBeDisabled();
  });

  it('should dismiss banner when dismiss button is clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    await screen.findByText(/Backend Not Available/i, {}, { timeout: 5000 });

    const dismissButton = screen.getByLabelText(/Dismiss banner/i);
    fireEvent.click(dismissButton);

    await waitFor(() => {
      expect(screen.queryByText(/Backend Not Available/i)).not.toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('should provide link to API docs', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    await screen.findByText(/Backend Not Available/i, {}, { timeout: 5000 });

    const docsLink = screen.getByRole('link', { name: /View API docs/i });
    expect(docsLink).toBeInTheDocument();
    expect(docsLink).toHaveAttribute('href', '/docs');
  });

  it('should display appropriate error message', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    render(
      <BackendStatusProvider>
        <BackendStatusBanner />
      </BackendStatusProvider>
    );

    await screen.findByText(/Backend Not Available/i, {}, { timeout: 5000 });

    expect(screen.getByText(/backend server is currently unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/Some features may not work properly/i)).toBeInTheDocument();
  });
});
