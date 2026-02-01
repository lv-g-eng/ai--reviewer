/**
 * Validation schemas for Admin API endpoints
 * Defines request validation for administrative operations
 */

import { z } from 'zod';
import {
  paginationSchema,
  sortOrderSchema,
  isoDateSchema,
} from './common.schema';

/**
 * User role enum
 */
export const userRoleSchema = z.enum(['admin', 'user', 'viewer']);

/**
 * User status enum
 */
export const userStatusSchema = z.enum(['active', 'inactive', 'suspended']);

/**
 * List users query parameters
 */
export const listUsersQuerySchema = paginationSchema.extend({
  role: userRoleSchema.optional().describe('Filter by role'),
  status: userStatusSchema.optional().describe('Filter by status'),
  search: z.string().max(200).optional().describe('Search by name or email'),
  sortBy: z
    .enum(['name', 'email', 'createdAt', 'lastLogin'])
    .default('createdAt')
    .describe('Sort field'),
  sortOrder: sortOrderSchema.describe('Sort order'),
});

/**
 * Audit log action types
 */
export const auditActionSchema = z.enum([
  'create',
  'read',
  'update',
  'delete',
  'login',
  'logout',
  'access_denied',
  'settings_changed',
]);

/**
 * Resource types for audit logs
 */
export const resourceTypeSchema = z.enum([
  'user',
  'project',
  'review',
  'settings',
  'architecture',
  'webhook',
]);

/**
 * List audit logs query parameters
 */
export const listAuditLogsQuerySchema = paginationSchema.extend({
  userId: z.string().optional().describe('Filter by user ID'),
  action: auditActionSchema.optional().describe('Filter by action type'),
  resource: resourceTypeSchema.optional().describe('Filter by resource type'),
  startDate: isoDateSchema.optional().describe('Filter from date'),
  endDate: isoDateSchema.optional().describe('Filter to date'),
  sortBy: z
    .enum(['timestamp', 'action', 'userId'])
    .default('timestamp')
    .describe('Sort field'),
  sortOrder: sortOrderSchema.describe('Sort order'),
});

/**
 * System settings update body
 */
export const updateSettingsBodySchema = z.object({
  featureFlags: z
    .record(z.string(), z.boolean())
    .optional()
    .describe('Feature flag settings'),
  integrations: z
    .object({
      github: z
        .object({
          enabled: z.boolean().optional(),
          webhookSecret: z.string().optional(),
        })
        .optional(),
      gitlab: z
        .object({
          enabled: z.boolean().optional(),
          webhookSecret: z.string().optional(),
        })
        .optional(),
      slack: z
        .object({
          enabled: z.boolean().optional(),
          webhookUrl: z.string().url().optional(),
        })
        .optional(),
    })
    .optional()
    .describe('Integration configurations'),
  security: z
    .object({
      sessionTimeout: z.number().int().positive().optional(),
      maxLoginAttempts: z.number().int().positive().optional(),
      passwordMinLength: z.number().int().min(8).max(128).optional(),
      requireMfa: z.boolean().optional(),
    })
    .optional()
    .describe('Security settings'),
  notifications: z
    .object({
      emailEnabled: z.boolean().optional(),
      slackEnabled: z.boolean().optional(),
      webhookEnabled: z.boolean().optional(),
    })
    .optional()
    .describe('Notification settings'),
});

/**
 * Complete request validation schemas
 */

// GET /api/v1/admin/users
export const listUsersSchema = z.object({
  query: listUsersQuerySchema,
  body: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/admin/audit-logs
export const listAuditLogsSchema = z.object({
  query: listAuditLogsQuerySchema,
  body: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/admin/settings
export const getSettingsSchema = z.object({
  query: z.object({}).optional(),
  body: z.object({}).optional(),
  params: z.object({}).optional(),
});

// PUT /api/v1/admin/settings
export const updateSettingsSchema = z.object({
  body: updateSettingsBodySchema,
  query: z.object({}).optional(),
  params: z.object({}).optional(),
});

// Type exports for TypeScript
export type ListUsersQuery = z.infer<typeof listUsersQuerySchema>;
export type ListAuditLogsQuery = z.infer<typeof listAuditLogsQuerySchema>;
export type UpdateSettingsBody = z.infer<typeof updateSettingsBodySchema>;
export type UserRole = z.infer<typeof userRoleSchema>;
export type UserStatus = z.infer<typeof userStatusSchema>;
export type AuditAction = z.infer<typeof auditActionSchema>;
export type ResourceType = z.infer<typeof resourceTypeSchema>;
