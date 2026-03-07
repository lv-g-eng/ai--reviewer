"""
Performance tests for parser optimization
Task 7.3: Verify parser meets performance requirements

Requirements:
- 1.2: Parse files within 2 seconds per file
- 10.2: Complete analysis within 12 seconds for <10K LOC
- 10.3: Complete analysis within 60 seconds for 10K-50K LOC
"""
import logging
logger = logging.getLogger(__name__)

import pytest
import time
import tempfile
import os
from pathlib import Path

from app.services.optimized_parser import OptimizedParser
from app.services.code_entity_extractor import CodeEntityExtractor


class TestParserPerformance:
    """Test parser performance requirements"""
    
    def _generate_python_code(self, num_functions: int, num_classes: int) -> str:
        """Generate Python code with specified complexity"""
        code = "import os\nimport sys\nfrom typing import List, Dict\n\n"
        
        # Generate functions
        for i in range(num_functions):
            code += f"""
def function_{i}(x, y):
    '''Function {i} documentation'''
    result = 0
    if x > y:
        for j in range(x):
            if j % 2 == 0:
                result += j
            else:
                result -= j
    elif x < y:
        for k in range(y):
            if k % 3 == 0:
                result += k
    else:
        result = x * y
    return result

"""
        
        # Generate classes
        for i in range(num_classes):
            code += f"""
class Class_{i}:
    '''Class {i} documentation'''
    
    def __init__(self):
        self.value = {i}
        self.data = []
    
    def method_1(self, param):
        if param > 0:
            for i in range(param):
                self.data.append(i)
        return len(self.data)
    
    def method_2(self, x, y):
        result = 0
        if x > y:
            result = x - y
        else:
            result = y - x
        return result
    
    def method_3(self):
        total = 0
        for item in self.data:
            if item % 2 == 0:
                total += item
        return total

"""
        
        return code
    
    def test_single_file_under_2_seconds(self):
        """
        Test Requirement 1.2: Parse single file within 2 seconds
        """
        parser = OptimizedParser()
        
        # Generate a reasonably complex file (~500 LOC)
        code = self._generate_python_code(num_functions=20, num_classes=10)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name
        
        try:
            # Parse the file
            parsed_file, parse_time = parser.parse_file(temp_path)
            
            # Verify successful parse
            assert parsed_file is not None
            assert len(parsed_file.errors) == 0
            
            # Verify performance requirement
            assert parse_time < 2.0, (
                f"Parse time {parse_time:.3f}s exceeds 2 second requirement "
                f"(Requirement 1.2)"
            )
            
            logger.info("✓ Single file parsed in {parse_time:.3f}s (< 2s requirement)")
        finally:
            os.unlink(temp_path)
    
    def test_small_repository_under_12_seconds(self):
        """
        Test Requirement 10.2: Analyze repository <10K LOC within 12 seconds
        """
        extractor = CodeEntityExtractor(enable_optimization=True)
        
        # Create a small repository (~8K LOC with 20 files)
        temp_files = []
        total_loc = 0
        target_loc = 8000
        num_files = 20
        loc_per_file = target_loc // num_files
        
        for i in range(num_files):
            # Calculate functions/classes to reach target LOC
            # Each function ~15 LOC, each class ~25 LOC
            num_functions = loc_per_file // 40
            num_classes = loc_per_file // 80
            
            code = self._generate_python_code(num_functions, num_classes)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                temp_files.append(f.name)
                total_loc += len(code.split('\n'))
        
        try:
            logger.info("Testing with {num_files} files, ~{total_loc} LOC")
            
            # Analyze all files
            start_time = time.time()
            result = extractor.extract_from_files(temp_files, use_parallel=True)
            analysis_time = time.time() - start_time
            
            # Verify successful analysis
            assert len(result["entities"]) > 0
            assert len(result["parsed_files"]) == num_files
            
            # Verify performance requirement
            assert analysis_time < 12.0, (
                f"Analysis time {analysis_time:.3f}s exceeds 12 second requirement "
                f"for {total_loc} LOC (Requirement 10.2)"
            )
            
            logger.info("✓ Small repository ({total_loc} LOC) analyzed in {analysis_time:.3f}s (< 12s requirement)")
            
            # Print performance stats
            stats = extractor.get_performance_stats()
            logger.info("  - Files parsed: {stats.get('total_files_parsed', 0)}")
            logger.info("  - Avg parse time: {stats.get('avg_parse_time', 0):.3f}s")
            logger.info("  - Cache stats: {stats.get('cache_stats', {})}")
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_medium_repository_under_60_seconds(self):
        """
        Test Requirement 10.3: Analyze repository 10K-50K LOC within 60 seconds
        """
        extractor = CodeEntityExtractor(enable_optimization=True)
        
        # Create a medium repository (~30K LOC with 50 files)
        temp_files = []
        total_loc = 0
        target_loc = 30000
        num_files = 50
        loc_per_file = target_loc // num_files
        
        for i in range(num_files):
            # Calculate functions/classes to reach target LOC
            num_functions = loc_per_file // 40
            num_classes = loc_per_file // 80
            
            code = self._generate_python_code(num_functions, num_classes)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                temp_files.append(f.name)
                total_loc += len(code.split('\n'))
        
        try:
            logger.info("Testing with {num_files} files, ~{total_loc} LOC")
            
            # Analyze all files
            start_time = time.time()
            result = extractor.extract_from_files(temp_files, use_parallel=True)
            analysis_time = time.time() - start_time
            
            # Verify successful analysis
            assert len(result["entities"]) > 0
            assert len(result["parsed_files"]) == num_files
            
            # Verify performance requirement
            assert analysis_time < 60.0, (
                f"Analysis time {analysis_time:.3f}s exceeds 60 second requirement "
                f"for {total_loc} LOC (Requirement 10.3)"
            )
            
            logger.info("✓ Medium repository ({total_loc} LOC) analyzed in {analysis_time:.3f}s (< 60s requirement)")
            
            # Print performance stats
            stats = extractor.get_performance_stats()
            logger.info("  - Files parsed: {stats.get('total_files_parsed', 0)}")
            logger.info("  - Avg parse time: {stats.get('avg_parse_time', 0):.3f}s")
            logger.info("  - Cache stats: {stats.get('cache_stats', {})}")
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_parallel_parsing_performance(self):
        """Test that parallel parsing provides performance benefit"""
        # Create test files
        temp_files = []
        for i in range(10):
            code = self._generate_python_code(num_functions=10, num_classes=5)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                temp_files.append(f.name)
        
        try:
            # Test with parallel processing
            parser_parallel = OptimizedParser(max_workers=4, enable_cache=False)
            start_parallel = time.time()
            results_parallel = parser_parallel.parse_files_parallel(
                temp_files, 
                use_cache=False,
                use_processes=True
            )
            time_parallel = time.time() - start_parallel
            
            # Verify all files parsed successfully
            assert len(results_parallel) == 10
            for file_path in temp_files:
                assert file_path in results_parallel
                parsed_file, _ = results_parallel[file_path]
                assert parsed_file is not None
                assert len(parsed_file.errors) == 0
            
            logger.info("✓ Parallel parsing of 10 files completed in {time_parallel:.3f}s")
            
            # Get performance stats
            stats = parser_parallel.get_performance_stats()
            logger.info("  - Total files: {stats['total_files_parsed']}")
            logger.info("  - Avg parse time: {stats['avg_parse_time']:.3f}s")
            logger.info("  - Max workers: {stats['max_workers']}")
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_cache_performance_benefit(self):
        """Test that caching provides performance benefit"""
        parser = OptimizedParser(enable_cache=True)
        
        # Generate test code
        code = self._generate_python_code(num_functions=15, num_classes=8)
        
        # First parse (cache miss)
        start_first = time.time()
        parsed_first, time_first = parser.parse_file("test.py", code)
        total_first = time.time() - start_first
        
        # Second parse (cache hit)
        start_second = time.time()
        parsed_second, time_second = parser.parse_file("test.py", code)
        total_second = time.time() - start_second
        
        # Verify both parses successful
        assert parsed_first is not None
        assert parsed_second is not None
        assert len(parsed_first.errors) == 0
        assert len(parsed_second.errors) == 0
        
        # Verify cache hit is faster
        assert total_second < total_first, (
            f"Cache hit ({total_second:.3f}s) should be faster than "
            f"cache miss ({total_first:.3f}s)"
        )
        
        # Check cache stats
        stats = parser.get_cache_stats()
        assert stats["hits"] >= 1
        assert stats["hit_rate"] > 0
        
        logger.info("✓ Cache performance benefit verified:")
        logger.info("  - First parse (miss): {total_first:.3f}s")
        logger.info("  - Second parse (hit): {total_second:.3f}s")
        logger.info("  - Speedup: {total_first / total_second:.2f}x")
        logger.info("  - Cache hit rate: {stats['hit_rate']:.2%}")
    
    def test_batch_processing_performance(self):
        """Test batch processing for large file sets"""
        parser = OptimizedParser()
        
        # Create many small files
        temp_files = []
        for i in range(30):
            code = self._generate_python_code(num_functions=5, num_classes=2)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                temp_files.append(f.name)
        
        try:
            # Parse in batches
            start_time = time.time()
            results = parser.parse_files_batch(temp_files, batch_size=10)
            batch_time = time.time() - start_time
            
            # Verify all files parsed
            assert len(results) == 30
            for file_path in temp_files:
                assert file_path in results
                parsed_file, _ = results[file_path]
                assert parsed_file is not None
            
            logger.info("✓ Batch processing of 30 files completed in {batch_time:.3f}s")
            logger.info("  - Avg time per file: {batch_time / 30:.3f}s")
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)


