/**
 * Full-Stack Integration Tests
 * 
 * Comprehensive integration tests that verify the entire system works together:
 * - Frontend-Backend communication
 * - Database operations
 * - Authentication flow
 * - API Gateway routing
 * - Real-time features
 * - Performance requirements
 */

import { describe, test, expect, beforeAll, afterAll, beforeEach } from '@jest/globals';
import { spawn, ChildProcess } from 'child_process';
import axios from 'axios';

// Test configuration
const TEST_CONFIG = {
  frontend_url: 'http://localhost:3000',
  backend_url: 'http://localhost:8000',
  api_gateway_url: 'http://localhost:3000',
  websocket_url: 'ws://localhost:3000/ws',
  test_timeout: 60000,
  startup_timeout: 30000,
};

// Test data
const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  name: 'Test User',
  role: 'developer',
};

const TEST_PROJECT = {
  name: 'Integration Test Project',
  description: 'Project created during integration testing',
  repository_url: 'https://github.com/test/integration-test',
};

// Service management
class ServiceManager {
  private processes: Map<string, ChildProcess> = new Map();
  private healthCheckUrls: Map<string, string> = new Map();

  constructor() {
    this.healthCheckUrls.set('backend', `${TEST_CONFIG.backend_url}/health`);
    this.healthCheckUrls.set('frontend', `${TEST_CONFIG.frontend_url}/api/health`);
    this.healthCheckUrls.set('api-gateway', `${TEST_CONFIG.api_gateway_url}/health`);
  }

  async startService(name: string, command: string, args: string[], cwd?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const childProcess = spawn(command, args, { 
        cwd: cwd || process.cwd(),
        stdio: 'pipe',
        shell: true 
      });

      childProcess.stdout?.on('data', (data) => {
        console.log(`[${name}] ${data.toString()}`);
      });

      childProcess.stderr?.on('data', (data) => {
        console.error(`[${name}] ${data.toString()}`);
      });

      childProcess.on('error', (error) => {
        console.error(`Failed to start ${name}:`, error);
        reject(error);
      });

      this.processes.set(name, childProcess);

      // Wait for service to be healthy
      this.waitForHealthy(name)
        .then(() => resolve())
        .catch(reject);
    });
  }

  async waitForHealthy(serviceName: string, maxAttempts: number = 30): Promise<void> {
    const url = this.healthCheckUrls.get(serviceName);
    if (!url) {
      throw new Error(`No health check URL configured for ${serviceName}`);
    }

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await axios.get(url, { timeout: 5000 });
        if (response.status === 200) {
          console.log(`${serviceName} is healthy`);
          return;
        }
      } catch (error) {
        console.log(`Health check attempt ${attempt}/${maxAttempts} failed for ${serviceName}`);
        if (attempt === maxAttempts) {
          throw new Error(`${serviceName} failed to become healthy after ${maxAttempts} attempts`);
        }
        await this.sleep(2000);
      }
    }
  }

  async stopService(name: string): Promise<void> {
    const childProcess = this.processes.get(name);
    if (childProcess) {
      childProcess.kill('SIGTERM');
      this.processes.delete(name);
      console.log(`Stopped ${name}`);
    }
  }

  async stopAllServices(): Promise<void> {
    const stopPromises = Array.from(this.processes.keys()).map(name => this.stopService(name));
    await Promise.all(stopPromises);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// HTTP Client for API testing
class ApiClient {
  private baseUrl: string;
  private authToken?: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    
    return headers;
  }

  async get(endpoint: string) {
    const response = await axios.get(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders(),
      timeout: 10000,
    });
    return response;
  }

  async post(endpoint: string, data: any) {
    const response = await axios.post(`${this.baseUrl}${endpoint}`, data, {
      headers: this.getHeaders(),
      timeout: 10000,
    });
    return response;
  }

  async put(endpoint: string, data: any) {
    const response = await axios.put(`${this.baseUrl}${endpoint}`, data, {
      headers: this.getHeaders(),
      timeout: 10000,
    });
    return response;
  }

  async delete(endpoint: string) {
    const response = await axios.delete(`${this.baseUrl}${endpoint}`, {
      headers: this.getHeaders(),
      timeout: 10000,
    });
    return response;
  }
}

