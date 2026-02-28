# CloudWatch Dashboards Module
# Implements Requirement 18.2: Create CloudWatch dashboards for system health, performance, and business metrics

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# System Health Dashboard
resource "aws_cloudwatch_dashboard" "system_health" {
  dashboard_name = "${var.environment}-${var.service_name}-system-health"

  dashboard_body = jsonencode({
    widgets = [
      # Uptime Percentage Widget
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", { stat = "Average", label = "Healthy Hosts" }],
            [".", "UnHealthyHostCount", { stat = "Average", label = "Unhealthy Hosts" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "System Uptime - Healthy vs Unhealthy Hosts"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 0
      },
      # Uptime Percentage Calculation
      {
        type = "metric"
        properties = {
          metrics = [
            [{ expression = "100 * (m1 / (m1 + m2))", label = "Uptime %", id = "e1" }],
            ["AWS/ApplicationELB", "HealthyHostCount", { id = "m1", visible = false }],
            [".", "UnHealthyHostCount", { id = "m2", visible = false }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "System Uptime Percentage (Target: 99.5%)"
          yAxis = {
            left = {
              min = 95
              max = 100
            }
          }
          annotations = {
            horizontal = [
              {
                value = 99.5
                label = "SLA Target"
                fill  = "above"
                color = "#2ca02c"
              }
            ]
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 0
      },
      # Error Rate by Endpoint Widget
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "http_errors_total", "endpoint", "/api/v1/projects", { stat = "Sum", label = "Projects API" }],
            ["...", "/api/v1/analysis", { stat = "Sum", label = "Analysis API" }],
            ["...", "/api/v1/auth/login", { stat = "Sum", label = "Auth API" }],
            ["...", "/api/v1/webhooks", { stat = "Sum", label = "Webhooks API" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Error Count by Endpoint"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 6
      },
      # Error Rate Percentage
      {
        type = "metric"
        properties = {
          metrics = [
            [{ expression = "100 * (m1 / m2)", label = "Error Rate %", id = "e1" }],
            ["${var.service_name}", "http_errors_total", { id = "m1", stat = "Sum", visible = false }],
            [".", "http_requests_total", { id = "m2", stat = "Sum", visible = false }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Overall Error Rate (Target: < 5%)"
          yAxis = {
            left = {
              min = 0
              max = 10
            }
          }
          annotations = {
            horizontal = [
              {
                value = 5
                label = "Alert Threshold"
                fill  = "above"
                color = "#d62728"
              }
            ]
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 6
      },
      # Health Check Status Widget
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", { stat = "Average", label = "Response Time" }],
            ["...", { stat = "p99", label = "P99 Response Time" }]
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
          title  = "Health Check Response Time"
          yAxis = {
            left = {
              min = 0
            }
          }
          annotations = {
            horizontal = [
              {
                value = 1
                label = "Alert Threshold (1s)"
                fill  = "above"
                color = "#ff7f0e"
              }
            ]
          }
        }
        width  = 8
        height = 6
        x      = 0
        y      = 12
      },
      # Database Health Status
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "database_connections_active", "database", "postgresql", { stat = "Average", label = "PostgreSQL Connections" }],
            ["...", "redis", { stat = "Average", label = "Redis Connections" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Database Connection Health"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 8
        height = 6
        x      = 8
        y      = 12
      },
      # Active User Sessions Widget
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "active_sessions", { stat = "Average", label = "Active Sessions" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Active User Sessions"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 8
        height = 6
        x      = 16
        y      = 12
      },
      # Request Throughput
      {
        type = "metric"
        properties = {
          metrics = [
            [{ expression = "m1 / 60", label = "Requests/Second", id = "e1" }],
            ["${var.service_name}", "http_requests_total", { id = "m1", stat = "Sum", visible = false }]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
          title  = "Request Throughput (req/s)"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 18
      },
      # Authentication Metrics
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "auth_attempts_total", "status", "success", { stat = "Sum", label = "Successful Logins" }],
            ["...", "failure", { stat = "Sum", label = "Failed Logins" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Authentication Activity"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 18
      }
    ]
  })
}

# Performance Metrics Dashboard
resource "aws_cloudwatch_dashboard" "performance" {
  dashboard_name = "${var.environment}-${var.service_name}-performance"

  dashboard_body = jsonencode({
    widgets = [
      # API Response Time (P50, P95, P99)
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "http_request_duration_seconds", { stat = "p50", label = "P50" }],
            ["...", { stat = "p95", label = "P95" }],
            ["...", { stat = "p99", label = "P99" }]
          ]
          period = 300
          region = var.aws_region
          title  = "API Response Time Percentiles (Target P95 < 500ms)"
          yAxis = {
            left = {
              min = 0
            }
          }
          annotations = {
            horizontal = [
              {
                value = 0.5
                label = "P95 Target (500ms)"
                fill  = "above"
                color = "#ff7f0e"
              }
            ]
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 0
      },
      # Request Throughput
      {
        type = "metric"
        properties = {
          metrics = [
            [{ expression = "m1 / 60", label = "Requests/Second", id = "e1" }],
            ["${var.service_name}", "http_requests_total", { id = "m1", stat = "Sum", visible = false }]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
          title  = "Request Throughput"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 0
      },
      # Database Query Performance
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "database_query_duration_seconds", "database", "postgresql", { stat = "Average", label = "PostgreSQL Avg" }],
            ["...", { stat = "p95", label = "PostgreSQL P95" }],
            ["...", "redis", { stat = "Average", label = "Redis Avg" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Database Query Performance"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 6
      },
      # Cache Hit/Miss Ratio
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "cache_hit_ratio", { stat = "Average", label = "Cache Hit Ratio" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Cache Hit Ratio (Target: > 70%)"
          yAxis = {
            left = {
              min = 0
              max = 1
            }
          }
          annotations = {
            horizontal = [
              {
                value = 0.7
                label = "Target"
                fill  = "below"
                color = "#ff7f0e"
              }
            ]
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 6
      },
      # CPU Utilization
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", { stat = "Average", label = "Average CPU" }],
            ["...", { stat = "Maximum", label = "Max CPU" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "EC2 CPU Utilization (Alert at 80%)"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          annotations = {
            horizontal = [
              {
                value = 80
                label = "Alert Threshold"
                fill  = "above"
                color = "#d62728"
              }
            ]
          }
        }
        width  = 8
        height = 6
        x      = 0
        y      = 12
      },
      # Memory Utilization
      {
        type = "metric"
        properties = {
          metrics = [
            ["CWAgent", "mem_used_percent", { stat = "Average", label = "Memory Used %" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Memory Utilization (Alert at 85%)"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          annotations = {
            horizontal = [
              {
                value = 85
                label = "Alert Threshold"
                fill  = "above"
                color = "#d62728"
              }
            ]
          }
        }
        width  = 8
        height = 6
        x      = 8
        y      = 12
      },
      # Disk Utilization
      {
        type = "metric"
        properties = {
          metrics = [
            ["CWAgent", "disk_used_percent", { stat = "Average", label = "Disk Used %" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Disk Utilization (Alert at 90%)"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          annotations = {
            horizontal = [
              {
                value = 90
                label = "Alert Threshold"
                fill  = "above"
                color = "#d62728"
              }
            ]
          }
        }
        width  = 8
        height = 6
        x      = 16
        y      = 12
      }
    ]
  })
}

# Business Metrics Dashboard
resource "aws_cloudwatch_dashboard" "business_metrics" {
  dashboard_name = "${var.environment}-${var.service_name}-business-metrics"

  dashboard_body = jsonencode({
    widgets = [
      # Analysis Completion Rate
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "code_analysis_total", "status", "success", { stat = "Sum", label = "Successful" }],
            ["...", "error", { stat = "Sum", label = "Failed" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "Code Analysis Completion Rate"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 0
      },
      # Average Analysis Duration
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "code_analysis_duration_seconds", "analysis_type", "ast_parsing", { stat = "Average", label = "AST Parsing" }],
            ["...", "dependency_graph", { stat = "Average", label = "Dependency Graph" }],
            ["...", "llm_review", { stat = "Average", label = "LLM Review" }]
          ]
          period = 3600
          stat   = "Average"
          region = var.aws_region
          title  = "Average Analysis Duration by Type"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 0
      },
      # User Activity
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "auth_attempts_total", "method", "login", "status", "success", { stat = "Sum", label = "Logins" }],
            ["...", "register", "...", { stat = "Sum", label = "Registrations" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "User Activity (Logins & Registrations)"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 6
      },
      # GitHub Webhook Processing
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "github_webhook_events_total", "status", "success", { stat = "Sum", label = "Successful" }],
            ["...", "error", { stat = "Sum", label = "Failed" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "GitHub Webhook Processing Rate"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 6
      },
      # LLM API Usage
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "llm_requests_total", "provider", "openai", "status", "success", { stat = "Sum", label = "OpenAI Success" }],
            ["...", "anthropic", "...", { stat = "Sum", label = "Anthropic Success" }],
            ["...", "openai", "error", { stat = "Sum", label = "OpenAI Error" }],
            ["...", "anthropic", "...", { stat = "Sum", label = "Anthropic Error" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "LLM API Request Status"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 12
      },
      # LLM Token Usage
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "llm_tokens_used", "token_type", "prompt", { stat = "Sum", label = "Prompt Tokens" }],
            ["...", "completion", { stat = "Sum", label = "Completion Tokens" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "LLM Token Usage"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 12
      },
      # Celery Task Queue
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "celery_queue_length", "queue_name", "default", { stat = "Average", label = "Default Queue" }],
            ["...", "analysis", { stat = "Average", label = "Analysis Queue" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Celery Task Queue Length"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 0
        y      = 18
      },
      # Circular Dependencies Detected
      {
        type = "metric"
        properties = {
          metrics = [
            ["${var.service_name}", "circular_dependencies_detected", "severity", "high", { stat = "Sum", label = "High Severity" }],
            ["...", "medium", { stat = "Sum", label = "Medium Severity" }],
            ["...", "low", { stat = "Sum", label = "Low Severity" }]
          ]
          period = 3600
          stat   = "Sum"
          region = var.aws_region
          title  = "Circular Dependencies Detected"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
        width  = 12
        height = 6
        x      = 12
        y      = 18
      }
    ]
  })
}

# CloudWatch Alarms
# Implements Requirement 7.6: Configure alerts for critical conditions

# SNS Topic for Alert Notifications
resource "aws_sns_topic" "alerts" {
  name = "${var.environment}-${var.service_name}-alerts"

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-alerts"
      Environment = var.environment
      Purpose     = "CloudWatch alarm notifications"
    }
  )
}

# SNS Topic Subscription for Email
resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# SNS Topic Subscription for Slack (via HTTPS endpoint)
resource "aws_sns_topic_subscription" "slack" {
  count     = var.slack_webhook_url != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}

# Alarm 1: Error Rate > 5%
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.environment}-${var.service_name}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  alarm_description   = "Alert when error rate exceeds 5% for 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "100 * (errors / requests)"
    label       = "Error Rate %"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "http_errors_total"
      namespace   = var.service_name
      period      = 300
      stat        = "Sum"
    }
  }

  metric_query {
    id = "requests"
    metric {
      metric_name = "http_requests_total"
      namespace   = var.service_name
      period      = 300
      stat        = "Sum"
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-high-error-rate"
      Environment = var.environment
      Severity    = "Critical"
      Runbook     = "https://docs.example.com/runbooks/high-error-rate"
    }
  )
}

# Alarm 2: API Response Time > 1 second (P95)
resource "aws_cloudwatch_metric_alarm" "high_response_time" {
  alarm_name          = "${var.environment}-${var.service_name}-high-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 1.0
  alarm_description   = "Alert when API P95 response time exceeds 1 second for 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  metric_query {
    id = "response_time"
    metric {
      metric_name = "http_request_duration_seconds"
      namespace   = var.service_name
      period      = 300
      stat        = "p95"
    }
    return_data = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-high-response-time"
      Environment = var.environment
      Severity    = "Critical"
      Runbook     = "https://docs.example.com/runbooks/high-response-time"
    }
  )
}

# Alarm 3: CPU Utilization > 80%
resource "aws_cloudwatch_metric_alarm" "high_cpu_utilization" {
  alarm_name          = "${var.environment}-${var.service_name}-high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alert when CPU utilization exceeds 80% for 10 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    AutoScalingGroupName = var.autoscaling_group_name
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-high-cpu-utilization"
      Environment = var.environment
      Severity    = "Critical"
      Runbook     = "https://docs.example.com/runbooks/high-cpu-utilization"
    }
  )
}

# Additional Alarm: Memory Utilization > 85%
resource "aws_cloudwatch_metric_alarm" "high_memory_utilization" {
  alarm_name          = "${var.environment}-${var.service_name}-high-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "mem_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Alert when memory utilization exceeds 85% for 10 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-high-memory-utilization"
      Environment = var.environment
      Severity    = "Warning"
      Runbook     = "https://docs.example.com/runbooks/high-memory-utilization"
    }
  )
}