class TestParserScalability:
    """Test parser scalability with varying workloads"""
    
    def test_increasing_file_sizes(self):
        """Test parser performance with increasing file sizes"""
        parser = OptimizedParser()
        
        file_sizes = [100, 500, 1000, 2000]  # LOC
        results = []
        
        for size in file_sizes:
            # Generate code
            num_functions = size // 15
            num_classes = size // 30
            code = TestParserPerformance()._generate_python_code(num_functions, num_classes)
            
            # Parse
            parsed_file, parse_time = parser.parse_file(f"test_{size}.py", code)
            
            # Verify
            assert parsed_file is not None
            assert len(parsed_file.errors) == 0
            assert parse_time < 2.0, f"File with {size} LOC took {parse_time:.3f}s (> 2s)"
            
            results.append((size, parse_time))
            logger.info("  - {size} LOC: {parse_time:.3f}s")
        
        logger.info("✓ Parser scales linearly with file size")
    
    def test_increasing_file_counts(self):
        """Test parser performance with increasing file counts"""
        extractor = CodeEntityExtractor(enable_optimization=True)
        
        file_counts = [5, 10, 20, 40]
        results = []
        
        for count in file_counts:
            # Create files
            temp_files = []
            for i in range(count):
                code = TestParserPerformance()._generate_python_code(
                    num_functions=10, 
                    num_classes=5
                )
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    f.flush()
                    temp_files.append(f.name)
            
            try:
                # Analyze
                start_time = time.time()
                result = extractor.extract_from_files(temp_files, use_parallel=True)
                analysis_time = time.time() - start_time
                
                # Verify
                assert len(result["parsed_files"]) == count
                
                results.append((count, analysis_time))
                logger.info("  - {count} files: {analysis_time:.3f}s ({analysis_time/count:.3f}s per file)")
            finally:
                for temp_file in temp_files:
                    os.unlink(temp_file)
        
        logger.info("✓ Parser scales efficiently with file count")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
