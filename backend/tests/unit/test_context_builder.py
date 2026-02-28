"""
Unit tests for context_builder service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.context_builder import ContextBuilder


class TestContextBuilder:
    """Test suite for ContextBuilder"""
    
    @pytest.fixture
    def builder(self):
        """Create ContextBuilder instance"""
        return ContextBuilder()
    
    def test_build_context_empty_files(self, builder):
        """Test building context with empty file list"""
        result = builder.build_context([])
        
        assert isinstance(result, dict)
        assert 'files' in result
        assert len(result['files']) == 0
    
    def test_build_context_single_file(self, builder):
        """Test building context with single file"""
        files = [
            {'path': 'test.py', 'content': 'def hello(): pass'}
        ]
        
        result = builder.build_context(files)
        
        assert len(result['files']) == 1
        assert result['files'][0]['path'] == 'test.py'
    
    def test_build_context_multiple_files(self, builder):
        """Test building context with multiple files"""
        files = [
            {'path': 'file1.py', 'content': 'content1'},
            {'path': 'file2.py', 'content': 'content2'},
            {'path': 'file3.py', 'content': 'content3'}
        ]
        
        result = builder.build_context(files)
        
        assert len(result['files']) == 3
    
    def test_extract_imports_python(self, builder):
        """Test extracting imports from Python file"""
        content = """
import os
import sys
from typing import List, Dict
from app.models import User
"""
        
        imports = builder.extract_imports(content, 'python')
        
        assert 'os' in imports
        assert 'sys' in imports
        assert 'typing' in imports
        assert 'app.models' in imports
    
    def test_extract_imports_javascript(self, builder):
        """Test extracting imports from JavaScript file"""
        content = """
import React from 'react';
import { useState, useEffect } from 'react';
const axios = require('axios');
"""
        
        imports = builder.extract_imports(content, 'javascript')
        
        assert 'react' in imports
        assert 'axios' in imports
    
    def test_extract_functions_python(self, builder):
        """Test extracting function names from Python code"""
        content = """
def function1():
    pass

def function2(arg1, arg2):
    return arg1 + arg2

async def async_function():
    await something()
"""
        
        functions = builder.extract_functions(content, 'python')
        
        assert 'function1' in functions
        assert 'function2' in functions
        assert 'async_function' in functions
    
    def test_extract_classes_python(self, builder):
        """Test extracting class names from Python code"""
        content = """
class MyClass:
    def __init__(self):
        pass

class AnotherClass(BaseClass):
    pass
"""
        
        classes = builder.extract_classes(content, 'python')
        
        assert 'MyClass' in classes
        assert 'AnotherClass' in classes
    
    def test_calculate_complexity_simple(self, builder):
        """Test calculating complexity for simple code"""
        content = """
def simple_function():
    return True
"""
        
        complexity = builder.calculate_complexity(content)
        
        assert complexity >= 1
        assert isinstance(complexity, (int, float))
    
    def test_calculate_complexity_complex(self, builder):
        """Test calculating complexity for complex code"""
        content = """
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                while i > 0:
                    i -= 1
    elif x < 0:
        return -1
    else:
        return 0
"""
        
        complexity = builder.calculate_complexity(content)
        
        assert complexity > 5  # Should have high complexity
    
    def test_identify_dependencies_between_files(self, builder):
        """Test identifying dependencies between files"""
        files = [
            {'path': 'module_a.py', 'content': 'from module_b import function'},
            {'path': 'module_b.py', 'content': 'def function(): pass'}
        ]
        
        dependencies = builder.identify_dependencies(files)
        
        assert isinstance(dependencies, dict)
        assert 'module_a.py' in dependencies
    
    def test_build_context_includes_metadata(self, builder):
        """Test that built context includes metadata"""
        files = [
            {'path': 'test.py', 'content': 'def test(): pass'}
        ]
        
        result = builder.build_context(files)
        
        assert 'metadata' in result
        assert 'total_files' in result['metadata']
        assert result['metadata']['total_files'] == 1
    
    def test_filter_relevant_files(self, builder):
        """Test filtering relevant files based on criteria"""
        files = [
            {'path': 'important.py', 'content': 'important code'},
            {'path': 'test_file.py', 'content': 'test code'},
            {'path': 'README.md', 'content': 'documentation'}
        ]
        
        filtered = builder.filter_relevant_files(files, extensions=['.py'])
        
        assert len(filtered) == 2
        assert all(f['path'].endswith('.py') for f in filtered)
    
    def test_summarize_file_content(self, builder):
        """Test summarizing file content"""
        content = "x" * 10000  # Very long content
        
        summary = builder.summarize_content(content, max_length=100)
        
        assert len(summary) <= 100
        assert isinstance(summary, str)
    
    def test_extract_docstrings_python(self, builder):
        """Test extracting docstrings from Python code"""
        content = '''
def function():
    """This is a docstring"""
    pass

class MyClass:
    """Class docstring"""
    pass
'''
        
        docstrings = builder.extract_docstrings(content, 'python')
        
        assert len(docstrings) >= 2
        assert any('This is a docstring' in d for d in docstrings)
    
    def test_build_context_handles_binary_files(self, builder):
        """Test that binary files are handled gracefully"""
        files = [
            {'path': 'image.png', 'content': b'\x89PNG\r\n\x1a\n', 'binary': True},
            {'path': 'text.py', 'content': 'def test(): pass'}
        ]
        
        result = builder.build_context(files)
        
        # Should only include text files or handle binary appropriately
        assert isinstance(result, dict)
    
    def test_identify_entry_points(self, builder):
        """Test identifying entry points in codebase"""
        files = [
            {'path': 'main.py', 'content': 'if __name__ == "__main__": main()'},
            {'path': 'app.py', 'content': 'app = FastAPI()'},
            {'path': 'utils.py', 'content': 'def helper(): pass'}
        ]
        
        entry_points = builder.identify_entry_points(files)
        
        assert 'main.py' in entry_points or 'app.py' in entry_points
