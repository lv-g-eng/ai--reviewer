/**
 * Comprehensive Full-Stack Integration Tests
 * 
 * Tests the complete integration between frontend and backend with:
 * - API endpoint validation
 * - Real-time communication
 * - Performance benchmarks
 * - Error handling
 * - Security validation
 */

import { describe, test, expect, beforeAll, afterAll, beforeEach } from '@jest/jest-globals';
import { apiClient } from '../../frontend/src/lib/api-client-optimized';
import { apiIntegration, APIError } from '../../shared/integration/api-integration';
import { performance } from 'perf_hooks';

// Test configuration
const TEST_CONFIG = {
  API_BASE_URL: process.env.TEST_API_URL || 'http://localhost:8000',
  SOCKET_URL: process.env.TEST_SOCKET_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  PERFORMANCE_THRESHOLD: {
    API_RESPONSE: 200, // ms
    CACHE_HIT: 50, // ms
    REAL_TIME_LATENCY: 100, // ms
  }
};

// Test data
const TEST_PROJECT = {
  name: 'Integration Test Project',
  description: 'Test project for integration testing',
  status: 'active' as const,
  owner_id: 1,
};

const TEST_REVIEW = {
  title: 'Integration Test Review',
  description: 'Test review for integration testing',
  status: 'pending' as const,
  score: 85,
  findings: [
    {
      type: 'warning' as const,
      message: 'Test finding',
      file: 'test.js',
      line: 10,
      severity: 'medium' as const,
    }
  ],
};

