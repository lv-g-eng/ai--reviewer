# WAF Module Variables
# AI-Based Code Reviewer Infrastructure

variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "alb_arn" {
  description = "ARN of the Application Load Balancer to associate with WAF"
  type        = string
}

variable "rate_limit" {
  description = "Rate limit for WAF (requests per 5 minutes from a single IP)"
  type        = number
  default     = 2000
  validation {
    condition     = var.rate_limit >= 100 && var.rate_limit <= 20000000
    error_message = "Rate limit must be between 100 and 20,000,000 requests per 5 minutes."
  }
}

variable "blocked_countries" {
  description = "List of country codes to block (ISO 3166-1 alpha-2). Leave empty to allow all countries."
  type        = list(string)
  default     = []
  validation {
    condition = alltrue([
      for country in var.blocked_countries : length(country) == 2
    ])
    error_message = "Country codes must be 2-letter ISO 3166-1 alpha-2 codes."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain WAF logs in CloudWatch"
  type        = number
  default     = 30
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch Logs retention period."
  }
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
