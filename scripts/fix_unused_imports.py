#!/usr/bin/env python3
"""
Automatically fix unused imports in TypeScript files
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / 'frontend' / 'src'

# Map of files to unused imports to remove
UNUSED_IMPORTS = {
    'components/common/backend-status.tsx': ['CheckCircle2'],
}

def fix_unused_import(file_path: Path, unused_names: list):
    """Remove unused imports from a file"""
    content = file_path.read_text(encoding='utf-8')
    
    for name in unused_names:
        # Pattern to match import with the unused name
        patterns = [
            # Remove from middle of import list: , Name,
            (rf',\s*{name}\s*,', ','),
            # Remove from start: { Name,
            (rf'\{{\s*{name}\s*,', '{'),
            # Remove from end: , Name }
            (rf',\s*{name}\s*\}}', '}'),
            # Remove single import: { Name }
            (rf'\{{\s*{name}\s*\}}', ''),
        ]
        
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                print(f"  ✅ Removed {name}")
                break
    
    # Clean up empty imports
    content = re.sub(r"import\s+\{\s*\}\s+from\s+['\"][^'\"]+['\"];?\s*\n", '', content)
    
    file_path.write_text(content, encoding='utf-8')

def main():
    print("🔧 Fixing unused imports...")
    
    for file_rel_path, unused in UNUSED_IMPORTS.items():
        file_path = FRONTEND_SRC / file_rel_path
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_rel_path}")
            continue
        
        print(f"\n📝 {file_rel_path}")
        fix_unused_import(file_path, unused)
    
    print("\n✅ All unused imports fixed!")

if __name__ == '__main__':
    main()
