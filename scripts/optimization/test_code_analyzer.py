"""
Unit tests for code_analyzer.py

Tests the duplicate code detection functionality implemented in task 1.2
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from code_analyzer import (
    CodeAnalyzer, FileNode, DuplicateBlock, CodeLocation,
    PythonASTParser, TypeScriptASTParser
)


class TestDuplicateDetection(unittest.TestCase):
    """Test cases for duplicate code detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = CodeAnalyzer()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_identify_duplicates_with_similar_python_functions(self):
        """Test that similar Python functions are identified as duplicates"""
        # Create two files with similar functions
        file1 = os.path.join(self.temp_dir, "module1.py")
        with open(file1, 'w') as f:
            f.write("""
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
""")
        
        file2 = os.path.join(self.temp_dir, "module2.py")
        with open(file2, 'w') as f:
            f.write("""
def compute_total(values):
    result = 0
    for val in values:
        result += val
    return result
""")
        
        # Scan and analyze
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Verify duplicates were found
        self.assertGreater(len(report.duplicate_blocks), 0, 
                          "Should find duplicate code blocks")
        
        # Verify similarity is high
        for dup_block in report.duplicate_blocks:
            self.assertGreaterEqual(dup_block.similarity, 0.85,
                                   "Similarity should be >= 0.85")
            self.assertEqual(len(dup_block.locations), 2,
                           "Should have exactly 2 locations")
    
    def test_identify_duplicates_with_different_code(self):
        """Test that different code is not identified as duplicate"""
        file1 = os.path.join(self.temp_dir, "unique1.py")
        with open(file1, 'w') as f:
            f.write("""
def function_a():
    print("Hello World")
    return 42
""")
        
        file2 = os.path.join(self.temp_dir, "unique2.py")
        with open(file2, 'w') as f:
            f.write("""
def function_b():
    data = [1, 2, 3, 4, 5]
    return sum(data) * 2
""")
        
        # Scan and analyze
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Verify no duplicates found
        self.assertEqual(len(report.duplicate_blocks), 0,
                        "Should not find duplicates in different code")
    
    def test_configurable_similarity_threshold(self):
        """Test that similarity threshold is configurable"""
        file1 = os.path.join(self.temp_dir, "test1.py")
        with open(file1, 'w') as f:
            f.write("""
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
""")
        
        file2 = os.path.join(self.temp_dir, "test2.py")
        with open(file2, 'w') as f:
            f.write("""
def transform_data(data):
    output = []
    for d in data:
        output.append(d * 3)
    return output
""")
        
        # Parse files
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Test with different thresholds
        duplicates_low = self.analyzer.identify_duplicates(
            report.file_nodes, similarity_threshold=0.5
        )
        duplicates_high = self.analyzer.identify_duplicates(
            report.file_nodes, similarity_threshold=0.95
        )
        
        # Lower threshold should find more or equal duplicates
        self.assertGreaterEqual(len(duplicates_low), len(duplicates_high),
                               "Lower threshold should find more duplicates")
    
    def test_min_lines_parameter(self):
        """Test that min_lines parameter filters small blocks"""
        file1 = os.path.join(self.temp_dir, "small1.py")
        with open(file1, 'w') as f:
            f.write("""
def tiny():
    return 1

def larger_function():
    result = 0
    for i in range(10):
        result += i
    return result
""")
        
        file2 = os.path.join(self.temp_dir, "small2.py")
        with open(file2, 'w') as f:
            f.write("""
def small():
    return 1

def bigger_function():
    total = 0
    for j in range(10):
        total += j
    return total
""")
        
        # Parse files
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Test with different min_lines
        duplicates_min3 = self.analyzer.identify_duplicates(
            report.file_nodes, min_lines=3
        )
        duplicates_min10 = self.analyzer.identify_duplicates(
            report.file_nodes, min_lines=10
        )
        
        # Higher min_lines should find fewer or equal duplicates
        self.assertGreaterEqual(len(duplicates_min3), len(duplicates_min10),
                               "Lower min_lines should find more duplicates")
    
    def test_duplicate_block_structure(self):
        """Test that DuplicateBlock has correct structure"""
        file1 = os.path.join(self.temp_dir, "dup1.py")
        with open(file1, 'w') as f:
            f.write("""
def add_values(a, b):
    result = a + b
    return result
""")
        
        file2 = os.path.join(self.temp_dir, "dup2.py")
        with open(file2, 'w') as f:
            f.write("""
def sum_numbers(x, y):
    total = x + y
    return total
""")
        
        # Scan and analyze
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        if report.duplicate_blocks:
            dup_block = report.duplicate_blocks[0]
            
            # Verify structure
            self.assertIsInstance(dup_block, DuplicateBlock)
            self.assertIsInstance(dup_block.locations, list)
            self.assertIsInstance(dup_block.similarity, float)
            self.assertIsInstance(dup_block.lines_of_code, int)
            self.assertIsInstance(dup_block.suggested_refactoring, str)
            
            # Verify values
            self.assertGreater(dup_block.similarity, 0.0)
            self.assertLessEqual(dup_block.similarity, 1.0)
            self.assertGreater(dup_block.lines_of_code, 0)
            self.assertGreater(len(dup_block.suggested_refactoring), 0)
            
            # Verify locations
            for loc in dup_block.locations:
                self.assertIsInstance(loc, CodeLocation)
                self.assertGreater(loc.end_line, loc.start_line)
    
    def test_refactoring_suggestions(self):
        """Test that refactoring suggestions are generated"""
        file1 = os.path.join(self.temp_dir, "ref1.py")
        with open(file1, 'w') as f:
            f.write("""
def multiply_list(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
""")
        
        file2 = os.path.join(self.temp_dir, "ref2.py")
        with open(file2, 'w') as f:
            f.write("""
def double_values(values):
    output = []
    for value in values:
        output.append(value * 2)
    return output
""")
        
        # Scan and analyze
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        if report.duplicate_blocks:
            for dup_block in report.duplicate_blocks:
                suggestion = dup_block.suggested_refactoring
                
                # Verify suggestion contains key information
                self.assertIn("Extract", suggestion)
                self.assertIn("similar", suggestion)
                # Should mention file names or line numbers
                self.assertTrue(
                    any(word in suggestion for word in ["lines", "file", "module"]),
                    "Suggestion should mention location details"
                )


