"""
Tests for OWASP ZAP security scanning configuration

This test suite verifies that the security scanning infrastructure is properly
configured and can detect common vulnerabilities.

Requirements tested:
- Requirement 8.10: OWASP ZAP security scan compliance
- Requirement 5.10: Security tests for OWASP Top 10
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict

import pytest
import yaml


class TestSecurityScanningConfiguration:
    """Test security scanning configuration files"""
    
    @pytest.fixture
    def security_dir(self) -> Path:
        """Get security directory path"""
        backend_dir = Path(__file__).parent.parent
        return backend_dir / "security"
    
    def test_security_directory_exists(self, security_dir: Path):
        """Test that security directory exists"""
        assert security_dir.exists(), "Security directory should exist"
        assert security_dir.is_dir(), "Security path should be a directory"
    
    def test_zap_config_exists(self, security_dir: Path):
        """Test that ZAP configuration file exists"""
        config_file = security_dir / "zap_config.yaml"
        assert config_file.exists(), "ZAP config file should exist"
    
    def test_zap_config_valid_yaml(self, security_dir: Path):
        """Test that ZAP configuration is valid YAML"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None, "Config should not be empty"
        assert isinstance(config, dict), "Config should be a dictionary"
    
    def test_zap_config_has_required_sections(self, security_dir: Path):
        """Test that ZAP config has all required sections"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        required_sections = ['scan', 'rules', 'thresholds', 'reporting', 'context']
        for section in required_sections:
            assert section in config, f"Config should have '{section}' section"
    
    def test_zap_config_scan_settings(self, security_dir: Path):
        """Test ZAP scan configuration settings"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        scan_config = config['scan']
        assert 'target' in scan_config, "Scan config should have target"
        assert 'type' in scan_config, "Scan config should have type"
        assert scan_config['type'] in ['baseline', 'api', 'full'], \
            "Scan type should be valid"
    
    def test_zap_config_owasp_top_10_rules(self, security_dir: Path):
        """Test that OWASP Top 10 rules are configured"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        rules = config['rules']
        assert len(rules) > 0, "Should have security rules configured"
        
        # Check for key OWASP Top 10 categories
        rule_names = [rule['name'].lower() for rule in rules]
        
        # A03:2021 - Injection
        assert any('sql injection' in name for name in rule_names), \
            "Should have SQL injection rules"
        assert any('xss' in name or 'cross site scripting' in name for name in rule_names), \
            "Should have XSS rules"
        
        # A05:2021 - Security Misconfiguration
        assert any('header' in name for name in rule_names), \
            "Should have security header rules"
    
    def test_zap_config_compliance_thresholds(self, security_dir: Path):
        """Test that compliance thresholds meet requirements"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        thresholds = config['thresholds']
        max_alerts = thresholds['max_alerts']
        
        # Requirement 8.10: Zero critical and high severity
        assert max_alerts['high'] == 0, \
            "Should allow zero high severity vulnerabilities"
        assert max_alerts.get('critical', 0) == 0, \
            "Should allow zero critical severity vulnerabilities"
    
    def test_zap_config_reporting_formats(self, security_dir: Path):
        """Test that multiple report formats are configured"""
        config_file = security_dir / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        reporting = config['reporting']
        formats = reporting['formats']
        
        assert 'html' in formats, "Should generate HTML reports"
        assert 'json' in formats, "Should generate JSON reports"
        assert 'md' in formats or 'markdown' in formats, \
            "Should generate Markdown reports"
    
    def test_run_zap_scan_script_exists(self, security_dir: Path):
        """Test that ZAP scan runner script exists"""
        script_file = security_dir / "run_zap_scan.py"
        assert script_file.exists(), "ZAP scan runner script should exist"
    
    def test_run_zap_scan_script_executable(self, security_dir: Path):
        """Test that ZAP scan runner script is valid Python"""
        script_file = security_dir / "run_zap_scan.py"
        
        # Try to compile the script
        with open(script_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            compile(code, str(script_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Script has syntax errors: {e}")
    
    def test_bash_script_exists(self, security_dir: Path):
        """Test that bash script exists"""
        script_file = security_dir / "run_security_scan.sh"
        assert script_file.exists(), "Bash script should exist"
    
    def test_powershell_script_exists(self, security_dir: Path):
        """Test that PowerShell script exists"""
        script_file = security_dir / "run_security_scan.ps1"
        assert script_file.exists(), "PowerShell script should exist"
    
    def test_docker_compose_zap_exists(self, security_dir: Path):
        """Test that Docker Compose ZAP configuration exists"""
        compose_file = security_dir / "docker-compose.zap.yml"
        assert compose_file.exists(), "Docker Compose ZAP file should exist"
    
    def test_docker_compose_zap_valid_yaml(self, security_dir: Path):
        """Test that Docker Compose ZAP file is valid YAML"""
        compose_file = security_dir / "docker-compose.zap.yml"
        
        with open(compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        assert compose_config is not None, "Compose config should not be empty"
        assert 'services' in compose_config, "Should have services section"
        assert 'zap' in compose_config['services'], "Should have ZAP service"
    
    def test_documentation_exists(self, security_dir: Path):
        """Test that security scanning documentation exists"""
        readme_file = security_dir / "SECURITY_SCANNING_README.md"
        assert readme_file.exists(), "Documentation should exist"
        
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        assert "OWASP ZAP" in content, "Should document OWASP ZAP"
        assert "Requirement 8.10" in content, "Should reference requirement"
        assert "Quick Start" in content, "Should have quick start guide"
        assert "OWASP Top 10" in content, "Should document OWASP Top 10"


class TestSecurityScannerFunctionality:
    """Test security scanner functionality"""
    
    @pytest.fixture
    def security_dir(self) -> Path:
        """Get security directory path"""
        backend_dir = Path(__file__).parent.parent
        return backend_dir / "security"
    
    def test_docker_availability(self):
        """Test that Docker is available for running scans"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, "Docker should be available"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available")
    
    def test_zap_image_available(self):
        """Test that ZAP Docker image can be pulled"""
        try:
            # Check if image exists locally
            result = subprocess.run(
                ['docker', 'images', 'owasp/zap2docker-stable', '-q'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Image exists
                return
            
            # Try to pull image (skip if network unavailable)
            pytest.skip("ZAP image not available locally, skipping pull test")
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available")
    
    def test_zap_config_loads_successfully(self, security_dir: Path):
        """Test that ZAP configuration can be loaded by scanner"""
        config_file = security_dir / "zap_config.yaml"
        
        # Import the scanner module
        sys.path.insert(0, str(security_dir))
        try:
            from run_zap_scan import ZAPScanner
            
            scanner = ZAPScanner(str(config_file))
            assert scanner.config is not None, "Config should load"
            assert 'scan' in scanner.config, "Config should have scan section"
            
        except ImportError as e:
            pytest.skip(f"Cannot import scanner module: {e}")
        finally:
            sys.path.pop(0)


class TestOWASPTop10Coverage:
    """Test OWASP Top 10 2021 coverage"""
    
    @pytest.fixture
    def zap_config(self) -> Dict:
        """Load ZAP configuration"""
        backend_dir = Path(__file__).parent.parent
        config_file = backend_dir / "security" / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def test_a01_broken_access_control(self, zap_config: Dict):
        """Test A01:2021 - Broken Access Control coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        assert any('access control' in name for name in rule_names), \
            "Should test for broken access control"
    
    def test_a02_cryptographic_failures(self, zap_config: Dict):
        """Test A02:2021 - Cryptographic Failures coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        assert any('crypto' in name or 'encryption' in name for name in rule_names), \
            "Should test for cryptographic failures"
    
    def test_a03_injection(self, zap_config: Dict):
        """Test A03:2021 - Injection coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        # SQL Injection
        assert any('sql injection' in name for name in rule_names), \
            "Should test for SQL injection"
        
        # XSS
        assert any('xss' in name or 'cross site scripting' in name for name in rule_names), \
            "Should test for XSS"
        
        # Code Injection
        assert any('code injection' in name for name in rule_names), \
            "Should test for code injection"
    
    def test_a04_insecure_design(self, zap_config: Dict):
        """Test A04:2021 - Insecure Design coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        assert any('content-type' in name for name in rule_names), \
            "Should test for insecure design patterns"
    
    def test_a05_security_misconfiguration(self, zap_config: Dict):
        """Test A05:2021 - Security Misconfiguration coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        # Security headers
        assert any('x-frame-options' in name for name in rule_names), \
            "Should test for X-Frame-Options header"
        assert any('strict-transport-security' in name for name in rule_names), \
            "Should test for HSTS header"
        assert any('xss protection' in name for name in rule_names), \
            "Should test for XSS protection header"
    
    def test_a07_authentication_failures(self, zap_config: Dict):
        """Test A07:2021 - Identification and Authentication Failures coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        assert any('authentication' in name or 'session' in name for name in rule_names), \
            "Should test for authentication failures"
    
    def test_a10_ssrf(self, zap_config: Dict):
        """Test A10:2021 - Server Side Request Forgery coverage"""
        rules = zap_config['rules']
        rule_names = [rule['name'].lower() for rule in rules]
        
        assert any('ssrf' in name or 'server side request forgery' in name for name in rule_names), \
            "Should test for SSRF"


class TestComplianceRequirements:
    """Test compliance with security requirements"""
    
    @pytest.fixture
    def zap_config(self) -> Dict:
        """Load ZAP configuration"""
        backend_dir = Path(__file__).parent.parent
        config_file = backend_dir / "security" / "zap_config.yaml"
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def test_requirement_8_10_zero_high_severity(self, zap_config: Dict):
        """
        Test Requirement 8.10: Zero high severity vulnerabilities allowed
        
        THE System SHALL pass OWASP ZAP security scan with zero critical 
        and zero high severity vulnerabilities.
        """
        thresholds = zap_config['thresholds']
        max_alerts = thresholds['max_alerts']
        
        assert max_alerts['high'] == 0, \
            "Requirement 8.10: Must allow zero high severity vulnerabilities"
    
    def test_requirement_8_10_zero_critical_severity(self, zap_config: Dict):
        """
        Test Requirement 8.10: Zero critical severity vulnerabilities allowed
        """
        thresholds = zap_config['thresholds']
        max_alerts = thresholds['max_alerts']
        
        # Critical may not be explicitly configured, default to 0
        assert max_alerts.get('critical', 0) == 0, \
            "Requirement 8.10: Must allow zero critical severity vulnerabilities"
    
    def test_requirement_5_10_owasp_top_10_coverage(self, zap_config: Dict):
        """
        Test Requirement 5.10: OWASP Top 10 vulnerability scanning
        
        THE Test_Suite SHALL implement security tests scanning for 
        OWASP Top 10 vulnerabilities using automated tools.
        """
        rules = zap_config['rules']
        
        # Should have multiple rules covering OWASP Top 10
        assert len(rules) >= 10, \
            "Requirement 5.10: Should have comprehensive OWASP Top 10 coverage"
        
        # Check that rules are enabled
        enabled_rules = [rule for rule in rules if rule.get('enabled', False)]
        assert len(enabled_rules) >= 10, \
            "Requirement 5.10: Should have at least 10 enabled security rules"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
