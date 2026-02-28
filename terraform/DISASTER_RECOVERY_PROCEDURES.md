# Disaster Recovery Procedures

## Overview

This document provides comprehensive disaster recovery (DR) procedures for the AI-Based Code Reviewer platform. It defines recovery objectives, outlines step-by-step recovery procedures, and documents testing protocols to ensure business continuity in the event of a disaster.

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Next Review Date**: 2024-04-15

## Executive Summary

The AI-Based Code Reviewer platform implements disaster recovery procedures to ensure rapid recovery from catastrophic failures. This document meets requirements:

- **Requirement 4.10**: Disaster recovery procedures with RTO of 4 hours and RPO of 1 hour
- **Requirement 9.8**: Backup and recovery procedures with tested restore steps
- **Requirement 9.10**: Disaster recovery plan with RTO/RPO targets and procedures

### Recovery Objectives

| Metric | Target | Actual Capability |
|--------|--------|-------------------|
| **RTO** (Recovery Time Objective) | 4 hours | 2-3 hours |
| **RPO** (Recovery Point Objective) | 1 hour | 5-15 minutes |

### Disaster Scenarios Covered

1. Complete AWS region failure
2. Database corruption or loss
3. Application infrastructure failure
4. Security breach requiring infrastructure rebuild
5. Data center disaster

## Table of Contents