class TestTokenization(unittest.TestCase):
    """Test cases for tokenization methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CodeAnalyzer()
    
    def test_python_tokenization(self):
        """Test Python code tokenization"""
        source = """
def add(a, b):
    return a + b
"""
        tokens = self.analyzer._tokenize_python(source)
        
        # Verify tokens were generated
        self.assertGreater(len(tokens), 0, "Should generate tokens")
        
        # Verify variable names are normalized
        self.assertIn('VAR', tokens, "Should normalize variable names")
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization"""
        source = """
function add(a: number, b: number): number {
    return a + b;
}
"""
        tokens = self.analyzer._tokenize_typescript(source)
        
        # Verify tokens were generated
        self.assertGreater(len(tokens), 0, "Should generate tokens")
        
        # Verify keywords are captured
        self.assertIn('FUNCTION', tokens, "Should capture function keyword")
    
    def test_token_similarity_calculation(self):
        """Test token similarity calculation"""
        tokens1 = ['FUNC', 'VAR', 'VAR', 'Add', 'VAR', 'VAR', 'Return']
        tokens2 = ['FUNC', 'VAR', 'VAR', 'Add', 'VAR', 'VAR', 'Return']
        
        similarity = self.analyzer._calculate_token_similarity(tokens1, tokens2)
        
        # Identical tokens should have high similarity
        self.assertGreater(similarity, 0.9, "Identical tokens should be very similar")
    
    def test_token_similarity_with_different_tokens(self):
        """Test token similarity with different tokens"""
        tokens1 = ['FUNC', 'VAR', 'Add', 'Return']
        tokens2 = ['CLASS', 'VAR', 'Multiply', 'Print']
        
        similarity = self.analyzer._calculate_token_similarity(tokens1, tokens2)
        
        # Different tokens should have low similarity
        self.assertLess(similarity, 0.5, "Different tokens should have low similarity")


class TestCodeBlockExtraction(unittest.TestCase):
    """Test cases for code block extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CodeAnalyzer()
        self.python_parser = PythonASTParser()
    
    def test_extract_python_blocks(self):
        """Test extraction of Python code blocks"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write("""
def function_one():
    x = 1
    y = 2
    return x + y

def function_two():
    a = 10
    b = 20
    return a * b
""")
        temp_file.close()
        
        try:
            # Parse file
            file_node = self.python_parser.parse_file(temp_file.name)
            self.assertIsNotNone(file_node)
            
            # Extract blocks
            blocks = self.analyzer._extract_code_blocks(file_node, min_lines=3)
            
            # Verify blocks were extracted
            self.assertGreater(len(blocks), 0, "Should extract code blocks")
            
            # Verify block structure
            for block in blocks:
                self.assertIn('location', block)
                self.assertIn('tokens', block)
                self.assertIn('lines', block)
                self.assertIn('source', block)
        finally:
            os.unlink(temp_file.name)


class TestAnalysisReport(unittest.TestCase):
    """Test cases for analysis report generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = CodeAnalyzer()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_report_generation(self):
        """Test that analysis report is generated correctly"""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
def test_function():
    return 42
""")
        
        # Scan and generate report
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Verify report structure
        self.assertGreater(report.total_files, 0)
        self.assertGreater(report.total_lines, 0)
        self.assertIsInstance(report.duplicate_blocks, list)
        self.assertIsInstance(report.dead_code_locations, list)
        self.assertIsInstance(report.complexity_hotspots, list)
        self.assertIsInstance(report.file_nodes, list)
    
    def test_report_serialization(self):
        """Test that report can be serialized to JSON"""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
def test_function():
    return 42
""")
        
        # Scan and generate report
        report = self.analyzer.scan_codebase(self.temp_dir, exclude_patterns=[])
        
        # Serialize to dict
        report_dict = report.to_dict()
        
        # Verify dict structure
        self.assertIn('total_files', report_dict)
        self.assertIn('total_lines', report_dict)
        self.assertIn('duplicate_blocks', report_dict)
        self.assertIn('file_nodes', report_dict)
        
        # Verify can be converted to JSON
        import json
        json_str = json.dumps(report_dict)
        self.assertIsInstance(json_str, str)


if __name__ == '__main__':
    unittest.main()
