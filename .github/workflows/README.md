# GitHub Actions CI/CD Workflows

This directory contains the complete CI/CD pipeline for the AI-Based Reviewer platform, implementing automated testing, security scanning, code coverage enforcement, and blue-green deployments.

## Overview

The CI/CD pipeline consists of five main workflows:

1. **CI Pipeline** (`ci.yml`) - Continuous Integration with unit and integration tests
2. **Security Scanning** (`security.yml`) - Comprehensive security vulnerability scanning
3. **Code Coverage** (`coverage.yml`) - Enforce 80% code coverage threshold
4. **CD Pipeline** (`cd.yml`) - Continuous Deployment with blue-green strategy
5. **Automatic Rollback** (`rollback.yml`) - Automated rollback on deployment failures

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Every commit to any branch
- Pull requests to `main` and `develop` branches

**Jobs:**
- **Backend Linting**: PEP 8 compliance using Black, isort, and Flake8
- **Frontend Linting**: ESLint and TypeScript type checking
- **Backend Unit Tests**: Run on every commit with PostgreSQL and Redis services
- **Frontend Unit Tests**: Run on every commit with Jest
- **Backend Integration Tests**: Run on pull requests only
- **Frontend Integration Tests**: Run on pull requests only

**Features:**
- Path filtering to run only affected tests
- Parallel execution for faster feedback
- Test result artifacts uploaded for review
- Comprehensive test coverage reporting

**Requirements Satisfied:**
- 6.1: Run unit tests on every commit
- 6.2: Run integration tests on pull requests
- 6.5: Run linting checks (PEP 8, ESLint)

### 2. Security Scanning (`security.yml`)

**Triggers:**
- Pull requests to `main` and `develop` branches
- Daily scheduled scan at 2 AM UTC
- Manual workflow dispatch

**Jobs:**
- **Snyk Scan**: Vulnerability scanning for dependencies
- **OWASP Dependency Check**: Check for known vulnerabilities in dependencies
- **Trivy Scan**: Container and filesystem vulnerability scanning
- **CodeQL Analysis**: Static code analysis for security issues
- **Secret Scanning**: Detect exposed secrets using TruffleHog
- **Bandit Scan**: Python security linting
- **npm Audit**: Frontend dependency vulnerability check

**Features:**
- Multiple security tools for comprehensive coverage
- Results uploaded to GitHub Security tab
- SARIF format for integration with GitHub Advanced Security
- Automated daily scans to catch new vulnerabilities

**Requirements Satisfied:**
- 6.3: Run Snyk security scan on pull requests
- 6.3: Run OWASP dependency check

### 3. Code Coverage (`coverage.yml`)

**Triggers:**
- Pull requests to `main` and `develop` branches
- Push to `main` and `develop` branches

**Jobs:**
- **Backend Coverage**: Calculate coverage with 80% threshold
- **Frontend Coverage**: Calculate coverage with 80% threshold
- **Combined Coverage**: Generate summary and enforce thresholds

**Features:**
- Fail build if coverage < 80%
- Upload coverage reports to Codecov
- Comment coverage metrics on pull requests
- HTML coverage reports as artifacts
- Detailed coverage breakdown by file

**Requirements Satisfied:**
- 6.4: Calculate code coverage in CI
- 6.4: Fail build if coverage < 80%

### 4. CD Pipeline (`cd.yml`)

**Triggers:**
- Push to `main` branch (auto-deploy to staging)
- Manual workflow dispatch for production deployment

**Jobs:**
- **Build**: Create deployment packages with versioning
- **Deploy to Staging**: Automatic deployment using blue-green strategy
- **Deploy to Production**: Manual approval required, blue-green deployment

**Features:**
- Blue-green deployment strategy for zero-downtime
- Automated smoke tests after deployment
- Traffic switching after successful health checks
- Deployment versioning and artifact retention
- AWS S3 for deployment package storage
- AWS Systems Manager for EC2 instance updates

**Staging Deployment:**
1. Build and package application
2. Deploy to inactive environment (blue or green)
3. Run smoke tests
4. Switch load balancer traffic
5. Monitor for issues

**Production Deployment:**
1. Requires manual approval (GitHub environment protection)
2. Create backup of current production
3. Deploy to inactive environment
4. Run comprehensive smoke tests
5. Switch load balancer traffic
6. Monitor for 5 minutes
7. Automatic rollback if issues detected

**Requirements Satisfied:**
- 6.6: Auto-deploy to staging on main branch
- 6.7: Run smoke tests after deployment
- 6.8: Require manual approval for production
- 6.9: Implement blue-green deployment

### 5. Automatic Rollback (`rollback.yml`)

**Triggers:**
- Manual workflow dispatch for immediate rollback
- Scheduled health monitoring (can trigger automatic rollback)

**Jobs:**
- **Rollback**: Execute rollback to previous stable version
- **Monitor Health**: Continuous health monitoring

**Features:**
- Detect deployment failures via CloudWatch metrics
- Automatic rollback within 5 minutes
- Switch traffic back to previous environment
- Verify rollback success with health checks
- Create incident reports
- Notification system integration

**Rollback Process:**
1. Detect deployment failure (error rate > threshold)
2. Identify previous stable environment
3. Switch load balancer to previous environment
4. Verify service health
5. Create incident report
6. Send notifications

**Requirements Satisfied:**
- 6.10: Detect deployment failures
- 6.10: Rollback to previous version within 5 minutes

