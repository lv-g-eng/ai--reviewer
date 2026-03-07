import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
OWASP ZAP Security Scanner Runner

This script orchestrates OWASP ZAP security scans against the API backend.
It handles scan execution, result parsing, and vulnerability reporting.

Requirements:
- Docker installed and running
- Backend application running and accessible
- ZAP Docker image (owasp/zap2docker-stable)

Usage:
    python run_zap_scan.py --target http://localhost:8000 --scan-type api
    python run_zap_scan.py --config zap_config.yaml --output-dir ./reports
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class ZAPScanner:
    """OWASP ZAP security scanner wrapper"""
    
    # Risk levels
    RISK_HIGH = "High"
    RISK_MEDIUM = "Medium"
    RISK_LOW = "Low"
    RISK_INFO = "Informational"
    
    # OWASP Top 10 2021 mapping
    OWASP_TOP_10 = {
        "A01:2021": "Broken Access Control",
        "A02:2021": "Cryptographic Failures",
        "A03:2021": "Injection",
        "A04:2021": "Insecure Design",
        "A05:2021": "Security Misconfiguration",
        "A06:2021": "Vulnerable and Outdated Components",
        "A07:2021": "Identification and Authentication Failures",
        "A08:2021": "Software and Data Integrity Failures",
        "A09:2021": "Security Logging and Monitoring Failures",
        "A10:2021": "Server Side Request Forgery (SSRF)",
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ZAP scanner with configuration"""
        self.config = self._load_config(config_path)
        self.scan_results = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'scan': {
                'target': 'http://localhost:8000',
                'type': 'api',
                'max_duration': 30,
            },
            'thresholds': {
                'fail_level': 'high',
                'max_alerts': {
                    'high': 0,
                    'medium': 0,
                }
            },
            'reporting': {
                'formats': ['html', 'json', 'md'],
                'output_dir': './zap_reports',
            }
        }
    
    def check_docker(self) -> bool:
        """Check if Docker is available"""
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
    
    def check_target_availability(self, target: str) -> bool:
        """Check if target application is accessible"""
        import urllib.request
        import urllib.error
        
        try:
            # Try to access health endpoint
            health_url = f"{target.rstrip('/')}/api/v1/health"
            urllib.request.urlopen(health_url, timeout=5)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            # Try base URL
            try:
                urllib.request.urlopen(target, timeout=5)
                return True
            except:
                return False
    
    def run_baseline_scan(self, target: str, output_dir: str) -> int:
        """Run ZAP baseline scan"""
        logger.info("Running ZAP baseline scan against {target}...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Prepare Docker command
        cmd = [
            'docker', 'run',
            '--rm',
            '--network', 'host',
            '-v', f'{os.path.abspath(output_dir)}:/zap/wrk:rw',
            'owasp/zap2docker-stable',
            'zap-baseline.py',
            '-t', target,
            '-r', 'baseline_report.html',
            '-J', 'baseline_report.json',
            '-w', 'baseline_report.md',
            '-c', 'zap_config.conf',
        ]
        
        # Run scan
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config['scan'].get('max_duration', 30) * 60
            )
            
            logger.info(str(result.stdout))
            if result.stderr:
                logger.info(str(result.stderr, file=sys.stderr))
            
            return result.returncode
            
        except subprocess.TimeoutExpired:
            logger.info("ERROR: Scan timed out", file=sys.stderr)
            return 1
        except Exception as e:
            logger.info(str(f"ERROR: Scan failed: {e}", file=sys.stderr))
            return 1
    
    def run_api_scan(self, target: str, api_spec: str, output_dir: str) -> int:
        """Run ZAP API scan with OpenAPI specification"""
        logger.info("Running ZAP API scan against {target}...")
        logger.info("Using API spec: {api_spec}")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Prepare Docker command
        cmd = [
            'docker', 'run',
            '--rm',
            '--network', 'host',
            '-v', f'{os.path.abspath(output_dir)}:/zap/wrk:rw',
            'owasp/zap2docker-stable',
            'zap-api-scan.py',
            '-t', api_spec,
            '-f', 'openapi',
            '-r', 'api_report.html',
            '-J', 'api_report.json',
            '-w', 'api_report.md',
        ]
        
        # Run scan
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config['scan'].get('max_duration', 30) * 60
            )
            
            logger.info(str(result.stdout))
            if result.stderr:
                logger.info(str(result.stderr, file=sys.stderr))
            
            return result.returncode
            
        except subprocess.TimeoutExpired:
            logger.info("ERROR: Scan timed out", file=sys.stderr)
            return 1
        except Exception as e:
            logger.info(str(f"ERROR: Scan failed: {e}", file=sys.stderr))
            return 1
    
    def run_full_scan(self, target: str, output_dir: str) -> int:
        """Run ZAP full scan (active + passive)"""
        logger.info("Running ZAP full scan against {target}...")
        logger.info("WARNING: Full scan may take significant time and generate load")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Prepare Docker command
        cmd = [
            'docker', 'run',
            '--rm',
            '--network', 'host',
            '-v', f'{os.path.abspath(output_dir)}:/zap/wrk:rw',
            'owasp/zap2docker-stable',
            'zap-full-scan.py',
            '-t', target,
            '-r', 'full_report.html',
            '-J', 'full_report.json',
            '-w', 'full_report.md',
        ]
        
        # Run scan
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config['scan'].get('max_duration', 30) * 60
            )
            
            logger.info(str(result.stdout))
            if result.stderr:
                logger.info(str(result.stderr, file=sys.stderr))
            
            return result.returncode
            
        except subprocess.TimeoutExpired:
            logger.info("ERROR: Scan timed out", file=sys.stderr)
            return 1
        except Exception as e:
            logger.info(str(f"ERROR: Scan failed: {e}", file=sys.stderr))
            return 1
    
    def parse_results(self, json_report_path: str) -> Dict:
        """Parse ZAP JSON report"""
        try:
            with open(json_report_path, 'r') as f:
                data = json.load(f)
            
            # Extract alerts
            alerts = data.get('site', [{}])[0].get('alerts', [])
            
            # Categorize by risk level
            categorized = {
                'high': [],
                'medium': [],
                'low': [],
                'informational': []
            }
            
            for alert in alerts:
                risk = alert.get('riskdesc', '').split()[0].lower()
                if risk in categorized:
                    categorized[risk].append(alert)
            
            return {
                'total_alerts': len(alerts),
                'by_risk': categorized,
                'summary': {
                    'high': len(categorized['high']),
                    'medium': len(categorized['medium']),
                    'low': len(categorized['low']),
                    'informational': len(categorized['informational']),
                }
            }
            
        except Exception as e:
            logger.info(str(f"ERROR: Failed to parse results: {e}", file=sys.stderr))
            return None
    
    def check_compliance(self, results: Dict) -> bool:
        """Check if scan results meet compliance thresholds"""
        if not results:
            return False
        
        thresholds = self.config.get('thresholds', {})
        max_alerts = thresholds.get('max_alerts', {})
        
        summary = results.get('summary', {})
        
        # Check high severity
        if summary.get('high', 0) > max_alerts.get('high', 0):
            logger.info(f"FAIL: {summary['high']} high severity issues found "
                  f"(max allowed: {max_alerts.get('high', 0)})")
            return False
        
        # Check medium severity
        if summary.get('medium', 0) > max_alerts.get('medium', 0):
            logger.info(f"FAIL: {summary['medium']} medium severity issues found "
                  f"(max allowed: {max_alerts.get('medium', 0)})")
            return False
        
        logger.info("PASS: Security scan meets compliance thresholds")
        return True
    
    def generate_summary_report(self, results: Dict, output_path: str):
        """Generate human-readable summary report"""
        if not results:
            return
        
        summary = results.get('summary', {})
        by_risk = results.get('by_risk', {})
        
        with open(output_path, 'w') as f:
            f.write("# OWASP ZAP Security Scan Summary\n\n")
            f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Alerts:** {results['total_alerts']}\n")
            f.write(f"- **High Risk:** {summary['high']}\n")
            f.write(f"- **Medium Risk:** {summary['medium']}\n")
            f.write(f"- **Low Risk:** {summary['low']}\n")
            f.write(f"- **Informational:** {summary['informational']}\n\n")
            
            # Compliance status
            thresholds = self.config.get('thresholds', {})
            max_alerts = thresholds.get('max_alerts', {})
            
            f.write("## Compliance Status\n\n")
            
            if summary['high'] <= max_alerts.get('high', 0):
                f.write(f"✅ High Risk: {summary['high']}/{max_alerts.get('high', 0)}\n")
            else:
                f.write(f"❌ High Risk: {summary['high']}/{max_alerts.get('high', 0)}\n")
            
            if summary['medium'] <= max_alerts.get('medium', 0):
                f.write(f"✅ Medium Risk: {summary['medium']}/{max_alerts.get('medium', 0)}\n")
            else:
                f.write(f"❌ Medium Risk: {summary['medium']}/{max_alerts.get('medium', 0)}\n")
            
            # High risk details
            if by_risk['high']:
                f.write("\n## High Risk Issues\n\n")
                for i, alert in enumerate(by_risk['high'], 1):
                    f.write(f"### {i}. {alert.get('name', 'Unknown')}\n\n")
                    f.write(f"- **Risk:** {alert.get('riskdesc', 'Unknown')}\n")
                    f.write(f"- **Confidence:** {alert.get('confidence', 'Unknown')}\n")
                    f.write(f"- **Description:** {alert.get('desc', 'N/A')}\n")
                    f.write(f"- **Solution:** {alert.get('solution', 'N/A')}\n")
                    f.write(f"- **Reference:** {alert.get('reference', 'N/A')}\n\n")
            
            # Medium risk details
            if by_risk['medium']:
                f.write("\n## Medium Risk Issues\n\n")
                for i, alert in enumerate(by_risk['medium'], 1):
                    f.write(f"### {i}. {alert.get('name', 'Unknown')}\n\n")
                    f.write(f"- **Risk:** {alert.get('riskdesc', 'Unknown')}\n")
                    f.write(f"- **Confidence:** {alert.get('confidence', 'Unknown')}\n")
                    f.write(f"- **Description:** {alert.get('desc', 'N/A')}\n")
                    f.write(f"- **Solution:** {alert.get('solution', 'N/A')}\n\n")
        
        logger.info("Summary report generated: {output_path}")
    
    def run(self, target: Optional[str] = None, scan_type: Optional[str] = None) -> int:
        """Run security scan"""
        # Use config or override
        target = target or self.config['scan']['target']
        scan_type = scan_type or self.config['scan']['type']
        output_dir = self.config['reporting']['output_dir']
        
        logger.info("=" * 60)
        logger.info("OWASP ZAP Security Scanner")
        logger.info("=" * 60)
        logger.info("Target: {target}")
        logger.info("Scan Type: {scan_type}")
        logger.info("Output Directory: {output_dir}")
        logger.info("=" * 60)
        
        # Pre-flight checks
        if not self.check_docker():
            logger.info("ERROR: Docker is not available", file=sys.stderr)
            return 1
        
        if not self.check_target_availability(target):
            logger.info("WARNING: Target {target} may not be accessible")
            logger.info("Continuing anyway...")
        
        # Run appropriate scan
        if scan_type == 'baseline':
            exit_code = self.run_baseline_scan(target, output_dir)
            json_report = os.path.join(output_dir, 'baseline_report.json')
        elif scan_type == 'api':
            api_spec = self.config.get('api', {}).get('spec_url', f"{target}/api/v1/openapi.json")
            exit_code = self.run_api_scan(target, api_spec, output_dir)
            json_report = os.path.join(output_dir, 'api_report.json')
        elif scan_type == 'full':
            exit_code = self.run_full_scan(target, output_dir)
            json_report = os.path.join(output_dir, 'full_report.json')
        else:
            logger.info(str(f"ERROR: Unknown scan type: {scan_type}", file=sys.stderr))
            return 1
        
        # Parse and analyze results
        if os.path.exists(json_report):
            results = self.parse_results(json_report)
            if results:
                # Generate summary
                summary_path = os.path.join(output_dir, 'summary.md')
                self.generate_summary_report(results, summary_path)
                
                # Check compliance
                if not self.check_compliance(results):
                    return 1
        
        return exit_code


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run OWASP ZAP security scans',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run baseline scan
  python run_zap_scan.py --target http://localhost:8000 --scan-type baseline
  
  # Run API scan with config
  python run_zap_scan.py --config zap_config.yaml --scan-type api
  
  # Run full scan
  python run_zap_scan.py --target http://localhost:8000 --scan-type full
        """
    )
    
    parser.add_argument(
        '--config',
        help='Path to ZAP configuration YAML file',
        default='zap_config.yaml'
    )
    
    parser.add_argument(
        '--target',
        help='Target URL to scan (overrides config)'
    )
    
    parser.add_argument(
        '--scan-type',
        choices=['baseline', 'api', 'full'],
        help='Type of scan to run (overrides config)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for reports (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = ZAPScanner(args.config if os.path.exists(args.config) else None)
    
    # Override config with CLI args
    if args.output_dir:
        scanner.config['reporting']['output_dir'] = args.output_dir
    
    # Run scan
    exit_code = scanner.run(target=args.target, scan_type=args.scan_type)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
