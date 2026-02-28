# CloudWatch Monitoring Module

This Terraform module creates comprehensive CloudWatch dashboards and alarms for monitoring the AI-Based Reviewer system.

**Validates Requirements**: 
- 18.2 - Complete monitoring and observability implementation
- 7.6 - Configure alerts for critical conditions

## Overview

The module creates:

### Dashboards

1. **System Health Dashboard** - Uptime, error rates, health checks, and active sessions
2. **Performance Metrics Dashboard** - API response times, throughput, database performance, and resource utilization
3. **Business Metrics Dashboard** - Analysis completion rates, user activity, and LLM usage

### Alarms

1. **High Error Rate** - Triggers when error rate > 5% for 10 minutes
2. **High Response Time** - Triggers when API P95 > 1 second for 10 minutes
3. **High CPU Utilization** - Triggers when CPU > 80% for 10 minutes
4. **High Memory Utilization** - Triggers when memory > 85% for 10 minutes
5. **High Disk Utilization** - Triggers when disk > 90% for 5 minutes
6. **Database Connection Failures** - Triggers when connection errors > 5 in 5 minutes
7. **Health Check Failures** - Triggers when healthy hosts < 1 for 2 minutes

## Features

### Dashboards

- **Uptime Monitoring**: Track system availability with 99.5% SLA target
- **Error Tracking**: Monitor error rates by endpoint with 5% threshold alerts
- **Health Checks**: Monitor service health and response times
- **Active Sessions**: Track concurrent user sessions
- **Performance Metrics**: API response times (P50, P95, P99) with 500ms target
- **Resource Utilization**: CPU, memory, and disk usage monitoring
- **Business Metrics**: Code analysis completion rates and user activity
- **LLM Integration**: Track LLM API usage and token consumption

### Alarms

- **SNS Integration**: Email and Slack notifications for all alarms
- **Configurable Thresholds**: Customize alert thresholds per environment
- **Evaluation Periods**: Multi-period evaluation to reduce false positives
- **Runbook Links**: Each alarm includes troubleshooting documentation
- **Auto-Scaling Integration**: CPU alarms can target Auto Scaling Groups
- **OK Actions**: Notifications when alarms return to normal state

## Usage

### Basic Usage

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = "prod"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  # Alert configuration
  alert_email            = "ops@example.com"
  slack_webhook_url      = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  autoscaling_group_name = "prod-ai-reviewer-asg"
  
  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

### With Custom Thresholds

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = "prod"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  # Alert configuration
  alert_email             = "ops@example.com"
  error_rate_threshold    = 3      # Alert at 3% instead of 5%
  response_time_threshold = 0.5    # Alert at 500ms instead of 1s
  cpu_threshold           = 70     # Alert at 70% instead of 80%
  
  tags = {
    Environment = "production"
  }
}
```

### Selective Dashboard Creation

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = "dev"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  enable_system_health_dashboard      = true
  enable_performance_dashboard        = true
  enable_business_metrics_dashboard   = false  # Disable in dev
  
  tags = {
    Environment = "development"
  }
}
```

### Integration with Main Terraform Configuration

Add to your `main.tf`:

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = var.environment
  service_name = var.service_name
  aws_region   = var.aws_region
  
  tags = var.tags
}

