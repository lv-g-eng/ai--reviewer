# Variables for CloudWatch Dashboards Module

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "service_name" {
  description = "Service name for dashboard naming and metrics namespace"
  type        = string
  default     = "ai-reviewer"
}

variable "aws_region" {
  description = "AWS region for CloudWatch dashboards"
  type        = string
}

variable "enable_system_health_dashboard" {
  description = "Enable System Health dashboard"
  type        = bool
  default     = true
}

variable "enable_performance_dashboard" {
  description = "Enable Performance Metrics dashboard"
  type        = bool
  default     = true
}

variable "enable_business_metrics_dashboard" {
  description = "Enable Business Metrics dashboard"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Alert Configuration Variables

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = ""
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alert notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group for CPU alarms"
  type        = string
  default     = ""
}

variable "enable_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "error_rate_threshold" {
  description = "Error rate threshold percentage for alerts"
  type        = number
  default     = 5
}

variable "response_time_threshold" {
  description = "Response time threshold in seconds for alerts"
  type        = number
  default     = 1.0
}

variable "cpu_threshold" {
  description = "CPU utilization threshold percentage for alerts"
  type        = number
  default     = 80
}

variable "memory_threshold" {
  description = "Memory utilization threshold percentage for alerts"
  type        = number
  default     = 85
}

variable "disk_threshold" {
  description = "Disk utilization threshold percentage for alerts"
  type        = number
  default     = 90
}
