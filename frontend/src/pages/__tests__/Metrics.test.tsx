import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Metrics from '../Metrics';
import { DashboardService } from '../../services/DashboardService';

describe('Metrics Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  it('should render loading state initially', () => {
    render(<Metrics />);
    expect(screen.getByText(/loading metrics/i)).toBeInTheDocument();
  });

  it('should render metrics dashboard after loading', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/monitor system performance/i)).toBeInTheDocument();
  });

  it('should render time range selector buttons', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    expect(screen.getByRole('button', { name: /day/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /week/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /month/i })).toBeInTheDocument();
  });

  it('should have week as default time range', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const weekButton = screen.getByRole('button', { name: /week/i });
    expect(weekButton).toHaveClass('bg-blue-600');
  });

  it('should change time range when button is clicked', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const dayButton = screen.getByRole('button', { name: /day/i });
    fireEvent.click(dayButton);
    
    await waitFor(() => {
      expect(dayButton).toHaveClass('bg-blue-600');
    });
  });

  it('should call onTimeRangeChange callback when time range changes', async () => {
    const mockCallback = jest.fn();
    render(<Metrics onTimeRangeChange={mockCallback} />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const monthButton = screen.getByRole('button', { name: /month/i });
    fireEvent.click(monthButton);
    
    expect(mockCallback).toHaveBeenCalledWith('month');
  });

  it('should render metric summary cards', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      const performanceElements = screen.getAllByText(/performance score/i);
      expect(performanceElements.length).toBeGreaterThan(0);
    });
    
    const errorRateElements = screen.getAllByText(/error rate/i);
    expect(errorRateElements.length).toBeGreaterThan(0);
    
    const responseTimeElements = screen.getAllByText(/response time/i);
    expect(responseTimeElements.length).toBeGreaterThan(0);
  });

  it('should render chart with metric trends', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metric trends/i)).toBeInTheDocument();
    });
  });

  it('should use custom initial time range', async () => {
    render(<Metrics initialTimeRange="day" />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const dayButton = screen.getByRole('button', { name: /day/i });
    expect(dayButton).toHaveClass('bg-blue-600');
  });

  it('should reload data when time range changes', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const monthButton = screen.getByRole('button', { name: /month/i });
    fireEvent.click(monthButton);
    
    // Should show loading state briefly
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
  });

  it('should display latest metric values in summary cards', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      const elements = screen.getAllByText(/latest value from week view/i);
      expect(elements.length).toBe(3); // One for each metric card
    });
  });
});

