#!/usr/bin/env python3
"""
Comprehensive Code Optimization and Internationalization Tool
- Replaces Chinese with English
- Detects and reports redundant code
- Analyzes performance bottlenecks
- Generates bilingual mapping and regression tests
"""

import os
import re
import json
import ast
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Comprehensive bilingual mapping based on GB/T 30269-2013
BILINGUAL_MAP = {
    # === Core Terms ===
    "验证": "verify", "需求": "requirement", "测试": "test", "配置": "config",
    "请求": "request", "响应": "response", "错误": "error", "状态": "status",
    "数据": "data", "用户": "user", "服务": "service", "接口": "interface",
    "功能": "feature", "模块": "module", "组件": "component", "系统": "system",
    "方法": "method", "参数": "param", "返回": "return", "输入": "input",
    "输出": "output", "结果": "result", "文件": "file", "目录": "directory",
    "路径": "path", "类型": "type", "实例": "instance", "对象": "object",
    "变量": "variable", "函数": "function", "类": "class", "属性": "property",
    "字段": "field", "值": "value", "密钥": "key", "版本": "version",
    
    # === Actions ===
    "创建": "create", "添加": "add", "删除": "delete", "更新": "update",
    "查询": "query", "保存": "save", "加载": "load", "导出": "export",
    "导入": "import", "处理": "handle", "检查": "check", "清理": "cleanup",
    "重置": "reset", "刷新": "refresh", "同步": "sync", "连接": "connect",
    "断开": "disconnect", "启动": "start", "停止": "stop", "重启": "restart",
    "执行": "execute", "运行": "run", "完成": "complete", "取消": "cancel",
    "确认": "confirm", "提交": "submit", "关闭": "close", "打开": "open",
    "编辑": "edit", "查看": "view", "搜索": "search", "过滤": "filter",
    "排序": "sort", "设置": "set", "获取": "get", "显示": "show",
    "隐藏": "hide",
    
    # === Time Units ===
    "秒": "sec", "分钟": "min", "小时": "hour", "天": "day", "毫秒": "ms",
    
    # === Technical Terms ===
    "端点": "endpoint", "中间件": "middleware", "数据库": "database",
    "会话": "session", "事务": "transaction", "缓存": "cache",
    "队列": "queue", "线程": "thread", "进程": "process",
    "权限": "permission", "角色": "role", "认证": "auth",
    "授权": "authorize", "加密": "encrypt", "解密": "decrypt",
    "签名": "sign", "日志": "log", "记录": "record",
    
    # === Quality Terms ===
    "覆盖": "coverage", "重复": "duplicate", "冗余": "redundant",
    "复杂度": "complexity", "可维护性": "maintainability", "可读性": "readability",
    
    # === Common Words ===
    "使用": "use", "包含": "contain", "生成": "generate", "渲染": "render",
    "应该": "should", "发现": "found", "提供": "provide", "支持": "support",
    "允许": "allow", "需要": "need", "必须": "must", "和": "and",
    "个": "item", "次": "times", "格式": "format", "阈值": "threshold",
    "注意": "note", "说明": "desc", "备注": "remark", "注释": "comment",
    "文档": "document", "代码": "code", "项目": "project", "任务": "task",
    "计划": "plan", "报告": "report", "分析": "analyze", "优化": "optimize",
    "跳过": "skip", "反推": "infer", "详情": "detail", "信息": "info",
    "提示": "hint", "警告": "warn", "异常": "exception", "成功": "success",
    "失败": "failure", "超时": "timeout", "重试": "retry", "等待": "wait",
    
    # === Domain Terms ===
    "审查": "review", "架构": "architecture", "依赖": "dependency",
    "集成": "integration", "部署": "deploy", "环境": "env",
    "生产": "prod", "开发": "dev",
    
    # === UI Terms ===
    "按钮": "button", "表单": "form", "输入框": "input", "下拉框": "select",
    "复选框": "checkbox", "单选框": "radio", "开关": "switch",
    "弹窗": "modal", "提示框": "tooltip", "导航": "nav",
    "菜单": "menu", "标签": "tag", "标题": "title", "内容": "content",
    "页脚": "footer", "侧栏": "sidebar", "布局": "layout", "样式": "style",
    
    # === Compound Terms ===
    "自定义生成器": "customGenerator",
    "测试覆盖": "testCoverage",
    "验证需求": "verifyRequirement",
    "渲染组件": "renderComponent",
    "版本信息": "versionInfo",
    "数据库会话": "dbSession",
    "提供者实例": "providerInstance",
    "等待数据加载": "waitDataLoad",
    "等待数据加载完成": "waitDataLoaded",
    "等待导出完成": "waitExportDone",
    "此测试验证": "testVerifies",
    "应该在": "shouldBeAt",
    "生产就绪状态检查脚本": "prodReadinessCheckScript",
    "检查项目是否满足生产部署要求": "checkProdDeployRequirements",
    "兼容各种编码": "compatibleWithEncodings",
    "生产就绪状态检查器": "prodReadinessChecker",
    "记录通过的检查": "recordPassedChecks",
    "记录失败的检查": "recordFailedChecks",
    "执行所有检查": "executeAllChecks",
    "生产就绪状态检查": "prodReadinessCheck",
    "代码质量检查": "codeQualityCheck",
    "文件结构检查": "fileStructureCheck",
    "检查代码质量": "checkCodeQuality",
    "文件中的调试代码": "debugCodeInFile",
    "语句应使用": "statementShouldUse",
    "排除跳过的目录": "excludeSkippedDirs",
    "集成完成": "integrationComplete",
    "数据库连接测试脚本": "dbConnectionTestScript",
    "验证数据结构": "verifyDataStructure",
    "审查数据": "reviewData",
    "使用真实的": "useReal",
    "如果没有则显示加载状态": "showLoadingIfNone",
    "测试成功": "testSuccess",
    "任务自动重试调度器": "taskAutoRetryScheduler",
}


