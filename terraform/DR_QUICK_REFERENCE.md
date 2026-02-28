# Disaster Recovery Quick Reference

**PRINT THIS PAGE AND KEEP IT ACCESSIBLE**

## Emergency Contacts

| Role | Primary Contact | Phone | Email |
|------|----------------|-------|-------|
| **Incident Commander** | [Name] | [Phone] | [Email] |
| **Technical Lead** | [Name] | [Phone] | [Email] |
| **Communications Lead** | [Name] | [Phone] | [Email] |
| **On-Call Engineer** | Check PagerDuty | - | - |

## Critical Information

- **Primary Region**: us-east-1 (N. Virginia)
- **DR Region**: us-west-2 (Oregon)
- **RTO Target**: 4 hours
- **RPO Target**: 1 hour
- **Status Page**: https://status.ai-code-reviewer.com
- **War Room**: Slack #incident-response
- **Conference Bridge**: [Phone] / [Zoom link]

## Decision Tree

```
┌─ Is the system completely down? ─────────────────────────┐
│                                                           │
├─ YES → Is entire AWS region unavailable?                 │
│   ├─ YES → EXECUTE: Recovery Procedure 1 (Region Failure)│
│   │        Full DR failover to us-west-2                 │
│   │        ETA: 3-4 hours                                │
│   │                                                       │
│   └─ NO → Is it a database issue?                        │
│       ├─ YES → EXECUTE: Recovery Procedure 2 (Database)  │
│       │        Restore from backup                       │
│       │        ETA: 1-2 hours                            │
│       │                                                   │
│       └─ NO → EXECUTE: Recovery Procedure 3 (Application)│
│               Recreate infrastructure                    │
│               ETA: 30-60 minutes                         │
│                                                           │
└─ NO → Is performance severely degraded?                  │
    ├─ YES → Investigate and monitor                       │
    │         May need to scale up                         │
    │                                                       │
    └─ NO → False alarm                                    │
            Document and close                             │
└───────────────────────────────────────────────────────────┘
```

## Quick Health Checks

```bash
# 1. Check if AWS region is accessible
aws ec2 describe-instances --region us-east-1 --max-results 1

# 2. Check application health
curl -f https://app.ai-code-reviewer.com/health

# 3. Check database connectivity
psql -h <rds-endpoint> -U dbadmin -d ai_code_reviewer -c "SELECT 1;"

# 4. Check recent backups
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].LatestRestorableTime'
```

## Disaster Declaration Checklist

- [ ] Verify system is actually down (not false alarm)
- [ ] Check AWS Service Health Dashboard
- [ ] Estimate impact (all users / partial / specific features)
- [ ] Notify Incident Commander
- [ ] Post in Slack #incident-response: "@channel DISASTER DECLARED"
- [ ] Update status page: "Major service disruption"
- [ ] Join conference bridge
- [ ] Start documenting timeline

## Recovery Procedure 1: Complete Region Failure

**Use when**: Primary AWS region (us-east-1) is completely unavailable

**Steps**:
1. **Declare disaster** (15 min) - Notify team, establish war room
2. **Prepare DR region** (30 min) - Switch to us-west-2, prepare Terraform
3. **Restore databases** (90 min) - Restore RDS, Redis, Neo4j from backups
4. **Deploy infrastructure** (45 min) - Apply Terraform in DR region
5. **Deploy application** (30 min) - Build and deploy application code
6. **Update DNS** (15 min) - Point DNS to new Load Balancer
7. **Verify and monitor** (30 min) - Run smoke tests, validate
8. **Notify stakeholders** (15 min) - Send recovery complete notification

**Total Time**: 3-4 hours

## Recovery Procedure 2: Database Corruption

**Use when**: Database is corrupted but infrastructure is intact

**Steps**:
1. Stop application traffic (5 min)
2. Create snapshot of corrupted DB (10 min)
3. Identify last good backup (5 min)
4. Restore to new instance (60 min)
5. Verify restored data (15 min)
6. Update application config (10 min)
7. Re-enable traffic (5 min)
8. Monitor and verify (15 min)

