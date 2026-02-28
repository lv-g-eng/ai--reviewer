# System Security Tests

This directory contains comprehensive system-level security tests that validate the application against OWASP Top 10 2021 vulnerabilities.

## Overview

The security test suite provides:

- **OWASP ZAP Integration**: Automated vulnerability scanning using OWASP ZAP
- **OWASP Top 10 Coverage**: Tests for all 10 vulnerability categories
- **Compliance Verification**: Ensures zero critical/high severity vulnerabilities
- **Security Headers Testing**: Validates proper security header configuration
- **Rate Limiting Tests**: Verifies rate limiting implementation

## Requirements

**Requirement 5.10**: THE Test_Suite SHALL implement security tests scanning for OWASP Top 10 vulnerabilities using automated tools.

**Requirement 8.10**: THE System SHALL pass OWASP ZAP security scan with zero critical and zero high severity vulnerabilities.

## Prerequisites

1. **Docker** installed and running (for OWASP ZAP)
2. **Backend application** running at http://localhost:8000
3. **Python dependencies** installed:
   ```bash
   pip install pytest requests pyyaml
   ```

## Running Security Tests

### Quick Start

Run all security tests:

```bash
cd backend
pytest tests/system/test_security_owasp_top10.py -v
```

### Run Specific Test Categories

**OWASP ZAP Automated Scan:**
```bash
pytest tests/system/test_security_owasp_top10.py::TestOWASPZAPScan -v
```

**OWASP Top 10 Vulnerability Tests:**
```bash
pytest tests/system/test_security_owasp_top10.py::TestOWASPTop10Vulnerabilities -v
```

**Security Headers Tests:**
```bash
pytest tests/system/test_security_owasp_top10.py::TestSecurityHeaders -v
```

**Rate Limiting Tests:**
```bash
pytest tests/system/test_security_owasp_top10.py::TestRateLimiting -v
```

### Run with Detailed Output

```bash
pytest tests/system/test_security_owasp_top10.py -v -s
```

The `-s` flag shows print statements and scan progress.

## Test Categories

### 1. OWASP ZAP Automated Scan

**Test**: `test_run_zap_baseline_scan`

Runs a complete OWASP ZAP baseline security scan against the backend API.

**What it tests:**
- Passive vulnerability scanning
- Spider crawling of application
- OWASP Top 10 vulnerability detection
- Compliance with zero high/critical severity requirement

**Duration**: 5-10 minutes

**Reports Generated**:
- `backend/security/zap_reports/baseline_report.html` - Detailed HTML report
- `backend/security/zap_reports/baseline_report.json` - Machine-readable JSON
- `backend/security/zap_reports/baseline_report.md` - Markdown summary

### 2. OWASP Top 10 Vulnerability Tests

Individual tests for each OWASP Top 10 2021 category:

#### A01:2021 - Broken Access Control
**Test**: `test_a01_broken_access_control`

Verifies that:
- Protected endpoints require authentication
- Users cannot access resources outside their permissions
- Admin endpoints require admin role

#### A02:2021 - Cryptographic Failures
**Test**: `test_a02_cryptographic_failures`

Verifies that:
- HTTPS is enforced (in production)
- HSTS header is set
- Strong cryptographic algorithms are used

#### A03:2021 - Injection
**Tests**: `test_a03_sql_injection`, `test_a03_xss_reflected`

Verifies that:
- SQL injection attempts are blocked
- XSS payloads are sanitized
- Parameterized queries are used
- Content-Security-Policy header is set

#### A05:2021 - Security Misconfiguration
**Test**: `test_a05_security_misconfiguration`

Verifies that:
- Security headers are properly configured
- Debug mode is disabled
- Server version is not exposed
- Debug endpoints are not accessible

#### A07:2021 - Authentication Failures
**Test**: `test_a07_authentication_failures`

Verifies that:
- Weak passwords are rejected
- Invalid credentials are rejected
- Session management is secure

#### A10:2021 - Server Side Request Forgery (SSRF)
**Test**: `test_a10_ssrf`

Verifies that:
- User-controlled URLs are validated
- Internal network access is restricted
- URL schemes are whitelisted

### 3. Security Headers Tests

**Test**: `test_security_headers_present`

