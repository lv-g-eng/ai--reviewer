# Multi-Language AST Parsers

This directory contains AST (Abstract Syntax Tree) parsers for multiple programming languages, designed to support the Graph Analysis Service for code dependency extraction and architecture analysis.

## Overview

The parser system provides a unified interface for parsing source code across different programming languages, extracting structural information such as classes, functions, imports, and calculating code metrics.

## Supported Languages

### Python
- **Parser**: `PythonASTParser`
- **Technology**: Python's built-in `ast` module
- **File Extensions**: `.py`
- **Features**:
  - Class and function extraction
  - Import statement parsing
  - Cyclomatic complexity calculation
  - Nesting depth analysis
  - Async function detection
  - Decorator extraction
  - Docstring extraction
  - Line counting (code, comments, blank)

### JavaScript/TypeScript
- **Parser**: `JavaScriptParser`
- **Technology**: Tree-sitter (with esprima fallback)
- **File Extensions**: `.js`, `.jsx`, `.ts`, `.tsx`
- **Features**:
  - Class and function extraction
  - Import/export statement parsing
  - Cyclomatic complexity calculation
  - Nesting depth analysis
  - Async function detection
  - Method extraction from classes
  - Line counting (code, comments, blank)

**Note**: The JavaScript parser uses tree-sitter when available for better performance and accuracy. If tree-sitter language bindings are not installed, it automatically falls back to esprima. TypeScript parsing works best with tree-sitter; esprima may have limitations with TypeScript-specific syntax.

### Java
- **Parser**: `JavaParser`
- **Technology**: Tree-sitter-java
- **File Extensions**: `.java`
- **Features**:
  - Class, interface, and enum extraction
  - Method and constructor extraction
  - Field (property) extraction
  - Import statement parsing
  - Cyclomatic complexity calculation
  - Nesting depth analysis
  - Modifier extraction (public, private, static, etc.)
  - Javadoc comment extraction
  - Line counting (code, comments, blank)

### Go
- **Parser**: `GoParser`
- **Technology**: Tree-sitter-go
- **File Extensions**: `.go`
- **Features**:
  - Function and method extraction (with receivers)
  - Import statement parsing
  - Cyclomatic complexity calculation
  - Nesting depth analysis
  - Package name extraction
  - Line counting (code, comments, blank)
  - **Note**: Go doesn't have classes, so class extraction returns empty list

## Architecture

### Base Parser

All parsers inherit from `BaseASTParser`, which defines the common interface:

```python
class BaseASTParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str, content: Optional[str] = None) -> ParsedFile
    
    @abstractmethod
    def extract_classes(self, ast_tree) -> List[ClassNode]
    
    @abstractmethod
    def extract_functions(self, ast_tree) -> List[FunctionNode]
    
    @abstractmethod
    def extract_imports(self, ast_tree) -> List[ImportNode]
    
    @abstractmethod
    def calculate_complexity(self, node) -> int
```

### Parser Factory

The `ParserFactory` provides a convenient way to get the appropriate parser for a given language:

```python
from app.services.parsers.factory import ParserFactory

# Get parser by language name
parser = ParserFactory.get_parser('python')

# Get parser by filename
parser = ParserFactory.get_parser_by_filename('script.py')

# Check if language is supported
if ParserFactory.is_language_supported('javascript'):
    parser = ParserFactory.get_parser('javascript')
```

## Usage Examples

### Parsing a Python File

```python
from app.services.parsers.python_parser import PythonASTParser

parser = PythonASTParser()
result = parser.parse_file('example.py')

# Access parsed data
print(f"Classes: {len(result.module.classes)}")
print(f"Functions: {len(result.module.functions)}")
print(f"Imports: {len(result.module.imports)}")
print(f"Lines of code: {result.module.lines_of_code}")

# Check for errors
if result.errors:
    print(f"Parse errors: {result.errors}")
```

### Parsing a JavaScript File

```python
from app.services.parsers.javascript_parser import JavaScriptParser

parser = JavaScriptParser(language='javascript')
result = parser.parse_file('example.js')

# Access parsed data
for cls in result.module.classes:
    print(f"Class: {cls.name}")
    for method in cls.methods:
        print(f"  Method: {method.name} (complexity: {method.complexity})")

for func in result.module.functions:
    print(f"Function: {func.name}")
    print(f"  Parameters: {[p.name for p in func.parameters]}")
    print(f"  Complexity: {func.complexity}")
    print(f"  Async: {func.is_async}")
```

### Using the Factory

```python
from app.services.parsers.factory import ParserFactory

# Parse multiple files
files = ['script.py', 'app.js', 'component.tsx']

for file_path in files:
    parser = ParserFactory.get_parser_by_filename(file_path)
    if parser:
        result = parser.parse_file(file_path)
        print(f"{file_path}: {len(result.module.functions)} functions")
    else:
        print(f"{file_path}: Unsupported language")
```

## Data Models

### ParsedFile
The main result object containing:
- `module`: ModuleNode with all extracted information
- `metrics`: Dictionary of calculated metrics
- `errors`: List of parse errors (if any)

