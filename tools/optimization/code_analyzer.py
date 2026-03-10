"""
Code Analyzer Module for Comprehensive Project Optimization

This module provides AST-based code analysis for Python and TypeScript files.
It implements the Code Analyzer component from the design specification.

Validates Requirements: 1.1, 1.3, 1.5
Design Component: Code Analyzer

Features:
- AST parsing for Python files using Python's ast module
- Basic parsing for TypeScript files (simplified regex-based approach)
- Codebase scanning and file node building
- Interfaces for duplicate code detection (task 1.2)
- Interfaces for dead code detection (task 1.3)
- Interfaces for complexity analysis (future tasks)
"""

import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any


@dataclass
class CodeLocation:
    """Represents a location in source code"""
    file_path: str
    start_line: int
    end_line: int
    start_column: int = 0
    end_column: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class Import:
    """Represents an import statement"""
    module: str
    names: List[str]
    is_from_import: bool
    location: CodeLocation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'module': self.module,
            'names': self.names,
            'is_from_import': self.is_from_import,
            'location': self.location.to_dict()
        }


@dataclass
class Export:
    """Represents an export (for TypeScript) or public symbol (for Python)"""
    name: str
    type: str  # 'function', 'class', 'variable', 'const', 'type', etc.
    location: CodeLocation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'type': self.type,
            'location': self.location.to_dict()
        }


@dataclass
class FileNode:
    """Represents a parsed source file with its AST and metadata"""
    path: str
    content: str
    ast_tree: Optional[object]  # ast.Module for Python, None for TypeScript
    imports: List[Import] = field(default_factory=list)
    exports: List[Export] = field(default_factory=list)
    size: int = 0
    language: str = ""  # 'python' or 'typescript'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization (excluding AST tree)"""
        return {
            'path': self.path,
            'size': self.size,
            'language': self.language,
            'imports': [imp.to_dict() for imp in self.imports],
            'exports': [exp.to_dict() for exp in self.exports],
            'line_count': len(self.content.splitlines())
        }


@dataclass
class DuplicateBlock:
    """Represents a duplicate code block"""
    locations: List[CodeLocation]
    similarity: float
    lines_of_code: int
    suggested_refactoring: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'locations': [loc.to_dict() for loc in self.locations],
            'similarity': self.similarity,
            'lines_of_code': self.lines_of_code,
            'suggested_refactoring': self.suggested_refactoring
        }


@dataclass
class ComplexityMetric:
    """Represents complexity metrics for a code location"""
    location: CodeLocation
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    suggested_refactoring: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'location': self.location.to_dict(),
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'cognitive_complexity': self.cognitive_complexity,
            'lines_of_code': self.lines_of_code,
            'suggested_refactoring': self.suggested_refactoring
        }


@dataclass
class AnalysisReport:
    """Comprehensive analysis report for the codebase"""
    total_files: int
    total_lines: int
    duplicate_blocks: List[DuplicateBlock]
    dead_code_locations: List[CodeLocation]
    complexity_hotspots: List[ComplexityMetric]
    file_nodes: List[FileNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_files': self.total_files,
            'total_lines': self.total_lines,
            'duplicate_blocks': [block.to_dict() for block in self.duplicate_blocks],
            'dead_code_locations': [loc.to_dict() for loc in self.dead_code_locations],
            'complexity_hotspots': [metric.to_dict() for metric in self.complexity_hotspots],
            'file_nodes': [node.to_dict() for node in self.file_nodes]
        }



