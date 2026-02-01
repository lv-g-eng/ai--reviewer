import axios from 'axios';
import { ServiceRegistry, ServiceConfig, ServiceHealth } from '../../../src/services/serviceRegistry';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock logger
jest.mock('../../../src/utils/logger', () => ({
  logger: {
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock config
jest.mock('../../../src/config', () => ({
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

describe('ServiceRegistry', () => {
  let registry: ServiceRegistry;

  beforeEach(() => {
    jest.clearAllMocks();
    registry = new ServiceRegistry();
  });

  afterEach(() => {
    registry.clear();
  });

  describe('Service Registration', () => {
    it('should initialize with default services', () => {
      const services = registry.getAllServices();
      expect(services.length).toBe(5);
      
      const serviceNames = services.map(s => s.name);
      expect(serviceNames).toContain('auth');
      expect(serviceNames).toContain('code-review');
      expect(serviceNames).toContain('architecture');
      expect(serviceNames).toContain('ai-service');
      expect(serviceNames).toContain('project-manager');
    });

    it('should register a new service', () => {
      const newService: ServiceConfig = {
        name: 'test-service',
        url: 'http://test:3000',
        healthCheckPath: '/health',
        timeout: 5000,
      };

      registry.registerService(newService);
      
      const service = registry.getService('test-service');
      expect(service).toBeDefined();
      expect(service?.name).toBe('test-service');
      expect(service?.url).toBe('http://test:3000');
    });

    it('should get service by name', () => {
      const service = registry.getService('auth');
      expect(service).toBeDefined();
      expect(service?.name).toBe('auth');
      expect(service?.url).toBe('http://auth:3001');
    });

    it('should return undefined for non-existent service', () => {
      const service = registry.getService('non-existent');
      expect(service).toBeUndefined();
    });

    it('should get service URL by name', () => {
      const url = registry.getServiceUrl('auth');
      expect(url).toBe('http://auth:3001');
    });

    it('should return undefined for non-existent service URL', () => {
      const url = registry.getServiceUrl('non-existent');
      expect(url).toBeUndefined();
    });

    it('should check if service exists', () => {
      expect(registry.hasService('auth')).toBe(true);
      expect(registry.hasService('non-existent')).toBe(false);
    });

    it('should unregister a service', () => {
      const result = registry.unregisterService('auth');
      expect(result).toBe(true);
      expect(registry.hasService('auth')).toBe(false);
    });

    it('should return false when unregistering non-existent service', () => {
      const result = registry.unregisterService('non-existent');
      expect(result).toBe(false);
    });

    it('should clear all services', () => {
      registry.clear();
      const services = registry.getAllServices();
      expect(services.length).toBe(0);
    });
  });

  describe('Health Checks', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('should check service health successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        status: 200,
        data: { status: 'ok' },
      });

      const health = await registry.checkServiceHealth('auth');

      expect(health.name).toBe('auth');
      expect(health.status).toBe('healthy');
      expect(health.url).toBe('http://auth:3001');
      expect(health.responseTime).toBeDefined();
      expect(health.error).toBeUndefined();
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://auth:3001/health',
        expect.objectContaining({
          timeout: 3000,
        })
      );
    });

    it('should handle unhealthy service', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Connection refused'));

      const health = await registry.checkServiceHealth('auth');

      expect(health.name).toBe('auth');
      expect(health.status).toBe('unhealthy');
      expect(health.error).toBe('Connection refused');
      expect(health.responseTime).toBeDefined();
    });

    it('should handle unknown service', async () => {
      const health = await registry.checkServiceHealth('non-existent');

      expect(health.name).toBe('non-existent');
      expect(health.status).toBe('unknown');
      expect(health.error).toBe('Service not registered');
    });

    it('should check all services health', async () => {
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { status: 'ok' },
      });

      const healthStatuses = await registry.checkAllServicesHealth();

      expect(healthStatuses.length).toBe(5);
      expect(mockedAxios.get).toHaveBeenCalledTimes(5);
    });

    it('should cache health status', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        status: 200,
        data: { status: 'ok' },
      });

      await registry.checkServiceHealth('auth');
      const cachedHealth = registry.getCachedHealth('auth');

      expect(cachedHealth).toBeDefined();
      expect(cachedHealth?.status).toBe('healthy');
    });

    it('should get all cached health statuses', async () => {
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { status: 'ok' },
      });

      await registry.checkAllServicesHealth();
      const allCachedHealth = registry.getAllCachedHealth();

      expect(allCachedHealth.length).toBe(5);
    });

    it('should return healthy system status when all services are healthy', async () => {
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { status: 'ok' },
      });

      const systemHealth = await registry.getSystemHealth();

      expect(systemHealth.status).toBe('healthy');
      expect(systemHealth.services.length).toBe(5);
      expect(systemHealth.timestamp).toBeInstanceOf(Date);
    });

    it('should return degraded system status when some services are unhealthy', async () => {
      mockedAxios.get
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } });

      const systemHealth = await registry.getSystemHealth();

      expect(systemHealth.status).toBe('degraded');
      expect(systemHealth.services.length).toBe(5);
    });

    it('should return unhealthy system status when all services are unhealthy', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Connection refused'));

      const systemHealth = await registry.getSystemHealth();

      expect(systemHealth.status).toBe('unhealthy');
      expect(systemHealth.services.length).toBe(5);
    });

    it('should handle timeout in health check', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        message: 'timeout of 3000ms exceeded',
        code: 'ECONNABORTED',
      });

      const health = await registry.checkServiceHealth('auth');

      expect(health.status).toBe('unhealthy');
      expect(health.error).toContain('timeout');
    });

    it('should use custom timeout for service', async () => {
      const customService: ServiceConfig = {
        name: 'custom-service',
        url: 'http://custom:3000',
        healthCheckPath: '/health',
        timeout: 10000,
      };

      registry.registerService(customService);

      mockedAxios.get.mockResolvedValueOnce({
        status: 200,
        data: { status: 'ok' },
      });

      await registry.checkServiceHealth('custom-service');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://custom:3000/health',
        expect.objectContaining({
          timeout: 10000,
        })
      );
    });
  });

  describe('Edge Cases', () => {
    it('should handle service with no timeout specified', async () => {
      const service: ServiceConfig = {
        name: 'no-timeout-service',
        url: 'http://test:3000',
        healthCheckPath: '/health',
      };

      registry.registerService(service);

      mockedAxios.get.mockResolvedValueOnce({
        status: 200,
        data: { status: 'ok' },
      });

      await registry.checkServiceHealth('no-timeout-service');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://test:3000/health',
        expect.objectContaining({
          timeout: 5000, // default timeout
        })
      );
    });

    it('should handle service with custom health check path', async () => {
      const service: ServiceConfig = {
        name: 'custom-health-service',
        url: 'http://test:3000',
        healthCheckPath: '/api/health',
        timeout: 3000,
      };

      registry.registerService(service);

      mockedAxios.get.mockResolvedValueOnce({
        status: 200,
        data: { status: 'ok' },
      });

      await registry.checkServiceHealth('custom-health-service');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://test:3000/api/health',
        expect.any(Object)
      );
    });

    it('should update cached health on subsequent checks', async () => {
      mockedAxios.get
        .mockResolvedValueOnce({ status: 200, data: { status: 'ok' } })
        .mockRejectedValueOnce(new Error('Connection refused'));

      // First check - healthy
      await registry.checkServiceHealth('auth');
      let cachedHealth = registry.getCachedHealth('auth');
      expect(cachedHealth?.status).toBe('healthy');

      // Second check - unhealthy
      await registry.checkServiceHealth('auth');
      cachedHealth = registry.getCachedHealth('auth');
      expect(cachedHealth?.status).toBe('unhealthy');
    });
  });
});
