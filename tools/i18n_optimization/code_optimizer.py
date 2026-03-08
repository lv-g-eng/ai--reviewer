#!/usr/bin/env python3
"""
Code Optimization and I18n Tool
- Scans for redundant code
- Detects unused dependencies
- Creates bilingual mapping table
- Replaces Chinese text with English
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Standard terminology mapping based on GB/T 30269-2013 and industry standards
BILINGUAL_MAPPING = {
    # Common terms
    "验证": "validate",
    "需求": "requirement",
    "测试": "test",
    "配置": "config",
    "请求": "request",
    "响应": "response",
    "错误": "error",
    "状态": "status",
    "数据": "data",
    "用户": "user",
    "服务": "service",
    "接口": "interface",
    "功能": "feature",
    "模块": "module",
    "组件": "component",
    "系统": "system",
    "方法": "method",
    "参数": "param",
    "返回": "return",
    "输入": "input",
    "输出": "output",
    "结果": "result",
    "文件": "file",
    "目录": "directory",
    "路径": "path",
    "类型": "type",
    "实例": "instance",
    "对象": "object",
    "变量": "variable",
    "函数": "function",
    "类": "class",
    "属性": "property",
    "字段": "field",
    "值": "value",
    "密钥": "key",
    "版本": "version",
    "日志": "log",
    "记录": "record",
    "查询": "query",
    "更新": "update",
    "删除": "delete",
    "创建": "create",
    "添加": "add",
    "设置": "set",
    "获取": "get",
    "显示": "show",
    "隐藏": "hide",
    "加载": "load",
    "保存": "save",
    "导出": "export",
    "导入": "import",
    "处理": "handle",
    "检查": "check",
    "清理": "cleanup",
    "重置": "reset",
    "刷新": "refresh",
    "同步": "sync",
    "连接": "connect",
    "断开": "disconnect",
    "启动": "start",
    "停止": "stop",
    "重启": "restart",
    "执行": "execute",
    "运行": "run",
    "完成": "complete",
    "取消": "cancel",
    "确认": "confirm",
    "提交": "submit",
    "取消": "cancel",
    "关闭": "close",
    "打开": "open",
    "编辑": "edit",
    "查看": "view",
    "搜索": "search",
    "过滤": "filter",
    "排序": "sort",
    "分页": "page",
    "列表": "list",
    "详情": "detail",
    "信息": "info",
    "提示": "hint",
    "警告": "warn",
    "异常": "exception",
    "成功": "success",
    "失败": "failure",
    "超时": "timeout",
    "重试": "retry",
    "等待": "wait",
    "注意": "note",
    "说明": "desc",
    "备注": "remark",
    "注释": "comment",
    "文档": "document",
    "代码": "code",
    "项目": "project",
    "任务": "task",
    "计划": "plan",
    "报告": "report",
    "分析": "analyze",
    "优化": "optimize",
    
    # Time units
    "秒": "sec",
    "分钟": "min",
    "小时": "hour",
    "天": "day",
    "毫秒": "ms",
    
    # Technical terms
    "端点": "endpoint",
    "中间件": "middleware",
    "数据库": "database",
    "会话": "session",
    "事务": "transaction",
    "缓存": "cache",
    "队列": "queue",
    "线程": "thread",
    "进程": "process",
    "权限": "permission",
    "角色": "role",
    "认证": "auth",
    "授权": "authorize",
    "加密": "encrypt",
    "解密": "decrypt",
    "签名": "sign",
    "验证": "verify",
    
    # UI terms
    "按钮": "button",
    "表单": "form",
    "输入框": "input",
    "下拉框": "select",
    "复选框": "checkbox",
    "单选框": "radio",
    "开关": "switch",
    "弹窗": "modal",
    "提示框": "tooltip",
    "导航": "nav",
    "菜单": "menu",
    "标签": "tag",
    "标题": "title",
    "内容": "content",
    "页脚": "footer",
    "侧栏": "sidebar",
    "布局": "layout",
    "样式": "style",
    
    # Code quality
    "覆盖": "coverage",
    "重复": "duplicate",
    "冗余": "redundant",
    "复杂度": "complexity",
    "可维护性": "maintainability",
    "可读性": "readability",
    
    # Action phrases
    "使用": "use",
    "包含": "contain",
    "生成": "generate",
    "渲染": "render",
    "应该": "should",
    "发现": "found",
    "提供": "provide",
    "支持": "support",
    "允许": "allow",
    "需要": "need",
    "必须": "must",
    
    # Domain specific
    "审查": "review",
    "架构": "architecture",
    "依赖": "dependency",
    "集成": "integration",
    "部署": "deploy",
    "环境": "env",
    "生产": "prod",
    "开发": "dev",
    "测试": "test",
    
    # Common phrases
    "自定义生成器": "custom generator",
    "测试覆盖": "test coverage",
    "验证需求": "verify requirement",
    "渲染组件": "render component",
    "版本信息": "version info",
    "数据库会话": "db session",
    "提供者实例": "provider instance",
    "等待数据加载": "wait data load",
    "等待数据加载完成": "wait data loaded",
    "等待导出完成": "wait export done",
    "此测试验证": "test verifies",
    "应该在": "should be at",
}

@dataclass
class OptimizationResult:
    """Result of code optimization analysis"""
    chinese_texts: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)
    unused_imports: Dict[str, List[str]] = field(default_factory=dict)
    duplicate_code: List[Dict] = field(default_factory=list)
    complex_functions: List[Dict] = field(default_factory=list)
    replaced_texts: Dict[str, str] = field(default_factory=dict)


class CodeOptimizer:
    """Main optimizer class"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        self.result = OptimizationResult()
        self.bilingual_map = {}
        
    def scan_chinese_text(self) -> Dict[str, List[Tuple[str, int]]]:
        """Scan all files for Chinese text"""
        logger.info("Scanning for Chinese text...")
        chinese_texts = defaultdict(list)
        
        for root, dirs, files in os.walk(self.workspace):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist', 'build', '.next', 'coverage']]
            
            for f in files:
                if f.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            for i, line in enumerate(file, 1):
                                matches = self.chinese_pattern.findall(line)
                                for m in matches:
                                    chinese_texts[m].append((path, i))
                    except Exception as e:
                        logger.debug(f"Error reading {path}: {e}")
                        
        self.result.chinese_texts = dict(chinese_texts)
        logger.info(f"Found {len(chinese_texts)} unique Chinese phrases")
        return dict(chinese_texts)
    
    def detect_unused_imports_python(self, filepath: str) -> List[str]:
        """Detect unused imports in Python files"""
        unused = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.asname or alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.add(alias.asname or alias.name)
            
            # Check usage
            for imp in imports:
                pattern = r'\b' + re.escape(imp) + r'\b'
                usages = len(re.findall(pattern, content))
                if usages <= 1:  # Only the import statement itself
                    unused.append(imp)
                    
        except Exception as e:
            logger.debug(f"Error analyzing {filepath}: {e}")
            
        return unused
    
    def calculate_complexity(self, filepath: str) -> List[Dict]:
        """Calculate cyclomatic complexity for functions"""
        complex_funcs = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = 1  # Base complexity
                    
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                            complexity += 1
                        elif isinstance(child, ast.BoolOp):
                            complexity += len(child.values) - 1
                    
                    if complexity > 10:  # Threshold
                        complex_funcs.append({
                            'file': filepath,
                            'function': node.name,
                            'line': node.lineno,
                            'complexity': complexity
                        })
                        
        except Exception as e:
            logger.debug(f"Error analyzing complexity {filepath}: {e}")
            
        return complex_funcs
    
    def create_bilingual_mapping(self) -> Dict[str, str]:
        """Create bilingual mapping table"""
        logger.info("Creating bilingual mapping...")
        
        # Start with standard mapping
        mapping = BILINGUAL_MAPPING.copy()
        
        # Add discovered phrases
        for chinese, locations in self.result.chinese_texts.items():
            if chinese not in mapping:
                # Try to find similar phrases in standard mapping
                best_match = None
                for key, value in BILINGUAL_MAPPING.items():
                    if key in chinese:
                        best_match = value
                        break
                
                if not best_match:
                    # Generate transliteration (pinyin-like abbreviation)
                    best_match = self._generate_abbreviation(chinese)
                
                mapping[chinese] = best_match
        
        self.bilingual_map = mapping
        return mapping
    
    def _generate_abbreviation(self, chinese: str) -> str:
        """Generate English abbreviation for Chinese text"""
        # Simple mapping for common patterns
        abbrev_map = {
            "测试": "test",
            "验证": "verify",
            "检查": "check",
            "等待": "wait",
            "加载": "load",
            "数据": "data",
            "完成": "done",
            "开始": "start",
            "结束": "end",
        }
        
        result = []
        for char in chinese:
            if char in abbrev_map:
                result.append(abbrev_map[char])
        
        if result:
            return '_'.join(result)
        return f"text_{hash(chinese) % 10000}"
    
    def optimize_file(self, filepath: str) -> bool:
        """Optimize a single file: replace Chinese with English"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            
            # Sort by length (longest first) to avoid partial replacements
            sorted_mapping = sorted(self.bilingual_map.items(), key=lambda x: -len(x[0]))
            
            for chinese, english in sorted_mapping:
                content = content.replace(chinese, english)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error optimizing {filepath}: {e}")
            return False
    
    def run_optimization(self, dry_run: bool = True) -> Dict:
        """Run full optimization process"""
        logger.info(f"Starting optimization (dry_run={dry_run})...")
        
        # 1. Scan for Chinese text
        self.scan_chinese_text()
        
        # 2. Create bilingual mapping
        self.create_bilingual_mapping()
        
        # 3. Analyze Python files for unused imports and complexity
        for root, dirs, files in os.walk(self.workspace / 'backend'):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
            
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(root, f)
                    unused = self.detect_unused_imports_python(path)
                    if unused:
                        self.result.unused_imports[path] = unused
                    
                    complex_funcs = self.calculate_complexity(path)
                    self.result.complex_functions.extend(complex_funcs)
        
        # 4. Apply optimizations
        if not dry_run:
            for root, dirs, files in os.walk(self.workspace):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'dist', 'build', '.next']]
                
                for f in files:
                    if f.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                        path = os.path.join(root, f)
                        if self.optimize_file(path):
                            logger.info(f"Optimized: {path}")
        
        return {
            'chinese_phrases': len(self.result.chinese_texts),
            'bilingual_mapping': self.bilingual_map,
            'unused_imports': self.result.unused_imports,
            'complex_functions': self.result.complex_functions,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Code Optimization and I18n Tool')
    parser.add_argument('--workspace', default='/workspace', help='Workspace path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--output', default='optimization_report.json', help='Output report file')
    args = parser.parse_args()
    
    optimizer = CodeOptimizer(args.workspace)
    result = optimizer.run_optimization(dry_run=args.dry_run)
    
    # Save bilingual mapping
    mapping_file = os.path.join(args.workspace, 'tools/i18n_optimization/bilingual_mapping.json')
    os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(result['bilingual_mapping'], f, ensure_ascii=False, indent=2)
    logger.info(f"Bilingual mapping saved to: {mapping_file}")
    
    # Save optimization report
    report = {
        'chinese_phrases_count': result['chinese_phrases'],
        'unused_imports_count': sum(len(v) for v in result['unused_imports'].values()),
        'complex_functions_count': len(result['complex_functions']),
        'files_with_unused_imports': len(result['unused_imports']),
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Report saved to: {args.output}")
    
    print(f"\n=== Optimization Summary ===")
    print(f"Chinese phrases found: {result['chinese_phrases']}")
    print(f"Files with unused imports: {report['files_with_unused_imports']}")
    print(f"Complex functions (complexity > 10): {len(result['complex_functions'])}")


if __name__ == '__main__':
    main()
