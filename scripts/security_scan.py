#!/usr/bin/env python3
"""
定期安全扫描流程
集成多种安全扫描工具，提供全面的安全检查
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import argparse

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """扫描结果"""
    tool: str
    status: str  # success, failed, skipped
    issues_found: int
    high_severity: int
    medium_severity: int
    low_severity: int
    report_file: Optional[str] = None
    error_message: Optional[str] = None


class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.reports_dir = self.project_root / "security_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # 扫描结果
        self.results: List[ScanResult] = []
        
        # 时间戳
        self.scan_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    def run_bandit_scan(self) -> ScanResult:
        """运行Bandit Python安全扫描"""
        logger.info("🔍 运行Bandit安全扫描...")
        
        try:
            # 检查bandit是否安装
            subprocess.run(["bandit", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Bandit未安装，跳过扫描")
            return ScanResult(
                tool="bandit",
                status="skipped",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message="Bandit not installed"
            )
        
        try:
            report_file = self.reports_dir / f"bandit_report_{self.scan_timestamp}.json"
            
            # 运行bandit扫描
            cmd = [
                "bandit",
                "-r", str(self.project_root / "backend"),
                "-f", "json",
                "-o", str(report_file),
                "--confidence-level", "medium",
                "--severity-level", "medium"
            ]
            
            # 检查是否有bandit配置文件
            bandit_config = self.project_root / "backend" / "bandit.yaml"
            if bandit_config.exists():
                cmd.extend(["-c", str(bandit_config)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析结果
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                issues = report_data.get('results', [])
                high_count = sum(1 for issue in issues if issue.get('issue_severity') == 'HIGH')
                medium_count = sum(1 for issue in issues if issue.get('issue_severity') == 'MEDIUM')
                low_count = sum(1 for issue in issues if issue.get('issue_severity') == 'LOW')
                
                return ScanResult(
                    tool="bandit",
                    status="success",
                    issues_found=len(issues),
                    high_severity=high_count,
                    medium_severity=medium_count,
                    low_severity=low_count,
                    report_file=str(report_file)
                )
            else:
                return ScanResult(
                    tool="bandit",
                    status="failed",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0,
                    error_message="Report file not generated"
                )
                
        except Exception as e:
            logger.error(f"Bandit扫描失败: {e}")
            return ScanResult(
                tool="bandit",
                status="failed",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message=str(e)
            )
    
    def run_safety_scan(self) -> ScanResult:
        """运行Safety依赖漏洞扫描"""
        logger.info("🔍 运行Safety依赖漏洞扫描...")
        
        try:
            # 检查safety是否安装
            subprocess.run(["safety", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Safety未安装，跳过扫描")
            return ScanResult(
                tool="safety",
                status="skipped",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message="Safety not installed"
            )
        
        try:
            report_file = self.reports_dir / f"safety_report_{self.scan_timestamp}.json"
            
            # 查找requirements文件
            requirements_files = [
                self.project_root / "backend" / "requirements.txt",
                self.project_root / "requirements.txt",
                self.project_root / "backend" / "requirements" / "base.txt"
            ]
            
            requirements_file = None
            for req_file in requirements_files:
                if req_file.exists():
                    requirements_file = req_file
                    break
            
            if not requirements_file:
                return ScanResult(
                    tool="safety",
                    status="skipped",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0,
                    error_message="No requirements.txt found"
                )
            
            # 运行safety扫描
            cmd = [
                "safety", "check",
                "--json",
                "--file", str(requirements_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 保存结果
            with open(report_file, 'w') as f:
                f.write(result.stdout)
            
            # 解析结果
            if result.stdout:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return ScanResult(
                        tool="safety",
                        status="success",
                        issues_found=len(vulnerabilities),
                        high_severity=len(vulnerabilities),  # Safety将所有漏洞视为高风险
                        medium_severity=0,
                        low_severity=0,
                        report_file=str(report_file)
                    )
                except json.JSONDecodeError:
                    # 如果没有漏洞，safety返回空字符串
                    return ScanResult(
                        tool="safety",
                        status="success",
                        issues_found=0,
                        high_severity=0,
                        medium_severity=0,
                        low_severity=0,
                        report_file=str(report_file)
                    )
            else:
                return ScanResult(
                    tool="safety",
                    status="success",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0,
                    report_file=str(report_file)
                )
                
        except Exception as e:
            logger.error(f"Safety扫描失败: {e}")
            return ScanResult(
                tool="safety",
                status="failed",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message=str(e)
            )
    
    def run_semgrep_scan(self) -> ScanResult:
        """运行Semgrep静态分析扫描"""
        logger.info("🔍 运行Semgrep静态分析扫描...")
        
        try:
            # 检查semgrep是否安装
            subprocess.run(["semgrep", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Semgrep未安装，跳过扫描")
            return ScanResult(
                tool="semgrep",
                status="skipped",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message="Semgrep not installed"
            )
        
        try:
            report_file = self.reports_dir / f"semgrep_report_{self.scan_timestamp}.json"
            
            # 运行semgrep扫描
            cmd = [
                "semgrep",
                "--config=auto",
                "--json",
                "--output", str(report_file),
                str(self.project_root / "backend"),
                str(self.project_root / "frontend")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析结果
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                results = report_data.get('results', [])
                
                # 按严重程度分类
                high_count = sum(1 for r in results if r.get('extra', {}).get('severity') == 'ERROR')
                medium_count = sum(1 for r in results if r.get('extra', {}).get('severity') == 'WARNING')
                low_count = sum(1 for r in results if r.get('extra', {}).get('severity') == 'INFO')
                
                return ScanResult(
                    tool="semgrep",
                    status="success",
                    issues_found=len(results),
                    high_severity=high_count,
                    medium_severity=medium_count,
                    low_severity=low_count,
                    report_file=str(report_file)
                )
            else:
                return ScanResult(
                    tool="semgrep",
                    status="failed",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0,
                    error_message="Report file not generated"
                )
                
        except Exception as e:
            logger.error(f"Semgrep扫描失败: {e}")
            return ScanResult(
                tool="semgrep",
                status="failed",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message=str(e)
            )
    
    def run_eslint_security_scan(self) -> ScanResult:
        """运行ESLint安全扫描（前端）"""
        logger.info("🔍 运行ESLint安全扫描...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            return ScanResult(
                tool="eslint-security",
                status="skipped",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message="Frontend directory not found"
            )
        
        try:
            # 检查eslint是否安装
            result = subprocess.run(
                ["npm", "list", "eslint"], 
                cwd=frontend_dir,
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                return ScanResult(
                    tool="eslint-security",
                    status="skipped",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0,
                    error_message="ESLint not installed in frontend"
                )
            
            report_file = self.reports_dir / f"eslint_security_report_{self.scan_timestamp}.json"
            
            # 运行ESLint扫描
            cmd = [
                "npx", "eslint",
                "src/**/*.{js,jsx,ts,tsx}",
                "--format", "json",
                "--output-file", str(report_file)
            ]
            
            result = subprocess.run(cmd, cwd=frontend_dir, capture_output=True, text=True)
            
            # 解析结果
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                total_issues = 0
                high_count = 0
                medium_count = 0
                low_count = 0
                
                for file_result in report_data:
                    messages = file_result.get('messages', [])
                    total_issues += len(messages)
                    
                    for message in messages:
                        severity = message.get('severity', 1)
                        if severity == 2:  # Error
                            high_count += 1
                        else:  # Warning
                            medium_count += 1
                
                return ScanResult(
                    tool="eslint-security",
                    status="success",
                    issues_found=total_issues,
                    high_severity=high_count,
                    medium_severity=medium_count,
                    low_severity=low_count,
                    report_file=str(report_file)
                )
            else:
                return ScanResult(
                    tool="eslint-security",
                    status="success",
                    issues_found=0,
                    high_severity=0,
                    medium_severity=0,
                    low_severity=0
                )
                
        except Exception as e:
            logger.error(f"ESLint安全扫描失败: {e}")
            return ScanResult(
                tool="eslint-security",
                status="failed",
                issues_found=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                error_message=str(e)
            )
    
    def run_all_scans(self) -> List[ScanResult]:
        """运行所有安全扫描"""
        logger.info("🚀 开始全面安全扫描...")
        
        # 运行各种扫描
        self.results = [
            self.run_bandit_scan(),
            self.run_safety_scan(),
            self.run_semgrep_scan(),
            self.run_eslint_security_scan()
        ]
        
        return self.results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总报告"""
        total_issues = sum(r.issues_found for r in self.results)
        total_high = sum(r.high_severity for r in self.results)
        total_medium = sum(r.medium_severity for r in self.results)
        total_low = sum(r.low_severity for r in self.results)
        
        successful_scans = sum(1 for r in self.results if r.status == "success")
        failed_scans = sum(1 for r in self.results if r.status == "failed")
        skipped_scans = sum(1 for r in self.results if r.status == "skipped")
        
        summary = {
            "scan_timestamp": self.scan_timestamp,
            "project_root": str(self.project_root),
            "summary": {
                "total_issues": total_issues,
                "high_severity": total_high,
                "medium_severity": total_medium,
                "low_severity": total_low,
                "successful_scans": successful_scans,
                "failed_scans": failed_scans,
                "skipped_scans": skipped_scans
            },
            "scan_results": [
                {
                    "tool": r.tool,
                    "status": r.status,
                    "issues_found": r.issues_found,
                    "high_severity": r.high_severity,
                    "medium_severity": r.medium_severity,
                    "low_severity": r.low_severity,
                    "report_file": r.report_file,
                    "error_message": r.error_message
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        # 保存汇总报告
        summary_file = self.reports_dir / f"security_summary_{self.scan_timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"汇总报告已保存到: {summary_file}")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        total_high = sum(r.high_severity for r in self.results)
        total_medium = sum(r.medium_severity for r in self.results)
        
        if total_high > 0:
            recommendations.append(f"🚨 发现 {total_high} 个高风险安全问题，需要立即修复")
        
        if total_medium > 0:
            recommendations.append(f"⚠️ 发现 {total_medium} 个中风险安全问题，建议尽快修复")
        
        # 检查失败的扫描
        failed_tools = [r.tool for r in self.results if r.status == "failed"]
        if failed_tools:
            recommendations.append(f"🔧 以下扫描工具执行失败，请检查配置: {', '.join(failed_tools)}")
        
        # 检查跳过的扫描
        skipped_tools = [r.tool for r in self.results if r.status == "skipped"]
        if skipped_tools:
            recommendations.append(f"📦 以下扫描工具未安装，建议安装: {', '.join(skipped_tools)}")
        
        if not recommendations:
            recommendations.append("✅ 未发现严重安全问题，继续保持良好的安全实践")
        
        return recommendations
    
    def print_summary(self):
        """打印扫描结果摘要"""
        print("\n" + "="*60)
        print("🔒 安全扫描结果摘要")
        print("="*60)
        
        for result in self.results:
            status_emoji = {
                "success": "✅",
                "failed": "❌", 
                "skipped": "⏭️"
            }.get(result.status, "❓")
            
            print(f"\n{status_emoji} {result.tool.upper()}")
            print(f"   状态: {result.status}")
            print(f"   问题总数: {result.issues_found}")
            if result.issues_found > 0:
                print(f"   高风险: {result.high_severity}")
                print(f"   中风险: {result.medium_severity}")
                print(f"   低风险: {result.low_severity}")
            if result.report_file:
                print(f"   报告文件: {result.report_file}")
            if result.error_message:
                print(f"   错误信息: {result.error_message}")
        
        # 总体统计
        total_issues = sum(r.issues_found for r in self.results)
        total_high = sum(r.high_severity for r in self.results)
        total_medium = sum(r.medium_severity for r in self.results)
        total_low = sum(r.low_severity for r in self.results)
        
        print(f"\n📊 总体统计:")
        print(f"   问题总数: {total_issues}")
        print(f"   高风险: {total_high}")
        print(f"   中风险: {total_medium}")
        print(f"   低风险: {total_low}")
        
        print(f"\n📁 报告目录: {self.reports_dir}")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Code Review Platform 安全扫描工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--tools", nargs="+", 
                       choices=["bandit", "safety", "semgrep", "eslint"],
                       help="指定要运行的扫描工具")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # 创建扫描器
    scanner = SecurityScanner(args.project_root)
    
    # 运行扫描
    if args.tools:
        # 运行指定的工具
        results = []
        if "bandit" in args.tools:
            results.append(scanner.run_bandit_scan())
        if "safety" in args.tools:
            results.append(scanner.run_safety_scan())
        if "semgrep" in args.tools:
            results.append(scanner.run_semgrep_scan())
        if "eslint" in args.tools:
            results.append(scanner.run_eslint_security_scan())
        scanner.results = results
    else:
        # 运行所有扫描
        scanner.run_all_scans()
    
    # 生成报告
    summary = scanner.generate_summary_report()
    
    # 打印结果
    if not args.quiet:
        scanner.print_summary()
    
    # 返回退出码
    total_high = sum(r.high_severity for r in scanner.results)
    if total_high > 0:
        sys.exit(1)  # 有高风险问题时返回错误码
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()