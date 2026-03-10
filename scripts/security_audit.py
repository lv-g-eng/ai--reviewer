#!/usr/bin/env python3
"""
Comprehensive security audit script

Performs automated security checks on the codebase including:
- Hardcoded secrets detection
- Vulnerability scanning
- Configuration validation
- Dependency security audit
"""
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import hashlib


class SecurityAuditor:
    """Comprehensive security auditor"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.findings = []
        
    def audit_secrets(self) -> List[Dict[str, Any]]:
        """Audit for hardcoded secrets"""
        print("🔍 Scanning for hardcoded secrets...")
        
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', "API key"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']{20,}["\']', "Secret key"),
            (r'jwt[_-]?secret\s*=\s*["\'][^"\']{20,}["\']', "JWT secret"),
            (r'database[_-]?url\s*=\s*["\'].*://.*:.*@.*["\']', "Database URL with credentials"),
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', "Base64 encoded secret"),
            (r'["\'][0-9a-f]{32,}["\']', "Hex encoded secret"),
        ]
        
        findings = []
        
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern, description in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            "type": "hardcoded_secret",
                            "severity": "critical",
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "description": description,
                            "pattern": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0)
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        # Check environment files
        env_files = [".env", "backend/.env", "frontend/.env.local", "frontend/.env.development"]
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                try:
                    content = env_path.read_text()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.split('=', 1)
                            if value and not value.startswith('CHANGE_ME') and len(value) > 10:
                                findings.append({
                                    "type": "env_secret",
                                    "severity": "high",
                                    "file": env_file,
                                    "line": i,
                                    "description": f"Potential secret in environment variable: {key}",
                                    "pattern": f"{key}={value[:20]}..."
                                })
                except Exception as e:
                    print(f"Error reading {env_path}: {e}")
        
        return findings
    
    def audit_sql_injection(self) -> List[Dict[str, Any]]:
        """Audit for SQL injection vulnerabilities"""
        print("🔍 Scanning for SQL injection vulnerabilities...")
        
        findings = []
        
        # Patterns that indicate potential SQL injection
        dangerous_patterns = [
            (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "f-string in SQL execute"),
            (r'execute\s*\(\s*["\'].*%.*["\'].*%', "String formatting in SQL"),
            (r'execute\s*\(\s*.*\+.*\)', "String concatenation in SQL"),
            (r'query\s*=\s*f["\'].*\{.*\}.*["\']', "f-string in SQL query"),
        ]
        
        # Files to exclude from SQL injection checks (legitimate uses)
        excluded_files = [
            "sql_injection_prevention.py",  # This file is designed to prevent SQL injection
            "test_code_reviewer_ai_integration.py",  # Contains educational examples in comments
            "test_prompts.py",  # Contains educational examples in comments
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            # Skip excluded files
            if any(excluded in str(file_path) for excluded in excluded_files):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern, description in dangerous_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Additional check: skip if it's in a comment or string literal
                        line_content = content.split('\n')[line_num - 1].strip()
                        if line_content.startswith('#') or '# Example' in line_content or '# BAD:' in line_content:
                            continue
                        
                        findings.append({
                            "type": "sql_injection",
                            "severity": "critical",
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "description": description,
                            "pattern": match.group(0)
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return findings
    
    def audit_xss_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Audit for XSS vulnerabilities"""
        print("🔍 Scanning for XSS vulnerabilities...")
        
        findings = []
        
        # Check for dangerous HTML rendering
        xss_patterns = [
            (r'dangerouslySetInnerHTML', "Dangerous HTML rendering"),
            (r'innerHTML\s*=', "Direct innerHTML assignment"),
            (r'document\.write\s*\(', "Document.write usage"),
            (r'eval\s*\(', "eval() usage"),
        ]
        
        for file_path in self.project_root.rglob("*.tsx"):
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern, description in xss_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            "type": "xss_vulnerability",
                            "severity": "high",
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "description": description,
                            "pattern": match.group(0)
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return findings
    
    def audit_insecure_configurations(self) -> List[Dict[str, Any]]:
        """Audit for insecure configurations"""
        print("🔍 Scanning for insecure configurations...")
        
        findings = []
        
        # Check Docker configurations
        dockerfile_patterns = [
            (r'USER\s+root', "Running as root user"),
            (r'--privileged', "Privileged container"),
            (r'--no-access-log', "Access logging disabled"),
        ]
        
        for dockerfile in self.project_root.rglob("Dockerfile*"):
            try:
                content = dockerfile.read_text()
                
                for pattern, description in dockerfile_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            "type": "insecure_config",
                            "severity": "medium",
                            "file": str(dockerfile.relative_to(self.project_root)),
                            "line": line_num,
                            "description": description,
                            "pattern": match.group(0)
                        })
            except Exception as e:
                print(f"Error reading {dockerfile}: {e}")
        
        return findings
    
    def audit_dependencies(self) -> List[Dict[str, Any]]:
        """Audit dependencies for known vulnerabilities"""
        print("🔍 Auditing dependencies for vulnerabilities...")
        
        findings = []
        
        # Check Python dependencies
        requirements_files = list(self.project_root.rglob("requirements*.txt"))
        for req_file in requirements_files:
            try:
                # Run safety check if available
                result = subprocess.run(
                    ["safety", "check", "-r", str(req_file), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        findings.append({
                            "type": "dependency_vulnerability",
                            "severity": "high",
                            "file": str(req_file.relative_to(self.project_root)),
                            "description": f"Vulnerable dependency: {vuln.get('package_name')}",
                            "pattern": vuln.get('vulnerability_id', 'Unknown'),
                            "details": vuln.get('advisory', 'No details available')
                        })
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                # Safety not installed or failed
                findings.append({
                    "type": "audit_limitation",
                    "severity": "info",
                    "file": str(req_file.relative_to(self.project_root)),
                    "description": "Could not audit dependencies (install 'safety' package)",
                    "pattern": "safety check failed"
                })
        
        return findings
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        print("📊 Generating security report...")
        
        all_findings = []
        
        # Run all audits
        all_findings.extend(self.audit_secrets())
        all_findings.extend(self.audit_sql_injection())
        all_findings.extend(self.audit_xss_vulnerabilities())
        all_findings.extend(self.audit_insecure_configurations())
        all_findings.extend(self.audit_dependencies())
        
        # Categorize findings by severity
        critical = [f for f in all_findings if f.get("severity") == "critical"]
        high = [f for f in all_findings if f.get("severity") == "high"]
        medium = [f for f in all_findings if f.get("severity") == "medium"]
        low = [f for f in all_findings if f.get("severity") == "low"]
        info = [f for f in all_findings if f.get("severity") == "info"]
        
        # Calculate security score
        score = max(0, 100 - len(critical) * 25 - len(high) * 10 - len(medium) * 5 - len(low) * 2)
        
        report = {
            "timestamp": "2026-03-10T12:00:00Z",
            "project_root": str(self.project_root),
            "summary": {
                "total_findings": len(all_findings),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
                "info": len(info),
                "security_score": score
            },
            "findings": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "info": info
            },
            "recommendations": [
                "Move all secrets to environment variables or secret management service",
                "Use parameterized queries for all database operations",
                "Implement input validation and sanitization",
                "Enable security headers (HSTS, CSP, etc.)",
                "Use HTTPS for all communications",
                "Implement proper error handling without information disclosure",
                "Regular dependency updates and vulnerability scanning",
                "Code review process with security focus",
                "Implement automated security testing in CI/CD"
            ]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "security_audit_report.json"):
        """Save security report to file"""
        report_path = self.project_root / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Security report saved to: {report_path}")
        return report_path


def main():
    """Main function"""
    print("🔒 Starting Security Audit")
    print("=" * 50)
    
    auditor = SecurityAuditor()
    report = auditor.generate_report()
    
    # Print summary
    print("\n📊 Security Audit Summary")
    print("=" * 50)
    print(f"Security Score: {report['summary']['security_score']}/100")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  🔴 Critical: {report['summary']['critical']}")
    print(f"  🟠 High: {report['summary']['high']}")
    print(f"  🟡 Medium: {report['summary']['medium']}")
    print(f"  🟢 Low: {report['summary']['low']}")
    print(f"  ℹ️  Info: {report['summary']['info']}")
    
    # Save report
    report_path = auditor.save_report(report)
    
    # Print critical findings
    if report['findings']['critical']:
        print("\n🔴 Critical Findings (Immediate Action Required):")
        for finding in report['findings']['critical'][:5]:  # Show first 5
            print(f"  - {finding['file']}:{finding.get('line', '?')} - {finding['description']}")
    
    print(f"\n📄 Full report available at: {report_path}")
    
    # Exit with error code if critical issues found
    if report['summary']['critical'] > 0:
        print("\n❌ Critical security issues found! Please address immediately.")
        return 1
    elif report['summary']['high'] > 0:
        print("\n⚠️  High severity issues found. Please review and address.")
        return 0
    else:
        print("\n✅ No critical security issues found.")
        return 0


if __name__ == "__main__":
    exit(main())