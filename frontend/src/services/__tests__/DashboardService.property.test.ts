/**
 * Dashboard Service Property-Based Tests
 * 
 * Feature: frontend-production-optimization, Property 20: 自定义仪表板持久化
 * 
 * **Validates: Requirements 6.1**
 * 
 * Property-based tests to verify that any created custom dashboard configuration
 * can be saved and loaded correctly with round-trip consistency.
 */

import fc from 'fast-check';
import { DashboardService } from '../DashboardService';
import { CustomDashboard, DashboardFormData, TimeRange, Widget } from '../../types/dashboard';

describe('DashboardService Property-Based Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  // Arbitraries for generating test data
  const userArbitrary = fc.record({
    id: fc.string({ minLength: 1, maxLength: 50 }),
    name: fc.string({ minLength: 1, maxLength: 100 }),
    email: fc.emailAddress(),
  });

  const timeRangeRelativeArbitrary = fc.record({
    type: fc.constant('relative' as const),
    value: fc.integer({ min: 1, max: 365 }),
    unit: fc.constantFrom('minute', 'hour', 'day', 'week', 'month'),
  });

  const timeRangeAbsoluteArbitrary = fc.record({
    type: fc.constant('absolute' as const),
    start: fc.date({ min: new Date('2020-01-01'), max: new Date('2025-12-31') }).filter(d => !isNaN(d.getTime())),
    end: fc.date({ min: new Date('2020-01-01'), max: new Date('2025-12-31') }).filter(d => !isNaN(d.getTime())),
  });

  const timeRangeArbitrary = fc.oneof(
    timeRangeRelativeArbitrary,
    timeRangeAbsoluteArbitrary
  );

  const dashboardFormDataArbitrary = fc.record({
    name: fc.string({ minLength: 1, maxLength: 100 }),
    description: fc.option(fc.string({ minLength: 0, maxLength: 500 }), { nil: undefined }),
    metrics: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 20 }),
    timeRange: timeRangeArbitrary,
    refreshInterval: fc.integer({ min: 5, max: 300 }),
    shared: fc.boolean(),
  });

  const widgetArbitrary = fc.record({
    id: fc.string({ minLength: 1, maxLength: 50 }),
    metricId: fc.string({ minLength: 1, maxLength: 50 }),
    position: fc.record({
      x: fc.integer({ min: 0, max: 11 }),
      y: fc.integer({ min: 0, max: 100 }),
      w: fc.integer({ min: 1, max: 12 }),
      h: fc.integer({ min: 1, max: 20 }),
    }),
    chartType: fc.constantFrom('line', 'bar', 'pie', 'gauge', 'number'),
    // Use JSON-safe values only (no undefined, functions, etc.)
    options: fc.dictionary(
      fc.string({ minLength: 1, maxLength: 20 }),
      fc.oneof(fc.string(), fc.integer(), fc.boolean(), fc.constant(null))
    ),
  });

  const layoutArbitrary = fc.record({
    columns: fc.integer({ min: 1, max: 24 }),
    widgets: fc.array(widgetArbitrary, { minLength: 0, maxLength: 10 }),
  });

  /**
   * Property 20: 自定义仪表板持久化
   * 
   * For any created custom dashboard configuration, it should be possible to save
   * and correctly load it on subsequent access.
   * 
   * This test verifies round-trip consistency: save → load → verify equality
   */
  it('should persist and load any dashboard configuration correctly', () => {
    fc.assert(
      fc.property(
        dashboardFormDataArbitrary,
        userArbitrary,
        fc.option(layoutArbitrary, { nil: undefined }),
        (formData, user, layout) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save the dashboard
          const saved = DashboardService.saveDashboard(formData, user, layout);

          // Load it back
          const loaded = DashboardService.getDashboard(saved.id);

          // Verify it was loaded successfully
          expect(loaded).not.toBeNull();
          if (!loaded) return false;

          // Verify all properties match
          expect(loaded.id).toBe(saved.id);
          expect(loaded.name).toBe(formData.name);
          expect(loaded.description).toBe(formData.description);
          expect(loaded.owner).toEqual(user);
          expect(loaded.metrics).toEqual(formData.metrics);
          expect(loaded.refreshInterval).toBe(formData.refreshInterval);
          expect(loaded.shared).toBe(formData.shared);

          // Verify time range
          expect(loaded.timeRange.type).toBe(formData.timeRange.type);
          if (formData.timeRange.type === 'relative') {
            expect(loaded.timeRange.value).toBe(formData.timeRange.value);
            expect(loaded.timeRange.unit).toBe(formData.timeRange.unit);
          } else {
            expect(loaded.timeRange.start).toEqual(formData.timeRange.start);
            expect(loaded.timeRange.end).toEqual(formData.timeRange.end);
          }

          // Verify layout (use deep comparison that handles JSON serialization)
          if (layout) {
            expect(loaded.layout.columns).toBe(layout.columns);
            expect(loaded.layout.widgets.length).toBe(layout.widgets.length);
            // Compare widgets with JSON serialization in mind
            for (let i = 0; i < layout.widgets.length; i++) {
              const loadedWidget = loaded.layout.widgets[i];
              const expectedWidget = layout.widgets[i];
              expect(loadedWidget.id).toBe(expectedWidget.id);
              expect(loadedWidget.metricId).toBe(expectedWidget.metricId);
              expect(loadedWidget.position).toEqual(expectedWidget.position);
              expect(loadedWidget.chartType).toBe(expectedWidget.chartType);
              // Options may have been JSON serialized, so compare as JSON
              expect(JSON.stringify(loadedWidget.options)).toBe(JSON.stringify(expectedWidget.options));
            }
          } else {
            expect(loaded.layout.columns).toBe(12);
            expect(loaded.layout.widgets).toEqual([]);
          }

          // Verify timestamps are valid dates
          expect(loaded.createdAt).toBeInstanceOf(Date);
          expect(loaded.updatedAt).toBeInstanceOf(Date);
          expect(loaded.createdAt.getTime()).toBe(saved.createdAt.getTime());
          expect(loaded.updatedAt.getTime()).toBe(saved.updatedAt.getTime());

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Multiple dashboards should be independently persisted
   * 
   * For any set of dashboard configurations, each should be saved and loaded
   * independently without affecting others.
   */
  it('should persist multiple dashboards independently', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(dashboardFormDataArbitrary, userArbitrary),
          { minLength: 1, maxLength: 10 }
        ),
        (dashboardsData) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save all dashboards
          const savedDashboards = dashboardsData.map(([formData, user]) =>
            DashboardService.saveDashboard(formData, user)
          );

          // Verify each can be loaded independently
          for (let i = 0; i < savedDashboards.length; i++) {
            const saved = savedDashboards[i];
            const loaded = DashboardService.getDashboard(saved.id);

            expect(loaded).not.toBeNull();
            if (!loaded) return false;

            expect(loaded.id).toBe(saved.id);
            expect(loaded.name).toBe(saved.name);
            expect(loaded.owner).toEqual(saved.owner);
          }

          // Verify all dashboards are in storage
          const allUsers = dashboardsData.map(([_, user]) => user);
          const uniqueUserIds = [...new Set(allUsers.map(u => u.id))];

          for (const userId of uniqueUserIds) {
            const userDashboards = DashboardService.getDashboards(userId);
            const expectedCount = savedDashboards.filter(d => d.owner.id === userId).length;
            expect(userDashboards.length).toBe(expectedCount);
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Dashboard updates should preserve identity and update timestamp
   * 
   * For any dashboard and any valid updates, the updated dashboard should
   * maintain the same ID, update the modified fields, and have a newer timestamp.
   */
  it('should update dashboards while preserving identity', () => {
    fc.assert(
      fc.property(
        dashboardFormDataArbitrary,
        userArbitrary,
        fc.record({
          name: fc.option(fc.string({ minLength: 1, maxLength: 100 })),
          description: fc.option(fc.string({ minLength: 0, maxLength: 500 })),
          metrics: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 20 })),
          refreshInterval: fc.option(fc.integer({ min: 5, max: 300 })),
          shared: fc.option(fc.boolean()),
        }),
        (formData, user, updates) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save initial dashboard
          const saved = DashboardService.saveDashboard(formData, user);
          const originalCreatedAt = saved.createdAt;

          // Apply updates
          const updated = DashboardService.updateDashboard(saved.id, updates);

          expect(updated).not.toBeNull();
          if (!updated) return false;

          // ID should remain the same
          expect(updated.id).toBe(saved.id);

          // Updated fields should reflect changes
          if (updates.name !== undefined && updates.name !== null) {
            expect(updated.name).toBe(updates.name);
          }
          if (updates.description !== undefined) {
            expect(updated.description).toBe(updates.description);
          }
          if (updates.metrics !== undefined && updates.metrics !== null) {
            expect(updated.metrics).toEqual(updates.metrics);
          }
          if (updates.refreshInterval !== undefined && updates.refreshInterval !== null) {
            expect(updated.refreshInterval).toBe(updates.refreshInterval);
          }
          if (updates.shared !== undefined && updates.shared !== null) {
            expect(updated.shared).toBe(updates.shared);
          }

          // CreatedAt should remain unchanged
          expect(updated.createdAt).toBeInstanceOf(Date);
          expect(updated.createdAt.getTime()).toBe(originalCreatedAt.getTime());

          // UpdatedAt should be equal or later (may be same if update is very fast)
          expect(updated.updatedAt).toBeInstanceOf(Date);
          expect(updated.updatedAt.getTime()).toBeGreaterThanOrEqual(originalCreatedAt.getTime());

          // Verify persistence
          const loaded = DashboardService.getDashboard(saved.id);
          expect(loaded).not.toBeNull();
          if (!loaded) return false;
          expect(loaded.id).toBe(updated.id);
          expect(loaded.name).toBe(updated.name);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Dashboard deletion should remove only the specified dashboard
   * 
   * For any set of dashboards, deleting one should remove only that dashboard
   * and leave all others intact.
   */
  it('should delete specific dashboard without affecting others', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(dashboardFormDataArbitrary, userArbitrary),
          { minLength: 2, maxLength: 10 }
        ),
        fc.integer({ min: 0, max: 9 }),
        (dashboardsData, deleteIndex) => {
          if (deleteIndex >= dashboardsData.length) return true;

          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save all dashboards
          const savedDashboards = dashboardsData.map(([formData, user]) =>
            DashboardService.saveDashboard(formData, user)
          );

          // Delete one dashboard
          const toDelete = savedDashboards[deleteIndex];
          const deleted = DashboardService.deleteDashboard(toDelete.id);
          expect(deleted).toBe(true);

          // Verify it's gone
          const loadedDeleted = DashboardService.getDashboard(toDelete.id);
          expect(loadedDeleted).toBeNull();

          // Verify others still exist
          for (let i = 0; i < savedDashboards.length; i++) {
            if (i === deleteIndex) continue;

            const loaded = DashboardService.getDashboard(savedDashboards[i].id);
            expect(loaded).not.toBeNull();
            if (!loaded) return false;
            expect(loaded.id).toBe(savedDashboards[i].id);
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Widget operations should maintain dashboard integrity
   * 
   * For any dashboard, adding and removing widgets should correctly update
   * the layout while preserving other dashboard properties.
   */
  it('should maintain dashboard integrity during widget operations', () => {
    fc.assert(
      fc.property(
        dashboardFormDataArbitrary,
        userArbitrary,
        fc.array(widgetArbitrary, { minLength: 1, maxLength: 5 }),
        (formData, user, widgets) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save dashboard
          const saved = DashboardService.saveDashboard(formData, user);

          // Add widgets one by one
          for (const widget of widgets) {
            const success = DashboardService.addWidget(saved.id, widget);
            expect(success).toBe(true);
          }

          // Verify all widgets are present
          const loaded = DashboardService.getDashboard(saved.id);
          expect(loaded).not.toBeNull();
          if (!loaded) return false;

          expect(loaded.layout.widgets).toHaveLength(widgets.length);
          // Compare widgets with JSON serialization in mind
          for (let i = 0; i < widgets.length; i++) {
            expect(loaded.layout.widgets[i].id).toBe(widgets[i].id);
            expect(loaded.layout.widgets[i].metricId).toBe(widgets[i].metricId);
            expect(JSON.stringify(loaded.layout.widgets[i].options)).toBe(JSON.stringify(widgets[i].options));
          }

          // Other properties should remain unchanged
          expect(loaded.name).toBe(formData.name);
          expect(loaded.metrics).toEqual(formData.metrics);

          // Remove widgets one by one
          for (const widget of widgets) {
            const success = DashboardService.removeWidget(saved.id, widget.id);
            expect(success).toBe(true);
          }

          // Verify all widgets are removed
          const loadedAfterRemoval = DashboardService.getDashboard(saved.id);
          expect(loadedAfterRemoval).not.toBeNull();
          if (!loadedAfterRemoval) return false;

          expect(loadedAfterRemoval.layout.widgets).toHaveLength(0);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: User isolation - dashboards should be filtered by user
   * 
   * For any set of dashboards belonging to different users, each user
   * should only see their own dashboards.
   */
  it('should isolate dashboards by user', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.tuple(dashboardFormDataArbitrary, userArbitrary),
          { minLength: 2, maxLength: 10 }
        ),
        (dashboardsData) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save all dashboards
          const savedDashboards = dashboardsData.map(([formData, user]) =>
            DashboardService.saveDashboard(formData, user)
          );

          // Group by user
          const dashboardsByUser = new Map<string, typeof savedDashboards>();
          for (const dashboard of savedDashboards) {
            const userId = dashboard.owner.id;
            if (!dashboardsByUser.has(userId)) {
              dashboardsByUser.set(userId, []);
            }
            dashboardsByUser.get(userId)!.push(dashboard);
          }

          // Verify each user sees only their dashboards
          for (const [userId, expectedDashboards] of dashboardsByUser) {
            const userDashboards = DashboardService.getDashboards(userId);
            expect(userDashboards).toHaveLength(expectedDashboards.length);

            // All returned dashboards should belong to this user
            for (const dashboard of userDashboards) {
              expect(dashboard.owner.id).toBe(userId);
            }

            // All expected dashboards should be present
            const loadedIds = new Set(userDashboards.map(d => d.id));
            for (const expected of expectedDashboards) {
              expect(loadedIds.has(expected.id)).toBe(true);
            }
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Layout updates should preserve dashboard metadata
   * 
   * For any dashboard and any layout update, the dashboard metadata
   * (name, metrics, owner, etc.) should remain unchanged.
   */
  it('should preserve metadata when updating layout', () => {
    fc.assert(
      fc.property(
        dashboardFormDataArbitrary,
        userArbitrary,
        layoutArbitrary,
        layoutArbitrary,
        (formData, user, initialLayout, newLayout) => {
          // Clear localStorage to ensure test isolation
          localStorage.clear();

          // Save dashboard with initial layout
          const saved = DashboardService.saveDashboard(formData, user, initialLayout);

          // Update layout
          const success = DashboardService.updateLayout(saved.id, newLayout);
          expect(success).toBe(true);

          // Load and verify
          const loaded = DashboardService.getDashboard(saved.id);
          expect(loaded).not.toBeNull();
          if (!loaded) return false;

          // Layout should be updated (compare with JSON serialization in mind)
          expect(loaded.layout.columns).toBe(newLayout.columns);
          expect(loaded.layout.widgets.length).toBe(newLayout.widgets.length);
          for (let i = 0; i < newLayout.widgets.length; i++) {
            expect(loaded.layout.widgets[i].id).toBe(newLayout.widgets[i].id);
            expect(JSON.stringify(loaded.layout.widgets[i].options)).toBe(JSON.stringify(newLayout.widgets[i].options));
          }

          // Metadata should be preserved
          expect(loaded.name).toBe(formData.name);
          expect(loaded.description).toBe(formData.description);
          expect(loaded.owner).toEqual(user);
          expect(loaded.metrics).toEqual(formData.metrics);
          expect(loaded.refreshInterval).toBe(formData.refreshInterval);
          expect(loaded.shared).toBe(formData.shared);

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Error handling - corrupted data should not crash the service
   * 
   * The service should handle corrupted localStorage data gracefully
   * and return empty results rather than throwing errors.
   */
  it('should handle corrupted data gracefully', () => {
    fc.assert(
      fc.property(
        fc.string(),
        userArbitrary,
        (corruptedData, user) => {
          // Set corrupted data
          localStorage.setItem('custom_dashboards', corruptedData);

          // Should not throw
          const dashboards = DashboardService.getDashboards(user.id);
          expect(dashboards).toEqual([]);

          const dashboard = DashboardService.getDashboard('any-id');
          expect(dashboard).toBeNull();

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });
});
