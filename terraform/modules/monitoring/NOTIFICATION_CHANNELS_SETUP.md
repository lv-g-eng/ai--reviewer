# CloudWatch Notification Channels Setup Guide

## Overview

This guide provides step-by-step instructions for configuring notification channels for CloudWatch alarms. The monitoring module supports two notification channels:

1. **Email Notifications** - Direct email alerts via Amazon SNS
2. **Slack Notifications** - Real-time alerts to Slack channels via webhook

Both channels are integrated with the SNS topic created in Task 40.1 and will receive notifications for all CloudWatch alarms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Email Notification Setup](#email-notification-setup)
- [Slack Notification Setup](#slack-notification-setup)
- [Terraform Configuration](#terraform-configuration)
- [Testing Notifications](#testing-notifications)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Prerequisites

Before configuring notification channels, ensure you have:

- ✅ AWS account with appropriate permissions (SNS, CloudWatch)
- ✅ Terraform installed (version >= 1.0)
- ✅ AWS CLI configured with credentials
- ✅ CloudWatch alarms created (Task 40.1)
- ✅ For Slack: Admin access to your Slack workspace

## Email Notification Setup

### Step 1: Choose Email Address

Decide which email address(es) should receive alerts:

**Options**:
- **Individual email**: `ops-engineer@example.com`
- **Team distribution list**: `ops-team@example.com`
- **Ticketing system**: `alerts@ticketing.example.com`

**Recommendation**: Use a team distribution list or shared inbox to ensure alerts are seen even when individuals are unavailable.

### Step 2: Configure Terraform Variable

Add the email address to your Terraform configuration:

**Option A: In terraform.tfvars**
```hcl
# terraform/environments/prod/terraform.tfvars
alert_email = "ops-team@example.com"
```

**Option B: As environment variable**
```bash
export TF_VAR_alert_email="ops-team@example.com"
```

**Option C: In module call**
```hcl
module "monitoring" {
  source = "./modules/monitoring"
  
  environment  = "prod"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  alert_email  = "ops-team@example.com"
  
  # ... other variables
}
```

### Step 3: Apply Terraform Configuration

```bash
cd terraform
terraform plan
terraform apply
```

This will create:
- SNS topic: `prod-ai-reviewer-alerts`
- SNS email subscription (pending confirmation)

### Step 4: Confirm Email Subscription

**Important**: Email subscriptions require confirmation!

1. Check the inbox for the email address you configured
2. Look for an email from "AWS Notifications" with subject: "AWS Notification - Subscription Confirmation"
3. Click the "Confirm subscription" link in the email
4. You should see a confirmation page: "Subscription confirmed!"

**Troubleshooting**:
- Check spam/junk folder if email not received
- Subscription expires after 3 days if not confirmed
- Re-run `terraform apply` to resend confirmation email

### Step 5: Verify Email Subscription

Check subscription status:

```bash
# List SNS subscriptions
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --region us-east-1

# Look for:
# "SubscriptionArn": "arn:aws:sns:..." (confirmed)
# "SubscriptionArn": "PendingConfirmation" (not confirmed yet)
```

### Email Notification Format

Once configured, you'll receive emails like this:

```
Subject: ALARM: "prod-ai-reviewer-high-error-rate" in US East (N. Virginia)

You are receiving this email because your Amazon CloudWatch Alarm 
"prod-ai-reviewer-high-error-rate" in the US East (N. Virginia) 
region has entered the ALARM state.

Alarm Details:
- State Change: OK -> ALARM
- Reason: Threshold Crossed: 1 datapoint [7.5 (15/01/24 10:15:00)] 
  was greater than the threshold (5.0).
- Timestamp: Monday 15 January, 2024 10:15:23 UTC

Alarm Description:
Alert when error rate exceeds 5% for 5 minutes

View this alarm in the AWS Management Console:
https://console.aws.amazon.com/cloudwatch/...
```

## Slack Notification Setup

### Step 1: Create Slack Incoming Webhook

1. **Go to Slack App Directory**
   - Visit: https://api.slack.com/apps
   - Click "Create New App" → "From scratch"

2. **Configure App**
   - App Name: `CloudWatch Alerts`
   - Workspace: Select your workspace
   - Click "Create App"

3. **Enable Incoming Webhooks**
   - In the left sidebar, click "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to ON
   - Click "Add New Webhook to Workspace"

4. **Select Channel**
   - Choose the channel for alerts (e.g., `#production-alerts`)
   - Click "Allow"

5. **Copy Webhook URL**
   - You'll see a webhook URL like:
     ```
     https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
     ```
   - **Keep this URL secure!** It allows posting to your Slack channel.

### Step 2: Store Webhook URL Securely

**Option A: AWS Secrets Manager (Recommended for Production)**

```bash
# Store webhook URL in Secrets Manager
aws secretsmanager create-secret \
  --name prod/ai-reviewer/slack-webhook \
  --description "Slack webhook URL for CloudWatch alerts" \
  --secret-string "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX" \
  --region us-east-1

# Retrieve webhook URL
aws secretsmanager get-secret-value \
  --secret-id prod/ai-reviewer/slack-webhook \
  --region us-east-1 \
  --query SecretString \
  --output text
```

**Option B: Environment Variable (Development/Staging)**

```bash
export TF_VAR_slack_webhook_url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
```

**Option C: Terraform Variables File (Not Recommended - Security Risk)**

```hcl
# terraform/environments/prod/terraform.tfvars
# WARNING: Do not commit this file to version control!
slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
```

### Step 3: Configure Terraform with Secrets Manager

**Best Practice**: Retrieve webhook from Secrets Manager in Terraform:

```hcl
# terraform/main.tf or terraform/environments/prod/main.tf

# Data source to retrieve Slack webhook from Secrets Manager
data "aws_secretsmanager_secret_version" "slack_webhook" {
  secret_id = "prod/ai-reviewer/slack-webhook"
}

module "monitoring" {
  source = "./modules/monitoring"
  
  environment        = "prod"
  service_name       = "ai-reviewer"
  aws_region         = "us-east-1"
  
  alert_email        = "ops-team@example.com"
  slack_webhook_url  = data.aws_secretsmanager_secret_version.slack_webhook.secret_string
  
  # ... other variables
}
```

### Step 4: Apply Terraform Configuration

```bash
cd terraform
terraform plan
terraform apply
```

This will create an SNS HTTPS subscription to your Slack webhook.

### Step 5: Verify Slack Subscription

**Note**: Slack webhooks via SNS do NOT require confirmation. They are automatically active.

Check subscription status:

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --region us-east-1 \
  --query 'Subscriptions[?Protocol==`https`]'
```

### Slack Notification Format

Slack notifications will appear in your configured channel:

```
🚨 CloudWatch Alarm: ALARM

Alarm Name: prod-ai-reviewer-high-error-rate
State: ALARM
Region: us-east-1
Time: 2024-01-15 10:15:23 UTC

Reason: Threshold Crossed: 1 datapoint [7.5] was greater than threshold (5.0)

Description: Alert when error rate exceeds 5% for 5 minutes

View in Console: https://console.aws.amazon.com/cloudwatch/...
```

### Step 6: Customize Slack Notifications (Optional)

For better formatting, you can use AWS Lambda to transform SNS messages:

```python
# lambda/slack_formatter.py
import json
import urllib.request

def lambda_handler(event, context):
    """Transform SNS alarm to formatted Slack message"""
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    # Extract alarm details
    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    timestamp = message['StateChangeTime']
    
    # Choose emoji based on state
    emoji = "🚨" if new_state == "ALARM" else "✅"
    color = "danger" if new_state == "ALARM" else "good"
    
    # Format Slack message
    slack_message = {
        "text": f"{emoji} CloudWatch Alarm: {new_state}",
        "attachments": [{
            "color": color,
            "fields": [
                {"title": "Alarm Name", "value": alarm_name, "short": True},
                {"title": "State", "value": new_state, "short": True},
                {"title": "Reason", "value": reason, "short": False},
                {"title": "Time", "value": timestamp, "short": True}
            ]
        }]
    }
    
    # Send to Slack webhook
    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(slack_message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)
    
    return {'statusCode': 200}
```

## Terraform Configuration

### Complete Example

```hcl
# terraform/environments/prod/main.tf

terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/ai-reviewer/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

# Retrieve Slack webhook from Secrets Manager
data "aws_secretsmanager_secret_version" "slack_webhook" {
  secret_id = "prod/ai-reviewer/slack-webhook"
}

# Monitoring module with notification channels
module "monitoring" {
  source = "../../modules/monitoring"
  
  # Environment configuration
  environment  = "prod"
  service_name = "ai-reviewer"
  aws_region   = "us-east-1"
  
  # Notification channels
  alert_email       = "ops-team@example.com"
  slack_webhook_url = data.aws_secretsmanager_secret_version.slack_webhook.secret_string
  
  # Optional: Auto Scaling Group for CPU alarms
  autoscaling_group_name = "prod-ai-reviewer-asg"
  
  # Optional: Enable/disable alarms
  enable_alarms = true
  
  # Optional: Custom thresholds
  error_rate_threshold    = 5
  response_time_threshold = 1.0
  cpu_threshold           = 80
  memory_threshold        = 85
  disk_threshold          = 90
  
  tags = {
    Environment = "prod"
    Project     = "ai-reviewer"
    ManagedBy   = "terraform"
  }
}

# Outputs
output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = module.monitoring.sns_topic_arn
}

output "alarm_names" {
  description = "Names of all CloudWatch alarms"
  value       = module.monitoring.alarm_names
}
```

### Environment-Specific Configuration

**Development Environment**:
```hcl
# terraform/environments/dev/terraform.tfvars
environment             = "dev"
service_name            = "ai-reviewer"
aws_region              = "us-east-1"
alert_email             = "dev-team@example.com"
slack_webhook_url       = ""  # Optional for dev
enable_alarms           = true
error_rate_threshold    = 10  # More lenient for dev
```

**Staging Environment**:
```hcl
# terraform/environments/staging/terraform.tfvars
environment             = "staging"
service_name            = "ai-reviewer"
aws_region              = "us-east-1"
alert_email             = "staging-alerts@example.com"
slack_webhook_url       = var.staging_slack_webhook
enable_alarms           = true
error_rate_threshold    = 7
```

**Production Environment**:
```hcl
# terraform/environments/prod/terraform.tfvars
environment             = "prod"
service_name            = "ai-reviewer"
aws_region              = "us-east-1"
alert_email             = "ops-team@example.com"
# slack_webhook_url retrieved from Secrets Manager
enable_alarms           = true
error_rate_threshold    = 5  # Strict for production
```

## Testing Notifications

### Test Email Notifications

**Method 1: Using AWS CLI**

```bash
# Publish test message to SNS topic
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --subject "TEST: CloudWatch Alarm Notification" \
  --message "This is a test notification. Please ignore." \
  --region us-east-1
```

**Method 2: Using Python Script**

```bash
# Use the management script from Task 40.1
python backend/scripts/manage_cloudwatch_alarms.py test \
  --region us-east-1 \
  --alarm-name prod-ai-reviewer-high-error-rate
```

**Method 3: Trigger Actual Alarm**

```bash
# Temporarily set alarm to ALARM state
aws cloudwatch set-alarm-state \
  --alarm-name prod-ai-reviewer-high-error-rate \
  --state-value ALARM \
  --state-reason "Manual test of notification channels" \
  --region us-east-1

# Wait for notification (should arrive within 1 minute)

# Reset alarm to OK state
aws cloudwatch set-alarm-state \
  --alarm-name prod-ai-reviewer-high-error-rate \
  --state-value OK \
  --state-reason "Test complete" \
  --region us-east-1
```

### Test Slack Notifications

**Method 1: Direct Webhook Test**

```bash
# Test Slack webhook directly
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🧪 Test notification from CloudWatch Alarms",
    "attachments": [{
      "color": "warning",
      "fields": [
        {"title": "Test Type", "value": "Manual Test", "short": true},
        {"title": "Status", "value": "Success", "short": true}
      ]
    }]
  }' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Method 2: Via SNS Topic**

```bash
# Publish test message to SNS (will forward to Slack)
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
  --message "Test Slack notification via SNS" \
  --region us-east-1
```

### Verify Notification Delivery

**Email Verification Checklist**:
- [ ] Email received within 1 minute
- [ ] Subject line contains alarm name
- [ ] Email body contains alarm details
- [ ] Links to AWS Console work
- [ ] Email not in spam folder

**Slack Verification Checklist**:
- [ ] Message appears in correct channel
- [ ] Message received within 1 minute
- [ ] Message formatting is readable
- [ ] Emoji/icons display correctly
- [ ] Links work (if included)

## Troubleshooting

### Email Notifications Not Received

**Problem**: Email subscription created but no emails received

**Diagnostic Steps**:

1. **Check subscription status**:
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
     --region us-east-1
   ```
   
   Look for `"SubscriptionArn": "PendingConfirmation"` - subscription not confirmed

2. **Check spam/junk folder**: AWS emails often flagged as spam

3. **Verify email address**: Check for typos in terraform.tfvars

4. **Check SNS delivery logs**:
   ```bash
   aws sns get-subscription-attributes \
     --subscription-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts:SUBSCRIPTION_ID \
     --region us-east-1
   ```

**Solutions**:

- **Resend confirmation email**: Re-run `terraform apply`
- **Whitelist AWS emails**: Add `no-reply@sns.amazonaws.com` to safe senders
- **Use different email**: Try a different email provider
- **Check email quotas**: Ensure email account not over quota

### Slack Notifications Not Received

**Problem**: Slack webhook configured but no messages in channel

**Diagnostic Steps**:

1. **Test webhook directly**:
   ```bash
   curl -X POST \
     -H 'Content-Type: application/json' \
     -d '{"text": "Test"}' \
     YOUR_WEBHOOK_URL
   ```
   
   If this fails, webhook URL is invalid or revoked

2. **Check SNS subscription**:
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:prod-ai-reviewer-alerts \
     --region us-east-1 \
     --query 'Subscriptions[?Protocol==`https`]'
   ```

3. **Check CloudWatch Logs** (if using Lambda formatter):
   ```bash
   aws logs tail /aws/lambda/slack-formatter --follow
   ```

**Solutions**:

- **Regenerate webhook**: Create new webhook in Slack, update Secrets Manager
- **Check webhook permissions**: Ensure webhook not revoked in Slack
- **Verify HTTPS endpoint**: SNS requires HTTPS, not HTTP
- **Check Slack app status**: Ensure app not disabled in workspace

### Notifications Delayed

**Problem**: Notifications arrive several minutes late

**Diagnostic Steps**:

1. **Check alarm evaluation periods**:
   ```bash
   aws cloudwatch describe-alarms \
     --alarm-names prod-ai-reviewer-high-error-rate \
     --region us-east-1 \
     --query 'MetricAlarms[0].[EvaluationPeriods,Period]'
   ```

2. **Check SNS delivery metrics**:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/SNS \
     --metric-name NumberOfNotificationsFailed \
     --dimensions Name=TopicName,Value=prod-ai-reviewer-alerts \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Sum \
     --region us-east-1
   ```

**Solutions**:

- **Reduce evaluation periods**: Change from 2 periods to 1 (faster but more false positives)
- **Reduce period duration**: Change from 5 minutes to 1 minute
- **Check SNS throttling**: Ensure not hitting SNS rate limits

### Too Many Notifications (Alert Fatigue)

**Problem**: Receiving too many alerts, team ignoring them

**Solutions**:

1. **Increase thresholds**: Make alarms less sensitive
   ```hcl
   error_rate_threshold = 10  # Instead of 5
   cpu_threshold = 90         # Instead of 80
   ```

2. **Increase evaluation periods**: Require sustained issues
   ```hcl
   evaluation_periods = 3  # Instead of 2
   ```

3. **Add alarm suppression**: Use CloudWatch Composite Alarms
   ```hcl
   resource "aws_cloudwatch_composite_alarm" "critical_only" {
     alarm_name = "critical-alerts-only"
     alarm_rule = "ALARM(high-error-rate) AND ALARM(high-response-time)"
   }
   ```

4. **Implement on-call schedule**: Use PagerDuty for critical alerts only

5. **Create alert severity levels**:
   - **Critical**: Page on-call engineer immediately
   - **Warning**: Email only, review during business hours
   - **Info**: Log only, no notification

## Best Practices

### 1. Use Multiple Notification Channels

**Why**: Redundancy ensures alerts are received even if one channel fails

**Implementation**:
```hcl
alert_email       = "ops-team@example.com"
slack_webhook_url = var.slack_webhook_url
# Future: Add PagerDuty, OpsGenie, etc.
```

### 2. Separate Channels by Severity

**Why**: Reduce alert fatigue by routing based on urgency

**Implementation**:
```hcl
# Critical alarms -> PagerDuty + Slack
resource "aws_sns_topic" "critical_alerts" {
  name = "${var.environment}-critical-alerts"
}

# Warning alarms -> Email + Slack
resource "aws_sns_topic" "warning_alerts" {
  name = "${var.environment}-warning-alerts"
}

# Info alarms -> Email only
resource "aws_sns_topic" "info_alerts" {
  name = "${var.environment}-info-alerts"
}
```

### 3. Use Team Distribution Lists

**Why**: Ensures alerts reach multiple people, not just one individual

**Good**:
- `ops-team@example.com` (distribution list)
- `#production-alerts` (Slack channel with multiple members)

**Bad**:
- `john.doe@example.com` (single person)
- `@john.doe` (Slack DM)

### 4. Secure Webhook URLs

**Why**: Webhook URLs allow posting to your Slack channel - treat as secrets

**Best Practices**:
- ✅ Store in AWS Secrets Manager
- ✅ Rotate webhooks periodically
- ✅ Use separate webhooks per environment
- ❌ Never commit to version control
- ❌ Never log webhook URLs
- ❌ Never share via email/chat

### 5. Test Notifications Regularly

**Why**: Ensure notification channels work when you need them

**Schedule**:
- **Weekly**: Automated test notification
- **Monthly**: Manual test of all channels
- **After changes**: Test immediately after configuration changes

**Automation**:
```bash
# Add to cron or CloudWatch Events
0 9 * * 1 /usr/local/bin/test-notifications.sh  # Every Monday at 9 AM
```

### 6. Document Escalation Procedures

**Why**: Team needs to know what to do when alerts fire

**Example Runbook**:
```markdown
## Alert Response Procedure

### 1. Acknowledge Alert (< 5 minutes)
- Respond in Slack thread: "Investigating"
- Check CloudWatch dashboard for context

### 2. Assess Severity (< 10 minutes)
- Is service down? → Escalate to on-call manager
- Is performance degraded? → Continue investigation
- Is this a false alarm? → Document and tune threshold

### 3. Investigate Root Cause (< 30 minutes)
- Check application logs
- Check infrastructure metrics
- Check recent deployments

### 4. Resolve or Escalate (< 1 hour)
- If resolved: Document resolution in Slack
- If not resolved: Escalate to senior engineer
- If critical: Initiate incident response

### 5. Post-Mortem (within 24 hours)
- Document root cause
- Implement preventive measures
- Update runbooks
```

### 7. Monitor Notification Delivery

**Why**: Ensure notifications are actually being delivered

**Metrics to Track**:
```bash
# SNS delivery success rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/SNS \
  --metric-name NumberOfNotificationsDelivered \
  --dimensions Name=TopicName,Value=prod-ai-reviewer-alerts \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

**Create Alarm for Failed Notifications**:
```hcl
resource "aws_cloudwatch_metric_alarm" "sns_delivery_failures" {
  alarm_name          = "${var.environment}-sns-delivery-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "NumberOfNotificationsFailed"
  namespace           = "AWS/SNS"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when SNS notifications fail to deliver"
  
  dimensions = {
    TopicName = aws_sns_topic.alerts.name
  }
  
  # Send to different channel to avoid circular dependency
  alarm_actions = [aws_sns_topic.meta_alerts.arn]
}
```

### 8. Implement Quiet Hours (Optional)

**Why**: Reduce non-critical alerts during off-hours

**Implementation**:
```python
# Lambda function to filter notifications by time
import json
from datetime import datetime

def lambda_handler(event, context):
    """Filter notifications based on time and severity"""
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    alarm_name = message['AlarmName']
    
    # Check if critical alarm (always send)
    if 'critical' in alarm_name.lower():
        return forward_to_slack(message)
    
    # Check time (only send warnings during business hours)
    now = datetime.utcnow()
    if 9 <= now.hour < 18 and now.weekday() < 5:  # 9 AM - 6 PM, Mon-Fri
        return forward_to_slack(message)
    
    # Suppress non-critical alerts outside business hours
    return {'statusCode': 200, 'body': 'Suppressed'}
```

## Next Steps

After configuring notification channels:

1. **Test All Channels**: Verify email and Slack notifications work
2. **Document Procedures**: Create runbooks for alert response
3. **Train Team**: Ensure team knows how to respond to alerts
4. **Monitor Delivery**: Track notification success rates
5. **Tune Thresholds**: Adjust based on baseline metrics to reduce false positives
6. **Implement On-Call**: Set up rotation for critical alerts
7. **Review Regularly**: Monthly review of alert effectiveness

## Related Documentation

- [ALERTS_README.md](./ALERTS_README.md) - Comprehensive alarm documentation
- [ALERTS_QUICK_REFERENCE.md](./ALERTS_QUICK_REFERENCE.md) - Quick reference guide
- [DASHBOARD_QUICK_REFERENCE.md](./DASHBOARD_QUICK_REFERENCE.md) - Dashboard guide
- [README.md](./README.md) - Monitoring module overview

## Support

For issues or questions:
- **Terraform Issues**: Check `terraform plan` output for errors
- **AWS Issues**: Check CloudWatch Logs and SNS delivery logs
- **Slack Issues**: Verify webhook URL in Slack app settings
- **Email Issues**: Check spam folder and subscription status

---

**Last Updated**: 2024-01-15  
**Version**: 1.0  
**Maintained By**: DevOps Team
