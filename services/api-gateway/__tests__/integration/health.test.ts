import request from 'supertest';
import express from 'express';
import { healthCheck } from '../../src/routes/health';
import { serviceRegistry } from '../../src/services/serviceRegistry';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock logger
jest.mock('../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock config
jest.mock('../../src/config', () => ({
  config: {
    services: {
      authService: 'http://auth:3001',
      codeReviewEngine: 'http://code-review:3002',
      architectureAnalyzer: 'http://architecture:3003',
      agenticAI: 'http://ai-service:3004',
      projectManager: 'http://project-manager:3005',
    },
  },
}));

describe('Health Check Integration', () => {
  let app: express.Application;

  beforeAll(() => {
    app = express();
    app.use('/health', healthCheck);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return 200 when all services are healthy', async () => {
    mockedAxios.get.mockResolvedValue({
      status: 200,
      data: { status: 'ok' },
    });

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('healthy');
    expect(response.body.service).toBe('api-gateway');
    expect(response.body.services).toHaveLength(5);
    expect(response.body.services.every((s: any) => s.status === 'healthy')).toBe(true);
  });

  it('should return 503 when some services are unhealthy', async () => {
    mockedAxios.get
      .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
      .mockRejectedValueOnce(new Error('Connection refused'))
      .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
      .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
      .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } });

    const response = await request(app).get('/health');

    expect(response.status).toBe(503);
    expect(response.body.status).toBe('degraded');
    expect(response.body.services).toHaveLength(5);
  });

  it('should return 503 when all services are unhealthy', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Connection refused'));

    const response = await request(app).get('/health');

    expect(response.status).toBe(503);
    expect(response.body.status).toBe('unhealthy');
    expect(response.body.services).toHaveLength(5);
    expect(response.body.services.every((s: any) => s.status === 'unhealthy')).toBe(true);
  });

  it('should include response times in health check', async () => {
    mockedAxios.get.mockResolvedValue({
      status: 200,
      data: { status: 'ok' },
    });

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.services[0].responseTime).toBeDefined();
    expect(typeof response.body.services[0].responseTime).toBe('number');
  });

  it('should include timestamp in response', async () => {
    mockedAxios.get.mockResolvedValue({
      status: 200,
      data: { status: 'ok' },
    });

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.timestamp).toBeDefined();
    expect(new Date(response.body.timestamp).toString()).not.toBe('Invalid Date');
  });

  it('should include service URLs in response', async () => {
    mockedAxios.get.mockResolvedValue({
      status: 200,
      data: { status: 'ok' },
    });

    const response = await request(app).get('/health');

    expect(response.status).toBe(200);
    expect(response.body.services[0].url).toBeDefined();
    expect(response.body.services[0].url).toContain('http://');
  });

  it('should include error messages for unhealthy services', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Connection timeout'));

    const response = await request(app).get('/health');

    expect(response.status).toBe(503);
    expect(response.body.services[0].error).toBeDefined();
    expect(response.body.services[0].error).toContain('Connection timeout');
  });
});
