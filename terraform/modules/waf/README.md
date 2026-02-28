# WAF Module

This module configures AWS WAF (Web Application Firewall) with OWASP Top 10 protection rules and rate limiting for the AI-Based Code Reviewer infrastructure.

## Features

### OWASP Top 10 Protection

The module implements comprehensive protection against OWASP Top 10 vulnerabilities using AWS Managed Rule Groups:

1. **Core Rule Set (CRS)** - Protects against common web exploits including:
   - SQL Injection (SQLi)
   - Cross-Site Scripting (XSS)
   - Local File Inclusion (LFI)
   - Remote File Inclusion (RFI)
   - Remote Code Execution (RCE)
   - PHP injection attacks
   - Cross-Site Request Forgery (CSRF)

2. **Known Bad Inputs** - Blocks requests with patterns known to be malicious

3. **SQL Injection Protection** - Additional layer specifically for SQL injection attacks

4. **Linux Operating System Protection** - Protects against Linux-specific exploits

5. **IP Reputation List** - Blocks requests from known malicious IP addresses

6. **Anonymous IP List** - Blocks requests from:
   - VPN services
   - Proxy services
   - Tor exit nodes
   - Hosting providers commonly used for attacks

### Rate Limiting

- Configurable rate limit per IP address (default: 2000 requests per 5 minutes)
- Returns HTTP 429 (Too Many Requests) with JSON error message
- Prevents DDoS attacks and API abuse

### Geo-Blocking (Optional)

- Ability to block traffic from specific countries
- Useful for compliance requirements or threat mitigation

### Logging and Monitoring

- All WAF events logged to CloudWatch Logs
- Sensitive headers (Authorization, Cookie) automatically redacted
- CloudWatch metrics enabled for all rules
- Sampled requests available for analysis

## Usage

```hcl
module "waf" {
  source = "./modules/waf"

  project_name = "ai-code-reviewer"
  environment  = "prod"
  alb_arn      = module.compute.alb_arn

  # Rate limiting configuration
  rate_limit = 2000  # requests per 5 minutes per IP

  # Optional: Block specific countries
  blocked_countries = []  # e.g., ["CN", "RU"] to block China and Russia

  # Log retention
  log_retention_days = 30

  tags = {
    ManagedBy = "Terraform"
  }
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Name of the project for resource naming | string | - | yes |
| environment | Environment name (dev, staging, prod) | string | - | yes |
| alb_arn | ARN of the Application Load Balancer | string | - | yes |
| rate_limit | Rate limit (requests per 5 minutes per IP) | number | 2000 | no |
| blocked_countries | List of country codes to block (ISO 3166-1 alpha-2) | list(string) | [] | no |
| log_retention_days | CloudWatch Logs retention period | number | 30 | no |
| tags | Additional tags for resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| web_acl_id | ID of the WAF Web ACL |
| web_acl_arn | ARN of the WAF Web ACL |
| web_acl_name | Name of the WAF Web ACL |
| web_acl_capacity | Web ACL capacity units (WCU) used |
| log_group_name | CloudWatch Log Group name for WAF logs |
| log_group_arn | CloudWatch Log Group ARN for WAF logs |

## WAF Rules Priority

Rules are evaluated in priority order (lower number = higher priority):

1. **Priority 1**: Core Rule Set (OWASP Top 10)
2. **Priority 2**: Known Bad Inputs
3. **Priority 3**: SQL Injection Protection
4. **Priority 4**: Linux OS Protection
5. **Priority 5**: Rate Limiting
6. **Priority 6**: Geo-Blocking (if enabled)
7. **Priority 7**: IP Reputation List
8. **Priority 8**: Anonymous IP List

## Monitoring WAF Activity

### View Blocked Requests

```bash
# View WAF logs in CloudWatch
aws logs tail /aws/wafv2/ai-code-reviewer-prod --follow

# Filter for blocked requests
aws logs filter-log-events \
  --log-group-name /aws/wafv2/ai-code-reviewer-prod \
  --filter-pattern '{ $.action = "BLOCK" }'
