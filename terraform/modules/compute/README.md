# Compute Module

This module provisions the compute infrastructure for the AI-Based Code Reviewer platform, including EC2 Auto Scaling Groups and Application Load Balancer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Application Load     │
              │ Balancer (ALB)       │
              │ - SSL/TLS Termination│
              │ - Health Checks      │
              └──────────┬───────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│ Auto Scaling    │            │ Auto Scaling    │
│ Group - AZ1     │            │ Group - AZ2     │
│                 │            │                 │
│ ┌─────────────┐ │            │ ┌─────────────┐ │
│ │ EC2 Instance│ │            │ │ EC2 Instance│ │
│ │ t3.large    │ │            │ │ t3.large    │ │
│ │ - FastAPI   │ │            │ │ - FastAPI   │ │
│ │ - React     │ │            │ │ - React     │ │
│ │ - Docker    │ │            │ │ - Docker    │ │
│ └─────────────┘ │            │ └─────────────┘ │
└─────────────────┘            └─────────────────┘
```

## Features

### Auto Scaling Group
- **Multi-AZ Deployment**: Instances distributed across multiple availability zones
- **Auto Scaling**: Scales from 2 to 10 instances based on CPU utilization
- **Health Checks**: ELB health checks with 300s grace period
- **Launch Template**: Versioned configuration for consistent deployments
- **CloudWatch Metrics**: Comprehensive metrics collection

### Application Load Balancer
- **SSL/TLS Termination**: HTTPS support with configurable certificates
- **HTTP to HTTPS Redirect**: Automatic redirect for security
- **Health Checks**: Application-level health monitoring
- **Cross-Zone Load Balancing**: Even distribution across AZs
- **Sticky Sessions**: Session affinity with cookie-based stickiness

### Security
- **IAM Roles**: Least privilege access for EC2 instances
- **IMDSv2**: Enforced metadata service v2 for enhanced security
- **Security Groups**: Network-level access control
- **CloudWatch Logs**: Centralized logging for audit and troubleshooting

### Monitoring
- **CloudWatch Agent**: System and application metrics
- **Auto Scaling Metrics**: Group capacity and health metrics
- **CloudWatch Alarms**: CPU-based scaling triggers
- **Access Logs**: Optional ALB access logging

## Usage

```hcl
module "compute" {
  source = "./modules/compute"

  project_name   = "ai-code-reviewer"
  environment    = "prod"
  aws_region     = "us-east-1"
  
  # Network Configuration
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  
  # Security Groups
  app_security_group_id = module.security.app_security_group_id
  alb_security_group_id = module.security.alb_security_group_id
  
  # Instance Configuration
  instance_type      = "t3.large"
  min_instances      = 2
  max_instances      = 10
  desired_instances  = 2
  
  # SSL Configuration
  ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
  
  # Monitoring
  enable_detailed_monitoring = true
  enable_alb_logs           = true
  alb_logs_bucket           = "my-alb-logs-bucket"
  
