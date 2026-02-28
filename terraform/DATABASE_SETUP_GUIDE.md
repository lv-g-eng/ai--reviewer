# Database Setup Guide

This guide provides instructions for setting up the database infrastructure for the AI-Based Code Reviewer platform.

## Overview

The database infrastructure consists of three components:

1. **RDS PostgreSQL** (db.t3.large, Multi-AZ) - Primary relational database
2. **ElastiCache Redis** (cache.t3.small, Multi-AZ) - Caching and task queue
3. **Neo4j AuraDB Enterprise** (4GB RAM) - Graph database for dependency analysis

## Prerequisites

Before deploying the database infrastructure, ensure you have:

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0 installed
- VPC and networking infrastructure deployed (Task 30.1)
- Compute infrastructure deployed (Task 30.2)
- Neo4j AuraDB Enterprise instance provisioned

## Neo4j AuraDB Setup

Neo4j AuraDB must be provisioned separately before running Terraform:

### Step 1: Create Neo4j AuraDB Instance

1. Go to https://console.neo4j.io/
2. Sign in or create an account
3. Click "New Instance"
4. Select "AuraDB Enterprise"
5. Configure the instance:
   - **Name**: `ai-code-reviewer-{environment}`
   - **Region**: Same as your AWS region (e.g., us-east-1)
   - **Memory**: 4GB RAM
   - **Storage**: Default (auto-scaling)
6. Click "Create"
7. **IMPORTANT**: Save the connection details:
   - Connection URI (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username (default: `neo4j`)
   - Password (generated, save securely)

### Step 2: Configure Network Access

1. In the Neo4j Aura console, go to your instance
2. Click "Network Access"
3. Add IP addresses of your application servers
   - For development: You can allow all IPs (0.0.0.0/0)
   - For production: Restrict to your NAT Gateway IPs

### Step 3: Store Credentials in AWS Secrets Manager

```bash
# Create a secret for Neo4j credentials
aws secretsmanager create-secret \
  --name ai-code-reviewer/prod/neo4j-credentials \
  --description "Neo4j AuraDB credentials for production" \
  --secret-string '{
    "uri": "neo4j+s://xxxxx.databases.neo4j.io",
    "username": "neo4j",
    "password": "your-secure-password"
  }'
```

## Database Deployment

### Step 1: Set Required Variables

Create a `terraform.tfvars` file or set environment variables:

```hcl
# Database passwords (use strong passwords!)
db_password = "your-strong-postgres-password"
redis_auth_token = "your-strong-redis-token-16-to-128-chars"

# Neo4j connection details
neo4j_connection_uri = "neo4j+s://xxxxx.databases.neo4j.io"
neo4j_username = "neo4j"
neo4j_password = "your-neo4j-password"
```

**IMPORTANT**: Never commit passwords to version control. Use environment variables or AWS Secrets Manager:

```bash
# Set via environment variables
export TF_VAR_db_password="your-strong-postgres-password"
export TF_VAR_redis_auth_token="your-strong-redis-token"
export TF_VAR_neo4j_connection_uri="neo4j+s://xxxxx.databases.neo4j.io"
export TF_VAR_neo4j_username="neo4j"
export TF_VAR_neo4j_password="your-neo4j-password"
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Plan the Deployment

```bash
terraform plan -out=tfplan
```

Review the plan to ensure:
- RDS PostgreSQL instance is configured correctly (db.t3.large, Multi-AZ)
- ElastiCache Redis is configured correctly (cache.t3.small, Multi-AZ)
- Security groups allow proper access
- Secrets Manager secret is created

### Step 4: Apply the Configuration

```bash
terraform apply tfplan
```

This will create:
- RDS PostgreSQL instance (takes ~10-15 minutes)
- ElastiCache Redis replication group (takes ~5-10 minutes)
- Security groups for database access
- Secrets Manager secret with all connection details
- CloudWatch alarms for monitoring

### Step 5: Verify Deployment

```bash
# Get database endpoints
terraform output postgres_endpoint
terraform output redis_endpoint

# Get Secrets Manager secret ARN
terraform output database_credentials_secret_arn
```

## Database Configuration

### RDS PostgreSQL

**Instance Specifications:**
- Instance Class: db.t3.large (2 vCPUs, 8 GB RAM)
- Storage: 100 GB (auto-scaling up to 500 GB)
- Engine: PostgreSQL 15.4
- Multi-AZ: Enabled (automatic failover)
- Backup Retention: 7 days
- Encryption: Enabled (at rest and in transit)

**Connection Details:**
```
Host: <postgres_endpoint from Terraform output>
Port: 5432
Database: ai_code_reviewer
Username: dbadmin
Password: <stored in Secrets Manager>
```

**Connection String:**
```
postgresql://dbadmin:<password>@<endpoint>:5432/ai_code_reviewer?sslmode=require
```

### ElastiCache Redis

**Instance Specifications:**
- Node Type: cache.t3.small (2 vCPUs, 1.37 GB RAM)
- Number of Nodes: 2 (primary + replica)
- Engine: Redis 7.0
- Multi-AZ: Enabled (automatic failover)
- Encryption: Enabled (at rest and in transit)
- Auth Token: Enabled (if configured)

**Connection Details:**
```
Primary Endpoint: <redis_endpoint from Terraform output>
Configuration Endpoint: <redis_configuration_endpoint from Terraform output>
Port: 6379
Auth Token: <stored in Secrets Manager>
```

**Connection String:**
```
redis://<endpoint>:6379
# With auth token:
redis://:<auth_token>@<endpoint>:6379
```

### Neo4j AuraDB

**Instance Specifications:**
- Memory: 4 GB RAM
- Storage: Auto-scaling
- Edition: Enterprise
- Encryption: Enabled (at rest and in transit)

**Connection Details:**
```
URI: neo4j+s://xxxxx.databases.neo4j.io
Port: 7687 (Bolt protocol)
Username: neo4j
Password: <stored in Secrets Manager>
```

**Connection String:**
```
neo4j+s://neo4j:<password>@xxxxx.databases.neo4j.io
```

## Accessing Database Credentials

All database credentials are stored in AWS Secrets Manager for secure access:

### Using AWS CLI

```bash
# Get all database credentials
aws secretsmanager get-secret-value \
  --secret-id ai-code-reviewer/prod/database-credentials \
  --query SecretString \
  --output text | jq .

# Get specific credential
aws secretsmanager get-secret-value \
  --secret-id ai-code-reviewer/prod/database-credentials \
  --query SecretString \
  --output text | jq -r .postgres_password
```

### Using Python (boto3)

```python
import boto3
import json

def get_database_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId='ai-code-reviewer/prod/database-credentials'
    )
    return json.loads(response['SecretString'])