Verifies that all required security headers are present:
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `Strict-Transport-Security`: Enforces HTTPS (production)

**Test**: `test_cors_configuration`

Verifies CORS configuration:
- CORS policies are properly configured
- Origins are restricted (not `*` in production)

### 4. Rate Limiting Tests

**Test**: `test_rate_limiting_enforced`

Verifies that:
- Rate limiting is enforced (100 requests/minute per user)
- 429 status code is returned when limit exceeded

## Environment Variables

Configure tests using environment variables:

```bash
# Backend URL (default: http://localhost:8000)
export BACKEND_URL=http://localhost:8000

# Environment (affects some test expectations)
export ENVIRONMENT=development  # or staging, production
```

## Interpreting Results

### Successful Test Run

```
tests/system/test_security_owasp_top10.py::TestOWASPZAPScan::test_run_zap_baseline_scan PASSED
tests/system/test_security_owasp_top10.py::TestOWASPTop10Vulnerabilities::test_a01_broken_access_control PASSED
tests/system/test_security_owasp_top10.py::TestOWASPTop10Vulnerabilities::test_a03_sql_injection PASSED
...

============================================================
Security Scan Results:
  Total Alerts: 5
  High Severity: 0
  Medium Severity: 2
============================================================

✅ All tests passed
```

### Failed Test Run

```
tests/system/test_security_owasp_top10.py::TestOWASPZAPScan::test_run_zap_baseline_scan FAILED

AssertionError: Found 2 high severity vulnerabilities. 
Requirement 8.10 requires zero high severity issues.

❌ Tests failed - fix vulnerabilities before proceeding
```

## Troubleshooting

### Backend Not Accessible

**Problem**: `Backend at http://localhost:8000 is not accessible`

**Solution**:
1. Start the backend: `cd backend && uvicorn app.main:app --reload`
2. Verify it's running: `curl http://localhost:8000/api/v1/health`
3. Update `BACKEND_URL` if using different port

### Docker Not Available

**Problem**: `Docker is not available`

**Solution**:
1. Install Docker: https://docs.docker.com/get-docker/
2. Start Docker daemon
3. Verify: `docker --version`

### ZAP Scan Timeout

**Problem**: `ZAP scan timed out after 10 minutes`

**Solution**:
1. Increase timeout in test code (line with `timeout=600`)
2. Use faster scan type (baseline instead of full)
3. Reduce application complexity

### False Positives

**Problem**: Tests report vulnerabilities that aren't real issues

**Solution**:
1. Review detailed report in `backend/security/zap_reports/baseline_report.html`
2. Verify if issue is real or false positive
3. If false positive, add exclusion to `backend/security/zap_config.yaml`
4. Document decision in security review

## Integration with CI/CD

### GitHub Actions

Add to `.github/workflows/security.yml`:

```yaml
security-tests:
  runs-on: ubuntu-latest
  
  steps:
    - uses: actions/checkout@v3
    
    - name: Start backend
      run: |
        docker-compose up -d backend
        sleep 30
    
    - name: Run security tests
      run: |
        cd backend
        pytest tests/system/test_security_owasp_top10.py -v
    
    - name: Upload ZAP reports
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: zap-security-reports
        path: backend/security/zap_reports/
```

## Best Practices

1. **Run regularly**: Include in CI/CD pipeline for every PR
2. **Review all findings**: Don't ignore low severity issues
3. **Fix high/critical first**: Prioritize by risk level
4. **Document exceptions**: Track accepted risks with justification
5. **Keep ZAP updated**: Pull latest Docker image regularly
6. **Test in staging**: Run comprehensive scans before production deployment
7. **Monitor trends**: Track vulnerability counts over time

## Security Considerations

- **Never run in production** without explicit authorization
- **Scan reports contain sensitive information** - restrict access
- **Active scans may trigger security alerts** - coordinate with security team
- **Rate limiting may block scans** - adjust configuration if needed

## Support

For questions or issues:
- Review OWASP ZAP documentation: https://www.zaproxy.org/docs/
- Check OWASP Top 10: https://owasp.org/www-project-top-ten/
- Consult security team
- Open issue in project repository

## License

Part of the AI-Based Reviewer project. See project license for details.