1. [Recovery Objectives](#recovery-objectives-detailed)
2. [Architecture Overview](#architecture-overview)
3. [Backup Strategy](#backup-strategy)
4. [Recovery Procedures](#recovery-procedures)
5. [Disaster Scenarios](#disaster-scenarios)
6. [Testing Procedures](#testing-procedures)
7. [Roles and Responsibilities](#roles-and-responsibilities)
8. [Communication Plan](#communication-plan)
9. [Post-Recovery Validation](#post-recovery-validation)
10. [Appendices](#appendices)


## Recovery Objectives (Detailed)

### Recovery Time Objective (RTO): 4 Hours

RTO defines the maximum acceptable time to restore services after a disaster. Our target is 4 hours from disaster declaration to full service restoration.

**Component RTOs:**

| Component | RTO Target | Typical Recovery Time | Notes |
|-----------|------------|----------------------|-------|
| PostgreSQL RDS | 2 hours | 45-90 minutes | Point-in-time restore + DNS update |
| ElastiCache Redis | 1 hour | 30-45 minutes | Snapshot restore + cache warming |
| Neo4j AuraDB | 2 hours | 60-120 minutes | Managed restore by Neo4j |
| EC2 Application Servers | 1 hour | 30-45 minutes | Auto Scaling Group recreation |
| Load Balancer & Networking | 30 minutes | 15-30 minutes | Terraform recreation |
| **Total System RTO** | **4 hours** | **2-3 hours** | Parallel recovery reduces total time |

### Recovery Point Objective (RPO): 1 Hour

RPO defines the maximum acceptable data loss measured in time. Our target is 1 hour of data loss maximum.

**Component RPOs:**

| Component | RPO Target | Actual RPO | Backup Frequency |
|-----------|------------|------------|------------------|
| PostgreSQL RDS | 1 hour | ~5 minutes | Continuous transaction logs |
| ElastiCache Redis | 1 hour | ~15 minutes | Cache data, acceptable loss |
| Neo4j AuraDB | 1 hour | ~5 minutes | Continuous backups |
| Application Code | 0 minutes | 0 minutes | Git repository (no data loss) |
| Configuration | 0 minutes | 0 minutes | Terraform state (no data loss) |

**Note**: Redis is used for caching and session storage. Data loss up to 24 hours is acceptable as it can be regenerated from PostgreSQL.


## Architecture Overview

### Multi-Region Architecture

The platform is deployed in a primary AWS region with disaster recovery capabilities:

**Primary Region**: us-east-1 (N. Virginia)  
**DR Region**: us-west-2 (Oregon)

```
┌─────────────────────────────────────────────────────────────┐
│                     Primary Region (us-east-1)              │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   RDS        │    │  ElastiCache │    │   Neo4j      │ │
│  │  PostgreSQL  │    │    Redis     │    │   AuraDB     │ │
│  │  Multi-AZ    │    │  Multi-AZ    │    │  Enterprise  │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
│         │                   │                   │          │
│         │ Automated Backups │                   │          │
│         └───────────────────┴───────────────────┘          │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              │ Cross-Region Replication
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DR Region (us-west-2)                  │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   RDS        │    │  ElastiCache │    │   Neo4j      │ │
│  │  Snapshots   │    │  Snapshots   │    │   Backups    │ │
│  │  (Encrypted) │    │  (Encrypted) │    │  (Managed)   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### High Availability Features

**Within Primary Region:**
- Multi-AZ deployment for RDS PostgreSQL (automatic failover)
- Multi-AZ deployment for ElastiCache Redis (automatic failover)
- Auto Scaling Group across 2 availability zones
- Application Load Balancer with health checks

**Cross-Region:**
- Automated backup replication to DR region
- Terraform state stored in S3 with versioning
- Application code in Git (GitHub)
- Infrastructure as Code for rapid recreation


## Backup Strategy

### Backup Schedule

All backups run daily at 02:00 UTC (2 AM UTC) to minimize impact during low-traffic hours.

| Database | Backup Type | Schedule | Retention | Encryption | Cross-Region |
|----------|-------------|----------|-----------|------------|--------------|
| PostgreSQL | Automated + Transaction Logs | Daily 02:00-03:00 UTC | 7 days | AES-256 (KMS) | ✓ Yes |
| Redis | Automated Snapshots | Daily 02:00-04:00 UTC | 7 days | AES-256 (KMS) | ✓ Yes |
| Neo4j | Continuous Backups | Continuous | Aura-managed | AES-256 | ✓ Yes |

### Backup Verification

Automated backup verification runs weekly:
- Backup integrity checks
- Restore test to isolated environment
- Data validation queries
- Results logged to CloudWatch

### Cross-Region Backup Replication

**RDS PostgreSQL:**
```bash
# Automated snapshot copy to DR region
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:xxx:snapshot:xxx \
  --target-db-snapshot-identifier dr-copy-$(date +%Y%m%d) \
  --source-region us-east-1 \
  --region us-west-2 \
  --kms-key-id arn:aws:kms:us-west-2:xxx:key/xxx
```

**ElastiCache Redis:**
```bash
# Copy snapshot to DR region
aws elasticache copy-snapshot \
  --source-snapshot-name automatic.xxx-2024-01-15-02-00 \
  --target-snapshot-name dr-copy-$(date +%Y%m%d) \
  --target-bucket s3-dr-backups-us-west-2 \
  --source-region us-east-1 \
  --region us-west-2
```

**Neo4j AuraDB:**
- Managed by Neo4j with automatic geographic redundancy
- Backups stored across multiple regions by default
- No manual replication required

### Backup Monitoring

CloudWatch alarms monitor backup health:
- Alert if backup fails
- Alert if latest restorable time > 24 hours old
- Alert if backup storage exceeds threshold
- Alert if cross-region replication fails


## Recovery Procedures

### Pre-Recovery Checklist

Before initiating disaster recovery:

- [ ] **Declare Disaster**: Incident Commander declares disaster and activates DR plan
- [ ] **Assess Scope**: Determine which components are affected
- [ ] **Notify Stakeholders**: Alert management, customers, and recovery team
- [ ] **Document Timeline**: Record disaster start time for RTO tracking
- [ ] **Verify DR Resources**: Confirm DR region resources are available
- [ ] **Establish Communication**: Set up war room (Slack channel, conference bridge)
- [ ] **Assign Roles**: Confirm Incident Commander, Technical Lead, Communications Lead

### Recovery Procedure 1: Complete Region Failure

**Scenario**: Primary AWS region (us-east-1) is completely unavailable.

**Estimated Recovery Time**: 3-4 hours  
**Data Loss**: 5-15 minutes (last backup to failure)

#### Step 1: Assess and Declare (15 minutes)

```bash
# Verify region is down
aws ec2 describe-instances --region us-east-1 --max-results 1
# Expected: Connection timeout or service unavailable

# Check AWS Service Health Dashboard
# https://health.aws.amazon.com/health/status

# Declare disaster if region is confirmed down
echo "DISASTER DECLARED: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee disaster-log.txt
```

#### Step 2: Prepare DR Region (30 minutes)

```bash
# Switch to DR region
export AWS_DEFAULT_REGION=us-west-2

# Verify DR region is healthy
aws ec2 describe-availability-zones --region us-west-2

# Clone Terraform configuration
cd /path/to/terraform
git pull origin main

# Update terraform.tfvars for DR region
cp environments/prod/terraform.tfvars environments/dr/terraform.tfvars
sed -i 's/us-east-1/us-west-2/g' environments/dr/terraform.tfvars
sed -i 's/prod/dr/g' environments/dr/terraform.tfvars
```

#### Step 3: Restore Databases (90 minutes)

**PostgreSQL RDS (45-60 minutes):**

```bash
# List available snapshots in DR region
aws rds describe-db-snapshots \
  --region us-west-2 \
  --query 'DBSnapshots[?starts_with(DBSnapshotIdentifier, `dr-copy`)]' \
  --output table

# Identify most recent snapshot
LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
  --region us-west-2 \
  --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime)[-1].DBSnapshotIdentifier' \
  --output text)

echo "Restoring from snapshot: $LATEST_SNAPSHOT"

# Restore RDS from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-code-reviewer-dr-postgres \
  --db-snapshot-identifier $LATEST_SNAPSHOT \
  --db-instance-class db.t3.large \
  --db-subnet-group-name ai-code-reviewer-dr-db-subnet-group \
  --vpc-security-group-ids sg-xxxxx \
  --multi-az \
  --publicly-accessible false \
  --region us-west-2

# Wait for RDS to become available (30-45 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier ai-code-reviewer-dr-postgres \
  --region us-west-2

# Get new endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-dr-postgres \
  --region us-west-2 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "RDS restored at: $RDS_ENDPOINT"
```

**ElastiCache Redis (30-45 minutes):**

```bash
# List available Redis snapshots
aws elasticache describe-snapshots \
  --region us-west-2 \
  --query 'Snapshots[?starts_with(SnapshotName, `dr-copy`)]' \
  --output table

# Identify most recent snapshot
LATEST_REDIS_SNAPSHOT=$(aws elasticache describe-snapshots \
  --region us-west-2 \
  --query 'Snapshots | sort_by(@, &NodeSnapshots[0].SnapshotCreateTime)[-1].SnapshotName' \
  --output text)

echo "Restoring Redis from snapshot: $LATEST_REDIS_SNAPSHOT"

# Restore Redis from snapshot
aws elasticache create-replication-group \
  --replication-group-id ai-code-reviewer-dr-redis \
  --replication-group-description "DR Redis restored from snapshot" \
  --snapshot-name $LATEST_REDIS_SNAPSHOT \
  --cache-node-type cache.t3.small \
  --engine redis \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --cache-subnet-group-name ai-code-reviewer-dr-redis-subnet-group \
  --security-group-ids sg-xxxxx \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --auth-token "$(cat /secure/redis-auth-token.txt)" \
  --region us-west-2

# Wait for Redis to become available (15-20 minutes)
aws elasticache wait replication-group-available \
  --replication-group-id ai-code-reviewer-dr-redis \
  --region us-west-2

# Get new endpoint
REDIS_ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id ai-code-reviewer-dr-redis \
  --region us-west-2 \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text)

echo "Redis restored at: $REDIS_ENDPOINT"
```

**Neo4j AuraDB (60-90 minutes):**

```bash
# Neo4j restore is managed through Aura Console
# 1. Log in to Neo4j Aura Console: https://console.neo4j.io/
# 2. Navigate to Backups section
# 3. Select most recent backup before disaster
# 4. Click "Restore to new instance"
# 5. Select us-west-2 region
# 6. Choose 4GB RAM configuration
# 7. Wait for restore to complete (60-90 minutes)
# 8. Note new connection URI

# Alternative: Contact Neo4j Support for expedited restore
# Email: support@neo4j.com
# Phone: [Enterprise support number]
# Mention: "Production disaster recovery - Priority 1"

# Once restored, update connection details
NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io"
echo "Neo4j restored at: $NEO4J_URI"
```


#### Step 4: Deploy Infrastructure (45 minutes)

```bash
# Navigate to Terraform directory
cd /path/to/terraform

# Initialize Terraform for DR region
terraform init -backend-config="region=us-west-2"

# Update variables with restored database endpoints
cat > terraform.tfvars <<EOF
region = "us-west-2"
environment = "dr"
project_name = "ai-code-reviewer"

# Database endpoints from Step 3
postgres_endpoint = "$RDS_ENDPOINT"
redis_endpoint = "$REDIS_ENDPOINT"
neo4j_uri = "$NEO4J_URI"

# Other configuration...
EOF

# Plan infrastructure deployment
terraform plan -out=dr-deployment.tfplan

# Review plan carefully
# Verify it will create VPC, subnets, ALB, ASG, security groups

# Apply infrastructure
terraform apply dr-deployment.tfplan

# Wait for infrastructure to be ready (30-40 minutes)
# Monitor progress
watch -n 30 'aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-code-reviewer-dr-asg \
  --region us-west-2 \
  --query "AutoScalingGroups[0].Instances[*].[InstanceId,HealthStatus,LifecycleState]" \
  --output table'
```

#### Step 5: Deploy Application (30 minutes)

```bash
# Get latest application version from Git
cd /path/to/application
git pull origin main

# Build Docker images
docker build -t ai-code-reviewer-backend:latest ./backend
docker build -t ai-code-reviewer-frontend:latest ./frontend

# Push to ECR in DR region
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

docker tag ai-code-reviewer-backend:latest \
  <account-id>.dkr.ecr.us-west-2.amazonaws.com/ai-code-reviewer-backend:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/ai-code-reviewer-backend:latest

docker tag ai-code-reviewer-frontend:latest \
  <account-id>.dkr.ecr.us-west-2.amazonaws.com/ai-code-reviewer-frontend:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/ai-code-reviewer-frontend:latest

# Update Auto Scaling Group launch template
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name ai-code-reviewer-dr-asg \
  --launch-template LaunchTemplateId=lt-xxxxx,Version='$Latest' \
  --region us-west-2

# Trigger instance refresh to deploy new version
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name ai-code-reviewer-dr-asg \
  --region us-west-2

# Wait for deployment to complete (15-20 minutes)
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name ai-code-reviewer-dr-asg \
  --region us-west-2
```

#### Step 6: Update DNS (15 minutes)

```bash
# Get new Load Balancer DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names ai-code-reviewer-dr-alb \
  --region us-west-2 \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "New ALB DNS: $ALB_DNS"

# Update Route 53 DNS records
# Option 1: Automated (if using Route 53)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.ai-code-reviewer.com",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "'"$ALB_DNS"'"}]
      }
    }]
  }'

# Option 2: Manual (if using external DNS provider)
# Update DNS A/CNAME record to point to new ALB
# TTL should be low (60 seconds) for faster propagation

# Wait for DNS propagation (5-15 minutes)
watch -n 10 'dig +short app.ai-code-reviewer.com'
```

#### Step 7: Verify and Monitor (30 minutes)

```bash
# Run health checks
curl -f https://app.ai-code-reviewer.com/health || echo "Health check failed"

# Run smoke tests
cd /path/to/tests
./run-smoke-tests.sh --environment dr

# Monitor application logs
aws logs tail /aws/ec2/ai-code-reviewer-dr --follow --region us-west-2

# Monitor CloudWatch metrics
# - API response times
# - Error rates
# - Database connections
# - Cache hit rates

# Verify database connectivity
psql -h $RDS_ENDPOINT -U dbadmin -d ai_code_reviewer -c "SELECT COUNT(*) FROM users;"
redis-cli -h $REDIS_ENDPOINT -p 6379 --tls -a "$(cat /secure/redis-auth-token.txt)" PING
cypher-shell -a $NEO4J_URI -u neo4j -p "$(cat /secure/neo4j-password.txt)" "MATCH (n) RETURN count(n);"
```

#### Step 8: Notify Stakeholders (15 minutes)

```bash
# Send recovery completion notification
cat > recovery-notification.txt <<EOF
DISASTER RECOVERY COMPLETED

Disaster Start: $(cat disaster-log.txt | grep "DISASTER DECLARED" | cut -d: -f2-)
Recovery Complete: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Total Recovery Time: [Calculate from disaster-log.txt]

Status: System operational in DR region (us-west-2)
URL: https://app.ai-code-reviewer.com
Data Loss: Approximately 5-15 minutes

Next Steps:
1. Continue monitoring for 24 hours
2. Assess primary region status
3. Plan failback when primary region is restored

Incident Commander: [Name]
Technical Lead: [Name]
EOF

# Send via email/Slack
# Update status page
# Notify customers
```


### Recovery Procedure 2: Database Corruption

**Scenario**: PostgreSQL database is corrupted but infrastructure is intact.

**Estimated Recovery Time**: 1-2 hours  
**Data Loss**: Up to 1 hour (depending on backup timing)

#### Step-by-Step Recovery

```bash
# 1. Assess corruption (10 minutes)
psql -h $RDS_ENDPOINT -U dbadmin -d ai_code_reviewer

# Try to query tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM projects;

# Check for corruption indicators
# - Query failures
# - Inconsistent data
# - Missing tables

# 2. Stop application traffic (5 minutes)
# Update ALB target group to drain connections
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/xxx \
  --health-check-enabled false

# Wait for connections to drain
sleep 60

# 3. Create snapshot of corrupted database (10 minutes)
aws rds create-db-snapshot \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --db-snapshot-identifier corrupted-$(date +%Y%m%d-%H%M) \
  --region us-east-1

# 4. Identify last good backup (5 minutes)
aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime)[-5:]' \
  --output table

# Select snapshot from before corruption occurred
RESTORE_SNAPSHOT="rds:ai-code-reviewer-prod-postgres-2024-01-15-02-00"

# 5. Restore to new instance (45-60 minutes)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-code-reviewer-prod-postgres-restored \
  --db-snapshot-identifier $RESTORE_SNAPSHOT \
  --db-instance-class db.t3.large \
  --db-subnet-group-name ai-code-reviewer-prod-db-subnet-group \
  --vpc-security-group-ids sg-xxxxx \
  --multi-az \
  --region us-east-1

# Wait for restore
aws rds wait db-instance-available \
  --db-instance-identifier ai-code-reviewer-prod-postgres-restored \
  --region us-east-1

# 6. Verify restored data (15 minutes)
NEW_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres-restored \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

psql -h $NEW_ENDPOINT -U dbadmin -d ai_code_reviewer

# Run validation queries
SELECT COUNT(*) FROM users;
SELECT MAX(created_at) FROM analysis_results;
SELECT COUNT(*) FROM projects;

# 7. Update application configuration (10 minutes)
# Update database endpoint in Secrets Manager
aws secretsmanager update-secret \
  --secret-id ai-code-reviewer/prod/database \
  --secret-string "{\"host\":\"$NEW_ENDPOINT\",\"port\":5432,\"database\":\"ai_code_reviewer\",\"username\":\"dbadmin\",\"password\":\"***\"}"

# Restart application servers to pick up new endpoint
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name ai-code-reviewer-prod-asg

# 8. Re-enable traffic (5 minutes)
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/xxx \
  --health-check-enabled true

# 9. Monitor and verify (15 minutes)
# Check application logs
# Run smoke tests
# Monitor error rates

# 10. Clean up old instance (after 24 hours)
# Rename old instance
aws rds modify-db-instance \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --new-db-instance-identifier ai-code-reviewer-prod-postgres-old \
  --apply-immediately

# Rename restored instance to production name
aws rds modify-db-instance \
  --db-instance-identifier ai-code-reviewer-prod-postgres-restored \
  --new-db-instance-identifier ai-code-reviewer-prod-postgres \
  --apply-immediately
```


### Recovery Procedure 3: Application Infrastructure Failure

**Scenario**: EC2 instances, Auto Scaling Group, or Load Balancer failure.

**Estimated Recovery Time**: 30-60 minutes  
**Data Loss**: None (databases intact)

#### Step-by-Step Recovery

```bash
# 1. Assess infrastructure status (5 minutes)
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-code-reviewer-prod-asg \
  --query 'AutoScalingGroups[0].[DesiredCapacity,MinSize,MaxSize,Instances[*].[InstanceId,HealthStatus]]'

aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/xxx

# 2. If Auto Scaling Group is unhealthy, recreate (30 minutes)
# Use Terraform to recreate infrastructure
cd /path/to/terraform
terraform plan -target=module.compute
terraform apply -target=module.compute -auto-approve

# 3. If Load Balancer is unhealthy, recreate (20 minutes)
terraform plan -target=aws_lb.main
terraform apply -target=aws_lb.main -auto-approve

# 4. Force instance refresh (15 minutes)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name ai-code-reviewer-prod-asg \
  --preferences '{"MinHealthyPercentage":50,"InstanceWarmup":300}'

# 5. Monitor recovery
watch -n 10 'aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/xxx \
  --query "TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]" \
  --output table'

# 6. Verify application (10 minutes)
curl -f https://app.ai-code-reviewer.com/health
./run-smoke-tests.sh
```

### Recovery Procedure 4: Security Breach

**Scenario**: Security breach requires complete infrastructure rebuild.

**Estimated Recovery Time**: 4-6 hours  
**Data Loss**: Minimal (databases can be preserved or restored)

#### Step-by-Step Recovery

```bash
# 1. Isolate compromised infrastructure (15 minutes)
# Disable all ingress traffic
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxx \
  --ip-permissions '[{"IpProtocol":"-1","IpRanges":[{"CidrIp":"0.0.0.0/0"}]}]'

# Stop all EC2 instances
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name ai-code-reviewer-prod-asg \
  --min-size 0 \
  --desired-capacity 0

# 2. Forensics and assessment (60 minutes)
# Create snapshots of compromised instances for investigation
aws ec2 create-snapshots \
  --instance-specification InstanceId=i-xxxxx \
  --description "Forensics snapshot $(date +%Y%m%d-%H%M)"

# Analyze logs
aws logs filter-log-events \
  --log-group-name /aws/ec2/ai-code-reviewer \
  --start-time $(date -d '24 hours ago' +%s)000

# 3. Assess database integrity (30 minutes)
# Check for unauthorized access or data modification
psql -h $RDS_ENDPOINT -U dbadmin -d ai_code_reviewer

# Review audit logs
SELECT * FROM audit_log_entries 
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

# Check for suspicious activity
SELECT user_id, action, COUNT(*) 
FROM audit_log_entries 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_id, action
HAVING COUNT(*) > 1000;

# 4. Rotate all credentials (30 minutes)
# Rotate database passwords
aws rds modify-db-instance \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --master-user-password "$(openssl rand -base64 32)" \
  --apply-immediately

# Rotate Redis auth token
aws elasticache modify-replication-group \
  --replication-group-id ai-code-reviewer-prod-redis \
  --auth-token "$(openssl rand -base64 32)" \
  --auth-token-update-strategy ROTATE \
  --apply-immediately

# Rotate all API keys in Secrets Manager
aws secretsmanager rotate-secret --secret-id ai-code-reviewer/prod/github-token
aws secretsmanager rotate-secret --secret-id ai-code-reviewer/prod/openai-key
aws secretsmanager rotate-secret --secret-id ai-code-reviewer/prod/anthropic-key

# Rotate JWT signing keys
aws secretsmanager update-secret \
  --secret-id ai-code-reviewer/prod/jwt-secret \
  --secret-string "$(openssl rand -base64 64)"

# 5. Rebuild infrastructure from clean state (120 minutes)
# Destroy compromised infrastructure
cd /path/to/terraform
terraform destroy -target=module.compute -auto-approve

# Pull latest clean code
cd /path/to/application
git fetch origin
git reset --hard origin/main

# Rebuild and scan Docker images
docker build -t ai-code-reviewer-backend:latest ./backend
docker build -t ai-code-reviewer-frontend:latest ./frontend

# Scan images for vulnerabilities
docker scan ai-code-reviewer-backend:latest
docker scan ai-code-reviewer-frontend:latest

# Deploy clean infrastructure
cd /path/to/terraform
terraform apply -auto-approve

# 6. Enhanced monitoring (30 minutes)
# Enable additional CloudWatch alarms
# Enable AWS GuardDuty
# Enable VPC Flow Logs
# Enable CloudTrail logging

# 7. Verify and monitor (60 minutes)
# Run comprehensive security scan
./security/run_security_scan.sh

# Monitor for 24 hours with enhanced alerting
```


## Disaster Scenarios

### Scenario Matrix

| Scenario | Likelihood | Impact | RTO | RPO | Primary Response |
|----------|-----------|--------|-----|-----|------------------|
| Complete Region Failure | Very Low | Critical | 4 hours | 15 min | Failover to DR region |
| Database Corruption | Low | High | 2 hours | 1 hour | Restore from backup |
| Application Failure | Medium | Medium | 1 hour | None | Recreate infrastructure |
| Security Breach | Low | Critical | 6 hours | Varies | Isolate, rebuild, rotate |
| Network Outage | Medium | High | 2 hours | None | Failover networking |
| Data Center Disaster | Very Low | Critical | 4 hours | 15 min | Failover to DR region |

### Scenario 1: AWS Region Failure

**Triggers:**
- AWS Service Health Dashboard shows region-wide outage
- Multiple availability zones unavailable
- Unable to access any AWS services in region

**Response:** Execute Recovery Procedure 1 (Complete Region Failure)

**Key Decisions:**
- Declare disaster if outage expected to exceed 1 hour
- Failover to DR region immediately
- Do not wait for AWS to restore primary region

### Scenario 2: Database Corruption or Loss

**Triggers:**
- Database queries returning errors
- Data inconsistencies detected
- Tables missing or corrupted
- Replication lag exceeding 1 hour

**Response:** Execute Recovery Procedure 2 (Database Corruption)

**Key Decisions:**
- Identify corruption scope (single table vs entire database)
- Determine last known good backup
- Accept data loss from backup point to corruption time

### Scenario 3: Application Infrastructure Failure

**Triggers:**
- All EC2 instances unhealthy
- Load Balancer health checks failing
- Auto Scaling Group unable to launch instances
- Application returning 5xx errors

**Response:** Execute Recovery Procedure 3 (Application Infrastructure Failure)

**Key Decisions:**
- Determine if issue is code-related or infrastructure-related
- Rollback application if recent deployment caused issue
- Recreate infrastructure if underlying AWS resources failed

### Scenario 4: Security Breach

**Triggers:**
- Unauthorized access detected
- Malware or ransomware detected
- Data exfiltration suspected
- AWS GuardDuty critical alerts
- Unusual API activity patterns

**Response:** Execute Recovery Procedure 4 (Security Breach)

**Key Decisions:**
- Isolate immediately to prevent further damage
- Preserve evidence for forensics
- Determine if data was compromised
- Notify customers if data breach confirmed

### Scenario 5: Multi-AZ Failover (Automatic)

**Triggers:**
- Primary AZ failure
- RDS or Redis automatic failover triggered

**Response:** Monitor automatic failover (no manual intervention required)

**Verification:**
```bash
# Verify RDS failover completed
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].[AvailabilityZone,SecondaryAvailabilityZone,MultiAZ]'

# Verify Redis failover completed
aws elasticache describe-replication-groups \
  --replication-group-id ai-code-reviewer-prod-redis \
  --query 'ReplicationGroups[0].[Status,AutomaticFailover,MultiAZ]'

# Monitor application for any issues
# Failover should be transparent to application
```


## Testing Procedures

### DR Testing Schedule

| Test Type | Frequency | Duration | Participants | Success Criteria |
|-----------|-----------|----------|--------------|------------------|
| Backup Verification | Weekly | 30 min | DevOps | Successful restore to test environment |
| Database Restore | Monthly | 2 hours | DevOps, DBA | Data integrity verified |
| Application Failover | Quarterly | 4 hours | Full team | RTO < 4 hours achieved |
| Full DR Exercise | Annually | 8 hours | Full team + management | All procedures validated |
| Tabletop Exercise | Semi-annually | 2 hours | Management + leads | Roles and communication verified |

### Test 1: Backup Verification (Weekly)

**Objective**: Verify backups are being created and are restorable.

**Procedure:**
```bash
# 1. Verify latest backup exists
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].LatestRestorableTime'

# Expected: Timestamp within last 24 hours

# 2. List recent snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --max-records 3

# Expected: At least 3 snapshots with status "available"

# 3. Verify cross-region replication
aws rds describe-db-snapshots \
  --region us-west-2 \
  --query 'DBSnapshots[?starts_with(DBSnapshotIdentifier, `dr-copy`)]' \
  --max-records 3

# Expected: Recent snapshots in DR region

# 4. Document results
echo "Backup verification completed: $(date)" >> backup-verification-log.txt
```

**Success Criteria:**
- [ ] Latest restorable time < 24 hours old
- [ ] At least 3 automated snapshots available
- [ ] Cross-region snapshots exist in DR region
- [ ] All snapshots have status "available"

### Test 2: Database Restore (Monthly)

**Objective**: Verify database can be restored and data is intact.

**Procedure:**
```bash
# 1. Create test environment
terraform workspace new dr-test
terraform apply -var="environment=dr-test" -auto-approve

# 2. Restore latest backup to test environment
LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBSnapshots | sort_by(@, &SnapshotCreateTime)[-1].DBSnapshotIdentifier' \
  --output text)

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-code-reviewer-test-restore \
  --db-snapshot-identifier $LATEST_SNAPSHOT \
  --db-instance-class db.t3.small \
  --db-subnet-group-name ai-code-reviewer-test-db-subnet-group

# 3. Wait for restore
aws rds wait db-instance-available \
  --db-instance-identifier ai-code-reviewer-test-restore

# 4. Verify data integrity
TEST_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-test-restore \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

psql -h $TEST_ENDPOINT -U dbadmin -d ai_code_reviewer <<EOF
-- Check row counts
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'analysis_results', COUNT(*) FROM analysis_results;

-- Check data recency
SELECT MAX(created_at) as latest_record FROM analysis_results;

-- Verify referential integrity
SELECT COUNT(*) FROM projects p
LEFT JOIN users u ON p.owner_id = u.id
WHERE u.id IS NULL;
-- Expected: 0 (no orphaned records)
EOF

# 5. Clean up test environment
aws rds delete-db-instance \
  --db-instance-identifier ai-code-reviewer-test-restore \
  --skip-final-snapshot

terraform workspace select default
terraform workspace delete dr-test
```

**Success Criteria:**
- [ ] Restore completed within 60 minutes
- [ ] All tables present with expected row counts
- [ ] Latest data within 24 hours of current time
- [ ] No referential integrity violations
- [ ] Sample queries return expected results

### Test 3: Application Failover (Quarterly)

**Objective**: Verify complete application can failover to DR region within RTO.

**Procedure:**
```bash
# 1. Schedule test during maintenance window
# Notify stakeholders 1 week in advance

# 2. Document start time
echo "DR Test Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" > dr-test-log.txt

# 3. Execute Recovery Procedure 1 (Complete Region Failure)
# Follow all steps in the procedure
# Document time for each step

# 4. Verify application functionality
./run-smoke-tests.sh --environment dr

# 5. Run load test
artillery run load-test-config.yml --target https://dr.ai-code-reviewer.com

# 6. Monitor for 2 hours
# Check error rates, response times, database performance

# 7. Failback to primary region
# Reverse DNS changes
# Shut down DR environment

# 8. Document results
echo "DR Test Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> dr-test-log.txt
# Calculate total time
# Document any issues encountered
```

**Success Criteria:**
- [ ] Total recovery time < 4 hours (RTO)
- [ ] Data loss < 1 hour (RPO)
- [ ] All smoke tests pass
- [ ] Load test shows acceptable performance
- [ ] No critical errors during 2-hour monitoring
- [ ] Successful failback to primary region

### Test 4: Full DR Exercise (Annually)

**Objective**: Validate entire DR plan with all teams participating.

**Procedure:**
1. **Planning (2 weeks before)**
   - Schedule 8-hour exercise
   - Notify all participants
   - Prepare test scenario
   - Set up monitoring and communication channels

2. **Execution (8 hours)**
   - Simulate disaster scenario
   - Activate DR plan
   - Execute all recovery procedures
   - Test communication protocols
   - Verify all systems operational

3. **Validation (2 hours)**
   - Run comprehensive test suite
   - Verify data integrity
   - Test all application features
   - Validate monitoring and alerting

4. **Debrief (2 hours)**
   - Review timeline and performance
   - Identify issues and gaps
   - Document lessons learned
   - Update DR procedures

**Success Criteria:**
- [ ] RTO < 4 hours achieved
- [ ] RPO < 1 hour achieved
- [ ] All teams executed their roles effectively
- [ ] Communication protocols worked
- [ ] All systems fully operational
- [ ] Comprehensive test results documented
- [ ] Action items identified for improvement

### Test 5: Tabletop Exercise (Semi-annually)

**Objective**: Validate roles, responsibilities, and communication without actual failover.

**Procedure:**
1. Gather all DR team members
2. Present disaster scenario
3. Walk through response procedures
4. Discuss decision points and escalations
5. Verify contact information current
6. Review and update DR documentation

**Success Criteria:**
- [ ] All team members understand their roles
- [ ] Contact information verified and updated
- [ ] Decision-making process clear
- [ ] Communication channels tested
- [ ] DR documentation reviewed and updated


## Roles and Responsibilities

### DR Team Structure

```
                    ┌─────────────────────┐
                    │ Incident Commander  │
                    │  (VP Engineering)   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼────────┐ ┌────▼─────────┐ ┌───▼──────────────┐
    │ Technical Lead   │ │ Comms Lead   │ │ Business Lead    │
    │ (Senior DevOps)  │ │ (Product Mgr)│ │ (Director Ops)   │
    └─────────┬────────┘ └──────────────┘ └──────────────────┘
              │
    ┌─────────┼─────────┬─────────────┐
    │         │         │             │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐ ┌─────▼─────┐
│DevOps │ │ DBA  │ │Backend │ │ Frontend  │
│Engineer│ │      │ │ Dev    │ │ Dev       │
└────────┘ └──────┘ └────────┘ └───────────┘
```

### Role Definitions

#### Incident Commander
**Primary**: VP Engineering  
**Backup**: Director of Engineering

**Responsibilities:**
- Declare disaster and activate DR plan
- Make final decisions on recovery strategy
- Coordinate all recovery activities
- Approve major changes (DNS updates, infrastructure changes)
- Communicate with executive leadership
- Declare recovery complete

**Authority:**
- Authorize emergency spending
- Override normal change management processes
- Mobilize additional resources

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Technical Lead
**Primary**: Senior DevOps Engineer  
**Backup**: Lead Backend Developer

**Responsibilities:**
- Execute technical recovery procedures
- Coordinate technical team members
- Make technical decisions within scope
- Monitor recovery progress
- Escalate issues to Incident Commander
- Document technical actions taken

**Authority:**
- Execute recovery procedures
- Assign tasks to technical team
- Make infrastructure changes

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Communications Lead
**Primary**: Product Manager  
**Backup**: Customer Success Manager

**Responsibilities:**
- Notify stakeholders of disaster
- Provide regular status updates
- Update status page
- Communicate with customers
- Coordinate with PR/Marketing
- Document timeline and communications

**Authority:**
- Send customer communications
- Update public status page
- Coordinate with media (with approval)

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Business Lead
**Primary**: Director of Operations  
**Backup**: VP Product

**Responsibilities:**
- Assess business impact
- Prioritize recovery activities
- Coordinate with business stakeholders
- Make business continuity decisions
- Approve customer communications
- Document business impact

**Authority:**
- Prioritize which services to restore first
- Approve customer compensation
- Make business continuity decisions

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### DevOps Engineer
**Primary**: [Name]  
**Backup**: [Name]

**Responsibilities:**
- Execute infrastructure recovery
- Deploy Terraform configurations
- Manage AWS resources
- Configure networking and security
- Monitor infrastructure health

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Database Administrator
**Primary**: [Name]  
**Backup**: [Name]

**Responsibilities:**
- Restore database backups
- Verify data integrity
- Optimize database performance
- Monitor database health
- Coordinate with Neo4j support

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Backend Developer
**Primary**: [Name]  
**Backup**: [Name]

**Responsibilities:**
- Deploy application code
- Verify API functionality
- Monitor application logs
- Fix application issues
- Run smoke tests

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

#### Frontend Developer
**Primary**: [Name]  
**Backup**: [Name]

**Responsibilities:**
- Deploy frontend application
- Verify UI functionality
- Test user workflows
- Monitor frontend errors
- Update DNS if needed

**Contact:**
- Primary: [Name] - [Phone] - [Email]
- Backup: [Name] - [Phone] - [Email]

### Escalation Matrix

| Issue | First Contact | Escalate To | Escalate Time |
|-------|--------------|-------------|---------------|
| Technical blocker | Technical Lead | Incident Commander | 30 minutes |
| AWS support needed | DevOps Engineer | Technical Lead | 15 minutes |
| Database issue | DBA | Technical Lead | 30 minutes |
| Customer impact | Comms Lead | Business Lead | Immediate |
| Budget approval | Incident Commander | CFO | Immediate |
| Legal issue | Incident Commander | General Counsel | Immediate |
| Media inquiry | Comms Lead | PR/Marketing | Immediate |

### On-Call Rotation

**Primary On-Call**: Rotates weekly  
**Secondary On-Call**: Rotates weekly (different person)

**On-Call Responsibilities:**
- Monitor alerts 24/7
- Respond within 15 minutes
- Assess severity and escalate if needed
- Activate DR plan if disaster declared

**Current On-Call Schedule:**
- View in PagerDuty: [URL]
- View in Slack: `/oncall`


## Communication Plan

### Communication Channels

#### Internal Communication

**Primary**: Slack #incident-response channel  
**Backup**: Conference bridge: [Phone number] / [Zoom link]  
**Documentation**: Google Doc (shared in Slack)

**Slack Channel Setup:**
```
Channel: #incident-response
Purpose: Real-time coordination during disasters
Members: All DR team members + executives
Notifications: @channel for critical updates
```

**Conference Bridge:**
- Always available 24/7
- No reservation required
- Record for documentation

#### External Communication

**Status Page**: https://status.ai-code-reviewer.com  
**Customer Email**: support@ai-code-reviewer.com  
**Twitter**: @AICodeReviewer  
**Support Portal**: https://support.ai-code-reviewer.com

### Communication Templates

#### Template 1: Disaster Declaration

**Subject**: [DISASTER] System Outage - DR Plan Activated

**Internal (Slack):**
```
@channel DISASTER DECLARED

Time: [UTC timestamp]
Severity: Critical
Impact: [Complete outage / Partial outage / Degraded performance]
Affected: [All users / Specific region / Specific features]

Incident Commander: [Name]
Technical Lead: [Name]
Comms Lead: [Name]

War Room: #incident-response
Conference: [Bridge number]
Status Doc: [Google Doc link]

Next update in 30 minutes.
```

**External (Status Page):**
```
We are currently experiencing a major service disruption affecting [scope].
Our team has activated disaster recovery procedures and is working to restore service.

Started: [Time]
Expected Resolution: [Time + 4 hours]
Next Update: [Time + 30 minutes]

We apologize for the inconvenience and will provide updates every 30 minutes.
```

#### Template 2: Progress Update

**Internal (Slack):**
```
UPDATE - [HH:MM] elapsed

Progress:
✓ [Completed step]
✓ [Completed step]
⏳ [In progress step] - ETA [time]
⏸ [Pending step]

Blockers: [None / Description]
ETA to recovery: [time]

Next update in 30 minutes.
```

**External (Status Page):**
```
Update [HH:MM] - Recovery in progress

We have completed [X] of [Y] recovery steps.
Current status: [Brief description]

Expected resolution: [Updated ETA]
Next update: [Time]
```

#### Template 3: Recovery Complete

**Internal (Slack):**
```
@channel RECOVERY COMPLETE

Disaster Start: [Time]
Recovery Complete: [Time]
Total Duration: [HH:MM]
Data Loss: [None / X minutes]

Status: All systems operational
Monitoring: Enhanced monitoring for 24 hours

Post-Mortem: Scheduled for [Date/Time]
Thank you team! 🎉
```

**External (Status Page):**
```
RESOLVED - Service Restored

Our disaster recovery procedures have been completed successfully.
All systems are now operational.

Incident Duration: [HH:MM]
Root Cause: [Brief description]

We apologize for the disruption. A detailed post-mortem will be published within 5 business days.

Thank you for your patience.
```

#### Template 4: Customer Email

**Subject**: Service Disruption - [Date] - Post-Mortem

**Body:**
```
Dear Valued Customer,

On [Date] at [Time UTC], we experienced a service disruption that affected [scope].
Our disaster recovery procedures were activated, and service was fully restored at [Time UTC].

Incident Summary:
- Start Time: [Time UTC]
- End Time: [Time UTC]
- Duration: [HH:MM]
- Impact: [Description]
- Data Loss: [None / Minimal - X minutes]

Root Cause:
[Brief explanation]

Resolution:
[Brief explanation of recovery]

Preventive Measures:
[Actions taken to prevent recurrence]

We sincerely apologize for any inconvenience this may have caused. If you have any questions or concerns, please contact our support team at support@ai-code-reviewer.com.

Thank you for your understanding and continued trust.

Best regards,
[Name]
[Title]
AI Code Reviewer Team
```

### Communication Schedule

| Time from Disaster | Internal Update | External Update | Audience |
|-------------------|-----------------|-----------------|----------|
| T+0 (Immediate) | Disaster declaration | Status page update | All |
| T+15 min | Initial assessment | Status page update | All |
| T+30 min | Progress update | Status page update | All |
| Every 30 min | Progress update | Status page update | All |
| T+1 hour | Detailed update | Email to customers | Customers |
| Recovery complete | Final update | Status page + email | All |
| T+24 hours | Post-incident review | Internal only | Team |
| T+5 days | Post-mortem | Public post-mortem | All |

### Stakeholder Notification List

**Immediate Notification (within 15 minutes):**
- [ ] CEO
- [ ] CTO
- [ ] VP Engineering
- [ ] VP Product
- [ ] Director of Operations
- [ ] Customer Success Lead

**Regular Updates (every 30 minutes):**
- [ ] All executives
- [ ] All DR team members
- [ ] Customer success team
- [ ] Support team

**Post-Recovery Notification:**
- [ ] All employees
- [ ] Board of Directors
- [ ] Key customers (enterprise accounts)
- [ ] Partners and integrations

### External Vendor Contacts

**AWS Support:**
- Enterprise Support: 1-800-xxx-xxxx
- Support Portal: https://console.aws.amazon.com/support/
- Account Manager: [Name] - [Email] - [Phone]

**Neo4j Support:**
- Enterprise Support: support@neo4j.com
- Emergency Phone: [Phone number]
- Account Manager: [Name] - [Email] - [Phone]

**GitHub Support:**
- Enterprise Support: https://support.github.com/
- Account Manager: [Name] - [Email]

**DNS Provider:**
- Support: [Contact info]
- Emergency: [Phone number]


## Post-Recovery Validation

### Validation Checklist

After recovery is complete, validate all systems before declaring success.

#### Infrastructure Validation

```bash
# 1. Verify all EC2 instances are healthy
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-code-reviewer-*-asg \
  --query 'AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity,Instances[*].[InstanceId,HealthStatus]]'

# Expected: All instances show "Healthy"

# 2. Verify Load Balancer targets are healthy
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:*:*:targetgroup/* \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]'

# Expected: All targets show "healthy"

# 3. Verify security groups are correct
aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=ai-code-reviewer" \
  --query 'SecurityGroups[*].[GroupId,GroupName,IpPermissions]'

# Expected: Only necessary ports open (443, 5432, 6379, 7687)

# 4. Verify VPC and networking
aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=ai-code-reviewer" \
  --query 'Vpcs[*].[VpcId,CidrBlock,State]'

# Expected: VPC in "available" state
```

#### Database Validation

```bash
# 1. PostgreSQL connectivity and data
psql -h $RDS_ENDPOINT -U dbadmin -d ai_code_reviewer <<EOF
-- Check connectivity
SELECT version();

-- Check row counts
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'analysis_results', COUNT(*) FROM analysis_results
UNION ALL
SELECT 'audit_log_entries', COUNT(*) FROM audit_log_entries;

-- Check data recency
SELECT 
  'users' as table_name, 
  MAX(created_at) as latest_record,
  NOW() - MAX(created_at) as age
FROM users
UNION ALL
SELECT 'projects', MAX(created_at), NOW() - MAX(created_at) FROM projects
UNION ALL
SELECT 'analysis_results', MAX(created_at), NOW() - MAX(created_at) FROM analysis_results;

-- Verify referential integrity
SELECT 
  'orphaned_projects' as check_name,
  COUNT(*) as count
FROM projects p
LEFT JOIN users u ON p.owner_id = u.id
WHERE u.id IS NULL;

-- Check for duplicate data
SELECT 
  'duplicate_users' as check_name,
  COUNT(*) as count
FROM (
  SELECT email, COUNT(*) as cnt
  FROM users
  GROUP BY email
  HAVING COUNT(*) > 1
) duplicates;
EOF

# 2. Redis connectivity and data
redis-cli -h $REDIS_ENDPOINT -p 6379 --tls -a "$REDIS_AUTH_TOKEN" <<EOF
PING
INFO replication
DBSIZE
KEYS session:* | head -10
EOF

# 3. Neo4j connectivity and data
cypher-shell -a $NEO4J_URI -u neo4j -p "$NEO4J_PASSWORD" <<EOF
// Check connectivity
CALL dbms.components() YIELD name, versions, edition;

// Check node counts
MATCH (n) RETURN labels(n) as label, count(*) as count;

// Check relationship counts
MATCH ()-[r]->() RETURN type(r) as type, count(*) as count;

// Check data recency
MATCH (n) WHERE n.created_at IS NOT NULL 
RETURN max(n.created_at) as latest_record;

// Verify graph integrity
MATCH (n) WHERE NOT (n)--() 
RETURN labels(n) as isolated_nodes, count(*) as count;
EOF
```

#### Application Validation

```bash
# 1. Health check endpoints
curl -f https://app.ai-code-reviewer.com/health
curl -f https://app.ai-code-reviewer.com/api/health
curl -f https://app.ai-code-reviewer.com/api/v1/health

# Expected: All return 200 OK with healthy status

# 2. Run smoke tests
cd /path/to/tests
./run-smoke-tests.sh --environment prod

# Expected: All smoke tests pass

# 3. Test authentication
curl -X POST https://app.ai-code-reviewer.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Expected: Returns JWT token

# 4. Test API endpoints
TOKEN="<jwt-token-from-above>"

curl -H "Authorization: Bearer $TOKEN" \
  https://app.ai-code-reviewer.com/api/v1/projects

# Expected: Returns project list

# 5. Test GitHub webhook
curl -X POST https://app.ai-code-reviewer.com/api/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=test" \
  -d '{"action":"opened","pull_request":{"id":1}}'

# Expected: Returns 200 (or 401 if signature invalid, which is expected)

# 6. Test frontend
curl -f https://app.ai-code-reviewer.com/
curl -f https://app.ai-code-reviewer.com/login
curl -f https://app.ai-code-reviewer.com/projects

# Expected: All return 200 OK
```

#### Monitoring Validation

```bash
# 1. Verify CloudWatch logs are flowing
aws logs describe-log-streams \
  --log-group-name /aws/ec2/ai-code-reviewer \
  --order-by LastEventTime \
  --descending \
  --max-items 5

# Expected: Recent log streams with recent lastEventTime

# 2. Verify CloudWatch metrics are being collected
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=app/ai-code-reviewer-alb/* \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Expected: Recent datapoints

# 3. Verify alarms are active
aws cloudwatch describe-alarms \
  --alarm-name-prefix ai-code-reviewer \
  --query 'MetricAlarms[*].[AlarmName,StateValue]'

# Expected: All alarms in OK or INSUFFICIENT_DATA state (not ALARM)

# 4. Test alert notifications
aws sns publish \
  --topic-arn arn:aws:sns:*:*:ai-code-reviewer-alerts \
  --message "DR Test: Alert notification test" \
  --subject "DR Test Alert"

# Expected: Alert received via email/Slack
```

#### Performance Validation

```bash
# 1. Run load test
cd /path/to/tests
artillery run load-test-config.yml --target https://app.ai-code-reviewer.com

# Expected: 
# - P95 response time < 500ms
# - Error rate < 1%
# - All requests complete successfully

# 2. Check database performance
psql -h $RDS_ENDPOINT -U dbadmin -d ai_code_reviewer <<EOF
-- Check slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check connection count
SELECT COUNT(*) as active_connections
FROM pg_stat_activity
WHERE state = 'active';
EOF

# 3. Check Redis performance
redis-cli -h $REDIS_ENDPOINT -p 6379 --tls -a "$REDIS_AUTH_TOKEN" INFO stats

# Expected:
# - Hit rate > 80%
# - Evicted keys = 0
# - Rejected connections = 0
```

### Validation Sign-Off

After completing all validation checks, obtain sign-off from:

- [ ] **Technical Lead**: All technical systems validated
- [ ] **DBA**: All databases validated and performing well
- [ ] **DevOps Engineer**: All infrastructure validated
- [ ] **Backend Developer**: All APIs validated
- [ ] **Frontend Developer**: All UI functionality validated
- [ ] **Incident Commander**: Overall recovery validated

**Sign-Off Template:**
```
DISASTER RECOVERY VALIDATION COMPLETE

Disaster: [Description]
Recovery Start: [Time]
Recovery Complete: [Time]
Total Duration: [HH:MM]

Validation Results:
✓ Infrastructure: All systems healthy
✓ Databases: All databases operational and validated
✓ Application: All APIs and UI functional
✓ Monitoring: All monitoring and alerting operational
✓ Performance: Performance within acceptable limits

Data Loss: [None / X minutes]
RTO Achieved: [HH:MM] (Target: 4 hours)
RPO Achieved: [X minutes] (Target: 1 hour)

Issues Encountered:
[List any issues and how they were resolved]

Recommendations:
[List any improvements to DR procedures]

Signed:
- Technical Lead: [Name] - [Time]
- Incident Commander: [Name] - [Time]

Status: RECOVERY VALIDATED - SYSTEM OPERATIONAL
```


## Appendices

### Appendix A: Quick Reference Card

**Print this page and keep it accessible**

#### Emergency Contacts

| Role | Primary | Phone | Email |
|------|---------|-------|-------|
| Incident Commander | [Name] | [Phone] | [Email] |
| Technical Lead | [Name] | [Phone] | [Email] |
| Comms Lead | [Name] | [Phone] | [Email] |
| On-Call (Current) | Check PagerDuty | - | - |

#### Critical Information

**Primary Region**: us-east-1  
**DR Region**: us-west-2  
**Status Page**: https://status.ai-code-reviewer.com  
**War Room**: Slack #incident-response  
**Conference Bridge**: [Phone] / [Zoom link]

#### Recovery Objectives

- **RTO**: 4 hours
- **RPO**: 1 hour

#### Quick Commands

```bash
# Check AWS region health
aws ec2 describe-instances --region us-east-1 --max-results 1

# List latest backups
aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --max-records 3

# Check application health
curl -f https://app.ai-code-reviewer.com/health

# View DR procedures
cat /path/to/DISASTER_RECOVERY_PROCEDURES.md
```

#### Decision Tree

```
Is the system down?
├─ Yes → Is it a complete region failure?
│  ├─ Yes → Execute Recovery Procedure 1 (Region Failure)
│  └─ No → Is it a database issue?
│     ├─ Yes → Execute Recovery Procedure 2 (Database)
│     └─ No → Execute Recovery Procedure 3 (Application)
└─ No → Is performance degraded?
   ├─ Yes → Investigate and monitor
   └─ No → False alarm, document and close
```

### Appendix B: AWS Resource Identifiers

**Production Environment (us-east-1)**

| Resource Type | Identifier | Name |
|--------------|------------|------|
| VPC | vpc-xxxxx | ai-code-reviewer-prod-vpc |
| RDS Instance | ai-code-reviewer-prod-postgres | PostgreSQL |
| Redis Group | ai-code-reviewer-prod-redis | ElastiCache |
| Auto Scaling Group | ai-code-reviewer-prod-asg | Application Servers |
| Load Balancer | ai-code-reviewer-prod-alb | Application LB |
| Security Group (DB) | sg-xxxxx | Database SG |
| Security Group (App) | sg-xxxxx | Application SG |
| S3 Bucket (Backups) | ai-code-reviewer-prod-backups | Backup Storage |

**DR Environment (us-west-2)**

| Resource Type | Identifier | Name |
|--------------|------------|------|
| S3 Bucket (Backups) | ai-code-reviewer-dr-backups | DR Backup Storage |
| KMS Key | arn:aws:kms:us-west-2:xxx:key/xxx | DR Encryption Key |

### Appendix C: Database Connection Strings

**Production (us-east-1)**

```bash
# PostgreSQL
export POSTGRES_HOST="ai-code-reviewer-prod-postgres.xxxxx.us-east-1.rds.amazonaws.com"
export POSTGRES_PORT="5432"
export POSTGRES_DB="ai_code_reviewer"
export POSTGRES_USER="dbadmin"
# Password in Secrets Manager: ai-code-reviewer/prod/database

# Redis
export REDIS_HOST="ai-code-reviewer-prod-redis.xxxxx.cache.amazonaws.com"
export REDIS_PORT="6379"
# Auth token in Secrets Manager: ai-code-reviewer/prod/redis

# Neo4j
export NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io"
export NEO4J_USER="neo4j"
# Password in Secrets Manager: ai-code-reviewer/prod/neo4j
```

### Appendix D: Terraform Commands

```bash
# Initialize Terraform
cd /path/to/terraform
terraform init

# Switch to DR region
terraform workspace new dr
terraform workspace select dr

# Plan DR deployment
terraform plan -var="region=us-west-2" -var="environment=dr" -out=dr.tfplan

# Apply DR deployment
terraform apply dr.tfplan

# Destroy DR environment (after failback)
terraform destroy -var="region=us-west-2" -var="environment=dr"

# View current state
terraform show

# List all resources
terraform state list
```

### Appendix E: Monitoring Dashboards

**CloudWatch Dashboards**

- System Health: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ai-code-reviewer-health
- Performance: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ai-code-reviewer-performance
- Database: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ai-code-reviewer-database

**Key Metrics to Monitor**

| Metric | Normal Range | Alert Threshold |
|--------|-------------|-----------------|
| API Response Time (P95) | < 300ms | > 500ms |
| Error Rate | < 0.5% | > 5% |
| CPU Utilization | < 60% | > 80% |
| Memory Utilization | < 70% | > 85% |
| Database Connections | < 50 | > 80 |
| Cache Hit Rate | > 85% | < 70% |

### Appendix F: Post-Mortem Template

**Incident Post-Mortem**

**Incident ID**: [YYYY-MM-DD-XXX]  
**Date**: [Date]  
**Duration**: [HH:MM]  
**Severity**: [Critical / High / Medium]

**Summary**
[Brief description of what happened]

**Timeline**
| Time (UTC) | Event |
|------------|-------|
| HH:MM | [Event description] |
| HH:MM | [Event description] |

**Impact**
- Users Affected: [Number / Percentage]
- Services Affected: [List]
- Data Loss: [None / Description]
- Revenue Impact: [Amount]

**Root Cause**
[Detailed explanation of what caused the incident]

**Resolution**
[How the incident was resolved]

**What Went Well**
- [Item]
- [Item]

**What Went Wrong**
- [Item]
- [Item]

**Action Items**
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | [ ] |

**Lessons Learned**
[Key takeaways and improvements]

### Appendix G: Compliance and Audit

**Regulatory Requirements**

This DR plan addresses the following compliance requirements:

- **SOC 2 Type II**: Business continuity and disaster recovery
- **ISO 27001**: Information security incident management
- **GDPR**: Data protection and breach notification
- **HIPAA** (if applicable): Contingency planning and disaster recovery

**Audit Trail**

All disaster recovery activities must be logged:

```bash
# Log all commands executed
script -a dr-audit-$(date +%Y%m%d-%H%M).log

# All commands will be recorded in the log file
# Include timestamps and operator names

# Example log entry format:
# [2024-01-15 14:30:00 UTC] [operator@hostname] command executed
```

**Required Documentation**

After each DR event or test:
- [ ] Timeline of events
- [ ] Commands executed
- [ ] Decisions made and rationale
- [ ] Issues encountered
- [ ] Validation results
- [ ] Post-mortem report
- [ ] Updated procedures (if needed)

### Appendix H: Vendor SLAs

**AWS Service Level Agreements**

| Service | SLA | Compensation |
|---------|-----|--------------|
| EC2 | 99.99% | 10% credit if < 99.99% |
| RDS | 99.95% | 10% credit if < 99.95% |
| ElastiCache | 99.99% | 10% credit if < 99.99% |
| ELB | 99.99% | 10% credit if < 99.99% |

**Neo4j Aura SLA**

| Tier | SLA | Support Response |
|------|-----|------------------|
| Enterprise | 99.95% | < 1 hour for P1 |

**Support Escalation**

For AWS:
1. Open support case (Enterprise Support)
2. Mark as "Production system down"
3. Request callback
4. Escalate to TAM if no response in 15 minutes

For Neo4j:
1. Email support@neo4j.com with "URGENT" in subject
2. Call emergency support line
3. Escalate to account manager if no response in 30 minutes

### Appendix I: Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 1.0 | Initial disaster recovery procedures | DevOps Team |
| | | | |
| | | | |

**Review Schedule**: Quarterly  
**Next Review**: 2024-04-15

---

## Document Approval

**Prepared By**: DevOps Team  
**Reviewed By**: [Name], VP Engineering  
**Approved By**: [Name], CTO  
**Date**: 2024-01-15

**Distribution List**:
- All Engineering Team Members
- Operations Team
- Executive Leadership
- Compliance Team

---

**END OF DOCUMENT**

For questions or updates to this document, contact: devops@ai-code-reviewer.com

