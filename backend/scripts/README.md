# Backend Scripts

This directory contains utility scripts for backend operations and maintenance.

## Configuration Validation Tool

### Overview

The `validate_config.py` script validates environment configuration for backend-frontend connectivity. It checks for:

- Required environment variables
- Port conflicts between services
- URL format validation and accessibility
- Configuration consistency

### Usage

```bash
# Validate all configuration (default)
python backend/scripts/validate_config.py

# Validate only required variables
python backend/scripts/validate_config.py --mode required

# Validate only port configurations
python backend/scripts/validate_config.py --mode ports

# Validate only URL formats and accessibility
python backend/scripts/validate_config.py --mode urls

# Enable verbose output
python backend/scripts/validate_config.py --verbose

# Output results in JSON format
python backend/scripts/validate_config.py --json

# Combine options
python backend/scripts/validate_config.py --mode ports --verbose --json
```

### Validation Modes

- **all** (default): Validate all configuration settings
- **required**: Check only required environment variables
- **ports**: Check only port configurations and conflicts
- **urls**: Check only URL formats and accessibility

### Exit Codes

- **0**: Validation passed (all checks successful)
- **1**: Validation failed (one or more errors found)

### Output Formats

#### Human-Readable Format (Default)

```
======================================================================
CONFIGURATION VALIDATION REPORT
======================================================================

Status: ✅ PASSED
Errors: 0
Warnings: 0

----------------------------------------------------------------------
CONFIGURATION SUMMARY
----------------------------------------------------------------------

PORTS:
  backend: Backend (FastAPI) on port 8000
  frontend: Frontend (Next.js) on port 3000
  postgres: PostgreSQL on port 5432
  redis: Redis on port 6379
  neo4j: Neo4j on port 7687

======================================================================
```

#### JSON Format

```json
{
  "is_valid": true,
  "status": "PASSED",
  "errors": [],
  "warnings": [],
  "config_summary": {
    "ports": {
      "backend": "Backend (FastAPI) on port 8000",
      "frontend": "Frontend (Next.js) on port 3000",
      "postgres": "PostgreSQL on port 5432",
      "redis": "Redis on port 6379",
      "neo4j": "Neo4j on port 7687"
    }
  },
  "error_count": 0,
  "warning_count": 0
}
```

### Integration with CI/CD

You can use this script in your CI/CD pipeline to validate configuration before deployment:

```bash
# In your CI/CD script
python backend/scripts/validate_config.py
if [ $? -ne 0 ]; then
    echo "Configuration validation failed!"
    exit 1
fi
```

### Requirements Validated

This tool validates the following requirements from the backend-frontend-connectivity-improvement spec:

- **Requirement 10.1**: Configuration validation command
- **Requirement 10.2**: Report missing or invalid variables
- **Requirement 10.3**: Detect port conflicts
- **Requirement 10.4**: Validate URL accessibility
- **Requirement 10.5**: Output validation summary

### Troubleshooting

#### Missing Environment Variables

If you see errors about missing environment variables, ensure your `.env` file contains all required variables:

```bash
# Required variables
JWT_SECRET=<your-jwt-secret>
SECRET_KEY=<your-secret-key>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-password>
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
REDIS_HOST=redis
REDIS_PORT=6379
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Port Conflicts

If you see port conflict errors, check that no two services are configured to use the same port. Common conflicts:

- Backend and frontend using the same port
- Database services using conflicting ports
- Services conflicting with other applications on your system

#### URL Accessibility Issues

If you see URL accessibility warnings, ensure:

- Services are running and accessible
- Firewall rules allow connections
- URLs are correctly formatted
- DNS resolution is working

### Development

To run tests for the CLI tool:

```bash
cd backend
python -m pytest tests/test_validate_config_cli.py -v
```
