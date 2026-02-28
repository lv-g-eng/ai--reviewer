# Database Backup Configuration Guide

This document provides detailed information about the automated backup configuration for all databases in the AI-Based Code Reviewer platform.

## Overview

The system implements automated backups for all three databases with 7-day retention, meeting requirements 4.9 and 11.2:

- **Requirement 4.9**: Configure automated backups with 7-day retention for all databases
- **Requirement 11.2**: Implement data backup procedures running daily at 2 AM UTC

## Backup Configuration Summary

| Database | Backup Type | Schedule | Retention | Encryption | Status |
|----------|-------------|----------|-----------|------------|--------|
| PostgreSQL RDS | Automated Backup | Daily 02:00-03:00 UTC | 7 days | AES-256 (KMS) | ✓ Enabled |
| ElastiCache Redis | Automated Snapshot | Daily 02:00-04:00 UTC | 7 days | AES-256 (KMS) | ✓ Enabled |
| Neo4j AuraDB | Continuous Backup | Managed by Aura | Aura-managed | AES-256 | ✓ Enabled |

## RDS PostgreSQL Backup Configuration

### Automated Backups

The RDS PostgreSQL instance is configured with automated backups:

```hcl
backup_retention_period   = 7  # 7-day retention
backup_window             = "02:00-03:00"  # Daily at 2 AM UTC
copy_tags_to_snapshot     = true
skip_final_snapshot       = false  # Production only
```

### Features

- **Daily Automated Backups**: Runs during the 02:00-03:00 UTC window
- **7-Day Retention**: Backups are retained for 7 days
- **Point-in-Time Recovery**: Restore to any point within the retention period
- **Encryption**: All backups encrypted using AWS KMS
- **Final Snapshot**: Created before instance deletion (production only)
- **Multi-AZ**: Backups taken from standby instance to minimize performance impact

### Backup Window

The backup window is set to 02:00-03:00 UTC (2 AM UTC) to minimize impact during low-traffic hours. This window is separate from the maintenance window (Monday 03:30-04:30 UTC).

### Verification

```bash
# Check backup configuration
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].[BackupRetentionPeriod,PreferredBackupWindow,LatestRestorableTime]'

# List available automated backups
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].LatestRestorableTime'

# List manual snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier ai-code-reviewer-prod-postgres
```

### Restore Procedures

**Point-in-Time Restore:**
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier ai-code-reviewer-prod-postgres \
  --target-db-instance-identifier ai-code-reviewer-restored-$(date +%Y%m%d) \
  --restore-time "2024-01-15T02:30:00Z" \
  --db-subnet-group-name ai-code-reviewer-prod-db-subnet-group \
  --vpc-security-group-ids sg-xxxxx
```

**Snapshot Restore:**
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-code-reviewer-restored-$(date +%Y%m%d) \
  --db-snapshot-identifier rds:ai-code-reviewer-prod-postgres-2024-01-15-02-00 \
  --db-subnet-group-name ai-code-reviewer-prod-db-subnet-group \
  --vpc-security-group-ids sg-xxxxx
```

## ElastiCache Redis Backup Configuration

### Automated Snapshots

The ElastiCache Redis replication group is configured with automated snapshots:

```hcl
snapshot_retention_limit = 7  # 7-day retention
snapshot_window          = "02:00-04:00"  # Daily at 2 AM UTC
```

### Features

- **Daily Automated Snapshots**: Runs during the 02:00-04:00 UTC window
- **7-Day Retention**: Snapshots are retained for 7 days
- **Encryption**: All snapshots encrypted at rest
- **Multi-AZ**: Snapshots taken from replica nodes to minimize performance impact
- **Manual Snapshots**: Can be created on-demand for additional protection

### Snapshot Window

The snapshot window is set to 02:00-04:00 UTC (2 AM UTC start) to align with the backup schedule. The 2-hour window provides flexibility for snapshot completion.

### Verification

```bash
# Check snapshot configuration
aws elasticache describe-replication-groups \
  --replication-group-id ai-code-reviewer-prod-redis \
  --query 'ReplicationGroups[0].[SnapshotRetentionLimit,SnapshotWindow]'

# List available snapshots
aws elasticache describe-snapshots \
  --replication-group-id ai-code-reviewer-prod-redis

# Create manual snapshot
aws elasticache create-snapshot \
  --replication-group-id ai-code-reviewer-prod-redis \
  --snapshot-name ai-code-reviewer-manual-$(date +%Y%m%d-%H%M)
```

