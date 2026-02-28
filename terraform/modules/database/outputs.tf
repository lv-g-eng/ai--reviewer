# Database Module Outputs
# AI-Based Code Reviewer Infrastructure

# RDS PostgreSQL Outputs
output "postgres_endpoint" {
  description = "RDS PostgreSQL connection endpoint"
  value       = aws_db_instance.postgresql.endpoint
}

output "postgres_address" {
  description = "RDS PostgreSQL hostname"
  value       = aws_db_instance.postgresql.address
}

output "postgres_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.postgresql.port
}

output "postgres_database_name" {
  description = "RDS PostgreSQL database name"
  value       = aws_db_instance.postgresql.db_name
}

output "postgres_instance_id" {
  description = "RDS PostgreSQL instance identifier"
  value       = aws_db_instance.postgresql.id
}

output "postgres_arn" {
  description = "RDS PostgreSQL instance ARN"
  value       = aws_db_instance.postgresql.arn
}

output "postgres_resource_id" {
  description = "RDS PostgreSQL resource ID"
  value       = aws_db_instance.postgresql.resource_id
}

# ElastiCache Redis Outputs
output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_configuration_endpoint" {
  description = "ElastiCache Redis configuration endpoint (for cluster mode)"
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
}

output "redis_reader_endpoint" {
  description = "ElastiCache Redis reader endpoint"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_replication_group_id" {
  description = "ElastiCache Redis replication group ID"
  value       = aws_elasticache_replication_group.redis.id
}

output "redis_arn" {
  description = "ElastiCache Redis replication group ARN"
  value       = aws_elasticache_replication_group.redis.arn
}

output "redis_member_clusters" {
  description = "List of ElastiCache Redis member cluster IDs"
  value       = aws_elasticache_replication_group.redis.member_clusters
}

# Neo4j Outputs (connection details passed through)
output "neo4j_connection_uri" {
  description = "Neo4j AuraDB connection URI"
  value       = var.neo4j_connection_uri
  sensitive   = true
}

output "neo4j_username" {
  description = "Neo4j database username"
  value       = var.neo4j_username
  sensitive   = true
}

# Secrets Manager Outputs
output "database_credentials_secret_arn" {
  description = "ARN of the Secrets Manager secret containing all database credentials"
  value       = aws_secretsmanager_secret.database_credentials.arn
}

output "database_credentials_secret_name" {
  description = "Name of the Secrets Manager secret containing all database credentials"
  value       = aws_secretsmanager_secret.database_credentials.name
}

# Connection Strings (for application configuration)
output "postgres_connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${var.db_username}@${aws_db_instance.postgresql.address}:${aws_db_instance.postgresql.port}/${aws_db_instance.postgresql.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${aws_elasticache_replication_group.redis.configuration_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
}

# Subnet Group Outputs
output "db_subnet_group_name" {
  description = "Name of the RDS subnet group"
  value       = aws_db_subnet_group.main.name
}

output "elasticache_subnet_group_name" {
  description = "Name of the ElastiCache subnet group"
  value       = aws_elasticache_subnet_group.main.name
}
