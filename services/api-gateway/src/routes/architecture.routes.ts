import { Router } from 'express';
import { createProxyForService } from '../services/serviceProxy';
import { logger } from '../utils/logger';
import { validateRequest } from '../middleware/requestValidator';
import {
  getArchitectureSchema,
  triggerScanSchema,
  getGraphSchema,
  getDriftSchema,
} from '../schemas/architecture.schema';

/**
 * Architecture Routes
 *
 * Handles all architecture analysis-related API endpoints and forwards them to the Architecture Analyzer service.
 *
 * Endpoints:
 * - GET    /api/v1/architecture/:projectId       - Get architecture
 * - POST   /api/v1/architecture/:projectId/scan  - Trigger scan
 * - GET    /api/v1/architecture/:projectId/graph - Get graph data
 * - GET    /api/v1/architecture/:projectId/drift - Get drift analysis
 */

const router = Router();

// Create proxy middleware for architecture service
// Path rewrite removes /api/v1/architecture prefix and forwards to service as /api/architecture
const architectureProxy = createProxyForService('architecture', {
  '^/api/v1/architecture': '/api/architecture',
});

/**
 * Get architecture for a project
 * GET /api/v1/architecture/:projectId
 *
 * Params:
 * - projectId: string (required) - Project ID
 *
 * Returns:
 * - Architecture overview
 * - Component structure
 * - Dependencies
 * - Metrics
 */
router.get(
  '/:projectId',
  validateRequest(getArchitectureSchema),
  architectureProxy
);

/**
 * Trigger architecture scan
 * POST /api/v1/architecture/:projectId/scan
 *
 * Params:
 * - projectId: string (required) - Project ID
 *
 * Body:
 * - commitHash: string (optional) - Specific commit to scan
 * - deep: boolean (optional) - Perform deep analysis
 *
 * Initiates an asynchronous architecture analysis scan
 */
router.post(
  '/:projectId/scan',
  validateRequest(triggerScanSchema),
  architectureProxy
);

/**
 * Get architecture graph data
 * GET /api/v1/architecture/:projectId/graph
 *
 * Params:
 * - projectId: string (required) - Project ID
 *
 * Query parameters:
 * - format: string (optional) - Graph format (json, dot, mermaid)
 * - depth: number (optional) - Graph depth level
 *
 * Returns graph data suitable for visualization
 */
router.get(
  '/:projectId/graph',
  validateRequest(getGraphSchema),
  architectureProxy
);

/**
 * Get architecture drift analysis
 * GET /api/v1/architecture/:projectId/drift
 *
 * Params:
 * - projectId: string (required) - Project ID
 *
 * Query parameters:
 * - baseline: string (optional) - Baseline commit hash for comparison
 * - since: string (optional) - ISO date to compare from
 *
 * Returns:
 * - Drift metrics
 * - Changed components
 * - New dependencies
 * - Removed dependencies
 */
router.get(
  '/:projectId/drift',
  validateRequest(getDriftSchema),
  architectureProxy
);

logger.info('Architecture routes initialized');

export { router as architectureRoutes };
