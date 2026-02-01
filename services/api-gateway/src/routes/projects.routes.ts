import { Router } from 'express';
import { createProxyForService } from '../services/serviceProxy';
import { logger } from '../utils/logger';
import { validateRequest } from '../middleware/requestValidator';
import {
  createProjectSchema,
  listProjectsSchema,
  getProjectSchema,
  updateProjectSchema,
  deleteProjectSchema,
  getProjectStatsSchema,
} from '../schemas/projects.schema';

/**
 * Projects Routes
 *
 * Handles all project-related API endpoints and forwards them to the Project Manager service.
 *
 * Endpoints:
 * - GET    /api/v1/projects           - List projects
 * - POST   /api/v1/projects           - Create project
 * - GET    /api/v1/projects/:id       - Get project
 * - PUT    /api/v1/projects/:id       - Update project
 * - DELETE /api/v1/projects/:id       - Delete project
 * - GET    /api/v1/projects/:id/stats - Get project stats
 */

const router = Router();

// Create proxy middleware for project-manager service
// Path rewrite removes /api/v1/projects prefix and forwards to service as /api/projects
const projectsProxy = createProxyForService('project-manager', {
  '^/api/v1/projects': '/api/projects',
});

/**
 * List all projects
 * GET /api/v1/projects
 *
 * Query parameters:
 * - page: number (optional) - Page number for pagination
 * - limit: number (optional) - Number of items per page
 * - status: string (optional) - Filter by project status
 * - search: string (optional) - Search projects by name
 */
router.get('/', validateRequest(listProjectsSchema), projectsProxy);

/**
 * Create a new project
 * POST /api/v1/projects
 *
 * Body:
 * - name: string (required) - Project name
 * - description: string (optional) - Project description
 * - repositoryUrl: string (required) - Git repository URL
 * - settings: object (optional) - Project settings
 */
router.post('/', validateRequest(createProjectSchema), projectsProxy);

/**
 * Get project by ID
 * GET /api/v1/projects/:id
 *
 * Params:
 * - id: string (required) - Project ID
 */
router.get('/:id', validateRequest(getProjectSchema), projectsProxy);

/**
 * Update project
 * PUT /api/v1/projects/:id
 *
 * Params:
 * - id: string (required) - Project ID
 *
 * Body:
 * - name: string (optional) - Project name
 * - description: string (optional) - Project description
 * - settings: object (optional) - Project settings
 */
router.put('/:id', validateRequest(updateProjectSchema), projectsProxy);

/**
 * Delete project
 * DELETE /api/v1/projects/:id
 *
 * Params:
 * - id: string (required) - Project ID
 */
router.delete('/:id', validateRequest(deleteProjectSchema), projectsProxy);

/**
 * Get project statistics
 * GET /api/v1/projects/:id/stats
 *
 * Params:
 * - id: string (required) - Project ID
 *
 * Returns statistics like:
 * - Total reviews
 * - Code quality metrics
 * - Recent activity
 */
router.get('/:id/stats', validateRequest(getProjectStatsSchema), projectsProxy);

logger.info('Projects routes initialized');

export { router as projectsRoutes };
