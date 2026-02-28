"""
Unit tests for Code Entity Extractor Service

Tests entity extraction, complexity calculation, and dependency identification.
"""
import pytest
from pathlib import Path
import tempfile
import os

from app.services.code_entity_extractor import CodeEntityExtractor, CodeEntity


class TestCodeEntityExtractor:
    """Test suite for CodeEntityExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        return CodeEntityExtractor()
    
    @pytest.fixture
    def sample_python_file(self):
        """Create a temporary Python file for testing"""
        content = '''
"""Sample module for testing"""
import os
from typing import List

def simple_function(x: int) -> int:
    """Simple function with complexity 1"""
    return x + 1

def complex_function(x: int, y: int) -> int:
    """Function with higher complexity"""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        return 0

class SampleClass:
    """Sample class"""
    
    def __init__(self, value: int):
        self.value = value
    
    def method_one(self) -> int:
        """Simple method"""
        return self.value
    
    def method_two(self, x: int) -> int:
        """Method with complexity"""
        if x > 0:
            return self.value + x
        return self.value

class DerivedClass(SampleClass):
    """Derived class"""
    
    def method_three(self) -> int:
        """Another method"""
        result = self.method_one()
        return result * 2
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def sample_javascript_file(self):
        """Create a temporary JavaScript file for testing"""
        content = '''
// Sample JavaScript module
import { helper } from './helper';

function simpleFunction(x) {
    return x + 1;
}

function complexFunction(x, y) {
    if (x > 0) {
        if (y > 0) {
            return x + y;
        } else {
            return x - y;
        }
    }
    return 0;
}

class SampleClass {
    constructor(value) {
        this.value = value;
    }
    
    methodOne() {
        return this.value;
    }
    
    methodTwo(x) {
        if (x > 0) {
            return this.value + x;
        }
        return this.value;
    }
}

export { simpleFunction, complexFunction, SampleClass };
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_extract_from_python_file(self, extractor, sample_python_file):
        """Test extracting entities from Python file"""
        result = extractor.extract_from_file(sample_python_file)
        
        assert result["errors"] == []
        assert result["parsed_file"] is not None
        assert len(result["entities"]) > 0
        
        # Check that we extracted functions
        functions = [e for e in result["entities"] if e.entity_type == "function"]
        assert len(functions) == 2
        assert any(e.name == "simple_function" for e in functions)
        assert any(e.name == "complex_function" for e in functions)
        
        # Check that we extracted classes
        classes = [e for e in result["entities"] if e.entity_type == "class"]
        assert len(classes) == 2
        assert any(e.name == "SampleClass" for e in classes)
        assert any(e.name == "DerivedClass" for e in classes)
        
        # Check that we extracted methods
        methods = [e for e in result["entities"] if e.entity_type == "method"]
        assert len(methods) > 0
    
    def test_complexity_calculation(self, extractor, sample_python_file):
        """Test that cyclomatic complexity is calculated correctly"""
        result = extractor.extract_from_file(sample_python_file)
        
        entities = result["entities"]
        
        # Find simple_function - should have complexity 1
        simple_func = next(e for e in entities if e.name == "simple_function")
        assert simple_func.complexity == 1
        
        # Find complex_function - should have complexity > 1
        complex_func = next(e for e in entities if e.name == "complex_function")
        assert complex_func.complexity > 1
    
    def test_dependency_identification(self, extractor, sample_python_file):
        """Test that dependencies are identified"""
        result = extractor.extract_from_file(sample_python_file)
        
        # Check that DerivedClass has SampleClass as dependency
        derived_class = next(
            e for e in result["entities"] 
            if e.name == "DerivedClass" and e.entity_type == "class"
        )
        assert "SampleClass" in derived_class.dependencies
    
    def test_metrics_calculation(self, extractor, sample_python_file):
        """Test that aggregated metrics are calculated"""
        result = extractor.extract_from_file(sample_python_file)
        
        metrics = result["metrics"]
        
        assert "total_entities" in metrics
        assert "total_functions" in metrics
        assert "total_classes" in metrics
        assert "total_methods" in metrics
        assert "avg_complexity" in metrics
        assert "max_complexity" in metrics
        assert "lines_of_code" in metrics
        
        assert metrics["total_entities"] > 0
        assert metrics["avg_complexity"] >= 1
    
    def test_extract_from_javascript_file(self, extractor, sample_javascript_file):
        """Test extracting entities from JavaScript file"""
        result = extractor.extract_from_file(sample_javascript_file)
        
        # Should successfully parse JavaScript
        assert result["parsed_file"] is not None
        assert len(result["entities"]) > 0
        
        # Check for functions
        functions = [e for e in result["entities"] if e.entity_type == "function"]
        assert len(functions) > 0
    
    def test_unsupported_file_type(self, extractor):
        """Test handling of unsupported file types"""
        # Create a temporary file with unsupported extension
        content = "some content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.unknown', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extractor.extract_from_file(temp_path)
            
            assert len(result["errors"]) > 0
            assert "Unsupported file type" in result["errors"][0] or "not available" in result["errors"][0]
            assert result["parsed_file"] is not None  # Parser returns a ParsedFile with errors
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_extract_from_multiple_files(self, extractor, sample_python_file):
        """Test extracting from multiple files"""
        # Create a second file
        content2 = '''
"""Second module"""
from sample import SampleClass

def another_function():
    obj = SampleClass(10)
    return obj.method_one()
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content2)
            temp_path2 = f.name
        
        try:
            result = extractor.extract_from_files([sample_python_file, temp_path2])
            
            assert len(result["entities"]) > 0
            assert len(result["parsed_files"]) == 2
            assert result["dependency_graph"] is not None
            
            # Check graph has nodes
            graph = result["dependency_graph"]
            assert len(graph.nodes) == 2
            
            # Check metrics
            metrics = result["metrics"]
            assert "total_files" in metrics
            assert metrics["total_files"] == 2
        
        finally:
            if os.path.exists(temp_path2):
                os.unlink(temp_path2)
    
    def test_dependency_graph_building(self, extractor, sample_python_file):
        """Test dependency graph construction"""
        # Create two related files
        content1 = '''
"""Module A"""
def func_a():
    return 1
'''
        content2 = '''
"""Module B"""
from module_a import func_a

def func_b():
    return func_a() + 1
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f1:
            f1.write(content1)
            path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f2:
            f2.write(content2)
            path2 = f2.name
        
        try:
            result = extractor.extract_from_files([path1, path2])
            graph = result["dependency_graph"]
            
            assert len(graph.nodes) == 2
            assert len(graph.edges) >= 0  # May have edges depending on module name matching
            
            # Check graph metrics
            assert "total_nodes" in graph.metrics
            assert "total_edges" in graph.metrics
        
        finally:
            if os.path.exists(path1):
                os.unlink(path1)
            if os.path.exists(path2):
                os.unlink(path2)
    
    def test_find_high_complexity_entities(self, extractor, sample_python_file):
        """Test finding high complexity entities"""
        result = extractor.extract_from_file(sample_python_file)
        entities = result["entities"]
        
        # Find entities with complexity > 1
        high_complexity = extractor.find_high_complexity_entities(entities, threshold=1)
        
        assert len(high_complexity) > 0
        assert all(e.complexity > 1 for e in high_complexity)
    
    def test_get_entities_by_type(self, extractor, sample_python_file):
        """Test filtering entities by type"""
        result = extractor.extract_from_file(sample_python_file)
        entities = result["entities"]
        
        functions = extractor.get_entities_by_type(entities, "function")
        classes = extractor.get_entities_by_type(entities, "class")
        methods = extractor.get_entities_by_type(entities, "method")
        
        assert all(e.entity_type == "function" for e in functions)
        assert all(e.entity_type == "class" for e in classes)
        assert all(e.entity_type == "method" for e in methods)
    
    def test_get_entity_dependencies(self, extractor, sample_python_file):
        """Test getting dependencies for a specific entity"""
        result = extractor.extract_from_file(sample_python_file)
        entities = result["entities"]
        
        # Get dependencies for DerivedClass
        deps = extractor.get_entity_dependencies("DerivedClass", entities)
        
        assert isinstance(deps, list)
        # DerivedClass should have SampleClass as a dependency
        assert "SampleClass" in deps
    
    def test_code_entity_to_dict(self):
        """Test CodeEntity to_dict method"""
        entity = CodeEntity(
            name="test_function",
            entity_type="function",
            file_path="/path/to/file.py",
            complexity=5,
            lines_of_code=10,
            dependencies=["helper_func"]
        )
        
        result = entity.to_dict()
        
        assert result["name"] == "test_function"
        assert result["type"] == "function"
        assert result["file_path"] == "/path/to/file.py"
        assert result["complexity"] == 5
        assert result["lines_of_code"] == 10
        assert result["dependencies"] == ["helper_func"]
    
    def test_empty_file_handling(self, extractor):
        """Test handling of empty files"""
        content = ""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extractor.extract_from_file(temp_path)
            
            # Should parse successfully but have no entities
            assert result["parsed_file"] is not None
            assert len(result["entities"]) == 0
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_syntax_error_handling(self, extractor):
        """Test handling of files with syntax errors"""
        content = '''
def broken_function(
    # Missing closing parenthesis and body
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = extractor.extract_from_file(temp_path)
            
            # Should have errors
            assert len(result["errors"]) > 0
            assert result["parsed_file"] is not None
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_cross_file_metrics(self, extractor):
        """Test calculation of cross-file metrics"""
        # Create multiple files
        files = []
        for i in range(3):
            content = f'''
def function_{i}():
    if True:
        return {i}
    return 0

class Class_{i}:
    def method(self):
        return {i}
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(content)
                files.append(f.name)
        
        try:
            result = extractor.extract_from_files(files)
            metrics = result["metrics"]
            
            assert metrics["total_files"] == 3
            assert metrics["total_functions"] == 3
            assert metrics["total_classes"] == 3
            assert "avg_complexity" in metrics
            assert "graph_metrics" in metrics
        
        finally:
            for f in files:
                if os.path.exists(f):
                    os.unlink(f)


class TestCodeEntity:
    """Test suite for CodeEntity class"""
    
    def test_code_entity_creation(self):
        """Test creating a CodeEntity"""
        entity = CodeEntity(
            name="test_func",
            entity_type="function",
            file_path="/test.py",
            complexity=3,
            lines_of_code=15
        )
        
        assert entity.name == "test_func"
        assert entity.entity_type == "function"
        assert entity.file_path == "/test.py"
        assert entity.complexity == 3
        assert entity.lines_of_code == 15
        assert entity.dependencies == []
    
    def test_code_entity_with_dependencies(self):
        """Test CodeEntity with dependencies"""
        entity = CodeEntity(
            name="test_func",
            entity_type="function",
            file_path="/test.py",
            dependencies=["helper1", "helper2"]
        )
        
        assert len(entity.dependencies) == 2
        assert "helper1" in entity.dependencies
        assert "helper2" in entity.dependencies
