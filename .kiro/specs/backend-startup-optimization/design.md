# Design Document: Backend Startup Optimization

## Overview

This design establishes a robust startup framework for the AI Code Review Platform backend. The system will implement comprehensive environment configuration management, database migration automation, startup validation, and health monitoring. The design addresses critical blocking issues: empty root `.env` file, missing database migrations, hardcoded Docker Compose credentials, and insufficient startup validation.

The solution provides:
- **Configuration Management**: Centralized environment variable loading with validation
- **Database Migrations**: Complete Alembic migration framework with initial schema
- **Startup Validation**: Comprehensive checks for all dependencies before application starts
- **Error Reporting**: Clear, actionable error messages with sensitive data masking
- **Health Monitoring**: Detailed health check endpoints for orchestration systems
- **Dependency Optimization**: Organized optional dependency groups for smaller deployments

## Architecture

### High-Level Flow

```
Application Start
    ↓
Load Environment Variables (.env files)
    ↓
Validate Configuration (required vars, formats, lengths)
    ↓
Verify Database Connections (PostgreSQL, Neo4j, Redis)
    ↓
Apply Database Migrations (Alembic)
    ↓
Initialize Optional Services (Celery, LLM)
    ↓
Log Startup Summary
    ↓
Start FastAPI Application
    ↓
Health Check Endpoints Ready
```

### Configuration Layers

```
Environment Variables (.env files)
    ↓
Pydantic Settings (validation, defaults)
    ↓
Application Configuration (settings object)
    ↓
Component Initialization (databases, services)
```

### Startup Validation Pipeline

```
Required Variables Check
    ↓
Credential Format Validation
    ↓
Security Settings Validation
    ↓
Database Connection Verification
    ↓
Celery Configuration Validation
    ↓
Migration Status Check
    ↓
Optional Services Initialization
```

## Components and Interfaces

### 1. Configuration Manager (`app/core/config.py`)

**Responsibilities:**
- Load environment variables from `.env` files
- Validate required and optional configuration
- Provide computed properties for connection URLs
- Generate security warnings for weak settings

**Key Methods:**
```python
class Settings(BaseSettings):
    # Required fields (will raise ValidationError if missing)
    JWT_SECRET: str
    POSTGRES_PASSWORD: str
    NEO4J_PASSWORD: str
    
    # Optional fields with defaults
    GITHUB_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Validation methods
    def validate_security_settings() -> List[str]
    def validate_database_urls() -> List[str]
    def validate_celery_config() -> List[str]
    
    # Computed properties
    @property
    def postgres_url() -> str
    @property
    def redis_url() -> str
    @property
    def celery_broker_url() -> str
```

**Error Handling:**
- Missing required variables: Raise `ValidationError` with variable name
- Invalid formats: Raise `ValidationError` with expected format
- Weak security settings: Log warnings but allow startup

### 2. Startup Validator (`app/core/startup_validator.py`)

**Responsibilities:**
- Verify all required environment variables are present
- Check database connectivity
- Validate security settings
- Verify migration status
- Collect and report all errors at once

**Key Methods:**
```python
class StartupValidator:
    async def validate_all() -> StartupValidationResult
    async def validate_environment() -> List[ValidationError]
    async def validate_databases() -> List[DatabaseError]
    async def validate_security() -> List[SecurityWarning]
    async def validate_migrations() -> List[MigrationError]
    
    def format_error_report() -> str
```

**Validation Result:**
```python
@dataclass
class StartupValidationResult:
    is_valid: bool
    errors: List[str]  # Critical errors
    warnings: List[str]  # Non-critical warnings
    database_status: Dict[str, bool]  # PostgreSQL, Neo4j, Redis
    migration_status: str  # "pending", "applied", "error"
    summary: str  # Human-readable summary
```

### 3. Database Connection Manager (`app/database/connection_manager.py`)

**Responsibilities:**
- Establish connections to PostgreSQL, Neo4j, Redis
- Verify connections are working
- Handle connection failures gracefully
- Provide connection status information

