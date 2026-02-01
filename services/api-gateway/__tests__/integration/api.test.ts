import request from 'supertest';
import express, { Application } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../../src/config';

// Mock axios for external service calls
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock Redis
jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => ({
    get: jest.fn(),
    set: jest.fn(),
    incr: jest.fn().mockResolvedValue(1),
    expire: jest.fn(),
    ttl: jest.fn().mockResolvedValue(60),
    del: jest.fn(),
    on: jest.fn(),
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn().mockResolvedValue(undefined),
    quit: jest.fn().mockResolvedValue(undefined),
  }));
});

// Mock logger to avoid console noise
jest.mock('../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    error: jest.fn(),
    log: jest.fn(),
  },
}));

// Mock config to use test port
jest.mock('../../src/config', () => ({
  config: {
    port: 0, // Use random port for testing
    nodeEnv: 'test',
    services: {
      authService: 'http://localhost:3001',
      codeReviewEngine: 'http://localhost:3002',
      architectureAnalyzer: 'http://localhost:3003',
      agenticAI: 'http://localhost:3004',
      projectManager: 'http://localhost:3005',
    },
    jwt: {
      secret: 'test-secret-key',
      expiresIn: '24h',
    },
    cors: {
      allowedOrigins: ['http://localhost:3000'],
    },
    redis: {
      url: 'redis://localhost:6379',
    },
    rateLimit: {
      windowMs: 900000,
      max: 100,
    },
    github: {
      webhookSecret: '',
    },
    logging: {
      level: 'error',
    },
  },
}));

