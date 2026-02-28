# Deployment Guide: AI-Based Code Reviewer Platform

## Overview

This comprehensive deployment guide provides step-by-step instructions for deploying the AI-Based Code Reviewer platform to production on AWS. It consolidates infrastructure setup, application deployment, and operational procedures into a single authoritative resource.

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Target Audience**: DevOps Engineers, System Administrators, Developers

### What This Guide Covers

1. **Infrastructure Setup** - AWS resources provisioning with Terraform
2. **Application Deployment** - Docker-based application deployment
3. **Post-Deployment Configuration** - DNS, SSL/TLS, monitoring setup
4. **Verification Procedures** - Health checks and smoke tests
5. **Troubleshooting** - Common issues and solutions
6. **Operational Procedures** - Maintenance, backups, disaster recovery

### Prerequisites

Before starting deployment, ensure you have:

- AWS account with appropriate IAM permissions
- Terraform >= 1.0 installed
- AWS CLI v2 configured with credentials
- Docker >= 20.10 installed
- Git for version control
- Neo4j AuraDB Enterprise instance provisioned
- OpenAI and Anthropic API keys

### Architecture Overview

The platform deploys to AWS with the following components:

- **Compute**: EC2 Auto Scaling Group (2-10 t3.large instances) behind Application Load Balancer
- **Databases**: RDS PostgreSQL (Multi-AZ), ElastiCache Redis (Multi-AZ), Neo4j AuraDB Enterprise
- **Networking**: Multi-AZ VPC with public/private subnets, NAT Gateways, Internet Gateway
- **Security**: AWS WAF, Security Groups, SSL/TLS encryption, AWS Secrets Manager
- **Monitoring**: CloudWatch Logs, Metrics, Alarms, Dashboards

### Deployment Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Prerequisites Setup | 30-60 min | AWS account, tools, external services |
| Infrastructure Deployment | 15-20 min | Terraform provisioning |
| Application Deployment | 10-15 min | Docker build and deployment |
| Post-Deployment Configuration | 30-45 min | DNS, SSL, monitoring |
| Verification | 15-30 min | Health checks, smoke tests |
| **Total** | **2-3 hours** | Complete deployment |



## Table of Contents

