# Terraform Variables
# AI-Based Code Reviewer Infrastructure

# General Configuration
variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
  default     = "ai-code-reviewer"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones for high availability (minimum 2 required)"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least 2 availability zones are required for high availability."
  }
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

# Compute Configuration
variable "instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.large"
}

variable "min_instances" {
  description = "Minimum number of instances in Auto Scaling Group"
  type        = number
  default     = 2
  validation {
    condition     = var.min_instances >= 2
    error_message = "Minimum instances must be at least 2 for high availability."
  }
}

variable "max_instances" {
  description = "Maximum number of instances in Auto Scaling Group"
  type        = number
  default     = 10
  validation {
    condition     = var.max_instances >= var.min_instances
    error_message = "Maximum instances must be greater than or equal to minimum instances."
  }
}

variable "desired_instances" {
  description = "Desired number of instances in Auto Scaling Group"
  type        = number
  default     = 2
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t3.large"
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "ai_code_reviewer"
}

variable "db_username" {
  description = "Master username for PostgreSQL database"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_password" {
  description = "Master password for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
  validation {
    condition     = var.db_backup_retention_days >= 7
    error_message = "Backup retention must be at least 7 days per requirements."
  }
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

# ElastiCache Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.small"
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

# Neo4j Configuration
variable "neo4j_connection_uri" {
  description = "Neo4j AuraDB connection URI (e.g., neo4j+s://xxxxx.databases.neo4j.io)"
  type        = string
  sensitive   = true
  default     = ""
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
  default     = ""
}

# Redis Auth Token
variable "redis_auth_token" {
  description = "Auth token for Redis (must be 16-128 characters, leave empty to disable)"
  type        = string
  sensitive   = true
  default     = ""
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for ALB HTTPS listener"
  type        = string
  default     = ""
}

# WAF Configuration
variable "enable_waf" {
  description = "Enable AWS WAF for OWASP protection"
  type        = bool
  default     = true
}

variable "waf_rate_limit" {
  description = "Rate limit for WAF (requests per 5 minutes)"
  type        = number
  default     = 2000
}

variable "waf_blocked_countries" {
  description = "List of country codes to block via WAF (ISO 3166-1 alpha-2). Leave empty to allow all countries."
  type        = list(string)
  default     = []
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# Tags
variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
