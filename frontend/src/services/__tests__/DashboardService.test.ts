/**
 * Dashboard Service Tests
 * 
 * Unit tests for dashboard configuration save/load functionality
 */

import { DashboardService } from '../DashboardService';
import { CustomDashboard, DashboardFormData } from '../../types/dashboard';

describe('DashboardService', () => {
  const mockUser = {
    id: 'user_1',
    name: 'Test User',
    email: 'test@example.com'
  };

  const mockFormData: DashboardFormData = {
    name: 'Test Dashboard',
    description: 'A test dashboard',
    metrics: ['metric1', 'metric2'],
    timeRange: {
      type: 'relative',
      value: 7,
      unit: 'day'
    },
    refreshInterval: 30,
    shared: false
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('saveDashboard', () => {
    it('should save a new dashboard to localStorage', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);

      expect(dashboard).toBeDefined();
      expect(dashboard.id).toBeDefined();
      expect(dashboard.name).toBe(mockFormData.name);
      expect(dashboard.owner).toEqual(mockUser);
      expect(dashboard.metrics).toEqual(mockFormData.metrics);
    });

    it('should generate unique IDs for multiple dashboards', () => {
      const dashboard1 = DashboardService.saveDashboard(mockFormData, mockUser);
      const dashboard2 = DashboardService.saveDashboard(mockFormData, mockUser);

      expect(dashboard1.id).not.toBe(dashboard2.id);
    });

    it('should set createdAt and updatedAt timestamps', () => {
      const before = new Date();
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      const after = new Date();

      expect(dashboard.createdAt.getTime()).toBeGreaterThanOrEqual(before.getTime());
      expect(dashboard.createdAt.getTime()).toBeLessThanOrEqual(after.getTime());
      expect(dashboard.updatedAt).toEqual(dashboard.createdAt);
    });

    it('should initialize with empty widget layout', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);

      expect(dashboard.layout).toBeDefined();
      expect(dashboard.layout.columns).toBe(12);
      expect(dashboard.layout.widgets).toEqual([]);
    });
  });

  describe('getDashboards', () => {
    it('should return empty array when no dashboards exist', () => {
      const dashboards = DashboardService.getDashboards(mockUser.id);
      expect(dashboards).toEqual([]);
    });

    it('should return all dashboards for a user', () => {
      DashboardService.saveDashboard(mockFormData, mockUser);
      DashboardService.saveDashboard({ ...mockFormData, name: 'Dashboard 2' }, mockUser);

      const dashboards = DashboardService.getDashboards(mockUser.id);
      expect(dashboards).toHaveLength(2);
    });

    it('should filter dashboards by user ID', () => {
      const user2 = { ...mockUser, id: 'user_2' };
      
      DashboardService.saveDashboard(mockFormData, mockUser);
      DashboardService.saveDashboard(mockFormData, user2);

      const user1Dashboards = DashboardService.getDashboards(mockUser.id);
      const user2Dashboards = DashboardService.getDashboards(user2.id);

      expect(user1Dashboards).toHaveLength(1);
      expect(user2Dashboards).toHaveLength(1);
      expect(user1Dashboards[0].owner.id).toBe(mockUser.id);
      expect(user2Dashboards[0].owner.id).toBe(user2.id);
    });

    it('should parse dates correctly when loading', () => {
      const saved = DashboardService.saveDashboard(mockFormData, mockUser);
      const loaded = DashboardService.getDashboards(mockUser.id)[0];

      expect(loaded.createdAt).toBeInstanceOf(Date);
      expect(loaded.updatedAt).toBeInstanceOf(Date);
      expect(loaded.createdAt.getTime()).toBe(saved.createdAt.getTime());
    });
  });

  describe('getDashboard', () => {
    it('should return null when dashboard does not exist', () => {
      const dashboard = DashboardService.getDashboard('nonexistent');
      expect(dashboard).toBeNull();
    });

    it('should return specific dashboard by ID', () => {
      const saved = DashboardService.saveDashboard(mockFormData, mockUser);
      const loaded = DashboardService.getDashboard(saved.id);

      expect(loaded).toBeDefined();
      expect(loaded?.id).toBe(saved.id);
      expect(loaded?.name).toBe(saved.name);
    });
  });

  describe('updateDashboard', () => {
    it('should update dashboard properties', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const updated = DashboardService.updateDashboard(dashboard.id, {
        name: 'Updated Name',
        description: 'Updated description'
      });

      expect(updated).toBeDefined();
      expect(updated?.name).toBe('Updated Name');
      expect(updated?.description).toBe('Updated description');
      expect(updated?.metrics).toEqual(dashboard.metrics); // Unchanged
    });

    it('should update updatedAt timestamp', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      const originalUpdatedAt = dashboard.updatedAt;

      // Wait a bit to ensure timestamp difference
      setTimeout(() => {
        const updated = DashboardService.updateDashboard(dashboard.id, {
          name: 'Updated'
        });

        expect(updated?.updatedAt.getTime()).toBeGreaterThan(originalUpdatedAt.getTime());
      }, 10);
    });

    it('should return null for nonexistent dashboard', () => {
      const updated = DashboardService.updateDashboard('nonexistent', {
        name: 'Updated'
      });

      expect(updated).toBeNull();
    });
  });

  describe('deleteDashboard', () => {
    it('should delete dashboard from storage', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const deleted = DashboardService.deleteDashboard(dashboard.id);
      expect(deleted).toBe(true);

      const loaded = DashboardService.getDashboard(dashboard.id);
      expect(loaded).toBeNull();
    });

    it('should return false for nonexistent dashboard', () => {
      const deleted = DashboardService.deleteDashboard('nonexistent');
      expect(deleted).toBe(false);
    });

    it('should not affect other dashboards', () => {
      const dashboard1 = DashboardService.saveDashboard(mockFormData, mockUser);
      const dashboard2 = DashboardService.saveDashboard({ ...mockFormData, name: 'Dashboard 2' }, mockUser);

      DashboardService.deleteDashboard(dashboard1.id);

      const remaining = DashboardService.getDashboards(mockUser.id);
      expect(remaining).toHaveLength(1);
      expect(remaining[0].id).toBe(dashboard2.id);
    });
  });

  describe('updateLayout', () => {
    it('should update dashboard layout', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const newLayout = {
        columns: 12,
        widgets: [
          {
            id: 'widget1',
            metricId: 'metric1',
            position: { x: 0, y: 0, w: 6, h: 4 },
            chartType: 'line' as const,
            options: {}
          }
        ]
      };

      const success = DashboardService.updateLayout(dashboard.id, newLayout);
      expect(success).toBe(true);

      const updated = DashboardService.getDashboard(dashboard.id);
      expect(updated?.layout.widgets).toHaveLength(1);
      expect(updated?.layout.widgets[0].id).toBe('widget1');
    });
  });

  describe('addWidget', () => {
    it('should add widget to dashboard', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const widget = {
        id: 'widget1',
        metricId: 'metric1',
        position: { x: 0, y: 0, w: 6, h: 4 },
        chartType: 'line' as const,
        options: {}
      };

      const success = DashboardService.addWidget(dashboard.id, widget);
      expect(success).toBe(true);

      const updated = DashboardService.getDashboard(dashboard.id);
      expect(updated?.layout.widgets).toHaveLength(1);
      expect(updated?.layout.widgets[0]).toEqual(widget);
    });

    it('should preserve existing widgets when adding new one', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const widget1 = {
        id: 'widget1',
        metricId: 'metric1',
        position: { x: 0, y: 0, w: 6, h: 4 },
        chartType: 'line' as const,
        options: {}
      };

      const widget2 = {
        id: 'widget2',
        metricId: 'metric2',
        position: { x: 6, y: 0, w: 6, h: 4 },
        chartType: 'bar' as const,
        options: {}
      };

      DashboardService.addWidget(dashboard.id, widget1);
      DashboardService.addWidget(dashboard.id, widget2);

      const updated = DashboardService.getDashboard(dashboard.id);
      expect(updated?.layout.widgets).toHaveLength(2);
    });
  });

  describe('removeWidget', () => {
    it('should remove widget from dashboard', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const widget = {
        id: 'widget1',
        metricId: 'metric1',
        position: { x: 0, y: 0, w: 6, h: 4 },
        chartType: 'line' as const,
        options: {}
      };

      DashboardService.addWidget(dashboard.id, widget);
      const success = DashboardService.removeWidget(dashboard.id, 'widget1');
      expect(success).toBe(true);

      const updated = DashboardService.getDashboard(dashboard.id);
      expect(updated?.layout.widgets).toHaveLength(0);
    });

    it('should not affect other widgets', () => {
      const dashboard = DashboardService.saveDashboard(mockFormData, mockUser);
      
      const widget1 = {
        id: 'widget1',
        metricId: 'metric1',
        position: { x: 0, y: 0, w: 6, h: 4 },
        chartType: 'line' as const,
        options: {}
      };

      const widget2 = {
        id: 'widget2',
        metricId: 'metric2',
        position: { x: 6, y: 0, w: 6, h: 4 },
        chartType: 'bar' as const,
        options: {}
      };

      DashboardService.addWidget(dashboard.id, widget1);
      DashboardService.addWidget(dashboard.id, widget2);
      DashboardService.removeWidget(dashboard.id, 'widget1');

      const updated = DashboardService.getDashboard(dashboard.id);
      expect(updated?.layout.widgets).toHaveLength(1);
      expect(updated?.layout.widgets[0].id).toBe('widget2');
    });
  });

  describe('error handling', () => {
    it('should handle corrupted localStorage data gracefully', () => {
      localStorage.setItem('custom_dashboards', 'invalid json');
      
      const dashboards = DashboardService.getDashboards(mockUser.id);
      expect(dashboards).toEqual([]);
    });

    it('should handle localStorage errors when saving', () => {
      // Mock localStorage.setItem to throw error
      const originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = jest.fn(() => {
        throw new Error('Storage full');
      });

      expect(() => {
        DashboardService.saveDashboard(mockFormData, mockUser);
      }).toThrow('Failed to save dashboard');

      // Restore original
      Storage.prototype.setItem = originalSetItem;
    });
  });
});