**Key Methods:**
```python
class ConnectionManager:
    async def verify_postgres() -> ConnectionStatus
    async def verify_neo4j() -> ConnectionStatus
    async def verify_redis() -> ConnectionStatus
    async def verify_all() -> Dict[str, ConnectionStatus]
    
    def get_connection_error_message(error: Exception) -> str
```

**Connection Status:**
```python
@dataclass
class ConnectionStatus:
    service: str  # "PostgreSQL", "Neo4j", "Redis"
    is_connected: bool
    error: Optional[str]
    response_time_ms: float
    is_critical: bool  # True for PostgreSQL, False for optional services
```

### 4. Migration Manager (`app/database/migration_manager.py`)

**Responsibilities:**
- Check if migrations are pending
- Apply pending migrations automatically
- Provide migration status information
- Handle migration errors

**Key Methods:**
```python
class MigrationManager:
    async def check_pending_migrations() -> List[str]
    async def apply_pending_migrations() -> MigrationResult
    async def get_migration_status() -> MigrationStatus
    
    def format_migration_error(error: Exception) -> str
```

**Migration Status:**
```python
@dataclass
class MigrationStatus:
    pending_count: int
    applied_count: int
    current_version: str
    is_up_to_date: bool
    errors: List[str]
```

### 5. Error Reporter (`app/core/error_reporter.py`)

**Responsibilities:**
- Format error messages with sensitive data masking
- Provide actionable remediation guidance
- Collect multiple errors for batch reporting
- Log errors with appropriate severity levels

**Key Methods:**
```python
class ErrorReporter:
    def mask_sensitive_data(value: str) -> str
    def format_missing_variable_error(var_name: str, expected_format: str) -> str
    def format_connection_error(service: str, error: Exception) -> str
    def format_validation_error(field: str, reason: str) -> str
    def format_error_report(errors: List[str], warnings: List[str]) -> str
```

**Sensitive Data Patterns:**
- Passwords: `password=***`
- API Keys: `sk-***` (show first 3 and last 3 chars)
- Tokens: `ghp_***` (show first 3 and last 3 chars)
- Connection strings: Show host/port, mask password

### 6. Health Check Service (`app/services/health_service.py`)

**Responsibilities:**
- Provide health status of application and dependencies
- Implement Kubernetes-style probes (liveness, readiness)
- Return detailed status information
- Update status in real-time

**Key Methods:**
```python
class HealthService:
    async def get_health_status() -> HealthStatus
    async def get_readiness_status() -> ReadinessStatus
    async def get_liveness_status() -> LivenessStatus
    
    async def check_database_health() -> Dict[str, bool]
    async def check_service_health() -> Dict[str, bool]
```

**Health Status:**
```python
@dataclass
class HealthStatus:
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    environment: str
    timestamp: datetime
    databases: Dict[str, DatabaseHealth]
    services: Dict[str, ServiceHealth]
    
@dataclass
class DatabaseHealth:
    name: str
    is_connected: bool
    response_time_ms: float
    error: Optional[str]
```

### 7. Logging Configuration (`app/core/logging_config.py`)

**Responsibilities:**
- Configure structured logging
- Mask sensitive data in logs
- Provide startup diagnostics
- Support JSON logging for log aggregation

**Key Methods:**
```python
class LoggingConfig:
    def setup_logging(level: str, enable_json: bool) -> None
    def log_startup_summary(config: Settings, validation: StartupValidationResult) -> None
    def mask_sensitive_in_logs(message: str) -> str
    def log_database_status(status: Dict[str, ConnectionStatus]) -> None
```

## Data Models

### Environment Configuration

```python
@dataclass
class EnvironmentConfig:
    # Database
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Cache
    redis_host: str
    redis_port: int
    redis_password: Optional[str]
    
    # Graph Database
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Security
    jwt_secret: str
    jwt_algorithm: str
    bcrypt_rounds: int
    
    # Optional APIs
    github_token: Optional[str]
    openai_api_key: Optional[str]
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    # Application
    environment: str  # development, staging, production
    debug: bool
    log_level: str
```

### Validation Result

```python
@dataclass
class ValidationResult:
    field: str
    is_valid: bool
    error_message: Optional[str]
    expected_format: Optional[str]
    current_value: Optional[str]  # Masked if sensitive
```