# Additional Alarm: Disk Utilization > 90%
resource "aws_cloudwatch_metric_alarm" "high_disk_utilization" {
  alarm_name          = "${var.environment}-${var.service_name}-high-disk-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "Alert when disk utilization exceeds 90%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-high-disk-utilization"
      Environment = var.environment
      Severity    = "Warning"
      Runbook     = "https://docs.example.com/runbooks/high-disk-utilization"
    }
  )
}

# Additional Alarm: Database Connection Failures
resource "aws_cloudwatch_metric_alarm" "database_connection_failures" {
  alarm_name          = "${var.environment}-${var.service_name}-database-connection-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 5
  alarm_description   = "Alert when database connection failures exceed 5 in 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"

  metric_query {
    id = "connection_failures"
    metric {
      metric_name = "database_connection_errors"
      namespace   = var.service_name
      period      = 300
      stat        = "Sum"
    }
    return_data = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-database-connection-failures"
      Environment = var.environment
      Severity    = "Critical"
      Runbook     = "https://docs.example.com/runbooks/database-connection-failures"
    }
  )
}

# Additional Alarm: Health Check Failures
resource "aws_cloudwatch_metric_alarm" "health_check_failures" {
  alarm_name          = "${var.environment}-${var.service_name}-health-check-failures"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Alert when healthy host count drops below 1"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "breaching"

  tags = merge(
    var.tags,
    {
      Name        = "${var.environment}-${var.service_name}-health-check-failures"
      Environment = var.environment
      Severity    = "Critical"
      Runbook     = "https://docs.example.com/runbooks/health-check-failures"
    }
  )
}
