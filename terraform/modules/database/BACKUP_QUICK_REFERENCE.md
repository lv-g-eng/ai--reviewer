# Database Backup Quick Reference

Quick reference guide for database backup configuration and operations.

## Backup Schedule

| Database | Type | Schedule | Retention | Window |
|----------|------|----------|-----------|--------|
| PostgreSQL | Automated | Daily | 7 days | 02:00-03:00 UTC |
| Redis | Snapshot | Daily | 7 days | 02:00-04:00 UTC |
| Neo4j | Continuous | Continuous | Aura-managed | N/A |

## Quick Commands

### Check Backup Status

```bash
# PostgreSQL - Check backup configuration
aws rds describe-db-instances \
  --db-instance-identifier <instance-id> \
  --query 'DBInstances[0].[BackupRetentionPeriod,PreferredBackupWindow,LatestRestorableTime]'

# Redis - Check snapshot configuration
aws elasticache describe-replication-groups \
  --replication-group-id <replication-group-id> \
  --query 'ReplicationGroups[0].[SnapshotRetentionLimit,SnapshotWindow]'
```

### List Backups

```bash
# PostgreSQL - List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier <instance-id> \
  --max-records 10

# Redis - List snapshots
aws elasticache describe-snapshots \
  --replication-group-id <replication-group-id> \
  --max-records 10
```

### Create Manual Backup

```bash
# PostgreSQL - Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier <instance-id> \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d-%H%M)

# Redis - Create manual snapshot
aws elasticache create-snapshot \
  --replication-group-id <replication-group-id> \
  --snapshot-name manual-backup-$(date +%Y%m%d-%H%M)
```

### Restore from Backup

```bash
# PostgreSQL - Point-in-time restore
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier <source-instance> \
  --target-db-instance-identifier <new-instance> \
  --restore-time "2024-01-15T02:30:00Z"

# Redis - Restore from snapshot
aws elasticache create-replication-group \
  --replication-group-id <new-group-id> \
  --snapshot-name <snapshot-name> \
  --cache-node-type cache.t3.small
```

## Terraform Variables

```hcl
# Set backup retention (default: 7 days)
db_backup_retention_days     = 7
redis_snapshot_retention_days = 7

# Backup windows (default: 2 AM UTC)
# Configured in main.tf:
# - RDS: 02:00-03:00 UTC
# - Redis: 02:00-04:00 UTC
```

## Verification Checklist

- [ ] RDS backup retention = 7 days
- [ ] RDS backup window = 02:00-03:00 UTC
- [ ] Redis snapshot retention = 7 days
- [ ] Redis snapshot window = 02:00-04:00 UTC
- [ ] All backups encrypted with KMS
- [ ] Latest restorable time is recent (< 24 hours)
- [ ] Test restore completed successfully

## Emergency Contacts

- **AWS Support**: https://console.aws.amazon.com/support/
- **Neo4j Support**: support@neo4j.com
- **On-Call Engineer**: [Add contact info]

## Related Documentation

- [BACKUP_CONFIGURATION.md](./BACKUP_CONFIGURATION.md) - Detailed backup guide
- [README.md](./README.md) - Database module documentation
- [AWS RDS Backup Docs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [AWS ElastiCache Backup Docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups.html)
