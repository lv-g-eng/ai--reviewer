# AWS Secrets Manager Integration

This module provides secure configuration management using AWS Secrets Manager for storing sensitive credentials like API keys, database passwords, and encryption keys.

## Features

- **Secure Storage**: Store sensitive configuration in AWS Secrets Manager instead of environment variables
- **Automatic Caching**: Reduce API calls with configurable TTL-based caching
- **Fallback Support**: Automatically fall back to environment variables if Secrets Manager is unavailable
- **Secret Rotation**: Support for automatic secret rotation with Lambda functions
- **JSON Secrets**: Store multiple related secrets in a single JSON object

## Architecture

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ SecretsManager  │─────▶│  AWS Secrets     │
│    Client       │      │    Manager       │
└────────┬────────┘      └──────────────────┘
         │
         │ (fallback)
         ▼
┌─────────────────┐
│  Environment    │
│   Variables     │
└─────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
pip install boto3
```

### 2. Configure AWS Credentials

Ensure your application has AWS credentials configured:

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Option 2: IAM role (recommended for EC2/ECS)
# Attach IAM role with SecretsManagerReadWrite policy
```

### 3. Enable Secrets Manager

Set environment variable to enable Secrets Manager:

```bash
export AWS_SECRETS_MANAGER_ENABLED=true
export AWS_REGION=us-east-1
```

### 4. Create Secrets

Use the setup script to create secrets:

```bash
# Dry run to see what would be created
python backend/scripts/setup_secrets_manager.py \
    --environment production \
    --dry-run

# Actually create secrets
python backend/scripts/setup_secrets_manager.py \
    --environment production
```

## Usage

### Basic Usage

```python
from app.core.secrets_manager import get_secrets_manager

# Get secrets manager instance
secrets = get_secrets_manager()

# Retrieve a simple secret
api_key = secrets.get_secret("production/integrations/openai_api_key")

# Retrieve with default value
github_token = secrets.get_secret(
    "production/integrations/github_token",
    default="fallback_token"
)
```

### JSON Secrets

Store multiple related secrets in a single JSON object:

```python
# Get entire JSON secret as dictionary
db_config = secrets.get_secret_dict("production/database/postgresql")
host = db_config.get("postgres_host")
password = db_config.get("postgres_password")

# Or get specific key from JSON secret
password = secrets.get_secret(
    "production/database/postgresql",
    key="postgres_password"
)
```

### Load Secrets at Startup

Load secrets into environment variables at application startup:

```python
from app.core.secrets_manager import load_secrets_into_env

# Define secret mappings
secret_mappings = {
    "production/database/postgresql": "POSTGRES_PASSWORD",
    "production/integrations/openai_api_key": "OPENAI_API_KEY",
    "production/integrations/github_token": "GITHUB_TOKEN",
    "production/app/secrets": "JWT_SECRET"
}

# Load secrets into environment
load_secrets_into_env(secret_mappings)

# Now access via environment variables
import os
postgres_password = os.environ.get("POSTGRES_PASSWORD")
```

### Cache Management

```python
# Invalidate specific secret cache
secrets.invalidate_cache("production/database/postgresql")

# Invalidate all cached secrets
secrets.invalidate_cache()

# Disable caching for specific call
secret = secrets.get_secret("production/api/key", use_cache=False)
```

## Secret Naming Convention

Use a hierarchical naming structure:

```
{environment}/{category}/{secret_name}

Examples:
- production/database/postgresql
- production/database/neo4j
- production/database/redis
- production/integrations/github
- production/integrations/openai_api_key
- production/app/secrets
- staging/database/postgresql
- development/api/test_key
```

## Secret Rotation

### Manual Rotation

```python
# Trigger manual rotation
success = secrets.rotate_secret("production/database/postgresql")
if success:
    print("Rotation initiated successfully")
```

### Automatic Rotation

Set up automatic rotation with AWS Lambda:

1. Create a Lambda function for rotation
2. Enable rotation via script:

```bash
python backend/scripts/setup_secrets_manager.py \
    --environment production \
    --enable-rotation \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789:function:rotate-secret
```

## Security Best Practices

### 1. IAM Permissions