credentials = get_database_credentials()
postgres_host = credentials['postgres_host']
postgres_password = credentials['postgres_password']
```

### Using Application Configuration

Update your application's environment variables:

```bash
# .env file
DATABASE_URL=postgresql://dbadmin:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/ai_code_reviewer
REDIS_URL=redis://:${REDIS_AUTH_TOKEN}@${REDIS_ENDPOINT}:6379
NEO4J_URI=${NEO4J_URI}
NEO4J_USERNAME=${NEO4J_USERNAME}
NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

## Testing Database Connectivity

### PostgreSQL

```bash
# Install PostgreSQL client
sudo apt-get install postgresql-client  # Ubuntu/Debian
brew install postgresql                  # macOS

# Test connection
psql "postgresql://dbadmin:<password>@<endpoint>:5432/ai_code_reviewer?sslmode=require"

# Run a test query
psql "postgresql://dbadmin:<password>@<endpoint>:5432/ai_code_reviewer?sslmode=require" \
  -c "SELECT version();"
```

### Redis

```bash
# Install Redis CLI
sudo apt-get install redis-tools  # Ubuntu/Debian
brew install redis                # macOS

# Test connection (without auth)
redis-cli -h <endpoint> -p 6379 --tls ping

# Test connection (with auth token)
redis-cli -h <endpoint> -p 6379 --tls -a <auth_token> ping

# Run a test command
redis-cli -h <endpoint> -p 6379 --tls -a <auth_token> SET test "Hello"
redis-cli -h <endpoint> -p 6379 --tls -a <auth_token> GET test
```

### Neo4j

```bash
# Install cypher-shell
# Download from https://neo4j.com/download-center/#cypher-shell

# Test connection
cypher-shell -a <uri> -u <username> -p <password>

# Run a test query
cypher-shell -a <uri> -u <username> -p <password> \
  "RETURN 'Connection successful' AS message;"
```

## Monitoring and Alarms

CloudWatch alarms are automatically created for:

### RDS PostgreSQL Alarms
- **CPU High**: Triggers when CPU > 80% for 10 minutes
- **Memory Low**: Triggers when freeable memory < 1GB for 10 minutes
- **Storage Low**: Triggers when free storage < 10GB

