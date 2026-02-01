/**
 * Validation schemas for Reviews API endpoints
 * Defines request validation for review-related operations
 */

import { z } from 'zod';
import {
  objectIdSchema,
  paginationSchema,
  sortOrderSchema,
  nonEmptyStringSchema,
  tagsSchema,
  metadataSchema,
  idParamSchema,
} from './common.schema';

/**
 * Review status enum
 */
export const reviewStatusSchema = z.enum([
  'pending',
  'in_progress',
  'completed',
  'failed',
  'cancelled',
]);

/**
 * Review type enum
 */
export const reviewTypeSchema = z.enum([
  'manual',
  'automatic',
  'scheduled',
  'webhook',
]);

/**
 * Review priority enum
 */
export const reviewPrioritySchema = z.enum([
  'low',
  'medium',
  'high',
  'critical',
]);

/**
 * Severity level enum
 */
export const severitySchema = z.enum([
  'info',
  'low',
  'medium',
  'high',
  'critical',
]);

/**
 * Issue category enum
 */
export const issueCategorySchema = z.enum([
  'bug',
  'security',
  'performance',
  'maintainability',
  'style',
  'documentation',
  'best-practice',
  'other',
]);

/**
 * Create review request body
 */
export const createReviewBodySchema = z.object({
  projectId: objectIdSchema.describe('Project ID'),
  commitHash: nonEmptyStringSchema
    .max(40, 'Commit hash must be at most 40 characters')
    .optional()
    .describe('Git commit hash'),
  branch: nonEmptyStringSchema
    .max(100, 'Branch name must be at most 100 characters')
    .optional()
    .describe('Git branch'),
  pullRequestNumber: z
    .number()
    .int()
    .positive()
    .optional()
    .describe('Pull request number'),
  type: reviewTypeSchema.default('manual').describe('Review type'),
  priority: reviewPrioritySchema.default('medium').describe('Review priority'),
  description: z
    .string()
    .min(1, 'Description cannot be empty if provided')
    .max(1000, 'Description must be at most 1000 characters')
    .trim()
    .optional()
    .describe('Review description'),
  files: z
    .array(z.string().min(1).max(500))
    .max(1000)
    .optional()
    .describe('List of files to review (max 1000 files)'),
  options: z
    .object({
      includeTests: z.boolean().default(true).describe('Include test files'),
      includeDocs: z.boolean().default(true).describe('Include documentation'),
      checkSecurity: z.boolean().default(true).describe('Run security checks'),
      checkPerformance: z
        .boolean()
        .default(true)
        .describe('Run performance checks'),
      checkStyle: z.boolean().default(true).describe('Run style checks'),
      checkComplexity: z
        .boolean()
        .default(true)
        .describe('Check code complexity'),
    })
    .optional()
    .describe('Review options'),
  tags: tagsSchema.describe('Review tags'),
  metadata: metadataSchema.describe('Additional metadata'),
});

/**
 * Update review request body
 */
export const updateReviewBodySchema = z.object({
  status: reviewStatusSchema.optional().describe('Review status'),
  priority: reviewPrioritySchema.optional().describe('Review priority'),
  description: z
    .string()
    .min(1, 'Description cannot be empty if provided')
    .max(1000, 'Description must be at most 1000 characters')
    .trim()
    .optional()
    .describe('Review description'),
  tags: tagsSchema.describe('Review tags'),
  metadata: metadataSchema.describe('Additional metadata'),
});

/**
 * List reviews query parameters
 */
export const listReviewsQuerySchema = paginationSchema.extend({
  projectId: objectIdSchema.optional().describe('Filter by project ID'),
  status: reviewStatusSchema.optional().describe('Filter by status'),
  type: reviewTypeSchema.optional().describe('Filter by type'),
  priority: reviewPrioritySchema.optional().describe('Filter by priority'),
  branch: z.string().max(100).optional().describe('Filter by branch'),
  search: z.string().max(200).optional().describe('Search in description'),
  sortBy: z
    .enum(['createdAt', 'updatedAt', 'priority', 'status'])
    .default('createdAt')
    .describe('Sort field'),
  sortOrder: sortOrderSchema.describe('Sort order'),
  startDate: z.string().datetime().optional().describe('Filter by start date'),
  endDate: z.string().datetime().optional().describe('Filter by end date'),
  tags: z.string().optional().describe('Filter by tags (comma-separated)'),
});

