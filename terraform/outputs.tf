# Terraform Outputs
# AI-Based Code Reviewer Infrastructure

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr
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

output "availability_zones" {
  description = "Availability zones used for deployment"
  value       = module.vpc.availability_zones
}

# Network Information
output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = module.vpc.internet_gateway_id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = module.vpc.nat_gateway_ids
}

# Deployment Information
output "region" {
  description = "AWS region where infrastructure is deployed"
  value       = var.aws_region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

# Database Outputs
output "postgres_endpoint" {
  description = "RDS PostgreSQL connection endpoint"
  value       = module.database.postgres_endpoint
}

output "postgres_database_name" {
  description = "RDS PostgreSQL database name"
  value       = module.database.postgres_database_name
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = module.database.redis_endpoint
}

output "redis_configuration_endpoint" {
  description = "ElastiCache Redis configuration endpoint"
  value       = module.database.redis_configuration_endpoint
}

output "database_credentials_secret_arn" {
  description = "ARN of the Secrets Manager secret containing all database credentials"
  value       = module.database.database_credentials_secret_arn
}

output "database_credentials_secret_name" {
  description = "Name of the Secrets Manager secret containing all database credentials"
  value       = module.database.database_credentials_secret_name
}

# Compute Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.compute.alb_zone_id
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = module.compute.autoscaling_group_name
}

# WAF Outputs
output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = var.enable_waf ? module.waf[0].web_acl_id : null
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = var.enable_waf ? module.waf[0].web_acl_arn : null
}

output "waf_web_acl_name" {
  description = "Name of the WAF Web ACL"
  value       = var.enable_waf ? module.waf[0].web_acl_name : null
}

output "waf_log_group_name" {
  description = "Name of the CloudWatch Log Group for WAF logs"
  value       = var.enable_waf ? module.waf[0].log_group_name : null
}
