# Terraform Infrastructure for AI-Based Code Reviewer

This directory contains Terraform configuration for deploying the AI-Based Code Reviewer platform to AWS.

## Architecture Overview

The infrastructure includes:
- **VPC**: Multi-AZ VPC with public and private subnets across 2 availability zones
- **Compute**: EC2 Auto Scaling Group (t3.large, 2-10 instances) behind Application Load Balancer
- **Databases**: RDS PostgreSQL (Multi-AZ), ElastiCache Redis (Multi-AZ), Neo4j AuraDB Enterprise
- **Security**: Security groups, AWS WAF with OWASP Top 10 protection
- **Monitoring**: CloudWatch logs and metrics

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- AWS account with necessary permissions

## Directory Structure

```
terraform/
├── main.tf              # Main configuration and provider setup
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── terraform.tfvars     # Variable values (not committed)
├── modules/
│   ├── vpc/            # VPC and networking module
│   ├── compute/        # EC2, ASG, ALB module
│   ├── database/       # RDS, ElastiCache, Neo4j module
│   ├── security/       # Security groups module
│   └── waf/            # AWS WAF module
└── environments/
    ├── dev/            # Development environment
    ├── staging/        # Staging environment
    └── prod/           # Production environment
```

## Usage

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Plan Infrastructure Changes

```bash
terraform plan -var-file="environments/staging/terraform.tfvars"
```

### Apply Infrastructure

```bash
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### Destroy Infrastructure

```bash
terraform destroy -var-file="environments/staging/terraform.tfvars"
```

## Configuration

Copy `terraform.tfvars.example` to `terraform.tfvars` and configure:

- `aws_region`: AWS region for deployment
- `environment`: Environment name (dev, staging, prod)
- `project_name`: Project name for resource naming
- `vpc_cidr`: VPC CIDR block
- `availability_zones`: List of availability zones
- Database credentials and configuration
- Neo4j AuraDB connection details

## Security Notes

- Never commit `terraform.tfvars` or any files containing secrets
- Use AWS Secrets Manager for sensitive configuration
- All data encrypted at rest and in transit
- Security groups follow least privilege principle
- AWS WAF protects against OWASP Top 10 vulnerabilities

## Backup and Disaster Recovery

- RDS automated backups: 7-day retention
- ElastiCache snapshots: Daily
- Backups encrypted with AES-256
- Cross-region backup replication for disaster recovery
- RTO: 4 hours, RPO: 1 hour