### Migration Schema

```python
@dataclass
class MigrationFile:
    version: str  # e.g., "001"
    timestamp: datetime
    description: str
    upgrade_script: str
    downgrade_script: str
    is_applied: bool
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Environment Variable Loading
*For any* set of environment variables in a `.env` file, the Settings object should successfully load all variables and make them accessible through the settings instance.
**Validates: Requirements 1.1**

### Property 2: Missing Required Variable Detection
*For any* required environment variable that is missing, the Settings initialization should raise a ValidationError that includes the variable name.
**Validates: Requirements 1.2**

### Property 3: Credential Non-Empty Validation
*For any* required credential field, if the value is an empty string, the Settings initialization should raise a ValidationError.
**Validates: Requirements 1.3**

### Property 4: Optional Variable Defaults
*For any* optional environment variable that is missing, the Settings object should use the defined default value or disable the feature gracefully.
**Validates: Requirements 1.4**

### Property 5: Environment-Specific Configuration
*For any* environment value (development, staging, production), the Settings object should load the appropriate configuration for that environment.
**Validates: Requirements 1.5**

### Property 6: Sensitive Data Masking in Logs
*For any* log message containing sensitive data (passwords, API keys), the logged message should not contain the actual sensitive value.
**Validates: Requirements 1.6**

### Property 7: Docker Compose Environment Variable Usage
*For any* credential in docker-compose.yml, the value should use environment variable syntax (${VAR_NAME}) rather than hardcoded values.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 8: No Hardcoded Test Credentials
*For any* docker-compose.yml file, it should not contain known test credentials like "postgres", "password", "123456789", or "neo4j".
**Validates: Requirements 3.5**

### Property 9: Migration Table Creation
*For any* migration that is applied, the corresponding database tables should be created and queryable.
**Validates: Requirements 4.2**

### Property 10: Migration Bidirectionality
*For any* migration, applying it and then rolling it back should restore the database to its previous state.
**Validates: Requirements 4.4**

### Property 11: Automatic Migration on Empty Database
*For any* empty database, starting the application should automatically apply all pending migrations.
**Validates: Requirements 4.5**

### Property 12: Startup Validation Completeness
*For any* missing required environment variable, the startup validation should detect it and include it in the error report.
**Validates: Requirements 5.1**

### Property 13: Database Connection Verification
*For any* database service (PostgreSQL, Neo4j, Redis), the startup validator should attempt to connect and report the connection status.
**Validates: Requirements 5.2, 6.1, 6.2, 6.3**

### Property 14: JWT Secret Length Validation
*For any* JWT_SECRET value, if it is less than 32 characters, the startup validator should report a validation error.
**Validates: Requirements 5.3**

### Property 15: BCRYPT Rounds Validation
*For any* BCRYPT_ROUNDS value, if it is less than 12, the startup validator should report a validation error.
**Validates: Requirements 5.4**

### Property 16: Critical vs Optional Dependency Handling
*For any* critical dependency (PostgreSQL) that fails, the application should fail startup; for optional dependencies (Neo4j), the application should log a warning and continue.
**Validates: Requirements 5.5, 5.6**

### Property 17: Non-Zero Exit Code on Validation Failure
*For any* startup validation failure, the application should exit with a non-zero exit code.
**Validates: Requirements 5.7**

### Property 18: Error Message Completeness
*For any* validation error, the error message should include the variable name, expected format, and remediation guidance.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 19: Sensitive Data Masking in Error Messages
*For any* error message containing sensitive data, the message should mask the sensitive value (e.g., password=***, sk-***).
**Validates: Requirements 7.5**

### Property 20: Configuration Summary Masking
*For any* configuration summary displayed at startup, sensitive values should be masked while non-sensitive values are visible.
**Validates: Requirements 7.6**

### Property 21: Celery Configuration Validation
*For any* Celery configuration, the startup validator should verify that CELERY_BROKER_URL and CELERY_RESULT_BACKEND are reachable.
**Validates: Requirements 8.1, 8.2**

### Property 22: Celery Graceful Degradation
*For any* Celery configuration that is invalid or disabled, the application should start without Celery functionality.
**Validates: Requirements 8.5**

### Property 23: Dependency Organization
*For any* requirements file, base dependencies should be in requirements.txt, and optional dependencies should be in separate files (requirements-test.txt, requirements-llm.txt, etc.).
**Validates: Requirements 9.1, 9.2, 9.3, 9.4**

### Property 24: Production Dependency Minimization
*For any* production Docker build, only base dependencies should be installed, resulting in a smaller image than development builds.
**Validates: Requirements 9.5**

### Property 25: Docker Multi-Stage Build
*For any* Docker image build, the Dockerfile should use multi-stage builds to separate build dependencies from runtime dependencies.
**Validates: Requirements 10.1, 10.2**

### Property 26: Docker Base Image Minimization
*For any* Docker image, the base image should be Alpine Linux or another minimal image (not full Ubuntu/Debian).
**Validates: Requirements 10.3**

### Property 27: Startup Logging Completeness
*For any* application startup, the logs should include application name, version, environment, configuration file path, database status, and optional features status.
**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**

### Property 28: Health Check Status Code
*For any* call to the `/health` endpoint when the application is healthy, the response should have a 200 status code.
**Validates: Requirements 12.1**

### Property 29: Health Check Response Content
*For any* call to the `/health` endpoint, the response should include database connection status, application version, and environment.
**Validates: Requirements 12.2, 12.3**

### Property 30: Health Check Degraded Status
*For any* database that is unavailable, the `/health` endpoint should return a 503 status code and indicate which database is down.
**Validates: Requirements 12.4**

### Property 31: Readiness Probe Strictness
*For any* call to the `/health/ready` endpoint, it should return 200 only if all required dependencies are ready (PostgreSQL, migrations applied).
**Validates: Requirements 12.5**

### Property 32: Liveness Probe Simplicity
*For any* call to the `/health/live` endpoint, it should return 200 if the application process is running, regardless of dependency status.
**Validates: Requirements 12.6**

## Error Handling

### Configuration Errors

**Missing Required Variable:**
```
ERROR: Missing required environment variable: JWT_SECRET
Expected format: 32+ character hex string
How to fix: Generate with: openssl rand -hex 32
```

**Invalid Credential Format:**
```
ERROR: Invalid POSTGRES_PASSWORD format
Expected: Non-empty string
Current: (empty)
How to fix: Set POSTGRES_PASSWORD to a secure password
```

**Weak Security Setting:**
```
WARNING: JWT_SECRET is only 16 characters (minimum 32 recommended)
This may reduce security. Consider regenerating with: openssl rand -hex 32
```

### Database Connection Errors

**Connection Refused:**
```
ERROR: Cannot connect to PostgreSQL at postgres:5432
Error: Connection refused
How to fix: Ensure PostgreSQL is running and accessible at postgres:5432
```

**Authentication Failed:**
```
ERROR: PostgreSQL authentication failed
Error: FATAL: password authentication failed for user "postgres"
How to fix: Verify POSTGRES_USER and POSTGRES_PASSWORD are correct
```

**Timeout:**
```
ERROR: PostgreSQL connection timeout (5s)
Error: Connection timeout
How to fix: Check network connectivity and PostgreSQL service status
```

### Migration Errors

**Migration Failed:**
```
ERROR: Migration 002_add_users_table failed
Error: Column "email" already exists
How to fix: Check migration file for conflicts with existing schema
```

**Pending Migrations:**
```
WARNING: 3 pending migrations
Run: alembic upgrade head
```

### Startup Validation Errors

**Multiple Errors:**
```
STARTUP VALIDATION FAILED

