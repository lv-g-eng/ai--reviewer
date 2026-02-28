# Database Module

This Terraform module provisions the database infrastructure for the AI-Based Code Reviewer platform, including:

- **RDS PostgreSQL** (db.t3.large, Multi-AZ) - Primary relational database
- **ElastiCache Redis** (cache.t3.small, Multi-AZ) - Caching and task queue
- **Neo4j AuraDB Enterprise** (4GB RAM) - Graph database for dependency analysis

## Requirements

This module implements the following requirements:
- **Requirement 4.2**: RDS PostgreSQL db.t3.large in Multi-AZ deployment
- **Requirement 4.3**: ElastiCache Redis cache.t3.small in Multi-AZ deployment
- **Requirement 4.4**: Neo4j AuraDB Enterprise with 4GB RAM
- **Requirement 4.9**: Automated backups with 7-day retention
- **Requirement 11.2**: Data backup procedures running daily at 2 AM UTC

## Backup Configuration

✓ **Automated backups configured for all databases with 7-day retention**

All databases have automated backups running daily at 2 AM UTC:
- **PostgreSQL RDS**: Automated backups (02:00-03:00 UTC), 7-day retention, point-in-time recovery
- **ElastiCache Redis**: Automated snapshots (02:00-04:00 UTC), 7-day retention
- **Neo4j AuraDB**: Continuous backups managed by Neo4j Aura

See [BACKUP_CONFIGURATION.md](./BACKUP_CONFIGURATION.md) for detailed backup documentation and [BACKUP_QUICK_REFERENCE.md](./BACKUP_QUICK_REFERENCE.md) for quick commands.

## Features

### RDS PostgreSQL
- Multi-AZ deployment for high availability
- Automated backups with configurable retention (default: 7 days)
- Encryption at rest using AWS KMS
- Enhanced monitoring and Performance Insights
- Automated minor version upgrades
- CloudWatch alarms for CPU, memory, and storage

### ElastiCache Redis
- Multi-AZ replication group with automatic failover
- Encryption at rest and in transit
- Auth token support for secure access
- Automated snapshots with configurable retention
- Optimized parameter group for caching workload
- CloudWatch alarms for CPU and memory

### Neo4j AuraDB
- Managed Neo4j Enterprise instance (provisioned externally)
- Connection details stored securely in AWS Secrets Manager
- 4GB RAM configuration for graph operations

### Security
- All databases deployed in private subnets
- Encryption at rest and in transit
- Credentials stored in AWS Secrets Manager
- Security groups restrict access to application tier only
- Deletion protection enabled for production environments

## Usage