## Setup Instructions

### Prerequisites

1. **GitHub Secrets** - Configure the following secrets in your repository:

   **AWS Credentials:**
   - `AWS_ACCESS_KEY_ID_STAGING`
   - `AWS_SECRET_ACCESS_KEY_STAGING`
   - `AWS_ACCESS_KEY_ID_PRODUCTION`
   - `AWS_SECRET_ACCESS_KEY_PRODUCTION`
   - `AWS_REGION`

   **AWS Resources:**
   - `STAGING_ALB_LISTENER_ARN`
   - `STAGING_TG_ARN_PREFIX`
   - `STAGING_ALB_NAME`
   - `PRODUCTION_ALB_LISTENER_ARN`
   - `PRODUCTION_TG_ARN_PREFIX`
   - `PRODUCTION_ALB_NAME`

   **Security Tools:**
   - `SNYK_TOKEN` (from Snyk.io)
   - `CODECOV_TOKEN` (from Codecov.io)

   **Notifications (optional):**
   - `SLACK_WEBHOOK_URL`

2. **GitHub Environments** - Create two environments:
   - `staging` - No protection rules (auto-deploy)
   - `production` - Require manual approval from designated reviewers

3. **AWS Infrastructure** - Ensure the following resources exist:
   - Application Load Balancers (staging and production)
   - Target Groups (blue and green for each environment)
   - EC2 Auto Scaling Groups
   - S3 buckets for deployment packages
   - CloudWatch metrics and alarms
   - Systems Manager for EC2 management

### Configuration

1. **Update URLs** in workflows:
   - Replace `ai-code-review.example.com` with your actual domain
   - Replace `staging.ai-code-review.example.com` with your staging domain

2. **Customize Thresholds**:
   - Error rate threshold (currently 10 errors in 5 minutes)
   - Coverage threshold (currently 80%)
   - Rollback time SLA (currently 5 minutes)

3. **Notification Integration**:
   - Uncomment and configure Slack/email notifications in rollback workflow
   - Add notification steps to CD workflow for deployment success/failure

## Usage

### Running Tests Locally

**Backend:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=term
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
```

### Manual Deployment

**Deploy to Staging:**
```bash
# Automatically triggered on push to main
git push origin main
```

**Deploy to Production:**
1. Go to Actions tab in GitHub
2. Select "CD Pipeline" workflow
3. Click "Run workflow"
4. Select "production" environment
5. Approve deployment when prompted

### Manual Rollback

1. Go to Actions tab in GitHub
2. Select "Automatic Rollback" workflow
3. Click "Run workflow"
4. Select environment (staging or production)
5. Optionally specify backup version
6. Confirm rollback

## Monitoring

### Key Metrics

- **Error Rate**: 5XX errors from Application Load Balancer
- **Response Time**: P95 response time < 500ms
- **Health Checks**: Target health status
- **Coverage**: Code coverage percentage
- **Security**: Vulnerability count by severity

### Dashboards

- GitHub Actions dashboard for workflow status
- GitHub Security tab for vulnerability findings
- Codecov dashboard for coverage trends
- AWS CloudWatch for infrastructure metrics

## Troubleshooting

### CI Pipeline Failures

**Linting Errors:**
```bash
# Fix Python formatting
cd backend
black app/ tests/
isort app/ tests/

# Fix JavaScript/TypeScript
cd frontend
npm run lint:fix
```

**Test Failures:**
- Check test logs in GitHub Actions artifacts
- Run tests locally to reproduce
- Ensure all services (PostgreSQL, Redis) are running

**Coverage Below Threshold:**
- Add tests for uncovered code
- Check coverage report in artifacts
- Focus on critical paths first

### Security Scan Failures

**High/Critical Vulnerabilities:**
- Review findings in GitHub Security tab
- Update dependencies to patched versions
- Add suppressions for false positives (with justification)

**Secret Detection:**
- Remove exposed secrets immediately
- Rotate compromised credentials
- Use GitHub Secrets for sensitive data

### Deployment Failures

**Smoke Tests Failing:**
- Check application logs in CloudWatch
- Verify environment variables are set correctly
- Ensure database migrations completed successfully

**Rollback Triggered:**
- Review incident report in S3
- Check CloudWatch metrics for error spikes
- Investigate application logs for root cause

## Best Practices

1. **Always run tests locally** before pushing
2. **Keep dependencies updated** to avoid security vulnerabilities
3. **Monitor coverage trends** and maintain 80%+ coverage
4. **Review security findings** promptly
5. **Test deployments in staging** before production
6. **Monitor production** closely after deployment
7. **Document incidents** and update runbooks

## Maintenance

### Regular Tasks

- **Weekly**: Review security scan results
- **Monthly**: Update dependencies and re-run security scans
- **Quarterly**: Review and update deployment procedures
- **Annually**: Audit AWS credentials and rotate secrets

### Workflow Updates

When updating workflows:
1. Test changes in a feature branch
2. Review workflow syntax with GitHub Actions validator
3. Test with manual workflow dispatch first
4. Monitor first automated run closely
5. Document changes in this README

## Support

For issues or questions:
- Check GitHub Actions logs for detailed error messages
- Review this README for common solutions
- Consult AWS CloudWatch for infrastructure issues
- Contact DevOps team for deployment assistance

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Deployment Best Practices](https://aws.amazon.com/architecture/well-architected/)
- [Blue-Green Deployment Strategy](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
