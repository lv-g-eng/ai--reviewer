/**
 * Unified Configuration Management System
 * 
 * Provides centralized configuration management for the entire platform:
 * - Type-safe configuration schema
 * - Environment variable validation
 * - Configuration inheritance and overrides
 * - Runtime configuration updates
 * - Configuration documentation
 */

import { z } from 'zod';

// Base configuration schemas
const DatabaseConfigSchema = z.object({
  postgres: z.object({
    host: z.string().min(1, 'PostgreSQL host is required'),
    port: z.number().int().min(1).max(65535, 'Invalid PostgreSQL port'),
    database: z.string().min(1, 'PostgreSQL database name is required'),
    username: z.string().min(1, 'PostgreSQL username is required'),
    password: z.string().min(8, 'PostgreSQL password must be at least 8 characters'),
    pool_size: z.number().int().min(1).max(100).default(20),
    max_overflow: z.number().int().min(0).max(50).default(10),
    pool_timeout: z.number().int().min(1).max(300).default(30),
    pool_recycle: z.number().int().min(300).max(7200).default(3600),
  }),
  neo4j: z.object({
    uri: z.string().url('Invalid Neo4j URI'),
    username: z.string().min(1, 'Neo4j username is required'),
    password: z.string().min(8, 'Neo4j password must be at least 8 characters'),
    database: z.string().default('neo4j'),
    max_connection_lifetime: z.number().int().min(300).max(7200).default(3600),
    max_connection_pool_size: z.number().int().min(1).max(100).default(50),
    connection_acquisition_timeout: z.number().int().min(1).max(300).default(60),
  }),
  redis: z.object({
    host: z.string().min(1, 'Redis host is required'),
    port: z.number().int().min(1).max(65535, 'Invalid Redis port'),
    password: z.string().optional(),
    database: z.number().int().min(0).max(15).default(0),
    max_connections: z.number().int().min(1).max(1000).default(100),
    retry_on_timeout: z.boolean().default(true),
    socket_timeout: z.number().int().min(1).max(300).default(30),
  }),
});