Grant minimal required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:production/*"
    }
  ]
}
```

### 2. Encryption

All secrets are encrypted at rest using AWS KMS. Optionally specify a custom KMS key:

```python
# When creating secrets via AWS CLI
aws secretsmanager create-secret \
    --name production/database/postgresql \
    --secret-string '{"password":"secure_password"}' \
    --kms-key-id arn:aws:kms:us-east-1:123456789:key/your-key-id
```

### 3. Access Logging

Enable CloudTrail logging for Secrets Manager API calls:

```bash
aws cloudtrail create-trail \
    --name secrets-manager-trail \
    --s3-bucket-name my-cloudtrail-bucket
```

### 4. Secret Versioning

Secrets Manager automatically versions secrets. Access previous versions:

```python
# Get specific version
response = client.get_secret_value(
    SecretId="production/database/postgresql",
    VersionId="version-id-here"
)
```

## Environment-Specific Configuration

### Development

```bash
# Disable Secrets Manager for local development
export AWS_SECRETS_MANAGER_ENABLED=false

# Use local environment variables
export POSTGRES_PASSWORD=local_password
export OPENAI_API_KEY=local_api_key
```

### Staging/Production

```bash
# Enable Secrets Manager
export AWS_SECRETS_MANAGER_ENABLED=true
export AWS_REGION=us-east-1

# Secrets will be loaded from AWS Secrets Manager
```

## Troubleshooting

### Secret Not Found

```
WARNING: Secret not found in Secrets Manager: production/api/key
```

**Solution**: Verify secret exists and IAM permissions are correct:

```bash
aws secretsmanager list-secrets --region us-east-1
aws secretsmanager get-secret-value --secret-id production/api/key
```

### Access Denied

```
ERROR: Error retrieving secret: AccessDeniedException
```

**Solution**: Check IAM role/user has `secretsmanager:GetSecretValue` permission.

### Decryption Failure

```
ERROR: Failed to decrypt secret: DecryptionFailure
```

**Solution**: Ensure IAM role has `kms:Decrypt` permission for the KMS key.

## Cost Optimization

### Caching

Default cache TTL is 5 minutes. Adjust based on your needs:

```python
secrets = SecretsManagerClient(
    cache_ttl_seconds=600  # 10 minutes
)
```

### API Call Costs

- $0.05 per 10,000 API calls
- Caching reduces costs significantly
- Consider loading secrets at startup for frequently accessed values

## Testing

### Unit Tests

```python
import pytest
from app.core.secrets_manager import SecretsManagerClient

def test_get_secret_with_fallback():
    # Disable Secrets Manager for testing
    secrets = SecretsManagerClient(enabled=False)
    
    # Should fall back to environment variable
    import os
    os.environ['TEST_SECRET'] = 'test_value'
    
    value = secrets.get_secret('test/secret')
    assert value == 'test_value'
```

### Integration Tests

```python
def test_secrets_manager_integration():
    secrets = SecretsManagerClient(enabled=True)
    
    # Test retrieving actual secret
    value = secrets.get_secret('test/integration/secret')
    assert value is not None
```

## Migration Guide

### From Environment Variables to Secrets Manager

1. **Identify sensitive variables**:
   - Database passwords
   - API keys
   - Encryption keys
   - OAuth secrets

2. **Create secrets in Secrets Manager**:
   ```bash
   python backend/scripts/setup_secrets_manager.py --environment production
   ```

3. **Update application code**:
   ```python
   # Before
   import os
   api_key = os.environ.get('OPENAI_API_KEY')
   
   # After
   from app.core.secrets_manager import get_secrets_manager
   secrets = get_secrets_manager()
   api_key = secrets.get_secret('production/integrations/openai_api_key')
   ```

4. **Remove from environment files**:
   - Remove sensitive values from `.env` files
   - Keep placeholders with `${AWS_SECRET:...}` syntax

5. **Test thoroughly**:
   - Verify all secrets load correctly
   - Test fallback to environment variables
   - Validate rotation works

## Related Documentation

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Configuration Management](./config.py)
- [Security Best Practices](../security/README.md)

## Validates Requirements

- **Requirement 14.4**: Store sensitive configuration in AWS Secrets Manager
- **Requirement 14.1**: Externalize all configuration
- **Requirement 14.3**: Implement configuration validation on startup
