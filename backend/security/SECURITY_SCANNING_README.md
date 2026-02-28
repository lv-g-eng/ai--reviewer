# OWASP ZAP Security Scanning

This directory contains automated security scanning tools using OWASP ZAP (Zed Attack Proxy) to verify compliance with OWASP Top 10 security standards.

## Overview

The security scanning implementation provides:

- **Automated OWASP ZAP scanning** for API and web application security
- **OWASP Top 10 2021 coverage** including injection, broken access control, and cryptographic failures
- **Multiple scan types** (baseline, API, full) for different testing scenarios
- **Compliance verification** ensuring zero critical and high severity vulnerabilities
- **Detailed reporting** in HTML, JSON, and Markdown formats

## Requirements

**Requirement 8.10**: THE System SHALL pass OWASP ZAP security scan with zero critical and zero high severity vulnerabilities.

**Requirement 5.10**: THE Test_Suite SHALL implement security tests scanning for OWASP Top 10 vulnerabilities using automated tools.

## Files

- `zap_config.yaml` - ZAP scanner configuration with OWASP Top 10 rules
- `run_zap_scan.py` - Python script for running and analyzing scans
- `run_security_scan.sh` - Bash script for Linux/macOS
- `run_security_scan.ps1` - PowerShell script for Windows
- `docker-compose.zap.yml` - Docker Compose configuration for ZAP service
- `SECURITY_SCANNING_README.md` - This documentation file

## Quick Start

### Prerequisites

1. **Docker** installed and running
2. **Backend application** running at http://localhost:8000
3. **Network connectivity** to backend

### Running a Scan

**Linux/macOS:**
```bash
cd backend/security
chmod +x run_security_scan.sh
./run_security_scan.sh --type baseline
```

**Windows:**
```powershell
cd backend\security
.\run_security_scan.ps1 -ScanType baseline
```

**Python:**
```bash
cd backend/security
python run_zap_scan.py --target http://localhost:8000 --scan-type baseline
```

## Scan Types

### 1. Baseline Scan (Recommended for CI/CD)

Fast passive scan suitable for continuous integration.

**Features:**
- Passive scanning only (no active attacks)
- Spider crawls the application
- Checks for common vulnerabilities
- Completes in 5-10 minutes

**Usage:**
```bash
./run_security_scan.sh --type baseline
```

**When to use:**
- Pull request validation
- Continuous integration pipelines
- Quick security checks
- Pre-deployment verification

### 2. API Scan (Recommended for API Testing)

Specialized scan for REST APIs using OpenAPI specification.

**Features:**
- Uses OpenAPI/Swagger spec for comprehensive coverage
- Tests all API endpoints
- Validates authentication and authorization
- Checks for API-specific vulnerabilities

**Usage:**
```bash
./run_security_scan.sh --type api --url http://localhost:8000
```

**When to use:**
- API security testing
- Backend-only deployments
- Microservices testing
- API compliance verification

### 3. Full Scan (Use with Caution)

Comprehensive active + passive scan with attack simulations.

**Features:**
- Active scanning with simulated attacks
- Deep crawling and fuzzing
- Comprehensive vulnerability detection
- May take 30+ minutes

**Usage:**
```bash
./run_security_scan.sh --type full
```

**When to use:**
- Pre-release security audits
- Penetration testing
- Comprehensive security assessment
- Staging environment testing

**⚠️ Warning:** Full scans generate significant load and may trigger rate limiting or security alerts. Only run against test/staging environments.

## Configuration

### ZAP Configuration File

Edit `zap_config.yaml` to customize scanning behavior:

```yaml
# Scan Configuration
scan:
  target: "http://backend:8000"
  type: "api"
  max_duration: 30

# OWASP Top 10 Rules
rules:
  - id: 40018
    name: "SQL Injection"
    enabled: true
    threshold: "low"

# Compliance Thresholds
thresholds:
  fail_level: "high"
  max_alerts:
    high: 0      # Zero high severity allowed
    medium: 0    # Zero medium severity allowed
    low: 10
```

### Environment Variables

```bash
# Backend URL
export BACKEND_URL=http://localhost:8000

# Scan type
export SCAN_TYPE=baseline

# Output directory
export OUTPUT_DIR=./zap_reports

# ZAP API key (for daemon mode)
export ZAP_API_KEY=changeme
```

