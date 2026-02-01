#!/usr/bin/env python3
"""
Fix TypeScript unused variable/import errors in frontend
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / 'frontend' / 'src'

# Files and their fixes
FIXES = {
    'app/register/page.tsx': [
        {
            'find': r"import\s+\{[^}]*getPasswordStrengthColor[^}]*\}\s+from\s+'@/lib/validations/auth';",
            'replace': lambda m: m.group(0).replace('getPasswordStrengthColor,', '').replace(', getPasswordStrengthColor', ''),
            'description': 'Remove unused getPasswordStrengthColor import'
        }
    ],
}

def apply_fixes():
    """Apply all fixes"""
    print("🔧 Fixing TypeScript errors...")
    
    for file_path, fixes in FIXES.items():
        full_path = FRONTEND_SRC / file_path
        
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        content = full_path.read_text(encoding='utf-8')
        original_content = content
        
        for fix in fixes:
            pattern = fix['find']
            if callable(fix['replace']):
                content = re.sub(pattern, fix['replace'], content)
            else:
                content = re.sub(pattern, fix['replace'], content)
            
            print(f"✅ {file_path}: {fix['description']}")
        
        if content != original_content:
            full_path.write_text(content, encoding='utf-8')
            print(f"💾 Saved: {file_path}")

if __name__ == '__main__':
    apply_fixes()
    print("\n✅ All fixes applied!")