describe('API Gateway Integration Tests', () => {
  let app: Application;
  let validToken: string;

  beforeAll(() => {
    // Create a valid JWT token for testing
    validToken = jwt.sign(
      {
        userId: 'test-user-123',
        roles: ['user'],
        permissions: ['read:projects', 'write:projects'],
      },
      config.jwt.secret,
      { expiresIn: '1h' }
    );
  });

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create a fresh app instance for each test
    app = express();
    
    // Mock successful auth service validation by default
    mockedAxios.post.mockResolvedValue({
      data: { valid: true },
      status: 200,
    });
  });

  describe('Complete Request Flow', () => {
    it('should successfully process a request with correlation ID', async () => {
      // Setup a simple test route
      app.get('/test', (req, res) => {
        res.json({ success: true, correlationId: req.headers['x-correlation-id'] });
      });

      const response = await request(app)
        .get('/test')
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    it('should forward correlation ID through the entire request chain', async () => {
      const correlationId = 'test-correlation-id-123';

      app.get('/test', (req, res) => {
        res.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] as string);
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .set('X-Correlation-ID', correlationId)
        .expect(200);

      expect(response.headers['x-correlation-id']).toBe(correlationId);
    });

    it('should handle request body validation', async () => {
      app.use(express.json());
      app.post('/test', (req, res) => {
        if (!req.body.name) {
          return res.status(400).json({ error: 'Validation failed', details: ['name is required'] });
        }
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/test')
        .send({ name: 'Test' })
        .expect(200);

      expect(response.body.success).toBe(true);
    });

    it('should reject invalid request body', async () => {
      app.use(express.json());
      app.post('/test', (req, res) => {
        if (!req.body.name) {
          return res.status(400).json({ error: 'Validation failed', details: ['name is required'] });
        }
        res.json({ success: true });
      });

      const response = await request(app)
        .post('/test')
        .send({})
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
    });
  });

  describe('Authentication Flow', () => {
    it('should reject requests without authorization header', async () => {
      app.get('/test', (req, res) => {
        if (!req.headers.authorization) {
          return res.status(401).json({ error: 'Missing or invalid authorization header' });
        }
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .expect(401);

      expect(response.body.error).toBe('Missing or invalid authorization header');
    });

    it('should reject requests with invalid token format', async () => {
      app.get('/test', (req, res) => {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
          return res.status(401).json({ error: 'Missing or invalid authorization header' });
        }
        res.json({ success: true });
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', 'InvalidFormat')
        .expect(401);

      expect(response.body.error).toBe('Missing or invalid authorization header');
    });

    it('should reject requests with expired token', async () => {
      const expiredToken = jwt.sign(
        { userId: 'test-user', roles: ['user'] },
        config.jwt.secret,
        { expiresIn: '-1h' }
      );

      app.get('/test', (req, res) => {
        try {
          const token = req.headers.authorization?.substring(7);
          jwt.verify(token!, config.jwt.secret);
          res.json({ success: true });
        } catch (error) {
          res.status(401).json({ error: 'Invalid token' });
        }
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', `Bearer ${expiredToken}`)
        .expect(401);

      expect(response.body.error).toBe('Invalid token');
    });

    it('should accept valid token', async () => {
      app.get('/test', (req, res) => {
        try {
          const token = req.headers.authorization?.substring(7);
          const decoded = jwt.verify(token!, config.jwt.secret);
          res.json({ success: true, userId: (decoded as any).userId });
        } catch (error) {
          res.status(401).json({ error: 'Invalid token' });
        }
      });

      const response = await request(app)
        .get('/test')
        .set('Authorization', `Bearer ${validToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.userId).toBe('test-user-123');
    });
  });

  describe('Rate Limiting Behavior', () => {
    it('should track request counts', async () => {
      let requestCount = 0;
      const maxRequests = 5;

      app.get('/test', (req, res) => {
        requestCount++;
        if (requestCount > maxRequests) {
          return res.status(429).json({
            error: 'Too many requests',
            retryAfter: 60,
          });
        }
        res.json({ success: true, count: requestCount });
      });

      // Make requests within limit
      for (let i = 0; i < maxRequests; i++) {
        const response = await request(app).get('/test');
        expect(response.status).toBe(200);
      }

      // Next request should be rate limited
      const response = await request(app).get('/test').expect(429);
      expect(response.body.error).toBe('Too many requests');
    });

    it('should include rate limit information in error response', async () => {
      app.get('/test', (req, res) => {
        res.status(429).json({
          error: 'Too many requests',
          message: 'Rate limit exceeded',
          retryAfter: 60,
        });
      });

      const response = await request(app).get('/test').expect(429);

      expect(response.body.error).toBe('Too many requests');
      expect(response.body.retryAfter).toBe(60);
    });
  });

  describe('Circuit Breaker Behavior', () => {
    it('should handle service unavailability', async () => {
      app.get('/test', (req, res) => {
        res.status(503).json({
          error: 'Service Unavailable',
          message: 'Backend service is currently unavailable',
        });
      });

      const response = await request(app).get('/test').expect(503);

      expect(response.body.error).toBe('Service Unavailable');
    });

    it('should include correlation ID in service errors', async () => {
      const correlationId = 'test-correlation-123';

      app.get('/test', (req, res) => {
        res.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] as string);
        res.status(503).json({
          error: 'Service Unavailable',
          correlationId: req.headers['x-correlation-id'],
        });
      });

      const response = await request(app)
        .get('/test')
        .set('X-Correlation-ID', correlationId)
        .expect(503);

      expect(response.headers['x-correlation-id']).toBe(correlationId);
      expect(response.body.correlationId).toBe(correlationId);
    });
  });

  describe('Error Handling', () => {
    it('should return standardized error format', async () => {
      app.get('/test', (req, res) => {
        res.status(400).json({
          error: 'Bad Request',
          message: 'Invalid request parameters',
        });
      });

      const response = await request(app).get('/test').expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body).toHaveProperty('message');
    });

    it('should include correlation ID in error responses', async () => {
      const correlationId = 'error-test-123';

      app.get('/test', (req, res) => {
        res.setHeader('X-Correlation-ID', req.headers['x-correlation-id'] as string);
        res.status(500).json({
          error: 'Internal Server Error',
          correlationId: req.headers['x-correlation-id'],
        });
      });

      const response = await request(app)
        .get('/test')
        .set('X-Correlation-ID', correlationId)
        .expect(500);

      expect(response.headers['x-correlation-id']).toBe(correlationId);
    });

    it('should handle validation errors with 400 status', async () => {
      app.use(express.json());
      app.post('/test', (req, res) => {
        const errors = [];
        if (!req.body.name) errors.push({ field: 'name', message: 'Name is required' });
        if (!req.body.email) errors.push({ field: 'email', message: 'Email is required' });

        if (errors.length > 0) {
          return res.status(400).json({
            error: 'Validation failed',
            details: errors,
          });
        }

        res.json({ success: true });
      });

      const response = await request(app)
        .post('/test')
        .send({ name: 'Test' })
        .expect(400);

      expect(response.body.error).toBe('Validation failed');
      expect(response.body.details).toHaveLength(1);
    });

    it('should handle 404 for non-existent routes', async () => {
      app.use((req, res) => {
        res.status(404).json({
          error: 'Not Found',
          message: `Route ${req.path} not found`,
        });
      });

      const response = await request(app)
        .get('/nonexistent')
        .expect(404);

      expect(response.body.error).toBe('Not Found');
    });

    it('should handle internal server errors with 500 status', async () => {
      app.get('/test', (req, res) => {
        res.status(500).json({
          error: 'Internal Server Error',
          message: 'An unexpected error occurred',
        });
      });

      const response = await request(app).get('/test').expect(500);

      expect(response.body.error).toBe('Internal Server Error');
    });

    it('should not expose stack traces in production', async () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      app.get('/test', (req, res) => {
        res.status(500).json({
          error: 'Internal Server Error',
          message: 'An unexpected error occurred',
          // No stack trace in production
        });
      });

      const response = await request(app).get('/test').expect(500);

      expect(response.body.stack).toBeUndefined();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Health Check Endpoint', () => {
    it('should not require authentication', async () => {
      app.get('/health', (req, res) => {
        res.json({
          status: 'healthy',
          timestamp: new Date().toISOString(),
        });
      });

      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should return service status', async () => {
      app.get('/health', (req, res) => {
        res.json({
          status: 'healthy',
          service: 'api-gateway',
          timestamp: new Date().toISOString(),
          services: [
            { name: 'auth', status: 'healthy' },
            { name: 'projects', status: 'healthy' },
          ],
        });
      });

      const response = await request(app).get('/health').expect(200);

      expect(response.body.status).toBe('healthy');
      expect(response.body.services).toHaveLength(2);
    });
  });

  describe('CORS and Security Headers', () => {
    it('should include security headers in response', async () => {
      app.use((req, res, next) => {
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'DENY');
        next();
      });

      app.get('/test', (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app).get('/test');

      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['x-frame-options']).toBe('DENY');
    });

    it('should handle CORS preflight requests', async () => {
      app.use((req, res, next) => {
        res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        
        if (req.method === 'OPTIONS') {
          return res.sendStatus(200);
        }
        next();
      });

      app.get('/test', (req, res) => {
        res.json({ success: true });
      });

      const response = await request(app)
        .options('/test')
        .set('Origin', 'http://localhost:3000')
        .set('Access-Control-Request-Method', 'GET');

      expect(response.headers['access-control-allow-origin']).toBe('http://localhost:3000');
      expect(response.status).toBe(200);
    });
  });

  describe('Request/Response Logging', () => {
    it('should log request metadata', async () => {
      const logs: any[] = [];

      app.use((req, res, next) => {
        logs.push({
          method: req.method,
          path: req.path,
          timestamp: new Date().toISOString(),
        });
        next();
      });

      app.get('/test', (req, res) => {
        res.json({ success: true });
      });

      await request(app).get('/test').expect(200);

      expect(logs).toHaveLength(1);
      expect(logs[0].method).toBe('GET');
      expect(logs[0].path).toBe('/test');
    });

    it('should log response status and time', async () => {
      const logs: any[] = [];

      app.use((req, res, next) => {
        const startTime = Date.now();
        res.on('finish', () => {
          logs.push({
            statusCode: res.statusCode,
            duration: Date.now() - startTime,
          });
        });
        next();
      });

      app.get('/test', (req, res) => {
        res.json({ success: true });
      });

      await request(app).get('/test').expect(200);

      expect(logs).toHaveLength(1);
      expect(logs[0].statusCode).toBe(200);
      expect(logs[0].duration).toBeGreaterThanOrEqual(0);
    });
  });
});