## Reports

Scans generate multiple report formats in the output directory:

### HTML Report
- **File**: `baseline_report.html`, `api_report.html`, or `full_report.html`
- **Purpose**: Human-readable detailed report
- **Contains**: Vulnerability details, evidence, remediation steps

### JSON Report
- **File**: `baseline_report.json`, `api_report.json`, or `full_report.json`
- **Purpose**: Machine-readable for automation
- **Contains**: Structured alert data, risk levels, CWE references

### Markdown Report
- **File**: `baseline_report.md`, `api_report.md`, or `full_report.md`
- **Purpose**: Documentation and version control
- **Contains**: Summary and key findings

### Summary Report
- **File**: `summary.md`
- **Purpose**: Quick compliance check
- **Contains**: Alert counts, compliance status, high/medium issues

## OWASP Top 10 2021 Coverage

The scanner tests for all OWASP Top 10 2021 categories:

| Category | Description | ZAP Rules |
|----------|-------------|-----------|
| **A01:2021** | Broken Access Control | Access control testing, authorization bypass |
| **A02:2021** | Cryptographic Failures | Weak cryptography, insecure transmission |
| **A03:2021** | Injection | SQL injection, XSS, code injection |
| **A04:2021** | Insecure Design | Missing security headers, design flaws |
| **A05:2021** | Security Misconfiguration | Missing headers, CORS issues, default configs |
| **A06:2021** | Vulnerable Components | Outdated libraries, known vulnerabilities |
| **A07:2021** | Authentication Failures | Weak authentication, session fixation |
| **A08:2021** | Data Integrity Failures | Missing SRI, insecure deserialization |
| **A09:2021** | Logging Failures | Insufficient logging and monitoring |
| **A10:2021** | SSRF | Server-side request forgery |

## Compliance Verification

### Requirement 8.10 Compliance

The system must pass with:
- ✅ **Zero critical severity** vulnerabilities
- ✅ **Zero high severity** vulnerabilities
- ⚠️ **Limited medium severity** vulnerabilities (max 0 by default)
- ℹ️ **Low and informational** findings are acceptable

### Checking Compliance

The scan scripts automatically check compliance:

```bash
./run_security_scan.sh --type baseline
# Output:
# [INFO] ✅ PASS: Zero high severity vulnerabilities found
# [INFO] ✅ Security scan PASSED
```

Failed compliance:
```bash
./run_security_scan.sh --type baseline
# Output:
# [ERROR] ❌ FAIL: 2 high severity vulnerabilities found (requirement: 0)
# [ERROR] ❌ Security scan FAILED
```

## Integration with CI/CD

### GitHub Actions

Add to `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start backend
        run: |
          docker-compose up -d backend
          sleep 30  # Wait for backend to be ready
      
      - name: Run ZAP baseline scan
        run: |
          cd backend/security
          ./run_security_scan.sh --type baseline
      
      - name: Upload scan reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: zap-reports
          path: backend/security/zap_reports/
      
      - name: Check compliance
        run: |
          if [ -f backend/security/zap_reports/summary.md ]; then
            cat backend/security/zap_reports/summary.md
          fi
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
security-scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd backend/security
    - chmod +x run_security_scan.sh
    - ./run_security_scan.sh --type baseline
  artifacts:
    paths:
      - backend/security/zap_reports/
    when: always
  only:
    - merge_requests
    - main
```

## Troubleshooting

### Backend Not Accessible

**Problem:** Scanner cannot reach backend at http://localhost:8000

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check Docker network: Use `--network host` for Docker scans
3. Update target URL: `./run_security_scan.sh --url http://backend:8000`

### Docker Permission Denied

**Problem:** Permission denied when running Docker commands

**Solutions:**
1. Add user to docker group: `sudo usermod -aG docker $USER`
2. Restart shell or run: `newgrp docker`
3. Use sudo: `sudo ./run_security_scan.sh`

### Scan Timeout

**Problem:** Scan exceeds maximum duration

**Solutions:**
1. Increase timeout in `zap_config.yaml`: `max_duration: 60`
2. Use baseline scan instead of full scan
3. Reduce spider depth: `spider.max_depth: 3`