1. [Prerequisites Setup](#prerequisites-setup)
2. [Infrastructure Deployment](#infrastructure-deployment)
3. [Application Deployment](#application-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Verification and Testing](#verification-and-testing)
6. [Troubleshooting](#troubleshooting)
7. [Operational Procedures](#operational-procedures)
8. [Disaster Recovery](#disaster-recovery)
9. [Security Best Practices](#security-best-practices)
10. [Appendices](#appendices)

---

## Prerequisites Setup

### 1.1 AWS Account Configuration

#### IAM Permissions Required

Your AWS IAM user or role needs permissions for:

- **VPC and Networking**: VPC, Subnets, Route Tables, Internet Gateway, NAT Gateway, Elastic IPs
- **Compute**: EC2 instances, Auto Scaling Groups, Launch Templates, Application Load Balancers, Target Groups
- **Databases**: RDS (PostgreSQL), ElastiCache (Redis)
- **Security**: Security Groups, AWS WAF, AWS Secrets Manager, AWS KMS
- **Monitoring**: CloudWatch Logs, Metrics, Alarms, Dashboards
- **IAM**: Service roles and policies
- **ECR**: Container registries

#### Configure AWS CLI

```bash
# Configure AWS credentials
aws configure

# Verify configuration
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAXXXXXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```



### 1.2 Install Required Tools

#### Terraform

```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
# Expected: Terraform v1.6.0 or higher
```

#### Docker

```bash
# macOS
brew install docker

# Linux (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version
# Expected: Docker version 20.10.0 or higher
```

#### AWS CLI v2

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
# Expected: aws-cli/2.x.x or higher
```

### 1.3 External Services Setup

#### Neo4j AuraDB Enterprise

1. **Create Account**: Go to https://console.neo4j.io/ and sign up
2. **Create Instance**:
   - Click "New Instance"
   - Select "AuraDB Enterprise"
   - Configuration:
     - Name: `ai-code-reviewer-production`
     - Region: Same as AWS region (e.g., us-east-1)
     - Memory: 4GB RAM
     - Storage: Auto-scaling (default)
3. **Save Credentials**: Record connection details securely
   - Connection URI: `neo4j+s://xxxxx.databases.neo4j.io`
   - Username: `neo4j`
   - Password: (generated - save securely)
4. **Configure Network Access**:
   - Add NAT Gateway IPs from your AWS VPC
   - For production, restrict to specific IPs only

#### API Keys

Obtain API keys for:

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **GitHub**: Create GitHub App or Personal Access Token



---

## Infrastructure Deployment

### 2.1 Prepare Configuration

#### Set Environment Variables

Set sensitive variables as environment variables (never commit to version control):

**Linux/macOS:**
```bash
export TF_VAR_db_password='your-secure-database-password-min-16-chars'
export TF_VAR_neo4j_connection_uri='neo4j+s://xxxxx.databases.neo4j.io'
export TF_VAR_neo4j_password='your-neo4j-password'
export TF_VAR_redis_auth_token='your-redis-auth-token-16-to-128-chars'
```

**Windows PowerShell:**
```powershell
$env:TF_VAR_db_password = 'your-secure-database-password-min-16-chars'
$env:TF_VAR_neo4j_connection_uri = 'neo4j+s://xxxxx.databases.neo4j.io'
$env:TF_VAR_neo4j_password = 'your-neo4j-password'
$env:TF_VAR_redis_auth_token = 'your-redis-auth-token-16-to-128-chars'
```

**Password Requirements:**
- Minimum 16 characters
- Include uppercase, lowercase, numbers, and special characters
- Avoid common patterns or dictionary words
- Use a password manager to generate secure passwords

#### Review Environment Configuration

```bash
cd terraform

# For production deployment
cat environments/prod/terraform.tfvars
```

Key production settings:
```hcl
environment          = "prod"
aws_region          = "us-east-1"
vpc_cidr            = "10.2.0.0/16"
availability_zones  = ["us-east-1a", "us-east-1b"]

# Compute
instance_type       = "t3.large"
min_size            = 2
max_size            = 10
desired_capacity    = 2

# Database
db_instance_class   = "db.t3.large"
db_multi_az         = true
redis_node_type     = "cache.t3.small"
redis_num_nodes     = 2

# Security
enable_waf          = true
allowed_cidr_blocks = ["0.0.0.0/0"]  # Restrict in production!
```



### 2.2 Deploy Infrastructure with Terraform

#### Step 1: Initialize Terraform

```bash
cd terraform
terraform init
```

This command:
- Downloads AWS provider plugins
- Initializes backend for state storage
- Prepares working directory

#### Step 2: Validate Configuration

```bash
# Validate Terraform syntax
terraform validate

# Run validation script
# Linux/macOS
./validate.sh

# Windows PowerShell
.\validate.ps1
```

The validation script checks:
- Terraform and AWS CLI installation
- AWS credentials configuration
- Required environment variables
- Configuration file syntax

#### Step 3: Plan Infrastructure

```bash
# Create execution plan
terraform plan -var-file="environments/prod/terraform.tfvars" -out=prod.tfplan

# Review the plan carefully
terraform show prod.tfplan
```

Expected resources to be created:
- VPC with public and private subnets (2 AZs)
- Internet Gateway and NAT Gateways (2)
- Route tables and associations
- Security groups (ALB, EC2, RDS, Redis)
- Application Load Balancer and Target Group
- Auto Scaling Group and Launch Template
- RDS PostgreSQL instance (Multi-AZ)
- ElastiCache Redis replication group (Multi-AZ)
- AWS WAF Web ACL with OWASP rules
- CloudWatch Log Groups and Alarms
- AWS Secrets Manager secrets
- IAM roles and policies

#### Step 4: Apply Infrastructure

```bash
# Apply the plan
terraform apply prod.tfplan

# Or apply directly (will prompt for confirmation)
terraform apply -var-file="environments/prod/terraform.tfvars"
```

**Expected Duration**: 15-20 minutes

Progress indicators:
- VPC and networking: 2-3 minutes
- Security groups: 1 minute
- Load balancer: 3-5 minutes
- RDS PostgreSQL: 10-15 minutes (longest)
- ElastiCache Redis: 5-10 minutes
- Auto Scaling Group: 3-5 minutes

#### Step 5: Verify Infrastructure

```bash
# View all outputs
terraform output

# Get specific outputs
terraform output vpc_id
terraform output alb_dns_name
terraform output postgres_endpoint
terraform output redis_endpoint
terraform output nat_gateway_ips

# Save outputs to file for reference
terraform output -json > terraform-outputs.json
```



### 2.3 Configure AWS Secrets Manager

Store application secrets in AWS Secrets Manager for secure access:

```bash
# Get database endpoints from Terraform outputs
POSTGRES_ENDPOINT=$(terraform output -raw postgres_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

# Create backend secrets
aws secretsmanager create-secret \
    --name ai-code-reviewer/prod/backend \
    --description "Backend application secrets for production" \
    --secret-string "{
        \"DATABASE_URL\": \"postgresql://dbadmin:${TF_VAR_db_password}@${POSTGRES_ENDPOINT}:5432/ai_code_reviewer\",
        \"REDIS_URL\": \"redis://:${TF_VAR_redis_auth_token}@${REDIS_ENDPOINT}:6379/0\",
        \"NEO4J_URI\": \"${TF_VAR_neo4j_connection_uri}\",
        \"NEO4J_USER\": \"neo4j\",
        \"NEO4J_PASSWORD\": \"${TF_VAR_neo4j_password}\",
        \"JWT_SECRET_KEY\": \"$(openssl rand -base64 64)\",
        \"OPENAI_API_KEY\": \"your-openai-api-key\",
        \"ANTHROPIC_API_KEY\": \"your-anthropic-api-key\",
        \"GITHUB_WEBHOOK_SECRET\": \"$(openssl rand -base64 32)\",
        \"ENVIRONMENT\": \"production\",
        \"LOG_LEVEL\": \"INFO\"
    }" \
    --region us-east-1

# Create frontend secrets
ALB_DNS=$(terraform output -raw alb_dns_name)

aws secretsmanager create-secret \
    --name ai-code-reviewer/prod/frontend \
    --description "Frontend application secrets for production" \
    --secret-string "{
        \"NEXT_PUBLIC_API_URL\": \"https://${ALB_DNS}\",
        \"NEXTAUTH_SECRET\": \"$(openssl rand -base64 64)\",
        \"NEXTAUTH_URL\": \"https://app.yourdomain.com\"
    }" \
    --region us-east-1

# Verify secrets were created
aws secretsmanager list-secrets \
    --filters Key=name,Values=ai-code-reviewer/prod \
    --query 'SecretList[*].[Name,ARN]' \
    --output table
```

---

## Application Deployment

### 3.1 Prepare Application Code

```bash
# Clone repository (if not already cloned)
git clone https://github.com/your-org/ai-code-reviewer.git
cd ai-code-reviewer

# Checkout production branch/tag
git checkout main
git pull origin main

# Verify code integrity
git log -1
git status
```



### 3.2 Build and Push Docker Images

#### Create ECR Repositories

```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Create ECR repositories
aws ecr create-repository \
    --repository-name ai-code-reviewer-backend \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

aws ecr create-repository \
    --repository-name ai-code-reviewer-frontend \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256
```

#### Build Docker Images

```bash
# Build backend image
cd backend
docker build -t ai-code-reviewer-backend:latest \
    --build-arg ENVIRONMENT=production \
    --platform linux/amd64 \
    .

# Build frontend image
cd ../frontend
docker build -t ai-code-reviewer-frontend:latest \
    --build-arg NEXT_PUBLIC_API_URL=https://app.yourdomain.com \
    --platform linux/amd64 \
    .

cd ..
```

#### Push Images to ECR

```bash
# Authenticate Docker with ECR
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Tag images
docker tag ai-code-reviewer-backend:latest \
    ${ECR_REGISTRY}/ai-code-reviewer-backend:latest

docker tag ai-code-reviewer-backend:latest \
    ${ECR_REGISTRY}/ai-code-reviewer-backend:$(git rev-parse --short HEAD)

docker tag ai-code-reviewer-frontend:latest \
    ${ECR_REGISTRY}/ai-code-reviewer-frontend:latest

docker tag ai-code-reviewer-frontend:latest \
    ${ECR_REGISTRY}/ai-code-reviewer-frontend:$(git rev-parse --short HEAD)

# Push images
docker push ${ECR_REGISTRY}/ai-code-reviewer-backend:latest
docker push ${ECR_REGISTRY}/ai-code-reviewer-backend:$(git rev-parse --short HEAD)
docker push ${ECR_REGISTRY}/ai-code-reviewer-frontend:latest
docker push ${ECR_REGISTRY}/ai-code-reviewer-frontend:$(git rev-parse --short HEAD)

# Verify images were pushed
aws ecr list-images \
    --repository-name ai-code-reviewer-backend \
    --region ${AWS_REGION}

aws ecr list-images \
    --repository-name ai-code-reviewer-frontend \
    --region ${AWS_REGION}
```



### 3.3 Deploy to EC2 Instances

#### Get EC2 Instance IDs

```bash
# List running instances in Auto Scaling Group
aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=prod" \
              "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].[InstanceId,PrivateIpAddress,State.Name]' \
    --output table

# Save instance IDs
INSTANCE_IDS=$(aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=prod" \
              "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].InstanceId' \
    --output text)
```

#### Deploy Application via AWS Systems Manager

```bash
# Create deployment script
cat > deploy-to-instances.sh <<'EOF'
#!/bin/bash
set -e

# Variables
ECR_REGISTRY="$1"
INSTANCE_ID="$2"

echo "Deploying to instance: $INSTANCE_ID"

# Connect via SSM and deploy
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "# Stop existing containers",
        "docker stop backend frontend || true",
        "docker rm backend frontend || true",
        "",
        "# Pull latest images",
        "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin '"$ECR_REGISTRY"'",
        "docker pull '"$ECR_REGISTRY"'/ai-code-reviewer-backend:latest",
        "docker pull '"$ECR_REGISTRY"'/ai-code-reviewer-frontend:latest",
        "",
        "# Get secrets from Secrets Manager",
        "aws secretsmanager get-secret-value --secret-id ai-code-reviewer/prod/backend --query SecretString --output text > /tmp/backend-secrets.json",
        "",
        "# Start backend container",
        "docker run -d --name backend --restart unless-stopped \\",
        "  -p 8000:8000 \\",
        "  --env-file <(cat /tmp/backend-secrets.json | jq -r \"to_entries|map(\\\"\\(.key)=\\(.value|tostring)\\\")|.[]\") \\",
        "  '"$ECR_REGISTRY"'/ai-code-reviewer-backend:latest",
        "",
        "# Start frontend container",
        "docker run -d --name frontend --restart unless-stopped \\",
        "  -p 3000:3000 \\",
        "  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \\",
        "  '"$ECR_REGISTRY"'/ai-code-reviewer-frontend:latest",
        "",
        "# Clean up secrets",
        "rm /tmp/backend-secrets.json",
        "",
        "# Verify containers are running",
        "docker ps",
        "sleep 10",
        "curl -f http://localhost:8000/health || exit 1",
        "curl -f http://localhost:3000/api/health || exit 1",
        "",
        "echo \"Deployment successful\""
    ]' \
    --output text
EOF

chmod +x deploy-to-instances.sh

# Deploy to all instances
for INSTANCE_ID in $INSTANCE_IDS; do
    ./deploy-to-instances.sh "$ECR_REGISTRY" "$INSTANCE_ID"
    echo "Waiting 30 seconds before next instance..."
    sleep 30
done
```

#### Run Database Migrations

```bash
# Connect to one instance via SSM
FIRST_INSTANCE=$(echo $INSTANCE_IDS | awk '{print $1}')
aws ssm start-session --target $FIRST_INSTANCE

# Inside the instance, run migrations
docker exec backend alembic upgrade head

# Verify migration
docker exec backend alembic current

# Exit SSM session
exit
```



---

## Post-Deployment Configuration

### 4.1 Configure DNS

#### Option 1: Using Route 53 (Recommended)

```bash
# Get Load Balancer DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Create hosted zone (if not exists)
aws route53 create-hosted-zone \
    --name yourdomain.com \
    --caller-reference $(date +%s)

# Get hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='yourdomain.com.'].Id" \
    --output text | cut -d'/' -f3)

# Create A record (alias to ALB)
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "app.yourdomain.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z35SXDOTRQ7X7K",
                    "DNSName": "'"$ALB_DNS"'",
                    "EvaluateTargetHealth": true
                }
            }
        }]
    }'

# Verify DNS propagation
dig +short app.yourdomain.com
```

#### Option 2: Using External DNS Provider

1. Log in to your DNS provider (GoDaddy, Cloudflare, etc.)
2. Create a CNAME record:
   - Name: `app` (or `@` for root domain)
   - Type: CNAME
   - Value: `<alb-dns-name>` (from Terraform output)
   - TTL: 300 (5 minutes)
3. Wait for DNS propagation (5-15 minutes)
4. Verify: `dig +short app.yourdomain.com`

### 4.2 Configure SSL/TLS

#### Request SSL Certificate

```bash
# Request certificate from AWS Certificate Manager
aws acm request-certificate \
    --domain-name app.yourdomain.com \
    --subject-alternative-names "*.yourdomain.com" \
    --validation-method DNS \
    --region us-east-1

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates \
    --query "CertificateSummaryList[?DomainName=='app.yourdomain.com'].CertificateArn" \
    --output text)

echo "Certificate ARN: $CERT_ARN"

# Get DNS validation records
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --query 'Certificate.DomainValidationOptions[*].[ResourceRecord.Name,ResourceRecord.Value]' \
    --output table
```

#### Add DNS Validation Records

Add the CNAME records to your DNS provider to validate certificate ownership.

**Route 53:**
```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file://dns-validation.json
```

**External DNS**: Manually add CNAME records from ACM console.

#### Wait for Certificate Validation

```bash
# Wait for certificate to be issued (5-30 minutes)
aws acm wait certificate-validated \
    --certificate-arn $CERT_ARN

echo "Certificate validated successfully"
```



#### Update Load Balancer with HTTPS

```bash
# Update Terraform configuration
cd terraform

# Edit environments/prod/terraform.tfvars
# Add: ssl_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID"

# Apply changes
terraform apply -var-file="environments/prod/terraform.tfvars"

# Verify HTTPS listener
aws elbv2 describe-listeners \
    --load-balancer-arn $(terraform output -raw alb_arn) \
    --query 'Listeners[?Protocol==`HTTPS`]'
```

### 4.3 Configure GitHub Webhooks

1. Go to your GitHub repository settings
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure webhook:
   - **Payload URL**: `https://app.yourdomain.com/api/v1/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Use the `GITHUB_WEBHOOK_SECRET` from Secrets Manager
   - **SSL verification**: Enable SSL verification
   - **Events**: Select "Pull requests" and "Push"
4. Click **Add webhook**
5. Test webhook by creating a test pull request

### 4.4 Configure Monitoring and Alerts

#### Create CloudWatch Dashboards

```bash
# Create system health dashboard
aws cloudwatch put-dashboard \
    --dashboard-name ai-code-reviewer-prod-health \
    --dashboard-body file://cloudwatch-dashboard-health.json

# Create performance dashboard
aws cloudwatch put-dashboard \
    --dashboard-name ai-code-reviewer-prod-performance \
    --dashboard-body file://cloudwatch-dashboard-performance.json
```

#### Configure CloudWatch Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name prod-high-error-rate \
    --alarm-description "Alert when error rate exceeds 5%" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 50 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts

# High response time alarm
aws cloudwatch put-metric-alarm \
    --alarm-name prod-high-response-time \
    --alarm-description "Alert when P95 response time exceeds 1 second" \
    --metric-name TargetResponseTime \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 300 \
    --threshold 1.0 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts

# High CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name prod-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts
```

#### Configure SNS for Alert Notifications

```bash
# Create SNS topic
aws sns create-topic --name prod-alerts

# Subscribe email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:ACCOUNT:prod-alerts \
    --protocol email \
    --notification-endpoint ops-team@yourdomain.com

# Subscribe Slack (requires AWS Chatbot setup)
# Configure via AWS Console: AWS Chatbot → Slack → Configure client
```

