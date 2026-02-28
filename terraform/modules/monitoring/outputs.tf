# Outputs for CloudWatch Dashboards Module

output "system_health_dashboard_arn" {
  description = "ARN of the System Health dashboard"
  value       = aws_cloudwatch_dashboard.system_health.dashboard_arn
}

output "system_health_dashboard_name" {
  description = "Name of the System Health dashboard"
  value       = aws_cloudwatch_dashboard.system_health.dashboard_name
}

output "performance_dashboard_arn" {
  description = "ARN of the Performance Metrics dashboard"
  value       = aws_cloudwatch_dashboard.performance.dashboard_arn
}

output "performance_dashboard_name" {
  description = "Name of the Performance Metrics dashboard"
  value       = aws_cloudwatch_dashboard.performance.dashboard_name
}

output "business_metrics_dashboard_arn" {
  description = "ARN of the Business Metrics dashboard"
  value       = aws_cloudwatch_dashboard.business_metrics.dashboard_arn
}

output "business_metrics_dashboard_name" {
  description = "Name of the Business Metrics dashboard"
  value       = aws_cloudwatch_dashboard.business_metrics.dashboard_name
}

output "dashboard_urls" {
  description = "URLs to access the CloudWatch dashboards"
  value = {
    system_health     = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.system_health.dashboard_name}"
    performance       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.performance.dashboard_name}"
    business_metrics  = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.business_metrics.dashboard_name}"
  }
}

# Alarm Outputs

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alert notifications"
  value       = aws_sns_topic.alerts.arn
}

output "sns_topic_name" {
  description = "Name of the SNS topic for alert notifications"
  value       = aws_sns_topic.alerts.name
}

output "alarm_arns" {
  description = "ARNs of all CloudWatch alarms"
  value = {
    high_error_rate              = aws_cloudwatch_metric_alarm.high_error_rate.arn
    high_response_time           = aws_cloudwatch_metric_alarm.high_response_time.arn
    high_cpu_utilization         = aws_cloudwatch_metric_alarm.high_cpu_utilization.arn
    high_memory_utilization      = aws_cloudwatch_metric_alarm.high_memory_utilization.arn
    high_disk_utilization        = aws_cloudwatch_metric_alarm.high_disk_utilization.arn
    database_connection_failures = aws_cloudwatch_metric_alarm.database_connection_failures.arn
    health_check_failures        = aws_cloudwatch_metric_alarm.health_check_failures.arn
  }
}

output "alarm_names" {
  description = "Names of all CloudWatch alarms"
  value = {
    high_error_rate              = aws_cloudwatch_metric_alarm.high_error_rate.alarm_name
    high_response_time           = aws_cloudwatch_metric_alarm.high_response_time.alarm_name
    high_cpu_utilization         = aws_cloudwatch_metric_alarm.high_cpu_utilization.alarm_name
    high_memory_utilization      = aws_cloudwatch_metric_alarm.high_memory_utilization.alarm_name
    high_disk_utilization        = aws_cloudwatch_metric_alarm.high_disk_utilization.alarm_name
    database_connection_failures = aws_cloudwatch_metric_alarm.database_connection_failures.alarm_name
    health_check_failures        = aws_cloudwatch_metric_alarm.health_check_failures.alarm_name
  }
}