/**
 * Get review by ID params
 */
export const getReviewParamsSchema = idParamSchema;

/**
 * Update review params
 */
export const updateReviewParamsSchema = idParamSchema;

/**
 * Delete review params
 */
export const deleteReviewParamsSchema = idParamSchema;

/**
 * Add comment to review params
 */
export const addCommentParamsSchema = idParamSchema;

/**
 * Add comment request body
 */
export const addCommentBodySchema = z.object({
  content: nonEmptyStringSchema
    .max(5000, 'Comment must be at most 5000 characters')
    .describe('Comment content'),
  fileId: objectIdSchema.optional().describe('Related file ID'),
  lineNumber: z
    .number()
    .int()
    .positive()
    .optional()
    .describe('Line number in file'),
  severity: severitySchema.optional().describe('Issue severity'),
  category: issueCategorySchema.optional().describe('Issue category'),
  suggestion: z
    .string()
    .min(1, 'Suggestion cannot be empty if provided')
    .max(2000, 'Suggestion must be at most 2000 characters')
    .trim()
    .optional()
    .describe('Suggested fix'),
  codeSnippet: z.string().max(1000).optional().describe('Related code snippet'),
  metadata: metadataSchema.describe('Additional metadata'),
});

/**
 * Get review comments query parameters
 */
export const getReviewCommentsQuerySchema = paginationSchema.extend({
  severity: severitySchema.optional().describe('Filter by severity'),
  category: issueCategorySchema.optional().describe('Filter by category'),
  fileId: objectIdSchema.optional().describe('Filter by file ID'),
  resolved: z
    .string()
    .optional()
    .transform((val) => val === 'true')
    .pipe(z.boolean())
    .describe('Filter by resolved status'),
  sortBy: z
    .enum(['createdAt', 'severity', 'lineNumber'])
    .default('createdAt')
    .describe('Sort field'),
  sortOrder: sortOrderSchema.describe('Sort order'),
});

/**
 * Get review statistics query parameters
 */
export const getReviewStatsQuerySchema = z.object({
  groupBy: z
    .enum(['severity', 'category', 'file', 'date'])
    .default('severity')
    .describe('Group statistics by'),
});

/**
 * Complete request validation schemas
 */

// POST /api/v1/reviews
export const createReviewSchema = z.object({
  body: createReviewBodySchema,
  query: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/reviews
export const listReviewsSchema = z.object({
  query: listReviewsQuerySchema,
  body: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/reviews/:id
export const getReviewSchema = z.object({
  params: getReviewParamsSchema,
  query: z.object({}).optional(),
  body: z.object({}).optional(),
});

// PUT /api/v1/reviews/:id
export const updateReviewSchema = z.object({
  params: updateReviewParamsSchema,
  body: updateReviewBodySchema,
  query: z.object({}).optional(),
});

// DELETE /api/v1/reviews/:id
export const deleteReviewSchema = z.object({
  params: deleteReviewParamsSchema,
  query: z.object({}).optional(),
  body: z.object({}).optional(),
});

// POST /api/v1/reviews/:id/comments
export const addCommentSchema = z.object({
  params: addCommentParamsSchema,
  body: addCommentBodySchema,
  query: z.object({}).optional(),
});

// GET /api/v1/reviews/:id/comments
export const getReviewCommentsSchema = z.object({
  params: getReviewParamsSchema,
  query: getReviewCommentsQuerySchema,
  body: z.object({}).optional(),
});

// GET /api/v1/reviews/:id/stats
export const getReviewStatsSchema = z.object({
  params: getReviewParamsSchema,
  query: getReviewStatsQuerySchema,
  body: z.object({}).optional(),
});

// Type exports for TypeScript
export type CreateReviewBody = z.infer<typeof createReviewBodySchema>;
export type UpdateReviewBody = z.infer<typeof updateReviewBodySchema>;
export type ListReviewsQuery = z.infer<typeof listReviewsQuerySchema>;
export type AddCommentBody = z.infer<typeof addCommentBodySchema>;
export type ReviewStatus = z.infer<typeof reviewStatusSchema>;
export type ReviewType = z.infer<typeof reviewTypeSchema>;
export type ReviewPriority = z.infer<typeof reviewPrioritySchema>;
export type Severity = z.infer<typeof severitySchema>;
export type IssueCategory = z.infer<typeof issueCategorySchema>;
