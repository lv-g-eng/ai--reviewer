#!/usr/bin/env python3
"""
Auto-generated Regression Tests for I18n Optimization
Generated: 2026-03-08T08:29:14.033390
"""

import pytest
import os
import re
from pathlib import Path


class TestI18nRegression:
    """Regression tests for Chinese-to-English translation"""
    
    def test_no_chinese_in_backend(self):
        """Verify no Chinese characters remain in backend source files"""
        chinese_pattern = re.compile(r'[一-龥]+')
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
        chinese_pattern = re.compile(r'[一-龥]+')
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
        chinese_pattern = re.compile(r'[一-龥]+')
        frontend_path = Path('/workspace/frontend/src/components')
        
        for component in frontend_path.rglob('*.tsx'):
            with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Check for Chinese in JSX text content
                jsx_text = re.findall(r'>([^<]+)<', content)
                for text in jsx_text:
                    assert not chinese_pattern.search(text),                         f"Hardcoded Chinese in {component}: {text}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