### False Positives

**Problem:** Scanner reports issues that aren't real vulnerabilities

**Solutions:**
1. Review alert details in HTML report
2. Add exclusions to `zap_config.yaml`:
   ```yaml
   context:
     exclude_urls:
       - "http://backend:8000/api/v1/health"
   ```
3. Adjust rule thresholds for specific alerts

### High Memory Usage

**Problem:** ZAP container uses excessive memory

**Solutions:**
1. Reduce scan scope with URL filters
2. Limit spider depth and children
3. Increase Docker memory limit in `docker-compose.zap.yml`

## Advanced Usage

### Custom Authentication

For authenticated scans, provide JWT token:

```bash
# Get authentication token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  | jq -r '.access_token')

# Run scan with authentication
docker run --rm --network host \
  -v "$(pwd)/zap_reports:/zap/wrk:rw" \
  owasp/zap2docker-stable \
  zap-api-scan.py \
  -t http://localhost:8000/api/v1/openapi.json \
  -f openapi \
  -z "-config replacer.full_list(0).description=auth \
      -config replacer.full_list(0).enabled=true \
      -config replacer.full_list(0).matchtype=REQ_HEADER \
      -config replacer.full_list(0).matchstr=Authorization \
      -config replacer.full_list(0).replacement='Bearer $TOKEN'"
```

### Continuous Scanning with ZAP Daemon

Run ZAP as a persistent service:

```bash
# Start ZAP daemon
docker-compose -f docker-compose.zap.yml up -d

# ZAP API available at http://localhost:8080
# ZAP Web UI available at http://localhost:8090

# Run scans via API
curl "http://localhost:8080/JSON/ascan/action/scan/?url=http://backend:8000&apikey=changeme"
```

### Custom Scan Policies

Create custom scan policies for specific needs:

```yaml
# zap_custom_policy.yaml
rules:
  # Only test for injection vulnerabilities
  - id: 40018
    name: "SQL Injection"
    enabled: true
    threshold: "low"
  
  - id: 40014
    name: "XSS Reflected"
    enabled: true
    threshold: "low"
  
  # Disable other rules
  - id: 10016
    enabled: false
```

## Best Practices

1. **Run scans regularly** - Schedule daily or weekly scans
2. **Scan early** - Include in CI/CD pipeline for every PR
3. **Start with baseline** - Use baseline scans for quick feedback
4. **Progress to full scans** - Run comprehensive scans before releases
5. **Review all findings** - Don't ignore low severity issues
6. **Fix high/critical first** - Prioritize by risk level
7. **Document exceptions** - Track accepted risks with justification
8. **Keep ZAP updated** - Pull latest Docker image regularly
9. **Test in staging** - Never run full scans in production
10. **Monitor trends** - Track vulnerability counts over time

## Security Considerations

- **Never scan production** without explicit authorization
- **Rate limiting** may block aggressive scans
- **Active scans** may trigger security alerts or WAF rules
- **Sensitive data** may appear in scan reports - handle securely
- **Authentication tokens** should be short-lived test credentials
- **Scan reports** may contain security details - restrict access

## Support and Resources

- **OWASP ZAP Documentation**: https://www.zaproxy.org/docs/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **ZAP Docker Images**: https://www.zaproxy.org/docs/docker/
- **ZAP API Documentation**: https://www.zaproxy.org/docs/api/

## Maintenance

### Updating ZAP

Pull the latest ZAP Docker image:

```bash
docker pull owasp/zap2docker-stable
```

### Updating Configuration

1. Review OWASP Top 10 updates annually
2. Adjust rule thresholds based on findings
3. Update exclusion patterns as application evolves
4. Tune performance settings for scan duration

### Archiving Reports

Archive scan reports for compliance:

```bash
# Create timestamped archive
tar -czf zap_reports_$(date +%Y%m%d).tar.gz zap_reports/

# Move to archive location
mv zap_reports_*.tar.gz /path/to/archive/
```

## License

This security scanning configuration is part of the AI-Based Reviewer project and follows the project's license terms.

## Contact

For questions or issues with security scanning:
- Review this documentation
- Check ZAP documentation
- Consult security team
- Open an issue in the project repository
