# CloudWatch Dashboards Quick Reference

Quick reference guide for CloudWatch dashboards monitoring.

**Validates Requirements**: 18.2

## Dashboard URLs

After deployment, access dashboards at:

```
System Health:
https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name={env}-{service}-system-health

Performance:
https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name={env}-{service}-performance

Business Metrics:
https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name={env}-{service}-business-metrics
```

Replace `{region}`, `{env}`, and `{service}` with your values.

## Quick Commands

### Deploy Dashboards

```bash
# Using Terraform
cd terraform
terraform apply -target=module.monitoring

# Using Python script
python backend/scripts/manage_cloudwatch_dashboards.py create-all \
  --region us-east-1 \
  --environment prod
```

### List Dashboards

```bash
# AWS CLI
aws cloudwatch list-dashboards --region us-east-1

# Python script
python backend/scripts/manage_cloudwatch_dashboards.py list
```

### View Dashboard Configuration

```bash
# AWS CLI
aws cloudwatch get-dashboard \
  --dashboard-name prod-ai-reviewer-system-health \
  --region us-east-1

# Python script
python backend/scripts/manage_cloudwatch_dashboards.py get \
  --dashboard prod-ai-reviewer-system-health
```

### Delete Dashboard

```bash
# AWS CLI
aws cloudwatch delete-dashboards \
  --dashboard-names prod-ai-reviewer-system-health \
  --region us-east-1

# Python script
python backend/scripts/manage_cloudwatch_dashboards.py delete \
  --dashboard prod-ai-reviewer-system-health
```

## Key Metrics at a Glance

### System Health

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Uptime % | 99.5% | < 99.5% |
| Error Rate | < 5% | > 5% |
| Health Check Response | < 1s | > 1s |
| Active Sessions | - | - |

### Performance

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API P95 Response Time | < 500ms | > 500ms |
| Cache Hit Ratio | > 70% | < 70% |
| CPU Utilization | < 80% | > 80% for 10min |
| Memory Utilization | < 85% | > 85% for 10min |
| Disk Utilization | < 90% | > 90% |

### Business Metrics

| Metric | Description |
|--------|-------------|
| Analysis Completion Rate | Success vs failure count |
| Average Analysis Duration | Time by analysis type |
| User Activity | Logins and registrations |
| GitHub Webhook Processing | Webhook event success rate |
| LLM API Usage | Requests by provider |
| LLM Token Usage | Token consumption |

## Common Dashboard Tasks

### Check System Health

1. Open System Health dashboard
2. Verify uptime % is above 99.5%
3. Check error rate is below 5%
4. Confirm health checks are responding < 1s
5. Review active sessions for capacity

### Investigate Performance Issues

1. Open Performance dashboard
2. Check API response time percentiles
3. Review database query performance
4. Verify cache hit ratio > 70%
5. Check CPU/Memory/Disk utilization

### Monitor Business Metrics

1. Open Business Metrics dashboard
2. Review analysis completion rate
3. Check average analysis duration trends
4. Monitor user activity patterns
5. Track LLM API usage and costs

### Troubleshoot High Error Rate

1. Open System Health dashboard
2. Identify which endpoint has high errors
3. Check error rate percentage widget
4. Cross-reference with Performance dashboard
5. Review logs in CloudWatch Logs

### Investigate Slow Response Times

1. Open Performance dashboard
2. Check API response time percentiles
3. Identify if P95 > 500ms
4. Review database query performance
5. Check cache hit ratio
6. Verify CPU/Memory not saturated

## Widget Descriptions

### System Health Dashboard

**Uptime Percentage**
- Shows healthy vs unhealthy hosts
- Calculates uptime % with SLA target line
- Green fill above 99.5% target

**Error Rate by Endpoint**
- Tracks errors for each API endpoint
- Helps identify problematic endpoints
- 5-minute aggregation

**Overall Error Rate**
- Percentage of failed requests
- Red fill above 5% threshold
- Calculated from total errors / total requests

**Health Check Response Time**
- Average and P99 response times
- Orange fill above 1s threshold
- 1-minute granularity

**Database Connection Health**
- Active connections to PostgreSQL and Redis
- Helps identify connection pool issues

**Active User Sessions**
- Number of concurrent authenticated users
- Useful for capacity planning

### Performance Dashboard

**API Response Time Percentiles**
- P50, P95, P99 response times
- Orange fill above 500ms for P95
- 5-minute aggregation

**Request Throughput**
- Requests per second
- Calculated from total request count
- 1-minute granularity

**Database Query Performance**
- Average and P95 query times
- Separate metrics for PostgreSQL and Redis

**Cache Hit Ratio**
- Percentage of cache hits
- Orange fill below 70% target
- Value between 0 and 1