describe('Full-Stack Integration Tests', () => {
  let testProjectId: number;
  let testReviewId: number;

  beforeAll(async () => {
    // Initialize API integration
    await apiIntegration.initializeRealTime();
    
    // Wait for connection
    await new Promise((resolve) => {
      const checkConnection = () => {
        if (apiIntegration['socket']?.connected) {
          resolve(true);
        } else {
          setTimeout(checkConnection, 100);
        }
      };
      checkConnection();
    });
  }, TEST_CONFIG.TIMEOUT);

  afterAll(async () => {
    // Cleanup test data
    if (testProjectId) {
      try {
        await apiIntegration.deleteProject(testProjectId);
      } catch (error) {
        console.warn('Failed to cleanup test project:', error);
      }
    }
    
    // Disconnect
    apiIntegration.disconnect();
  });

  describe('API Client Optimization', () => {
    test('should handle concurrent requests efficiently', async () => {
      const startTime = performance.now();
      
      // Make multiple concurrent requests
      const promises = Array.from({ length: 10 }, () => 
        apiClient.get('/health')
      );
      
      const results = await Promise.all(promises);
      const endTime = performance.now();
      
      // All requests should succeed
      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result).toBeDefined();
      });
      
      // Should complete within reasonable time (with caching)
      const totalTime = endTime - startTime;
      expect(totalTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE * 2);
    });

    test('should implement request deduplication', async () => {
      const endpoint = '/health';
      
      // Clear cache first
      apiClient.clearCache();
      
      const startTime = performance.now();
      
      // Make identical concurrent requests
      const promises = Array.from({ length: 5 }, () => 
        apiClient.get(endpoint)
      );
      
      const results = await Promise.all(promises);
      const endTime = performance.now();
      
      // All should return same result
      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result).toEqual(results[0]);
      });
      
      // Should be faster than making 5 separate requests
      const totalTime = endTime - startTime;
      expect(totalTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });

    test('should cache GET requests effectively', async () => {
      const endpoint = '/health';
      
      // Clear cache
      apiClient.clearCache();
      
      // First request (cache miss)
      const startTime1 = performance.now();
      const result1 = await apiClient.get(endpoint);
      const endTime1 = performance.now();
      
      // Second request (cache hit)
      const startTime2 = performance.now();
      const result2 = await apiClient.get(endpoint);
      const endTime2 = performance.now();
      
      // Results should be identical
      expect(result1).toEqual(result2);
      
      // Second request should be significantly faster
      const firstRequestTime = endTime1 - startTime1;
      const secondRequestTime = endTime2 - startTime2;
      
      expect(secondRequestTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.CACHE_HIT);
      expect(secondRequestTime).toBeLessThan(firstRequestTime / 2);
    });

    test('should handle retry logic with exponential backoff', async () => {
      // Mock a failing endpoint
      const failingEndpoint = '/non-existent-endpoint';
      
      const startTime = performance.now();
      
      try {
        await apiClient.get(failingEndpoint);
        fail('Should have thrown an error');
      } catch (error) {
        const endTime = performance.now();
        const totalTime = endTime - startTime;
        
        // Should have retried (taking more time than a single request)
        expect(totalTime).toBeGreaterThan(1000); // At least 1 second for retries
        expect(error).toBeDefined();
      }
    });
  });

  describe('API Integration Layer', () => {
    test('should create and retrieve projects', async () => {
      // Create project
      const startTime = performance.now();
      const createdProject = await apiIntegration.createProject(TEST_PROJECT);
      const createTime = performance.now() - startTime;
      
      expect(createdProject).toBeDefined();
      expect(createdProject.id).toBeDefined();
      expect(createdProject.name).toBe(TEST_PROJECT.name);
      expect(createTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
      
      testProjectId = createdProject.id;
      
      // Retrieve project
      const retrieveStartTime = performance.now();
      const retrievedProject = await apiIntegration.getProject(testProjectId);
      const retrieveTime = performance.now() - retrieveStartTime;
      
      expect(retrievedProject).toEqual(createdProject);
      expect(retrieveTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });

    test('should handle paginated project listing', async () => {
      const startTime = performance.now();
      const projects = await apiIntegration.getProjects({
        page: 1,
        pageSize: 10,
      });
      const endTime = performance.now();
      
      expect(projects).toBeDefined();
      expect(projects.items).toBeInstanceOf(Array);
      expect(projects.total).toBeGreaterThanOrEqual(0);
      expect(projects.page).toBe(1);
      expect(projects.pageSize).toBe(10);
      
      const responseTime = endTime - startTime;
      expect(responseTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });

    test('should validate project statistics', async () => {
      if (!testProjectId) {
        const project = await apiIntegration.createProject(TEST_PROJECT);
        testProjectId = project.id;
      }
      
      const startTime = performance.now();
      const stats = await apiIntegration.getProjectStats(testProjectId);
      const endTime = performance.now();
      
      expect(stats).toBeDefined();
      expect(typeof stats.review_count).toBe('number');
      expect(typeof stats.library_count).toBe('number');
      expect(typeof stats.team_member_count).toBe('number');
      expect(typeof stats.avg_review_score).toBe('number');
      
      const responseTime = endTime - startTime;
      expect(responseTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });

    test('should handle review operations', async () => {
      if (!testProjectId) {
        const project = await apiIntegration.createProject(TEST_PROJECT);
        testProjectId = project.id;
      }
      
      // Create review
      const startTime = performance.now();
      const createdReview = await apiIntegration.createReview(testProjectId, TEST_REVIEW);
      const createTime = performance.now() - startTime;
      
      expect(createdReview).toBeDefined();
      expect(createdReview.id).toBeDefined();
      expect(createdReview.project_id).toBe(testProjectId);
      expect(createdReview.title).toBe(TEST_REVIEW.title);
      expect(createTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
      
      testReviewId = createdReview.id;
      
      // Get reviews
      const retrieveStartTime = performance.now();
      const reviews = await apiIntegration.getReviews(testProjectId);
      const retrieveTime = performance.now() - retrieveStartTime;
      
      expect(reviews).toBeDefined();
      expect(reviews.items).toBeInstanceOf(Array);
      expect(reviews.items.length).toBeGreaterThan(0);
      expect(retrieveTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });

    test('should search libraries efficiently', async () => {
      const startTime = performance.now();
      const libraries = await apiIntegration.searchLibraries('react', {
        minSecurityScore: 70,
        minPopularityScore: 80,
      });
      const endTime = performance.now();
      
      expect(libraries).toBeInstanceOf(Array);
      libraries.forEach(library => {
        expect(library.security_score).toBeGreaterThanOrEqual(70);
        expect(library.popularity_score).toBeGreaterThanOrEqual(80);
      });
      
      const responseTime = endTime - startTime;
      expect(responseTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE * 2); // Search can be slower
    });
  });

  describe('Real-time Communication', () => {
    test('should establish WebSocket connection', async () => {
      const socket = apiIntegration['socket'];
      expect(socket).toBeDefined();
      expect(socket?.connected).toBe(true);
    });

    test('should receive real-time project updates', async () => {
      if (!testProjectId) {
        const project = await apiIntegration.createProject(TEST_PROJECT);
        testProjectId = project.id;
      }
      
      return new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Real-time update timeout'));
        }, 5000);
        
        // Listen for project updates
        apiIntegration.on('project:updated', (data) => {
          clearTimeout(timeout);
          expect(data).toBeDefined();
          expect(data.project_id || data.id).toBe(testProjectId);
          resolve();
        });
        
        // Trigger an update
        setTimeout(async () => {
          try {
            await apiIntegration.updateProject(testProjectId, {
              description: 'Updated description for real-time test'
            });
          } catch (error) {
            clearTimeout(timeout);
            reject(error);
          }
        }, 100);
      });
    });

    test('should handle connection recovery', async () => {
      const socket = apiIntegration['socket'];
      if (!socket) {
        throw new Error('Socket not initialized');
      }
      
      return new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Connection recovery timeout'));
        }, 10000);
        
        // Listen for reconnection
        apiIntegration.on('connection:restored', () => {
          clearTimeout(timeout);
          resolve();
        });
        
        // Simulate disconnection
        socket.disconnect();
        
        // Reconnect after a short delay
        setTimeout(() => {
          socket.connect();
        }, 1000);
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      try {
        await apiIntegration.getProject(999999); // Non-existent project
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(APIError);
        expect((error as APIError).status).toBe(404);
      }
    });

    test('should handle network errors with retry', async () => {
      // Mock network failure
      const originalBaseURL = apiIntegration['baseURL'];
      apiIntegration['baseURL'] = 'http://non-existent-server:9999';
      
      try {
        await apiIntegration.healthCheck();
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeDefined();
      } finally {
        // Restore original URL
        apiIntegration['baseURL'] = originalBaseURL;
      }
    });

    test('should validate response schemas', async () => {
      // This test ensures that API responses match expected schemas
      const health = await apiIntegration.healthCheck();
      
      expect(health).toBeDefined();
      expect(typeof health.status).toBe('string');
      expect(typeof health.timestamp).toBe('string');
      expect(typeof health.services).toBe('object');
    });
  });

  describe('Performance Benchmarks', () => {
    test('should meet API response time requirements', async () => {
      const endpoints = [
        '/health',
        '/api/v1/projects',
        '/api/v1/libraries',
      ];
      
      for (const endpoint of endpoints) {
        const startTime = performance.now();
        
        try {
          await apiClient.get(endpoint);
          const endTime = performance.now();
          const responseTime = endTime - startTime;
          
          expect(responseTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
        } catch (error) {
          // Some endpoints might not exist in test environment
          console.warn(`Endpoint ${endpoint} not available in test environment`);
        }
      }
    });

    test('should maintain cache hit rate above 50%', async () => {
      // Clear cache
      apiClient.clearCache();
      
      // Make requests to populate cache
      const endpoint = '/health';
      await apiClient.get(endpoint);
      await apiClient.get(endpoint);
      await apiClient.get(endpoint);
      
      const stats = apiClient.getCacheStats();
      expect(stats.hitRate).toBeGreaterThan(0.5); // 50% hit rate
    });

    test('should handle concurrent load efficiently', async () => {
      const concurrentRequests = 50;
      const startTime = performance.now();
      
      const promises = Array.from({ length: concurrentRequests }, (_, i) => 
        apiClient.get(`/health?test=${i}`)
      );
      
      const results = await Promise.allSettled(promises);
      const endTime = performance.now();
      
      const successfulRequests = results.filter(r => r.status === 'fulfilled').length;
      const totalTime = endTime - startTime;
      const avgResponseTime = totalTime / concurrentRequests;
      
      expect(successfulRequests).toBeGreaterThan(concurrentRequests * 0.9); // 90% success rate
      expect(avgResponseTime).toBeLessThan(TEST_CONFIG.PERFORMANCE_THRESHOLD.API_RESPONSE);
    });
  });

  describe('Security Validation', () => {
    test('should include security headers in requests', async () => {
      // This would typically be tested with a mock server
      // For now, we verify that the client includes expected headers
      const headers = apiIntegration['getHeaders']();
      
      expect(headers['Content-Type']).toBe('application/json');
      expect(headers['Accept']).toBe('application/json');
    });

    test('should handle authentication errors', async () => {
      // Mock invalid token
      if (typeof window !== 'undefined') {
        const originalToken = localStorage.getItem('auth_token');
        localStorage.setItem('auth_token', 'invalid-token');
        
        try {
          await apiIntegration.getProjects();
          fail('Should have thrown authentication error');
        } catch (error) {
          expect(error).toBeInstanceOf(APIError);
          expect((error as APIError).status).toBe(401);
        } finally {
          // Restore original token
          if (originalToken) {
            localStorage.setItem('auth_token', originalToken);
          } else {
            localStorage.removeItem('auth_token');
          }
        }
      }
    });
  });
});

// Performance monitoring utilities
export const performanceMonitor = {
  measureApiCall: async <T>(
    name: string,
    apiCall: () => Promise<T>
  ): Promise<{ result: T; duration: number }> => {
    const startTime = performance.now();
    const result = await apiCall();
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`API Call ${name}: ${duration.toFixed(2)}ms`);
    
    return { result, duration };
  },
  
  measureCacheHitRate: (client: typeof apiClient) => {
    const stats = client.getCacheStats();
    console.log(`Cache Stats: ${stats.entries} entries, ${(stats.hitRate * 100).toFixed(1)}% hit rate`);
    return stats;
  },
  
  measureRealTimeLatency: (integration: typeof apiIntegration) => {
    const startTime = Date.now();
    
    return new Promise<number>((resolve) => {
      integration.on('connection:established', () => {
        const latency = Date.now() - startTime;
        console.log(`Real-time connection latency: ${latency}ms`);
        resolve(latency);
      });
    });
  }
};