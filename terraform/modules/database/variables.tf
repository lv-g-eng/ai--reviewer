# Database Module Variables
# AI-Based Code Reviewer Infrastructure

variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for database deployment"
  type        = list(string)
}

variable "db_security_group_id" {
  description = "Security group ID for RDS PostgreSQL"
  type        = string
}

variable "redis_security_group_id" {
  description = "Security group ID for ElastiCache Redis"
  type        = string
}

# RDS PostgreSQL Configuration
variable "db_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t3.large"
}

variable "postgres_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "ai_code_reviewer"
}

variable "db_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Master password for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling in GB"
  type        = number
  default     = 500
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "enable_enhanced_monitoring" {
  description = "Enable RDS Enhanced Monitoring"
  type        = bool
  default     = true
}

variable "enable_performance_insights" {
  description = "Enable RDS Performance Insights"
  type        = bool
  default     = true
}

# ElastiCache Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.small"
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in Redis cluster"
  type        = number
  default     = 2
}

variable "redis_multi_az" {
  description = "Enable Multi-AZ deployment for Redis"
  type        = bool
  default     = true
}

variable "redis_parameter_group_family" {
  description = "Redis parameter group family"
  type        = string
  default     = "redis7"
}

variable "redis_snapshot_retention_days" {
  description = "Number of days to retain Redis snapshots"
  type        = number
  default     = 7
}

variable "redis_auth_token" {
  description = "Auth token for Redis (must be 16-128 characters)"
  type        = string
  sensitive   = true
  default     = ""
}

# Neo4j Configuration
variable "neo4j_connection_uri" {
  description = "Neo4j AuraDB connection URI (e.g., neo4j+s://xxxxx.databases.neo4j.io)"
  type        = string
  sensitive   = true
}

variable "neo4j_username" {
  description = "Neo4j database username"
  type        = string
  default     = "neo4j"
  sensitive   = true
}

variable "neo4j_password" {
  description = "Neo4j database password"
  type        = string
  sensitive   = true
}

# Security Configuration
variable "kms_key_id" {
  description = "KMS key ID for encryption at rest"
  type        = string
  default     = ""
}

# Monitoring Configuration
variable "alarm_actions" {
  description = "List of ARNs to notify when alarms trigger"
  type        = list(string)
  default     = []
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for ElastiCache notifications"
  type        = string
  default     = ""
}

# Tags
variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