class PythonASTParser:
    """Parser for Python source files using Python's ast module"""

    def parse_file(self, file_path: str) -> Optional[FileNode]:
        """
        Parse a Python file and extract AST, imports, and exports
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileNode with parsed information or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content, filename=file_path)
            
            # Extract imports and exports
            imports = self._extract_imports(tree, file_path)
            exports = self._extract_exports(tree, file_path)
            
            return FileNode(
                path=file_path,
                content=content,
                ast_tree=tree,
                imports=imports,
                exports=exports,
                size=len(content),
                language='python'
            )
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}", file=sys.stderr)
            return None

    def _extract_imports(self, tree: ast.Module, file_path: str) -> List[Import]:
        """Extract import statements from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(Import(
                        module=alias.name,
                        names=[alias.asname if alias.asname else alias.name],
                        is_from_import=False,
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            start_column=node.col_offset,
                            end_column=node.end_col_offset or 0
                        )
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [alias.name for alias in node.names]
                imports.append(Import(
                    module=module,
                    names=names,
                    is_from_import=True,
                    location=CodeLocation(
                        file_path=file_path,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        start_column=node.col_offset,
                        end_column=node.end_col_offset or 0
                    )
                ))
        
        return imports

    def _extract_exports(self, tree: ast.Module, file_path: str) -> List[Export]:
        """Extract public symbols (functions, classes) from AST"""
        exports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Only include public functions (not starting with _)
                if not node.name.startswith('_'):
                    exports.append(Export(
                        name=node.name,
                        type='function',
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            start_column=node.col_offset,
                            end_column=node.end_col_offset or 0
                        )
                    ))
            elif isinstance(node, ast.ClassDef):
                # Only include public classes (not starting with _)
                if not node.name.startswith('_'):
                    exports.append(Export(
                        name=node.name,
                        type='class',
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            start_column=node.col_offset,
                            end_column=node.end_col_offset or 0
                        )
                    ))
        
        return exports