```

### CloudWatch Metrics

The following metrics are available in CloudWatch:

- `AllowedRequests` - Number of allowed requests
- `BlockedRequests` - Number of blocked requests
- `CountedRequests` - Number of counted requests (count mode only)
- `PassedRequests` - Number of requests that passed evaluation

### View Sampled Requests

1. Go to AWS WAF console
2. Select your Web ACL
3. Click "Sampled requests" tab
4. View detailed information about blocked/allowed requests

## Tuning and Customization

### Adjusting Rate Limits

For different environments, you may want different rate limits:

```hcl
# Development - more lenient
rate_limit = 5000

# Production - stricter
rate_limit = 2000

# API-heavy application - more lenient
rate_limit = 10000
```

### Handling False Positives

If legitimate requests are being blocked, you can exclude specific rules:

```hcl
# In main.tf, add to the managed_rule_group_statement:
excluded_rule {
  name = "RuleName"  # Name of the rule causing false positives
}
```

To identify which rule is blocking requests:
1. Check CloudWatch Logs for blocked requests
2. Look for the `ruleId` field in the log entry
3. Add the rule to excluded_rules if it's a false positive

### Custom Rules

You can add custom rules by adding additional `rule` blocks in `main.tf`:

```hcl
rule {
  name     = "CustomRule"
  priority = 10

  action {
    block {}
  }

  statement {
    # Your custom rule logic
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "custom-rule"
    sampled_requests_enabled   = true
  }
}
```

## Cost Considerations

AWS WAF pricing includes:
- **Web ACL**: $5.00 per month per Web ACL
- **Rules**: $1.00 per month per rule
- **Requests**: $0.60 per million requests

Estimated monthly cost for this configuration:
- Web ACL: $5.00
- Rules (8 rules): $8.00
- Requests (assuming 10M requests/month): $6.00
- **Total**: ~$19.00/month + request volume

## Security Best Practices

1. **Enable Logging**: Always enable WAF logging for security analysis
2. **Monitor Metrics**: Set up CloudWatch alarms for unusual patterns
3. **Regular Review**: Review blocked requests weekly to identify threats
4. **Test Changes**: Test WAF rule changes in staging before production
5. **Rate Limit Tuning**: Adjust rate limits based on legitimate traffic patterns
6. **Keep Updated**: AWS regularly updates managed rule groups automatically

## Compliance

This WAF configuration helps meet the following compliance requirements:

- **Requirement 4.8**: Implements AWS WAF rules to protect against OWASP Top 10 vulnerabilities
- **OWASP Top 10 Coverage**:
  - A01:2021 - Broken Access Control ✓
  - A02:2021 - Cryptographic Failures ✓
  - A03:2021 - Injection ✓
  - A04:2021 - Insecure Design ✓
  - A05:2021 - Security Misconfiguration ✓
  - A06:2021 - Vulnerable Components ✓
  - A07:2021 - Authentication Failures ✓
  - A08:2021 - Software and Data Integrity Failures ✓
  - A09:2021 - Security Logging Failures ✓
  - A10:2021 - Server-Side Request Forgery ✓

## Troubleshooting

### Issue: Legitimate requests being blocked

**Solution**: 
1. Check CloudWatch Logs to identify the blocking rule
2. Add the rule to `excluded_rule` in the managed rule group
3. Test thoroughly before deploying to production

### Issue: High rate of false positives

**Solution**:
1. Consider using COUNT mode temporarily to observe without blocking
2. Analyze patterns in sampled requests
3. Adjust rules or add exceptions as needed

### Issue: Rate limit too restrictive

**Solution**:
1. Analyze legitimate traffic patterns
2. Increase `rate_limit` variable
3. Consider implementing different rate limits for different endpoints

## References

- [AWS WAF Documentation](https://docs.aws.amazon.com/waf/)
- [AWS Managed Rules](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [WAF Best Practices](https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html)
