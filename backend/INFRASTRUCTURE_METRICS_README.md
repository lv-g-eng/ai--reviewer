# Infrastructure Metrics Collection

This document describes the comprehensive infrastructure metrics collection system that monitors EC2, RDS, and ElastiCache resources and sends metrics to CloudWatch.

## Overview

The infrastructure metrics collection system satisfies:

- **Requirement 7.4**: Collect infrastructure metrics for CPU, memory, disk, and network usage
- **Requirement 7.10**: Retain metrics for 90 days in CloudWatch

## Features

### EC2 Instance Metrics (Requirement 7.4)

**Detailed CloudWatch Monitoring**: Enabled by default on all EC2 instances for 1-minute metric granularity.

**CloudWatch Agent Metrics**: Custom metrics collected every 60 seconds:

**CPU Metrics**:
- CPU idle percentage
- CPU I/O wait percentage
- CPU system usage percentage
- CPU user usage percentage

**Memory Metrics**:
- Memory used percentage
- Memory available (MB)
- Memory used (MB)
- Memory total (MB)

**Disk Metrics**:
- Disk used percentage
- Disk free space (GB)
- Disk used space (GB)
- Disk inodes free

**Disk I/O Metrics**:
- Disk I/O time (milliseconds)
- Disk write bytes
- Disk read bytes
- Disk write operations count
- Disk read operations count

**Network Metrics**:
- Network bytes sent
- Network bytes received
- Network packets sent
- Network packets received
- Network packets dropped (in/out)
- Network errors (in/out)

**Network Connection Metrics**:
- TCP established connections
- TCP time wait connections
- TCP close wait connections

**Process Metrics**:
- Running processes count
- Sleeping processes count
- Dead processes count
- Total processes count

### Database Metrics (Requirement 7.4)

**RDS PostgreSQL Enhanced Monitoring**: Enabled with 60-second granularity.

**Connection Pool Metrics**:
- Pool size
- Connections checked out
- Connections checked in
- Overflow connections
- Pool utilization percentage

**Query Performance Metrics**:
- Query execution time
- Slow query count
- Connection count
- Transaction count

### Cache Metrics (Requirement 7.4)

**ElastiCache Redis Metrics**: Automatically collected by AWS.

**Custom Cache Metrics**:
- Cache hits count
- Cache misses count
- Cache hit ratio percentage
- Cache miss ratio percentage
- Cache evictions count
- Cache size

## Architecture

### Metrics Collection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     EC2 Instances                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         CloudWatch Agent                              │  │
│  │  - Collects system metrics (CPU, memory, disk, net)  │  │
│  │  - Sends to CloudWatch every 60 seconds              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    Application Metrics Collector                      │  │
│  │  - Collects connection pool metrics                   │  │
│  │  - Collects cache metrics                             │  │
│  │  - Sends to CloudWatch via boto3                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS CloudWatch                             │
│                                                              │
│  - Namespace: AICodeReviewer/{environment}                  │
│  - Retention: 90 days (Requirement 7.10)                    │
│  - Dimensions: Environment, ServiceName, InstanceId         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CloudWatch Dashboards & Alarms                  │
│                                                              │
│  - System health dashboard                                  │
│  - Performance metrics dashboard                            │
│  - Alerts for critical thresholds                           │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# Enable/disable CloudWatch metrics
CLOUDWATCH_METRICS_ENABLED=true

# AWS region for CloudWatch
AWS_REGION=us-east-1

# Service identification
SERVICE_NAME=backend-api
ENVIRONMENT=production
INSTANCE_ID=i-1234567890abcdef0
```

### Terraform Configuration

**EC2 Detailed Monitoring** (terraform/modules/compute/variables.tf):
```hcl
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring for EC2 instances"
  type        = bool
  default     = true
}
```

**RDS Enhanced Monitoring** (terraform/modules/database/variables.tf):
```hcl
variable "enable_enhanced_monitoring" {
  description = "Enable RDS enhanced monitoring"
  type        = bool
  default     = true
}

variable "enable_performance_insights" {
  description = "Enable RDS Performance Insights"
  type        = bool
  default     = true
}
```

### CloudWatch Agent Configuration

The CloudWatch Agent is automatically configured on EC2 instances via user_data script. Configuration file: `/opt/aws/amazon-cloudwatch-agent/etc/config.json`

Key settings:
- **Metrics collection interval**: 60 seconds
- **Namespace**: `AICodeReviewer/{environment}`
- **Dimensions**: AutoScalingGroupName, InstanceId, InstanceType, Environment, Project

## Usage

### Automatic Collection

Metrics are automatically collected by:

1. **CloudWatch Agent**: Runs on all EC2 instances, collects system metrics every 60 seconds
2. **Celery Periodic Tasks**: Collect application metrics every 1-2 minutes
3. **AWS Services**: RDS and ElastiCache automatically send metrics to CloudWatch

### Manual Collection

To manually trigger metrics collection:

```python
from app.core.infrastructure_metrics import collect_and_send_metrics