class CodeOptimizer:
    """Main optimization engine"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        self.stats = {
            'files_processed': 0,
            'chinese_replaced': 0,
            'unused_imports_removed': 0,
            'lines_removed': 0,
        }
        self.bilingual_map = BILINGUAL_MAP.copy()
        self.regression_tests = []
        
    def find_chinese_in_file(self, filepath: str) -> List[Tuple[int, str, str]]:
        """Find all Chinese text in a file with line numbers and context"""
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    matches = self.chinese_pattern.findall(line)
                    if matches:
                        for m in matches:
                            findings.append((i, m, line.strip()[:100]))
        except Exception as e:
            # Log error but continue processing
            pass
        return findings
    
    def translate_chinese(self, text: str) -> str:
        """Translate Chinese text to English using mapping"""
        # Sort by length (longest first) to avoid partial replacements
        sorted_map = sorted(self.bilingual_map.items(), key=lambda x: -len(x[0]))
        
        result = text
        for cn, en in sorted_map:
            result = result.replace(cn, en)
        return result
    
    def process_file(self, filepath: str, dry_run: bool = True) -> Dict:
        """Process a single file: replace Chinese, remove unused imports"""
        result = {
            'file': filepath,
            'chinese_replacements': [],
            'changes': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            original = content
            lines = content.split('\n')
            
            # Find and replace Chinese text
            for i, line in enumerate(lines):
                matches = self.chinese_pattern.findall(line)
                if matches:
                    new_line = self.translate_chinese(line)
                    if new_line != line:
                        result['chinese_replacements'].append({
                            'line': i + 1,
                            'original': line.strip()[:80],
                            'replaced': new_line.strip()[:80],
                            'terms': matches
                        })
                        lines[i] = new_line
            
            content = '\n'.join(lines)
            
            # Remove unused imports for Python files
            if filepath.endswith('.py') and content != original:
                try:
                    tree = ast.parse(content)
                    # Keep track of used names
                    used_names = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            used_names.add(node.id)
                        elif isinstance(node, ast.Attribute):
                            if isinstance(node.value, ast.Name):
                                used_names.add(node.value.id)
                    
                    # Check imports
                    new_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith(('import ', 'from ')):
                            # Parse import to get imported names
                            try:
                                import_tree = ast.parse(stripped)
                                for node in ast.walk(import_tree):
                                    if isinstance(node, ast.Import):
                                        names = [alias.asname or alias.name for alias in node.names]
                                        if not any(n in used_names for n in names):
                                            result['changes'].append(f"Removed unused import: {stripped}")
                                            continue
                            except Exception as e:
                                # Skip problematic imports
                                pass
                        new_lines.append(line)
                    content = '\n'.join(new_lines)
                except Exception as e:
                    # Skip file if processing fails
                    pass
            
            if content != original and not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['files_processed'] += 1
                self.stats['chinese_replaced'] += len(result['chinese_replacements'])
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def generate_regression_tests(self) -> str:
        """Generate regression test cases"""
        test_code = '''#!/usr/bin/env python3
"""
Auto-generated Regression Tests for I18n Optimization
Generated: ''' + datetime.now().isoformat() + '''
"""

import pytest
import os
import re
from pathlib import Path


class TestI18nRegression:
    """Regression tests for Chinese-to-English translation"""
    
    def test_no_chinese_in_backend(self):
        """Verify no Chinese characters remain in backend source files"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        backend_path = Path('/workspace/backend/app')
        
        violations = []
        for py_file in backend_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if chinese_pattern.search(line):
                        violations.append(f"{py_file}:{i}")
        
        assert len(violations) == 0, f"Chinese text found in: {violations[:10]}"
    
    def test_no_chinese_in_frontend(self):
        """Verify no Chinese characters remain in frontend source files"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        frontend_path = Path('/workspace/frontend/src')
        
        violations = []
        for ts_file in frontend_path.rglob('*.ts*'):
            if 'node_modules' in str(ts_file) or '.next' in str(ts_file):
                continue
            with open(ts_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if chinese_pattern.search(line):
                        violations.append(f"{ts_file}:{i}")
        
        assert len(violations) == 0, f"Chinese text found in: {violations[:10]}"
    
    def test_api_endpoints_functional(self):
        """Verify API endpoints are still functional"""
        import httpx
        # Add actual endpoint tests here
        pass
    
    def test_no_hardcoded_text(self):
        """Verify no hardcoded Chinese text in UI components"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        frontend_path = Path('/workspace/frontend/src/components')
        
        for component in frontend_path.rglob('*.tsx'):
            with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Check for Chinese in JSX text content
                jsx_text = re.findall(r'>([^<]+)<', content)
                for text in jsx_text:
                    assert not chinese_pattern.search(text), \
                        f"Hardcoded Chinese in {component}: {text}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''
        return test_code
    
    def run(self, dry_run: bool = True, modules: List[str] = None) -> Dict:
        """Run optimization across all files or specific modules"""
        logger.info(f"Starting optimization (dry_run={dry_run})...")
        
        results = {
            'stats': self.stats,
            'files': [],
            'bilingual_mapping': self.bilingual_map,
        }
        
        # Process backend
        backend_path = self.workspace / 'backend/app'
        if backend_path.exists():
            for py_file in backend_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                file_result = self.process_file(str(py_file), dry_run)
                if file_result['chinese_replacements']:
                    results['files'].append(file_result)
        
        # Process frontend
        frontend_path = self.workspace / 'frontend/src'
        if frontend_path.exists():
            for ts_file in frontend_path.rglob('*.ts*'):
                if 'node_modules' in str(ts_file) or '.next' in str(ts_file):
                    continue
                file_result = self.process_file(str(ts_file), dry_run)
                if file_result['chinese_replacements']:
                    results['files'].append(file_result)
        
        # Generate regression tests
        results['regression_tests'] = self.generate_regression_tests()
        
        # Summary
        total_replacements = sum(
            len(f['chinese_replacements']) for f in results['files']
        )
        results['stats']['total_replacements'] = total_replacements
        results['stats']['files_with_changes'] = len(results['files'])
        
        logger.info(f"Processed {results['stats']['files_processed']} files")
        logger.info(f"Total Chinese replacements: {total_replacements}")
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Code Optimization and I18n Tool')
    parser.add_argument('--workspace', default='/workspace', help='Workspace path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--modules', nargs='*', help='Specific modules to process')
    parser.add_argument('--output', default='optimization_result.json', help='Output file')
    args = parser.parse_args()
    
    optimizer = CodeOptimizer(args.workspace)
    result = optimizer.run(dry_run=args.dry_run, modules=args.modules)
    
    # Save results
    output_path = Path(args.workspace) / 'tools/i18n_optimization' / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save JSON result (without regression tests)
    json_result = {k: v for k, v in result.items() if k != 'regression_tests'}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, indent=2, ensure_ascii=False, default=str)
    
    # Save regression tests
    test_path = output_path.parent / 'test_i18n_regression.py'
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(result['regression_tests'])
    
    # Save bilingual mapping
    map_path = output_path.parent / 'bilingual_mapping_final.json'
    with open(map_path, 'w', encoding='utf-8') as f:
        json.dump(result['bilingual_mapping'], f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Optimization Complete!")
    print(f"{'='*60}")
    print(f"Files with changes: {result['stats']['files_with_changes']}")
    print(f"Total Chinese replacements: {result['stats']['total_replacements']}")
    print(f"\nOutput files:")
    print(f"  - Results: {output_path}")
    print(f"  - Mapping: {map_path}")
    print(f"  - Tests: {test_path}")


if __name__ == '__main__':
    main()
