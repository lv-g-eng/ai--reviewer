/**
 * Dashboard Service
 * 
 * Handles saving and loading custom dashboard configurations
 * Requirements: 6.1 - Allow users to create and save custom dashboard configurations
 */

import { CustomDashboard, DashboardFormData, DashboardLayout, Widget } from '../types/dashboard';

const STORAGE_KEY = 'custom_dashboards';

/**
 * Dashboard Service for managing custom dashboard configurations
 */
export class DashboardService {
  /**
   * Get all dashboards for a user
   */
  static getDashboards(userId: string): CustomDashboard[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return [];
      
      const allDashboards: CustomDashboard[] = JSON.parse(stored);
      
      // Filter by user and parse dates
      return allDashboards
        .filter(d => d.owner.id === userId)
        .map(d => ({
          ...d,
          createdAt: new Date(d.createdAt),
          updatedAt: new Date(d.updatedAt),
          timeRange: {
            ...d.timeRange,
            start: d.timeRange.start ? new Date(d.timeRange.start) : undefined,
            end: d.timeRange.end ? new Date(d.timeRange.end) : undefined,
          }
        }));
    } catch (error) {
      console.error('Failed to load dashboards:', error);
      return [];
    }
  }

  /**
   * Get a specific dashboard by ID
   */
  static getDashboard(dashboardId: string): CustomDashboard | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return null;
      
      const allDashboards: CustomDashboard[] = JSON.parse(stored);
      const dashboard = allDashboards.find(d => d.id === dashboardId);
      
      if (!dashboard) return null;
      
      // Parse dates
      return {
        ...dashboard,
        createdAt: new Date(dashboard.createdAt),
        updatedAt: new Date(dashboard.updatedAt),
        timeRange: {
          ...dashboard.timeRange,
          start: dashboard.timeRange.start ? new Date(dashboard.timeRange.start) : undefined,
          end: dashboard.timeRange.end ? new Date(dashboard.timeRange.end) : undefined,
        }
      };
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      return null;
    }
  }

  /**
   * Save a new dashboard
   */
  static saveDashboard(
    formData: DashboardFormData,
    owner: { id: string; name: string; email: string },
    layout?: DashboardLayout
  ): CustomDashboard {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const allDashboards: CustomDashboard[] = stored ? JSON.parse(stored) : [];
      
      const now = new Date();
      const newDashboard: CustomDashboard = {
        id: `dashboard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: formData.name,
        description: formData.description,
        owner,
        metrics: formData.metrics,
        layout: layout || {
          columns: 12,
          widgets: []
        },
        timeRange: formData.timeRange,
        refreshInterval: formData.refreshInterval,
        shared: formData.shared,
        createdAt: now,
        updatedAt: now,
      };
      
      allDashboards.push(newDashboard);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allDashboards));
      
      return newDashboard;
    } catch (error) {
      console.error('Failed to save dashboard:', error);
      throw new Error('Failed to save dashboard');
    }
  }

  /**
   * Update an existing dashboard
   */
  static updateDashboard(
    dashboardId: string,
    updates: Partial<DashboardFormData> & { layout?: DashboardLayout }
  ): CustomDashboard | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return null;
      
      const allDashboards: CustomDashboard[] = JSON.parse(stored);
      const index = allDashboards.findIndex(d => d.id === dashboardId);
      
      if (index === -1) return null;
      
      const updatedDashboard: CustomDashboard = {
        ...allDashboards[index],
        ...updates,
        updatedAt: new Date(),
      };
      
      allDashboards[index] = updatedDashboard;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allDashboards));
      
      // Parse dates before returning
      return {
        ...updatedDashboard,
        createdAt: new Date(updatedDashboard.createdAt),
        updatedAt: new Date(updatedDashboard.updatedAt),
        timeRange: {
          ...updatedDashboard.timeRange,
          start: updatedDashboard.timeRange.start ? new Date(updatedDashboard.timeRange.start) : undefined,
          end: updatedDashboard.timeRange.end ? new Date(updatedDashboard.timeRange.end) : undefined,
        }
      };
    } catch (error) {
      console.error('Failed to update dashboard:', error);
      throw new Error('Failed to update dashboard');
    }
  }

  /**
   * Delete a dashboard
   */
  static deleteDashboard(dashboardId: string): boolean {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return false;
      
      const allDashboards: CustomDashboard[] = JSON.parse(stored);
      const filtered = allDashboards.filter(d => d.id !== dashboardId);
      
      if (filtered.length === allDashboards.length) {
        return false; // Dashboard not found
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Failed to delete dashboard:', error);
      return false;
    }
  }

  /**
   * Update dashboard layout (widget positions)
   */
  static updateLayout(dashboardId: string, layout: DashboardLayout): boolean {
    try {
      const dashboard = this.updateDashboard(dashboardId, { layout });
      return dashboard !== null;
    } catch (error) {
      console.error('Failed to update layout:', error);
      return false;
    }
  }

  /**
   * Add a widget to a dashboard
   */
  static addWidget(dashboardId: string, widget: Widget): boolean {
    try {
      const dashboard = this.getDashboard(dashboardId);
      if (!dashboard) return false;
      
      const updatedLayout: DashboardLayout = {
        ...dashboard.layout,
        widgets: [...dashboard.layout.widgets, widget]
      };
      
      return this.updateLayout(dashboardId, updatedLayout);
    } catch (error) {
      console.error('Failed to add widget:', error);
      return false;
    }
  }

  /**
   * Remove a widget from a dashboard
   */
  static removeWidget(dashboardId: string, widgetId: string): boolean {
    try {
      const dashboard = this.getDashboard(dashboardId);
      if (!dashboard) return false;
      
      const updatedLayout: DashboardLayout = {
        ...dashboard.layout,
        widgets: dashboard.layout.widgets.filter(w => w.id !== widgetId)
      };
      
      return this.updateLayout(dashboardId, updatedLayout);
    } catch (error) {
      console.error('Failed to remove widget:', error);
      return false;
    }
  }
}
