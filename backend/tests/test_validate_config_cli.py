"""
Unit tests for configuration validation CLI tool.

Tests the command-line interface for configuration validation,
including different validation modes and output formats.

Validates Requirements: 10.1, 10.5
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


# Path to the CLI script
CLI_SCRIPT = Path(__file__).parent.parent / "scripts" / "validate_config.py"


class TestValidateConfigCLI:
    """Test suite for configuration validation CLI tool"""
    
    def test_cli_help_option(self):
        """Test that --help option displays help message"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Validate environment configuration" in result.stdout
        assert "--mode" in result.stdout
        assert "--verbose" in result.stdout
        assert "--json" in result.stdout
    
    def test_cli_all_mode(self):
        """Test validation with 'all' mode (default)"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "all"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]  # 0 for pass, 1 for fail
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
        assert "Status:" in result.stdout
    
    def test_cli_required_mode(self):
        """Test validation with 'required' mode"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "required"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
    
    def test_cli_ports_mode(self):
        """Test validation with 'ports' mode"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "ports"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
    
    def test_cli_urls_mode(self):
        """Test validation with 'urls' mode"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "urls"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
    
    def test_cli_json_output(self):
        """Test JSON output format"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--json"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        
        # Output should be valid JSON
        try:
            output = json.loads(result.stdout)
            assert "is_valid" in output
            assert "status" in output
            assert "errors" in output
            assert "warnings" in output
            assert "config_summary" in output
            assert "error_count" in output
            assert "warning_count" in output
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_cli_verbose_mode(self):
        """Test verbose output mode"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--verbose"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        
        # Verbose mode should include DEBUG messages in stderr
        # (logging goes to stderr by default)
        combined_output = result.stdout + result.stderr
        assert "CONFIGURATION VALIDATION REPORT" in combined_output
    
    def test_cli_invalid_mode(self):
        """Test that invalid mode is rejected"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "invalid"],
            capture_output=True,
            text=True
        )
        
        # Should fail with non-zero exit code
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower()
    
    def test_cli_exit_code_on_validation_failure(self):
        """Test that CLI returns exit code 1 when validation fails"""
        # This test assumes there are some validation errors in the current environment
        # If all validation passes, this test may need adjustment
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        # Exit code should be 0 (pass) or 1 (fail)
        assert result.returncode in [0, 1]
        
        # If there are errors, exit code should be 1
        if "❌ FAILED" in result.stdout:
            assert result.returncode == 1
        elif "✅ PASSED" in result.stdout:
            assert result.returncode == 0
    
    def test_cli_json_mode_with_ports(self):
        """Test JSON output with ports mode"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "ports", "--json"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        
        # Output should be valid JSON
        try:
            output = json.loads(result.stdout)
            assert "is_valid" in output
            assert "config_summary" in output
            
            # Ports mode should include port information
            if "ports" in output["config_summary"]:
                ports = output["config_summary"]["ports"]
                assert isinstance(ports, dict)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_cli_report_format(self):
        """Test that report format includes all required sections"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        # Should include report sections
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
        assert "Status:" in result.stdout
        assert "Errors:" in result.stdout
        assert "Warnings:" in result.stdout
        assert "CONFIGURATION SUMMARY" in result.stdout
        
        # Should have proper formatting
        assert "=" * 70 in result.stdout  # Header separator
        assert "-" * 70 in result.stdout  # Section separator


class TestValidateConfigFunctions:
    """Test individual functions from the CLI module"""
    
    def test_validate_configuration_function(self):
        """Test validate_configuration function"""
        # Import the function
        sys.path.insert(0, str(CLI_SCRIPT.parent.parent))
        from scripts.validate_config import validate_configuration
        
        # Test with 'all' mode
        exit_code = validate_configuration(mode="all", verbose=False)
        assert exit_code in [0, 1]
        
        # Test with 'required' mode
        exit_code = validate_configuration(mode="required", verbose=False)
        assert exit_code in [0, 1]
        
        # Test with 'ports' mode
        exit_code = validate_configuration(mode="ports", verbose=False)
        assert exit_code in [0, 1]
        
        # Test with 'urls' mode
        exit_code = validate_configuration(mode="urls", verbose=False)
        assert exit_code in [0, 1]
    
    def test_print_validation_report_function(self):
        """Test print_validation_report function"""
        # Import the function
        sys.path.insert(0, str(CLI_SCRIPT.parent.parent))
        from scripts.validate_config import print_validation_report
        from app.core.config_validator import ValidationResult
        
        # Create a test result
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Test warning"],
            config_summary={"test": "value"}
        )
        
        # Test human-readable output (should not raise exception)
        try:
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                print_validation_report(result, json_output=False)
            output = f.getvalue()
            
            assert "CONFIGURATION VALIDATION REPORT" in output
            assert "Test warning" in output
        except Exception as e:
            pytest.fail(f"print_validation_report raised exception: {e}")
        
        # Test JSON output
        try:
            f = io.StringIO()
            with redirect_stdout(f):
                print_validation_report(result, json_output=True)
            output = f.getvalue()
            
            # Should be valid JSON
            json_data = json.loads(output)
            assert json_data["is_valid"] is True
            assert "Test warning" in json_data["warnings"]
        except Exception as e:
            pytest.fail(f"print_validation_report with JSON raised exception: {e}")


class TestCLIIntegration:
    """Integration tests for CLI tool"""
    
    def test_cli_full_workflow(self):
        """Test complete CLI workflow"""
        # Run validation
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT)],
            capture_output=True,
            text=True
        )
        
        # Should complete successfully
        assert result.returncode in [0, 1]
        
        # Should produce output
        assert len(result.stdout) > 0
        
        # Output should be well-formatted
        assert "CONFIGURATION VALIDATION REPORT" in result.stdout
        assert "Status:" in result.stdout
    
    def test_cli_with_multiple_options(self):
        """Test CLI with multiple options combined"""
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--mode", "ports", "--verbose", "--json"],
            capture_output=True,
            text=True
        )
        
        # Should run without crashing
        assert result.returncode in [0, 1]
        
        # Should produce JSON output
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
