# Security Groups Module

## Overview

This module defines AWS Security Groups for the AI-Based Code Reviewer infrastructure, implementing a defense-in-depth security model with least privilege access controls.

**Implements Requirement 4.7:** Configure security groups allowing only necessary ports (443, 5432, 6379, 7687)

## Architecture

The security groups implement a three-tier architecture with strict network segmentation:

```
Internet → ALB (443) → Application Servers (8000) → Databases (5432, 6379, 7687)
```

### Security Principles

1. **Least Privilege Access**: Each tier can only access the specific ports it needs
2. **Network Segmentation**: Databases are isolated in private subnets, accessible only from application tier
3. **Defense in Depth**: Multiple layers of security controls
4. **Explicit Allow**: All traffic is denied by default; only explicitly allowed traffic is permitted

## Security Groups

### 1. Application Load Balancer Security Group

**Purpose**: Controls inbound traffic to the Application Load Balancer from the internet.

**Inbound Rules:**
- Port 80 (HTTP): Allowed from configurable CIDR blocks (default: 0.0.0.0/0)
  - Used for HTTP to HTTPS redirect
- Port 443 (HTTPS): Allowed from configurable CIDR blocks (default: 0.0.0.0/0)
  - Primary application access point with TLS encryption

**Outbound Rules:**
- All traffic allowed (required for health checks and forwarding to application servers)

**Best Practices:**
- Restrict `allowed_cidr_blocks` to specific IP ranges in production
- Consider using AWS WAF for additional protection
- Enable ALB access logs for security monitoring

### 2. Application Server Security Group

**Purpose**: Controls traffic to EC2 instances running the FastAPI backend and React frontend.

**Inbound Rules:**
- Port 8000 (HTTP): Allowed only from ALB security group
  - Application listens on port 8000 internally
  - No direct internet access

**Outbound Rules:**
- All traffic allowed (required for external API calls, package downloads, etc.)

**Best Practices:**
- Application servers are in private subnets with no public IPs
- All internet-bound traffic routes through NAT Gateway
- Consider adding SSH access from bastion host for troubleshooting (currently commented out)

### 3. RDS PostgreSQL Security Group

**Purpose**: Controls access to the PostgreSQL database.

**Inbound Rules:**
- Port 5432 (PostgreSQL): Allowed only from application server security group
  - Implements least privilege: only application tier can access database

**Outbound Rules:**
- All traffic allowed (required for replication in Multi-AZ deployments)

**Best Practices:**
- Database is in private subnet with no internet access
- Access restricted to application tier only
- Multi-AZ deployment uses this security group for both primary and standby instances

### 4. ElastiCache Redis Security Group

**Purpose**: Controls access to the Redis cache cluster.

**Inbound Rules:**
- Port 6379 (Redis): Allowed only from application server security group
  - Implements least privilege: only application tier can access cache

**Outbound Rules:**
- All traffic allowed (required for cluster communication in Multi-AZ deployments)

**Best Practices:**
- Redis is in private subnet with no internet access
- Access restricted to application tier only
- Use Redis AUTH token for additional authentication layer

### 5. Neo4j AuraDB Access

**Note**: Neo4j AuraDB is a fully managed service outside the AWS VPC. Access control is managed through Neo4j's firewall rules, not AWS security groups.

**Connection Details:**
- Port 7687 (Bolt protocol) over TLS
- Application servers connect via public internet with TLS encryption
- Configure Neo4j firewall to allow only application server NAT Gateway IPs

## Usage

### Basic Usage

```hcl
module "security_groups" {
  source = "./modules/security_groups"

  project_name = "ai-code-reviewer"
  environment  = "production"
  vpc_id       = module.vpc.vpc_id

  tags = {
    Team = "DevOps"
  }
}
```

### Restrict Access to Specific IPs

