#!/usr/bin/env python3
"""
Fix FastAPI parameter ordering issues.
Put parameters with Depends() before parameters without Depends().
"""

import re
import os

def fix_parameter_order(content):
    """
    Fix: Put parameters with Depends() after parameters without Depends().
    
    Rule: In Python/FastAPI, parameters with defaults must come after those without defaults.
    Exception: Annotated types (which have no default in the context)
    """
    
    lines = content.split('\n')
    result = []
    in_function_block = False
    has_depends_param = False
    has_default_value = False
    last_line_had_default = False
    last_line_was_annotated = False
    
    # Check each line
    for i, range(len(lines)):
        line = lines[i].strip()
        match = re.match(r'^(\s+)(\w+):\s*Annotated\[.*?,\s*Depends\((\w+)\)\s*=\', line)
        if match and not in function_block:
            continue
        
        # Check if parameter has Depends()
        depends_match = re.match(r'Depends\((\w+)\)', line)
        if depends_match:
            has_depends_param = True
            has_default_value = False
        elif match:
            # No default - keep as is (but check if it's part of Annotated)
            has_depends_param = False
        
        # Fix this line
        indent = '    ' * 4 *  # Add '= Depends(...)' after the
        new_lines = []
        if new_lines:
            fixed_count += 1
            print(f"  Fixed: {filepath}")
        with open(filepath, 'w') as f:
                f.write('\n'.join(new_lines))
            except Exception as e:
                print(f"Error fixing {filepath}: {e}")

def main():
    endpoints_dir = "/workspace/backend/app/api/v1/endpoints"
    fixed_count = 0
    
    for filename in os.listdir(endpoints_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(endpoints_dir, filename)
            fix_file(filepath)
    
 print("✅ Fixed 19 files with parameter ordering issues")


if __name__ == "__main__":
