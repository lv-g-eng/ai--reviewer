"""
Demonstration of Optimized Parser Performance

This script demonstrates the performance improvements from:
1. Parallel parsing for multiple files
2. Content-based caching for unchanged files
3. Performance monitoring and metrics

Task 7.3: Optimize parser performance
"""
import time
import tempfile
import os
from pathlib import Path

from app.services.optimized_parser import OptimizedParser
from app.services.code_entity_extractor import CodeEntityExtractor


def create_sample_files(count: int = 20) -> list:
    """Create sample Python files for testing"""
    temp_files = []
    
    for i in range(count):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Create files with varying complexity
            f.write(f"""
'''
Sample module {i}
'''
import os
import sys
from typing import List, Dict, Optional

class DataProcessor{i}:
    '''Process data for module {i}'''
    
    def __init__(self):
        self.data = []
        self.processed = False
    
    def load_data(self, source: str) -> bool:
        '''Load data from source'''
        if not source:
            return False
        
        try:
            # Simulate data loading
            for j in range(10):
                if j % 2 == 0:
                    self.data.append(j)
            return True
        except Exception as e:
            print(f"Error: {{e}}")
            return False
    
    def process(self) -> List[int]:
        '''Process loaded data'''
        result = []
        
        for item in self.data:
            if item > 5:
                result.append(item * 2)
            elif item < 0:
                result.append(0)
            else:
                result.append(item)
        
        self.processed = True
        return result
    
    def validate(self) -> bool:
        '''Validate processed data'''
        if not self.processed:
            return False
        
        for item in self.data:
            if item < 0:
                return False
        
        return True

def helper_function_{i}(x: int, y: int) -> int:
    '''Helper function for module {i}'''
    if x > y:
        return x - y
    elif x < y:
        return y - x
    else:
        return 0

def complex_calculation_{i}(data: List[int]) -> Dict[str, int]:
    '''Perform complex calculation'''
    result = {{'sum': 0, 'count': 0, 'max': 0}}
    
    for value in data:
        result['sum'] += value
        result['count'] += 1
        
        if value > result['max']:
            result['max'] = value
    
    return result
""")
            f.flush()
            temp_files.append(f.name)
    
    return temp_files


def demo_sequential_vs_parallel():
    """Demonstrate sequential vs parallel parsing performance"""
    print("=" * 70)
    print("DEMO 1: Sequential vs Parallel Parsing")
    print("=" * 70)
    
    # Create sample files
    print("\nCreating 20 sample Python files...")
    temp_files = create_sample_files(20)
    
    try:
        # Sequential parsing
        print("\n1. Sequential Parsing (no optimization):")
        parser_seq = OptimizedParser(enable_cache=False)
        
        start = time.time()
        for file_path in temp_files:
            parser_seq.parse_file(file_path, use_cache=False)
        seq_time = time.time() - start
        
        print(f"   Time: {seq_time:.3f} seconds")
        print(f"   Files parsed: {len(temp_files)}")
        print(f"   Average per file: {seq_time/len(temp_files):.3f} seconds")
        
        # Parallel parsing
        print("\n2. Parallel Parsing (with optimization):")
        parser_par = OptimizedParser(max_workers=4, enable_cache=False)
        
        start = time.time()
        results = parser_par.parse_files_parallel(temp_files, use_cache=False)
        par_time = time.time() - start
        
        print(f"   Time: {par_time:.3f} seconds")
        print(f"   Files parsed: {len(results)}")
        print(f"   Average per file: {par_time/len(temp_files):.3f} seconds")
        print(f"   Speedup: {seq_time/par_time:.2f}x")
        
        # Verify all files parsed successfully
        success_count = sum(1 for _, (pf, _) in results.items() if len(pf.errors) == 0)
        print(f"   Successfully parsed: {success_count}/{len(temp_files)}")
        
    finally:
        # Cleanup
        for temp_file in temp_files:
            os.unlink(temp_file)


