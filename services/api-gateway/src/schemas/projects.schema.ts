/**
 * Validation schemas for Projects API endpoints
 * Defines request validation for project-related operations
 */

import { z } from 'zod';
import {
  paginationSchema,
  sortOrderSchema,
  nonEmptyStringSchema,
  urlSchema,
  tagsSchema,
  metadataSchema,
  idParamSchema,
} from './common.schema';

/**
 * Project status enum
 */
export const projectStatusSchema = z.enum([
  'active',
  'inactive',
  'archived',
  'pending',
]);

/**
 * Repository provider enum
 */
export const repositoryProviderSchema = z.enum([
  'github',
  'gitlab',
  'bitbucket',
  'other',
]);

/**
 * Create project request body
 */
export const createProjectBodySchema = z.object({
  name: nonEmptyStringSchema
    .max(100, 'Project name must be at most 100 characters')
    .describe('Project name'),
  description: z
    .string()
    .min(1, 'Description cannot be empty if provided')
    .max(500, 'Description must be at most 500 characters')
    .trim()
    .optional()
    .describe('Project description'),
  repositoryUrl: urlSchema.describe('Repository URL'),
  repositoryProvider: repositoryProviderSchema
    .default('github')
    .describe('Repository provider'),
  branch: nonEmptyStringSchema
    .max(100, 'Branch name must be at most 100 characters')
    .default('main')
    .describe('Default branch'),
  language: z
    .string()
    .min(1, 'Language cannot be empty if provided')
    .max(50, 'Language must be at most 50 characters')
    .trim()
    .optional()
    .describe('Primary programming language'),
  framework: z
    .string()
    .min(1, 'Framework cannot be empty if provided')
    .max(50, 'Framework must be at most 50 characters')
    .trim()
    .optional()
    .describe('Primary framework'),
  tags: tagsSchema.describe('Project tags'),
  settings: z
    .object({
      autoReview: z
        .boolean()
        .default(true)
        .describe('Enable automatic reviews'),
      reviewOnPush: z.boolean().default(true).describe('Review on push events'),
      reviewOnPR: z.boolean().default(true).describe('Review on pull requests'),
      minCoverageThreshold: z
        .number()
        .min(0)
        .max(100)
        .default(80)
        .describe('Minimum code coverage threshold'),
      enableArchitectureAnalysis: z
        .boolean()
        .default(true)
        .describe('Enable architecture analysis'),
      enableSecurityScan: z
        .boolean()
        .default(true)
        .describe('Enable security scanning'),
    })
    .optional()
    .describe('Project settings'),
  metadata: metadataSchema.describe('Additional metadata'),
});

/**
 * Update project request body
 * All fields are optional for partial updates
 */
export const updateProjectBodySchema = z.object({
  name: nonEmptyStringSchema
    .max(100, 'Project name must be at most 100 characters')
    .optional()
    .describe('Project name'),
  description: z
    .string()
    .min(1, 'Description cannot be empty if provided')
    .max(500, 'Description must be at most 500 characters')
    .trim()
    .optional()
    .describe('Project description'),
  repositoryUrl: urlSchema.optional().describe('Repository URL'),
  repositoryProvider: repositoryProviderSchema
    .optional()
    .describe('Repository provider'),
  branch: nonEmptyStringSchema
    .max(100, 'Branch name must be at most 100 characters')
    .optional()
    .describe('Default branch'),
  language: z
    .string()
    .min(1, 'Language cannot be empty if provided')
    .max(50, 'Language must be at most 50 characters')
    .trim()
    .optional()
    .describe('Primary programming language'),
  framework: z
    .string()
    .min(1, 'Framework cannot be empty if provided')
    .max(50, 'Framework must be at most 50 characters')
    .trim()
    .optional()
    .describe('Primary framework'),
  status: projectStatusSchema.optional().describe('Project status'),
  tags: tagsSchema.describe('Project tags'),
  settings: z
    .object({
      autoReview: z.boolean().optional().describe('Enable automatic reviews'),
      reviewOnPush: z.boolean().optional().describe('Review on push events'),
      reviewOnPR: z.boolean().optional().describe('Review on pull requests'),
      minCoverageThreshold: z
        .number()
        .min(0)
        .max(100)
        .optional()
        .describe('Minimum code coverage threshold'),
      enableArchitectureAnalysis: z
        .boolean()
        .optional()
        .describe('Enable architecture analysis'),
      enableSecurityScan: z
        .boolean()
        .optional()
        .describe('Enable security scanning'),
    })
    .optional()
    .describe('Project settings'),
  metadata: metadataSchema.describe('Additional metadata'),
});

