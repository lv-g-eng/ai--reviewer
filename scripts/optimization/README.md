# Code Analyzer Module

## Overview

AST-based code analysis for Python and TypeScript files. Identifies duplicate code, analyzes dependencies, and provides optimization recommendations.

## Features

- **AST Parsing**: Python (ast module) and TypeScript (regex-based)
- **Duplicate Detection**: Token-based similarity analysis
- **Dependency Analysis**: Scans package.json and requirements.txt
- **Codebase Scanning**: Recursive directory analysis
- **Optimization Reports**: JSON output with actionable recommendations

## Quick Start

```bash
# Analyze backend
python code_analyzer.py backend --output backend_analysis.json

# Analyze frontend
python code_analyzer.py frontend/src --output frontend_analysis.json

# Analyze entire project
python code_analyzer.py . --output full_analysis.json
```

## Usage

### Command Line

```bash
# Basic analysis
python code_analyzer.py <path> [--output report.json]

# With exclusions
python code_analyzer.py . --exclude node_modules __pycache__ .git

# Examples
python code_analyzer.py backend --output backend_analysis.json
python code_analyzer.py frontend/src --output frontend_analysis.json
```

### Python API

```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
report = analyzer.scan_codebase('backend')

print(f"Files: {report.total_files}")
print(f"Lines: {report.total_lines}")
print(f"Duplicates: {len(report.duplicate_blocks)}")

analyzer.generate_report('analysis.json', report)
```

## Output

The analyzer generates JSON reports with:
- Total files and lines analyzed
- Duplicate code blocks with similarity scores
- File-level metrics (imports, exports, size)
- Refactoring suggestions

Example output:
```json
{
  "total_files": 205,
  "total_lines": 75187,
  "duplicate_blocks": [
    {
      "similarity": 0.92,
      "lines_of_code": 8,
      "locations": [
        {"file_path": "module1.py", "start_line": 15, "end_line": 22},
        {"file_path": "module2.py", "start_line": 30, "end_line": 37}
      ],
      "suggested_refactoring": "Extract duplicate code into shared module"
    }
  ]
}
```

## Configuration

### Duplicate Detection

- `similarity_threshold`: 0.0-1.0 (default: 0.85)
  - 0.70-0.80: Aggressive (more duplicates, may have false positives)
  - 0.85: Balanced (recommended)
  - 0.90-0.95: Conservative (high confidence)

- `min_lines`: Minimum lines per block (default: 5)

### Excluded Patterns

Default exclusions:
- `node_modules`, `__pycache__`, `.git`
- `.venv`, `venv`, `dist`, `build`
- `.next`, `coverage`, `.pytest_cache`

## Testing

```bash
# Run unit tests
pytest test_code_analyzer.py -v

# Run integration tests
python test_duplicate_detection.py
```

## Performance

- Backend: ~205 files, ~75K lines in < 5 seconds
- Frontend: ~118 files, ~21K lines in < 3 seconds
- Memory efficient: One file at a time processing

## Documentation

- `README.md` - This file
- `TASK_1.1_SUMMARY.md` - Implementation details (Task 1.1)
- `TASK_1.2_SUMMARY.md` - Duplicate detection details (Task 1.2)
- `DUPLICATE_DETECTION_GUIDE.md` - User guide for duplicate detection
