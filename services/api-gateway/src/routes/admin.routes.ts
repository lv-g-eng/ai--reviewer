import { Router } from 'express';
import { createProxyForService } from '../services/serviceProxy';
import { logger } from '../utils/logger';
import { validateRequest } from '../middleware/requestValidator';
import {
  listUsersSchema,
  listAuditLogsSchema,
  getSettingsSchema,
  updateSettingsSchema,
} from '../schemas/admin.schema';

/**
 * Admin Routes
 *
 * Handles all administrative API endpoints and forwards them to the Auth service.
 * These routes require admin privileges and are used for system management.
 *
 * Endpoints:
 * - GET    /api/v1/admin/users        - List users
 * - GET    /api/v1/admin/audit-logs   - Get audit logs
 * - GET    /api/v1/admin/settings     - Get settings
 * - PUT    /api/v1/admin/settings     - Update settings
 */

const router = Router();

// Create proxy middleware for auth service (which handles admin operations)
// Path rewrite removes /api/v1/admin prefix and forwards to service as /api/admin
const adminProxy = createProxyForService('auth', {
  '^/api/v1/admin': '/api/admin',
});

/**
 * List all users
 * GET /api/v1/admin/users
 *
 * Query parameters:
 * - page: number (optional) - Page number for pagination
 * - limit: number (optional) - Number of items per page
 * - role: string (optional) - Filter by role (admin, user, viewer)
 * - status: string (optional) - Filter by status (active, inactive, suspended)
 * - search: string (optional) - Search by name or email
 *
 * Returns:
 * - List of users with details
 * - Pagination metadata
 *
 * Requires: Admin role
 */
router.get('/users', validateRequest(listUsersSchema), adminProxy);

/**
 * Get audit logs
 * GET /api/v1/admin/audit-logs
 *
 * Query parameters:
 * - page: number (optional) - Page number for pagination
 * - limit: number (optional) - Number of items per page
 * - userId: string (optional) - Filter by user ID
 * - action: string (optional) - Filter by action type
 * - startDate: string (optional) - Filter from date (ISO 8601)
 * - endDate: string (optional) - Filter to date (ISO 8601)
 * - resource: string (optional) - Filter by resource type
 *
 * Returns:
 * - List of audit log entries
 * - Pagination metadata
 *
 * Requires: Admin role
 */
router.get('/audit-logs', validateRequest(listAuditLogsSchema), adminProxy);

/**
 * Get system settings
 * GET /api/v1/admin/settings
 *
 * Returns:
 * - System configuration
 * - Feature flags
 * - Integration settings
 * - Security settings
 *
 * Requires: Admin role
 */
router.get('/settings', validateRequest(getSettingsSchema), adminProxy);

/**
 * Update system settings
 * PUT /api/v1/admin/settings
 *
 * Body:
 * - settings: object (required) - Settings to update
 *   - featureFlags: object (optional) - Feature flag settings
 *   - integrations: object (optional) - Integration configurations
 *   - security: object (optional) - Security settings
 *   - notifications: object (optional) - Notification settings
 *
 * Returns:
 * - Updated settings
 *
 * Requires: Admin role
 */
router.put('/settings', validateRequest(updateSettingsSchema), adminProxy);

logger.info('Admin routes initialized');

export { router as adminRoutes };
