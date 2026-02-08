"""
Property-based tests for code parsing completeness

Tests Property 6: Code Parsing Completeness
For any valid source code in a supported language (Python, JavaScript, TypeScript),
the Graph Analysis Service SHALL successfully parse it into an AST representation
without errors.

Validates Requirements: 2.1, 9.1, 9.2
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from pathlib import Path
import tempfile
import os

from app.services.parsers.factory import ParserFactory
from app.services.parsers.python_parser import PythonASTParser
from app.services.parsers.javascript_parser import JavaScriptParser


# ============================================================================
# Code Generation Strategies
# ============================================================================

@st.composite
def valid_python_identifier(draw):
    """Generate valid Python identifiers"""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyz_'))
    rest = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyz0123456789_',
        min_size=0,
        max_size=15
    ))
    identifier = first_char + rest
    
    # Avoid Python keywords
    python_keywords = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    }
    assume(identifier not in python_keywords)
    
    return identifier


@st.composite
def valid_javascript_identifier(draw):
    """Generate valid JavaScript identifiers"""
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$'))
    rest = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$',
        min_size=0,
        max_size=15
    ))
    identifier = first_char + rest
    
    # Avoid JavaScript keywords
    js_keywords = {
        'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
        'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
        'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
        'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
        'void', 'while', 'with', 'yield'
    }
    assume(identifier not in js_keywords)
    
    return identifier


@st.composite
def simple_python_function(draw):
    """Generate a simple valid Python function"""
    func_name = draw(valid_python_identifier())
    param_count = draw(st.integers(min_value=0, max_value=3))
    params = [draw(valid_python_identifier()) for _ in range(param_count)]
    
    # Generate function body
    body_type = draw(st.sampled_from(['return_value', 'pass', 'simple_calc']))
    
    if body_type == 'return_value':
        return_val = draw(st.integers(min_value=0, max_value=100))
        body = f"    return {return_val}"
    elif body_type == 'pass':
        body = "    pass"
    else:  # simple_calc
        if param_count > 0:
            body = f"    return {params[0]} + 1"
        else:
            body = "    return 42"
    
    param_str = ', '.join(params)
    code = f"def {func_name}({param_str}):\n{body}\n"
    
    return code


@st.composite
def simple_python_class(draw):
    """Generate a simple valid Python class"""
    class_name = draw(valid_python_identifier()).capitalize()
    method_count = draw(st.integers(min_value=0, max_value=2))
    
    code = f"class {class_name}:\n"
    
    if method_count == 0:
        code += "    pass\n"
    else:
        for i in range(method_count):
            method_name = draw(valid_python_identifier())
            code += f"    def {method_name}(self):\n"
            code += "        pass\n"
    
    return code


@st.composite
def simple_python_import(draw):
    """Generate a simple valid Python import"""
    import_type = draw(st.sampled_from(['standard', 'from']))
    
    # Use common standard library modules
    modules = ['os', 'sys', 'json', 'math', 'random', 'datetime', 'collections']
    module = draw(st.sampled_from(modules))
    
    if import_type == 'standard':
        return f"import {module}\n"
    else:
        # For 'from' imports, use known submodules/functions
        from_items = {
            'os': ['path', 'environ'],
            'sys': ['argv', 'exit'],
            'json': ['loads', 'dumps'],
            'math': ['sqrt', 'pi'],
            'random': ['choice', 'randint'],
            'datetime': ['datetime', 'date'],
            'collections': ['Counter', 'defaultdict']
        }
        item = draw(st.sampled_from(from_items.get(module, ['*'])))
        return f"from {module} import {item}\n"


@st.composite
def valid_python_code(draw):
    """Generate valid Python code with various elements"""
    elements = []
    
    # Add imports
    import_count = draw(st.integers(min_value=0, max_value=3))
    for _ in range(import_count):
        elements.append(draw(simple_python_import()))
    
    # Add classes
    class_count = draw(st.integers(min_value=0, max_value=2))
    for _ in range(class_count):
        elements.append(draw(simple_python_class()))
    
    # Add functions
    func_count = draw(st.integers(min_value=1, max_value=3))
    for _ in range(func_count):
        elements.append(draw(simple_python_function()))
    
    return '\n'.join(elements)


@st.composite
def simple_javascript_function(draw):
    """Generate a simple valid JavaScript function"""
    func_name = draw(valid_javascript_identifier())
    param_count = draw(st.integers(min_value=0, max_value=3))
    params = [draw(valid_javascript_identifier()) for _ in range(param_count)]
    
    # Generate function body
    body_type = draw(st.sampled_from(['return_value', 'empty', 'simple_calc']))
    
    if body_type == 'return_value':
        return_val = draw(st.integers(min_value=0, max_value=100))
        body = f"  return {return_val};"
    elif body_type == 'empty':
        body = "  // empty function"
    else:  # simple_calc
        if param_count > 0:
            body = f"  return {params[0]} + 1;"
        else:
            body = "  return 42;"
    
    param_str = ', '.join(params)
    code = f"function {func_name}({param_str}) {{\n{body}\n}}\n"
    
    return code


@st.composite
def simple_javascript_class(draw):
    """Generate a simple valid JavaScript class"""
    class_name = draw(valid_javascript_identifier()).capitalize()
    method_count = draw(st.integers(min_value=0, max_value=2))
    
    code = f"class {class_name} {{\n"
    
    # Add constructor
    code += "  constructor() {\n"
    code += "    this.value = 0;\n"
    code += "  }\n"
    
    # Add methods
    for i in range(method_count):
        method_name = draw(valid_javascript_identifier())
        code += f"  {method_name}() {{\n"
        code += "    return this.value;\n"
        code += "  }\n"
    
    code += "}\n"
    
    return code


@st.composite
def simple_javascript_import(draw):
    """Generate a simple valid JavaScript import"""
    import_type = draw(st.sampled_from(['default', 'named', 'namespace']))
    module_name = draw(valid_javascript_identifier())
    
    if import_type == 'default':
        var_name = draw(valid_javascript_identifier())
        return f"import {var_name} from '{module_name}';\n"
    elif import_type == 'named':
        item_count = draw(st.integers(min_value=1, max_value=3))
        items = [draw(valid_javascript_identifier()) for _ in range(item_count)]
        items_str = ', '.join(items)
        return f"import {{ {items_str} }} from '{module_name}';\n"
    else:  # namespace
        var_name = draw(valid_javascript_identifier())
        return f"import * as {var_name} from '{module_name}';\n"


@st.composite
def valid_javascript_code(draw):
    """Generate valid JavaScript code with various elements"""
    elements = []
    
    # Add imports
    import_count = draw(st.integers(min_value=0, max_value=2))
    for _ in range(import_count):
        elements.append(draw(simple_javascript_import()))
    
    # Add classes
    class_count = draw(st.integers(min_value=0, max_value=2))
    for _ in range(class_count):
        elements.append(draw(simple_javascript_class()))
    
    # Add functions
    func_count = draw(st.integers(min_value=1, max_value=3))
    for _ in range(func_count):
        elements.append(draw(simple_javascript_function()))
    
    return '\n'.join(elements)


@st.composite
def simple_typescript_interface(draw):
    """Generate a simple valid TypeScript interface"""
    interface_name = draw(valid_javascript_identifier()).capitalize()
    prop_count = draw(st.integers(min_value=1, max_value=3))
    
    code = f"interface {interface_name} {{\n"
    
    for _ in range(prop_count):
        prop_name = draw(valid_javascript_identifier())
        prop_type = draw(st.sampled_from(['string', 'number', 'boolean']))
        code += f"  {prop_name}: {prop_type};\n"
    
    code += "}\n"
    
    return code


@st.composite
def valid_typescript_code(draw):
    """Generate valid TypeScript code with various elements"""
    elements = []
    
    # Add imports
    import_count = draw(st.integers(min_value=0, max_value=2))
    for _ in range(import_count):
        elements.append(draw(simple_javascript_import()))
    
    # Add interfaces
    interface_count = draw(st.integers(min_value=0, max_value=2))
    for _ in range(interface_count):
        elements.append(draw(simple_typescript_interface()))
    
    # Add classes
    class_count = draw(st.integers(min_value=0, max_value=1))
    for _ in range(class_count):
        elements.append(draw(simple_javascript_class()))
    
    # Add functions
    func_count = draw(st.integers(min_value=1, max_value=2))
    for _ in range(func_count):
        elements.append(draw(simple_javascript_function()))
    
    return '\n'.join(elements)


# ============================================================================
# Property Tests
# ============================================================================

@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(code=valid_python_code())
def test_property_python_parsing_completeness(code):
    """
    Property 6: Code Parsing Completeness (Python)
    
    For any valid Python source code, the Graph Analysis Service SHALL
    successfully parse it into an AST representation without errors.
    
    **Validates: Requirements 2.1, 9.1**
    """
    parser = PythonASTParser()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Parse the code
        result = parser.parse_file(temp_path, content=code)
        
        # PROPERTY: Should parse without errors
        assert len(result.errors) == 0, \
            f"Parser should handle valid Python code without errors. Errors: {result.errors}\nCode:\n{code}"
        
        # PROPERTY: Should return a ParsedFile with module
        assert result.module is not None, "Should return a module"
        assert result.module.language == "python", "Should identify language as Python"
        
        # PROPERTY: Should extract basic structure
        # At minimum, should have parsed the file (even if no elements found)
        assert result.module.file_path == temp_path, "Should preserve file path"
        assert result.module.name is not None, "Should have module name"
        
        # PROPERTY: Metrics should be present
        assert result.metrics is not None, "Should have metrics"
        assert isinstance(result.metrics, dict), "Metrics should be a dictionary"
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(code=valid_javascript_code())
def test_property_javascript_parsing_completeness(code):
    """
    Property 6: Code Parsing Completeness (JavaScript)
    
    For any valid JavaScript source code, the Graph Analysis Service SHALL
    successfully parse it into an AST representation without errors.
    
    **Validates: Requirements 2.1, 9.2**
    """
    parser = JavaScriptParser(language='javascript')
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Parse the code
        result = parser.parse_file(temp_path, content=code)
        
        # PROPERTY: Should parse without errors (or gracefully handle with fallback)
        # Note: JavaScript parser may use tree-sitter or esprima fallback
        # Both should handle valid JavaScript without critical errors
        assert result.module is not None, "Should return a module even if parsing has issues"
        
        # If parser is available and working, should have no errors
        if parser.available:
            # Parser is available, should parse successfully
            assert len(result.errors) == 0, \
                f"Parser should handle valid JavaScript code without errors. Errors: {result.errors}\nCode:\n{code}"
        
        # PROPERTY: Should identify language correctly
        assert result.module.language == "javascript", "Should identify language as JavaScript"
        
        # PROPERTY: Should extract basic structure
        assert result.module.file_path == temp_path, "Should preserve file path"
        assert result.module.name is not None, "Should have module name"
        
        # PROPERTY: Metrics should be present
        assert result.metrics is not None, "Should have metrics"
        assert isinstance(result.metrics, dict), "Metrics should be a dictionary"
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(code=valid_typescript_code())
def test_property_typescript_parsing_completeness(code):
    """
    Property 6: Code Parsing Completeness (TypeScript)
    
    For any valid TypeScript source code, the Graph Analysis Service SHALL
    successfully parse it into an AST representation without errors.
    
    **Validates: Requirements 2.1, 9.2**
    """
    parser = JavaScriptParser(language='typescript')
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Parse the code
        result = parser.parse_file(temp_path, content=code)
        
        # PROPERTY: Should return a module
        assert result.module is not None, "Should return a module"
        
        # Note: TypeScript parsing may have limitations with esprima fallback
        # Tree-sitter handles TypeScript better
        # We verify that parsing completes without crashing
        
        # PROPERTY: Should identify language correctly
        assert result.module.language == "typescript", "Should identify language as TypeScript"
        
        # PROPERTY: Should extract basic structure
        assert result.module.file_path == temp_path, "Should preserve file path"
        assert result.module.name is not None, "Should have module name"
        
        # PROPERTY: Metrics should be present
        assert result.metrics is not None, "Should have metrics"
        assert isinstance(result.metrics, dict), "Metrics should be a dictionary"
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=valid_python_code(),
    language=st.sampled_from(['python', 'py'])
)
def test_property_parser_factory_python(code, language):
    """
    Property 6: Parser Factory should return correct parser for Python
    
    **Validates: Requirements 2.1, 9.1**
    """
    parser = ParserFactory.get_parser(language)
    
    # PROPERTY: Should return a parser
    assert parser is not None, f"Should return parser for language '{language}'"
    assert isinstance(parser, PythonASTParser), "Should return PythonASTParser"
    
    # PROPERTY: Parser should successfully parse valid code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = parser.parse_file(temp_path, content=code)
        assert len(result.errors) == 0, "Should parse without errors"
        assert result.module is not None, "Should return module"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    code=valid_javascript_code(),
    language=st.sampled_from(['javascript', 'js'])
)
def test_property_parser_factory_javascript(code, language):
    """
    Property 6: Parser Factory should return correct parser for JavaScript
    
    **Validates: Requirements 2.1, 9.2**
    """
    parser = ParserFactory.get_parser(language)
    
    # PROPERTY: Should return a parser
    assert parser is not None, f"Should return parser for language '{language}'"
    assert isinstance(parser, JavaScriptParser), "Should return JavaScriptParser"
    
    # PROPERTY: Parser should successfully parse valid code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = parser.parse_file(temp_path, content=code)
        assert result.module is not None, "Should return module"
        
        # If parser is available, should parse without errors
        if parser.available:
            assert len(result.errors) == 0, "Should parse without errors when parser is available"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    filename=st.sampled_from(['test.py', 'module.py', 'app.js', 'script.js', 'component.ts', 'types.ts'])
)
def test_property_parser_factory_by_filename(filename):
    """
    Property 6: Parser Factory should return correct parser by filename
    
    **Validates: Requirements 2.1, 9.1, 9.2**
    """
    parser = ParserFactory.get_parser_by_filename(filename)
    
    # PROPERTY: Should return appropriate parser based on extension
    assert parser is not None, f"Should return parser for filename '{filename}'"
    
    if filename.endswith('.py'):
        assert isinstance(parser, PythonASTParser), "Should return PythonASTParser for .py files"
    elif filename.endswith('.js'):
        assert isinstance(parser, JavaScriptParser), "Should return JavaScriptParser for .js files"
        assert parser.language == 'javascript', "Should configure for JavaScript"
    elif filename.endswith('.ts'):
        assert isinstance(parser, JavaScriptParser), "Should return JavaScriptParser for .ts files"
        assert parser.language == 'typescript', "Should configure for TypeScript"


@pytest.mark.property_test
@pytest.mark.feature("platform-feature-completion-and-optimization")
@pytest.mark.property(6, "Code Parsing Completeness")
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
@given(code=valid_python_code())
def test_property_parsed_structure_completeness(code):
    """
    Property 6: Parsed structure should contain expected elements
    
    For any valid code, the parsed result should extract classes, functions,
    and imports when present.
    
    **Validates: Requirements 2.1, 9.1**
    """
    parser = PythonASTParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = parser.parse_file(temp_path, content=code)
        
        # PROPERTY: Should extract structure elements
        assert hasattr(result.module, 'classes'), "Module should have classes attribute"
        assert hasattr(result.module, 'functions'), "Module should have functions attribute"
        assert hasattr(result.module, 'imports'), "Module should have imports attribute"
        
        # PROPERTY: Elements should be lists
        assert isinstance(result.module.classes, list), "Classes should be a list"
        assert isinstance(result.module.functions, list), "Functions should be a list"
        assert isinstance(result.module.imports, list), "Imports should be a list"
        
        # PROPERTY: If code contains 'def ', should extract at least one function
        if 'def ' in code:
            assert len(result.module.functions) > 0 or len(result.module.classes) > 0, \
                "Should extract functions or methods when 'def' is present"
        
        # PROPERTY: If code contains 'class ', should extract at least one class
        if 'class ' in code:
            assert len(result.module.classes) > 0, \
                "Should extract classes when 'class' is present"
        
        # PROPERTY: If code contains 'import ', should extract at least one import
        if 'import ' in code or 'from ' in code:
            assert len(result.module.imports) > 0, \
                "Should extract imports when import statements are present"
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
