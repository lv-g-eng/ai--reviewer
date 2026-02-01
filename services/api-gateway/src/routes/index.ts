import { Router } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { config } from '../config';
import { logger } from '../utils/logger';
import { webhookRoutes } from './webhooks';
import { projectsRoutes } from './projects.routes';
import { reviewsRoutes } from './reviews.routes';
import { architectureRoutes } from './architecture.routes';
import { queueRoutes } from './queue.routes';
import { adminRoutes } from './admin.routes';

const router = Router();

// Webhook routes (special handling for GitHub webhooks)
router.use('/webhooks', webhookRoutes);

// API v1 routes - using dedicated route files
router.use('/v1/projects', projectsRoutes);
router.use('/v1/reviews', reviewsRoutes);
router.use('/v1/architecture', architectureRoutes);
router.use('/v1/queue', queueRoutes);
router.use('/v1/admin', adminRoutes);

// Legacy proxy routes to microservices (for backward compatibility)
const createServiceProxy = (serviceName: string, serviceUrl: string) => {
  return createProxyMiddleware({
    target: serviceUrl,
    changeOrigin: true,
    pathRewrite: {
      [`^/api/${serviceName}`]: '/api',
    },
    onError: (err, req, res) => {
      logger.error(`Proxy error for ${serviceName}:`, err);
      res.status(503).json({
        error: {
          code: 'SERVICE_UNAVAILABLE',
          message: `${serviceName} service is currently unavailable`,
          retryable: true,
        },
      });
    },
    onProxyReq: (proxyReq, req) => {
      // Add auth context to proxied requests
      if (req.auth) {
        proxyReq.setHeader('X-User-ID', req.auth.userId);
        proxyReq.setHeader('X-User-Roles', JSON.stringify(req.auth.roles));
        proxyReq.setHeader(
          'X-User-Permissions',
          JSON.stringify(req.auth.permissions)
        );
      }
    },
  });
};

// Legacy service proxy routes (kept for backward compatibility)
router.use('/auth', createServiceProxy('auth', config.services.authService));
router.use(
  '/code-review',
  createServiceProxy('code-review', config.services.codeReviewEngine)
);
router.use('/ai', createServiceProxy('ai', config.services.agenticAI));

logger.info('All routes registered successfully');

export { router as routes };