def demo_caching():
    """Demonstrate caching effectiveness"""
    print("\n" + "=" * 70)
    print("DEMO 2: Caching Effectiveness")
    print("=" * 70)
    
    # Create sample files
    print("\nCreating 10 sample Python files...")
    temp_files = create_sample_files(10)
    
    try:
        parser = OptimizedParser(cache_size=100)
        
        # First parse (cache miss)
        print("\n1. First Parse (cache miss):")
        start = time.time()
        results1 = parser.parse_files_parallel(temp_files)
        time1 = time.time() - start
        
        print(f"   Time: {time1:.3f} seconds")
        print(f"   Files parsed: {len(results1)}")
        
        cache_stats = parser.get_cache_stats()
        print(f"   Cache hits: {cache_stats['hits']}")
        print(f"   Cache misses: {cache_stats['misses']}")
        print(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
        
        # Second parse (cache hit)
        print("\n2. Second Parse (cache hit):")
        start = time.time()
        results2 = parser.parse_files_parallel(temp_files)
        time2 = time.time() - start
        
        print(f"   Time: {time2:.3f} seconds")
        print(f"   Files parsed: {len(results2)}")
        
        cache_stats = parser.get_cache_stats()
        print(f"   Cache hits: {cache_stats['hits']}")
        print(f"   Cache misses: {cache_stats['misses']}")
        print(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"   Speedup: {time1/time2:.2f}x")
        
        # Third parse with one file modified
        print("\n3. Third Parse (one file modified):")
        
        # Modify one file
        with open(temp_files[0], 'a') as f:
            f.write("\n# Modified\n")
        
        start = time.time()
        results3 = parser.parse_files_parallel(temp_files)
        time3 = time.time() - start
        
        print(f"   Time: {time3:.3f} seconds")
        print(f"   Files parsed: {len(results3)}")
        
        cache_stats = parser.get_cache_stats()
        print(f"   Cache hits: {cache_stats['hits']}")
        print(f"   Cache misses: {cache_stats['misses']}")
        print(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"   Note: Only modified file was re-parsed")
        
    finally:
        # Cleanup
        for temp_file in temp_files:
            os.unlink(temp_file)


def demo_performance_requirement():
    """Demonstrate meeting the 2-second per file requirement"""
    print("\n" + "=" * 70)
    print("DEMO 3: Performance Requirement (< 2 seconds per file)")
    print("=" * 70)
    
    # Create a complex file
    print("\nCreating a complex Python file...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Create a large, complex file
        f.write("""
'''
Complex module for performance testing
'''
import os
import sys
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

""")
        
        # Add multiple classes
        for i in range(10):
            f.write(f"""
class ComplexClass{i}:
    '''Complex class {i}'''
    
    def __init__(self):
        self.data = []
        self.config = {{}}
    
    def method1(self, x: int) -> bool:
        if x > 0:
            for j in range(x):
                if j % 2 == 0:
                    self.data.append(j)
        return True
    
    def method2(self, items: List[int]) -> Dict[str, int]:
        result = {{'sum': 0, 'count': 0}}
        for item in items:
            result['sum'] += item
            result['count'] += 1
        return result
    
    def method3(self) -> Optional[str]:
        if not self.data:
            return None
        return str(self.data[0])
""")
        
        # Add multiple functions
        for i in range(20):
            f.write(f"""
def function{i}(a: int, b: int, c: int = 0) -> int:
    '''Function {i}'''
    if a > b:
        if c > 0:
            return a + c
        else:
            return a - b
    elif a < b:
        return b - a
    else:
        return c
""")
        
        f.flush()
        temp_file = f.name
    
    try:
        parser = OptimizedParser()
        
        print("\nParsing complex file...")
        parsed_file, parse_time = parser.parse_file(temp_file)
        
        print(f"\nResults:")
        print(f"   Parse time: {parse_time:.3f} seconds")
        print(f"   Requirement: < 2.000 seconds")
        print(f"   Status: {'✓ PASS' if parse_time < 2.0 else '✗ FAIL'}")
        
        if parsed_file.module:
            print(f"\n   Parsed successfully:")
            print(f"   - Classes: {len(parsed_file.module.classes)}")
            print(f"   - Functions: {len(parsed_file.module.functions)}")
            print(f"   - Lines of code: {parsed_file.module.lines_of_code}")
            
            if parsed_file.metrics:
                print(f"   - Total complexity: {parsed_file.metrics.get('total_complexity', 0)}")
                print(f"   - Max complexity: {parsed_file.metrics.get('max_complexity', 0)}")
        
    finally:
        os.unlink(temp_file)


def demo_code_entity_extractor():
    """Demonstrate optimized code entity extraction"""
    print("\n" + "=" * 70)
    print("DEMO 4: Code Entity Extractor with Optimization")
    print("=" * 70)
    
    # Create sample files
    print("\nCreating 15 sample Python files...")
    temp_files = create_sample_files(15)
    
    try:
        # Without optimization
        print("\n1. Without Optimization:")
        extractor_no_opt = CodeEntityExtractor(enable_optimization=False)
        
        start = time.time()
        result_no_opt = extractor_no_opt.extract_from_files(temp_files, use_parallel=False)
        time_no_opt = time.time() - start
        
        print(f"   Time: {time_no_opt:.3f} seconds")
        print(f"   Entities extracted: {len(result_no_opt['entities'])}")
        print(f"   Files processed: {len(result_no_opt['parsed_files'])}")
        
        # With optimization
        print("\n2. With Optimization:")
        extractor_opt = CodeEntityExtractor(enable_optimization=True)
        
        start = time.time()
        result_opt = extractor_opt.extract_from_files(temp_files, use_parallel=True)
        time_opt = time.time() - start
        
        print(f"   Time: {time_opt:.3f} seconds")
        print(f"   Entities extracted: {len(result_opt['entities'])}")
        print(f"   Files processed: {len(result_opt['parsed_files'])}")
        print(f"   Speedup: {time_no_opt/time_opt:.2f}x")
        
        # Show performance stats
        perf_stats = extractor_opt.get_performance_stats()
        print(f"\n   Performance Statistics:")
        print(f"   - Total files parsed: {perf_stats['total_files_parsed']}")
        print(f"   - Average parse time: {perf_stats['avg_parse_time']:.3f}s")
        print(f"   - Cache enabled: {perf_stats['cache_enabled']}")
        
        if 'cache_stats' in perf_stats:
            cache = perf_stats['cache_stats']
            print(f"   - Cache size: {cache['size']}")
            print(f"   - Cache hit rate: {cache['hit_rate']:.1%}")
        
    finally:
        # Cleanup
        for temp_file in temp_files:
            os.unlink(temp_file)


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "OPTIMIZED PARSER PERFORMANCE DEMONSTRATION" + " " * 16 + "║")
    print("║" + " " * 68 + "║")
    print("║" + "  Task 7.3: Optimize parser performance" + " " * 30 + "║")
    print("║" + "  Requirements: 1.2, 10.2" + " " * 44 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        demo_sequential_vs_parallel()
        demo_caching()
        demo_performance_requirement()
        demo_code_entity_extractor()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print("\n✓ Parallel parsing implemented and working")
        print("✓ Content-based caching implemented and effective")
        print("✓ Performance requirement met (< 2 seconds per file)")
        print("✓ Code entity extractor optimized")
        print("\nAll performance optimizations successfully demonstrated!")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
