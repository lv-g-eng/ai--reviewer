/**
 * Validation schemas for Architecture API endpoints
 * Defines request validation for architecture-related operations
 */

import { z } from 'zod';
import { objectIdSchema, nonEmptyStringSchema } from './common.schema';

/**
 * Project ID parameter validation
 */
export const projectIdParamSchema = z.object({
  projectId: objectIdSchema.describe('Project ID'),
});

/**
 * Trigger scan request body
 */
export const triggerScanBodySchema = z.object({
  commitHash: nonEmptyStringSchema
    .max(40, 'Commit hash must be at most 40 characters')
    .optional()
    .describe('Specific commit to scan'),
  deep: z.boolean().default(false).describe('Perform deep analysis'),
});

/**
 * Get graph query parameters
 */
export const getGraphQuerySchema = z.object({
  format: z
    .enum(['json', 'dot', 'mermaid'])
    .default('json')
    .describe('Graph format'),
  depth: z
    .string()
    .optional()
    .transform((val) => (val ? parseInt(val, 10) : undefined))
    .pipe(z.number().int().positive().max(10).optional())
    .describe('Graph depth level (1-10)'),
});

/**
 * Get drift query parameters
 */
export const getDriftQuerySchema = z.object({
  baseline: nonEmptyStringSchema
    .max(40, 'Baseline commit hash must be at most 40 characters')
    .optional()
    .describe('Baseline commit hash for comparison'),
  since: z.string().datetime().optional().describe('ISO date to compare from'),
});

/**
 * Complete request validation schemas
 */

// GET /api/v1/architecture/:projectId
export const getArchitectureSchema = z.object({
  params: projectIdParamSchema,
  query: z.object({}).optional(),
  body: z.object({}).optional(),
});

// POST /api/v1/architecture/:projectId/scan
export const triggerScanSchema = z.object({
  params: projectIdParamSchema,
  body: triggerScanBodySchema,
  query: z.object({}).optional(),
});

// GET /api/v1/architecture/:projectId/graph
export const getGraphSchema = z.object({
  params: projectIdParamSchema,
  query: getGraphQuerySchema,
  body: z.object({}).optional(),
});

// GET /api/v1/architecture/:projectId/drift
export const getDriftSchema = z.object({
  params: projectIdParamSchema,
  query: getDriftQuerySchema,
  body: z.object({}).optional(),
});

// Type exports for TypeScript
export type TriggerScanBody = z.infer<typeof triggerScanBodySchema>;
export type GetGraphQuery = z.infer<typeof getGraphQuerySchema>;
export type GetDriftQuery = z.infer<typeof getDriftQuerySchema>;
