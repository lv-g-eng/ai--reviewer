#!/usr/bin/env python3
import os
import time
from pathlib import Path

def count_lines(directory, extensions=None):
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.tsx', '.css', '.html', '.md']
    
    total_lines = 0
    total_files = 0
    skip_dirs = {'node_modules', 'venv', '.git', '__pycache__', '.next', 'dist'}
    
    for root, dirs, files in os.walk(directory):
        # 排除跳过的目录
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            path = Path(root) / file
            if path.suffix in extensions:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                        total_files += 1
                except Exception:
                    pass
    return total_lines, total_files

def count_dependencies():
    backend_reqs = 0
    frontend_deps = 0
    
    # Backend
    req_file = Path('backend/requirements.txt')
    if req_file.exists():
        with open(req_file, 'r') as f:
            backend_reqs = len([line for line in f if line.strip() and not line.startswith('#')])
            
    # Frontend
    pkg_file = Path('frontend/package.json')
    if pkg_file.exists():
        import json
        with open(pkg_file, 'r') as f:
            data = json.load(f)
            frontend_deps = len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))
            
    return backend_reqs, frontend_deps

def main():
    root = Path('.')
    print("="*60)
    print("Codebase Benchmark Report")
    print("="*60)
    
    start_time = time.time()
    
    # Volume
    total_lines, total_files = count_lines(root)
    backend_lines, backend_files = count_lines(root / 'backend', ['.py'])
    frontend_lines, frontend_files = count_lines(root / 'frontend', ['.js', '.ts', '.tsx', '.css'])
    
    # Dependencies
    backend_reqs, frontend_deps = count_dependencies()
    
    duration = time.time() - start_time
    
    print(f"Total Files (source): {total_files}")
    print(f"Total Lines (source): {total_lines}")
    print(f"  - Backend (Python): {backend_lines} lines in {backend_files} files")
    print(f"  - Frontend (JS/TS): {frontend_lines} lines in {frontend_files} files")
    print("-" * 30)
    print(f"Backend Dependencies:  {backend_reqs}")
    print(f"Frontend Dependencies: {frontend_deps}")
    print("-" * 30)
    print(f"Benchmark took {duration:.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    main()
