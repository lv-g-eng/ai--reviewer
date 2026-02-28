# Terraform Quick Start Guide

Get your infrastructure up and running in minutes.

## Prerequisites

- Terraform >= 1.0 installed
- AWS CLI configured with credentials
- AWS account with appropriate permissions

## Quick Start (5 Minutes)

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:
- `db_password` - Strong password for PostgreSQL
- `neo4j_connection_uri` - Your Neo4j AuraDB URI
- `neo4j_password` - Your Neo4j password

### 2. Validate Configuration

```bash
# Linux/macOS
./validate.sh

# Windows PowerShell
.\validate.ps1
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan -var-file="environments/dev/terraform.tfvars"

# Deploy (type 'yes' when prompted)
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### 4. Get Outputs

```bash
# View all outputs
terraform output

# Get specific values
terraform output vpc_id
terraform output nat_gateway_ips
```

## What Gets Created

### Development Environment
- **VPC**: 10.0.0.0/16 with 2 AZs
- **Subnets**: 2 public + 2 private subnets
- **NAT Gateway**: 1 NAT Gateway (cost optimized)
- **Compute**: 1 t3.medium instance
- **Database**: db.t3.medium PostgreSQL (single AZ)
- **Cache**: cache.t3.micro Redis (single AZ)

**Estimated Cost**: ~$150/month

### Staging Environment
- **VPC**: 10.1.0.0/16 with 2 AZs
- **Subnets**: 2 public + 2 private subnets
- **NAT Gateways**: 2 (one per AZ for HA)
- **Compute**: 2-6 t3.large instances with auto-scaling
- **Database**: db.t3.large PostgreSQL (Multi-AZ)
- **Cache**: cache.t3.small Redis (Multi-AZ)
- **WAF**: Enabled with OWASP rules

**Estimated Cost**: ~$540/month

### Production Environment
- **VPC**: 10.2.0.0/16 with 2 AZs
- **Subnets**: 2 public + 2 private subnets
- **NAT Gateways**: 2 (one per AZ for HA)
- **Compute**: 2-10 t3.large instances with auto-scaling
- **Database**: db.t3.large PostgreSQL (Multi-AZ)
- **Cache**: cache.t3.small Redis (Multi-AZ)
- **WAF**: Enabled with OWASP rules
- **Monitoring**: Enhanced monitoring enabled

**Estimated Cost**: ~$600/month

## Common Commands

```bash
# View current infrastructure
terraform show

# List all resources
terraform state list

# Update infrastructure
terraform apply -var-file="environments/dev/terraform.tfvars"

# Destroy infrastructure (careful!)
terraform destroy -var-file="environments/dev/terraform.tfvars"
```

## Environment Selection

```bash
# Development
terraform apply -var-file="environments/dev/terraform.tfvars"

# Staging
terraform apply -var-file="environments/staging/terraform.tfvars"

# Production
terraform apply -var-file="environments/prod/terraform.tfvars"
```

## Troubleshooting

### Issue: "Error acquiring the state lock"
**Solution**: Wait for lock to release or force unlock:
```bash
terraform force-unlock LOCK_ID
```

### Issue: "UnauthorizedOperation"
**Solution**: Check AWS credentials and permissions:
```bash
aws sts get-caller-identity
```

### Issue: "Resource already exists"
**Solution**: Import existing resource:
```bash
terraform import module.vpc.aws_vpc.main vpc-xxxxx
```

## Next Steps

1. **Configure Remote State**: Set up S3 backend for state storage
2. **Add Compute Module**: Deploy EC2 instances and load balancer
3. **Add Database Module**: Deploy RDS, ElastiCache, and Neo4j
4. **Configure Security**: Set up security groups and WAF
5. **Enable Monitoring**: Configure CloudWatch logs and metrics

## Security Reminders

- ✅ Never commit `terraform.tfvars` to version control
- ✅ Use AWS Secrets Manager for sensitive data
- ✅ Enable MFA on AWS accounts
- ✅ Restrict `allowed_cidr_blocks` in production
- ✅ Review security group rules regularly
- ✅ Enable VPC Flow Logs for monitoring

## Support

- **Documentation**: See [USAGE.md](USAGE.md) for detailed guide
- **Validation**: Run `./validate.sh` or `.\validate.ps1`
- **AWS Docs**: https://docs.aws.amazon.com/
- **Terraform Docs**: https://www.terraform.io/docs

## Cost Optimization Tips

### Development
- Use single AZ deployments
- Use smaller instance types (t3.micro, t3.small)
- Disable VPC Flow Logs
- Disable detailed monitoring
- Stop instances when not in use

### All Environments
- Use Reserved Instances for predictable workloads
- Enable auto-scaling to match demand
- Review and delete unused resources
- Use AWS Cost Explorer to track spending
- Set up billing alerts

## Deployment Checklist

- [ ] AWS credentials configured
- [ ] terraform.tfvars created and configured
- [ ] Validation script passed
- [ ] Terraform plan reviewed
- [ ] Backup strategy documented
- [ ] Monitoring configured
- [ ] Security groups reviewed
- [ ] Cost estimate reviewed
- [ ] Team notified of deployment
- [ ] Rollback plan prepared

## Quick Reference

| Command | Description |
|---------|-------------|
| `terraform init` | Initialize working directory |
| `terraform validate` | Validate configuration |
| `terraform plan` | Preview changes |
| `terraform apply` | Apply changes |
| `terraform destroy` | Destroy infrastructure |
| `terraform output` | Show outputs |
| `terraform state list` | List resources |
| `terraform fmt` | Format files |

---

**Ready to deploy?** Run `./validate.sh` (or `.\validate.ps1` on Windows) to get started!
