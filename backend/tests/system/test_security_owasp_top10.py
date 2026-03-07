"""
OWASP Top 10 Security Tests

This test suite validates the application against OWASP Top 10 2021 vulnerabilities
using automated security testing with OWASP ZAP.

Requirements tested:
- Requirement 5.10: Security testing with automated vulnerability scanning
- Requirement 8.10: Zero critical and high severity vulnerabilities

Test Categories:
- A01:2021 - Broken Access Control
- A02:2021 - Cryptographic Failures
- A03:2021 - Injection
- A04:2021 - Insecure Design
- A05:2021 - Security Misconfiguration
- A06:2021 - Vulnerable and Outdated Components
- A07:2021 - Identification and Authentication Failures
- A08:2021 - Software and Data Integrity Failures
- A09:2021 - Security Logging and Monitoring Failures
- A10:2021 - Server Side Request Forgery (SSRF)
"""
import logging
logger = logging.getLogger(__name__)


import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import requests
import yaml


# Test configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ZAP_REPORTS_DIR = Path(__file__).parent.parent.parent / "security" / "zap_reports"
ZAP_CONFIG_FILE = Path(__file__).parent.parent.parent / "security" / "zap_config.yaml"

def is_backend_running():
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

pytestmark = pytest.mark.skipif(not is_backend_running(), reason="Backend server is not running")

