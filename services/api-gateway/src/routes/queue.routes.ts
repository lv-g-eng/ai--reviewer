import { Router } from 'express';
import { createProxyForService } from '../services/serviceProxy';
import { logger } from '../utils/logger';

/**
 * Queue Routes
 *
 * Handles all queue management-related API endpoints and forwards them to the appropriate service.
 * The queue service manages asynchronous tasks like code reviews, architecture scans, and AI analysis.
 *
 * Endpoints:
 * - GET    /api/v1/queue              - List queue items
 * - GET    /api/v1/queue/:id          - Get queue item
 * - POST   /api/v1/queue/:id/retry    - Retry failed item
 * - DELETE /api/v1/queue/:id          - Cancel queue item
 */

const router = Router();

// Create proxy middleware for agentic-ai service (which manages the queue)
// Path rewrite removes /api/v1/queue prefix and forwards to service as /api/queue
const queueProxy = createProxyForService('ai-service', {
  '^/api/v1/queue': '/api/queue',
});

/**
 * List all queue items
 * GET /api/v1/queue
 *
 * Query parameters:
 * - page: number (optional) - Page number for pagination
 * - limit: number (optional) - Number of items per page
 * - status: string (optional) - Filter by status (pending, processing, completed, failed)
 * - type: string (optional) - Filter by task type (review, scan, analysis)
 * - projectId: string (optional) - Filter by project ID
 *
 * Returns:
 * - List of queue items with status
 * - Pagination metadata
 */
router.get('/', queueProxy);

/**
 * Get queue item by ID
 * GET /api/v1/queue/:id
 *
 * Params:
 * - id: string (required) - Queue item ID
 *
 * Returns:
 * - Queue item details
 * - Current status
 * - Progress information
 * - Error details (if failed)
 * - Result data (if completed)
 */
router.get('/:id', queueProxy);

/**
 * Retry a failed queue item
 * POST /api/v1/queue/:id/retry
 *
 * Params:
 * - id: string (required) - Queue item ID
 *
 * Body:
 * - priority: string (optional) - Priority level (low, normal, high)
 *
 * Re-queues a failed task for processing
 */
router.post('/:id/retry', queueProxy);

/**
 * Cancel a queue item
 * DELETE /api/v1/queue/:id
 *
 * Params:
 * - id: string (required) - Queue item ID
 *
 * Cancels a pending or processing queue item.
 * Cannot cancel completed items.
 */
router.delete('/:id', queueProxy);

logger.info('Queue routes initialized');

export { router as queueRoutes };