class TypeScriptASTParser:
    """Parser for TypeScript source files - simplified regex-based approach"""

    def parse_file(self, file_path: str) -> Optional[FileNode]:
        """
        Parse a TypeScript file and extract basic information
        
        Note: This is a simplified parser that extracts imports/exports using regex.
        For full AST parsing, Node.js and TypeScript compiler would be required.
        
        Args:
            file_path: Path to the TypeScript file
            
        Returns:
            FileNode with parsed information or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = self._extract_imports(content, file_path)
            exports = self._extract_exports(content, file_path)
            
            return FileNode(
                path=file_path,
                content=content,
                ast_tree=None,  # Simplified version doesn't build full AST
                imports=imports,
                exports=exports,
                size=len(content),
                language='typescript'
            )
        except Exception as e:
            print(f"Error parsing TypeScript file {file_path}: {e}", file=sys.stderr)
            return None

    def _extract_imports(self, content: str, file_path: str) -> List[Import]:
        """Extract imports using regex (simplified approach)"""
        imports = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Simple pattern matching for common import statements
            if line.strip().startswith('import '):
                # Extract module name from quotes
                module_match = re.search(r'''from\s+['"]([^'"]+)['"]''', line)
                if module_match:
                    module = module_match.group(1)
                    
                    # Extract imported names
                    names = []
                    # Match: import { X, Y }
                    named_match = re.search(r'import\s+\{([^}]+)\}', line)
                    if named_match:
                        names = [n.strip() for n in named_match.group(1).split(',')]
                    # Match: import X
                    else:
                        default_match = re.search(r'import\s+(\w+)', line)
                        if default_match:
                            names = [default_match.group(1)]
                    
                    imports.append(Import(
                        module=module,
                        names=names,
                        is_from_import=True,
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=line_num,
                            end_line=line_num,
                            start_column=0,
                            end_column=len(line)
                        )
                    ))
        
        return imports

    def _extract_exports(self, content: str, file_path: str) -> List[Export]:
        """Extract exports using regex (simplified approach)"""
        exports = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Match: export function name
            if stripped.startswith('export function '):
                match = re.search(r'export\s+function\s+(\w+)', line)
                if match:
                    exports.append(Export(
                        name=match.group(1),
                        type='function',
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=line_num,
                            end_line=line_num,
                            start_column=0,
                            end_column=len(line)
                        )
                    ))
            
            # Match: export class Name
            elif stripped.startswith('export class '):
                match = re.search(r'export\s+class\s+(\w+)', line)
                if match:
                    exports.append(Export(
                        name=match.group(1),
                        type='class',
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=line_num,
                            end_line=line_num,
                            start_column=0,
                            end_column=len(line)
                        )
                    ))
            
            # Match: export const/let/var name
            elif stripped.startswith('export const ') or stripped.startswith('export let ') or stripped.startswith('export var '):
                match = re.search(r'export\s+(?:const|let|var)\s+(\w+)', line)
                if match:
                    exports.append(Export(
                        name=match.group(1),
                        type='variable',
                        location=CodeLocation(
                            file_path=file_path,
                            start_line=line_num,
                            end_line=line_num,
                            start_column=0,
                            end_column=len(line)
                        )
                    ))
        
        return exports



class CodeAnalyzer:
    """
    Main code analyzer class that implements the Code Analyzer component
    from the design specification.
    
    Provides methods for:
    - Scanning codebase and building file nodes
    - Identifying duplicates (interface for future implementation)
    - Finding dead code (interface for future implementation)
    - Analyzing complexity (interface for future implementation)
    """

    def __init__(self):
        """Initialize the code analyzer with language-specific parsers"""
        self.python_parser = PythonASTParser()
        self.typescript_parser = TypeScriptASTParser()
        self.file_nodes: List[FileNode] = []

    def scan_codebase(self, root_path: str, exclude_patterns: Optional[List[str]] = None) -> AnalysisReport:
        """
        Scan the codebase and build file nodes for all Python and TypeScript files
        
        Args:
            root_path: Root directory to scan
            exclude_patterns: List of patterns to exclude (e.g., 'node_modules', '__pycache__')
            
        Returns:
            AnalysisReport with scanned file nodes and basic metrics
        """
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules',
                '__pycache__',
                '.git',
                '.venv',
                'venv',
                'dist',
                'build',
                '.next',
                'coverage',
                '.pytest_cache',
                '.mypy_cache'
            ]
        
        self.file_nodes = []
        total_lines = 0
        
        root = Path(root_path)
        
        # Find all Python and TypeScript files
        python_files = []
        typescript_files = []
        
        for pattern in ['**/*.py', '**/*.ts', '**/*.tsx']:
            for file_path in root.rglob(pattern):
                # Check if file should be excluded
                if any(exclude in str(file_path) for exclude in exclude_patterns):
                    continue
                
                if pattern == '**/*.py':
                    python_files.append(file_path)
                else:
                    typescript_files.append(file_path)
        
        # Parse Python files
        print(f"Parsing {len(python_files)} Python files...")
        for file_path in python_files:
            file_node = self.python_parser.parse_file(str(file_path))
            if file_node:
                self.file_nodes.append(file_node)
                total_lines += len(file_node.content.splitlines())
        
        # Parse TypeScript files
        print(f"Parsing {len(typescript_files)} TypeScript files...")
        for file_path in typescript_files:
            file_node = self.typescript_parser.parse_file(str(file_path))
            if file_node:
                self.file_nodes.append(file_node)
                total_lines += len(file_node.content.splitlines())
        
        # Identify duplicate code blocks
        print("\nAnalyzing for duplicate code blocks...")
        duplicate_blocks = self.identify_duplicates(self.file_nodes)
        
        # Create analysis report
        report = AnalysisReport(
            total_files=len(self.file_nodes),
            total_lines=total_lines,
            duplicate_blocks=duplicate_blocks,
            dead_code_locations=[],  # To be implemented in task 1.3
            complexity_hotspots=[],  # To be implemented in future tasks
            file_nodes=self.file_nodes
        )
        
        return report

    def identify_duplicates(self, files: List[FileNode], 
                           similarity_threshold: float = 0.85,
                           min_lines: int = 5) -> List[DuplicateBlock]:
        """
        Identify duplicate code blocks using token-based similarity analysis
        
        Uses token-based similarity to detect semantic duplicates even when
        variable names differ. Implements the design specification's approach
        similar to PMD and SonarQube.
        
        Args:
            files: List of FileNode objects to analyze
            similarity_threshold: Minimum similarity score (0.0-1.0) to consider blocks duplicate
            min_lines: Minimum number of lines for a block to be considered
            
        Returns:
            List of DuplicateBlock objects representing duplicate code
        """
        duplicate_blocks = []
        
        # Extract code blocks from all files
        code_blocks = []
        for file_node in files:
            blocks = self._extract_code_blocks(file_node, min_lines)
            code_blocks.extend(blocks)
        
        print(f"Extracted {len(code_blocks)} code blocks for duplicate analysis...")
        
        # Compare all pairs of code blocks
        compared_pairs = set()
        
        for i, block1 in enumerate(code_blocks):
            for j, block2 in enumerate(code_blocks):
                # Skip same block or already compared pairs
                if i >= j:
                    continue
                
                # Skip blocks from the same location
                if (block1['location'].file_path == block2['location'].file_path and
                    block1['location'].start_line == block2['location'].start_line):
                    continue
                
                # Create a unique pair identifier
                pair_id = tuple(sorted([
                    (block1['location'].file_path, block1['location'].start_line),
                    (block2['location'].file_path, block2['location'].start_line)
                ]))
                
                if pair_id in compared_pairs:
                    continue
                compared_pairs.add(pair_id)
                
                # Calculate similarity
                similarity = self._calculate_token_similarity(
                    block1['tokens'], 
                    block2['tokens']
                )
                
                # If similarity exceeds threshold, record as duplicate
                if similarity >= similarity_threshold:
                    # Check if this duplicate is already part of an existing group
                    existing_group = None
                    for dup_block in duplicate_blocks:
                        for loc in dup_block.locations:
                            if ((loc.file_path == block1['location'].file_path and 
                                 loc.start_line == block1['location'].start_line) or
                                (loc.file_path == block2['location'].file_path and 
                                 loc.start_line == block2['location'].start_line)):
                                existing_group = dup_block
                                break
                        if existing_group:
                            break
                    
                    if existing_group:
                        # Add to existing group if not already present
                        locations_set = {(loc.file_path, loc.start_line) 
                                       for loc in existing_group.locations}
                        if (block1['location'].file_path, block1['location'].start_line) not in locations_set:
                            existing_group.locations.append(block1['location'])
                        if (block2['location'].file_path, block2['location'].start_line) not in locations_set:
                            existing_group.locations.append(block2['location'])
                        # Update similarity to average
                        existing_group.similarity = max(existing_group.similarity, similarity)
                    else:
                        # Create new duplicate group
                        refactoring_suggestion = self._generate_refactoring_suggestion(
                            block1, block2, similarity
                        )
                        
                        duplicate_blocks.append(DuplicateBlock(
                            locations=[block1['location'], block2['location']],
                            similarity=similarity,
                            lines_of_code=block1['lines'],
                            suggested_refactoring=refactoring_suggestion
                        ))
        
        print(f"Found {len(duplicate_blocks)} duplicate code groups")
        return duplicate_blocks
    
    def _extract_code_blocks(self, file_node: FileNode, min_lines: int) -> List[Dict]:
        """
        Extract code blocks from a file for duplicate detection
        
        Args:
            file_node: FileNode to extract blocks from
            min_lines: Minimum number of lines for a block
            
        Returns:
            List of dictionaries containing block information
        """
        blocks = []
        
        if file_node.language == 'python' and file_node.ast_tree:
            blocks = self._extract_python_blocks(file_node, min_lines)
        elif file_node.language == 'typescript':
            blocks = self._extract_typescript_blocks(file_node, min_lines)
        
        return blocks
    
    def _extract_python_blocks(self, file_node: FileNode, min_lines: int) -> List[Dict]:
        """Extract code blocks from Python AST"""
        blocks = []
        
        for node in ast.walk(file_node.ast_tree):
            # Extract function and method bodies
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                lines = end_line - start_line + 1
                
                if lines >= min_lines:
                    # Get the source code for this block
                    source_lines = file_node.content.splitlines()
                    block_source = '\n'.join(source_lines[start_line-1:end_line])
                    
                    # Tokenize the block
                    tokens = self._tokenize_python(block_source)
                    
                    blocks.append({
                        'location': CodeLocation(
                            file_path=file_node.path,
                            start_line=start_line,
                            end_line=end_line,
                            start_column=node.col_offset,
                            end_column=node.end_col_offset or 0
                        ),
                        'tokens': tokens,
                        'lines': lines,
                        'source': block_source
                    })
        
        return blocks
    
    def _extract_typescript_blocks(self, file_node: FileNode, min_lines: int) -> List[Dict]:
        """Extract code blocks from TypeScript using regex patterns"""
        blocks = []
        lines = file_node.content.splitlines()
        
        # Simple heuristic: look for function declarations
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match function declarations
            if (line.startswith('function ') or 
                line.startswith('export function ') or
                line.startswith('async function ') or
                'function(' in line or
                '=>' in line):
                
                # Find the matching closing brace
                start_line = i + 1  # 1-indexed
                brace_count = line.count('{') - line.count('}')
                end_line = start_line
                
                j = i + 1
                while j < len(lines) and brace_count > 0:
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    end_line = j + 1
                    j += 1
                
                block_lines = end_line - start_line + 1
                if block_lines >= min_lines:
                    block_source = '\n'.join(lines[i:j])
                    tokens = self._tokenize_typescript(block_source)
                    
                    blocks.append({
                        'location': CodeLocation(
                            file_path=file_node.path,
                            start_line=start_line,
                            end_line=end_line,
                            start_column=0,
                            end_column=len(lines[end_line-1]) if end_line <= len(lines) else 0
                        ),
                        'tokens': tokens,
                        'lines': block_lines,
                        'source': block_source
                    })
                
                i = j
            else:
                i += 1
        
        return blocks
    
    def _tokenize_python(self, source: str) -> List[str]:
        """
        Tokenize Python source code for similarity comparison
        
        Normalizes variable names to detect semantic duplicates
        """
        tokens = []
        
        try:
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                # Add node type as token
                tokens.append(type(node).__name__)
                
                # Add operation types
                if isinstance(node, ast.BinOp):
                    tokens.append(type(node.op).__name__)
                elif isinstance(node, ast.UnaryOp):
                    tokens.append(type(node.op).__name__)
                elif isinstance(node, ast.Compare):
                    for op in node.ops:
                        tokens.append(type(op).__name__)
                elif isinstance(node, ast.BoolOp):
                    tokens.append(type(node.op).__name__)
                
                # Add literal values (but normalize strings)
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, str):
                        tokens.append('STR_LITERAL')
                    elif isinstance(node.value, (int, float)):
                        tokens.append(f'NUM_{node.value}')
                    else:
                        tokens.append(f'CONST_{type(node.value).__name__}')
                
                # Normalize names (variables become VAR, functions become FUNC)
                if isinstance(node, ast.Name):
                    # Keep builtin names, normalize user-defined
                    if node.id in ('True', 'False', 'None'):
                        tokens.append(node.id)
                    else:
                        tokens.append('VAR')
                elif isinstance(node, ast.FunctionDef):
                    tokens.append('FUNC_DEF')
                elif isinstance(node, ast.Call):
                    tokens.append('CALL')
        
        except (SyntaxError, ValueError, TypeError) as e:
            # Fallback to simple tokenization if AST parsing fails
            tokens = self._simple_tokenize(source)
        
        return tokens
    
    def _tokenize_typescript(self, source: str) -> List[str]:
        """
        Tokenize TypeScript source code for similarity comparison
        
        Uses simple pattern-based tokenization
        """
        tokens = []
        
        # Remove comments
        source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
        
        # Tokenize keywords and operators
        keywords = [
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'return', 'class', 'interface', 'type', 'async', 'await', 'try',
            'catch', 'throw', 'new', 'this', 'super', 'extends', 'implements'
        ]
        
        operators = [
            '===', '!==', '==', '!=', '<=', '>=', '<', '>', '&&', '||',
            '+', '-', '*', '/', '%', '=', '=>', '?', ':'
        ]
        
        # Simple word-based tokenization
        words = re.findall(r'\w+|[^\w\s]', source)
        
        for word in words:
            if word in keywords:
                tokens.append(word.upper())
            elif word in operators:
                tokens.append(f'OP_{word}')
            elif word.isdigit():
                tokens.append('NUM')
            elif re.match(r'^[a-zA-Z_]\w*$', word):
                tokens.append('VAR')
            else:
                tokens.append(word)
        
        return tokens
    
    def _simple_tokenize(self, source: str) -> List[str]:
        """Fallback simple tokenization"""
        # Remove comments and strings
        source = re.sub(r'#.*?$', '', source, flags=re.MULTILINE)
        source = re.sub(r'["\'].*?["\']', 'STR', source)
        
        # Split into words
        tokens = re.findall(r'\w+|[^\w\s]', source)
        return tokens
    
    def _calculate_token_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate similarity between two token sequences using Jaccard similarity
        
        Args:
            tokens1: First token sequence
            tokens2: Second token sequence
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not tokens1 or not tokens2:
            return 0.0
        
        # Use Jaccard similarity: intersection / union
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        # Also consider sequence similarity (order matters)
        jaccard_similarity = intersection / union
        
        # Calculate sequence similarity using longest common subsequence
        sequence_similarity = self._lcs_similarity(tokens1, tokens2)
        
        # Weighted average: 60% Jaccard, 40% sequence
        return 0.6 * jaccard_similarity + 0.4 * sequence_similarity
    
    def _lcs_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate similarity based on longest common subsequence
        
        Args:
            tokens1: First token sequence
            tokens2: Second token sequence
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        m, n = len(tokens1), len(tokens2)
        
        if m == 0 or n == 0:
            return 0.0
        
        # Dynamic programming table for LCS
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if tokens1[i-1] == tokens2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        
        # Normalize by average length
        avg_length = (m + n) / 2
        return lcs_length / avg_length if avg_length > 0 else 0.0
    
    def _generate_refactoring_suggestion(self, block1: Dict, block2: Dict, 
                                        similarity: float) -> str:
        """
        Generate a refactoring suggestion for duplicate code blocks
        
        Args:
            block1: First code block
            block2: Second code block
            similarity: Similarity score
            
        Returns:
            Refactoring suggestion string
        """
        loc1 = block1['location']
        loc2 = block2['location']
        
        # Determine if blocks are in same file or different files
        same_file = loc1.file_path == loc2.file_path
        
        if same_file:
            suggestion = (
                f"Extract duplicate code into a shared function within {Path(loc1.file_path).name}. "
                f"The code at lines {loc1.start_line}-{loc1.end_line} and "
                f"lines {loc2.start_line}-{loc2.end_line} are {similarity*100:.1f}% similar."
            )
        else:
            file1 = Path(loc1.file_path).name
            file2 = Path(loc2.file_path).name
            suggestion = (
                f"Extract duplicate code into a shared module. "
                f"Code in {file1} (lines {loc1.start_line}-{loc1.end_line}) and "
                f"{file2} (lines {loc2.start_line}-{loc2.end_line}) are {similarity*100:.1f}% similar. "
                f"Consider creating a utility function in a shared module."
            )
        
        return suggestion

    def find_dead_code(self, entry_points: List[str]) -> List[CodeLocation]:
        """
        Find dead code by analyzing import/export graphs
        
        This is a placeholder interface for task 1.3
        
        Args:
            entry_points: List of entry point files (e.g., main.py, index.ts)
            
        Returns:
            List of CodeLocation objects representing dead code
        """
        # To be implemented in task 1.3
        return []

    def analyze_complexity(self, files: List[FileNode]) -> List[ComplexityMetric]:
        """
        Analyze code complexity and identify refactoring candidates
        
        This is a placeholder interface for future implementation
        
        Args:
            files: List of FileNode objects to analyze
            
        Returns:
            List of ComplexityMetric objects representing complexity hotspots
        """
        # To be implemented in future tasks
        return []

    def generate_report(self, output_path: str, report: AnalysisReport) -> None:
        """
        Generate a comprehensive analysis report in JSON format
        
        Args:
            output_path: Path to write the report
            report: AnalysisReport to serialize
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        print(f"Analysis report written to {output_path}")