const SecurityConfigSchema = z.object({
  jwt: z.object({
    secret: z.string().min(32, 'JWT secret must be at least 32 characters'),
    algorithm: z.enum(['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']).default('HS256'),
    access_token_expire_minutes: z.number().int().min(1).max(1440).default(15),
    refresh_token_expire_days: z.number().int().min(1).max(365).default(7),
    issuer: z.string().optional(),
    audience: z.string().optional(),
  }),
  session: z.object({
    secret: z.string().min(32, 'Session secret must be at least 32 characters'),
    cookie_secure: z.boolean().default(true),
    cookie_http_only: z.boolean().default(true),
    cookie_same_site: z.enum(['strict', 'lax', 'none']).default('lax'),
    max_age: z.number().int().min(300).max(86400).default(3600),
  }),
  bcrypt: z.object({
    rounds: z.number().int().min(12).max(16).default(12),
  }),
  cors: z.object({
    allowed_origins: z.array(z.string().url()).min(1, 'At least one CORS origin is required'),
    allowed_methods: z.array(z.string()).default(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']),
    allowed_headers: z.array(z.string()).default(['*']),
    allow_credentials: z.boolean().default(true),
    max_age: z.number().int().min(0).max(86400).default(3600),
  }),
  rate_limiting: z.object({
    enabled: z.boolean().default(true),
    window_ms: z.number().int().min(1000).max(3600000).default(900000), // 15 minutes
    max_requests: z.number().int().min(1).max(10000).default(100),
    skip_successful_requests: z.boolean().default(false),
    skip_failed_requests: z.boolean().default(false),
  }),
});

const ServiceConfigSchema = z.object({
  api_gateway: z.object({
    port: z.number().int().min(1000).max(65535).default(3000),
    host: z.string().default('0.0.0.0'),
    trust_proxy: z.boolean().default(true),
    body_limit: z.string().default('10mb'),
    timeout: z.number().int().min(1000).max(300000).default(30000),
    compression: z.object({
      enabled: z.boolean().default(true),
      threshold: z.number().int().min(0).max(10240).default(1024),
      level: z.number().int().min(1).max(9).default(6),
    }),
    circuit_breaker: z.object({
      enabled: z.boolean().default(true),
      timeout: z.number().int().min(1000).max(60000).default(10000),
      error_threshold_percentage: z.number().int().min(1).max(100).default(50),
      reset_timeout: z.number().int().min(10000).max(300000).default(60000),
      minimum_requests: z.number().int().min(1).max(100).default(10),
    }),
  }),
  backend: z.object({
    port: z.number().int().min(1000).max(65535).default(8000),
    host: z.string().default('0.0.0.0'),
    workers: z.number().int().min(1).max(32).default(1),
    reload: z.boolean().default(false),
    log_level: z.enum(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']).default('INFO'),
    access_log: z.boolean().default(true),
    keepalive_timeout: z.number().int().min(1).max(300).default(5),
    max_request_size: z.number().int().min(1024).max(104857600).default(16777216), // 16MB
  }),
  frontend: z.object({
    port: z.number().int().min(1000).max(65535).default(3000),
    host: z.string().default('0.0.0.0'),
    api_url: z.string().url('Invalid API URL'),
    ws_url: z.string().url('Invalid WebSocket URL').optional(),
    build_optimization: z.object({
      minify: z.boolean().default(true),
      source_maps: z.boolean().default(false),
      bundle_analyzer: z.boolean().default(false),
      tree_shaking: z.boolean().default(true),
    }),
  }),
});

const IntegrationConfigSchema = z.object({
  github: z.object({
    enabled: z.boolean().default(false),
    token: z.string().optional(),
    webhook_secret: z.string().optional(),
    app_id: z.string().optional(),
    private_key: z.string().optional(),
    installation_id: z.string().optional(),
  }),
  openai: z.object({
    enabled: z.boolean().default(false),
    api_key: z.string().optional(),
    model: z.string().default('gpt-4'),
    max_tokens: z.number().int().min(1).max(32000).default(4000),
    temperature: z.number().min(0).max(2).default(0.1),
    timeout: z.number().int().min(1000).max(300000).default(60000),
  }),
  anthropic: z.object({
    enabled: z.boolean().default(false),
    api_key: z.string().optional(),
    model: z.string().default('claude-3-sonnet-20240229'),
    max_tokens: z.number().int().min(1).max(200000).default(4000),
    timeout: z.number().int().min(1000).max(300000).default(60000),
  }),
  local_llm: z.object({
    enabled: z.boolean().default(false),
    model_path: z.string().optional(),
    context_length: z.number().int().min(512).max(32768).default(4096),
    gpu_layers: z.number().int().min(0).max(100).default(0),
    threads: z.number().int().min(1).max(32).default(8),
  }),
});

const MonitoringConfigSchema = z.object({
  logging: z.object({
    level: z.enum(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']).default('INFO'),
    format: z.enum(['text', 'json']).default('json'),
    file_enabled: z.boolean().default(true),
    file_path: z.string().default('logs/app.log'),
    file_max_size: z.number().int().min(1).max(1000).default(100), // MB
    file_backup_count: z.number().int().min(1).max(100).default(5),
    console_enabled: z.boolean().default(true),
  }),
  metrics: z.object({
    enabled: z.boolean().default(true),
    prometheus_enabled: z.boolean().default(false),
    prometheus_port: z.number().int().min(1000).max(65535).default(9090),
    collection_interval: z.number().int().min(1).max(300).default(15), // seconds
  }),
  health_checks: z.object({
    enabled: z.boolean().default(true),
    interval: z.number().int().min(5).max(300).default(30), // seconds
    timeout: z.number().int().min(1).max(60).default(10), // seconds
    failure_threshold: z.number().int().min(1).max(10).default(3),
  }),
  tracing: z.object({
    enabled: z.boolean().default(false),
    jaeger_endpoint: z.string().url().optional(),
    sample_rate: z.number().min(0).max(1).default(0.1),
  }),
});

// Main configuration schema
export const UnifiedConfigSchema = z.object({
  environment: z.enum(['development', 'staging', 'production']).default('development'),
  debug: z.boolean().default(false),
  database: DatabaseConfigSchema,
  security: SecurityConfigSchema,
  services: ServiceConfigSchema,
  integrations: IntegrationConfigSchema,
  monitoring: MonitoringConfigSchema,
});

export type UnifiedConfig = z.infer<typeof UnifiedConfigSchema>;

// Configuration validation and loading
export class ConfigManager {
  private config: UnifiedConfig | null = null;
  private validationErrors: z.ZodError | null = null;

  constructor(private envSource: Record<string, string | undefined> = process.env) {}

  /**
   * Load and validate configuration from environment variables
   */
  load(): { success: boolean; config?: UnifiedConfig; errors?: z.ZodError } {
    try {
      const rawConfig = this.parseEnvironmentVariables();
      const validatedConfig = UnifiedConfigSchema.parse(rawConfig);
      
      this.config = validatedConfig;
      this.validationErrors = null;
      
      return { success: true, config: validatedConfig };
    } catch (error) {
      if (error instanceof z.ZodError) {
        this.validationErrors = error;
        return { success: false, errors: error };
      }
      throw error;
    }
  }

  /**
   * Get the current configuration
   */
  getConfig(): UnifiedConfig {
    if (!this.config) {
      const result = this.load();
      if (!result.success) {
        throw new Error('Configuration validation failed. Call load() first and check for errors.');
      }
    }
    return this.config!;
  }

  /**
   * Get validation errors
   */
  getValidationErrors(): z.ZodError | null {
    return this.validationErrors;
  }

  /**
   * Check if configuration is valid
   */
  isValid(): boolean {
    return this.config !== null && this.validationErrors === null;
  }

  /**
   * Parse environment variables into configuration object
   */
  private parseEnvironmentVariables(): Partial<UnifiedConfig> {
    const env = this.envSource;

    return {
      environment: (env.ENVIRONMENT || env.NODE_ENV) as any,
      debug: env.DEBUG === 'true',
      
      database: {
        postgres: {
          host: env.POSTGRES_HOST || 'localhost',
          port: parseInt(env.POSTGRES_PORT || '5432'),
          database: env.POSTGRES_DB || env.POSTGRES_DATABASE || 'ai_code_review',
          username: env.POSTGRES_USER || env.POSTGRES_USERNAME || 'postgres',
          password: env.POSTGRES_PASSWORD || '',
          pool_size: parseInt(env.DB_POOL_SIZE || '20'),
          max_overflow: parseInt(env.DB_MAX_OVERFLOW || '10'),
          pool_timeout: parseInt(env.DB_POOL_TIMEOUT || '30'),
          pool_recycle: parseInt(env.DB_POOL_RECYCLE || '3600'),
        },
        neo4j: {
          uri: env.NEO4J_URI || 'bolt://localhost:7687',
          username: env.NEO4J_USER || env.NEO4J_USERNAME || 'neo4j',
          password: env.NEO4J_PASSWORD || '',
          database: env.NEO4J_DATABASE || 'neo4j',
          max_connection_lifetime: parseInt(env.NEO4J_MAX_CONNECTION_LIFETIME || '3600'),
          max_connection_pool_size: parseInt(env.NEO4J_MAX_CONNECTION_POOL_SIZE || '50'),
          connection_acquisition_timeout: parseInt(env.NEO4J_CONNECTION_ACQUISITION_TIMEOUT || '60'),
        },
        redis: {
          host: env.REDIS_HOST || 'localhost',
          port: parseInt(env.REDIS_PORT || '6379'),
          password: env.REDIS_PASSWORD,
          database: parseInt(env.REDIS_DB || '0'),
          max_connections: parseInt(env.REDIS_MAX_CONNECTIONS || '100'),
          retry_on_timeout: env.REDIS_RETRY_ON_TIMEOUT !== 'false',
          socket_timeout: parseInt(env.REDIS_SOCKET_TIMEOUT || '30'),
        },
      },

      security: {
        jwt: {
          secret: env.JWT_SECRET || '',
          algorithm: (env.JWT_ALGORITHM as any) || 'HS256',
          access_token_expire_minutes: parseInt(env.ACCESS_TOKEN_EXPIRE_MINUTES || '15'),
          refresh_token_expire_days: parseInt(env.REFRESH_TOKEN_EXPIRE_DAYS || '7'),
          issuer: env.JWT_ISSUER,
          audience: env.JWT_AUDIENCE,
        },
        session: {
          secret: env.SESSION_SECRET || env.SECRET_KEY || '',
          cookie_secure: env.SESSION_COOKIE_SECURE !== 'false',
          cookie_http_only: env.SESSION_COOKIE_HTTP_ONLY !== 'false',
          cookie_same_site: (env.SESSION_COOKIE_SAME_SITE as any) || 'lax',
          max_age: parseInt(env.SESSION_MAX_AGE || '3600'),
        },
        bcrypt: {
          rounds: parseInt(env.BCRYPT_ROUNDS || '12'),
        },
        cors: {
          allowed_origins: (env.CORS_ALLOWED_ORIGINS || env.CORS_ORIGINS || 'http://localhost:3000')
            .split(',')
            .map(origin => origin.trim()),
          allowed_methods: (env.CORS_ALLOWED_METHODS || 'GET,POST,PUT,DELETE,PATCH,OPTIONS')
            .split(',')
            .map(method => method.trim()),
          allowed_headers: (env.CORS_ALLOWED_HEADERS || '*')
            .split(',')
            .map(header => header.trim()),
          allow_credentials: env.CORS_ALLOW_CREDENTIALS !== 'false',
          max_age: parseInt(env.CORS_MAX_AGE || '3600'),
        },
        rate_limiting: {
          enabled: env.RATE_LIMITING_ENABLED !== 'false',
          window_ms: parseInt(env.RATE_LIMIT_WINDOW_MS || '900000'),
          max_requests: parseInt(env.RATE_LIMIT_MAX || env.RATE_LIMIT_MAX_REQUESTS || '100'),
          skip_successful_requests: env.RATE_LIMIT_SKIP_SUCCESSFUL_REQUESTS === 'true',
          skip_failed_requests: env.RATE_LIMIT_SKIP_FAILED_REQUESTS === 'true',
        },
      },

      services: {
        api_gateway: {
          port: parseInt(env.API_GATEWAY_PORT || '3000'),
          host: env.API_GATEWAY_HOST || '0.0.0.0',
          trust_proxy: env.TRUST_PROXY !== 'false',
          body_limit: env.MAX_REQUEST_BODY_SIZE || '10mb',
          timeout: parseInt(env.REQUEST_TIMEOUT || '30000'),
          compression: {
            enabled: env.ENABLE_COMPRESSION !== 'false',
            threshold: parseInt(env.COMPRESSION_THRESHOLD || '1024'),
            level: parseInt(env.COMPRESSION_LEVEL || '6'),
          },
          circuit_breaker: {
            enabled: env.CIRCUIT_BREAKER_ENABLED !== 'false',
            timeout: parseInt(env.CIRCUIT_BREAKER_TIMEOUT || '10000'),
            error_threshold_percentage: parseInt(env.CIRCUIT_BREAKER_ERROR_THRESHOLD || '50'),
            reset_timeout: parseInt(env.CIRCUIT_BREAKER_RESET_TIMEOUT || '60000'),
            minimum_requests: parseInt(env.CIRCUIT_BREAKER_MINIMUM_REQUESTS || '10'),
          },
        },
        backend: {
          port: parseInt(env.BACKEND_PORT || env.PORT || '8000'),
          host: env.BACKEND_HOST || env.HOST || '0.0.0.0',
          workers: parseInt(env.WORKERS || '1'),
          reload: env.RELOAD === 'true',
          log_level: (env.LOG_LEVEL as any) || 'INFO',
          access_log: env.ACCESS_LOG !== 'false',
          keepalive_timeout: parseInt(env.KEEPALIVE_TIMEOUT || '5'),
          max_request_size: parseInt(env.MAX_REQUEST_SIZE || '16777216'),
        },
        frontend: {
          port: parseInt(env.FRONTEND_PORT || '3000'),
          host: env.FRONTEND_HOST || '0.0.0.0',
          api_url: env.NEXT_PUBLIC_API_URL || env.API_URL || 'http://localhost:8000',
          ws_url: env.NEXT_PUBLIC_WS_URL || env.WS_URL,
          build_optimization: {
            minify: env.BUILD_MINIFY !== 'false',
            source_maps: env.BUILD_SOURCE_MAPS === 'true',
            bundle_analyzer: env.BUILD_BUNDLE_ANALYZER === 'true',
            tree_shaking: env.BUILD_TREE_SHAKING !== 'false',
          },
        },
      },

      integrations: {
        github: {
          enabled: env.GITHUB_ENABLED === 'true' || !!env.GITHUB_TOKEN,
          token: env.GITHUB_TOKEN || env.GITHUB_ACCESS_TOKEN,
          webhook_secret: env.GITHUB_WEBHOOK_SECRET,
          app_id: env.GITHUB_APP_ID,
          private_key: env.GITHUB_PRIVATE_KEY,
          installation_id: env.GITHUB_INSTALLATION_ID,
        },
        openai: {
          enabled: env.OPENAI_ENABLED === 'true' || !!env.OPENAI_API_KEY,
          api_key: env.OPENAI_API_KEY,
          model: env.OPENAI_MODEL || env.DEFAULT_LLM_MODEL || 'gpt-4',
          max_tokens: parseInt(env.OPENAI_MAX_TOKENS || '4000'),
          temperature: parseFloat(env.OPENAI_TEMPERATURE || '0.1'),
          timeout: parseInt(env.OPENAI_TIMEOUT || '60000'),
        },
        anthropic: {
          enabled: env.ANTHROPIC_ENABLED === 'true' || !!env.ANTHROPIC_API_KEY,
          api_key: env.ANTHROPIC_API_KEY,
          model: env.ANTHROPIC_MODEL || 'claude-3-sonnet-20240229',
          max_tokens: parseInt(env.ANTHROPIC_MAX_TOKENS || '4000'),
          timeout: parseInt(env.ANTHROPIC_TIMEOUT || '60000'),
        },
        local_llm: {
          enabled: env.LOCAL_LLM_ENABLED === 'true' || !!env.LLM_MODEL_PATH,
          model_path: env.LLM_MODEL_PATH || env.MODELS_DIR,
          context_length: parseInt(env.LLM_CONTEXT_LENGTH || '4096'),
          gpu_layers: parseInt(env.LLM_GPU_LAYERS || '0'),
          threads: parseInt(env.LLM_THREADS || '8'),
        },
      },

      monitoring: {
        logging: {
          level: (env.LOG_LEVEL as any) || 'INFO',
          format: (env.LOG_FORMAT as any) || (env.JSON_LOGGING === 'true' ? 'json' : 'text'),
          file_enabled: env.LOG_FILE_ENABLED !== 'false',
          file_path: env.LOG_FILE_PATH || 'logs/app.log',
          file_max_size: parseInt(env.LOG_FILE_MAX_SIZE || '100'),
          file_backup_count: parseInt(env.LOG_FILE_BACKUP_COUNT || '5'),
          console_enabled: env.LOG_CONSOLE_ENABLED !== 'false',
        },
        metrics: {
          enabled: env.METRICS_ENABLED !== 'false',
          prometheus_enabled: env.PROMETHEUS_ENABLED === 'true',
          prometheus_port: parseInt(env.PROMETHEUS_PORT || '9090'),
          collection_interval: parseInt(env.METRICS_COLLECTION_INTERVAL || '15'),
        },
        health_checks: {
          enabled: env.HEALTH_CHECKS_ENABLED !== 'false',
          interval: parseInt(env.HEALTH_CHECK_INTERVAL || '30'),
          timeout: parseInt(env.HEALTH_CHECK_TIMEOUT || '10'),
          failure_threshold: parseInt(env.HEALTH_CHECK_FAILURE_THRESHOLD || '3'),
        },
        tracing: {
          enabled: env.TRACING_ENABLED === 'true',
          jaeger_endpoint: env.JAEGER_ENDPOINT,
          sample_rate: parseFloat(env.TRACING_SAMPLE_RATE || '0.1'),
        },
      },
    };
  }

  /**
   * Generate configuration documentation
   */
  generateDocumentation(): string {
    const docs = `
# Configuration Documentation

This document describes all available configuration options for the AI Code Review Platform.

## Environment Variables

### Database Configuration

#### PostgreSQL
- \`POSTGRES_HOST\`: PostgreSQL server hostname (default: localhost)
- \`POSTGRES_PORT\`: PostgreSQL server port (default: 5432)
- \`POSTGRES_DB\`: Database name (default: ai_code_review)
- \`POSTGRES_USER\`: Database username (default: postgres)
- \`POSTGRES_PASSWORD\`: Database password (required, min 8 characters)
- \`DB_POOL_SIZE\`: Connection pool size (default: 20)
- \`DB_MAX_OVERFLOW\`: Maximum overflow connections (default: 10)

#### Neo4j
- \`NEO4J_URI\`: Neo4j connection URI (default: bolt://localhost:7687)
- \`NEO4J_USER\`: Neo4j username (default: neo4j)
- \`NEO4J_PASSWORD\`: Neo4j password (required, min 8 characters)
- \`NEO4J_DATABASE\`: Neo4j database name (default: neo4j)

#### Redis
- \`REDIS_HOST\`: Redis server hostname (default: localhost)
- \`REDIS_PORT\`: Redis server port (default: 6379)
- \`REDIS_PASSWORD\`: Redis password (optional)
- \`REDIS_DB\`: Redis database number (default: 0)

### Security Configuration

#### JWT
- \`JWT_SECRET\`: JWT signing secret (required, min 32 characters)
- \`JWT_ALGORITHM\`: JWT signing algorithm (default: HS256)
- \`ACCESS_TOKEN_EXPIRE_MINUTES\`: Access token expiration (default: 15)
- \`REFRESH_TOKEN_EXPIRE_DAYS\`: Refresh token expiration (default: 7)

#### Session
- \`SESSION_SECRET\`: Session signing secret (required, min 32 characters)
- \`SESSION_COOKIE_SECURE\`: Use secure cookies (default: true)
- \`SESSION_COOKIE_HTTP_ONLY\`: HTTP-only cookies (default: true)

#### CORS
- \`CORS_ALLOWED_ORIGINS\`: Comma-separated list of allowed origins
- \`CORS_ALLOWED_METHODS\`: Comma-separated list of allowed methods
- \`CORS_ALLOW_CREDENTIALS\`: Allow credentials (default: true)

#### Rate Limiting
- \`RATE_LIMITING_ENABLED\`: Enable rate limiting (default: true)
- \`RATE_LIMIT_WINDOW_MS\`: Rate limit window in milliseconds (default: 900000)
- \`RATE_LIMIT_MAX\`: Maximum requests per window (default: 100)

### Service Configuration

#### API Gateway
- \`API_GATEWAY_PORT\`: API Gateway port (default: 3000)
- \`TRUST_PROXY\`: Trust proxy headers (default: true)
- \`REQUEST_TIMEOUT\`: Request timeout in milliseconds (default: 30000)

#### Backend
- \`BACKEND_PORT\`: Backend server port (default: 8000)
- \`WORKERS\`: Number of worker processes (default: 1)
- \`LOG_LEVEL\`: Logging level (default: INFO)

#### Frontend
- \`FRONTEND_PORT\`: Frontend server port (default: 3000)
- \`NEXT_PUBLIC_API_URL\`: Public API URL for frontend
- \`BUILD_MINIFY\`: Minify build output (default: true)

### Integration Configuration

#### GitHub
- \`GITHUB_TOKEN\`: GitHub personal access token
- \`GITHUB_WEBHOOK_SECRET\`: GitHub webhook secret
- \`GITHUB_APP_ID\`: GitHub App ID

#### OpenAI
- \`OPENAI_API_KEY\`: OpenAI API key
- \`OPENAI_MODEL\`: OpenAI model to use (default: gpt-4)
- \`OPENAI_MAX_TOKENS\`: Maximum tokens per request (default: 4000)

#### Anthropic
- \`ANTHROPIC_API_KEY\`: Anthropic API key
- \`ANTHROPIC_MODEL\`: Anthropic model to use (default: claude-3-sonnet-20240229)

### Monitoring Configuration

#### Logging
- \`LOG_LEVEL\`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- \`LOG_FORMAT\`: Log format (text, json)
- \`JSON_LOGGING\`: Enable JSON logging (default: false)

#### Metrics
- \`METRICS_ENABLED\`: Enable metrics collection (default: true)
- \`PROMETHEUS_ENABLED\`: Enable Prometheus metrics (default: false)
- \`PROMETHEUS_PORT\`: Prometheus metrics port (default: 9090)

#### Health Checks
- \`HEALTH_CHECKS_ENABLED\`: Enable health checks (default: true)
- \`HEALTH_CHECK_INTERVAL\`: Health check interval in seconds (default: 30)

## Configuration Validation

The configuration system validates all settings and provides detailed error messages for invalid values.
Use the ConfigManager class to load and validate configuration:

\`\`\`typescript
const configManager = new ConfigManager();
const result = configManager.load();

if (!result.success) {
  console.error('Configuration validation failed:', result.errors);
} else {
  const config = result.config;
  // Use validated configuration
}
\`\`\`

## Environment-Specific Configuration

Different environments can have different default values and validation rules:

- **Development**: More permissive settings, debug enabled
- **Staging**: Production-like settings with additional logging
- **Production**: Strict security settings, optimized performance

Set the \`ENVIRONMENT\` variable to control environment-specific behavior.
`;

    return docs.trim();
  }

  /**
   * Export configuration as JSON
   */
  exportConfig(): string {
    if (!this.config) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * Validate a partial configuration update
   */
  validateUpdate(update: Partial<UnifiedConfig>): { success: boolean; errors?: z.ZodError } {
    try {
      const currentConfig = this.getConfig();
      const updatedConfig = { ...currentConfig, ...update };
      UnifiedConfigSchema.parse(updatedConfig);
      return { success: true };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return { success: false, errors: error };
      }
      throw error;
    }
  }
}

// Create singleton instance
export const configManager = new ConfigManager();