```hcl
module "security_groups" {
  source = "./modules/security_groups"

  project_name         = "ai-code-reviewer"
  environment          = "production"
  vpc_id               = module.vpc.vpc_id
  allowed_cidr_blocks  = ["203.0.113.0/24", "198.51.100.0/24"]  # Corporate IPs only

  tags = {
    Team = "DevOps"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Name of the project for resource naming | string | - | yes |
| environment | Environment name (dev, staging, prod) | string | - | yes |
| vpc_id | ID of the VPC | string | - | yes |
| allowed_cidr_blocks | List of CIDR blocks allowed to access the application | list(string) | ["0.0.0.0/0"] | no |
| tags | Additional tags to apply to all resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| alb_security_group_id | ID of the Application Load Balancer security group |
| app_security_group_id | ID of the application server security group |
| database_security_group_id | ID of the RDS PostgreSQL security group |
| redis_security_group_id | ID of the ElastiCache Redis security group |

## Security Considerations

### Port Restrictions

Only the following ports are allowed, implementing requirement 4.7:
- **443 (HTTPS)**: Public access to application via ALB
- **5432 (PostgreSQL)**: Application tier to database only
- **6379 (Redis)**: Application tier to cache only
- **7687 (Neo4j Bolt)**: Application tier to Neo4j (via internet with TLS)

### Least Privilege Implementation

1. **Database Isolation**: Databases cannot be accessed directly from the internet
2. **Application Isolation**: Application servers have no public IPs
3. **Tier Separation**: Each tier can only communicate with adjacent tiers
4. **Source-Based Rules**: Database security groups reference application security group, not CIDR blocks

### Production Hardening

For production deployments, consider these additional security measures:

1. **Restrict ALB Access**:
   ```hcl
   allowed_cidr_blocks = ["203.0.113.0/24"]  # Corporate network only
   ```

2. **Add Bastion Host** (for emergency access):
   ```hcl
   # Uncomment bastion ingress rule in app security group
   # Deploy bastion host in public subnet with MFA requirement
   ```

3. **Enable VPC Flow Logs**:
   - Monitor all network traffic for security analysis
   - Detect anomalous traffic patterns

4. **Implement AWS WAF**:
   - Protect against OWASP Top 10 vulnerabilities
   - Add rate limiting rules
   - Block known malicious IPs

5. **Use AWS Systems Manager Session Manager**:
   - Eliminate need for SSH access
   - Centralized access logging
   - No need to manage SSH keys

## Compliance

This module helps meet the following compliance requirements:

- **CIS AWS Foundations Benchmark**: Security group best practices
- **NIST Cybersecurity Framework**: Network segmentation and access control
- **ISO 27001**: Information security controls
- **SOC 2**: Security and availability controls

## Monitoring and Auditing

### CloudWatch Metrics

Monitor security group changes using AWS Config:
- Track security group rule modifications
- Alert on unauthorized changes
- Maintain compliance with security policies

### VPC Flow Logs

Enable VPC Flow Logs to monitor traffic:
```hcl
enable_flow_logs = true
```

Analyze logs for:
- Rejected connections (potential attacks)
- Unusual traffic patterns
- Compliance verification

### AWS Security Hub

Integrate with AWS Security Hub for:
- Automated security checks
- Compliance status monitoring
- Centralized security findings

## Troubleshooting

### Connection Refused Errors

If applications cannot connect to databases:

1. **Verify Security Group Rules**:
   ```bash
   aws ec2 describe-security-groups --group-ids sg-xxxxx
   ```

2. **Check Security Group Associations**:
   - Ensure RDS instance uses database security group
   - Ensure EC2 instances use application security group

3. **Verify Network ACLs**:
   - Check subnet-level network ACLs aren't blocking traffic

### Cannot Access Application

If users cannot access the application:

1. **Verify ALB Security Group**:
   - Ensure port 443 is open to required CIDR blocks
   - Check `allowed_cidr_blocks` variable

2. **Check ALB Target Health**:
   - Verify application servers are healthy
   - Check application security group allows traffic from ALB

3. **Verify SSL Certificate**:
   - Ensure valid SSL certificate is attached to ALB listener

## Testing

### Validate Security Group Rules

```bash
# Test ALB access (should succeed)
curl -I https://your-alb-dns-name.region.elb.amazonaws.com

# Test direct database access (should fail - timeout)
nc -zv your-rds-endpoint.region.rds.amazonaws.com 5432

# Test from application server (should succeed)
ssh -i key.pem ec2-user@app-server
psql -h your-rds-endpoint.region.rds.amazonaws.com -U dbuser -d dbname
```

### Security Audit

Run AWS CLI commands to audit security groups:

```bash
# List all security groups
aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=ai-code-reviewer"

# Check for overly permissive rules (0.0.0.0/0 on non-standard ports)
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]]'
```

## Migration and Updates

### Adding New Ports

If you need to add a new port (e.g., for monitoring):

1. Add the rule to the appropriate security group in `main.tf`
2. Document the change in this README
3. Update the security review documentation
4. Apply changes with `terraform plan` and `terraform apply`

### Removing Unused Rules

Regularly audit and remove unused security group rules:

1. Review VPC Flow Logs for unused ports
2. Remove rules that haven't seen traffic in 90 days
3. Document the removal
4. Apply changes with proper change management

## References

- [AWS Security Groups Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/latest/userguide/best-practices.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- Project Requirements Document: Requirement 4.7

## Support

For questions or issues with security groups:
1. Review this documentation
2. Check AWS CloudWatch Logs for connection errors
3. Review VPC Flow Logs for rejected connections
4. Contact the DevOps team

## Version History

- **v1.0.0** (2024): Initial implementation with ALB, application, database, and Redis security groups
  - Implements requirement 4.7: Allow only necessary ports (443, 5432, 6379, 7687)
  - Implements least privilege access controls
  - Supports Multi-AZ deployments
