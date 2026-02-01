import axios, { AxiosError } from 'axios';
import { logger } from '../utils/logger';
import { config } from '../config';

/**
 * Service configuration interface
 */
export interface ServiceConfig {
  name: string;
  url: string;
  healthCheckPath: string;
  timeout?: number;
}

/**
 * Service health status
 */
export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  url: string;
  lastChecked: Date;
  responseTime?: number;
  error?: string;
}

/**
 * Service Registry
 * Manages the configuration and discovery of all backend microservices
 */
export class ServiceRegistry {
  private services: Map<string, ServiceConfig>;
  private healthCache: Map<string, ServiceHealth>;
  private readonly defaultTimeout: number = 5000; // 5 seconds

  constructor() {
    this.services = new Map();
    this.healthCache = new Map();
    this.initializeServices();
  }

  /**
   * Initialize services from configuration
   */
  private initializeServices(): void {
    // Register services from config
    this.registerService({
      name: 'auth',
      url: config.services.authService,
      healthCheckPath: '/health',
      timeout: 3000,
    });

    this.registerService({
      name: 'code-review',
      url: config.services.codeReviewEngine,
      healthCheckPath: '/health',
      timeout: 5000,
    });

    this.registerService({
      name: 'architecture',
      url: config.services.architectureAnalyzer,
      healthCheckPath: '/health',
      timeout: 5000,
    });

    this.registerService({
      name: 'ai-service',
      url: config.services.agenticAI,
      healthCheckPath: '/health',
      timeout: 10000, // AI service may take longer
    });

    this.registerService({
      name: 'project-manager',
      url: config.services.projectManager,
      healthCheckPath: '/health',
      timeout: 3000,
    });

    logger.info('Service registry initialized', {
      serviceCount: this.services.size,
      services: Array.from(this.services.keys()),
    });
  }

  /**
   * Register a new service
   */
  public registerService(serviceConfig: ServiceConfig): void {
    this.services.set(serviceConfig.name, serviceConfig);
    logger.info(`Service registered: ${serviceConfig.name}`, {
      url: serviceConfig.url,
      healthCheckPath: serviceConfig.healthCheckPath,
    });
  }

  /**
   * Get service configuration by name
   */
  public getService(name: string): ServiceConfig | undefined {
    return this.services.get(name);
  }

  /**
   * Get service URL by name
   */
  public getServiceUrl(name: string): string | undefined {
    const service = this.services.get(name);
    return service?.url;
  }

  /**
   * Get all registered services
   */
  public getAllServices(): ServiceConfig[] {
    return Array.from(this.services.values());
  }

  /**
   * Check if a service is registered
   */
  public hasService(name: string): boolean {
    return this.services.has(name);
  }

  /**
   * Check health of a specific service
   */
  public async checkServiceHealth(name: string): Promise<ServiceHealth> {
    const service = this.services.get(name);

    if (!service) {
      const health: ServiceHealth = {
        name,
        status: 'unknown',
        url: 'unknown',
        lastChecked: new Date(),
        error: 'Service not registered',
      };
      this.healthCache.set(name, health);
      return health;
    }

    const startTime = Date.now();
    const healthCheckUrl = `${service.url}${service.healthCheckPath}`;

    try {
      const response = await axios.get(healthCheckUrl, {
        timeout: service.timeout || this.defaultTimeout,
        validateStatus: (status) => status >= 200 && status < 300,
      });

      const responseTime = Date.now() - startTime;

      const health: ServiceHealth = {
        name: service.name,
        status: 'healthy',
        url: service.url,
        lastChecked: new Date(),
        responseTime,
      };

      this.healthCache.set(name, health);

      logger.debug(`Health check passed for ${name}`, {
        responseTime,
        status: response.status,
      });

      return health;
    } catch (error) {
      const responseTime = Date.now() - startTime;
      let errorMessage = 'Unknown error';

      if (error instanceof AxiosError) {
        errorMessage = error.message;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      } else if (
        typeof error === 'object' &&
        error !== null &&
        'message' in error
      ) {
        errorMessage = String(error.message);
      }

      const health: ServiceHealth = {
        name: service.name,
        status: 'unhealthy',
        url: service.url,
        lastChecked: new Date(),
        responseTime,
        error: errorMessage,
      };

      this.healthCache.set(name, health);

      logger.warn(`Health check failed for ${name}`, {
        error: errorMessage,
        responseTime,
      });

      return health;
    }
  }

  /**
   * Check health of all registered services
   */
  public async checkAllServicesHealth(): Promise<ServiceHealth[]> {
    const healthChecks = Array.from(this.services.keys()).map((name) =>
      this.checkServiceHealth(name)
    );

    return Promise.all(healthChecks);
  }

  /**
   * Get cached health status for a service
   */
  public getCachedHealth(name: string): ServiceHealth | undefined {
    return this.healthCache.get(name);
  }

  /**
   * Get cached health status for all services
   */
  public getAllCachedHealth(): ServiceHealth[] {
    return Array.from(this.healthCache.values());
  }

  /**
   * Get overall system health status
   */
  public async getSystemHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    services: ServiceHealth[];
    timestamp: Date;
  }> {
    const services = await this.checkAllServicesHealth();

    const healthyCount = services.filter((s) => s.status === 'healthy').length;
    const totalCount = services.length;

    let status: 'healthy' | 'degraded' | 'unhealthy';

    if (healthyCount === totalCount) {
      status = 'healthy';
    } else if (healthyCount > 0) {
      status = 'degraded';
    } else {
      status = 'unhealthy';
    }

    return {
      status,
      services,
      timestamp: new Date(),
    };
  }

  /**
   * Remove a service from the registry
   */
  public unregisterService(name: string): boolean {
    const deleted = this.services.delete(name);
    if (deleted) {
      this.healthCache.delete(name);
      logger.info(`Service unregistered: ${name}`);
    }
    return deleted;
  }

  /**
   * Clear all services
   */
  public clear(): void {
    this.services.clear();
    this.healthCache.clear();
    logger.info('Service registry cleared');
  }
}

// Export singleton instance
export const serviceRegistry = new ServiceRegistry();
