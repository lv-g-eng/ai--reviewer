"""
Test script for duplicate code detection functionality

This script tests the token-based similarity analysis implementation
for task 1.2 of the comprehensive project optimization spec.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from code_analyzer import CodeAnalyzer, FileNode


def create_test_files():
    """Create temporary test files with duplicate code"""
    temp_dir = tempfile.mkdtemp()
    
    # Create Python test files with duplicate code
    python_file1 = os.path.join(temp_dir, "test1.py")
    with open(python_file1, 'w') as f:
        f.write("""
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total

def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
""")
    
    python_file2 = os.path.join(temp_dir, "test2.py")
    with open(python_file2, 'w') as f:
        f.write("""
def compute_sum(products):
    sum_value = 0
    for product in products:
        sum_value += product.price
    return sum_value

def transform_values(values):
    output = []
    for value in values:
        output.append(value * 3)
    return output
""")
    
    # Create TypeScript test files with duplicate code
    ts_file1 = os.path.join(temp_dir, "test1.ts")
    with open(ts_file1, 'w') as f:
        f.write("""
function calculateTotal(items: Item[]): number {
    let total = 0;
    for (const item of items) {
        total += item.price;
    }
    return total;
}

function processData(data: number[]): number[] {
    const result = [];
    for (const item of data) {
        result.push(item * 2);
    }
    return result;
}
""")
    
    ts_file2 = os.path.join(temp_dir, "test2.ts")
    with open(ts_file2, 'w') as f:
        f.write("""
function computeSum(products: Product[]): number {
    let sumValue = 0;
    for (const product of products) {
        sumValue += product.price;
    }
    return sumValue;
}

function transformValues(values: number[]): number[] {
    const output = [];
    for (const value of values) {
        output.push(value * 3);
    }
    return output;
}
""")
    
    return temp_dir


def test_duplicate_detection():
    """Test the duplicate code detection functionality"""
    print("=" * 70)
    print("Testing Duplicate Code Detection (Task 1.2)")
    print("=" * 70)
    
    # Create test files
    print("\n1. Creating test files with duplicate code...")
    temp_dir = create_test_files()
    print(f"   Test files created in: {temp_dir}")
    
    # Initialize analyzer
    print("\n2. Initializing CodeAnalyzer...")
    analyzer = CodeAnalyzer()
    
    # Scan the test directory
    print("\n3. Scanning test codebase...")
    report = analyzer.scan_codebase(temp_dir, exclude_patterns=[])
    
    # Display results
    print("\n4. Analysis Results:")
    print(f"   Total files scanned: {report.total_files}")
    print(f"   Total lines of code: {report.total_lines}")
    print(f"   Duplicate code groups found: {len(report.duplicate_blocks)}")
    
    # Display duplicate details
    if report.duplicate_blocks:
        print("\n5. Duplicate Code Details:")
        for i, dup_block in enumerate(report.duplicate_blocks, 1):
            print(f"\n   Duplicate Group {i}:")
            print(f"   - Similarity: {dup_block.similarity * 100:.1f}%")
            print(f"   - Lines of code: {dup_block.lines_of_code}")
            print(f"   - Number of occurrences: {len(dup_block.locations)}")
            print(f"   - Locations:")
            for loc in dup_block.locations:
                file_name = Path(loc.file_path).name
                print(f"     * {file_name}:{loc.start_line}-{loc.end_line}")
            print(f"   - Refactoring suggestion:")
            print(f"     {dup_block.suggested_refactoring}")
    else:
        print("\n   No duplicate code blocks found (threshold may be too high)")
    
    # Test with different thresholds
    print("\n6. Testing with different similarity thresholds:")
    for threshold in [0.5, 0.7, 0.85]:
        duplicates = analyzer.identify_duplicates(report.file_nodes, similarity_threshold=threshold)
        print(f"   Threshold {threshold}: {len(duplicates)} duplicate groups found")
    
    # Cleanup
    print(f"\n7. Cleaning up test files...")
    import shutil
    shutil.rmtree(temp_dir)
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)
    
    return len(report.duplicate_blocks) > 0


def test_edge_cases():
    """Test edge cases for duplicate detection"""
    print("\n" + "=" * 70)
    print("Testing Edge Cases")
    print("=" * 70)
    
    temp_dir = tempfile.mkdtemp()
    
    # Test 1: Identical code with different variable names
    print("\n1. Testing identical logic with different variable names...")
    file1 = os.path.join(temp_dir, "identical1.py")
    with open(file1, 'w') as f:
        f.write("""
def add_numbers(a, b):
    result = a + b
    return result
""")
    
    file2 = os.path.join(temp_dir, "identical2.py")
    with open(file2, 'w') as f:
        f.write("""
def sum_values(x, y):
    total = x + y
    return total
""")
    
    analyzer = CodeAnalyzer()
    report = analyzer.scan_codebase(temp_dir, exclude_patterns=[])
    
    print(f"   Files scanned: {report.total_files}")
    print(f"   Duplicates found: {len(report.duplicate_blocks)}")
    if report.duplicate_blocks:
        print(f"   Similarity: {report.duplicate_blocks[0].similarity * 100:.1f}%")
    
    # Test 2: No duplicates
    print("\n2. Testing files with no duplicates...")
    import shutil
    shutil.rmtree(temp_dir)
    temp_dir = tempfile.mkdtemp()
    
    file1 = os.path.join(temp_dir, "unique1.py")
    with open(file1, 'w') as f:
        f.write("""
def function_one():
    print("This is unique")
    return 1
""")
    
    file2 = os.path.join(temp_dir, "unique2.py")
    with open(file2, 'w') as f:
        f.write("""
def function_two():
    data = [1, 2, 3, 4, 5]
    return sum(data)
""")
    
    analyzer = CodeAnalyzer()
    report = analyzer.scan_codebase(temp_dir, exclude_patterns=[])
    
    print(f"   Files scanned: {report.total_files}")
    print(f"   Duplicates found: {len(report.duplicate_blocks)}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    print("\n" + "=" * 70)
    print("Edge case testing completed!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        # Run main test
        success = test_duplicate_detection()
        
        # Run edge case tests
        test_edge_cases()
        
        if success:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
