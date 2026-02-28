# CloudWatch Alerts Configuration

This document provides comprehensive information about CloudWatch alarms configured for the AI Reviewer system.

## Overview

The monitoring module includes CloudWatch alarms that trigger notifications when critical system metrics exceed defined thresholds. Alarms are integrated with SNS topics for email and Slack notifications.

## Alert Rules

### Critical Alerts

These alarms require immediate attention and indicate potential service degradation or outages.

#### 1. High Error Rate (> 5%)

**Alarm Name**: `{environment}-{service_name}-high-error-rate`

**Description**: Triggers when the HTTP error rate exceeds 5% for 5 minutes.

**Metrics**:
- Error Rate % = 100 * (http_errors_total / http_requests_total)

**Configuration**:
- Threshold: 5%
- Evaluation Period: 2 periods × 5 minutes = 10 minutes
- Comparison: GreaterThanThreshold
- Statistic: Calculated from Sum of errors and requests

**Severity**: Critical

**Runbook**: [High Error Rate Troubleshooting](#high-error-rate-troubleshooting)

**Common Causes**:
- Application bugs or exceptions
- Database connection failures
- External API failures (GitHub, LLM providers)
- Invalid input data
- Configuration errors

---

#### 2. High API Response Time (> 1 second)

**Alarm Name**: `{environment}-{service_name}-high-response-time`

**Description**: Triggers when API P95 response time exceeds 1 second for 5 minutes.

**Metrics**:
- http_request_duration_seconds (P95)

**Configuration**:
- Threshold: 1.0 second
- Evaluation Period: 2 periods × 5 minutes = 10 minutes
- Comparison: GreaterThanThreshold
- Statistic: p95 (95th percentile)

**Severity**: Critical

**Runbook**: [High Response Time Troubleshooting](#high-response-time-troubleshooting)

**Common Causes**:
- Database query performance issues
- High CPU or memory utilization
- Network latency
- LLM API slow responses
- Large payload processing
- Insufficient connection pool size

---

#### 3. High CPU Utilization (> 80%)

**Alarm Name**: `{environment}-{service_name}-high-cpu-utilization`

**Description**: Triggers when EC2 CPU utilization exceeds 80% for 10 minutes.

**Metrics**:
- AWS/EC2 CPUUtilization (Average)

**Configuration**:
- Threshold: 80%
- Evaluation Period: 2 periods × 5 minutes = 10 minutes
- Comparison: GreaterThanThreshold
- Statistic: Average
- Dimensions: AutoScalingGroupName (if configured)

**Severity**: Critical

**Runbook**: [High CPU Utilization Troubleshooting](#high-cpu-utilization-troubleshooting)

**Common Causes**:
- High request volume
- CPU-intensive operations (AST parsing, graph analysis)
- Inefficient algorithms
- Memory leaks causing garbage collection overhead
- Insufficient instance size

---

### Warning Alerts

These alarms indicate potential issues that should be monitored but may not require immediate action.

#### 4. High Memory Utilization (> 85%)

**Alarm Name**: `{environment}-{service_name}-high-memory-utilization`

**Description**: Triggers when memory utilization exceeds 85% for 10 minutes.

**Metrics**:
- CWAgent mem_used_percent (Average)

**Configuration**:
- Threshold: 85%
- Evaluation Period: 2 periods × 5 minutes = 10 minutes
- Comparison: GreaterThanThreshold
- Statistic: Average

**Severity**: Warning

**Runbook**: [High Memory Utilization Troubleshooting](#high-memory-utilization-troubleshooting)

**Common Causes**:
- Memory leaks
- Large data structures in memory
- Insufficient instance memory
- Cache size too large
- Too many concurrent requests

---

#### 5. High Disk Utilization (> 90%)

**Alarm Name**: `{environment}-{service_name}-high-disk-utilization`

**Description**: Triggers when disk utilization exceeds 90%.

**Metrics**:
- CWAgent disk_used_percent (Average)

**Configuration**:
- Threshold: 90%
- Evaluation Period: 1 period × 5 minutes = 5 minutes
- Comparison: GreaterThanThreshold
- Statistic: Average

**Severity**: Warning

**Runbook**: [High Disk Utilization Troubleshooting](#high-disk-utilization-troubleshooting)

**Common Causes**:
- Log files accumulation
- Temporary files not cleaned up
- Database growth
- Insufficient disk space provisioned

---

#### 6. Database Connection Failures

**Alarm Name**: `{environment}-{service_name}-database-connection-failures`

**Description**: Triggers when database connection failures exceed 5 in 5 minutes.

**Metrics**:
- database_connection_errors (Sum)

**Configuration**:
- Threshold: 5 errors
- Evaluation Period: 1 period × 5 minutes = 5 minutes
- Comparison: GreaterThanThreshold
- Statistic: Sum

**Severity**: Critical

**Common Causes**:
- Database instance down
- Network connectivity issues
- Connection pool exhausted
- Invalid credentials
- Database maintenance

---

#### 7. Health Check Failures

**Alarm Name**: `{environment}-{service_name}-health-check-failures`

**Description**: Triggers when healthy host count drops below 1.

**Metrics**:
- AWS/ApplicationELB HealthyHostCount (Average)

**Configuration**:
- Threshold: 1 host
- Evaluation Period: 2 periods × 1 minute = 2 minutes
- Comparison: LessThanThreshold
- Statistic: Average
- TreatMissingData: breaching

**Severity**: Critical

**Common Causes**:
- Application crashes
- Health check endpoint failures
- Instance termination
- Deployment issues

---

## Notification Channels

### SNS Topic

All alarms publish notifications to an SNS topic:

**Topic Name**: `{environment}-{service_name}-alerts`

**Subscriptions**:
- Email: Configured via `alert_email` variable
- Slack: Configured via `slack_webhook_url` variable (HTTPS endpoint)

### Notification Format

Alarm notifications include:
- Alarm name and description
- Current state (ALARM, OK, INSUFFICIENT_DATA)
- Threshold value
- Current metric value
- Timestamp
- AWS region
- Link to CloudWatch console

---

## Configuration

### Terraform Variables

Configure alarms using these variables in your Terraform configuration:

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment             = "prod"
  service_name            = "ai-reviewer"
  aws_region              = "us-east-1"
  
  # Alert configuration
  alert_email             = "ops@example.com"
  slack_webhook_url       = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  autoscaling_group_name  = "prod-ai-reviewer-asg"
  
  # Threshold customization (optional)
  error_rate_threshold    = 5      # Default: 5%
  response_time_threshold = 1.0    # Default: 1.0 second
  cpu_threshold           = 80     # Default: 80%
  memory_threshold        = 85     # Default: 85%
  disk_threshold          = 90     # Default: 90%
  
  tags = {
    Environment = "prod"
    Project     = "ai-reviewer"
  }
}
```

### Python Script

Alternatively, use the Python management script:

```bash
# Create all alarms
python backend/scripts/manage_cloudwatch_alarms.py create-all \
  --region us-east-1 \
  --environment prod \
  --email ops@example.com \
  --autoscaling-group prod-ai-reviewer-asg

# List alarms
python backend/scripts/manage_cloudwatch_alarms.py list \
  --region us-east-1 \
  --prefix prod-ai-reviewer

# Test alarm notification
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate
```

---

## Troubleshooting Runbooks

### High Error Rate Troubleshooting

**Symptoms**:
- Error rate exceeds 5%
- Users experiencing failures
- Increased 5xx responses

**Diagnostic Steps**:

1. **Check CloudWatch Logs**:
   ```bash
   aws logs tail /aws/lambda/ai-reviewer --follow --region us-east-1
   ```

2. **Identify Error Patterns**:
   - Check error types in logs
   - Identify affected endpoints
   - Review stack traces

3. **Check External Dependencies**:
   - GitHub API status
   - LLM provider status (OpenAI, Anthropic)
   - Database connectivity

4. **Review Recent Deployments**:
   - Check if error rate increased after deployment
   - Review recent code changes

**Resolution Steps**:

1. **Immediate**:
   - If deployment-related, rollback to previous version
   - If external API issue, enable circuit breaker fallback
   - Scale up instances if capacity issue

2. **Short-term**:
   - Fix identified bugs
   - Add error handling for edge cases
   - Improve input validation

3. **Long-term**:
   - Add more comprehensive error handling
   - Implement retry logic with exponential backoff
   - Add monitoring for specific error types

---

### High Response Time Troubleshooting

**Symptoms**:
- API P95 response time > 1 second
- Slow page loads
- Timeouts

**Diagnostic Steps**:

1. **Check Performance Dashboard**:
   - Review response time percentiles (P50, P95, P99)
   - Identify slow endpoints
   - Check request throughput

2. **Database Performance**:
   ```sql
   -- Check slow queries
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE mean_exec_time > 100
   ORDER BY mean_exec_time DESC
   LIMIT 20;
   ```

3. **Check Resource Utilization**:
   - CPU usage
   - Memory usage
   - Network I/O

4. **Review Application Traces**:
   - Use X-Ray distributed tracing
   - Identify bottlenecks in request flow

**Resolution Steps**:

1. **Immediate**:
   - Scale up instances
   - Increase connection pool size
   - Enable caching for frequently accessed data

2. **Short-term**:
   - Optimize slow database queries
   - Add database indexes
   - Implement query result caching

3. **Long-term**:
   - Refactor inefficient code
   - Implement asynchronous processing
   - Add CDN for static assets

---

### High CPU Utilization Troubleshooting

**Symptoms**:
- CPU usage > 80%
- Slow response times
- Auto-scaling triggered

**Diagnostic Steps**:

1. **Check CPU Metrics**:
   - Review CPU utilization trends
   - Identify peak usage times
   - Check per-instance CPU

2. **Profile Application**:
   ```python
   # Use cProfile for CPU profiling
   python -m cProfile -o profile.stats app.py
   ```

3. **Check Request Volume**:
   - Review request throughput
   - Identify CPU-intensive endpoints

**Resolution Steps**:

1. **Immediate**:
   - Scale up instances
   - Increase instance size (vertical scaling)

2. **Short-term**:
   - Optimize CPU-intensive operations
   - Implement caching
   - Use asynchronous processing for heavy tasks

3. **Long-term**:
   - Refactor algorithms for efficiency
   - Implement request queuing
   - Consider using specialized compute instances

---

### High Memory Utilization Troubleshooting

**Symptoms**:
- Memory usage > 85%
- Frequent garbage collection
- Out of memory errors

**Diagnostic Steps**:

1. **Check Memory Metrics**:
   - Review memory usage trends
   - Check for memory leaks

2. **Profile Memory Usage**:
   ```python
   # Use memory_profiler
   from memory_profiler import profile
   
   @profile
   def my_function():
       # Function code
       pass
   ```

3. **Check Cache Size**:
   - Review Redis memory usage
   - Check application-level caches

**Resolution Steps**:

1. **Immediate**:
   - Restart instances to clear memory
   - Reduce cache size
   - Scale up instances

2. **Short-term**:
   - Fix memory leaks
   - Implement proper object cleanup
   - Optimize data structures

3. **Long-term**:
   - Implement memory-efficient algorithms
   - Use streaming for large data processing
   - Increase instance memory

---

### High Disk Utilization Troubleshooting

**Symptoms**:
- Disk usage > 90%
- Write failures
- Application errors

**Diagnostic Steps**:

1. **Check Disk Usage**:
   ```bash
   df -h
   du -sh /* | sort -h
   ```

2. **Identify Large Files**:
   ```bash
   find / -type f -size +100M -exec ls -lh {} \;
   ```

3. **Check Log Files**:
   ```bash
   du -sh /var/log/*
   ```

**Resolution Steps**:

1. **Immediate**:
   - Clean up old log files
   - Remove temporary files
   - Compress large files

2. **Short-term**:
   - Implement log rotation
   - Set up automated cleanup
   - Archive old data

3. **Long-term**:
   - Increase disk size
   - Implement data retention policies
   - Use external storage (S3) for large files

---

## Testing Alarms

### Manual Testing

Test alarm notifications without waiting for actual threshold breaches:

```bash
# Test error rate alarm
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate

# Test response time alarm
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-response-time
```

### Automated Testing

Run the test suite to verify alarm configuration:

```bash
pytest backend/tests/test_cloudwatch_alarms.py -v
```

---

## Monitoring Best Practices

### 1. Alert Fatigue Prevention

- Set appropriate thresholds based on baseline metrics
- Use evaluation periods to avoid false positives
- Implement alert aggregation
- Review and tune alerts regularly

### 2. Runbook Maintenance

- Keep runbooks up to date
- Document resolution steps
- Include links to relevant dashboards
- Add contact information for escalation

### 3. Alert Response

- Acknowledge alerts promptly
- Document resolution steps
- Conduct post-incident reviews
- Update runbooks based on learnings

### 4. Metrics Collection

- Ensure all required metrics are being published
- Verify metric dimensions are correct
- Monitor metric publishing failures
- Set up alerts for missing metrics

---

## Integration with Dashboards

Alarms are designed to work with CloudWatch dashboards created in Task 39.1:

- **System Health Dashboard**: Shows error rates and uptime
- **Performance Dashboard**: Shows response times and resource utilization
- **Business Metrics Dashboard**: Shows analysis rates and user activity

Access dashboards:
```
https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:
```

---

## Cost Considerations

### CloudWatch Alarms Pricing

- First 10 alarms: Free
- Additional alarms: $0.10 per alarm per month
- SNS notifications: $0.50 per 1 million requests

**Estimated Monthly Cost** (7 alarms):
- Alarms: $0 (within free tier)
- SNS notifications: ~$0.01 (assuming 1000 notifications/month)
- **Total**: ~$0.01/month

---

## Compliance and Audit

### Requirements Validation

**Requirement 7.6**: Configure alerts for critical conditions

✅ **Acceptance Criteria 7.6.1**: Alert on error rate > 5%
- Implemented with 2-period evaluation (10 minutes)

✅ **Acceptance Criteria 7.6.2**: Alert on response time > 1s
- Implemented with P95 metric and 2-period evaluation

✅ **Acceptance Criteria 7.6.3**: Alert on CPU > 80%
- Implemented with 2-period evaluation (10 minutes)

✅ **Acceptance Criteria 7.6.4**: Send notifications via email
- Implemented via SNS email subscription

✅ **Acceptance Criteria 7.6.5**: Send notifications to Slack
- Implemented via SNS HTTPS endpoint

---

## Related Documentation

- [CloudWatch Dashboards README](./README.md)
- [Dashboard Quick Reference](./DASHBOARD_QUICK_REFERENCE.md)
- [Monitoring Module Variables](./variables.tf)
- [Monitoring Module Outputs](./outputs.tf)

---

## Support

For issues or questions:
- Check CloudWatch Logs for detailed error messages
- Review dashboards for metric trends
- Consult runbooks for common issues
- Escalate to on-call engineer if unresolved

---

## Changelog

### Version 1.0 (2024-01-15)
- Initial implementation of 7 CloudWatch alarms
- SNS topic integration for notifications
- Email and Slack notification support
- Comprehensive documentation and runbooks
- Automated testing suite