# Collect and send all system metrics
success = collect_and_send_metrics()

# Collect and send with additional custom metrics
success = collect_and_send_metrics({
    'custom_metric_1': 123,
    'custom_metric_2': 456
})
```

### Collecting Specific Metrics

```python
from app.core.infrastructure_metrics import get_metrics_collector

collector = get_metrics_collector()

# Collect system metrics only
system_metrics = collector.collect_system_metrics()

# Collect connection pool metrics
pool_metrics = collector.collect_connection_pool_metrics(
    pool_name='postgresql',
    size=20,
    checked_out=15,
    overflow=2,
    checked_in=5
)

# Collect cache metrics
cache_metrics = collector.collect_cache_metrics(
    cache_name='redis',
    hits=800,
    misses=200,
    evictions=50,
    size=10000
)

# Send metrics to CloudWatch
collector.send_metrics_to_cloudwatch(system_metrics)
```

## Periodic Tasks

Infrastructure metrics are collected automatically by Celery Beat periodic tasks:

### Infrastructure Metrics Task
- **Task**: `collect_infrastructure_metrics`
- **Schedule**: Every 1 minute
- **Collects**: CPU, memory, disk, network metrics
- **Queue**: low_priority

### Database Pool Metrics Task
- **Task**: `collect_database_pool_metrics`
- **Schedule**: Every 2 minutes
- **Collects**: Connection pool statistics
- **Queue**: low_priority

### Cache Metrics Task
- **Task**: `collect_cache_metrics`
- **Schedule**: Every 2 minutes
- **Collects**: Cache hit/miss ratio, eviction rate
- **Queue**: low_priority

## CloudWatch Metrics

### Metric Namespaces

- **EC2 System Metrics**: `AICodeReviewer/{environment}`
- **RDS Metrics**: `AWS/RDS`
- **ElastiCache Metrics**: `AWS/ElastiCache`
- **Application Metrics**: `AICodeReviewer/{environment}`

### Metric Dimensions

All custom metrics include the following dimensions:
- **Environment**: development, staging, production
- **ServiceName**: backend-api, worker, etc.
- **InstanceId**: EC2 instance ID
- **AutoScalingGroupName**: ASG name (for EC2 metrics)
- **InstanceType**: EC2 instance type (for EC2 metrics)

### Metric Retention

- **Metrics**: 90 days (Requirement 7.10)
- **Logs**: 30 days (Requirement 7.10)

## CloudWatch Dashboards

### System Health Dashboard

Visualizes:
- CPU utilization across all instances
- Memory usage trends
- Disk usage and I/O
- Network throughput
- Process counts

### Database Performance Dashboard

Visualizes:
- RDS CPU and memory utilization
- Database connections
- Query performance
- Connection pool utilization
- Slow query count

### Cache Performance Dashboard

Visualizes:
- ElastiCache CPU and memory
- Cache hit/miss ratio
- Eviction rate
- Cache size trends
- Network throughput

## CloudWatch Alarms

### EC2 Alarms

**High CPU Utilization**:
- Threshold: > 80% for 2 consecutive periods (4 minutes)
- Action: Scale up Auto Scaling Group

**Low CPU Utilization**:
- Threshold: < 20% for 2 consecutive periods (4 minutes)
- Action: Scale down Auto Scaling Group

**High Memory Usage**:
- Threshold: > 85% for 2 consecutive periods (2 minutes)
- Action: Send notification

**High Disk Usage**:
- Threshold: > 90%
- Action: Send critical alert

### RDS Alarms

**High CPU**:
- Threshold: > 80% for 2 consecutive periods (10 minutes)
- Action: Send notification

**Low Memory**:
- Threshold: < 1GB for 2 consecutive periods (10 minutes)
- Action: Send notification

**Low Storage**:
- Threshold: < 10GB
- Action: Send critical alert

### ElastiCache Alarms

**High CPU**:
- Threshold: > 75% for 2 consecutive periods (10 minutes)
- Action: Send notification

**High Memory**:
- Threshold: > 90% for 2 consecutive periods (10 minutes)
- Action: Send notification

**Low Cache Hit Ratio**:
- Threshold: < 70% for 5 consecutive periods (10 minutes)
- Action: Send notification

## Monitoring and Alerting

### Alert Channels

- **Email**: ops-team@example.com
- **Slack**: #production-alerts
- **PagerDuty**: For critical alerts

### Alert Response

When an alert triggers:

1. Check CloudWatch dashboard for context
2. Review recent deployments or changes
3. Check application logs in CloudWatch Logs
4. Follow runbook procedures for specific alerts
5. Escalate if needed

## Troubleshooting

### CloudWatch Agent Not Sending Metrics

**Symptom**: No custom metrics appearing in CloudWatch

**Possible Causes**:
1. CloudWatch Agent not running
2. IAM permissions missing
3. Configuration file errors

**Solution**:
```bash
# Check CloudWatch Agent status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a query -m ec2 -c default -s