### Restore Procedures

**Restore from Snapshot:**
```bash
aws elasticache create-replication-group \
  --replication-group-id ai-code-reviewer-restored-$(date +%Y%m%d) \
  --replication-group-description "Restored from snapshot" \
  --snapshot-name automatic.ai-code-reviewer-prod-redis-2024-01-15-02-00 \
  --cache-node-type cache.t3.small \
  --engine redis \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --cache-subnet-group-name ai-code-reviewer-prod-redis-subnet-group \
  --security-group-ids sg-xxxxx
```

## Neo4j AuraDB Backup Configuration

### Managed Backups

Neo4j AuraDB Enterprise includes automated continuous backups managed by the Neo4j Aura platform:

- **Continuous Backups**: Automatic continuous backup of all data
- **Point-in-Time Recovery**: Restore to any point in time
- **Encryption**: All backups encrypted with AES-256
- **Redundancy**: Backups stored across multiple availability zones
- **Retention**: Managed by Neo4j Aura (typically 7+ days for Enterprise)

### Features

- **Zero Configuration**: Backups are automatically enabled for all AuraDB instances
- **No Performance Impact**: Backups run continuously without affecting query performance
- **Automatic Testing**: Neo4j regularly tests backup integrity
- **Geographic Redundancy**: Backups stored in multiple regions

### Verification

1. Log in to Neo4j Aura Console: https://console.neo4j.io/
2. Select your instance
3. Navigate to "Backups" tab
4. View backup status and available restore points

### Restore Procedures

**Via Neo4j Aura Console:**
1. Log in to Neo4j Aura Console
2. Select the instance to restore
3. Click "Backups" tab
4. Select a backup or restore point
5. Click "Restore" and follow the wizard
6. Choose to restore to existing instance or create new instance

**Via Neo4j Support:**
For complex restore scenarios, contact Neo4j support:
- Email: support@neo4j.com
- Support Portal: https://support.neo4j.com/

## Backup Monitoring

### CloudWatch Alarms

The following CloudWatch alarms monitor backup health:

**RDS PostgreSQL:**
- No specific backup alarm (AWS manages backup reliability)
- Monitor `LatestRestorableTime` metric to ensure backups are current
- Storage alarms ensure sufficient space for backups

**ElastiCache Redis:**
- No specific snapshot alarm (AWS manages snapshot reliability)
- Monitor snapshot creation via CloudWatch Events

### Monitoring Commands

```bash
# Check RDS backup status
aws rds describe-db-instances \
  --db-instance-identifier ai-code-reviewer-prod-postgres \
  --query 'DBInstances[0].[BackupRetentionPeriod,LatestRestorableTime]'

# Check Redis snapshot status
aws elasticache describe-snapshots \
  --replication-group-id ai-code-reviewer-prod-redis \
  --max-records 5

# List recent snapshots with status
aws elasticache describe-snapshots \
  --replication-group-id ai-code-reviewer-prod-redis \
  --query 'Snapshots[*].[SnapshotName,SnapshotStatus,NodeSnapshots[0].SnapshotCreateTime]' \
  --output table
```

## Backup Testing

### Regular Testing Schedule

Backups should be tested regularly to ensure they can be restored successfully:

- **Monthly**: Test restore of RDS PostgreSQL to verify backup integrity
- **Quarterly**: Test restore of Redis snapshot to verify data consistency
- **Annually**: Test complete disaster recovery procedure including Neo4j

### Test Restore Procedure

1. **Identify Test Window**: Schedule during low-traffic period
2. **Create Test Environment**: Use separate VPC or account for testing
3. **Restore Backup**: Follow restore procedures above
4. **Verify Data Integrity**: Run validation queries to confirm data consistency
5. **Document Results**: Record restore time, data validation results, issues encountered
6. **Clean Up**: Delete test resources after validation

### Sample Validation Queries

**PostgreSQL:**
```sql
-- Check row counts
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'analysis_results', COUNT(*) FROM analysis_results;

-- Check recent data
SELECT MAX(created_at) as latest_record FROM analysis_results;
```

**Redis:**
```bash
# Check key count
redis-cli -h <restored-endpoint> -a <auth-token> --tls DBSIZE

# Sample keys
redis-cli -h <restored-endpoint> -a <auth-token> --tls KEYS "session:*" | head -10
```