### ElastiCache Redis Alarms
- **CPU High**: Triggers when CPU > 75% for 10 minutes
- **Memory High**: Triggers when memory usage > 90% for 10 minutes

### Viewing Alarms

```bash
# List all alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix ai-code-reviewer-prod

# Get alarm status
aws cloudwatch describe-alarms \
  --alarm-names ai-code-reviewer-prod-postgres-cpu-high
```

## Backup and Recovery

### RDS PostgreSQL

**Automated Backups:**
- Daily backups during maintenance window (03:00-04:00 UTC)
- 7-day retention period
- Point-in-time recovery enabled

**Manual Snapshot:**
```bash
aws rds create-db-snapshot \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --db-snapshot-identifier ai-code-reviewer-prod-manual-$(date +%Y%m%d)
```

**Restore from Snapshot:**
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-code-reviewer-prod-postgres-restored \
  --db-snapshot-identifier <snapshot-id>
```

### ElastiCache Redis

**Automated Snapshots:**
- Daily snapshots during maintenance window (03:00-05:00 UTC)
- 7-day retention period

**Manual Snapshot:**
```bash
aws elasticache create-snapshot \
  --replication-group-id ai-code-reviewer-prod-redis \
  --snapshot-name ai-code-reviewer-prod-manual-$(date +%Y%m%d)
```

**Restore from Snapshot:**
```bash
aws elasticache create-replication-group \
  --replication-group-id ai-code-reviewer-prod-redis-restored \
  --snapshot-name <snapshot-name>
```

### Neo4j AuraDB

Backups are managed by Neo4j Aura:
- Continuous backups
- Point-in-time recovery
- Managed through Neo4j Aura console

## Troubleshooting

### Cannot Connect to RDS PostgreSQL

1. **Check security group rules:**
   ```bash
   aws ec2 describe-security-groups \
     --group-ids <db-security-group-id>
   ```

2. **Verify instance is available:**
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier ai-code-reviewer-prod-postgres
   ```

3. **Check VPC and subnet configuration:**
   - Ensure application servers are in the same VPC
   - Verify route tables allow traffic between subnets

### Cannot Connect to ElastiCache Redis

1. **Check security group rules:**
   ```bash
   aws ec2 describe-security-groups \
     --group-ids <redis-security-group-id>
   ```

2. **Verify replication group status:**
   ```bash
   aws elasticache describe-replication-groups \
     --replication-group-id ai-code-reviewer-prod-redis
   ```

3. **Test from application server:**
   ```bash
   # SSH to application server
   redis-cli -h <endpoint> -p 6379 --tls ping
   ```

### Cannot Connect to Neo4j AuraDB

1. **Check Neo4j Aura console:**
   - Verify instance is running
   - Check network access rules

2. **Verify connection URI:**
   - Ensure using `neo4j+s://` protocol (TLS required)
   - Check port 7687 is accessible

3. **Test from application server:**
   ```bash
   cypher-shell -a <uri> -u <username> -p <password>
   ```

## Cost Optimization

### Development Environment
- Use smaller instance types (db.t3.medium, cache.t3.micro)
- Disable Multi-AZ deployment
- Reduce backup retention to 1-3 days
- Use Neo4j AuraDB Professional (2GB RAM) instead of Enterprise

### Production Environment
- Use reserved instances for 1-3 year commitment (up to 60% savings)
- Enable storage autoscaling to avoid over-provisioning
- Monitor CloudWatch metrics to right-size instances
- Consider Aurora Serverless for variable workloads

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use AWS Secrets Manager for all passwords**
3. **Enable encryption at rest and in transit**
4. **Restrict security group rules to minimum required access**
5. **Enable deletion protection for production databases**
6. **Regularly rotate database passwords**
7. **Enable CloudWatch Logs for audit trail**
8. **Use IAM authentication where possible**
9. **Implement least privilege access**
10. **Regular security audits and compliance checks**

## Next Steps

After deploying the database infrastructure:

1. **Initialize database schemas:**
   - Run Alembic migrations for PostgreSQL
   - Configure Redis for Celery task queue
   - Create Neo4j graph schema and indexes

2. **Configure application:**
   - Update application configuration with database endpoints
   - Test database connectivity from application servers
   - Run integration tests

3. **Set up monitoring:**
   - Configure CloudWatch dashboards
   - Set up SNS notifications for alarms
   - Enable Enhanced Monitoring for RDS

4. **Document procedures:**
   - Backup and recovery procedures
   - Incident response procedures
   - Maintenance procedures

## References

- [AWS RDS PostgreSQL Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [AWS ElastiCache Redis Documentation](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