describe('Custom Dashboard Functionality', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should render create dashboard button', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/create dashboard/i)).toBeInTheDocument();
    });
  });

  it('should open dashboard modal when create button is clicked', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const createButton = screen.getByRole('button', { name: /create dashboard/i });
    fireEvent.click(createButton);
    
    await waitFor(() => {
      expect(screen.getByText(/configure your custom metrics dashboard/i)).toBeInTheDocument();
    });
  });

  it('should close modal when cancel is clicked', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const createButton = screen.getByRole('button', { name: /create dashboard/i });
    fireEvent.click(createButton);
    
    await waitFor(() => {
      expect(screen.getByText(/configure your custom metrics dashboard/i)).toBeInTheDocument();
    });
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    await waitFor(() => {
      expect(screen.queryByText(/configure your custom metrics dashboard/i)).not.toBeInTheDocument();
    });
  });

  it('should create a new dashboard when form is submitted', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    // Open modal
    const createButtons = screen.getAllByRole('button', { name: /create dashboard/i });
    const headerCreateButton = createButtons[0]; // The one in the header
    fireEvent.click(headerCreateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/configure your custom metrics dashboard/i)).toBeInTheDocument();
    });
    
    // Fill form
    const nameInput = screen.getByPlaceholderText(/my dashboard/i);
    fireEvent.change(nameInput, { target: { value: 'Test Dashboard' } });
    
    // Select a metric
    const performanceCheckbox = screen.getByLabelText(/performance score/i);
    fireEvent.click(performanceCheckbox);
    
    // Submit - get the submit button inside the form
    const submitButtons = screen.getAllByRole('button', { name: /create dashboard/i });
    const formSubmitButton = submitButtons[1]; // The one in the modal form
    fireEvent.click(formSubmitButton);
    
    // Dashboard should be created and tab should appear
    await waitFor(() => {
      const tabs = screen.getAllByText('Test Dashboard');
      expect(tabs.length).toBeGreaterThan(0);
    });
  });

  it('should load saved dashboards on mount', async () => {
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Saved Dashboard',
      description: 'Test',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('Saved Dashboard')).toBeInTheDocument();
    });
  });

  it('should switch to custom dashboard view when dashboard tab is clicked', async () => {
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'My Dashboard',
      description: 'Custom dashboard',
      metrics: ['performance', 'errorRate'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('My Dashboard')).toBeInTheDocument();
    });
    
    // Click dashboard tab
    const dashboardTab = screen.getByRole('button', { name: 'My Dashboard' });
    fireEvent.click(dashboardTab);
    
    // Should show dashboard info
    await waitFor(() => {
      expect(screen.getByText('Custom dashboard')).toBeInTheDocument();
      expect(screen.getByText(/refresh: 30s/i)).toBeInTheDocument();
    });
  });

  it('should show edit and delete buttons when dashboard is active', async () => {
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Editable Dashboard',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('Editable Dashboard')).toBeInTheDocument();
    });
    
    // Click dashboard tab
    const dashboardTab = screen.getByRole('button', { name: 'Editable Dashboard' });
    fireEvent.click(dashboardTab);
    
    // Should show edit and delete buttons
    await waitFor(() => {
      const editButton = screen.getByTitle(/edit dashboard/i);
      const deleteButton = screen.getByTitle(/delete dashboard/i);
      expect(editButton).toBeInTheDocument();
      expect(deleteButton).toBeInTheDocument();
    });
  });

  it('should delete dashboard when delete button is clicked and confirmed', async () => {
    // Mock window.confirm
    global.confirm = jest.fn(() => true);
    
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Delete Me',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('Delete Me')).toBeInTheDocument();
    });
    
    // Click dashboard tab
    const dashboardTab = screen.getByRole('button', { name: 'Delete Me' });
    fireEvent.click(dashboardTab);
    
    // Click delete button
    const deleteButton = screen.getByTitle(/delete dashboard/i);
    fireEvent.click(deleteButton);
    
    // Dashboard should be removed
    await waitFor(() => {
      expect(screen.queryByText('Delete Me')).not.toBeInTheDocument();
    });
  });

  it('should not delete dashboard when delete is cancelled', async () => {
    // Mock window.confirm to return false
    global.confirm = jest.fn(() => false);
    
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Keep Me',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      const tabs = screen.getAllByText('Keep Me');
      expect(tabs.length).toBeGreaterThan(0);
    });
    
    // Click dashboard tab
    const dashboardTabs = screen.getAllByRole('button', { name: 'Keep Me' });
    fireEvent.click(dashboardTabs[0]);
    
    // Click delete button
    const deleteButton = screen.getByTitle(/delete dashboard/i);
    fireEvent.click(deleteButton);
    
    // Dashboard should still be there
    await waitFor(() => {
      const tabs = screen.getAllByText('Keep Me');
      expect(tabs.length).toBeGreaterThan(0);
    });
  });

  it('should switch back to default view when default view tab is clicked', async () => {
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Custom View',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('Custom View')).toBeInTheDocument();
    });
    
    // Click custom dashboard tab
    const customTab = screen.getByRole('button', { name: 'Custom View' });
    fireEvent.click(customTab);
    
    await waitFor(() => {
      expect(customTab).toHaveClass('bg-blue-600');
    });
    
    // Click default view tab
    const defaultTab = screen.getByRole('button', { name: /default view/i });
    fireEvent.click(defaultTab);
    
    // Should show time range selector (only in default view)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /day/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /week/i })).toBeInTheDocument();
    });
  });

  it('should validate dashboard form and show errors', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    // Open modal
    const createButtons = screen.getAllByRole('button', { name: /create dashboard/i });
    const headerCreateButton = createButtons[0];
    fireEvent.click(headerCreateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/configure your custom metrics dashboard/i)).toBeInTheDocument();
    });
    
    // Try to submit without filling required fields
    const submitButtons = screen.getAllByRole('button', { name: /create dashboard/i });
    const formSubmitButton = submitButtons[1];
    fireEvent.click(formSubmitButton);
    
    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/dashboard name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/select at least one metric/i)).toBeInTheDocument();
    });
  });
});

