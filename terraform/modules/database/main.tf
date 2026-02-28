# Database Module - RDS PostgreSQL, ElastiCache Redis, Neo4j AuraDB
# AI-Based Code Reviewer Infrastructure
# Implements Requirements 4.2, 4.3, 4.4

terraform {
  required_version = ">= 1.0"
}

# DB Subnet Group for RDS (spans multiple AZs)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-db-subnet-group"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# RDS PostgreSQL Instance (Multi-AZ for high availability)
# Requirement 4.2: db.t3.large, Multi-AZ deployment
resource "aws_db_instance" "postgresql" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = var.postgres_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = var.kms_key_id

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # High Availability Configuration
  multi_az               = var.db_multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  publicly_accessible    = false

  # Backup Configuration (Requirement 4.9: 7-day retention, Requirement 11.2: Daily at 2 AM UTC)
  backup_retention_period   = var.db_backup_retention_days
  backup_window             = "02:00-03:00"
  maintenance_window        = "mon:03:30-mon:04:30"
  copy_tags_to_snapshot     = true
  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-postgres-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Performance and Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = var.enable_enhanced_monitoring ? 60 : 0
  monitoring_role_arn             = var.enable_enhanced_monitoring ? aws_iam_role.rds_monitoring[0].arn : null
  performance_insights_enabled    = var.enable_performance_insights
  performance_insights_retention_period = var.enable_performance_insights ? 7 : null

  # Security
  deletion_protection = var.environment == "prod" ? true : false
  auto_minor_version_upgrade = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-postgres"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Database    = "PostgreSQL"
    }
  )

  lifecycle {
    ignore_changes = [
      password,
      final_snapshot_identifier
    ]
  }
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  count = var.enable_enhanced_monitoring ? 1 : 0
  name  = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-rds-monitoring-role"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# Attach AWS managed policy for RDS Enhanced Monitoring
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.enable_enhanced_monitoring ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ElastiCache Subnet Group for Redis (spans multiple AZs)
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-redis-subnet-group"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# ElastiCache Redis Replication Group (Multi-AZ for high availability)
# Requirement 4.3: cache.t3.small, Multi-AZ deployment
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  replication_group_description = "Redis cache for ${var.project_name} ${var.environment}"
  engine                     = "redis"
  engine_version             = var.redis_engine_version
  node_type                  = var.redis_node_type
  port                       = 6379

  # High Availability Configuration
  num_cache_clusters         = var.redis_num_cache_nodes
  automatic_failover_enabled = var.redis_multi_az && var.redis_num_cache_nodes >= 2
  multi_az_enabled           = var.redis_multi_az

  # Network Configuration
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [var.redis_security_group_id]

  # Backup Configuration (Requirement 4.9: 7-day retention, Requirement 11.2: Daily at 2 AM UTC)
  snapshot_retention_limit = var.redis_snapshot_retention_days
  snapshot_window          = "02:00-04:00"
  maintenance_window       = "mon:04:30-mon:06:30"

  # Security
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled         = var.redis_auth_token != "" ? true : false
  auth_token                 = var.redis_auth_token != "" ? var.redis_auth_token : null
  kms_key_id                 = var.kms_key_id

  # Monitoring
  notification_topic_arn = var.sns_topic_arn

  # Parameter Group
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-redis"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Database    = "Redis"
    }
  )

  lifecycle {
    ignore_changes = [auth_token]
  }
}

# ElastiCache Parameter Group for Redis
resource "aws_elasticache_parameter_group" "redis" {
  name   = "${var.project_name}-${var.environment}-redis-params"
  family = var.redis_parameter_group_family

  # Optimize for caching workload
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-redis-params"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# CloudWatch Alarms for RDS PostgreSQL
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-postgres-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgresql.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-postgres-cpu-alarm"
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "database_memory" {
  alarm_name          = "${var.project_name}-${var.environment}-postgres-memory-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "1000000000" # 1GB in bytes
  alarm_description   = "This metric monitors RDS freeable memory"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgresql.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-postgres-memory-alarm"
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "database_storage" {
  alarm_name          = "${var.project_name}-${var.environment}-postgres-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10000000000" # 10GB in bytes
  alarm_description   = "This metric monitors RDS free storage space"
  alarm_actions       = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgresql.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-postgres-storage-alarm"
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

# CloudWatch Alarms for ElastiCache Redis
resource "aws_cloudwatch_metric_alarm" "redis_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-redis-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "This metric monitors Redis CPU utilization"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-redis-cpu-alarm"
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "${var.project_name}-${var.environment}-redis-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "This metric monitors Redis memory usage"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-redis-memory-alarm"
      Environment = var.environment
      Project     = var.project_name
    }
  )
}

# Note: Neo4j AuraDB Enterprise is a managed service provisioned outside of Terraform
# Connection details should be stored in AWS Secrets Manager
# Requirement 4.4: Neo4j AuraDB Enterprise with 4GB RAM
# The connection URI, username, and password are passed as variables and stored in Secrets Manager

# AWS Secrets Manager Secret for Database Credentials
resource "aws_secretsmanager_secret" "database_credentials" {
  name        = "${var.project_name}/${var.environment}/database-credentials"
  description = "Database credentials for ${var.project_name} ${var.environment}"

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-db-credentials"
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  )
}

# Store all database connection strings in Secrets Manager
resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    postgres_host     = aws_db_instance.postgresql.address
    postgres_port     = aws_db_instance.postgresql.port
    postgres_database = aws_db_instance.postgresql.db_name
    postgres_username = var.db_username
    postgres_password = var.db_password
    redis_endpoint    = aws_elasticache_replication_group.redis.configuration_endpoint_address
    redis_port        = aws_elasticache_replication_group.redis.port
    redis_auth_token  = var.redis_auth_token
    neo4j_uri         = var.neo4j_connection_uri
    neo4j_username    = var.neo4j_username
    neo4j_password    = var.neo4j_password
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
