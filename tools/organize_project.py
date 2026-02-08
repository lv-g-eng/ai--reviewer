#!/usr/bin/env python3
"""
Project Organization Script
Categorizes and archives redundant documentation and script files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Define project root
PROJECT_ROOT = Path(__file__).parent.parent

# Files to archive (redundant or outdated)
ARCHIVE_FILES = {
    'documentation': [
        'BACKEND_STARTUP_FIX.md',
        'DOCUMENTATION_CLEANUP_SUMMARY.md',
        'FINAL_SETUP_SUMMARY.md',
        'LLM_INTEGRATION_COMPLETE.md',
        'NEXTAUTH_SETUP_GUIDE.md',
        'PROJECT_COMPLETION_STATUS.md',
        'QUICK_START_GUIDE.md',  # Duplicate of QUICK_START.md
        'README.md.bak',
        'START_BACKEND_GUIDE.md',
        'START_EVERYTHING.md',
        'UPDATE_SUMMARY.md',
        'backend/TASK_1.2_IMPLEMENTATION_SUMMARY.md',
        'backend/TASK_1.3_IMPLEMENTATION_SUMMARY.md',
        'backend/TASK_2.1_IMPLEMENTATION_SUMMARY.md',
        'backend/TASK_2.2_IMPLEMENTATION_SUMMARY.md',
        'backend/TASK_2.3_IMPLEMENTATION_SUMMARY.md',
        'backend/TASK_6.1_IMPLEMENTATION_SUMMARY.md',
    ],
    'scripts': [
        'start-backend-local.bat',
        'start-backend.bat',
        'START_BACKEND_LOCAL.bat',
        'START_BACKEND_NOW.bat',
        'START_BACKEND_SIMPLE.bat',
    ],
    'config': [
        'bandit-report.json',
        'bandit-results.json',
        'frontend/package-updated.json',
        'frontend/junit.xml',
        'backend/test-results.json',
    ],
}

# Files to keep (essential)
ESSENTIAL_FILES = [
    'README.md',
    'MASTER_GUIDE.md',
    'PROJECT_GUIDE.md',
    'QUICK_START.md',
    'TROUBLESHOOTING.md',
    'QUICK_REFERENCE.md',
    'START_ALL_SERVICES.bat',
    'STOP_ALL_SERVICES.bat',
    'START_NEO4J.bat',
    'START_REDIS.bat',
    'CREATE_DATABASE.bat',
]


def create_archive_structure():
    """Create archive directory structure"""
    archive_root = PROJECT_ROOT / 'archive' / datetime.now().strftime('%Y-%m-%d')
    
    for category in ARCHIVE_FILES.keys():
        (archive_root / category).mkdir(parents=True, exist_ok=True)
    
    return archive_root


def archive_file(file_path: Path, archive_root: Path, category: str):
    """Archive a single file"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    # Preserve directory structure in archive
    relative_path = file_path.relative_to(PROJECT_ROOT)
    archive_path = archive_root / category / relative_path
    
    # Create parent directories
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move file
    shutil.move(str(file_path), str(archive_path))
    print(f"✅ Archived: {relative_path} → archive/{category}/")
    return True


def create_archive_index(archive_root: Path):
    """Create an index file for archived content"""
    index_path = archive_root / 'INDEX.md'
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"# Archived Files - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("This directory contains files that were archived during project cleanup.\n\n")
        
        for category in ARCHIVE_FILES.keys():
            f.write(f"## {category.title()}\n\n")
            category_path = archive_root / category
            
            if category_path.exists():
                files = sorted(category_path.rglob('*'))
                files = [f for f in files if f.is_file()]
                
                for file in files:
                    rel_path = file.relative_to(category_path)
                    f.write(f"- {rel_path}\n")
            
            f.write("\n")
        
        f.write("## Reason for Archival\n\n")
        f.write("These files were archived because:\n")
        f.write("- Redundant with other documentation\n")
        f.write("- Outdated or superseded by newer files\n")
        f.write("- Temporary implementation summaries\n")
        f.write("- Duplicate startup scripts\n\n")
        f.write("## Restoration\n\n")
        f.write("If you need any of these files, they can be restored from this archive.\n")
    
    print(f"\n📋 Created archive index: {index_path}")


