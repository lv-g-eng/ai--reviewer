#!/bin/bash
# Phase 2 Cleanup Script
# This script helps with the remaining cleanup tasks

echo "🧹 Project Cleanup - Phase 2"
echo "=============================="
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# 1. Check for test backup files
echo "📋 Checking for test backup files..."
TEST_BACKUPS=$(find . -name "*_backup.py" -o -name "*_simple.py" -o -name "*_standalone.py" | grep -v node_modules | grep -v venv)
if [ ! -z "$TEST_BACKUPS" ]; then
    echo "Found test backup files:"
    echo "$TEST_BACKUPS"
    if confirm "Delete these test backup files?"; then
        echo "$TEST_BACKUPS" | xargs rm -f
        echo "✅ Deleted test backup files"
    fi
else
    echo "✅ No test backup files found"
fi
echo ""

# 2. Check enterprise_rbac_auth requirements
echo "📋 Checking enterprise_rbac_auth/requirements.txt..."
if [ -f "enterprise_rbac_auth/requirements.txt" ]; then
    echo "Found: enterprise_rbac_auth/requirements.txt"
    echo "This may be redundant after RBAC integration."
    if confirm "Delete enterprise_rbac_auth/requirements.txt?"; then
        rm -f enterprise_rbac_auth/requirements.txt
        echo "✅ Deleted enterprise_rbac_auth/requirements.txt"
    fi
else
    echo "✅ File not found or already deleted"
fi
echo ""

# 3. Check for empty test-results.json
echo "📋 Checking for empty test-results.json..."
if [ -f "test-results.json" ]; then
    SIZE=$(stat -f%z "test-results.json" 2>/dev/null || stat -c%s "test-results.json" 2>/dev/null)
    if [ "$SIZE" -lt 10 ]; then
        echo "Found empty test-results.json"
        if confirm "Delete empty test-results.json?"; then
            rm -f test-results.json
            echo "✅ Deleted test-results.json"
        fi
    fi
else
    echo "✅ File not found or already deleted"
fi
echo ""

# 4. Archive consolidation
echo "📋 Checking archive directories..."
echo "Current archive structure:"
echo "  - archive/2026-01-21/ ($(find archive/2026-01-21 -type f 2>/dev/null | wc -l) files)"
echo "  - docs/archive/ ($(find docs/archive -type f 2>/dev/null | wc -l) files)"
echo ""
echo "Recommendation: Consider consolidating archives into a single directory"
echo "Manual action required - review archive contents before moving"
echo ""

# 5. Requirements files check
echo "📋 Checking requirements files..."
echo "Found requirements files:"
ls -lh backend/requirements*.txt backend/requirements*.in 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Recommendation: Review and consolidate requirements files"
echo "Manual action required - check differences between files"
echo ""

# 6. Environment files check
echo "📋 Checking environment configuration files..."
echo "Root directory:"
ls -1 .env* 2>/dev/null | sed 's/^/  /'
echo "Backend:"
ls -1 backend/.env* 2>/dev/null | sed 's/^/  /'
echo "Frontend:"
ls -1 frontend/.env* 2>/dev/null | sed 's/^/  /'
echo ""
echo "Recommendation: Review and remove redundant .env files"
echo "Manual action required - ensure no production secrets are lost"
echo ""

# Summary
echo "=============================="
echo "✅ Phase 2 cleanup check complete"
echo ""
echo "Next steps:"
echo "1. Review CLEANUP_SUMMARY.md for detailed recommendations"
echo "2. Manually review requirements files for consolidation"
echo "3. Manually review environment files"
echo "4. Consider consolidating archive directories"
echo "5. Review and merge quick start guides"
echo ""
