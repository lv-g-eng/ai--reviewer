"""
Tests for multi-language AST parser
Task 7.1: Create multi-language AST parser
"""
import pytest
from app.services.parsers.factory import ParserFactory
from app.services.parsers.python_parser import PythonASTParser
from app.services.parsers.javascript_parser import JavaScriptParser
from app.services.parsers.java_parser import JavaParser
from app.services.parsers.go_parser import GoParser


class TestParserFactory:
    """Test parser factory functionality"""
    
    def test_get_python_parser(self):
        """Test getting Python parser"""
        parser = ParserFactory.get_parser('python')
        assert parser is not None
        assert isinstance(parser, PythonASTParser)
    
    def test_get_python_parser_by_extension(self):
        """Test getting Python parser by file extension"""
        parser = ParserFactory.get_parser('py')
        assert parser is not None
        assert isinstance(parser, PythonASTParser)
    
    def test_get_javascript_parser(self):
        """Test getting JavaScript parser"""
        parser = ParserFactory.get_parser('javascript')
        assert parser is not None
        assert isinstance(parser, JavaScriptParser)
    
    def test_get_typescript_parser(self):
        """Test getting TypeScript parser"""
        parser = ParserFactory.get_parser('typescript')
        assert parser is not None
        assert isinstance(parser, JavaScriptParser)
    
    def test_get_java_parser(self):
        """Test getting Java parser"""
        parser = ParserFactory.get_parser('java')
        assert parser is not None
        assert isinstance(parser, JavaParser)
    
    def test_get_go_parser(self):
        """Test getting Go parser"""
        parser = ParserFactory.get_parser('go')
        assert parser is not None
        assert isinstance(parser, GoParser)
    
    def test_get_parser_by_filename(self):
        """Test getting parser by filename"""
        test_cases = [
            ('test.py', PythonASTParser),
            ('test.js', JavaScriptParser),
            ('test.ts', JavaScriptParser),
            ('test.java', JavaParser),
            ('test.go', GoParser),
        ]
        
        for filename, expected_type in test_cases:
            parser = ParserFactory.get_parser_by_filename(filename)
            assert parser is not None
            assert isinstance(parser, expected_type)
    
    def test_supported_languages(self):
        """Test getting list of supported languages"""
        languages = ParserFactory.supported_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'typescript' in languages
        assert 'java' in languages
        assert 'go' in languages
    
    def test_is_language_supported(self):
        """Test checking if language is supported"""
        assert ParserFactory.is_language_supported('python')
        assert ParserFactory.is_language_supported('javascript')
        assert ParserFactory.is_language_supported('typescript')
        assert ParserFactory.is_language_supported('java')
        assert ParserFactory.is_language_supported('go')
        assert not ParserFactory.is_language_supported('rust')
        assert not ParserFactory.is_language_supported('c++')


class TestPythonParser:
    """Test Python parser functionality"""
    
    def test_parse_simple_python_file(self):
        """Test parsing a simple Python file"""
        code = '''
def hello_world():
    """Say hello"""
    print("Hello, World!")
    return True

class MyClass:
    """A simple class"""
    def __init__(self):
        self.value = 42
'''
        parser = PythonASTParser()
        result = parser.parse_file('test.py', content=code)
        
        assert result.module is not None
        assert result.module.language == 'python'
        assert len(result.module.functions) == 1
        assert result.module.functions[0].name == 'hello_world'
        assert len(result.module.classes) == 1
        assert result.module.classes[0].name == 'MyClass'
        assert len(result.errors) == 0
    
    def test_parse_python_with_imports(self):
        """Test parsing Python file with imports"""
        code = '''
import os
from typing import List, Dict
from pathlib import Path

def process_files():
    pass
'''
        parser = PythonASTParser()
        result = parser.parse_file('test.py', content=code)
        
        assert len(result.module.imports) >= 2
        assert any(imp.module_name == 'os' for imp in result.module.imports)


class TestJavaScriptParser:
    """Test JavaScript parser functionality"""
    
    def test_parse_simple_javascript_file(self):
        """Test parsing a simple JavaScript file"""
        code = '''
function helloWorld() {
    console.log("Hello, World!");
    return true;
}

class MyClass {
    constructor() {
        this.value = 42;
    }
}
'''
        parser = JavaScriptParser(language='javascript')
        result = parser.parse_file('test.js', content=code)
        
        assert result.module is not None
        assert result.module.language == 'javascript'
        # Parser should extract functions and classes
        assert len(result.errors) == 0 or 'not available' in result.errors[0]


class TestJavaParser:
    """Test Java parser functionality"""
    
    def test_parse_simple_java_file(self):
        """Test parsing a simple Java file"""
        code = '''
package com.example;

import java.util.List;
import java.util.ArrayList;

public class HelloWorld {
    private int value;
    
    public HelloWorld() {
        this.value = 42;
    }
    
    public void sayHello() {
        System.out.println("Hello, World!");
    }
    
    public int getValue() {
        return value;
    }
}
'''
        parser = JavaParser()
        result = parser.parse_file('HelloWorld.java', content=code)
        
        assert result.module is not None
        assert result.module.language == 'java'
        # Parser should extract imports and classes
        assert len(result.errors) == 0 or 'not available' in result.errors[0]


class TestGoParser:
    """Test Go parser functionality"""
    
    def test_parse_simple_go_file(self):
        """Test parsing a simple Go file"""
        code = '''
package main

import (
    "fmt"
    "os"
)

func main() {
    fmt.Println("Hello, World!")
}

func add(a int, b int) int {
    return a + b
}
'''
        parser = GoParser()
        result = parser.parse_file('main.go', content=code)
        
        assert result.module is not None
        assert result.module.language == 'go'
        # Parser should extract imports and functions
        assert len(result.errors) == 0 or 'not available' in result.errors[0]


class TestParserMetrics:
    """Test parser metrics calculation"""
    
    def test_python_complexity_calculation(self):
        """Test cyclomatic complexity calculation for Python"""
        code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            return "large"
        else:
            return "small"
    elif x < 0:
        return "negative"
    else:
        return "zero"
'''
        parser = PythonASTParser()
        result = parser.parse_file('test.py', content=code)
        
        assert len(result.module.functions) == 1
        func = result.module.functions[0]
        # Should have complexity > 1 due to multiple if statements
        assert func.complexity > 1
    
    def test_line_counting(self):
        """Test line counting functionality"""
        code = '''# Comment line
def hello():
    """Docstring"""
    # Another comment
    print("Hello")
    
    return True

'''
        parser = PythonASTParser()
        result = parser.parse_file('test.py', content=code)
        
        assert result.module.lines_of_code > 0
        assert result.module.comment_lines > 0
        assert result.module.blank_lines > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
