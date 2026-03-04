#!/bin/bash

# Frontend Mock Data Audit Script
# This script scans the frontend codebase for mock data usage patterns
# Requirements: 1.1, 1.2, 1.3, 1.4

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output file
REPORT_FILE="mock-data-audit-report.txt"
FRONTEND_DIR="frontend/src"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Frontend Mock Data Audit${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
Frontend Mock Data Audit Report
Generated: $(date)
========================================

EOF

# Counter variables
MATH_RANDOM_COUNT=0
GENERATE_SAMPLE_COUNT=0
HARDCODED_DATA_COUNT=0
TOTAL_ISSUES=0

echo -e "${YELLOW}Scanning for Math.random() usage...${NC}"
echo "" >> "$REPORT_FILE"
echo "1. Math.random() Usage (excluding tests and CSRF)" >> "$REPORT_FILE"
echo "=================================================" >> "$REPORT_FILE"

# Find Math.random() calls excluding test files and CSRF token generation
if grep -rn "Math\.random()" "$FRONTEND_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null > /tmp/math_random_results.txt; then
    while IFS= read -r line; do
        if [ -z "$line" ]; then
            continue
        fi
        
        file=$(echo "$line" | cut -d: -f1)
        line_num=$(echo "$line" | cut -d: -f2)
        content=$(echo "$line" | cut -d: -f3-)
        
        # Skip test files
        if [[ "$file" == *"__tests__"* ]] || [[ "$file" == *".test."* ]] || [[ "$file" == *".spec."* ]]; then
            continue
        fi
        
        # Skip CSRF token generation
        if echo "$content" | grep -qi "csrf\|state.*=.*Math.random"; then
            continue
        fi
        
        # Skip correlation ID generation (legitimate use)
        if echo "$content" | grep -qi "correlationId\|correlation-id"; then
            continue
        fi
        
        echo -e "${RED}  Found:${NC} $file:$line_num"
        echo "  File: $file" >> "$REPORT_FILE"
        echo "  Line: $line_num" >> "$REPORT_FILE"
        echo "  Code: $content" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        ((MATH_RANDOM_COUNT++))
    done < /tmp/math_random_results.txt
fi

if [ $MATH_RANDOM_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✓ No problematic Math.random() usage found${NC}"
    echo "  No problematic Math.random() usage found" >> "$REPORT_FILE"
else
    echo -e "${RED}  ✗ Found $MATH_RANDOM_COUNT problematic Math.random() calls${NC}"
fi
echo "" >> "$REPORT_FILE"

echo ""
echo -e "${YELLOW}Scanning for generateSampleData functions...${NC}"
echo "2. generateSampleData Functions" >> "$REPORT_FILE"
echo "===============================" >> "$REPORT_FILE"

# Find generateSampleData, generateMockData, generateTestData functions
SAMPLE_DATA_PATTERNS=(
    "generateSampleData"
    "generateMockData"
    "generateTestData"
    "generateSample"
    "createMockData"
    "createSampleData"
    "mockData"
    "sampleData"
)

for pattern in "${SAMPLE_DATA_PATTERNS[@]}"; do
    if grep -rn "\b$pattern\b" "$FRONTEND_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null > /tmp/sample_data_results.txt; then
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                continue
            fi
            
            file=$(echo "$line" | cut -d: -f1)
            line_num=$(echo "$line" | cut -d: -f2)
            content=$(echo "$line" | cut -d: -f3-)
            
            # Skip test files
            if [[ "$file" == *"__tests__"* ]] || [[ "$file" == *".test."* ]] || [[ "$file" == *".spec."* ]] || [[ "$file" == *"__mocks__"* ]]; then
                continue
            fi
            
            echo -e "${RED}  Found:${NC} $file:$line_num"
            echo "  Pattern: $pattern" >> "$REPORT_FILE"
            echo "  File: $file" >> "$REPORT_FILE"
            echo "  Line: $line_num" >> "$REPORT_FILE"
            echo "  Code: $content" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            ((GENERATE_SAMPLE_COUNT++))
        done < /tmp/sample_data_results.txt
    fi
done

if [ $GENERATE_SAMPLE_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✓ No generateSampleData functions found${NC}"
    echo "  No generateSampleData functions found" >> "$REPORT_FILE"
else
    echo -e "${RED}  ✗ Found $GENERATE_SAMPLE_COUNT sample data generation functions${NC}"
fi
echo "" >> "$REPORT_FILE"

echo ""
echo -e "${YELLOW}Scanning for hardcoded test data...${NC}"
echo "3. Hardcoded Test Data" >> "$REPORT_FILE"
echo "======================" >> "$REPORT_FILE"

# Find hardcoded test data patterns
HARDCODED_PATTERNS=(
    "const.*=.*\[.*{.*id:.*name:.*}.*\]"
    "const.*=.*{.*test.*:.*mock.*}"
    "const.*=.*{.*sample.*:.*data.*}"
    "const.*=.*{.*dummy.*:.*}"
    "const.*=.*{.*fake.*:.*}"
)

for pattern in "${HARDCODED_PATTERNS[@]}"; do
    if grep -rn -E "$pattern" "$FRONTEND_DIR" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null > /tmp/hardcoded_results.txt; then
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                continue
            fi
            
            file=$(echo "$line" | cut -d: -f1)
            line_num=$(echo "$line" | cut -d: -f2)
            content=$(echo "$line" | cut -d: -f3-)
            
            # Skip test files
            if [[ "$file" == *"__tests__"* ]] || [[ "$file" == *".test."* ]] || [[ "$file" == *".spec."* ]] || [[ "$file" == *"__mocks__"* ]]; then
                continue
            fi
            
            # Skip type definitions
            if [[ "$file" == *"types"* ]] || [[ "$file" == *".d.ts"* ]]; then
                continue
            fi
            
            echo -e "${RED}  Found:${NC} $file:$line_num"
            echo "  File: $file" >> "$REPORT_FILE"
            echo "  Line: $line_num" >> "$REPORT_FILE"
            echo "  Code: $content" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            ((HARDCODED_DATA_COUNT++))
        done < /tmp/hardcoded_results.txt
    fi
done

if [ $HARDCODED_DATA_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✓ No obvious hardcoded test data found${NC}"
    echo "  No obvious hardcoded test data found" >> "$REPORT_FILE"
else
    echo -e "${RED}  ✗ Found $HARDCODED_DATA_COUNT potential hardcoded test data instances${NC}"
fi
echo "" >> "$REPORT_FILE"

# Calculate total issues
TOTAL_ISSUES=$((MATH_RANDOM_COUNT + GENERATE_SAMPLE_COUNT + HARDCODED_DATA_COUNT))

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo "" >> "$REPORT_FILE"
echo "Summary" >> "$REPORT_FILE"
echo "=======" >> "$REPORT_FILE"
echo "Math.random() calls (excluding tests/CSRF): $MATH_RANDOM_COUNT" >> "$REPORT_FILE"
echo "Sample data generation functions: $GENERATE_SAMPLE_COUNT" >> "$REPORT_FILE"
echo "Hardcoded test data instances: $HARDCODED_DATA_COUNT" >> "$REPORT_FILE"
echo "Total issues found: $TOTAL_ISSUES" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo -e "Math.random() calls (excluding tests/CSRF): ${RED}$MATH_RANDOM_COUNT${NC}"
echo -e "Sample data generation functions: ${RED}$GENERATE_SAMPLE_COUNT${NC}"
echo -e "Hardcoded test data instances: ${RED}$HARDCODED_DATA_COUNT${NC}"
echo -e "Total issues found: ${RED}$TOTAL_ISSUES${NC}"
echo ""

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ No mock data issues found! Code is production-ready.${NC}"
    echo "✓ No mock data issues found! Code is production-ready." >> "$REPORT_FILE"
else
    echo -e "${YELLOW}⚠ Found $TOTAL_ISSUES mock data issues that need attention.${NC}"
    echo "⚠ Found $TOTAL_ISSUES mock data issues that need attention." >> "$REPORT_FILE"
fi

echo ""
echo -e "${BLUE}Report saved to: $REPORT_FILE${NC}"
echo ""

# Specific component checks
echo -e "${YELLOW}Checking specific visualization components...${NC}"
echo "" >> "$REPORT_FILE"
echo "4. Specific Component Analysis" >> "$REPORT_FILE"
echo "==============================" >> "$REPORT_FILE"

COMPONENTS=(
    "components/visualizations/ArchitectureGraph.tsx"
    "components/visualizations/DependencyGraphVisualization.tsx"
    "components/visualizations/Neo4jGraphVisualization.tsx"
    "components/visualizations/PerformanceDashboard.tsx"
)

for component in "${COMPONENTS[@]}"; do
    component_path="$FRONTEND_DIR/$component"
    if [ -f "$component_path" ]; then
        echo -e "${BLUE}  Analyzing: $component${NC}"
        echo "" >> "$REPORT_FILE"
        echo "Component: $component" >> "$REPORT_FILE"
        echo "---" >> "$REPORT_FILE"
        
        # Check for sample data generation
        if grep -q "generateSample" "$component_path"; then
            echo -e "${RED}    ✗ Contains sample data generation${NC}"
            echo "  Status: Contains sample data generation" >> "$REPORT_FILE"
        else
            echo -e "${GREEN}    ✓ No sample data generation found${NC}"
            echo "  Status: No sample data generation found" >> "$REPORT_FILE"
        fi
        
        # Check for Math.random
        random_count=$(grep -c "Math\.random()" "$component_path" || true)
        if [ $random_count -gt 0 ]; then
            echo -e "${RED}    ✗ Contains $random_count Math.random() calls${NC}"
            echo "  Math.random() calls: $random_count" >> "$REPORT_FILE"
        else
            echo -e "${GREEN}    ✓ No Math.random() calls${NC}"
            echo "  Math.random() calls: 0" >> "$REPORT_FILE"
        fi
        
        # Check for API calls
        if grep -q "fetch\|axios\|api" "$component_path"; then
            echo -e "${GREEN}    ✓ Contains API calls${NC}"
            echo "  API integration: Yes" >> "$REPORT_FILE"
        else
            echo -e "${YELLOW}    ⚠ No API calls detected${NC}"
            echo "  API integration: No" >> "$REPORT_FILE"
        fi
    else
        echo -e "${YELLOW}  Component not found: $component${NC}"
        echo "Component: $component - NOT FOUND" >> "$REPORT_FILE"
    fi
done

echo ""
echo -e "${GREEN}Audit complete!${NC}"
echo ""
echo "========================================" >> "$REPORT_FILE"
echo "End of Report" >> "$REPORT_FILE"

exit 0
