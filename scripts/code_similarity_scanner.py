#!/usr/bin/env python3
"""
Code Similarity Scanner
Fast and simple code duplication analyzer for quality gates.
"""

import os
import sys
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class CodeSimilarityScanner:
    """Fast code duplication scanner using file hashing."""
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.file_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs'}
        self.ignore_patterns = {
            '__pycache__', 'node_modules', '.git', '.vscode', 'dist', 'build',
            '.pytest_cache', '.mypy_cache', '.ruff_cache', 'coverage', '.monkeycode'
        }
        
    def should_ignore_path(self, path: Path) -> bool:
        """Check if path should be ignored."""
        for part in path.parts:
            if part in self.ignore_patterns or part.startswith('.'):
                return True
        return False
    
    def normalize_content(self, content: str) -> str:
        """Basic content normalization."""
        # Remove empty lines and normalize whitespace
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def get_file_hash(self, content: str) -> str:
        """Get hash of normalized file content."""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def scan_directory(self, directory: Path) -> Dict:
        """Scan directory for duplicate files using hash comparison."""
        file_hashes = defaultdict(list)
        file_contents = {}
        total_files = 0
        
        # Collect all code files and their hashes
        for file_path in directory.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in self.file_extensions and
                not self.should_ignore_path(file_path)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content.strip()) > 100:  # Only consider substantial files
                            file_hash = self.get_file_hash(content)
                            file_hashes[file_hash].append(str(file_path))
                            file_contents[str(file_path)] = len(content)
                            total_files += 1
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
        
        # Find exact duplicates
        duplications = []
        duplicate_files = 0
        
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicate_files += len(files) - 1  # Count extras as duplicates
                for i in range(len(files)):
                    for j in range(i + 1, len(files)):
                        duplications.append({
                            'file1': files[i],
                            'file2': files[j],
                            'similarity': 1.0,  # Exact match
                            'type': 'exact_duplicate',
                            'hash': file_hash
                        })
        
        # Calculate duplication ratio
        duplication_ratio = duplicate_files / total_files if total_files > 0 else 0.0
        
        return {
            'total_files_scanned': total_files,
            'duplicate_files_found': duplicate_files,
            'duplication_ratio': duplication_ratio,
            'threshold_used': self.threshold,
            'duplications': duplications[:20],  # Limit output
            'summary': {
                'status': 'PASS' if duplication_ratio <= 0.15 else 'FAIL',
                'message': f'Code duplication ratio: {duplication_ratio:.2%}'
            }
        }


def main():
    parser = argparse.ArgumentParser(description='Scan for code duplication')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--threshold', type=float, default=0.8, 
                       help='Similarity threshold (0.0-1.0)')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    scanner = CodeSimilarityScanner(threshold=args.threshold)
    directory = Path(args.directory)
    
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)
    
    print(f"Scanning {directory} for code duplication...")
    results = scanner.scan_directory(directory)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(results, indent=2))
    
    # Print summary
    print(f"\nScan Summary:")
    print(f"Files scanned: {results['total_files_scanned']}")
    print(f"Duplicate files found: {results['duplicate_files_found']}")
    print(f"Duplication ratio: {results['duplication_ratio']:.2%}")
    print(f"Status: {results['summary']['status']}")
    
    # Exit with appropriate code
    sys.exit(0 if results['summary']['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()