**CPU/Memory/Disk Utilization**
- Resource usage percentages
- Alert thresholds: CPU 80%, Memory 85%, Disk 90%
- Red fill above thresholds

### Business Metrics Dashboard

**Analysis Completion Rate**
- Successful vs failed analyses
- Hourly aggregation
- Stacked area chart

**Average Analysis Duration**
- Time by analysis type (AST, graph, LLM)
- Hourly aggregation
- Line chart

**User Activity**
- Logins and registrations
- Hourly aggregation
- Stacked area chart

**GitHub Webhook Processing**
- Successful vs failed webhook events
- Hourly aggregation

**LLM API Usage**
- Requests by provider and status
- Tracks OpenAI and Anthropic
- Shows success, error, rate limited

**LLM Token Usage**
- Prompt and completion tokens
- Useful for cost tracking
- Hourly aggregation

**Celery Task Queue**
- Queue length by queue name
- Helps identify processing bottlenecks
- 5-minute granularity

**Circular Dependencies Detected**
- Count by severity (high, medium, low)
- Hourly aggregation

## Alert Thresholds

### Critical (Immediate Action)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Uptime % | < 99.5% | Check ALB health checks |
| Error Rate | > 5% for 5min | Review error logs |
| Health Check | > 1s for 5min | Check service health |
| CPU | > 80% for 10min | Scale up or optimize |

### Warning (Monitor)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Cache Hit Ratio | < 70% | Review cache strategy |
| Memory | > 85% for 10min | Check for memory leaks |
| Disk | > 90% | Clean up or expand storage |
| API P95 | > 500ms | Optimize slow endpoints |

## Time Ranges

Dashboards support multiple time ranges:

- **1 hour**: Real-time monitoring
- **3 hours**: Recent trends
- **12 hours**: Half-day view
- **1 day**: Daily patterns
- **1 week**: Weekly trends
- **Custom**: Specific time range

Change time range using the dropdown in the top-right corner.

## Refresh Intervals

Dashboards auto-refresh at:

- **1 minute**: Real-time monitoring
- **5 minutes**: Default
- **15 minutes**: Reduced load
- **Manual**: Disable auto-refresh

Change refresh interval using the dropdown in the top-right corner.

## Exporting Data

### Export Dashboard Image

1. Open dashboard
2. Click "Actions" > "Export to PNG"
3. Save image for reports

### Export Metric Data

```bash
# Export metric data to CSV
aws cloudwatch get-metric-statistics \
  --namespace ai-reviewer \
  --metric-name http_request_duration_seconds \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average \
  --region us-east-1 \
  --output json > metrics.json
```

## Sharing Dashboards

### Share Dashboard Link

1. Open dashboard
2. Click "Actions" > "Share dashboard"
3. Copy link
4. Share with team members (requires AWS access)

### Create Dashboard Snapshot

Dashboards are defined as code in Terraform, making them:
- Version controlled
- Reproducible across environments
- Easy to share and modify

## Customization

### Add Custom Widget

Edit `terraform/modules/monitoring/main.tf`:

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

Then apply:

```bash
terraform apply -target=module.monitoring
```

### Modify Alert Threshold

Edit the `annotations` section:

```hcl
annotations = {
  horizontal = [
    {
      value = 99.5        # Change this value
      label = "SLA Target"
      fill  = "above"
      color = "#2ca02c"
    }
  ]
}
```

## Troubleshooting

### No Data in Widgets

**Check metrics are being published:**
```bash
aws cloudwatch list-metrics --namespace ai-reviewer
```

**Verify metric names match:**
- Check `backend/app/core/prometheus_metrics.py`
- Ensure labels match dashboard configuration

**Expand time range:**
- Try last 24 hours instead of 1 hour

### Missing Infrastructure Metrics

**Verify CloudWatch Agent is running:**
```bash
sudo systemctl status amazon-cloudwatch-agent
```

**Check agent configuration:**
```bash
cat /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

**Restart agent:**
```bash
sudo systemctl restart amazon-cloudwatch-agent
```

### Dashboard Not Found

**List available dashboards:**
```bash
aws cloudwatch list-dashboards --region us-east-1
```

**Recreate dashboard:**
```bash
terraform apply -target=module.monitoring
```

## Related Documentation

- [Full README](README.md) - Comprehensive documentation
- [CloudWatch Integration](../../../backend/CLOUDWATCH_INTEGRATION_README.md)
- [Prometheus Metrics](../../../backend/PROMETHEUS_METRICS_README.md)
- [Operations Runbook](../../../docs/operations/runbook.md)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Full README](README.md)
3. Contact DevOps team
