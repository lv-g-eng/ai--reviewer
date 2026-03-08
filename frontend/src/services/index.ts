/**
 * Service layer exports
 * Centralized API service modules
 */

// Export specific items to avoid conflicts
export { apiClient } from './api';
export * from './CacheService';
export * from './config';
export * from './ErrorMonitor';

// Re-export with alias to avoid conflict
export { ApiClient, apiClient as optimizedApiClient } from './ApiClient';
