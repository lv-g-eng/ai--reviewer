#!/usr/bin/env python3
"""
Technical Debt & Performance Monitor
=====================================
Automated scanning for code quality issues, technical debt, and performance warnings.

Run: python3 scripts/tech_debt_monitor.py
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Issue:
    severity: str
    category: str
    file: str
    line: int
    message: str


class TechDebtMonitor:
    """Monitor and report technical debt issues."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues: List[Issue] = []
        
    def scan(self) -> List[Issue]:
        """Run all scans."""
        print("🔍 Scanning for technical debt issues...\n")
        
        self._scan_complex_functions()
        self._scan_deep_nesting()
        self._scan_circular_imports()
        self._scan_hardcoded_secrets()
        self._scan_duplicate_code()
        self._scan_unused_imports()
        
        return self.issues
    
    def _scan_complex_functions(self):
        """Detect functions with high cyclomatic complexity."""
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                in_function = False
                func_name = ""
                indent_level = 0
                complexity = 1
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    if stripped.startswith("def ") or stripped.startswith("async def "):
                        if in_function:
                            if complexity > 10:
                                self.issues.append(Issue(
                                    severity="WARNING",
                                    category="COMPLEXITY",
                                    file=str(py_file.relative_to(self.root_path)),
                                    line=i,
                                    message=f"Function '{func_name}' has complexity {complexity} (>10)"
                                ))
                        
                        in_function = True
                        func_name = re.search(r"def (\w+)", stripped).group(1)
                        indent_level = len(line) - len(line.lstrip())
                        complexity = 1
                    
                    elif in_function:
                        if stripped and not stripped.startswith("#"):
                            if any(kw in stripped for kw in [" if ", " elif ", " for ", " while ", " and ", " or ", " except "]):
                                complexity += 1
                                
                            current_indent = len(line) - len(line.lstrip())
                            if current_indent <= indent_level and stripped:
                                if complexity > 10:
                                    self.issues.append(Issue(
                                        severity="WARNING",
                                        category="COMPLEXITY",
                                        file=str(py_file.relative_to(self.root_path)),
                                        line=i,
                                        message=f"Function '{func_name}' has complexity {complexity} (>10)"
                                    ))
                                in_function = False
                                
            except Exception:
                pass
    
    def _scan_deep_nesting(self):
        """Detect deeply nested code blocks."""
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    indent = len(line) - len(line.lstrip())
                    if indent > 16 and line.strip() and not line.strip().startswith("#"):
                        self.issues.append(Issue(
                            severity="INFO",
                            category="NESTING",
                            file=str(py_file.relative_to(self.root_path)),
                            line=i,
                            message=f"Deep nesting detected (indent={indent})"
                        ))
                        break
                        
            except Exception:
                pass
    
    def _scan_circular_imports(self):
        """Basic check for potential circular imports."""
        import_pattern = re.compile(r"^from \.(\.)* import |^import ")
        
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                imports = import_pattern.findall(content)
                
                module_name = py_file.stem
                for imp in imports:
                    if module_name in imp:
                        self.issues.append(Issue(
                            severity="WARNING",
                            category="CIRCULAR_IMPORT",
                            file=str(py_file.relative_to(self.root_path)),
                            line=1,
                            message=f"Potential circular import: {imp}"
                        ))
                        
            except Exception:
                pass
    
    def _scan_hardcoded_secrets(self):
        """Scan for hardcoded secrets."""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "HARDCODED_PASSWORD"),
            (r'api_key\s*=\s*["\'][^"\']{8,}["\']', "HARDCODED_API_KEY"),
            (r'secret\s*=\s*["\'][^"\']{8,}["\']', "HARDCODED_SECRET"),
            (r'token\s*=\s*["\'][^"\']{8,}["\']', "HARDCODED_TOKEN"),
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                for pattern, category in secret_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        self.issues.append(Issue(
                            severity="CRITICAL",
                            category=category,
                            file=str(py_file.relative_to(self.root_path)),
                            line=content[:match.start()].count('\n') + 1,
                            message=f"Potential hardcoded secret detected"
                        ))
                        
            except Exception:
                pass
    
    def _scan_duplicate_code(self):
        """Detect duplicate code blocks."""
        code_blocks = {}
        
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                for match in re.finditer(r'def (\w+)\([^)]*\):', content):
                    func_name = match.group(1)
                    if func_name not in code_blocks:
                        code_blocks[func_name] = []
                    code_blocks[func_name].append(str(py_file.relative_to(self.root_path)))
                    
            except Exception:
                pass
        
        for func, files in code_blocks.items():
            if len(files) > 2:
                self.issues.append(Issue(
                    severity="INFO",
                    category="DUPLICATE",
                    file=", ".join(files[:3]),
                    line=0,
                    message=f"Function '{func}' defined in {len(files)} files"
                ))
    
    def _scan_unused_imports(self):
        """Basic check for potentially unused imports."""
        for py_file in self.root_path.rglob("*.py"):
            if "test" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                imports = re.findall(r'^(?:from|import)\s+(\w+)', content, re.MULTILINE)
                
                for imp in imports:
                    if imp in ["os", "sys", "time", "datetime", "json", "logging"]:
                        count = content.count(imp)
                        if count < 3:
                            self.issues.append(Issue(
                                severity="INFO",
                                category="UNUSED_IMPORT",
                                file=str(py_file.relative_to(self.root_path)),
                                line=1,
                                message=f"Potentially unused import: {imp}"
                            ))
                            break
                            
            except Exception:
                pass
    
    def report(self):
        """Generate report."""
        if not self.issues:
            print("✅ No technical debt issues found!")
            return
            
        print(f"📊 Found {len(self.issues)} issues:\n")
        
        by_severity = {}
        for issue in self.issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)
        
        for severity in ["CRITICAL", "WARNING", "INFO"]:
            if severity in by_severity:
                print(f"\n{severity} ({len(by_severity[severity])})")
                print("-" * 40)
                for issue in by_severity[severity][:10]:
                    print(f"  {issue.file}:{issue.line} [{issue.category}]")
                    print(f"    {issue.message}")
                if len(by_severity[severity]) > 10:
                    print(f"  ... and {len(by_severity[severity]) - 10} more")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    monitor = TechDebtMonitor(root)
    monitor.scan()
    monitor.report()


if __name__ == "__main__":
    main()