def main():
    """Main entry point for the code analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze codebase for optimization opportunities')
    parser.add_argument('root_path', help='Root directory to analyze')
    parser.add_argument('--output', '-o', default='analysis_report.json', help='Output report path')
    parser.add_argument('--exclude', '-e', nargs='*', help='Additional patterns to exclude')
    
    args = parser.parse_args()
    
    analyzer = CodeAnalyzer()
    
    print(f"Scanning codebase at {args.root_path}...")
    report = analyzer.scan_codebase(args.root_path, exclude_patterns=args.exclude)
    
    print(f"\nAnalysis complete:")
    print(f"  Total files: {report.total_files}")
    print(f"  Total lines: {report.total_lines}")
    print(f"  Python files: {sum(1 for f in report.file_nodes if f.language == 'python')}")
    print(f"  TypeScript files: {sum(1 for f in report.file_nodes if f.language == 'typescript')}")
    print(f"  Duplicate code groups: {len(report.duplicate_blocks)}")
    
    if report.duplicate_blocks:
        total_duplicate_lines = sum(block.lines_of_code * (len(block.locations) - 1) 
                                   for block in report.duplicate_blocks)
        print(f"  Estimated duplicate lines: {total_duplicate_lines}")
    
    analyzer.generate_report(args.output, report)


if __name__ == '__main__':
    main()
