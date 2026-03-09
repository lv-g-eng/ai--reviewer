#!/bin/bash

echo "Finding TypeScript files with 'any' type usage..."
echo "=============================================="

# Find all TypeScript files and count 'any' usage
echo "Files with 'any' type usage:"
grep -rn ": any" frontend/src --include="*.ts" --include="*.tsx" | head -50

echo ""
echo "Summary:"
grep -r ": any" frontend/src --include="*.ts" --include="*.tsx" | wc -l | xargs echo "Total occurrences of ': any':"

echo ""
echo "Top 10 files with most 'any' usage:"
grep -r ": any" frontend/src --include="*.ts" --include="*.tsx" | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