### ModuleNode
Represents a source file:
- `name`: Module name
- `file_path`: File path
- `language`: Programming language
- `imports`: List of ImportNode
- `classes`: List of ClassNode
- `functions`: List of FunctionNode
- `lines_of_code`: Number of code lines
- `comment_lines`: Number of comment lines
- `blank_lines`: Number of blank lines
- `comment_ratio`: Ratio of comments to total lines

### ClassNode
Represents a class definition:
- `name`: Class name
- `methods`: List of FunctionNode
- `properties`: List of PropertyNode
- `base_classes`: List of parent class names
- `decorators`: List of decorator names
- `docstring`: Class documentation
- `location`: Source location

### FunctionNode
Represents a function or method:
- `name`: Function name
- `parameters`: List of ParameterNode
- `return_type`: Return type annotation (if available)
- `complexity`: Cyclomatic complexity
- `lines_of_code`: Number of lines
- `nesting_depth`: Maximum nesting depth
- `is_async`: Whether function is async
- `is_method`: Whether function is a method
- `decorators`: List of decorator names
- `docstring`: Function documentation
- `calls`: List of function calls within this function
- `location`: Source location

### ImportNode
Represents an import statement:
- `module_name`: Imported module name
- `imported_names`: List of imported symbols
- `is_from_import`: Whether it's a "from X import Y" statement
- `alias`: Import alias (if any)
- `location`: Source location

## Metrics

The parsers calculate various code metrics:

### Cyclomatic Complexity
Measures the number of linearly independent paths through code:
- Base complexity: 1
- +1 for each: if, while, for, case, catch, and, or
- Higher complexity indicates more complex code

### Nesting Depth
Maximum depth of nested control structures:
- Counts nested if, while, for, try blocks
- Higher depth indicates more complex control flow

### Line Counts
- **Total lines**: All lines in file
- **Code lines**: Lines containing code
- **Comment lines**: Lines containing comments
- **Blank lines**: Empty lines
- **Comment ratio**: comment_lines / total_lines

## Installation

### Required Dependencies

```bash
# Python parser (built-in)
# No additional dependencies required

# JavaScript/TypeScript parser
pip install esprima  # Fallback parser

# Optional: Tree-sitter for better performance
pip install tree-sitter
pip install tree-sitter-javascript
pip install tree-sitter-typescript

# Java parser
pip install tree-sitter-java

# Go parser
pip install tree-sitter-go
```

## Testing

Run the parser tests:

```bash
# Test all parsers
pytest tests/test_python_parser.py tests/test_javascript_parser.py tests/test_parser_factory.py -v

# Test specific parser
pytest tests/test_python_parser.py -v
pytest tests/test_javascript_parser.py -v

# Test factory
pytest tests/test_parser_factory.py -v
```

## Extending the System

To add support for a new language:

1. Create a new parser class inheriting from `BaseASTParser`
2. Implement all abstract methods
3. Add the parser to `ParserFactory._parsers`
4. Create tests for the new parser

Example:

```python
from app.services.parsers.base_parser import BaseASTParser

class GoParser(BaseASTParser):
    def parse_file(self, file_path: str, content: Optional[str] = None) -> ParsedFile:
        # Implementation
        pass
    
    def extract_classes(self, ast_tree) -> List[ClassNode]:
        # Implementation
        pass
    
    # ... implement other methods

# Add to factory
ParserFactory._parsers['go'] = (GoParser, {})
```

## Requirements Validation

This implementation satisfies the following requirements from the spec:

- **Requirement 1.2**: AST_Parser SHALL parse all modified files and generate abstract syntax trees within 2 seconds per file ✓
- **Task 7.1**: Create multi-language AST parser ✓
  - Implement Python parser using ast module ✓
  - Implement JavaScript/TypeScript parser using tree-sitter ✓
  - Implement Java parser using tree-sitter ✓
  - Implement Go parser using tree-sitter ✓

The parsers provide the foundation for:
- Dependency extraction (Requirement 1.3)
- Graph database storage (Requirement 1.3)
- Architecture analysis (Requirement 1.6)
- Circular dependency detection (Requirement 1.6)

## Performance Considerations

- **Python parser**: Very fast, uses built-in ast module
- **JavaScript parser**: 
  - Tree-sitter: Fast, handles large files well
  - Esprima fallback: Slower but more compatible
- **Caching**: Consider caching parsed results for frequently accessed files
- **Batch processing**: Use async processing for multiple files

## Limitations

### JavaScript/TypeScript Parser
- TypeScript-specific syntax (interfaces, type aliases) may not parse correctly with esprima fallback
- JSX/TSX support depends on parser availability
- Some advanced TypeScript features require tree-sitter

### General
- Very large files (>10MB) may be slow to parse
- Malformed code may produce incomplete results
- Some language-specific features may not be captured

## Future Enhancements

Potential improvements:
- Add support for more languages (C++, Rust, Ruby, PHP, C#)
- Implement incremental parsing for large files
- Add semantic analysis (type inference, scope analysis)
- Improve error recovery for malformed code
- Add support for language-specific metrics
- Implement parallel parsing for multiple files
- Add caching layer for frequently parsed files