/**
 * List projects query parameters
 */
export const listProjectsQuerySchema = paginationSchema.extend({
  status: projectStatusSchema.optional().describe('Filter by status'),
  language: z
    .string()
    .max(50)
    .optional()
    .describe('Filter by programming language'),
  framework: z.string().max(50).optional().describe('Filter by framework'),
  search: z
    .string()
    .max(200)
    .optional()
    .describe('Search in name and description'),
  sortBy: z
    .enum(['name', 'createdAt', 'updatedAt', 'lastReviewAt'])
    .default('updatedAt')
    .describe('Sort field'),
  sortOrder: sortOrderSchema.describe('Sort order'),
  tags: z.string().optional().describe('Filter by tags (comma-separated)'),
});

/**
 * Get project by ID params
 */
export const getProjectParamsSchema = idParamSchema;

/**
 * Update project params
 */
export const updateProjectParamsSchema = idParamSchema;

/**
 * Delete project params
 */
export const deleteProjectParamsSchema = idParamSchema;

/**
 * Get project stats params
 */
export const getProjectStatsParamsSchema = idParamSchema;

/**
 * Get project stats query parameters
 */
export const getProjectStatsQuerySchema = z.object({
  period: z
    .enum(['day', 'week', 'month', 'year', 'all'])
    .default('month')
    .describe('Time period for statistics'),
  startDate: z
    .string()
    .datetime()
    .optional()
    .describe('Start date for custom period'),
  endDate: z
    .string()
    .datetime()
    .optional()
    .describe('End date for custom period'),
});

/**
 * Complete request validation schemas
 * These combine params, query, and body schemas
 */

// POST /api/v1/projects
export const createProjectSchema = z.object({
  body: createProjectBodySchema,
  query: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/projects
export const listProjectsSchema = z.object({
  query: listProjectsQuerySchema,
  body: z.object({}).optional(),
  params: z.object({}).optional(),
});

// GET /api/v1/projects/:id
export const getProjectSchema = z.object({
  params: getProjectParamsSchema,
  query: z.object({}).optional(),
  body: z.object({}).optional(),
});

// PUT /api/v1/projects/:id
export const updateProjectSchema = z.object({
  params: updateProjectParamsSchema,
  body: updateProjectBodySchema,
  query: z.object({}).optional(),
});

// DELETE /api/v1/projects/:id
export const deleteProjectSchema = z.object({
  params: deleteProjectParamsSchema,
  query: z.object({}).optional(),
  body: z.object({}).optional(),
});

// GET /api/v1/projects/:id/stats
export const getProjectStatsSchema = z.object({
  params: getProjectStatsParamsSchema,
  query: getProjectStatsQuerySchema,
  body: z.object({}).optional(),
});

// Type exports for TypeScript
export type CreateProjectBody = z.infer<typeof createProjectBodySchema>;
export type UpdateProjectBody = z.infer<typeof updateProjectBodySchema>;
export type ListProjectsQuery = z.infer<typeof listProjectsQuerySchema>;
export type ProjectStatus = z.infer<typeof projectStatusSchema>;
export type RepositoryProvider = z.infer<typeof repositoryProviderSchema>;
