# Duplicate Code Detection - Quick Start Guide

## Overview

The duplicate code detection feature identifies similar code blocks across your Python and TypeScript codebase using token-based similarity analysis. This helps you find opportunities for code consolidation and refactoring.

## Quick Start

### 1. Basic Usage

```bash
# Analyze your codebase
cd scripts/optimization
python code_analyzer.py /path/to/your/project --output analysis.json
```

The analyzer will:
- Scan all Python (.py) and TypeScript (.ts, .tsx) files
- Identify duplicate code blocks
- Generate a JSON report with findings

### 2. View Results

The console output shows:
```
Analysis complete:
  Total files: 205
  Total lines: 75187
  Duplicate code groups: 12
  Estimated duplicate lines: 340
```

### 3. Examine Duplicates

Open the JSON report to see detailed information:
```json
{
  "duplicate_blocks": [
    {
      "similarity": 0.92,
      "lines_of_code": 8,
      "locations": [
        {"file_path": "module1.py", "start_line": 15, "end_line": 22},
        {"file_path": "module2.py", "start_line": 30, "end_line": 37}
      ],
      "suggested_refactoring": "Extract duplicate code into a shared module..."
    }
  ]
}
```

## Configuration Options

### Similarity Threshold

Control how similar code must be to be considered duplicate:

```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
report = analyzer.scan_codebase('.')

# More sensitive (finds more duplicates)
duplicates = analyzer.identify_duplicates(
    report.file_nodes,
    similarity_threshold=0.70  # 70% similar
)

# Less sensitive (fewer false positives)
duplicates = analyzer.identify_duplicates(
    report.file_nodes,
    similarity_threshold=0.95  # 95% similar
)
```

**Recommended values:**
- `0.70-0.80`: Aggressive - finds many duplicates, may have false positives
- `0.85`: Default - good balance of precision and recall
- `0.90-0.95`: Conservative - high confidence, may miss some duplicates

### Minimum Lines

Filter out small code blocks:

```python
# Only detect duplicates in larger blocks
duplicates = analyzer.identify_duplicates(
    report.file_nodes,
    min_lines=10  # At least 10 lines
)
```

**Recommended values:**
- `3-5`: Detect even small duplicates
- `5`: Default - good for most cases
- `10+`: Focus on significant duplicates only

## Understanding Results

### Similarity Score

- **0.90-1.00**: Nearly identical code, definitely should be consolidated
- **0.85-0.90**: Very similar, good candidate for refactoring
- **0.70-0.85**: Similar structure, review manually
- **< 0.70**: May be coincidental similarity

### Refactoring Suggestions

The analyzer provides actionable suggestions:

**Same File:**
```
Extract duplicate code into a shared function within validator.py.
The code at lines 15-22 and lines 45-52 are 92.0% similar.
```

**Different Files:**
```
Extract duplicate code into a shared module. Code in validator.py 
(lines 15-22) and checker.py (lines 30-37) are 92.5% similar. 
Consider creating a utility function in a shared module.
```

## Common Patterns Detected

### 1. Similar Validation Logic
```python
# File 1
def validate_user(user):
    if not user.email:
        raise ValueError("Email required")
    if not user.name:
        raise ValueError("Name required")
    return True

# File 2
def validate_product(product):
    if not product.name:
        raise ValueError("Name required")
    if not product.price:
        raise ValueError("Price required")
    return True
```

**Suggestion**: Extract common validation pattern

### 2. Similar Data Processing
```python
# File 1
def process_orders(orders):
    result = []
    for order in orders:
        result.append(transform_order(order))
    return result

# File 2
def process_users(users):
    result = []
    for user in users:
        result.append(transform_user(user))
    return result
```

**Suggestion**: Create generic `process_items()` function

### 3. Similar API Handlers
```typescript
// File 1
async function getUser(id: string) {
    const user = await db.users.findById(id);
    if (!user) throw new NotFoundError();
    return user;
}

// File 2
async function getProduct(id: string) {
    const product = await db.products.findById(id);
    if (!product) throw new NotFoundError();
    return product;
}
```

**Suggestion**: Create generic `getEntity()` function

## Best Practices

### 1. Review Before Refactoring

Not all duplicates should be consolidated:
- **Do consolidate**: Business logic, validation, data processing
- **Consider carefully**: UI components, configuration, test fixtures
- **Don't consolidate**: Coincidental similarity, domain-specific logic

### 2. Iterative Approach