  tags = {
    Team = "Platform"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Name of the project | string | - | yes |
| environment | Environment name (dev, staging, prod) | string | - | yes |
| aws_region | AWS region | string | - | yes |
| vpc_id | VPC ID | string | - | yes |
| public_subnet_ids | Public subnet IDs for ALB | list(string) | - | yes |
| private_subnet_ids | Private subnet IDs for EC2 | list(string) | - | yes |
| app_security_group_id | Security group for app servers | string | - | yes |
| alb_security_group_id | Security group for ALB | string | - | yes |
| instance_type | EC2 instance type | string | "t3.large" | no |
| min_instances | Minimum instances | number | 2 | no |
| max_instances | Maximum instances | number | 10 | no |
| desired_instances | Desired instances | number | 2 | no |
| enable_detailed_monitoring | Enable detailed monitoring | bool | true | no |
| ssl_certificate_arn | SSL certificate ARN | string | "" | no |
| alb_logs_bucket | S3 bucket for ALB logs | string | "" | no |
| enable_alb_logs | Enable ALB access logs | bool | false | no |
| tags | Additional tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| autoscaling_group_id | Auto Scaling Group ID |
| autoscaling_group_name | Auto Scaling Group name |
| autoscaling_group_arn | Auto Scaling Group ARN |
| launch_template_id | Launch Template ID |
| alb_id | Application Load Balancer ID |
| alb_arn | Application Load Balancer ARN |
| alb_dns_name | ALB DNS name |
| alb_zone_id | ALB Zone ID |
| target_group_id | Target Group ID |
| target_group_arn | Target Group ARN |
| iam_role_arn | IAM role ARN |
| iam_instance_profile_arn | IAM instance profile ARN |

## Auto Scaling Behavior

### Scale Up
- **Trigger**: CPU utilization > 80% for 2 consecutive periods (4 minutes)
- **Action**: Add 1 instance
- **Cooldown**: 5 minutes

### Scale Down
- **Trigger**: CPU utilization < 20% for 2 consecutive periods (4 minutes)
- **Action**: Remove 1 instance
- **Cooldown**: 5 minutes

## Health Checks

### Target Group Health Check
- **Path**: `/health`
- **Protocol**: HTTP
- **Port**: 8000
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Healthy Threshold**: 2 consecutive successes
- **Unhealthy Threshold**: 2 consecutive failures

### Auto Scaling Health Check
- **Type**: ELB
- **Grace Period**: 300 seconds (5 minutes)

## User Data Script

The user data script automatically:
1. Updates system packages
2. Installs Docker, Git, Python3, CloudWatch Agent, SSM Agent
3. Configures CloudWatch Agent for logs and metrics
4. Creates application directories
5. Sets up a basic health check endpoint
6. Configures systemd services

## IAM Permissions

EC2 instances have permissions for:
- **CloudWatch Logs**: Write logs
- **Secrets Manager**: Read secrets from `${project_name}/${environment}/*`
- **S3**: Read from project buckets
- **SSM**: Systems Manager access for remote management
- **CloudWatch Agent**: Publish metrics

## SSL/TLS Configuration

### With SSL Certificate
When `ssl_certificate_arn` is provided:
- HTTPS listener on port 443 with TLS 1.3
- HTTP listener redirects to HTTPS (301)
- Modern security policy: `ELBSecurityPolicy-TLS13-1-2-2021-06`

### Without SSL Certificate (Dev/Testing)
When `ssl_certificate_arn` is empty:
- HTTP listener on port 80 forwards to target group
- No HTTPS listener created
- Suitable for development environments

## Requirements Mapping

This module satisfies:
- **Requirement 4.1**: EC2 Auto Scaling Group (t3.large, 2-10 instances)
- **Requirement 4.6**: Application Load Balancer with SSL/TLS termination

## Best Practices

1. **Use SSL in Production**: Always provide `ssl_certificate_arn` for production
2. **Enable Detailed Monitoring**: Set `enable_detailed_monitoring = true`
3. **Configure ALB Logs**: Enable access logs for audit and troubleshooting
4. **Right-Size Instances**: Adjust `instance_type` based on workload
5. **Set Appropriate Limits**: Configure `min_instances` and `max_instances` for your needs
6. **Use IMDSv2**: Enforced by default for enhanced security
7. **Monitor Metrics**: Set up CloudWatch dashboards and alarms

## Cost Optimization

### Development
- Use smaller instance types (t3.medium)
- Set min_instances = 1, max_instances = 2
- Disable detailed monitoring
- Disable ALB access logs

### Production
- Use Reserved Instances for predictable workloads (up to 72% savings)
- Enable auto-scaling to match demand
- Use Savings Plans for flexible commitment
- Monitor and right-size based on actual usage

## Troubleshooting

### Instances Not Healthy
1. Check security group rules allow ALB to reach instances on port 8000
2. Verify health check endpoint `/health` returns 200 OK
3. Check CloudWatch logs for application errors
4. Increase health check grace period if needed

### Auto Scaling Not Working
1. Verify CloudWatch alarms are in ALARM state
2. Check auto scaling policies are attached
3. Ensure cooldown periods have elapsed
4. Review auto scaling activity history

### Cannot Access Application
1. Verify ALB security group allows inbound traffic on ports 80/443
2. Check target group has healthy instances
3. Verify DNS points to ALB DNS name
4. Check SSL certificate is valid (if using HTTPS)

## Security Considerations

1. **IMDSv2 Required**: Prevents SSRF attacks
2. **Least Privilege IAM**: Minimal permissions for EC2 instances
3. **Security Groups**: Network-level access control
4. **Encrypted Logs**: CloudWatch logs encrypted at rest
5. **No Public IPs**: Instances in private subnets
6. **SSL/TLS**: Modern cipher suites and protocols

## Maintenance

### Updating Launch Template
1. Modify launch template configuration
2. Apply Terraform changes
3. Launch template version increments automatically
4. Terminate old instances gradually (auto scaling replaces them)

### Updating AMI
1. Update `data.aws_ami.amazon_linux_2` filter if needed
2. Apply Terraform changes
3. Terminate instances to force new AMI deployment

### Scaling Adjustments
1. Update `min_instances`, `max_instances`, or `desired_instances`
2. Apply Terraform changes
3. Auto Scaling Group adjusts capacity automatically
