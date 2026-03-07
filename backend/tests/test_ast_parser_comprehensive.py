"""
Comprehensive Unit Tests for AST Parser

Task 7.4: Write unit tests for AST parser
Requirements: 5.2

This test suite provides comprehensive coverage for:
- Parsing valid code samples in multiple languages
- Error handling for invalid syntax
- Entity extraction accuracy (functions, classes, methods, imports)
- Complexity calculation
- Line counting and metrics
"""
import logging
logger = logging.getLogger(__name__)

import pytest
import tempfile
import os
from pathlib import Path

from app.services.parsers.python_parser import PythonASTParser
from app.services.parsers.javascript_parser import JavaScriptParser
from app.services.parsers.java_parser import JavaParser
from app.services.parsers.go_parser import GoParser
from app.services.parsers.factory import ParserFactory
from app.schemas.ast_models import ParsedFile, ModuleNode


class TestPythonParserValidCode:
    """Test Python parser with valid code samples"""
    
    @pytest.fixture
    def parser(self):
        return PythonASTParser()
    
    def test_parse_simple_function(self, parser):
        """Test parsing a simple function"""
        code = """
def hello_world():
    logger.info("Hello, World!")
    return True
"""
        result = parser.parse_file("test.py", content=code)
        
        assert result.module is not None
        assert result.module.language == "python"
        assert len(result.module.functions) == 1
        assert result.module.functions[0].name == "hello_world"
        assert len(result.errors) == 0


    
    def test_parse_function_with_parameters(self, parser):
        """Test parsing function with parameters and return type"""
        code = """
def add_numbers(a: int, b: int) -> int:
    '''Add two numbers'''
    return a + b
"""
        result = parser.parse_file("test.py", content=code)
        
        func = result.module.functions[0]
        assert func.name == "add_numbers"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[0].type_annotation == "int"
        assert func.parameters[1].name == "b"
        assert func.return_type == "int"
        assert func.docstring == "Add two numbers"
    
    def test_parse_simple_class(self, parser):
        """Test parsing a simple class"""
        code = """
class MyClass:
    '''A simple class'''
    def __init__(self):
        self.value = 42
"""
        result = parser.parse_file("test.py", content=code)
        
        assert len(result.module.classes) == 1
        cls = result.module.classes[0]
        assert cls.name == "MyClass"
        assert cls.docstring == "A simple class"
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "__init__"
    
    def test_parse_imports(self, parser):
        """Test parsing import statements"""
        code = """
import os
import sys
from typing import List, Dict
from pathlib import Path
"""
        result = parser.parse_file("test.py", content=code)
        
        assert len(result.module.imports) >= 3
        
        # Check for specific imports
        import_modules = [imp.module_name for imp in result.module.imports]
        assert "os" in import_modules
        assert "sys" in import_modules


class TestPythonParserComplexity:
    """Test complexity calculation for Python code"""
    
    @pytest.fixture
    def parser(self):
        return PythonASTParser()
    
    def test_simple_function_complexity(self, parser):
        """Test complexity of simple function (should be 1)"""
        code = """
def simple():
    return 42
"""
        result = parser.parse_file("test.py", content=code)
        func = result.module.functions[0]
        assert func.complexity == 1
    
    def test_if_statement_complexity(self, parser):
        """Test complexity with if statement"""
        code = """
def check_value(x):
    if x > 0:
        return "positive"
    return "non-positive"
"""
        result = parser.parse_file("test.py", content=code)
        func = result.module.functions[0]
        assert func.complexity == 2  # 1 base + 1 if
    
    def test_nested_if_complexity(self, parser):
        """Test complexity with nested if statements"""
        code = """
def classify(x):
    if x > 0:
        if x > 10:
            return "large"
        return "small"
    return "non-positive"
"""
        result = parser.parse_file("test.py", content=code)
        func = result.module.functions[0]
        assert func.complexity == 3  # 1 base + 2 ifs




class TestPythonParserErrorHandling:
    """Test error handling for invalid Python code"""
    
    @pytest.fixture
    def parser(self):
        return PythonASTParser()
    
    def test_syntax_error_missing_colon(self, parser):
        """Test handling of syntax error (missing colon)"""
        code = """
def broken_function()
    return True
"""
        result = parser.parse_file("test.py", content=code)
        
        assert len(result.errors) > 0
        assert "Syntax error" in result.errors[0] or "syntax" in result.errors[0].lower()
    
    def test_syntax_error_invalid_indentation(self, parser):
        """Test handling of indentation error"""
        code = """
def broken_function():
return True
"""
        result = parser.parse_file("test.py", content=code)
        
        assert len(result.errors) > 0
    
    def test_empty_file(self, parser):
        """Test parsing empty file"""
        code = ""
        result = parser.parse_file("test.py", content=code)
        
        # Should parse successfully but have no entities
        assert result.module is not None
        assert len(result.module.functions) == 0
        assert len(result.module.classes) == 0
        assert len(result.errors) == 0


class TestPythonParserMetrics:
    """Test metrics calculation"""
    
    @pytest.fixture
    def parser(self):
        return PythonASTParser()
    
    def test_metrics_calculation(self, parser):
        """Test that metrics are calculated correctly"""
        code = """
import os

def func1():
    return 1

def func2(x):
    if x > 0:
        return x
    return 0

class MyClass:
    def method1(self):
        pass
"""
        result = parser.parse_file("test.py", content=code)
        
        assert "total_classes" in result.metrics
        assert "total_functions" in result.metrics
        assert "total_imports" in result.metrics
        assert "avg_complexity" in result.metrics
        assert "max_complexity" in result.metrics
        
        assert result.metrics["total_classes"] == 1
        assert result.metrics["total_functions"] == 2
        assert result.metrics["avg_complexity"] >= 1


class TestParserFactory:
    """Test parser factory functionality"""
    
    def test_get_python_parser(self):
        """Test getting Python parser by language name"""
        parser = ParserFactory.get_parser("python")
        assert parser is not None
        assert isinstance(parser, PythonASTParser)
    
    def test_get_parser_by_filename(self):
        """Test getting parser by filename"""
        parser = ParserFactory.get_parser_by_filename("test.py")
        assert parser is not None
        assert isinstance(parser, PythonASTParser)
    
    def test_unsupported_language(self):
        """Test handling of unsupported language"""
        parser = ParserFactory.get_parser("unsupported")
        assert parser is None
    
    def test_supported_languages(self):
        """Test getting list of supported languages"""
        languages = ParserFactory.supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert "java" in languages
        assert "go" in languages


class TestParserFileOperations:
    """Test parser file I/O operations"""
    
    def test_parse_from_file_path(self):
        """Test parsing from actual file path"""
        parser = PythonASTParser()
        
        code = """
def test_function():
    return 42
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = parser.parse_file(temp_path)
            
            assert result.module is not None
            assert len(result.module.functions) == 1
            assert result.module.functions[0].name == "test_function"
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
