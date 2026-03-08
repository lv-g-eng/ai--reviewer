# Configuration Management System

## Overview

The ConfigService provides centralized environment configuration management for the frontend application. It ensures that all required configuration is present, valid, and type-safe before the application starts.

## Features

- ✅ Environment-specific configuration (development, test, production)
- ✅ Environment variable validation
- ✅ Type-safe configuration access
- ✅ Clear error messages for missing or invalid configuration
- ✅ Singleton pattern for consistent configuration access
- ✅ Configuration parsing and formatting utilities

## Requirements Validation

This implementation validates the following requirements:

- **8.1**: Maintains independent configuration files for development, test, and production
- **8.2**: Loads sensitive configuration from environment variables (not hardcoded)
- **8.3**: Validates all required environment variables on application startup
- **8.5**: Displays clear error messages and refuses to start with invalid configuration
- **20.1**: Parses configuration files into Configuration objects
- **20.2**: Returns errors with field names and descriptions for invalid configuration
- **20.5**: Validates all required fields exist and have correct types

## Usage

### Basic Usage

```typescript
import ConfigService from '@/services/config';

// Load configuration (typically done once at app startup)
const config = ConfigService.load();

// Get specific configuration values
const apiUrl = ConfigService.get('apiBaseUrl');
const environment = ConfigService.get('environment');
const features = ConfigService.get('features');

// Check if debug mode is enabled
if (ConfigService.get('enableDebugMode')) {
  console.log('Debug mode is enabled');
}
```

### In Application Entry Point

```typescript
// app/layout.tsx or similar
import ConfigService from '@/services/config';

try {
  // Load and validate configuration on startup
  const config = ConfigService.load();
  console.log(`Application starting in ${config.environment} mode`);
} catch (error) {
  // Configuration errors will prevent app from starting
  console.error('Configuration error:', error.message);
  throw error;
}
```

### Validation

```typescript
import ConfigService from '@/services/config';

const partialConfig = {
  apiBaseUrl: 'http://localhost:8000',
  environment: 'development',
  enableDebugMode: true,
  features: {
    enablePWA: false,
    enableOfflineMode: false,
    enablePerformanceMonitoring: true,
  },
};

const result = ConfigService.validate(partialConfig);

if (!result.valid) {
  console.error('Validation errors:');
  result.errors.forEach(error => {
    console.error(`- ${error.field}: ${error.message}`);
  });
}
```

### Configuration Parsing and Formatting

```typescript
import ConfigService from '@/services/config';

// Parse configuration from JSON string
const configString = '{"apiBaseUrl":"http://localhost:8000",...}';
const config = ConfigService.parseConfig(configString);

// Format configuration to JSON string
const formatted = ConfigService.formatConfig(config);
console.log(formatted);
```

## Environment Setup

### Development

1. Copy `.env.development.example` to `.env.development`
2. Update values as needed:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING=true
   ```

### Test

1. Copy `.env.test.example` to `.env.test`
2. Configure for test environment:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NODE_ENV=test
   ```

### Production

1. Copy `.env.production.example` to `.env.production`
2. Set all required production values:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
   NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   NEXT_PUBLIC_CDN_URL=https://cdn.yourdomain.com
   NEXT_PUBLIC_ENABLE_PWA=true
   NEXT_PUBLIC_ENABLE_OFFLINE_MODE=true
   NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING=true
   ```

## Configuration Schema

```typescript
interface AppConfig {
  // Required: Base URL for API requests
  apiBaseUrl: string;
  
  // Required: Current environment
  environment: 'development' | 'test' | 'production';
  
  // Required: Enable debug logging and tools
  enableDebugMode: boolean;
  
  // Optional: Sentry DSN for error monitoring
  sentryDsn?: string;
  
  // Optional: CDN URL for static assets
  cdnUrl?: string;
  
  // Required: Feature flags
  features: {
    enablePWA: boolean;
    enableOfflineMode: boolean;
    enablePerformanceMonitoring: boolean;
  };
}
```

## Error Handling

### Missing Required Variables

If required environment variables are missing, the application will throw an error:

```
Missing required environment variables:
NEXT_PUBLIC_API_BASE_URL

Please set these variables in your .env file or environment.
Application cannot start without required configuration.
```

### Invalid Configuration

If configuration validation fails, the application will throw an error with details:

```
Configuration validation failed:
apiBaseUrl: API base URL must be a valid URL
features.enablePWA: features.enablePWA must be a boolean

Application cannot start with invalid configuration.
```

### Invalid Configuration Format

If parsing a configuration file fails:

```
Configuration file format is invalid:
Line 5: Unexpected token } in JSON at position 123
```

## Testing

The ConfigService can be reset between tests:

```typescript
import ConfigService from '@/services/config';

beforeEach(() => {
  ConfigService.reset();
});

test('loads configuration', () => {
  const config = ConfigService.load();
  expect(config.environment).toBe('test');
});
```

## Best Practices

1. **Never hardcode sensitive values**: Always use environment variables
2. **Validate early**: Call `ConfigService.load()` at application startup
3. **Use type-safe access**: Use `ConfigService.get()` for type safety
4. **Document required variables**: Keep `.env.*.example` files up to date
5. **Fail fast**: Let the application refuse to start with invalid configuration

## Security Considerations

- Never commit `.env` files to version control
- Use different values for each environment
- Rotate sensitive values (API keys, DSNs) regularly
- Use HTTPS URLs in production
- Validate all configuration before use

## Troubleshooting

### Application won't start

1. Check that all required environment variables are set
2. Verify `.env` file exists for your environment
3. Check that values are valid (URLs, booleans, etc.)
4. Review error messages for specific validation failures

### Configuration not updating

1. Restart the development server
2. Clear Next.js cache: `rm -rf .next`
3. Verify you're editing the correct `.env` file for your environment

### Type errors

1. Ensure TypeScript is up to date
2. Run `npm run type-check` to verify types
3. Check that configuration matches the `AppConfig` interface
