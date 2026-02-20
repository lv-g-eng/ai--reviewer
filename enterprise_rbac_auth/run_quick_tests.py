"""
Quick test runner with reduced property test examples for faster validation.
"""
import sys
import pytest

# Set Hypothesis to use fewer examples for quick testing
import os
os.environ['HYPOTHESIS_MAX_EXAMPLES'] = '10'

if __name__ == '__main__':
    # Run pytest with custom settings
    import sys
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'tests/'
    
    exit_code = pytest.main([
        test_path,
        '-v',
        '--tb=short',
        '-x',  # Stop on first failure
    ])
    sys.exit(exit_code)