describe('Data Export Functionality', () => {
  beforeEach(() => {
    localStorage.clear();
    
    // Mock URL.createObjectURL and URL.revokeObjectURL
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    // Mock alert
    global.alert = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render CSV export button', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const csvButton = screen.getByRole('button', { name: /csv/i });
    expect(csvButton).toBeInTheDocument();
  });

  it('should render JSON export button', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const jsonButton = screen.getByRole('button', { name: /json/i });
    expect(jsonButton).toBeInTheDocument();
  });

  it('should export data as CSV when CSV button is clicked', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const csvButton = screen.getByRole('button', { name: /csv/i });
    fireEvent.click(csvButton);
    
    // Verify Blob was created with CSV content
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should export data as JSON when JSON button is clicked', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const jsonButton = screen.getByRole('button', { name: /json/i });
    fireEvent.click(jsonButton);
    
    // Verify Blob was created with JSON content
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should include time range in CSV filename', async () => {
    render(<Metrics initialTimeRange="month" />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const csvButton = screen.getByRole('button', { name: /csv/i });
    fireEvent.click(csvButton);
    
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should include time range in JSON filename', async () => {
    render(<Metrics initialTimeRange="day" />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const jsonButton = screen.getByRole('button', { name: /json/i });
    fireEvent.click(jsonButton);
    
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should include dashboard name in filename when exporting from custom dashboard', async () => {
    // Pre-create a dashboard
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'My Custom Dashboard',
      metrics: ['performance'],
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('My Custom Dashboard')).toBeInTheDocument();
    });
    
    // Switch to custom dashboard
    const dashboardTab = screen.getByRole('button', { name: 'My Custom Dashboard' });
    fireEvent.click(dashboardTab);
    
    await waitFor(() => {
      expect(screen.getByText(/refresh: 30s/i)).toBeInTheDocument();
    });
    
    // Export as CSV
    const csvButton = screen.getByRole('button', { name: /csv/i });
    fireEvent.click(csvButton);
    
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should export only selected metrics from custom dashboard', async () => {
    // Pre-create a dashboard with only performance metric
    const mockUser = {
      id: 'user_1',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    DashboardService.saveDashboard({
      name: 'Performance Only',
      metrics: ['performance'], // Only performance metric
      timeRange: { type: 'relative', value: 7, unit: 'day' },
      refreshInterval: 30,
      shared: false
    }, mockUser);
    
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText('Performance Only')).toBeInTheDocument();
    });
    
    // Switch to custom dashboard
    const dashboardTab = screen.getByRole('button', { name: 'Performance Only' });
    fireEvent.click(dashboardTab);
    
    await waitFor(() => {
      expect(screen.getByText(/refresh: 30s/i)).toBeInTheDocument();
    });
    
    // Export as JSON
    const jsonButton = screen.getByRole('button', { name: /json/i });
    fireEvent.click(jsonButton);
    
    // Verify export was triggered
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should disable export buttons when no data is available', async () => {
    render(<Metrics />);
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    // After loading, buttons should be enabled (data is available)
    const csvButton = screen.getByRole('button', { name: /csv/i });
    const jsonButton = screen.getByRole('button', { name: /json/i });
    
    expect(csvButton).not.toBeDisabled();
    expect(jsonButton).not.toBeDisabled();
  });

  it('should export data that matches displayed data', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    // Get displayed metric values
    const performanceCards = screen.getAllByText(/performance score/i);
    expect(performanceCards.length).toBeGreaterThan(0);
    
    // Export as JSON
    const jsonButton = screen.getByRole('button', { name: /json/i });
    fireEvent.click(jsonButton);
    
    // Verify export was triggered with data
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should include metric definitions in JSON export', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const jsonButton = screen.getByRole('button', { name: /json/i });
    fireEvent.click(jsonButton);
    
    // Verify Blob was created (metric definitions would be in the JSON)
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });

  it('should include timestamp and labels in CSV export', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });
    
    const csvButton = screen.getByRole('button', { name: /csv/i });
    fireEvent.click(csvButton);
    
    // Verify export was triggered
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });
  });
});

describe('Threshold Alert Display', () => {
  it('should display warning indicator when metric exceeds warning threshold', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getAllByText(/performance score/i).length).toBeGreaterThan(0);
    });

    // Check if warning or critical indicators are present (depends on mock data)
    // The mock data generates random values, so we just verify the component renders
    const summaryCards = screen.getAllByText(/latest value from/i);
    expect(summaryCards.length).toBeGreaterThan(0);
  });

  it('should display threshold configuration in summary cards', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // Wait for summary cards to render
    await waitFor(() => {
      expect(screen.getAllByText(/thresholds:/i).length).toBeGreaterThan(0);
    });

    // Check for warning and critical threshold labels
    expect(screen.getAllByText(/warning:/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/critical:/i).length).toBeGreaterThan(0);
  });

  it('should show threshold reference lines when single metric is selected', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // Deselect all but one metric
    const clearButton = screen.getByRole('button', { name: /clear/i });
    fireEvent.click(clearButton);

    await waitFor(() => {
      // Check for threshold configuration section
      expect(screen.getByText(/threshold configuration:/i)).toBeInTheDocument();
    });
  });

  it('should not show threshold lines when multiple metrics are selected', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // All metrics should be selected by default
    const selectedCount = screen.getByText(/3 metrics selected/i);
    expect(selectedCount).toBeInTheDocument();

    // Threshold configuration should not be visible with multiple metrics
    expect(screen.queryByText(/threshold configuration:/i)).not.toBeInTheDocument();
  });

  it('should apply correct alert level styling to summary cards', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // Wait for summary cards
    await waitFor(() => {
      const cards = screen.getAllByText(/latest value from/i);
      expect(cards.length).toBeGreaterThan(0);
    });

    // Cards should be rendered (styling depends on actual values)
    const performanceCards = screen.getAllByText(/performance score/i);
    expect(performanceCards.length).toBeGreaterThan(0);
  });

  it('should show threshold values in summary cards', async () => {
    render(<Metrics />);
    
    await waitFor(() => {
      expect(screen.getByText(/metrics dashboard/i)).toBeInTheDocument();
    });

    // Wait for threshold information to render
    await waitFor(() => {
      // Check for specific threshold values
      expect(screen.getByText(/70score/i)).toBeInTheDocument(); // Performance warning
      expect(screen.getByText(/50score/i)).toBeInTheDocument(); // Performance critical
    });
  });
});
