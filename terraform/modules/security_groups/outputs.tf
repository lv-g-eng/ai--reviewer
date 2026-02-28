# Security Groups Module Outputs
# AI-Based Code Reviewer Infrastructure

output "alb_security_group_id" {
  description = "ID of the Application Load Balancer security group"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the application server security group"
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "ID of the RDS PostgreSQL security group"
  value       = aws_security_group.database.id
}

output "redis_security_group_id" {
  description = "ID of the ElastiCache Redis security group"
  value       = aws_security_group.redis.id
}
