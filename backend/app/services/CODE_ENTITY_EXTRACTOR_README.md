# Code Entity Extractor Service

## Overview

The Code Entity Extractor service provides comprehensive code analysis capabilities by extracting entities (functions, classes, methods) from source files, calculating complexity metrics, and identifying dependencies between entities.

**Implements:** Requirement 1.2 - AST parsing and entity extraction

## Features

- ✅ **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go
- ✅ **Entity Extraction**: Functions, classes, methods, imports
- ✅ **Complexity Calculation**: Cyclomatic complexity for all entities
- ✅ **Dependency Analysis**: Import, call, and inheritance dependencies
- ✅ **Dependency Graphs**: Build and analyze cross-file dependencies
- ✅ **Metrics Aggregation**: File-level and project-level metrics

## Architecture

```
CodeEntityExtractor
├── ParserFactory (multi-language AST parsing)
├── CodeEntity (entity representation)
└── DependencyGraph (dependency relationships)
```

## Usage

### Basic Usage - Single File

```python
from app.services.code_entity_extractor import CodeEntityExtractor

extractor = CodeEntityExtractor()

# Extract entities from a file
result = extractor.extract_from_file("path/to/file.py")

# Access extracted entities
entities = result["entities"]
for entity in entities:
    print(f"{entity.name}: complexity={entity.complexity}")

# Access metrics
metrics = result["metrics"]
print(f"Average complexity: {metrics['avg_complexity']}")
```

### Multi-File Analysis

```python
# Analyze multiple files
result = extractor.extract_from_files([
    "src/module_a.py",
    "src/module_b.py",
    "src/module_c.py"
])

# Access dependency graph
graph = result["dependency_graph"]
print(f"Modules: {len(graph.nodes)}")
print(f"Dependencies: {len(graph.edges)}")

# View dependencies
for edge in graph.edges:
    print(f"{edge.source} --[{edge.type}]--> {edge.target}")
```

### Finding High Complexity Code

```python
# Extract entities
result = extractor.extract_from_file("complex_module.py")
entities = result["entities"]

# Find high complexity entities (threshold: 10)
high_complexity = extractor.find_high_complexity_entities(
    entities, 
    threshold=10
)

for entity in high_complexity:
    print(f"⚠️ {entity.name}: complexity={entity.complexity}")
```

### Filtering Entities

```python
# Get entities by type
functions = extractor.get_entities_by_type(entities, "function")
classes = extractor.get_entities_by_type(entities, "class")
methods = extractor.get_entities_by_type(entities, "method")

# Get dependencies for specific entity
deps = extractor.get_entity_dependencies("MyClass", entities)
print(f"MyClass depends on: {deps}")
```

## Data Models

### CodeEntity

Represents a code entity with its metadata:

```python
class CodeEntity:
    name: str              # Entity name
    entity_type: str       # 'function', 'class', 'method', 'module'
    file_path: str         # Source file path
    complexity: int        # Cyclomatic complexity
    lines_of_code: int     # Lines of code
    dependencies: List[str] # List of dependencies
```

### Result Structure

#### Single File Result

```python
{
    "entities": List[CodeEntity],
    "parsed_file": ParsedFile,
    "metrics": {
        "total_entities": int,
        "total_functions": int,
        "total_classes": int,
        "total_methods": int,
        "avg_complexity": float,
        "max_complexity": int,
        "lines_of_code": int,
        "comment_ratio": float,
        "high_complexity_entities": List[str]
    },
    "errors": List[str]
}
```

#### Multi-File Result

```python
{
    "entities": List[CodeEntity],
    "parsed_files": List[ParsedFile],
    "dependency_graph": DependencyGraph,
    "metrics": {
        "total_files": int,
        "total_entities": int,
        "avg_complexity": float,
        "high_complexity_entities": List[Dict],
        "graph_metrics": {
            "total_nodes": int,
            "total_edges": int,
            "import_edges": int,
            "call_edges": int,
            "inheritance_edges": int
        }
    },
    "errors": Dict[str, List[str]]
}
```

## Complexity Calculation

The service calculates **cyclomatic complexity** using the McCabe method:

```
Complexity = 1 + number of decision points
```

Decision points include:
- `if`, `elif`, `else` statements
- `for`, `while` loops
- `try`, `except` blocks
- Boolean operators (`and`, `or`)
- Ternary operators
- List/dict comprehensions with conditions

### Complexity Guidelines

| Complexity | Risk Level | Action |
|-----------|-----------|--------|
| 1-5 | Low | Simple, easy to test |
| 6-10 | Moderate | Consider refactoring |
| 11-20 | High | Should refactor |
| 21+ | Very High | Must refactor |

## Dependency Types

The service identifies three types of dependencies:

1. **Import Dependencies** (weight: 1.0)
   - Module A imports Module B
   - Strongest dependency type

2. **Inheritance Dependencies** (weight: 0.8)
   - Class A inherits from Class B
   - Strong coupling

3. **Call Dependencies** (weight: 0.5)
   - Function A calls Function B
   - Weaker coupling

