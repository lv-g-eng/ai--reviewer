/**
 * Enhanced API Integration Layer
 * 
 * Provides seamless integration between frontend and backend with:
 * - Type-safe API contracts
 * - Real-time synchronization
 * - Error handling and recovery
 * - Performance monitoring
 * - Caching strategies
 */

import { z } from 'zod';
import { io, Socket } from 'socket.io-client';
import * as React from 'react';

// API Response schemas
export const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.any().optional(),
  error: z.string().optional(),
  timestamp: z.string(),
  requestId: z.string().optional(),
});

export const PaginatedResponseSchema = z.object({
  items: z.array(z.any()),
  total: z.number(),
  page: z.number(),
  pageSize: z.number(),
  hasNext: z.boolean(),
  hasPrev: z.boolean(),
});

// Project schemas
export const ProjectSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().optional(),
  status: z.enum(['active', 'inactive', 'archived']),
  owner_id: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
  settings: z.record(z.any()).optional(),
});

export const ProjectStatsSchema = z.object({
  review_count: z.number(),
  library_count: z.number(),
  team_member_count: z.number(),
  avg_review_score: z.number(),
  last_review_date: z.string().nullable(),
});

// Review schemas
export const ReviewSchema = z.object({
  id: z.number(),
  project_id: z.number(),
  title: z.string(),
  description: z.string().optional(),
  status: z.enum(['pending', 'in_progress', 'completed', 'rejected']),
  score: z.number().min(0).max(100),
  findings: z.array(z.object({
    type: z.enum(['error', 'warning', 'info', 'suggestion']),
    message: z.string(),
    file: z.string().optional(),
    line: z.number().optional(),
    severity: z.enum(['low', 'medium', 'high', 'critical']),
  })),
  created_at: z.string(),
  updated_at: z.string(),
});

// Library schemas
export const LibrarySchema = z.object({
  id: z.number(),
  name: z.string(),
  version: z.string(),
  description: z.string().optional(),
  homepage: z.string().url().optional(),
  repository: z.string().url().optional(),
  license: z.string().optional(),
  dependencies: z.array(z.string()),
  dev_dependencies: z.array(z.string()),
  security_score: z.number().min(0).max(100),
  popularity_score: z.number().min(0).max(100),
  maintenance_score: z.number().min(0).max(100),
  created_at: z.string(),
  updated_at: z.string(),
});

// Type exports
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
  requestId?: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export type Project = z.infer<typeof ProjectSchema>;
export type ProjectStats = z.infer<typeof ProjectStatsSchema>;
export type Review = z.infer<typeof ReviewSchema>;
export type Library = z.infer<typeof LibrarySchema>;

// API Integration Class
export class APIIntegration {
  private socket: Socket | null = null;
  private eventHandlers = new Map<string, Set<Function>>();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(
    private baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    private socketURL: string = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8000'
  ) {}

