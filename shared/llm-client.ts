/**
 * LLM Service Client
 * Communicates with the local LLM service for code analysis
 */
import axios, { AxiosInstance } from 'axios';
// Import consolidated enums from common library
import { ModelType } from '../common/shared/enums';

export interface CodeAnalysisRequest {
  code: string;
  language: string;
  analysis_type?: 'review' | 'security' | 'performance';
}

export interface CodeAnalysisResponse {
  success: boolean;
  analysis: {
    analysis: string;
    issues: string[];
    suggestions: string[];
    severity: 'low' | 'medium' | 'high';
  };
}

export interface GenerateRequest {
  prompt: string;
  model_type?: ModelType;
  temperature?: number;
  max_tokens?: number;
  stop?: string[];
}

export interface GenerateResponse {
  success: boolean;
  response: string;
  model: string;
}

export interface ModelInfo {
  type: string;
  path: string;
  loaded: boolean;
  exists: boolean;
  config: {
    n_ctx: number;
    n_threads: number;
    n_gpu_layers: number;
  };
}

export class LLMClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || process.env.LLM_SERVICE_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 300000, // 5 minutes for LLM inference
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Analyze code using LLM
   */
  async analyzeCode(request: CodeAnalysisRequest): Promise<CodeAnalysisResponse> {
    try {
      const response = await this.client.post<CodeAnalysisResponse>(
        '/analyze/code',
        request
      );
      return response.data;
    } catch (error) {
      console.error('LLM code analysis failed:', error);
      throw new Error(`LLM analysis failed: ${error}`);
    }
  }

  /**
   * Generate text using LLM
   */
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      const response = await this.client.post<GenerateResponse>(
        '/generate',
        request
      );
      return response.data;
    } catch (error) {
      console.error('LLM generation failed:', error);
      throw new Error(`LLM generation failed: ${error}`);
    }
  }

  /**
   * Get available models
   */
  async listModels(): Promise<Record<string, ModelInfo>> {
    try {
      const response = await this.client.get('/models');
      return response.data.models;
    } catch (error) {
      console.error('Failed to list models:', error);
      throw new Error(`Failed to list models: ${error}`);
    }
  }

  /**
   * Load a specific model
   */
  async loadModel(modelType: ModelType): Promise<void> {
    try {
      await this.client.post(`/models/${modelType}/load`);
    } catch (error) {
      console.error(`Failed to load model ${modelType}:`, error);
      throw new Error(`Failed to load model: ${error}`);
    }
  }

  /**
   * Unload a model
   */
  async unloadModel(modelType: ModelType): Promise<void> {
    try {
      await this.client.post(`/models/${modelType}/unload`);
    } catch (error) {
      console.error(`Failed to unload model ${modelType}:`, error);
      throw new Error(`Failed to unload model: ${error}`);
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('LLM service health check failed:', error);
      return { status: 'unhealthy', error: String(error) };
    }
  }

  /**
   * Check if LLM service is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const health = await this.healthCheck();
      return health.status === 'healthy' || health.status === 'initializing';
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const llmClient = new LLMClient();