**Neo4j:**
```cypher
// Check node counts
MATCH (n) RETURN labels(n) as label, count(*) as count;

// Check relationship counts
MATCH ()-[r]->() RETURN type(r) as type, count(*) as count;

// Check recent data
MATCH (n) WHERE n.created_at IS NOT NULL 
RETURN max(n.created_at) as latest_record;
```

## Disaster Recovery

### Recovery Time Objective (RTO)

Target: 4 hours (Requirement 4.10)

**RDS PostgreSQL:**
- Restore time: 30-60 minutes (depends on database size)
- DNS update: 5-10 minutes
- Application restart: 5-10 minutes
- Total: ~1-2 hours

**ElastiCache Redis:**
- Restore time: 15-30 minutes
- DNS update: 5-10 minutes
- Cache warming: 10-20 minutes
- Total: ~30-60 minutes

**Neo4j AuraDB:**
- Restore time: 30-90 minutes (managed by Neo4j)
- Connection update: 5-10 minutes
- Total: ~1-2 hours

### Recovery Point Objective (RPO)

Target: 1 hour (Requirement 4.10)

**RDS PostgreSQL:**
- Point-in-time recovery available within retention period
- RPO: ~5 minutes (transaction log frequency)

**ElastiCache Redis:**
- Snapshot-based recovery
- RPO: Up to 24 hours (last snapshot)
- Note: Redis is used for caching, data loss is acceptable

**Neo4j AuraDB:**
- Continuous backup with point-in-time recovery
- RPO: ~5 minutes

## Backup Costs

### Cost Estimation

**RDS PostgreSQL:**
- Backup storage: First 100GB free (equal to allocated storage)
- Additional backup storage: $0.095 per GB-month
- Estimated cost: $0-20/month (depends on database size and retention)

**ElastiCache Redis:**
- Snapshot storage: $0.085 per GB-month
- Estimated cost: $5-15/month (depends on data size)

**Neo4j AuraDB:**
- Backup included in Enterprise plan pricing
- No additional backup costs

### Cost Optimization

- Use 7-day retention (meets requirements, minimizes costs)
- Delete manual snapshots after testing
- Monitor backup storage usage via CloudWatch
- Consider shorter retention for non-production environments

## Compliance

### Requirements Met

- ✓ **Requirement 4.9**: Automated backups with 7-day retention configured for all databases
- ✓ **Requirement 11.2**: Backup procedures run daily at 2 AM UTC
- ✓ **Requirement 11.3**: All backups encrypted with AES-256
- ✓ **Requirement 4.10**: Disaster recovery procedures support RTO of 4 hours and RPO of 1 hour

### Audit Trail

All backup operations are logged to CloudWatch Logs:
- Backup start/completion events
- Snapshot creation events
- Restore operations
- Backup deletion events

Access CloudWatch Logs:
```bash
aws logs filter-log-events \
  --log-group-name /aws/rds/instance/ai-code-reviewer-prod-postgres/backup \
  --start-time $(date -d '7 days ago' +%s)000
```

## Troubleshooting

### Common Issues

**Issue: Backup window conflicts with high traffic**
- Solution: Adjust backup window in Terraform variables
- Update `backup_window` and `snapshot_window` variables
- Apply changes during maintenance window

**Issue: Insufficient storage for backups**
- Solution: Enable storage autoscaling (already configured)
- Monitor `FreeStorageSpace` CloudWatch metric
- Increase `db_max_allocated_storage` if needed

**Issue: Backup taking too long**
- Solution: Backups run on standby instance (Multi-AZ)
- No action needed unless backup window is exceeded
- Consider increasing backup window duration

**Issue: Restore fails due to parameter group mismatch**
- Solution: Specify compatible parameter group during restore
- Use same parameter group as source instance
- Modify parameter group after restore if needed

### Support Contacts

**AWS Support:**
- Console: https://console.aws.amazon.com/support/
- Phone: Available in AWS Console

**Neo4j Support:**
- Email: support@neo4j.com
- Portal: https://support.neo4j.com/
- Phone: Available for Enterprise customers

## References

- [AWS RDS Backup Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [AWS ElastiCache Backup Documentation](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups.html)
- [Neo4j Aura Backup Documentation](https://neo4j.com/docs/aura/platform/backup-restore/)
- [AWS Disaster Recovery Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html)

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 1.0 | Initial backup configuration documentation | DevOps Team |