**Total Time**: 1-2 hours

## Recovery Procedure 3: Application Failure

**Use when**: EC2/ASG/ALB failure but databases are intact

**Steps**:
1. Assess infrastructure status (5 min)
2. Recreate infrastructure with Terraform (30 min)
3. Force instance refresh (15 min)
4. Verify application (10 min)

**Total Time**: 30-60 minutes

## Key Commands

### Check Backup Status
```bash
# PostgreSQL
aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --max-records 5

# Redis
aws elasticache describe-snapshots \
  --replication-group-id ai-code-reviewer-prod-redis \
  --max-records 5
```

### Restore Database
```bash
# PostgreSQL - Point-in-time restore
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier ai-code-reviewer-prod-postgres \
  --target-db-instance-identifier ai-code-reviewer-restored \
  --restore-time "2024-01-15T02:30:00Z" \
  --region us-west-2

# Redis - Restore from snapshot
aws elasticache create-replication-group \
  --replication-group-id ai-code-reviewer-restored-redis \
  --snapshot-name <snapshot-name> \
  --cache-node-type cache.t3.small \
  --region us-west-2
```

### Deploy Infrastructure
```bash
cd /path/to/terraform
terraform workspace select dr
terraform plan -var="region=us-west-2" -out=dr.tfplan
terraform apply dr.tfplan
```

### Update DNS
```bash
# Get new Load Balancer DNS
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names ai-code-reviewer-dr-alb \
  --region us-west-2 \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

# Update Route 53
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
```

## Communication Templates

### Disaster Declaration (Slack)
```
@channel DISASTER DECLARED

Time: [UTC timestamp]
Severity: Critical
Impact: [Description]

Incident Commander: [Name]
Technical Lead: [Name]

War Room: #incident-response
Conference: [Bridge]

Next update in 30 minutes.
```

### Status Page Update
```
We are experiencing a major service disruption.
Disaster recovery procedures activated.

Started: [Time]
Expected Resolution: [Time + 4 hours]
Next Update: [Time + 30 minutes]
```

## Vendor Support

### AWS Support
- **Phone**: 1-800-xxx-xxxx (Enterprise Support)
- **Portal**: https://console.aws.amazon.com/support/
- **Severity**: Mark as "Production system down"

### Neo4j Support
- **Email**: support@neo4j.com (Subject: "URGENT - Production DR")
- **Phone**: [Emergency support number]

## Monitoring During Recovery

```bash
# Watch Auto Scaling Group status
watch -n 30 'aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-code-reviewer-*-asg \
  --query "AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity,Instances[*].HealthStatus]"'

# Watch Load Balancer targets
watch -n 10 'aws elbv2 describe-target-health \
  --target-group-arn <arn> \
  --query "TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]"'

# Watch application logs
aws logs tail /aws/ec2/ai-code-reviewer --follow
```

## Post-Recovery Checklist

- [ ] All health checks passing
- [ ] Smoke tests completed successfully
- [ ] Database queries returning correct data
- [ ] Monitoring and alerting operational
- [ ] DNS propagated (check with `dig`)
- [ ] Load test shows acceptable performance
- [ ] Status page updated to "Resolved"
- [ ] Stakeholders notified
- [ ] Post-mortem scheduled

## Important Notes

⚠️ **DO NOT PANIC** - Follow procedures step by step  
⚠️ **DOCUMENT EVERYTHING** - Record all actions and timestamps  
⚠️ **COMMUNICATE REGULARLY** - Update every 30 minutes  
⚠️ **ASK FOR HELP** - Escalate if stuck for > 30 minutes  
⚠️ **VERIFY BEFORE DECLARING SUCCESS** - Run all validation checks  

## Full Documentation

For detailed procedures, see: `DISASTER_RECOVERY_PROCEDURES.md`

---

**Last Updated**: 2024-01-15  
**Next Review**: 2024-04-15  
**Contact**: devops@ai-code-reviewer.com
