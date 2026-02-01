import { Router } from 'express';
import { createProxyForService } from '../services/serviceProxy';
import { logger } from '../utils/logger';
import { validateRequest } from '../middleware/requestValidator';
import {
  createReviewSchema,
  listReviewsSchema,
  getReviewSchema,
  updateReviewSchema,
  deleteReviewSchema,
  addCommentSchema,
} from '../schemas/reviews.schema';

/**
 * Reviews Routes
 *
 * Handles all code review-related API endpoints and forwards them to the Code Review Engine service.
 *
 * Endpoints:
 * - GET    /api/v1/reviews            - List reviews
 * - POST   /api/v1/reviews            - Create review
 * - GET    /api/v1/reviews/:id        - Get review
 * - PUT    /api/v1/reviews/:id        - Update review
 * - DELETE /api/v1/reviews/:id        - Delete review
 * - POST   /api/v1/reviews/:id/comments - Add comment
 */

const router = Router();

// Create proxy middleware for code-review service
// Path rewrite removes /api/v1/reviews prefix and forwards to service as /api/reviews
const reviewsProxy = createProxyForService('code-review', {
  '^/api/v1/reviews': '/api/reviews',
});

/**
 * List all reviews
 * GET /api/v1/reviews
 *
 * Query parameters:
 * - page: number (optional) - Page number for pagination
 * - limit: number (optional) - Number of items per page
 * - projectId: string (optional) - Filter by project ID
 * - status: string (optional) - Filter by review status (pending, in_progress, completed)
 * - severity: string (optional) - Filter by severity (low, medium, high, critical)
 */
router.get('/', validateRequest(listReviewsSchema), reviewsProxy);

/**
 * Create a new review
 * POST /api/v1/reviews
 *
 * Body:
 * - projectId: string (required) - Project ID
 * - commitHash: string (required) - Git commit hash
 * - branch: string (optional) - Git branch name
 * - files: array (optional) - Specific files to review
 */
router.post('/', validateRequest(createReviewSchema), reviewsProxy);

/**
 * Get review by ID
 * GET /api/v1/reviews/:id
 *
 * Params:
 * - id: string (required) - Review ID
 *
 * Returns detailed review information including:
 * - Review metadata
 * - Code issues found
 * - Suggestions
 * - Comments
 */
router.get('/:id', validateRequest(getReviewSchema), reviewsProxy);

/**
 * Update review
 * PUT /api/v1/reviews/:id
 *
 * Params:
 * - id: string (required) - Review ID
 *
 * Body:
 * - status: string (optional) - Review status
 * - notes: string (optional) - Review notes
 */
router.put('/:id', validateRequest(updateReviewSchema), reviewsProxy);

/**
 * Delete review
 * DELETE /api/v1/reviews/:id
 *
 * Params:
 * - id: string (required) - Review ID
 */
router.delete('/:id', validateRequest(deleteReviewSchema), reviewsProxy);

/**
 * Add comment to review
 * POST /api/v1/reviews/:id/comments
 *
 * Params:
 * - id: string (required) - Review ID
 *
 * Body:
 * - text: string (required) - Comment text
 * - lineNumber: number (optional) - Line number reference
 * - file: string (optional) - File path reference
 */
router.post('/:id/comments', validateRequest(addCommentSchema), reviewsProxy);

logger.info('Reviews routes initialized');

export { router as reviewsRoutes };
