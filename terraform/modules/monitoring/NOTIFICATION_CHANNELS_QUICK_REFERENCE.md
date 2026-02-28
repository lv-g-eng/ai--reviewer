# Notification Channels Quick Reference

Quick commands and procedures for configuring CloudWatch notification channels.

## Quick Setup Commands

### Email Notification

```bash
# Configure email in Terraform
cd terraform
echo 'alert_email = "ops-team@example.com"' >> environments/prod/terraform.tfvars
terraform apply

# Or use Python script
python backend/scripts/configure_notification_channels.py setup-email \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --email ops-team@example.com

# Confirm subscription (check email inbox)
# Click "Confirm subscription" link in email from AWS Notifications
```

### Slack Notification

```bash
# 1. Create Slack webhook at https://api.slack.com/apps
# 2. Store webhook in Secrets Manager
aws secretsmanager create-secret \
  --name prod/ai-reviewer/slack-webhook \
  --secret-string "https://hooks.slack.com/services/T00/B00/XXX" \
  --region us-east-1

# 3. Configure in Terraform
cd terraform
terraform apply

# Or use Python script
python backend/scripts/configure_notification_channels.py setup-slack \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --webhook-url https://hooks.slack.com/services/T00/B00/XXX
```

## Quick Test Commands

```bash
# Test all notification channels
python backend/scripts/configure_notification_channels.py test \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts

# Test via AWS CLI
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --subject "TEST: CloudWatch Alarm" \
  --message "Test notification" \
  --region us-east-1

# Trigger actual alarm (then reset)
aws cloudwatch set-alarm-state \
  --alarm-name prod-ai-reviewer-high-error-rate \
  --state-value ALARM \
  --state-reason "Manual test" \
  --region us-east-1
```

## Quick Verification

```bash
# Verify configuration
python backend/scripts/configure_notification_channels.py verify \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts

# List subscriptions
python backend/scripts/configure_notification_channels.py list \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts

# Check subscription status via AWS CLI
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --region us-east-1
```

## Notification Channel Status

| Channel | Protocol | Confirmation Required | Auto-Active |
|---------|----------|----------------------|-------------|
| Email   | email    | ✅ Yes (via email)    | ❌ No       |
| Slack   | https    | ❌ No                 | ✅ Yes      |

## Common Issues

### Email Not Received

```bash
# Check subscription status
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --region us-east-1 \
  --query 'Subscriptions[?Protocol==`email`]'

# Look for "SubscriptionArn": "PendingConfirmation"
# Solution: Check spam folder, resend confirmation
terraform apply  # Resends confirmation email
```

### Slack Not Working

```bash
# Test webhook directly
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# If fails: Regenerate webhook in Slack, update Secrets Manager
aws secretsmanager update-secret \
  --secret-id prod/ai-reviewer/slack-webhook \
  --secret-string "NEW_WEBHOOK_URL" \
  --region us-east-1

terraform apply
```

## Environment-Specific Configuration

### Development
```hcl
alert_email = "dev-team@example.com"
slack_webhook_url = ""  # Optional
```

### Staging
```hcl
alert_email = "staging-alerts@example.com"
slack_webhook_url = data.aws_secretsmanager_secret_version.staging_slack.secret_string
```

### Production
```hcl
alert_email = "ops-team@example.com"
slack_webhook_url = data.aws_secretsmanager_secret_version.prod_slack.secret_string
```

## Notification Format Examples

### Email Format
```
Subject: ALARM: "prod-ai-reviewer-high-error-rate" in US East (N. Virginia)

State Change: OK -> ALARM
Reason: Threshold Crossed: 7.5% > 5.0%
Timestamp: 2024-01-15 10:15:23 UTC

View in Console: https://console.aws.amazon.com/cloudwatch/...
```

### Slack Format
```
🚨 CloudWatch Alarm: ALARM
Alarm: prod-ai-reviewer-high-error-rate
State: ALARM
Reason: Threshold Crossed: 7.5% > 5.0%
Time: 2024-01-15 10:15:23 UTC
```

## Terraform Module Usage

```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = "prod"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  # Notification channels
  alert_email       = "ops-team@example.com"
  slack_webhook_url = data.aws_secretsmanager_secret_version.slack.secret_string
  
  # Optional: Custom thresholds
  error_rate_threshold = 5
  cpu_threshold        = 80
}
```

## Python Script Commands

```bash
# Setup email
python backend/scripts/configure_notification_channels.py setup-email \
  --topic-arn ARN --email EMAIL

# Setup Slack
python backend/scripts/configure_notification_channels.py setup-slack \
  --topic-arn ARN --webhook-url URL

# List subscriptions
python backend/scripts/configure_notification_channels.py list \
  --topic-arn ARN

# Test notifications
python backend/scripts/configure_notification_channels.py test \
  --topic-arn ARN

# Verify configuration
python backend/scripts/configure_notification_channels.py verify \
  --topic-arn ARN
```

## Monitoring Notification Delivery

```bash
# Check SNS delivery metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/SNS \
  --metric-name NumberOfNotificationsDelivered \
  --dimensions Name=TopicName,Value=prod-ai-reviewer-alerts \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region us-east-1

# Check failed deliveries
aws cloudwatch get-metric-statistics \
  --namespace AWS/SNS \
  --metric-name NumberOfNotificationsFailed \
  --dimensions Name=TopicName,Value=prod-ai-reviewer-alerts \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

## Best Practices Checklist

- [ ] Use team distribution lists, not individual emails
- [ ] Store Slack webhooks in AWS Secrets Manager
- [ ] Test notifications after configuration
- [ ] Confirm email subscriptions within 3 days
- [ ] Monitor notification delivery metrics
- [ ] Document escalation procedures
- [ ] Set up separate channels for different severities
- [ ] Rotate webhook URLs periodically
- [ ] Use environment-specific notification channels
- [ ] Test notifications regularly (weekly/monthly)

## Related Documentation

- [NOTIFICATION_CHANNELS_SETUP.md](./NOTIFICATION_CHANNELS_SETUP.md) - Complete setup guide
- [ALERTS_README.md](./ALERTS_README.md) - Alarm documentation
- [ALERTS_QUICK_REFERENCE.md](./ALERTS_QUICK_REFERENCE.md) - Alarm quick reference

## Support Contacts

- **Email Issues**: Check spam folder, verify subscription status
- **Slack Issues**: Verify webhook URL, check Slack app status
- **AWS Issues**: Check CloudWatch Logs, SNS delivery logs

---

**Last Updated**: 2024-01-15  
**Version**: 1.0