Critical Errors:
1. Missing required environment variable: JWT_SECRET
2. PostgreSQL connection failed: Connection refused
3. Missing required environment variable: POSTGRES_PASSWORD

Warnings:
1. Neo4j connection failed (optional): Connection refused
2. Redis connection failed (optional): Connection refused

How to fix:
1. Set JWT_SECRET to a 32+ character value
2. Ensure PostgreSQL is running at postgres:5432
3. Set POSTGRES_PASSWORD to a secure password
4. (Optional) Start Neo4j and Redis services

Application startup aborted.
```

## Testing Strategy

### Unit Testing

**Configuration Validation:**
- Test loading valid environment variables
- Test missing required variables raise errors
- Test invalid credential formats are rejected
- Test optional variables use defaults
- Test environment-specific configuration

**Error Reporting:**
- Test sensitive data masking in error messages
- Test error message formatting and completeness
- Test remediation guidance is provided
- Test multiple errors are collected and reported

**Connection Management:**
- Test successful database connections
- Test connection failures are handled gracefully
- Test connection status is reported accurately
- Test connection timeouts are handled

**Health Checks:**
- Test health endpoint returns correct status codes
- Test health endpoint includes required information
- Test readiness probe strictness
- Test liveness probe simplicity

### Property-Based Testing

**Configuration Loading:**
- **Property 1**: For any valid environment variables, Settings should load them successfully
- **Property 2**: For any missing required variable, Settings should raise ValidationError with variable name
- **Property 3**: For any empty credential, Settings should raise ValidationError

**Docker Compose Security:**
- **Property 7**: For any credential in docker-compose.yml, it should use ${VAR_NAME} syntax
- **Property 8**: For any docker-compose.yml, it should not contain known test credentials

**Database Migrations:**
- **Property 9**: For any applied migration, corresponding tables should exist
- **Property 10**: For any migration, upgrade then downgrade should restore state

**Startup Validation:**
- **Property 12**: For any missing required variable, startup validation should detect it
- **Property 13**: For any database service, startup validator should verify connectivity
- **Property 17**: For any validation failure, exit code should be non-zero

**Health Checks:**
- **Property 28**: For any healthy application, /health should return 200
- **Property 30**: For any unavailable database, /health should return 503
- **Property 31**: For any missing dependency, /health/ready should return non-200

### Integration Testing

**Full Startup Flow:**
- Start with empty database and verify migrations run automatically
- Start with missing environment variables and verify startup fails with clear error
- Start with unavailable databases and verify appropriate handling
- Start with all services available and verify successful startup

**Health Check Integration:**
- Verify health endpoints work after startup
- Verify health endpoints reflect database status changes
- Verify readiness probe blocks traffic until ready

### Configuration Testing

**Environment-Specific:**
- Test development configuration loads correctly
- Test staging configuration loads correctly
- Test production configuration loads correctly
- Test configuration differences are applied

**Dependency Optimization:**
- Test base requirements install successfully
- Test optional requirements install successfully
- Test production build uses only base requirements
- Test development build can install all requirements

## Implementation Notes

### Alembic Migration Strategy

1. **Initial Migration**: Create `001_initial_schema.py` with all base tables
2. **Naming Convention**: `{version}_{description}.py` (e.g., `002_add_users_table.py`)
3. **Auto-generation**: Use `alembic revision --autogenerate` for schema changes
4. **Manual Review**: Always review generated migrations before applying
5. **Downgrade Support**: Ensure all migrations support downgrade operations

### Environment Variable Precedence

1. System environment variables (highest priority)
2. `.env` file in current directory
3. `.env.{ENVIRONMENT}` file (e.g., `.env.production`)
4. Default values in Settings class (lowest priority)

### Sensitive Data Masking Rules

- Passwords: Show first 0 chars, last 0 chars (fully masked)
- API Keys: Show first 3 chars, last 3 chars (e.g., `sk-***`)
- Tokens: Show first 3 chars, last 3 chars (e.g., `ghp_***`)
- Connection Strings: Show host/port, mask password
- URLs: Show scheme and host, mask credentials

### Health Check Endpoints

- `/health`: Overall health status (200 if healthy, 503 if degraded)
- `/health/ready`: Readiness probe (200 only if all required dependencies ready)
- `/health/live`: Liveness probe (200 if process running)

### Logging Levels

- **DEBUG**: Detailed configuration values (with masking)
- **INFO**: Startup summary, database status, feature status
- **WARNING**: Security warnings, optional service failures
- **ERROR**: Critical failures, startup validation errors