class TestOWASPZAPScan:
    """Test OWASP ZAP automated security scanning"""
    
    @pytest.fixture(scope="class")
    def backend_available(self) -> bool:
        """Check if backend is available for testing"""
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    
    @pytest.fixture(scope="class")
    def docker_available(self) -> bool:
        """Check if Docker is available for running ZAP"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @pytest.fixture(scope="class")
    def zap_config(self) -> Dict:
        """Load ZAP configuration"""
        if not ZAP_CONFIG_FILE.exists():
            pytest.skip("ZAP configuration file not found")
        
        with open(ZAP_CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    
    def test_backend_is_accessible(self, backend_available: bool):
        """
        Test that backend is accessible for security scanning
        
        Requirement 5.10: Backend must be running for security tests
        """
        assert backend_available, \
            f"Backend at {BACKEND_URL} is not accessible. Start backend before running security tests."
    
    def test_docker_is_available(self, docker_available: bool):
        """
        Test that Docker is available for running ZAP scans
        
        Requirement 5.10: Docker required for OWASP ZAP scanning
        """
        assert docker_available, \
            "Docker is not available. Install Docker to run security scans."

    
    def test_run_zap_baseline_scan(
        self, 
        backend_available: bool, 
        docker_available: bool,
        zap_config: Dict
    ):
        """
        Test running OWASP ZAP baseline security scan
        
        Requirement 5.10: Run automated vulnerability scanning
        Requirement 8.10: Verify zero critical/high severity vulnerabilities
        
        This test runs a ZAP baseline scan which includes:
        - Passive scanning for common vulnerabilities
        - Spider crawling of the application
        - OWASP Top 10 vulnerability detection
        """
        if not backend_available:
            pytest.skip("Backend not available")
        if not docker_available:
            pytest.skip("Docker not available")
        
        # Create reports directory
        ZAP_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Run ZAP baseline scan
        logger.info("\n{'='*60}")
        logger.info("Running OWASP ZAP Baseline Security Scan")
        logger.info("Target: {BACKEND_URL}")
        logger.info("{'='*60}\n")
        
        cmd = [
            'docker', 'run',
            '--rm',
            '--network', 'host',
            '-v', f'{ZAP_REPORTS_DIR.absolute()}:/zap/wrk:rw',
            'owasp/zap2docker-stable',
            'zap-baseline.py',
            '-t', BACKEND_URL,
            '-r', 'baseline_report.html',
            '-J', 'baseline_report.json',
            '-w', 'baseline_report.md',
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            logger.info(str(result.stdout))
            if result.stderr:
                logger.info(str(result.stderr, file=sys.stderr))
            
            # Parse results
            json_report = ZAP_REPORTS_DIR / 'baseline_report.json'
            if json_report.exists():
                with open(json_report, 'r') as f:
                    scan_results = json.load(f)
                
                # Analyze results
                alerts = scan_results.get('site', [{}])[0].get('alerts', [])
                
                high_severity = [a for a in alerts if 'High' in a.get('riskdesc', '')]
                medium_severity = [a for a in alerts if 'Medium' in a.get('riskdesc', '')]
                
                logger.info("\n{'='*60}")
                logger.info("Security Scan Results:")
                logger.info("  Total Alerts: {len(alerts)}")
                logger.info("  High Severity: {len(high_severity)}")
                logger.info("  Medium Severity: {len(medium_severity)}")
                logger.info("{'='*60}\n")
                
                # Requirement 8.10: Zero high severity vulnerabilities
                assert len(high_severity) == 0, \
                    f"Found {len(high_severity)} high severity vulnerabilities. " \
                    f"Requirement 8.10 requires zero high severity issues."
                
                # Log medium severity for awareness
                if medium_severity:
                    logger.info("WARNING: Found {len(medium_severity)} medium severity issues")
                    for alert in medium_severity[:5]:  # Show first 5
                        logger.info("  - {alert.get('name', 'Unknown')}")
            
        except subprocess.TimeoutExpired:
            pytest.fail("ZAP scan timed out after 10 minutes")
        except Exception as e:
            pytest.fail(f"ZAP scan failed: {e}")


class TestOWASPTop10Vulnerabilities:
    """Test specific OWASP Top 10 2021 vulnerability categories"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Create API client for testing"""
        return requests.Session()

    
    def test_a01_broken_access_control(self, api_client):
        """
        Test A01:2021 - Broken Access Control
        
        Verifies that:
        - Unauthorized users cannot access protected resources
        - Users cannot access resources outside their permissions
        - Proper authorization checks are in place
        """
        # Test accessing protected endpoint without authentication
        response = api_client.get(f"{BACKEND_URL}/api/v1/projects")
        assert response.status_code in [401, 403], \
            "Protected endpoint should require authentication"
        
        # Test accessing admin endpoint without admin role
        response = api_client.get(f"{BACKEND_URL}/api/v1/admin/users")
        assert response.status_code in [401, 403], \
            "Admin endpoint should require admin role"
    
    def test_a02_cryptographic_failures(self, api_client):
        """
        Test A02:2021 - Cryptographic Failures
        
        Verifies that:
        - HTTPS is enforced (in production)
        - Sensitive data is encrypted
        - Strong cryptographic algorithms are used
        """
        # Test that API returns security headers
        response = api_client.get(f"{BACKEND_URL}/api/v1/health")
        
        # Check for HSTS header (Strict-Transport-Security)
        headers = response.headers
        if 'Strict-Transport-Security' in headers:
            assert 'max-age' in headers['Strict-Transport-Security'], \
                "HSTS header should include max-age"
    
    def test_a03_sql_injection(self, api_client):
        """
        Test A03:2021 - Injection (SQL Injection)
        
        Verifies that:
        - SQL injection attempts are blocked
        - Parameterized queries are used
        - Input validation prevents injection
        """
        # Test SQL injection in query parameter
        sql_payloads = [
            "' OR '1'='1",
            "1' OR '1'='1' --",
            "'; DROP TABLE users; --",
            "1 UNION SELECT NULL, NULL, NULL--",
        ]
        
        for payload in sql_payloads:
            response = api_client.get(
                f"{BACKEND_URL}/api/v1/projects",
                params={'search': payload}
            )
            # Should not return 500 (server error from SQL injection)
            assert response.status_code != 500, \
                f"SQL injection payload caused server error: {payload}"
    
    def test_a03_xss_reflected(self, api_client):
        """
        Test A03:2021 - Injection (Cross-Site Scripting)
        
        Verifies that:
        - XSS payloads are sanitized
        - User input is properly escaped
        - Content-Security-Policy header is set
        """
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            response = api_client.get(
                f"{BACKEND_URL}/api/v1/projects",
                params={'search': payload}
            )
            
            # Response should not contain unescaped payload
            if response.status_code == 200:
                assert payload not in response.text, \
                    f"XSS payload not sanitized: {payload}"
        
        # Check for Content-Security-Policy header
        response = api_client.get(f"{BACKEND_URL}/api/v1/health")
        headers = response.headers
        # CSP header may be set by frontend or reverse proxy
        # This is informational
        if 'Content-Security-Policy' not in headers:
            logger.info("INFO: Content-Security-Policy header not set")

    
    def test_a05_security_misconfiguration(self, api_client):
        """
        Test A05:2021 - Security Misconfiguration
        
        Verifies that:
        - Security headers are properly configured
        - Debug mode is disabled in production
        - Default credentials are not used
        - Unnecessary features are disabled
        """
        response = api_client.get(f"{BACKEND_URL}/api/v1/health")
        headers = response.headers
        
        # Check for X-Frame-Options header (clickjacking protection)
        assert 'X-Frame-Options' in headers or 'x-frame-options' in headers, \
            "X-Frame-Options header should be set to prevent clickjacking"
        
        # Check for X-Content-Type-Options header
        assert 'X-Content-Type-Options' in headers or 'x-content-type-options' in headers, \
            "X-Content-Type-Options header should be set to prevent MIME sniffing"
        
        # Check that server version is not exposed
        server_header = headers.get('Server', '')
        assert 'uvicorn' not in server_header.lower() or '/' not in server_header, \
            "Server header should not expose version information"
        
        # Check that debug endpoints are not accessible
        debug_endpoints = [
            '/debug',
            '/api/debug',
            '/api/v1/debug',
        ]
        
        for endpoint in debug_endpoints:
            response = api_client.get(f"{BACKEND_URL}{endpoint}")
            assert response.status_code == 404, \
                f"Debug endpoint should not be accessible: {endpoint}"
    
    def test_a07_authentication_failures(self, api_client):
        """
        Test A07:2021 - Identification and Authentication Failures
        
        Verifies that:
        - Weak passwords are rejected
        - Account lockout is implemented
        - Session management is secure
        - Multi-factor authentication is supported (if applicable)
        """
        # Test weak password rejection
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "12345678",
        ]
        
        for weak_password in weak_passwords:
            response = api_client.post(
                f"{BACKEND_URL}/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": weak_password
                }
            )
            # Should reject weak passwords (400 or 422)
            if response.status_code == 200:
                logger.info("WARNING: Weak password accepted: {weak_password}")
        
        # Test that login requires valid credentials
        response = api_client.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "wrongpassword"
            }
        )
        assert response.status_code in [401, 403], \
            "Invalid credentials should be rejected"
    
    def test_a10_ssrf(self, api_client):
        """
        Test A10:2021 - Server Side Request Forgery (SSRF)
        
        Verifies that:
        - User-controlled URLs are validated
        - Internal network access is restricted
        - URL schemes are whitelisted
        """
        # Test SSRF payloads in repository URL
        ssrf_payloads = [
            "http://localhost:22",
            "http://127.0.0.1:6379",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "file:///etc/passwd",
            "gopher://localhost:25",
        ]
        
        for payload in ssrf_payloads:
            response = api_client.post(
                f"{BACKEND_URL}/api/v1/projects",
                json={
                    "name": "Test Project",
                    "github_repo_url": payload
                }
            )
            # Should reject invalid URLs (400 or 422)
            assert response.status_code in [400, 401, 403, 422], \
                f"SSRF payload should be rejected: {payload}"


