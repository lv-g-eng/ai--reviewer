# CloudWatch Alerts Quick Reference

Quick reference guide for CloudWatch alarms in the AI Reviewer system.

## Quick Commands

### Create All Alarms

```bash
# Using Python script
python backend/scripts/manage_cloudwatch_alarms.py create-all \
  --region us-east-1 \
  --environment prod \
  --email ops@example.com

# Using Terraform
cd terraform
terraform apply -target=module.monitoring
```

### List Alarms

```bash
python backend/scripts/manage_cloudwatch_alarms.py list \
  --region us-east-1 \
  --prefix prod-ai-reviewer
```

### Test Alarm

```bash
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate
```

### View Alarm Details

```bash
python backend/scripts/manage_cloudwatch_alarms.py describe \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate
```

---

## Alert Summary

| Alarm | Threshold | Period | Severity | Action |
|-------|-----------|--------|----------|--------|
| High Error Rate | > 5% | 10 min | Critical | Investigate logs, check external APIs |
| High Response Time | > 1s (P95) | 10 min | Critical | Check DB performance, scale instances |
| High CPU | > 80% | 10 min | Critical | Scale up, optimize code |
| High Memory | > 85% | 10 min | Warning | Check for leaks, restart instances |
| High Disk | > 90% | 5 min | Warning | Clean logs, archive data |
| DB Connection Failures | > 5 errors | 5 min | Critical | Check DB status, verify credentials |
| Health Check Failures | < 1 host | 2 min | Critical | Check app status, review deployment |

---

## Alarm States

- **OK**: Metric is within threshold
- **ALARM**: Metric has breached threshold
- **INSUFFICIENT_DATA**: Not enough data to evaluate

---

## Quick Troubleshooting

### High Error Rate

```bash
# Check recent errors
aws logs tail /aws/lambda/ai-reviewer --follow --filter-pattern "ERROR"

# Check error rate by endpoint
aws cloudwatch get-metric-statistics \
  --namespace ai-reviewer \
  --metric-name http_errors_total \
  --dimensions Name=endpoint,Value=/api/v1/projects \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### High Response Time

```bash
# Check slow queries
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;"

# Check API response times
aws cloudwatch get-metric-statistics \
  --namespace ai-reviewer \
  --metric-name http_request_duration_seconds \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics p95
```

### High CPU

```bash
# Check CPU usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=prod-ai-reviewer-asg \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Scale up instances
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name prod-ai-reviewer-asg \
  --desired-capacity 5
```

### High Memory

```bash
# Check memory usage
aws cloudwatch get-metric-statistics \
  --namespace CWAgent \
  --metric-name mem_used_percent \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Restart instances (rolling restart)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name prod-ai-reviewer-asg
```

### High Disk

```bash
# Check disk usage on instance
ssh ec2-user@$INSTANCE_IP "df -h"

# Clean up logs
ssh ec2-user@$INSTANCE_IP "sudo find /var/log -name '*.log' -mtime +7 -delete"

# Check largest files
ssh ec2-user@$INSTANCE_IP "sudo du -sh /* | sort -h | tail -10"
```

---

## Notification Channels

### Email

Configured via `alert_email` variable. Requires email confirmation.

### Slack

Configured via `slack_webhook_url` variable. Format:
```
https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Dashboard Links

Access CloudWatch dashboards:

```
System Health:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=prod-ai-reviewer-system-health

Performance:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=prod-ai-reviewer-performance

Business Metrics:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=prod-ai-reviewer-business-metrics
```

---

## Common Issues

### Alarm Not Triggering

1. Check metric is being published:
   ```bash
   aws cloudwatch list-metrics --namespace ai-reviewer
   ```

2. Verify alarm configuration:
   ```bash
   aws cloudwatch describe-alarms --alarm-names prod-ai-reviewer-high-error-rate
   ```

3. Check evaluation periods and threshold

### Too Many False Positives

1. Increase evaluation periods
2. Adjust threshold based on baseline
3. Use anomaly detection instead of static threshold

### Missing Notifications

1. Verify SNS subscription is confirmed
2. Check SNS topic permissions
3. Test notification manually:
   ```bash
   python backend/scripts/manage_cloudwatch_alarms.py test \
     --region us-east-1 \
     --alarm-name prod-ai-reviewer-high-error-rate
   ```

---

## Escalation

### Severity Levels

- **Critical**: Immediate response required (< 15 minutes)
- **Warning**: Response within 1 hour

### On-Call Rotation

Check PagerDuty or on-call schedule for current on-call engineer.

### Escalation Path

1. On-call engineer
2. Team lead
3. Engineering manager
4. CTO

---

## Metrics Reference

### Application Metrics

| Metric | Namespace | Description |
|--------|-----------|-------------|
| http_requests_total | ai-reviewer | Total HTTP requests |
| http_errors_total | ai-reviewer | Total HTTP errors |
| http_request_duration_seconds | ai-reviewer | Request duration |
| database_connection_errors | ai-reviewer | DB connection failures |
| cache_hit_ratio | ai-reviewer | Cache hit percentage |

### AWS Metrics

| Metric | Namespace | Description |
|--------|-----------|-------------|
| CPUUtilization | AWS/EC2 | CPU usage percentage |
| HealthyHostCount | AWS/ApplicationELB | Healthy hosts |
| TargetResponseTime | AWS/ApplicationELB | Response time |
| mem_used_percent | CWAgent | Memory usage |
| disk_used_percent | CWAgent | Disk usage |

---

## Testing

### Run Tests

```bash
pytest backend/tests/test_cloudwatch_alarms.py -v
```

### Manual Test

```bash
# Trigger test alarm
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate

# Check notification received
# Verify email or Slack message
```

---

## Maintenance

### Weekly Tasks

- Review alarm states
- Check for false positives
- Verify notifications working
- Update thresholds if needed

### Monthly Tasks

- Review alarm effectiveness
- Update runbooks
- Analyze alarm trends
- Optimize thresholds

### Quarterly Tasks

- Conduct alarm testing
- Review escalation procedures
- Update contact information
- Train new team members

---

## Related Documentation

- [Detailed Alerts Documentation](./ALERTS_README.md)
- [CloudWatch Dashboards](./README.md)
- [Monitoring Module](./main.tf)

---

## Quick Links

- [AWS CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
- [SNS Topics](https://console.aws.amazon.com/sns/v3/home#/topics)
- [EC2 Auto Scaling](https://console.aws.amazon.com/ec2/autoscaling/)
- [RDS Instances](https://console.aws.amazon.com/rds/)
