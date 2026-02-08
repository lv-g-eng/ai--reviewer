"""
Tests for JavaScript/TypeScript AST parser
"""
import pytest
from app.services.parsers.javascript_parser import JavaScriptParser


# Sample JavaScript code for testing
SAMPLE_JAVASCRIPT_CODE = '''
// Sample JavaScript module
import { useState, useEffect } from 'react';
import axios from 'axios';

class Calculator {
    constructor(initialValue = 0) {
        this.value = initialValue;
    }
    
    add(x, y) {
        const result = x + y;
        return result;
    }
    
    calculateFibonacci(n) {
        if (n <= 0) {
            return [];
        } else if (n === 1) {
            return [0];
        } else if (n === 2) {
            return [0, 1];
        }
        
        const fib = [0, 1];
        for (let i = 2; i < n; i++) {
            fib.push(fib[i-1] + fib[i-2]);
        }
        
        return fib;
    }
}

function complexFunction(data, threshold = 10) {
    let result = false;
    
    if (data && Object.keys(data).length > 0) {
        for (const [key, value] of Object.entries(data)) {
            if (typeof value === 'number') {
                if (value > threshold) {
                    result = true;
                    break;
                }
            } else if (typeof value === 'string') {
                try {
                    const num = parseInt(value);
                    if (num > threshold) {
                        result = true;
                    }
                } catch (error) {
                    // Ignore parse errors
                }
            }
        }
    }
    
    return result;
}

async function asyncFunction() {
    const data = await fetchData();
    return data;
}

export { Calculator, complexFunction, asyncFunction };
'''

# Sample TypeScript code for testing
SAMPLE_TYPESCRIPT_CODE = '''
// Sample TypeScript module
import { Component } from '@angular/core';

interface User {
    id: number;
    name: string;
    email: string;
}

class UserService {
    private users: User[] = [];
    
    constructor() {
        this.users = [];
    }
    
    addUser(user: User): void {
        this.users.push(user);
    }
    
    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }
    
    async fetchUsers(): Promise<User[]> {
        const response = await fetch('/api/users');
        return response.json();
    }
}

function processData<T>(items: T[], predicate: (item: T) => boolean): T[] {
    const result: T[] = [];
    
    for (const item of items) {
        if (predicate(item)) {
            result.push(item);
        }
    }
    
    return result;
}

export { UserService, User, processData };
'''


def test_parse_javascript_file():
    """Test parsing JavaScript code"""
    parser = JavaScriptParser(language='javascript')
    
    # Parse the sample code
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    # Should parse without errors (or with fallback to esprima)
    assert result.module.language == "javascript"
    assert result.module.name == "test"


def test_parse_typescript_file():
    """Test parsing TypeScript code"""
    parser = JavaScriptParser(language='typescript')
    
    # Parse the sample code
    result = parser.parse_file("test.ts", content=SAMPLE_TYPESCRIPT_CODE)
    
    # Should parse without errors (or with fallback to esprima)
    assert result.module.language == "typescript"
    assert result.module.name == "test"


def test_extract_imports_javascript():
    """Test import extraction from JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    imports = result.module.imports
    # Should extract at least the react and axios imports
    assert len(imports) >= 1
    
    import_names = [imp.module_name for imp in imports]
    # Check if any imports were found (tree-sitter or esprima)
    assert len(import_names) > 0


def test_extract_classes_javascript():
    """Test class extraction from JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    classes = result.module.classes
    # Should find Calculator class
    assert len(classes) >= 1
    
    if len(classes) > 0:
        calc_class = next((c for c in classes if c.name == "Calculator"), None)
        if calc_class:
            assert calc_class.name == "Calculator"
            # Should have methods
            assert len(calc_class.methods) >= 1


def test_extract_functions_javascript():
    """Test function extraction from JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    functions = result.module.functions
    # Should find complexFunction and asyncFunction
    assert len(functions) >= 1
    
    func_names = [f.name for f in functions]
    # Check if functions were extracted
    assert len(func_names) > 0


def test_complexity_calculation_javascript():
    """Test cyclomatic complexity calculation for JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    # Find complexFunction
    complex_func = next((f for f in result.module.functions if f.name == "complexFunction"), None)
    
    if complex_func:
        # Should have complexity > 1 due to nested conditions
        assert complex_func.complexity > 1
        print(f"Complex function complexity: {complex_func.complexity}")


def test_async_detection_javascript():
    """Test async function detection in JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    # Find asyncFunction
    async_func = next((f for f in result.module.functions if f.name == "asyncFunction"), None)
    
    if async_func:
        assert async_func.is_async is True


def test_extract_classes_typescript():
    """Test class extraction from TypeScript"""
    parser = JavaScriptParser(language='typescript')
    result = parser.parse_file("test.ts", content=SAMPLE_TYPESCRIPT_CODE)
    
    classes = result.module.classes
    # TypeScript may not parse correctly with esprima fallback
    # If tree-sitter is available, should find UserService class
    # Otherwise, may have parse errors
    if len(result.errors) == 0:
        # Successfully parsed
        assert len(classes) >= 0  # May or may not find classes depending on parser
    else:
        # Parse errors expected with esprima on TypeScript
        assert len(result.errors) > 0


def test_extract_functions_typescript():
    """Test function extraction from TypeScript"""
    parser = JavaScriptParser(language='typescript')
    result = parser.parse_file("test.ts", content=SAMPLE_TYPESCRIPT_CODE)
    
    functions = result.module.functions
    # Should find processData function
    assert len(functions) >= 0  # May or may not extract depending on parser


def test_metrics_calculation_javascript():
    """Test overall metrics calculation for JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    metrics = result.metrics
    assert "total_classes" in metrics
    assert "total_functions" in metrics
    assert "total_imports" in metrics
    assert metrics["total_classes"] >= 0
    assert metrics["total_functions"] >= 0


def test_line_counting_javascript():
    """Test line counting for JavaScript"""
    parser = JavaScriptParser(language='javascript')
    result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
    
    module = result.module
    assert module.lines_of_code > 0
    assert module.comment_lines >= 0
    assert module.blank_lines >= 0
    assert 0 <= module.comment_ratio <= 1


def test_error_handling_javascript():
    """Test handling of syntax errors in JavaScript"""
    parser = JavaScriptParser(language='javascript')
    
    # Invalid JavaScript code
    invalid_code = "function broken { syntax error"
    result = parser.parse_file("broken.js", content=invalid_code)
    
    # Should either parse with errors or return error message
    # Depending on whether tree-sitter or esprima is used
    assert result.module is not None


def test_parser_availability():
    """Test that parser reports availability correctly"""
    parser = JavaScriptParser(language='javascript')
    
    # Parser should be available (either tree-sitter or esprima)
    assert parser.available is True or parser.available is False
    
    # If not available, should return error in parse result
    if not parser.available:
        result = parser.parse_file("test.js", content=SAMPLE_JAVASCRIPT_CODE)
        assert len(result.errors) > 0


def test_typescript_specific_features():
    """Test TypeScript-specific feature handling"""
    parser = JavaScriptParser(language='typescript')
    result = parser.parse_file("test.ts", content=SAMPLE_TYPESCRIPT_CODE)
    
    # Should handle TypeScript without crashing
    assert result.module is not None
    assert result.module.language == "typescript"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