```hcl
module "database" {
  source = "./modules/database"

  project_name       = "ai-code-reviewer"
  environment        = "prod"
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Security Groups
  db_security_group_id    = aws_security_group.database.id
  redis_security_group_id = aws_security_group.redis.id

  # RDS PostgreSQL Configuration
  db_instance_class        = "db.t3.large"
  db_name                  = "ai_code_reviewer"
  db_username              = var.db_username
  db_password              = var.db_password
  db_multi_az              = true
  db_backup_retention_days = 7

  # ElastiCache Redis Configuration
  redis_node_type       = "cache.t3.small"
  redis_num_cache_nodes = 2
  redis_multi_az        = true
  redis_auth_token      = var.redis_auth_token

  # Neo4j Configuration
  neo4j_connection_uri = var.neo4j_connection_uri
  neo4j_username       = var.neo4j_username
  neo4j_password       = var.neo4j_password

  # Monitoring
  alarm_actions  = [aws_sns_topic.alerts.arn]
  sns_topic_arn  = aws_sns_topic.alerts.arn

  tags = {
    Terraform = "true"
    Owner     = "DevOps"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Name of the project | string | - | yes |
| environment | Environment name (dev, staging, prod) | string | - | yes |
| vpc_id | VPC ID | string | - | yes |
| private_subnet_ids | List of private subnet IDs | list(string) | - | yes |
| db_security_group_id | Security group ID for RDS | string | - | yes |
| redis_security_group_id | Security group ID for Redis | string | - | yes |
| db_instance_class | RDS instance class | string | "db.t3.large" | no |
| db_name | PostgreSQL database name | string | "ai_code_reviewer" | no |
| db_username | PostgreSQL master username | string | - | yes |
| db_password | PostgreSQL master password | string | - | yes |
| db_multi_az | Enable Multi-AZ for RDS | bool | true | no |
| db_backup_retention_days | Backup retention in days | number | 7 | no |
| redis_node_type | Redis node type | string | "cache.t3.small" | no |
| redis_num_cache_nodes | Number of Redis nodes | number | 2 | no |
| redis_multi_az | Enable Multi-AZ for Redis | bool | true | no |
| redis_auth_token | Redis auth token | string | "" | no |
| neo4j_connection_uri | Neo4j AuraDB connection URI | string | - | yes |
| neo4j_username | Neo4j username | string | "neo4j" | no |
| neo4j_password | Neo4j password | string | - | yes |

## Outputs

| Name | Description |
|------|-------------|
| postgres_endpoint | RDS PostgreSQL connection endpoint |
| postgres_address | RDS PostgreSQL hostname |
| postgres_port | RDS PostgreSQL port |
| postgres_database_name | RDS PostgreSQL database name |
| redis_endpoint | ElastiCache Redis primary endpoint |
| redis_configuration_endpoint | ElastiCache Redis configuration endpoint |
| redis_port | ElastiCache Redis port |
| neo4j_connection_uri | Neo4j AuraDB connection URI |
| database_credentials_secret_arn | ARN of Secrets Manager secret with all credentials |
| postgres_connection_string | PostgreSQL connection string |
| redis_connection_string | Redis connection string |

## Connection Strings

All database connection details are stored in AWS Secrets Manager for secure access by the application:

```json
{
  "postgres_host": "xxx.rds.amazonaws.com",
  "postgres_port": 5432,
  "postgres_database": "ai_code_reviewer",
  "postgres_username": "dbadmin",
  "postgres_password": "***",
  "redis_endpoint": "xxx.cache.amazonaws.com",
  "redis_port": 6379,
  "redis_auth_token": "***",
  "neo4j_uri": "neo4j+s://xxx.databases.neo4j.io",
  "neo4j_username": "neo4j",
  "neo4j_password": "***"
}
```

## Neo4j AuraDB Setup

Neo4j AuraDB Enterprise must be provisioned separately through the Neo4j Aura console:

1. Go to https://console.neo4j.io/
2. Create a new AuraDB Enterprise instance
3. Select 4GB RAM configuration
4. Note the connection URI, username, and password
5. Provide these values to the Terraform module via variables

## CloudWatch Alarms

The module creates the following CloudWatch alarms:

### RDS PostgreSQL
- **CPU High**: Triggers when CPU > 80% for 10 minutes
- **Memory Low**: Triggers when freeable memory < 1GB for 10 minutes
- **Storage Low**: Triggers when free storage < 10GB

### ElastiCache Redis
- **CPU High**: Triggers when CPU > 75% for 10 minutes
- **Memory High**: Triggers when memory usage > 90% for 10 minutes

## Backup and Recovery

### RDS PostgreSQL
- Automated daily backups during backup window (02:00-03:00 UTC / 2 AM UTC)
- 7-day retention period (configurable via `db_backup_retention_days`)
- Final snapshot created before deletion (production only)
- Point-in-time recovery enabled within retention period
- Backups are encrypted using AWS KMS
- Maintenance window: Monday 03:30-04:30 UTC

### ElastiCache Redis
- Automated daily snapshots during snapshot window (02:00-04:00 UTC / 2 AM UTC)
- 7-day retention period (configurable via `redis_snapshot_retention_days`)
- Manual snapshots can be created as needed via AWS Console or CLI
- Snapshots are encrypted at rest
- Maintenance window: Monday 04:30-06:30 UTC

### Neo4j AuraDB
- Managed by Neo4j Aura platform with automated backups
- Continuous backups included in Enterprise plan
- Point-in-time recovery available
- Backups are encrypted and stored redundantly
- Backup schedule and retention managed by Neo4j Aura
- Refer to Neo4j Aura documentation for detailed backup procedures: https://neo4j.com/docs/aura/platform/backup-restore/

### Backup Verification
To verify backups are configured correctly:

```bash
# Check RDS automated backups
aws rds describe-db-instances \
  --db-instance-identifier <instance-id> \
  --query 'DBInstances[0].[BackupRetentionPeriod,PreferredBackupWindow]'