# Check CloudWatch Agent logs
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log

# Restart CloudWatch Agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### Application Metrics Not Appearing

**Symptom**: System metrics work but application metrics don't

**Possible Causes**:
1. Celery Beat not running
2. AWS credentials not configured
3. Metrics collection disabled

**Solution**:
```bash
# Check Celery Beat status
celery -A app.celery_config inspect active

# Check environment variables
echo $CLOUDWATCH_METRICS_ENABLED
echo $AWS_REGION

# Test metrics collection manually
python -c "from app.core.infrastructure_metrics import collect_and_send_metrics; print(collect_and_send_metrics())"
```

### High CloudWatch Costs

**Symptom**: Unexpected CloudWatch costs

**Solutions**:
1. Reduce metrics collection frequency (increase interval from 60s to 120s)
2. Disable detailed monitoring for non-production environments
3. Reduce metric retention period (90 days → 30 days for non-critical metrics)
4. Use metric filters to reduce custom metric count

## Testing

### Unit Tests

Run infrastructure metrics tests:

```bash
cd backend
pytest tests/test_infrastructure_metrics.py -v
```

### Integration Tests

Test metrics collection end-to-end:

```bash
# Start application
python -m app.main

# Trigger metrics collection
curl -X POST http://localhost:8000/api/v1/admin/collect-metrics

# Check CloudWatch for metrics (wait 1-2 minutes)
aws cloudwatch get-metric-statistics \
    --namespace AICodeReviewer/development \
    --metric-name cpu_usage_percent \
    --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 60 \
    --statistics Average
```

## Best Practices

### 1. Use Appropriate Collection Intervals

- **System metrics**: 60 seconds (balance between granularity and cost)
- **Application metrics**: 120 seconds (less frequent for cost optimization)
- **Database metrics**: 60 seconds (RDS enhanced monitoring)

### 2. Set Meaningful Dimensions

Always include:
- Environment (development, staging, production)
- ServiceName (backend-api, worker)
- InstanceId (for troubleshooting specific instances)

### 3. Monitor Metric Costs

- Review CloudWatch costs monthly
- Disable detailed monitoring in development
- Use metric filters to reduce custom metric count
- Archive old metrics to S3 for long-term storage

### 4. Create Actionable Alerts

- Set thresholds based on baseline metrics
- Include runbook links in alert descriptions
- Use composite alarms to reduce alert fatigue
- Test alerts regularly

### 5. Optimize Metric Retention

- **Critical metrics**: 90 days
- **Non-critical metrics**: 30 days
- **Development metrics**: 7 days

## Performance Considerations

### Metrics Collection Overhead

- **CloudWatch Agent**: ~1-2% CPU overhead
- **Application metrics**: ~0.5% CPU overhead
- **Network bandwidth**: ~10-20 KB/minute per instance

### Cost Optimization

**Estimated Monthly Costs** (per environment):
- **EC2 detailed monitoring**: $2.10 per instance
- **Custom metrics**: $0.30 per metric
- **CloudWatch Logs**: $0.50 per GB ingested
- **Total**: ~$50-100 per month for production

**Cost Reduction Strategies**:
1. Disable detailed monitoring in development
2. Reduce custom metric count
3. Use metric math to derive metrics instead of sending separately
4. Aggregate metrics at application level before sending

## Security

### IAM Permissions

EC2 instances require the following CloudWatch permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/ec2/*"
    }
  ]
}
```

### Data Privacy

- Metrics do not contain PII
- Metric dimensions are sanitized
- Sensitive data is never included in metric names or values

## Compliance

### Data Retention (Requirement 7.10)

- **Metrics**: Retained for 90 days in CloudWatch
- **Logs**: Retained for 30 days in CloudWatch Logs
- **Automatic deletion**: After retention period

### Audit Trail

- All CloudWatch API calls logged in CloudTrail
- Metric access logged for compliance
- Retention policy changes audited

## References

- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [CloudWatch Agent Configuration](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html)
- [RDS Enhanced Monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html)
- [ElastiCache Metrics](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheMetrics.html)
- [CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/)