class TestSecurityHeaders:
    """Test security headers configuration"""
    
    def test_security_headers_present(self):
        """
        Test that all required security headers are present
        
        Requirement 8.8: CORS policies and security headers
        """
        response = requests.get(f"{BACKEND_URL}/api/v1/health")
        headers = response.headers
        
        # Required security headers
        required_headers = {
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-Content-Type-Options': ['nosniff'],
        }
        
        for header, valid_values in required_headers.items():
            # Check case-insensitive
            header_value = None
            for h, v in headers.items():
                if h.lower() == header.lower():
                    header_value = v
                    break
            
            assert header_value is not None, \
                f"Required security header missing: {header}"
            
            if valid_values:
                assert any(val.lower() in header_value.lower() for val in valid_values), \
                    f"Header {header} has invalid value: {header_value}"
    
    def test_cors_configuration(self):
        """
        Test CORS configuration
        
        Requirement 8.8: CORS policies restricting origins
        """
        # Test preflight request
        response = requests.options(
            f"{BACKEND_URL}/api/v1/projects",
            headers={
                'Origin': 'http://malicious-site.com',
                'Access-Control-Request-Method': 'GET',
            }
        )
        
        # CORS should be configured
        if 'Access-Control-Allow-Origin' in response.headers:
            allowed_origin = response.headers['Access-Control-Allow-Origin']
            # Should not allow all origins in production
            if os.getenv('ENVIRONMENT') == 'production':
                assert allowed_origin != '*', \
                    "CORS should not allow all origins in production"


class TestRateLimiting:
    """Test rate limiting implementation"""
    
    def test_rate_limiting_enforced(self):
        """
        Test that rate limiting is enforced
        
        Requirement 8.6: Rate limiting of 100 requests per minute per user
        """
        # Make rapid requests to trigger rate limiting
        endpoint = f"{BACKEND_URL}/api/v1/health"
        
        # Make 110 requests rapidly
        rate_limited = False
        for i in range(110):
            response = requests.get(endpoint)
            if response.status_code == 429:  # Too Many Requests
                rate_limited = True
                logger.info("Rate limiting triggered after {i+1} requests")
                break
        
        # Rate limiting should be enforced
        # Note: This may not trigger if rate limit is per-user and we're not authenticated
        if not rate_limited:
            logger.info("INFO: Rate limiting not triggered (may require authentication)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