1. Start with high similarity (0.90+)
2. Refactor obvious duplicates
3. Lower threshold gradually
4. Review each group manually

### 3. Test After Refactoring

Always verify that consolidated code works correctly:
```bash
# Run your test suite
pytest
npm test

# Re-run duplicate detection to verify reduction
python code_analyzer.py . --output after_refactoring.json
```

### 4. Track Progress

Compare before and after:
```python
# Before refactoring
# Duplicate code groups: 12
# Estimated duplicate lines: 340

# After refactoring
# Duplicate code groups: 3
# Estimated duplicate lines: 45

# Improvement: 75% reduction in duplicates
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Code Quality Check

on: [pull_request]

jobs:
  duplicate-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run duplicate detection
        run: |
          python scripts/optimization/code_analyzer.py . --output duplicates.json
      - name: Check for new duplicates
        run: |
          # Compare with baseline
          # Fail if duplicates increased
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python scripts/optimization/code_analyzer.py . --output /tmp/duplicates.json

# Parse results and warn if duplicates found
DUPLICATE_COUNT=$(python -c "import json; print(len(json.load(open('/tmp/duplicates.json'))['duplicate_blocks']))")

if [ "$DUPLICATE_COUNT" -gt 0 ]; then
    echo "Warning: $DUPLICATE_COUNT duplicate code groups detected"
    echo "Run 'python scripts/optimization/code_analyzer.py .' for details"
fi
```

## Troubleshooting

### No Duplicates Found

If the analyzer doesn't find expected duplicates:

1. **Lower the threshold**: Try `similarity_threshold=0.70`
2. **Reduce min_lines**: Try `min_lines=3`
3. **Check file types**: Ensure files are .py, .ts, or .tsx
4. **Verify code structure**: Very short functions may be filtered out

### Too Many False Positives

If you see too many unrelated duplicates:

1. **Raise the threshold**: Try `similarity_threshold=0.90`
2. **Increase min_lines**: Try `min_lines=10`
3. **Review manually**: Some patterns are legitimately similar

### Performance Issues

For very large codebases:

1. **Analyze subdirectories separately**:
   ```bash
   python code_analyzer.py backend --output backend_dups.json
   python code_analyzer.py frontend --output frontend_dups.json
   ```

2. **Exclude test files** (if desired):
   ```bash
   python code_analyzer.py . --exclude tests test __tests__
   ```

## Examples

### Example 1: Analyze Backend

```bash
cd scripts/optimization
python code_analyzer.py ../../backend --output backend_analysis.json
```

### Example 2: Custom Threshold

```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
report = analyzer.scan_codebase('../../backend')

# Find high-confidence duplicates only
duplicates = analyzer.identify_duplicates(
    report.file_nodes,
    similarity_threshold=0.92,
    min_lines=8
)

for dup in duplicates:
    print(f"\nDuplicate Group (Similarity: {dup.similarity*100:.1f}%)")
    for loc in dup.locations:
        print(f"  {loc.file_path}:{loc.start_line}-{loc.end_line}")
    print(f"  Suggestion: {dup.suggested_refactoring}")
```

### Example 3: Generate Report

```python
from code_analyzer import CodeAnalyzer
import json

analyzer = CodeAnalyzer()
report = analyzer.scan_codebase('.')

# Custom analysis
duplicates = analyzer.identify_duplicates(report.file_nodes)

# Create summary
summary = {
    'total_files': report.total_files,
    'total_lines': report.total_lines,
    'duplicate_groups': len(duplicates),
    'duplicate_lines': sum(d.lines_of_code * (len(d.locations) - 1) for d in duplicates),
    'top_duplicates': [
        {
            'similarity': d.similarity,
            'lines': d.lines_of_code,
            'locations': len(d.locations)
        }
        for d in sorted(duplicates, key=lambda x: x.similarity, reverse=True)[:5]
    ]
}

print(json.dumps(summary, indent=2))
```

## Support

For issues or questions:
1. Check the main README.md for detailed documentation
2. Review TASK_1.2_SUMMARY.md for implementation details
3. Run the test suite: `pytest test_code_analyzer.py -v`
4. Examine test_duplicate_detection.py for usage examples

## Next Steps

After identifying duplicates:
1. Review the refactoring suggestions
2. Prioritize high-similarity duplicates (>90%)
3. Extract common code into shared modules
4. Update tests to cover refactored code
5. Re-run analysis to verify improvement

Happy refactoring! 🚀