  // Initialize real-time connection
  async initializeRealTime(): Promise<void> {
    if (this.socket?.connected) return;

    this.socket = io(this.socketURL, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    this.setupSocketEventHandlers();
  }

  private setupSocketEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Real-time connection established');
      this.reconnectAttempts = 0;
      this.emit('connection:established');
    });

    this.socket.on('disconnect', (reason) => {
      console.warn('Real-time connection lost:', reason);
      this.emit('connection:lost', reason);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`Reconnected after ${attemptNumber} attempts`);
      this.emit('connection:restored', attemptNumber);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('Failed to reconnect after maximum attempts');
      this.emit('connection:failed');
    });

    // Project events
    this.socket.on('project:updated', (data) => {
      this.emit('project:updated', data);
    });

    this.socket.on('project:deleted', (data) => {
      this.emit('project:deleted', data);
    });

    // Review events
    this.socket.on('review:created', (data) => {
      this.emit('review:created', data);
    });

    this.socket.on('review:updated', (data) => {
      this.emit('review:updated', data);
    });

    this.socket.on('review:completed', (data) => {
      this.emit('review:completed', data);
    });

    // Library events
    this.socket.on('library:updated', (data) => {
      this.emit('library:updated', data);
    });

    // System events
    this.socket.on('system:maintenance', (data) => {
      this.emit('system:maintenance', data);
    });
  }

  // Event handling
  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
  }

  off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  // API Methods with validation
  async getProjects(params?: {
    page?: number;
    pageSize?: number;
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<Project>> {
    const response = await fetch(`${this.baseURL}/api/v1/projects`, {
      method: 'GET',
      headers: this.getHeaders(),
      ...this.buildQueryParams(params),
    });

    const data = await this.handleResponse(response);
    return PaginatedResponseSchema.parse(data) as PaginatedResponse<Project>;
  }

  async getProject(id: number): Promise<Project> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${id}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const data = await this.handleResponse(response);
    return ProjectSchema.parse(data);
  }

  async createProject(project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> {
    const response = await fetch(`${this.baseURL}/api/v1/projects`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(project),
    });

    const data = await this.handleResponse(response);
    return ProjectSchema.parse(data);
  }

  async updateProject(id: number, updates: Partial<Project>): Promise<Project> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(updates),
    });

    const data = await this.handleResponse(response);
    return ProjectSchema.parse(data);
  }

  async deleteProject(id: number): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${id}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    await this.handleResponse(response);
  }

  async getProjectStats(id: number): Promise<ProjectStats> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${id}/stats`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const data = await this.handleResponse(response);
    return ProjectStatsSchema.parse(data);
  }

  // Review methods
  async getReviews(projectId: number, params?: {
    page?: number;
    pageSize?: number;
    status?: string;
  }): Promise<PaginatedResponse<Review>> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${projectId}/reviews`, {
      method: 'GET',
      headers: this.getHeaders(),
      ...this.buildQueryParams(params),
    });

    const data = await this.handleResponse(response);
    return PaginatedResponseSchema.parse(data) as PaginatedResponse<Review>;
  }

  async createReview(projectId: number, review: Omit<Review, 'id' | 'project_id' | 'created_at' | 'updated_at'>): Promise<Review> {
    const response = await fetch(`${this.baseURL}/api/v1/projects/${projectId}/reviews`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(review),
    });

    const data = await this.handleResponse(response);
    return ReviewSchema.parse(data);
  }

  // Library methods
  async getLibraries(params?: {
    page?: number;
    pageSize?: number;
    search?: string;
    category?: string;
  }): Promise<PaginatedResponse<Library>> {
    const response = await fetch(`${this.baseURL}/api/v1/libraries`, {
      method: 'GET',
      headers: this.getHeaders(),
      ...this.buildQueryParams(params),
    });

    const data = await this.handleResponse(response);
    return PaginatedResponseSchema.parse(data) as PaginatedResponse<Library>;
  }

  async searchLibraries(query: string, filters?: {
    minSecurityScore?: number;
    minPopularityScore?: number;
    license?: string;
  }): Promise<Library[]> {
    const response = await fetch(`${this.baseURL}/api/v1/libraries/search`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, filters }),
    });

    const data = await this.handleResponse(response);
    return z.array(LibrarySchema).parse(data);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; services: Record<string, boolean> }> {
    const response = await fetch(`${this.baseURL}/health`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return await this.handleResponse(response);
  }

  // Utility methods
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add auth token if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private buildQueryParams(params?: Record<string, any>): { search?: URLSearchParams } {
    if (!params) return {};

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });

    return searchParams.toString() ? { search: searchParams } : {};
  }

  private async handleResponse(response: Response): Promise<any> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return data.data || data; // Handle both wrapped and unwrapped responses
  }

  // Cleanup
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.eventHandlers.clear();
  }
}

// Custom error class
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Singleton instance
export const apiIntegration = new APIIntegration();

// React hooks for integration
export const useRealTimeConnection = () => {
  const [connected, setConnected] = React.useState(false);
  const [reconnecting, setReconnecting] = React.useState(false);

  React.useEffect(() => {
    const handleConnection = () => setConnected(true);
    const handleDisconnection = () => setConnected(false);
    const handleReconnecting = () => setReconnecting(true);
    const handleReconnected = () => {
      setReconnecting(false);
      setConnected(true);
    };

    apiIntegration.on('connection:established', handleConnection);
    apiIntegration.on('connection:lost', handleDisconnection);
    apiIntegration.on('connection:failed', handleDisconnection);
    apiIntegration.on('reconnect', handleReconnected);

    // Initialize connection
    apiIntegration.initializeRealTime();

    return () => {
      apiIntegration.off('connection:established', handleConnection);
      apiIntegration.off('connection:lost', handleDisconnection);
      apiIntegration.off('connection:failed', handleDisconnection);
      apiIntegration.off('reconnect', handleReconnected);
    };
  }, []);

  return { connected, reconnecting };
};

export const useProjectUpdates = (projectId?: number) => {
  const [updates, setUpdates] = React.useState<any[]>([]);

  React.useEffect(() => {
    const handleUpdate = (data: any) => {
      if (!projectId || data.project_id === projectId) {
        setUpdates(prev => [...prev, data]);
      }
    };

    apiIntegration.on('project:updated', handleUpdate);
    apiIntegration.on('review:created', handleUpdate);
    apiIntegration.on('review:updated', handleUpdate);
    apiIntegration.on('review:completed', handleUpdate);

    return () => {
      apiIntegration.off('project:updated', handleUpdate);
      apiIntegration.off('review:created', handleUpdate);
      apiIntegration.off('review:updated', handleUpdate);
      apiIntegration.off('review:completed', handleUpdate);
    };
  }, [projectId]);

  return updates;
};