# Terraform Usage Guide

This guide provides step-by-step instructions for deploying the AI-Based Code Reviewer infrastructure using Terraform.

## Prerequisites

### Required Tools

1. **Terraform** (>= 1.0)
   ```bash
   # Install on macOS
   brew install terraform
   
   # Install on Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **AWS CLI** (>= 2.0)
   ```bash
   # Install on macOS
   brew install awscli
   
   # Install on Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

3. **AWS Account** with appropriate permissions

### AWS Permissions Required

Your AWS IAM user/role needs permissions for:
- VPC and networking (VPC, Subnets, Route Tables, Internet Gateway, NAT Gateway)
- EC2 (instances, Auto Scaling Groups, Load Balancers)
- RDS (PostgreSQL instances)
- ElastiCache (Redis clusters)
- Security Groups
- AWS WAF
- CloudWatch (logs and metrics)
- IAM (for service roles)

## Initial Setup

### 1. Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# Verify configuration
aws sts get-caller-identity
```

### 2. Clone Repository and Navigate to Terraform Directory

```bash
cd terraform
```

### 3. Create Configuration File

```bash
# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration with your values
nano terraform.tfvars
```

**Important**: Update the following in `terraform.tfvars`:
- `db_password`: Strong password for PostgreSQL
- `neo4j_connection_uri`: Your Neo4j AuraDB connection string
- `neo4j_password`: Your Neo4j password
- `ssl_certificate_arn`: ARN of your SSL certificate (if using HTTPS)
- `allowed_cidr_blocks`: Restrict to your IP ranges

### 4. Initialize Terraform

```bash
terraform init
```

This command:
- Downloads required provider plugins (AWS)
- Initializes the backend for state storage
- Prepares the working directory

## Deployment Workflow

### Development Environment

```bash
# Plan deployment
terraform plan -var-file="environments/dev/terraform.tfvars"

# Review the plan carefully, then apply
terraform apply -var-file="environments/dev/terraform.tfvars"

# Type 'yes' when prompted to confirm
```

### Staging Environment

```bash
# Plan deployment
terraform plan -var-file="environments/staging/terraform.tfvars"

# Apply changes
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### Production Environment

```bash
# Plan deployment
terraform plan -var-file="environments/prod/terraform.tfvars"

# Save plan for review
terraform plan -var-file="environments/prod/terraform.tfvars" -out=prod.tfplan

# Review the plan file
terraform show prod.tfplan

# Apply the reviewed plan
terraform apply prod.tfplan
```

## Common Operations

### View Current Infrastructure

```bash
# Show current state
terraform show

# List all resources
terraform state list

# Show specific resource
terraform state show module.vpc.aws_vpc.main
```

### Update Infrastructure

```bash
# Modify terraform.tfvars or .tf files

# Preview changes
terraform plan -var-file="environments/staging/terraform.tfvars"

# Apply changes
terraform apply -var-file="environments/staging/terraform.tfvars"
```

### View Outputs

```bash
# Show all outputs
terraform output

# Show specific output
terraform output vpc_id
terraform output nat_gateway_ips
```

### Destroy Infrastructure

**Warning**: This will delete all resources. Use with caution!

```bash
# Preview what will be destroyed
terraform plan -destroy -var-file="environments/dev/terraform.tfvars"

# Destroy infrastructure
terraform destroy -var-file="environments/dev/terraform.tfvars"

# Type 'yes' when prompted to confirm
```

## State Management

### Remote State (Recommended for Production)

1. Create S3 bucket for state storage:
   ```bash
   aws s3 mb s3://your-terraform-state-bucket
   aws s3api put-bucket-versioning \
     --bucket your-terraform-state-bucket \
     --versioning-configuration Status=Enabled
   ```

2. Create DynamoDB table for state locking:
   ```bash
   aws dynamodb create-table \
     --table-name terraform-state-lock \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

3. Uncomment and configure backend in `main.tf`:
   ```hcl
   backend "s3" {
     bucket         = "your-terraform-state-bucket"
     key            = "ai-code-reviewer/terraform.tfstate"
     region         = "us-east-1"
     encrypt        = true
     dynamodb_table = "terraform-state-lock"
   }
   ```

4. Initialize backend:
   ```bash
   terraform init -migrate-state
   ```

### State Backup

```bash
# Pull current state
terraform state pull > terraform.tfstate.backup

# Push state (use with caution)
terraform state push terraform.tfstate.backup
```

## Troubleshooting

### Common Issues

#### 1. Insufficient Permissions

**Error**: `Error: UnauthorizedOperation`

**Solution**: Verify your AWS credentials have necessary permissions.

#### 2. Resource Already Exists

**Error**: `Error: resource already exists`

**Solution**: Import existing resource or remove from AWS console.

```bash
# Import existing VPC
terraform import module.vpc.aws_vpc.main vpc-xxxxx
```

#### 3. State Lock

**Error**: `Error: Error acquiring the state lock`

**Solution**: Release the lock or wait for it to expire.

```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

#### 4. Terraform Version Mismatch

**Error**: `Error: Unsupported Terraform Core version`

**Solution**: Upgrade Terraform to required version.

```bash
# Check version
terraform version

# Upgrade Terraform
brew upgrade terraform  # macOS
```

### Validation

```bash
# Validate configuration syntax
terraform validate

# Format configuration files
terraform fmt -recursive

# Check for security issues (requires tfsec)
tfsec .
```

## Cost Estimation

Use AWS Pricing Calculator or Infracost:

```bash
# Install Infracost
brew install infracost  # macOS

# Generate cost estimate
infracost breakdown --path .
```

### Estimated Monthly Costs (Staging)

- VPC: Free (NAT Gateways: ~$65/month)
- EC2 t3.large (2 instances): ~$120/month
- RDS db.t3.large (Multi-AZ): ~$280/month
- ElastiCache cache.t3.small (Multi-AZ): ~$50/month
- ALB: ~$25/month
- Data transfer: Variable
- **Total**: ~$540/month (excluding Neo4j AuraDB)

## Security Best Practices

1. **Never commit secrets**: Use AWS Secrets Manager or environment variables
2. **Enable MFA**: For AWS accounts with Terraform access
3. **Use least privilege**: IAM policies with minimum required permissions
4. **Enable encryption**: All data at rest and in transit
5. **Regular backups**: Automated backups with 7-day retention
6. **State encryption**: Enable encryption for Terraform state
7. **Access logging**: Enable VPC Flow Logs and CloudWatch
8. **Network segmentation**: Use private subnets for databases

## Maintenance

### Regular Tasks

1. **Update Terraform**: Keep Terraform and providers up to date
2. **Review costs**: Monitor AWS costs regularly
3. **Security patches**: Apply security updates to EC2 instances
4. **Backup verification**: Test restore procedures quarterly
5. **State cleanup**: Remove unused resources from state

### Terraform Upgrades

```bash
# Check for provider updates
terraform init -upgrade

# Update lock file
terraform providers lock
```

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## Support

For issues or questions:
1. Check this documentation
2. Review Terraform logs: `TF_LOG=DEBUG terraform apply`
3. Consult AWS documentation
4. Contact DevOps team
