import { Router, Request, Response } from 'express';
import { serviceRegistry } from '../services/serviceRegistry';
import { logger } from '../utils/logger';

const router = Router();

router.get('/', async (req: Request, res: Response): Promise<void> => {
  try {
    const systemHealth = await serviceRegistry.getSystemHealth();

    const response = {
      status: systemHealth.status,
      timestamp: systemHealth.timestamp.toISOString(),
      service: 'api-gateway',
      version: '1.0.0',
      services: systemHealth.services.map((service) => ({
        name: service.name,
        status: service.status,
        url: service.url,
        responseTime: service.responseTime,
        error: service.error,
        lastChecked: service.lastChecked.toISOString(),
      })),
    };

    const statusCode = systemHealth.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(response);
  } catch (error) {
    logger.error('Health check error:', error);

    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
      version: '1.0.0',
      error: 'Health check failed',
    });
  }
});

export { router as healthCheck };