## Metrics Explained

### File-Level Metrics

- **total_entities**: Total number of extracted entities
- **avg_complexity**: Average cyclomatic complexity
- **max_complexity**: Highest complexity in file
- **lines_of_code**: Total lines of code (excluding comments/blanks)
- **comment_ratio**: Ratio of comment lines to total lines
- **high_complexity_entities**: Entities with complexity > 10

### Project-Level Metrics

- **total_files**: Number of analyzed files
- **total_entities**: Total entities across all files
- **avg_complexity**: Average complexity across all entities
- **graph_metrics**: Dependency graph statistics

## Error Handling

The service handles errors gracefully:

```python
result = extractor.extract_from_file("broken.py")

if result["errors"]:
    print("Parsing errors:")
    for error in result["errors"]:
        print(f"  - {error}")
else:
    # Process entities
    entities = result["entities"]
```

Common errors:
- **Syntax errors**: Invalid code syntax
- **Unsupported file types**: File extension not supported
- **File not found**: File path doesn't exist

## Supported Languages

| Language | Extension | Parser |
|----------|-----------|--------|
| Python | .py | Built-in `ast` module |
| JavaScript | .js, .jsx | tree-sitter |
| TypeScript | .ts, .tsx | tree-sitter |
| Java | .java | tree-sitter |
| Go | .go | tree-sitter |

## Performance Considerations

- **Single file**: ~2 seconds per file (per requirement 1.2)
- **Multiple files**: Parallel processing recommended for large codebases
- **Memory**: Minimal - only AST in memory, not full source
- **Caching**: Consider caching results for unchanged files

## Integration Examples

### With Neo4j Graph Database

```python
from app.services.code_entity_extractor import CodeEntityExtractor
from app.services.neo4j_service import Neo4jService

extractor = CodeEntityExtractor()
neo4j = Neo4jService()

# Extract entities
result = extractor.extract_from_files(file_paths)

# Store in Neo4j
for entity in result["entities"]:
    neo4j.create_node(
        label="CodeEntity",
        properties=entity.to_dict()
    )

# Store dependencies
for edge in result["dependency_graph"].edges:
    neo4j.create_relationship(
        source=edge.source,
        target=edge.target,
        rel_type=edge.type.upper()
    )
```

### With Analysis Pipeline

```python
from app.services.code_entity_extractor import CodeEntityExtractor

def analyze_pull_request(pr_files):
    extractor = CodeEntityExtractor()
    
    # Extract entities
    result = extractor.extract_from_files(pr_files)
    
    # Check for high complexity
    high_complexity = extractor.find_high_complexity_entities(
        result["entities"],
        threshold=10
    )
    
    if high_complexity:
        return {
            "status": "warning",
            "message": f"Found {len(high_complexity)} high complexity entities",
            "entities": [e.to_dict() for e in high_complexity]
        }
    
    return {"status": "pass"}
```

## Testing

Run the test suite:

```bash
pytest tests/test_code_entity_extractor.py -v
```

Run the demo:

```bash
python examples/code_entity_extraction_demo.py
```

## API Reference

### CodeEntityExtractor

#### Methods

##### `extract_from_file(file_path: str, content: Optional[str] = None) -> Dict`

Extract entities from a single file.

**Parameters:**
- `file_path`: Path to source file
- `content`: Optional file content (if already loaded)

**Returns:** Dictionary with entities, parsed_file, metrics, errors

##### `extract_from_files(file_paths: List[str]) -> Dict`

Extract entities from multiple files and build dependency graph.

**Parameters:**
- `file_paths`: List of file paths

**Returns:** Dictionary with entities, parsed_files, dependency_graph, metrics, errors

##### `find_high_complexity_entities(entities: List[CodeEntity], threshold: int = 10) -> List[CodeEntity]`

Find entities exceeding complexity threshold.

##### `get_entities_by_type(entities: List[CodeEntity], entity_type: str) -> List[CodeEntity]`

Filter entities by type ('function', 'class', 'method').

##### `get_entity_dependencies(entity_name: str, entities: List[CodeEntity]) -> List[str]`

Get dependencies for a specific entity.

## Requirements Mapping

This service implements:

- **Requirement 1.2**: AST parsing and entity extraction
  - ✅ Extract functions, classes, imports from AST
  - ✅ Calculate cyclomatic complexity
  - ✅ Identify dependencies between entities

## Future Enhancements

- [ ] Support for more languages (C++, C#, Ruby, PHP)
- [ ] Parallel file processing for large codebases
- [ ] Incremental analysis (only changed files)
- [ ] Advanced metrics (maintainability index, cognitive complexity)
- [ ] Circular dependency detection
- [ ] Dead code detection

## Related Services

- **ParserFactory**: Multi-language AST parsing
- **Neo4jService**: Graph database storage
- **ArchitectureAnalyzer**: Architectural analysis
- **CircularDependencyDetector**: Cycle detection

## License

Internal use only - Part of AI-Based Reviewer platform