def create_project_index():
    """Create a comprehensive project file index"""
    index_path = PROJECT_ROOT / 'PROJECT_INDEX.md'
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Project File Index\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📚 Documentation\n\n")
        f.write("### Root Level\n")
        for file in ESSENTIAL_FILES:
            if Path(PROJECT_ROOT / file).exists():
                f.write(f"- [{file}]({file})\n")
        
        f.write("\n### docs/ Directory\n")
        docs_dir = PROJECT_ROOT / 'docs'
        if docs_dir.exists():
            for file in sorted(docs_dir.glob('*.md')):
                f.write(f"- [docs/{file.name}](docs/{file.name})\n")
        
        f.write("\n## 🔧 Scripts\n\n")
        f.write("### Startup Scripts (Root)\n")
        for file in ['START_ALL_SERVICES.bat', 'STOP_ALL_SERVICES.bat', 
                     'START_NEO4J.bat', 'START_REDIS.bat', 'CREATE_DATABASE.bat']:
            if Path(PROJECT_ROOT / file).exists():
                f.write(f"- {file}\n")
        
        f.write("\n### Utility Scripts (scripts/)\n")
        scripts_dir = PROJECT_ROOT / 'scripts'
        if scripts_dir.exists():
            for file in sorted(scripts_dir.glob('*')):
                if file.suffix in ['.py', '.sh', '.bat'] and file.is_file():
                    f.write(f"- scripts/{file.name}\n")
        
        f.write("\n## 🏗️ Services\n\n")
        services_dir = PROJECT_ROOT / 'services'
        if services_dir.exists():
            for service in sorted(services_dir.iterdir()):
                if service.is_dir():
                    f.write(f"### {service.name}\n")
                    readme = service / 'README.md'
                    if readme.exists():
                        f.write(f"- [README](services/{service.name}/README.md)\n")
                    docs = service / 'docs'
                    if docs.exists() and docs.is_dir():
                        f.write(f"- [Documentation](services/{service.name}/docs/)\n")
                    f.write("\n")
        
        f.write("\n## 📦 Configuration\n\n")
        config_files = [
            'docker-compose.yml',
            'docker-compose.prod.yml',
            '.env.example',
            'package.json',
            'tsconfig.json',
        ]
        for file in config_files:
            if Path(PROJECT_ROOT / file).exists():
                f.write(f"- {file}\n")
        
        f.write("\n## 🗂️ Archived Files\n\n")
        f.write("Archived files are stored in `archive/` directory with date stamps.\n")
        f.write("See `archive/*/INDEX.md` for details on archived content.\n")
    
    print(f"📋 Created project index: {index_path}")


def main():
    """Main execution"""
    print("🗂️  Project Organization Script")
    print("=" * 50)
    
    # Create archive structure
    print("\n📁 Creating archive structure...")
    archive_root = create_archive_structure()
    print(f"✅ Archive location: {archive_root}")
    
    # Archive files
    print("\n📦 Archiving redundant files...")
    archived_count = 0
    
    for category, files in ARCHIVE_FILES.items():
        print(f"\n{category.title()}:")
        for file_path in files:
            full_path = PROJECT_ROOT / file_path
            if archive_file(full_path, archive_root, category):
                archived_count += 1
    
    # Create archive index
    print("\n📋 Creating archive index...")
    create_archive_index(archive_root)
    
    # Create project index
    print("\n📋 Creating project file index...")
    create_project_index()
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Organization complete!")
    print(f"📦 Archived {archived_count} files")
    print(f"📁 Archive location: {archive_root}")
    print(f"📋 Project index: PROJECT_INDEX.md")
    print("\n💡 Tip: Review MASTER_GUIDE.md for navigation")


if __name__ == '__main__':
    main()
