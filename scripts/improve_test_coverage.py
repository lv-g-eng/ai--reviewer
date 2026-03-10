#!/usr/bin/env python3
"""
测试覆盖率改进脚本
分析现有测试覆盖率并生成测试模板
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoverageAnalyzer:
    """测试覆盖率分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def analyze_backend_coverage(self) -> Dict[str, Any]:
        """分析后端测试覆盖率"""
        logger.info("🔍 分析后端测试覆盖率...")
        
        if not self.backend_dir.exists():
            return {"error": "Backend directory not found"}
        
        try:
            # 运行pytest with coverage
            cmd = [
                "python", "-m", "pytest",
                "--cov=app",
                "--cov-report=json",
                "--cov-report=term-missing",
                "tests/"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True
            )
            
            # 读取覆盖率报告
            coverage_file = self.backend_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "files": coverage_data.get("files", {}),
                    "missing_lines": self._extract_missing_lines(coverage_data)
                }
            else:
                return {"error": "Coverage report not generated"}
                
        except Exception as e:
            logger.error(f"Backend coverage analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_frontend_coverage(self) -> Dict[str, Any]:
        """分析前端测试覆盖率"""
        logger.info("🔍 分析前端测试覆盖率...")
        
        if not self.frontend_dir.exists():
            return {"error": "Frontend directory not found"}
        
        try:
            # 检查是否有Jest配置
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                return {"error": "package.json not found"}
            
            # 运行Jest with coverage
            cmd = ["npm", "run", "test", "--", "--coverage", "--watchAll=false"]
            
            result = subprocess.run(
                cmd,
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            
            # 查找覆盖率报告
            coverage_dir = self.frontend_dir / "coverage"
            if coverage_dir.exists():
                coverage_summary = coverage_dir / "coverage-summary.json"
                if coverage_summary.exists():
                    with open(coverage_summary, 'r') as f:
                        coverage_data = json.load(f)
                    
                    return {
                        "total_coverage": coverage_data.get("total", {}).get("lines", {}).get("pct", 0),
                        "files": coverage_data,
                        "uncovered_files": self._find_uncovered_frontend_files()
                    }
            
            return {"error": "Coverage report not found"}
            
        except Exception as e:
            logger.error(f"Frontend coverage analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_missing_lines(self, coverage_data: Dict) -> Dict[str, List[int]]:
        """提取缺失测试的行"""
        missing_lines = {}
        
        for file_path, file_data in coverage_data.get("files", {}).items():
            missing = file_data.get("missing_lines", [])
            if missing:
                missing_lines[file_path] = missing
        
        return missing_lines
    
    def _find_uncovered_frontend_files(self) -> List[str]:
        """查找未覆盖的前端文件"""
        src_dir = self.frontend_dir / "src"
        if not src_dir.exists():
            return []
        
        # 查找所有源文件
        source_files = []
        for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            source_files.extend(src_dir.rglob(ext))
        
        # 查找所有测试文件
        test_files = []
        for ext in ["*.test.ts", "*.test.tsx", "*.test.js", "*.test.jsx", "*.spec.ts", "*.spec.tsx"]:
            test_files.extend(src_dir.rglob(ext))
        
        # 提取测试文件对应的源文件名
        tested_files = set()
        for test_file in test_files:
            # 移除测试后缀
            source_name = str(test_file).replace(".test.", ".").replace(".spec.", ".")
            tested_files.add(source_name)
        
        # 找出未测试的文件
        uncovered = []
        for source_file in source_files:
            if str(source_file) not in tested_files and not str(source_file).endswith(('.test.ts', '.test.tsx', '.spec.ts', '.spec.tsx')):
                uncovered.append(str(source_file.relative_to(self.frontend_dir)))
        
        return uncovered
    
    def generate_backend_test_templates(self, coverage_data: Dict) -> List[str]:
        """生成后端测试模板"""
        logger.info("📝 生成后端测试模板...")
        
        templates = []
        
        # 查找低覆盖率的文件
        low_coverage_files = []
        for file_path, file_data in coverage_data.get("files", {}).items():
            coverage_pct = file_data.get("summary", {}).get("percent_covered", 100)
            if coverage_pct < 70:  # 覆盖率低于70%
                low_coverage_files.append((file_path, coverage_pct))
        
        # 为每个低覆盖率文件生成测试模板
        for file_path, coverage_pct in low_coverage_files:
            template = self._generate_python_test_template(file_path, coverage_pct)
            if template:
                templates.append(template)
        
        return templates
    
    def generate_frontend_test_templates(self, uncovered_files: List[str]) -> List[str]:
        """生成前端测试模板"""
        logger.info("📝 生成前端测试模板...")
        
        templates = []
        
        for file_path in uncovered_files[:10]:  # 限制生成数量
            template = self._generate_typescript_test_template(file_path)
            if template:
                templates.append(template)
        
        return templates
    
    def _generate_python_test_template(self, file_path: str, coverage_pct: float) -> Optional[str]:
        """生成Python测试模板"""
        # 提取模块名
        if not file_path.startswith("app/"):
            return None
        
        module_path = file_path.replace("app/", "").replace(".py", "").replace("/", ".")
        class_name = Path(file_path).stem.title().replace("_", "")
        test_file_name = f"test_{Path(file_path).stem}.py"
        
        template = f'''"""
测试模块: {module_path}
当前覆盖率: {coverage_pct:.1f}%
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.{module_path.replace(".", "/")} import *


class Test{class_name}:
    """测试 {class_name} 类"""
    
    def setup_method(self):
        """测试前置设置"""
        pass
    
    def teardown_method(self):
        """测试后置清理"""
        pass
    
    def test_initialization(self):
        """测试初始化"""
        # TODO: 实现初始化测试
        pass
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """测试异步方法"""
        # TODO: 实现异步方法测试
        pass
    
    def test_error_handling(self):
        """测试错误处理"""
        # TODO: 实现错误处理测试
        pass
    
    @patch('app.{module_path}.some_dependency')
    def test_with_mock(self, mock_dependency):
        """测试使用Mock"""
        # TODO: 实现Mock测试
        pass


# 集成测试
class Test{class_name}Integration:
    """集成测试"""
    
    @pytest.mark.integration
    def test_integration_scenario(self):
        """测试集成场景"""
        # TODO: 实现集成测试
        pass


# 性能测试
class Test{class_name}Performance:
    """性能测试"""
    
    @pytest.mark.performance
    def test_performance_benchmark(self):
        """性能基准测试"""
        # TODO: 实现性能测试
        pass
'''
        
        return template
    
    def _generate_typescript_test_template(self, file_path: str) -> Optional[str]:
        """生成TypeScript测试模板"""
        if not file_path.endswith(('.ts', '.tsx')):
            return None
        
        component_name = Path(file_path).stem
        is_component = file_path.endswith('.tsx')
        
        if is_component:
            template = f'''/**
 * 测试组件: {component_name}
 * 文件路径: {file_path}
 */

import React from 'react';
import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ jest }} from '@jest/globals';
import {component_name} from '../{component_name}';

describe('{component_name}', () => {{
  beforeEach(() => {{
    // 测试前置设置
  }});

  afterEach(() => {{
    // 测试后置清理
    jest.clearAllMocks();
  }});

  it('should render correctly', () => {{
    render(<{component_name} />);
    // TODO: 添加渲染测试断言
  }});

  it('should handle props correctly', () => {{
    const mockProps = {{
      // TODO: 定义测试属性
    }};
    render(<{component_name} {{...mockProps}} />);
    // TODO: 添加属性测试断言
  }});

  it('should handle user interactions', async () => {{
    render(<{component_name} />);
    
    // TODO: 模拟用户交互
    // const button = screen.getByRole('button');
    // fireEvent.click(button);
    
    // TODO: 验证交互结果
    // await waitFor(() => {{
    //   expect(screen.getByText('Expected Text')).toBeInTheDocument();
    // }});
  }});

  it('should handle error states', () => {{
    // TODO: 测试错误状态
  }});

  it('should be accessible', () => {{
    render(<{component_name} />);
    // TODO: 添加可访问性测试
  }});
}});
'''
        else:
            template = f'''/**
 * 测试模块: {component_name}
 * 文件路径: {file_path}
 */

import {{ jest }} from '@jest/globals';
import * as {component_name}Module from '../{component_name}';

describe('{component_name}', () => {{
  beforeEach(() => {{
    // 测试前置设置
  }});

  afterEach(() => {{
    // 测试后置清理
    jest.clearAllMocks();
  }});

  describe('function tests', () => {{
    it('should export expected functions', () => {{
      // TODO: 验证导出的函数
    }});

    it('should handle valid inputs', () => {{
      // TODO: 测试有效输入
    }});

    it('should handle invalid inputs', () => {{
      // TODO: 测试无效输入
    }});

    it('should handle edge cases', () => {{
      // TODO: 测试边界情况
    }});
  }});

  describe('error handling', () => {{
    it('should throw appropriate errors', () => {{
      // TODO: 测试错误抛出
    }});

    it('should handle async errors', async () => {{
      // TODO: 测试异步错误处理
    }});
  }});

  describe('performance', () => {{
    it('should perform within acceptable limits', () => {{
      // TODO: 性能测试
    }});
  }});
}});
'''
        
        return template
    
    def save_test_templates(self, templates: List[str], output_dir: str):
        """保存测试模板到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, template in enumerate(templates):
            file_name = f"test_template_{i+1}.py" if "import pytest" in template else f"test_template_{i+1}.test.ts"
            file_path = output_path / file_name
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            logger.info(f"测试模板已保存: {file_path}")
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """生成完整的覆盖率报告"""
        logger.info("📊 生成覆盖率报告...")
        
        backend_coverage = self.analyze_backend_coverage()
        frontend_coverage = self.analyze_frontend_coverage()
        
        report = {
            "timestamp": "2024-03-10T12:00:00Z",
            "backend": backend_coverage,
            "frontend": frontend_coverage,
            "recommendations": []
        }
        
        # 生成建议
        if isinstance(backend_coverage.get("total_coverage"), (int, float)):
            if backend_coverage["total_coverage"] < 70:
                report["recommendations"].append("后端测试覆盖率低于70%，需要增加测试")
        
        if isinstance(frontend_coverage.get("total_coverage"), (int, float)):
            if frontend_coverage["total_coverage"] < 70:
                report["recommendations"].append("前端测试覆盖率低于70%，需要增加测试")
        
        # 保存报告
        report_file = self.project_root / "test_coverage_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"覆盖率报告已保存: {report_file}")
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试覆盖率改进工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--generate-templates", action="store_true", help="生成测试模板")
    parser.add_argument("--output-dir", default="test_templates", help="测试模板输出目录")
    
    args = parser.parse_args()
    
    analyzer = TestCoverageAnalyzer(args.project_root)
    
    # 生成覆盖率报告
    report = analyzer.generate_coverage_report()
    
    # 打印摘要
    print("\n" + "="*50)
    print("📊 测试覆盖率报告")
    print("="*50)
    
    if "error" not in report["backend"]:
        backend_coverage = report["backend"].get("total_coverage", 0)
        print(f"后端覆盖率: {backend_coverage:.1f}%")
    else:
        print(f"后端覆盖率: 分析失败 - {report['backend']['error']}")
    
    if "error" not in report["frontend"]:
        frontend_coverage = report["frontend"].get("total_coverage", 0)
        print(f"前端覆盖率: {frontend_coverage:.1f}%")
    else:
        print(f"前端覆盖率: 分析失败 - {report['frontend']['error']}")
    
    # 生成测试模板
    if args.generate_templates:
        print(f"\n📝 生成测试模板到: {args.output_dir}")
        
        templates = []
        
        # 后端模板
        if "error" not in report["backend"]:
            backend_templates = analyzer.generate_backend_test_templates(report["backend"])
            templates.extend(backend_templates)
        
        # 前端模板
        if "error" not in report["frontend"]:
            uncovered_files = report["frontend"].get("uncovered_files", [])
            frontend_templates = analyzer.generate_frontend_test_templates(uncovered_files)
            templates.extend(frontend_templates)
        
        if templates:
            analyzer.save_test_templates(templates, args.output_dir)
            print(f"✅ 已生成 {len(templates)} 个测试模板")
        else:
            print("ℹ️ 没有需要生成的测试模板")
    
    # 打印建议
    if report["recommendations"]:
        print(f"\n💡 改进建议:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    print("="*50)


if __name__ == "__main__":
    main()