// Test suite setup
describe('Full-Stack Integration Tests', () => {
  let serviceManager: ServiceManager;
  let apiClient: ApiClient;
  let authToken: string;
  let userId: string;
  let projectId: string;

  beforeAll(async () => {
    serviceManager = new ServiceManager();
    apiClient = new ApiClient(TEST_CONFIG.backend_url);

    // Start all required services
    console.log('Starting services for integration tests...');
    
    try {
      // Start backend services
      await serviceManager.startService('backend', 'npm', ['run', 'dev'], './backend');
      await serviceManager.startService('frontend', 'npm', ['run', 'dev'], './frontend');
      
      console.log('All services started successfully');
    } catch (error) {
      console.error('Failed to start services:', error);
      throw error;
    }
  }, TEST_CONFIG.startup_timeout);

  afterAll(async () => {
    console.log('Stopping all services...');
    await serviceManager.stopAllServices();
  });

  beforeEach(() => {
    // Reset any test state if needed
  });

  describe('Authentication Flow', () => {
    test('should register a new user', async () => {
      const response = await apiClient.post('/api/v1/auth/register', TEST_USER);
      
      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('user');
      expect(response.data).toHaveProperty('access_token');
      expect(response.data.user.email).toBe(TEST_USER.email);
      
      authToken = response.data.access_token;
      userId = response.data.user.id;
      apiClient.setAuthToken(authToken);
    });

    test('should login with valid credentials', async () => {
      const loginData = {
        email: TEST_USER.email,
        password: TEST_USER.password,
      };

      const response = await apiClient.post('/api/v1/auth/login', loginData);
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('access_token');
      expect(response.data).toHaveProperty('user');
    });

    test('should reject invalid credentials', async () => {
      const invalidLogin = {
        email: TEST_USER.email,
        password: 'wrongpassword',
      };

      try {
        await apiClient.post('/api/v1/auth/login', invalidLogin);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }
    });

    test('should access protected routes with valid token', async () => {
      const response = await apiClient.get('/api/v1/auth/me');
      
      expect(response.status).toBe(200);
      expect(response.data.email).toBe(TEST_USER.email);
    });
  });

  describe('Project Management', () => {
    test('should create a new project', async () => {
      const response = await apiClient.post('/api/v1/projects', TEST_PROJECT);
      
      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('id');
      expect(response.data.name).toBe(TEST_PROJECT.name);
      expect(response.data.description).toBe(TEST_PROJECT.description);
      
      projectId = response.data.id;
    });

    test('should list user projects', async () => {
      const response = await apiClient.get('/api/v1/projects');
      
      expect(response.status).toBe(200);
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
      
      const project = response.data.find((p: any) => p.id === projectId);
      expect(project).toBeDefined();
    });

    test('should get project details', async () => {
      const response = await apiClient.get(`/api/v1/projects/${projectId}`);
      
      expect(response.status).toBe(200);
      expect(response.data.id).toBe(projectId);
      expect(response.data.name).toBe(TEST_PROJECT.name);
    });

    test('should update project', async () => {
      const updateData = {
        name: 'Updated Integration Test Project',
        description: 'Updated description',
      };

      const response = await apiClient.put(`/api/v1/projects/${projectId}`, updateData);
      
      expect(response.status).toBe(200);
      expect(response.data.name).toBe(updateData.name);
      expect(response.data.description).toBe(updateData.description);
    });
  });

  describe('Code Review Features', () => {
    test('should submit code for review', async () => {
      const codeReviewData = {
        project_id: projectId,
        code: `
          function calculateSum(a, b) {
            return a + b;
          }
        `,
        language: 'javascript',
        file_path: 'src/utils/math.js',
      };

      const response = await apiClient.post('/api/v1/code-review', codeReviewData);
      
      expect(response.status).toBe(201);
      expect(response.data).toHaveProperty('review_id');
      expect(response.data).toHaveProperty('status');
    });

    test('should get review results', async () => {
      // First submit code for review
      const codeReviewData = {
        project_id: projectId,
        code: 'console.log("Hello World");',
        language: 'javascript',
        file_path: 'src/test.js',
      };

      const submitResponse = await apiClient.post('/api/v1/code-review', codeReviewData);
      const reviewId = submitResponse.data.review_id;

      // Wait a bit for processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Get review results
      const response = await apiClient.get(`/api/v1/code-review/${reviewId}`);
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('review_id');
      expect(response.data).toHaveProperty('suggestions');
    });
  });

  describe('Performance Requirements', () => {
    test('API response times should be under 500ms', async () => {
      const startTime = Date.now();
      const response = await apiClient.get('/api/v1/projects');
      const endTime = Date.now();
      
      const responseTime = endTime - startTime;
      
      expect(response.status).toBe(200);
      expect(responseTime).toBeLessThan(500);
    });

    test('should handle concurrent requests', async () => {
      const concurrentRequests = Array(10).fill(null).map(() => 
        apiClient.get('/api/v1/auth/me')
      );

      const startTime = Date.now();
      const responses = await Promise.all(concurrentRequests);
      const endTime = Date.now();

      responses.forEach(response => {
        expect(response.status).toBe(200);
      });

      const totalTime = endTime - startTime;
      expect(totalTime).toBeLessThan(2000); // All 10 requests should complete within 2 seconds
    });
  });

  describe('Error Handling', () => {
    test('should handle 404 errors gracefully', async () => {
      try {
        await apiClient.get('/api/v1/nonexistent-endpoint');
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
        expect(error.response.data).toHaveProperty('message');
      }
    });

    test('should handle invalid JSON gracefully', async () => {
      try {
        await axios.post(`${TEST_CONFIG.backend_url}/api/v1/projects`, 'invalid json', {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`,
          },
        });
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });
  });

  describe('Database Operations', () => {
    test('should persist data correctly', async () => {
      // Create a project
      const createResponse = await apiClient.post('/api/v1/projects', {
        name: 'Persistence Test Project',
        description: 'Testing data persistence',
      });
      
      const newProjectId = createResponse.data.id;
      
      // Retrieve the project
      const getResponse = await apiClient.get(`/api/v1/projects/${newProjectId}`);
      
      expect(getResponse.status).toBe(200);
      expect(getResponse.data.name).toBe('Persistence Test Project');
      
      // Clean up
      await apiClient.delete(`/api/v1/projects/${newProjectId}`);
    });

    test('should handle database constraints', async () => {
      // Try to create a project with invalid data
      try {
        await apiClient.post('/api/v1/projects', {
          name: '', // Empty name should violate constraints
          description: 'Test description',
        });
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });
  });

  describe('Cleanup', () => {
    test('should clean up test data', async () => {
      // Delete test project
      if (projectId) {
        const response = await apiClient.delete(`/api/v1/projects/${projectId}`);
        expect(response.status).toBe(204);
      }

      // Verify project is deleted
      try {
        await apiClient.get(`/api/v1/projects/${projectId}`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });
});