# List RDS snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier <instance-id>

# Check Redis snapshot configuration
aws elasticache describe-replication-groups \
  --replication-group-id <replication-group-id> \
  --query 'ReplicationGroups[0].[SnapshotRetentionLimit,SnapshotWindow]'

# List Redis snapshots
aws elasticache describe-snapshots \
  --replication-group-id <replication-group-id>
```

### Restore Procedures

**RDS PostgreSQL Restore:**
```bash
# Restore from automated backup (point-in-time)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier <source-instance> \
  --target-db-instance-identifier <new-instance> \
  --restore-time "2024-01-15T02:30:00Z"

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier <new-instance> \
  --db-snapshot-identifier <snapshot-id>
```

**ElastiCache Redis Restore:**
```bash
# Restore from snapshot
aws elasticache create-replication-group \
  --replication-group-id <new-group-id> \
  --replication-group-description "Restored from snapshot" \
  --snapshot-name <snapshot-name> \
  --cache-node-type cache.t3.small
```

**Neo4j AuraDB Restore:**
- Use Neo4j Aura Console to restore from backup
- Select instance → Backups → Choose backup → Restore
- Alternatively, contact Neo4j support for assistance

## Security Considerations

1. **Network Isolation**: All databases are deployed in private subnets with no public access
2. **Encryption**: Data encrypted at rest (KMS) and in transit (TLS)
3. **Access Control**: Security groups restrict access to application tier only
4. **Credentials**: All passwords stored in AWS Secrets Manager, never in code
5. **Monitoring**: CloudWatch alarms notify on anomalous behavior
6. **Deletion Protection**: Enabled for production environments to prevent accidental deletion

## Cost Optimization

- Use `db.t3.large` and `cache.t3.small` for production (as per requirements)
- Consider smaller instance types for dev/staging environments
- Enable storage autoscaling to avoid over-provisioning
- Use reserved instances for production to reduce costs by up to 60%
- Monitor CloudWatch metrics to right-size instances

## Maintenance

- **RDS PostgreSQL**: 
  - Backup window: Daily 02:00-03:00 UTC (2 AM UTC)
  - Maintenance window: Monday 03:30-04:30 UTC
  - Auto minor version upgrades enabled
- **ElastiCache Redis**: 
  - Snapshot window: Daily 02:00-04:00 UTC (2 AM UTC)
  - Maintenance window: Monday 04:30-06:30 UTC
  - Auto minor version upgrades enabled
- **Neo4j AuraDB**: 
  - Managed by Neo4j Aura
  - Maintenance windows configured in Neo4j Aura console
  - Automatic updates applied during maintenance windows

## Troubleshooting

### RDS Connection Issues
```bash
# Test connectivity from application server
psql -h <postgres_address> -U <username> -d <database_name>

# Check security group rules
aws ec2 describe-security-groups --group-ids <sg-id>
```

### Redis Connection Issues
```bash
# Test connectivity (requires redis-cli)
redis-cli -h <redis_endpoint> -p 6379 --tls -a <auth_token>

# Check replication status
aws elasticache describe-replication-groups --replication-group-id <id>
```

### Neo4j Connection Issues
```bash
# Test connectivity using cypher-shell
cypher-shell -a <neo4j_uri> -u <username> -p <password>

# Verify connection from application
# Check Neo4j Aura console for instance status
```

## References

- [BACKUP_CONFIGURATION.md](./BACKUP_CONFIGURATION.md) - Comprehensive backup configuration guide
- [BACKUP_QUICK_REFERENCE.md](./BACKUP_QUICK_REFERENCE.md) - Quick reference for backup operations
- [AWS RDS PostgreSQL Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [AWS ElastiCache Redis Documentation](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