# Output dashboard URLs
output "dashboard_urls" {
  description = "URLs to access CloudWatch dashboards"
  value       = module.monitoring.dashboard_urls
}
```

## Dashboard Details

### System Health Dashboard

**Widgets**:
- **Uptime Percentage**: Calculates system uptime based on healthy/unhealthy hosts
  - Target: 99.5% uptime SLA
  - Alert threshold: Below 99.5%
  
- **Error Rate by Endpoint**: Tracks errors for each API endpoint
  - Endpoints: Projects, Analysis, Auth, Webhooks
  - Aggregation: Sum over 5-minute periods
  
- **Overall Error Rate**: Percentage of failed requests
  - Target: < 5% error rate
  - Alert threshold: Above 5%
  
- **Health Check Response Time**: Monitor service health check latency
  - Metrics: Average and P99 response time
  - Alert threshold: > 1 second
  
- **Database Connection Health**: Active connections to PostgreSQL and Redis
  - Helps identify connection pool issues
  
- **Active User Sessions**: Number of concurrent authenticated users
  - Useful for capacity planning

### Performance Metrics Dashboard

**Widgets**:
- **API Response Time Percentiles**: P50, P95, P99 response times
  - Target: P95 < 500ms
  - Alert threshold: P95 > 500ms
  
- **Request Throughput**: Requests per second
  - Calculated from total request count
  
- **Database Query Performance**: Query latency for PostgreSQL and Redis
  - Metrics: Average and P95
  - Helps identify slow queries
  
- **Cache Hit Ratio**: Percentage of cache hits
  - Target: > 70% hit rate
  - Alert threshold: < 70%
  
- **CPU Utilization**: EC2 instance CPU usage
  - Metrics: Average and Maximum
  - Alert threshold: > 80% for 10 minutes
  
- **Memory Utilization**: Memory usage percentage
  - Alert threshold: > 85%
  
- **Disk Utilization**: Disk usage percentage
  - Alert threshold: > 90%

### Business Metrics Dashboard

**Widgets**:
- **Code Analysis Completion Rate**: Successful vs failed analyses
  - Aggregation: Hourly sums
  
- **Average Analysis Duration**: Time taken by analysis type
  - Types: AST parsing, dependency graph, LLM review
  
- **User Activity**: Logins and registrations
  - Aggregation: Hourly sums
  
- **GitHub Webhook Processing**: Successful vs failed webhook events
  - Aggregation: Hourly sums
  
- **LLM API Usage**: Requests by provider and status
  - Providers: OpenAI, Anthropic
  - Status: Success, error, rate limited
  
- **LLM Token Usage**: Prompt and completion tokens consumed
  - Useful for cost tracking
  
- **Celery Task Queue**: Queue length by queue name
  - Queues: Default, analysis
  - Helps identify processing bottlenecks
  
- **Circular Dependencies Detected**: Count by severity
  - Severity levels: High, medium, low

## Metrics Requirements

The dashboards expect the following metrics to be published to CloudWatch:

### Application Metrics (Custom Namespace)

Namespace: `{service_name}` (default: `ai-reviewer`)

**HTTP Metrics**:
- `http_request_duration_seconds` - Histogram with labels: method, endpoint, status_code
- `http_requests_total` - Counter with labels: method, endpoint, status_code
- `http_errors_total` - Counter with labels: method, endpoint, status_code, error_type

**Database Metrics**:
- `database_query_duration_seconds` - Histogram with labels: database, operation
- `database_connections_active` - Gauge with labels: database
- `database_operations_total` - Counter with labels: database, operation, status

**Analysis Metrics**:
- `code_analysis_duration_seconds` - Histogram with labels: analysis_type
- `code_analysis_total` - Counter with labels: analysis_type, status
- `circular_dependencies_detected` - Counter with labels: severity

**LLM Metrics**:
- `llm_requests_total` - Counter with labels: provider, model, status
- `llm_request_duration_seconds` - Histogram with labels: provider, model
- `llm_tokens_used` - Counter with labels: provider, model, token_type

**Cache Metrics**:
- `cache_operations_total` - Counter with labels: operation, status
- `cache_hit_ratio` - Gauge

**Authentication Metrics**:
- `auth_attempts_total` - Counter with labels: method, status
- `active_sessions` - Gauge

**GitHub Metrics**:
- `github_webhook_events_total` - Counter with labels: event_type, status
- `github_api_requests_total` - Counter with labels: operation, status

**Celery Metrics**:
- `celery_tasks_total` - Counter with labels: task_name, status
- `celery_task_duration_seconds` - Histogram with labels: task_name
- `celery_queue_length` - Gauge with labels: queue_name

### AWS Metrics (Standard Namespaces)

**Application Load Balancer** (`AWS/ApplicationELB`):
- `HealthyHostCount`
- `UnHealthyHostCount`
- `TargetResponseTime`

**EC2** (`AWS/EC2`):
- `CPUUtilization`

**CloudWatch Agent** (`CWAgent`):
- `mem_used_percent`
- `disk_used_percent`

## Metric Publishing

Metrics are published using:

1. **Prometheus Client** - Application metrics collected via `backend/app/core/prometheus_metrics.py`
2. **CloudWatch Agent** - Infrastructure metrics (CPU, memory, disk)
3. **AWS Services** - Native AWS service metrics (ALB, EC2)

See `backend/app/middleware/prometheus_middleware.py` for automatic HTTP metric collection.

## Customization

### Adding New Widgets

To add a new widget to a dashboard:

1. Edit the dashboard resource in `main.tf`
2. Add a new widget object to the `widgets` array
3. Specify widget properties:
   - `type`: "metric", "log", or "text"
   - `properties`: Widget configuration
   - `width`, `height`: Widget dimensions (max width: 24)
   - `x`, `y`: Widget position

Example:

```hcl
{
  type = "metric"
  properties = {
    metrics = [
      ["${var.service_name}", "custom_metric", { stat = "Average" }]
    ]
    period = 300
    stat   = "Average"
    region = var.aws_region
    title  = "Custom Metric"
  }
  width  = 12
  height = 6
  x      = 0
  y      = 24
}
```

### Modifying Alert Thresholds

Alert thresholds are defined in the `annotations` section of widgets:

```hcl
annotations = {
  horizontal = [
    {
      value = 99.5        # Threshold value
      label = "SLA Target"
      fill  = "above"     # "above" or "below"
      color = "#2ca02c"   # Green
    }
  ]
}
```

Common colors:
- Green: `#2ca02c` (good)
- Orange: `#ff7f0e` (warning)
- Red: `#d62728` (critical)

