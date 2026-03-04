# Production Environment Setup Guide

This guide provides step-by-step instructions for setting up and validating the production environment configuration for the AI Code Review Platform.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration Files](#configuration-files)
4. [Environment Variables](#environment-variables)
5. [Validation Scripts](#validation-scripts)
6. [Setup Steps](#setup-steps)
7. [Validation Process](#validation-process)
8. [Troubleshooting](#troubleshooting)

## Overview

Task 1.1 of the production environment migration creates and validates all necessary configuration files and scripts for production deployment. This includes:

- Production environment configuration file (`.env.production`)
- Environment validation script (`scripts/validate-production-env.sh`)
- Database connection test script (`scripts/test_db_connections.py`)
- SSL certificate setup documentation

## Prerequisites

Before setting up the production environment, ensure you have:

1. **System Requirements**:
   - Linux/Unix-based system (Ubuntu 20.04+ recommended)
   - Bash shell (for validation scripts)
   - Python 3.8+ (for database connection tests)

2. **Required Python Packages**:
   ```bash
   pip install psycopg2-binary neo4j redis
   ```

3. **Database Services**:
   - PostgreSQL 13+ running and accessible
   - Neo4j 4.4+ running and accessible
   - Redis 6+ running and accessible

4. **SSL Certificates**:
   - Valid SSL certificate for your domain
   - Certificate files placed in `certs/` directory
   - See [SSL Certificate Setup](./SSL_CERTIFICATE_SETUP.md) for details

5. **Domain Configuration**:
   - Domain name registered and DNS configured
   - Domain pointing to your server's IP address

## Configuration Files

### 1. `.env.production`

The main production environment configuration file containing all environment variables.

**Location**: Project root directory

**Security**: 
- This file contains sensitive credentials
- It is automatically excluded from version control (`.gitignore`)
- **NEVER commit this file to Git**

**Template**: A template file `.env.production.template` is provided with placeholder values.

### 2. `scripts/validate-production-env.sh`

Bash script that validates the production environment configuration.

**Features**:
- Checks all required environment variables are set
- Validates secret key lengths (minimum 32 characters)
- Verifies database passwords are not placeholders
- Tests database connections
- Validates SSL certificates
- Checks security configurations

**Usage**:
```bash
bash scripts/validate-production-env.sh
```

### 3. `scripts/test_db_connections.py`

Python script that tests connectivity to all required databases.

**Features**:
- Tests PostgreSQL connection
- Tests Neo4j connection
- Tests Redis connection
- Reports connection status and versions
- Provides troubleshooting tips on failure

**Usage**:
```bash
python3 scripts/test_db_connections.py
```

### 4. `docs/SSL_CERTIFICATE_SETUP.md`

Comprehensive documentation for SSL certificate setup and validation.

**Contents**:
- Certificate requirements
- Obtaining certificates (Let's Encrypt, commercial CA)
- Installation instructions
- Validation procedures
- Renewal process
- Troubleshooting guide

## Environment Variables

### Critical Variables (Must Be Changed)

The following variables **MUST** be changed from their placeholder values before deployment:

#### Security Secrets
```bash
JWT_SECRET=CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32
SECRET_KEY=CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32
SESSION_SECRET=CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32
ENCRYPTION_KEY=CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32
```

**Generate with**:
```bash
openssl rand -hex 32
```

#### Database Passwords
```bash
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD_MIN_32_CHARS
NEO4J_PASSWORD=CHANGE_ME_STRONG_PASSWORD_MIN_32_CHARS
REDIS_PASSWORD=CHANGE_ME_STRONG_PASSWORD_MIN_32_CHARS
```

**Generate with**:
```bash
openssl rand -base64 32
```

#### Domain Configuration
```bash
NEXT_PUBLIC_API_URL=https://your-domain.com/api/v1
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Replace `your-domain.com` with your actual domain.

#### GitHub Integration
```bash
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
GITHUB_CALLBACK_URL=https://your-domain.com/api/v1/auth/github/callback
GITHUB_WEBHOOK_SECRET=CHANGE_ME_GENERATE_WITH_OPENSSL_RAND_HEX_32
GITHUB_TOKEN=your_github_personal_access_token
```

#### LLM Provider
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
# Or alternative providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Database Configuration

#### PostgreSQL
```bash
POSTGRES_DB=ai_code_review_prod
POSTGRES_USER=ai_review_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

#### Neo4j
```bash
NEO4J_USER=neo4j
NEO4J_PASSWORD=<strong-password>
NEO4J_URI=bolt://neo4j:7687
NEO4J_DATABASE=neo4j
```

#### Redis
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<strong-password>
REDIS_DB=0
```

### Security Configuration

```bash
# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=5000
ENABLE_RATE_LIMITING=true

# Security Headers
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000
ENABLE_CSP=true

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Monitoring Configuration

```bash
# Tracing
TRACING_ENABLED=true
OTLP_ENDPOINT=http://otel-collector:4317
TRACING_SAMPLE_RATE=0.1

# Metrics
ENABLE_METRICS=true
METRICS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Validation Scripts

### Environment Validation Script

The `validate-production-env.sh` script performs comprehensive validation:

#### Checks Performed

1. **Environment Variables**
   - Verifies all required variables are set
   - Checks for placeholder values
   - Validates variable formats

2. **Secret Keys**
   - Validates minimum length (32 characters)
   - Checks for placeholder values ("CHANGE_ME")
   - Ensures keys are properly generated

3. **Database Passwords**
   - Validates password length
   - Checks for placeholder values
   - Recommends strong passwords

4. **API Configuration**
   - Verifies HTTPS usage
   - Checks domain configuration
   - Validates CORS settings

5. **Security Settings**
   - Verifies rate limiting is enabled
   - Checks HSTS configuration
   - Validates CSP settings

6. **Database Connections**
   - Tests PostgreSQL connectivity
   - Tests Neo4j connectivity
   - Tests Redis connectivity

7. **SSL Certificates**
   - Verifies certificate files exist
   - Checks certificate expiration
   - Warns if expiring soon (< 30 days)

#### Exit Codes

- `0`: All checks passed (may have warnings)
- `1`: One or more checks failed

### Database Connection Test Script

The `test_db_connections.py` script tests database connectivity:

#### Features

- **PostgreSQL Test**: Connects and retrieves version
- **Neo4j Test**: Connects and retrieves version/edition
- **Redis Test**: Connects and retrieves version
- **Detailed Reporting**: Shows success/failure for each database
- **Troubleshooting**: Provides tips on connection failures

#### Requirements

Install required Python packages:

```bash
pip install psycopg2-binary neo4j redis
```

## Setup Steps

### Step 1: Copy Template to Production File

```bash
cp .env.production.template .env.production
```

### Step 2: Generate Secrets

Generate all required secrets:

```bash
# Generate JWT secret
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env.production.tmp

# Generate SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.production.tmp

# Generate SESSION_SECRET
echo "SESSION_SECRET=$(openssl rand -hex 32)" >> .env.production.tmp

# Generate ENCRYPTION_KEY
echo "ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env.production.tmp

# Generate database passwords
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env.production.tmp
echo "NEO4J_PASSWORD=$(openssl rand -base64 32)" >> .env.production.tmp
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.production.tmp

# Generate GitHub webhook secret
echo "GITHUB_WEBHOOK_SECRET=$(openssl rand -hex 32)" >> .env.production.tmp
```

### Step 3: Update Configuration

Edit `.env.production` and update the following:

1. **Domain Configuration**:
   - Replace `your-domain.com` with your actual domain
   - Update `NEXT_PUBLIC_API_URL`
   - Update `CORS_ALLOWED_ORIGINS`
   - Update `GITHUB_CALLBACK_URL`

2. **Database Hosts** (if not using Docker):
   - Update `POSTGRES_HOST`
   - Update `NEO4J_URI`
   - Update `REDIS_HOST`

3. **API Keys**:
   - Add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
   - Add `GITHUB_TOKEN`
   - Add `OPENROUTER_API_KEY` or other LLM provider keys

4. **Optional Services**:
   - Configure Sentry DSN (if using)
   - Configure backup S3 bucket and AWS credentials
   - Configure SMTP settings for email notifications

### Step 4: Set Up SSL Certificates

Follow the [SSL Certificate Setup Guide](./SSL_CERTIFICATE_SETUP.md):

1. Obtain SSL certificate (Let's Encrypt recommended)
2. Place certificate files in `certs/` directory:
   - `certs/fullchain.pem`
   - `certs/privkey.pem`
3. Set correct permissions:
   ```bash
   chmod 644 certs/fullchain.pem
   chmod 600 certs/privkey.pem
   ```

### Step 5: Install Python Dependencies

```bash
pip install psycopg2-binary neo4j redis
```

### Step 6: Make Scripts Executable

```bash
chmod +x scripts/validate-production-env.sh
chmod +x scripts/test_db_connections.py
```

## Validation Process

### Run Complete Validation

Execute the validation script:

```bash
bash scripts/validate-production-env.sh
```

### Expected Output

#### Successful Validation

```
=========================================
Production Environment Validation
=========================================

[INFO] Checking required environment variables...
[✓] Environment variable set: ENVIRONMENT
[✓] Environment variable set: POSTGRES_HOST
[✓] Environment variable set: POSTGRES_PORT
...

[INFO] Validating environment setting...
[✓] Environment is set to production
[✓] Debug mode is disabled

[INFO] Validating secret keys...
[✓] JWT_SECRET length is sufficient (64 characters)
[✓] SECRET_KEY length is sufficient (64 characters)
...

[INFO] Testing database connections...
[INFO] Running database connection tests...
[✓] PostgreSQL: Connected successfully
[✓] Neo4j: Connected successfully
[✓] Redis: Connected successfully

[INFO] Validating SSL certificates...
[✓] SSL certificate files found
[✓] SSL certificate is valid for 85 more days

=========================================
Validation Summary
=========================================
Successful checks: 45
Warnings: 0
Errors: 0

✓ All validation checks passed!
Production environment is ready for deployment.
```

#### Validation with Warnings

```
=========================================
Validation Summary
=========================================
Successful checks: 42
Warnings: 3
Errors: 0

⚠ Validation passed with warnings.
Please review the warnings above before deploying to production.
```

#### Validation Failure

```
=========================================
Validation Summary
=========================================
Successful checks: 35
Warnings: 2
Errors: 5

✗ Validation failed with 5 error(s).
Please fix the errors above before deploying to production.
```

### Test Database Connections Separately

```bash
python3 scripts/test_db_connections.py
```

Expected output:

```
==================================================
Database Connection Tests
==================================================

[INFO] Testing PostgreSQL connection...
[INFO] Connecting to PostgreSQL at postgres:5432...
[✓] PostgreSQL: Connected successfully (PostgreSQL 15.3)

[INFO] Testing Neo4j connection...
[INFO] Connecting to Neo4j at bolt://neo4j:7687...
[✓] Neo4j: Connected successfully (Neo4j 5.9.0 community)

[INFO] Testing Redis connection...
[INFO] Connecting to Redis at redis:6379...
[✓] Redis: Connected successfully (Redis 7.0.11)

==================================================
Connection Test Summary
==================================================
PostgreSQL      ✓ PASS
Neo4j           ✓ PASS
Redis           ✓ PASS

Total: 3 | Passed: 3 | Failed: 0

[✓] All database connections successful!
```

## Troubleshooting

### Common Issues

#### 1. Missing Environment Variables

**Error**: `Missing required environment variable: POSTGRES_PASSWORD`

**Solution**:
- Ensure `.env.production` file exists
- Verify all required variables are set
- Check for typos in variable names

#### 2. Placeholder Values Not Changed

**Error**: `JWT_SECRET still contains placeholder value - must be changed`

**Solution**:
- Generate new secrets using `openssl rand -hex 32`
- Replace all `CHANGE_ME` placeholders
- Update domain placeholders (`your-domain.com`)

#### 3. Database Connection Failed

**Error**: `PostgreSQL: Connection failed: could not connect to server`

**Solution**:
- Verify database service is running
- Check database host and port configuration
- Verify credentials are correct
- Check firewall rules
- Ensure database accepts connections from your IP

#### 4. SSL Certificate Not Found

**Error**: `SSL certificate files not found in certs/ directory`

**Solution**:
- Obtain SSL certificate (see [SSL Certificate Setup](./SSL_CERTIFICATE_SETUP.md))
- Place certificate files in `certs/` directory
- Verify file names: `fullchain.pem`, `privkey.pem`

#### 5. Certificate Expired

**Error**: `SSL certificate has expired`

**Solution**:
- Renew certificate immediately
- Follow renewal process in SSL documentation
- Set up automatic renewal for Let's Encrypt

#### 6. Permission Denied

**Error**: `Permission denied` when running scripts

**Solution**:
```bash
chmod +x scripts/validate-production-env.sh
chmod +x scripts/test_db_connections.py
```

#### 7. Python Package Not Found

**Error**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**:
```bash
pip install psycopg2-binary neo4j redis
```

### Getting Help

If you encounter issues not covered here:

1. Check the validation script output for specific error messages
2. Review the [SSL Certificate Setup Guide](./SSL_CERTIFICATE_SETUP.md)
3. Check database service logs
4. Verify network connectivity
5. Consult the main [Production Environment Migration Design Document](../.kiro/specs/production-environment-migration/design.md)

## Security Best Practices

1. **Never Commit Secrets**:
   - `.env.production` is in `.gitignore`
   - Never commit this file to version control
   - Use secret management tools for team sharing

2. **Strong Passwords**:
   - Use minimum 32-character passwords
   - Use cryptographically secure random generation
   - Rotate passwords regularly (every 90 days)

3. **Restrict Access**:
   - Limit who has access to `.env.production`
   - Use file permissions to restrict access
   - Audit access to production credentials

4. **Monitor and Alert**:
   - Set up monitoring for failed authentication attempts
   - Alert on certificate expiration
   - Monitor for unusual database activity

5. **Regular Audits**:
   - Run validation script regularly
   - Review security configurations
   - Update dependencies and certificates

## Next Steps

After completing this setup:

1. **Verify Configuration**: Run validation script and ensure all checks pass
2. **Test Connections**: Verify all database connections work
3. **Review Security**: Double-check all security settings
4. **Document Changes**: Note any custom configurations
5. **Proceed to Task 1.2**: Continue with the production environment migration

## Related Documentation

- [SSL Certificate Setup Guide](./SSL_CERTIFICATE_SETUP.md)
- [Production Environment Migration Design](../.kiro/specs/production-environment-migration/design.md)
- [Production Environment Migration Requirements](../.kiro/specs/production-environment-migration/requirements.md)
- [Production Environment Migration Tasks](../.kiro/specs/production-environment-migration/tasks.md)

## Support

For additional support:

- Review the comprehensive design document
- Check the requirements document for acceptance criteria
- Consult your DevOps team
- Review service-specific documentation (PostgreSQL, Neo4j, Redis)
