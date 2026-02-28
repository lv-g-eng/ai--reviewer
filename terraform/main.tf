# Main Terraform Configuration
# AI-Based Code Reviewer Infrastructure

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure for production use
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "ai-code-reviewer/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Repository  = "ai-code-reviewer"
    }
  }
}

# Data source for available availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module - Networking Infrastructure
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  enable_flow_logs   = var.enable_vpc_flow_logs

  tags = var.tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  allowed_cidr_blocks  = var.allowed_cidr_blocks

  tags = var.tags
}

# Compute Module - EC2 Auto Scaling and Load Balancer
module "compute" {
  source = "./modules/compute"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  aws_region         = var.aws_region

  # Instance Configuration
  instance_type    = var.instance_type
  min_instances    = var.min_instances
  max_instances    = var.max_instances
  desired_instances = var.desired_instances

  # Security Groups
  alb_security_group_id = module.security_groups.alb_security_group_id
  app_security_group_id = module.security_groups.app_security_group_id

  # SSL Configuration
  ssl_certificate_arn = var.ssl_certificate_arn

  # Monitoring
  enable_detailed_monitoring = var.enable_detailed_monitoring
  enable_alb_logs           = false
  alb_logs_bucket           = ""

  tags = var.tags
}

# Database Module - RDS PostgreSQL, ElastiCache Redis, Neo4j
module "database" {
  source = "./modules/database"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Security Groups
  db_security_group_id    = module.security_groups.database_security_group_id
  redis_security_group_id = module.security_groups.redis_security_group_id

  # RDS PostgreSQL Configuration
  db_instance_class        = var.db_instance_class
  db_name                  = var.db_name
  db_username              = var.db_username
  db_password              = var.db_password
  db_multi_az              = var.db_multi_az
  db_backup_retention_days = var.db_backup_retention_days

  # ElastiCache Redis Configuration
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_multi_az        = var.redis_multi_az
  redis_auth_token      = var.redis_auth_token

  # Neo4j Configuration
  neo4j_connection_uri = var.neo4j_connection_uri
  neo4j_username       = var.neo4j_username
  neo4j_password       = var.neo4j_password

  tags = var.tags
}

# WAF Module - Web Application Firewall with OWASP Protection
module "waf" {
  count  = var.enable_waf ? 1 : 0
  source = "./modules/waf"

  project_name = var.project_name
  environment  = var.environment
  alb_arn      = module.compute.alb_arn

  # Rate limiting configuration
  rate_limit = var.waf_rate_limit

  # Optional geo-blocking
  blocked_countries = var.waf_blocked_countries

  # Logging configuration
  log_retention_days = var.log_retention_days

  tags = var.tags
}

# Outputs from main configuration
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_ips" {
  description = "Public IP addresses of NAT Gateways"
  value       = module.vpc.nat_gateway_public_ips
}