### Changing Time Periods

Modify the `period` property (in seconds):
- 60 = 1 minute
- 300 = 5 minutes (default)
- 3600 = 1 hour

## Deployment

### Using Terraform

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# View dashboard URLs
terraform output dashboard_urls
```

### Using Python Script

```bash
# Install dependencies
pip install boto3

# Create all dashboards
python backend/scripts/manage_cloudwatch_dashboards.py create-all \
  --region us-east-1 \
  --environment prod \
  --service-name ai-reviewer

# List existing dashboards
python backend/scripts/manage_cloudwatch_dashboards.py list

# Get dashboard configuration
python backend/scripts/manage_cloudwatch_dashboards.py get \
  --dashboard prod-ai-reviewer-system-health

# Delete a dashboard
python backend/scripts/manage_cloudwatch_dashboards.py delete \
  --dashboard prod-ai-reviewer-system-health
```

## Accessing Dashboards

After deployment, access dashboards via:

1. **AWS Console**: Navigate to CloudWatch > Dashboards
2. **Direct URL**: Use the URLs from `terraform output dashboard_urls`
3. **CLI**: `aws cloudwatch get-dashboard --dashboard-name <name>`

## Monitoring Best Practices

1. **Regular Review**: Review dashboards daily during initial deployment, then weekly
2. **Alert Tuning**: Adjust alert thresholds based on baseline metrics to reduce false positives
3. **Capacity Planning**: Use trend analysis to predict when scaling is needed
4. **Incident Response**: Link dashboards in runbooks for faster troubleshooting
5. **Cost Optimization**: Monitor LLM token usage to control API costs

## Troubleshooting

### Dashboards Not Showing Data

**Symptom**: Widgets show "No data available"

**Causes**:
1. Metrics not being published
2. Incorrect metric namespace or dimensions
3. Time range too narrow

**Solutions**:
1. Verify metrics are being published: `aws cloudwatch list-metrics --namespace ai-reviewer`
2. Check metric names and labels match dashboard configuration
3. Expand time range to last 24 hours

### Missing Infrastructure Metrics

**Symptom**: CPU/Memory/Disk widgets show no data

**Causes**:
1. CloudWatch Agent not installed
2. CloudWatch Agent not configured correctly
3. IAM permissions missing

**Solutions**:
1. Install CloudWatch Agent: See `terraform/modules/compute/user_data.sh`
2. Verify agent configuration: `terraform/modules/compute/cloudwatch_agent_config.json`
3. Check IAM role has `CloudWatchAgentServerPolicy` attached

### High Dashboard Costs

**Symptom**: Unexpected CloudWatch costs

**Causes**:
1. Too many custom metrics
2. High-resolution metrics (< 60s period)
3. Long retention periods

**Solutions**:
1. Consolidate similar metrics using labels
2. Use standard resolution (60s minimum)
3. Reduce metric retention to 15 days for non-critical metrics

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| environment | Environment name | string | - | yes |
| service_name | Service name for metrics namespace | string | "ai-reviewer" | no |
| aws_region | AWS region | string | - | yes |
| enable_system_health_dashboard | Enable System Health dashboard | bool | true | no |
| enable_performance_dashboard | Enable Performance dashboard | bool | true | no |
| enable_business_metrics_dashboard | Enable Business Metrics dashboard | bool | true | no |
| tags | Tags to apply to resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| system_health_dashboard_arn | ARN of System Health dashboard |
| system_health_dashboard_name | Name of System Health dashboard |
| performance_dashboard_arn | ARN of Performance dashboard |
| performance_dashboard_name | Name of Performance dashboard |
| business_metrics_dashboard_arn | ARN of Business Metrics dashboard |
| business_metrics_dashboard_name | Name of Business Metrics dashboard |
| dashboard_urls | Map of dashboard URLs |

## Related Documentation

- [CloudWatch Integration](../../../backend/CLOUDWATCH_INTEGRATION_README.md)
- [Prometheus Metrics](../../../backend/PROMETHEUS_METRICS_README.md)
- [Infrastructure Metrics](../../../backend/INFRASTRUCTURE_METRICS_README.md)
- [Operations Runbook](../../../docs/operations/runbook.md)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0 |
| aws | ~> 5.0 |

## License

This module is part of the AI-Based Reviewer project.
