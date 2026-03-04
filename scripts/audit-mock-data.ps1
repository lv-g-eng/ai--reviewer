# Frontend Mock Data Audit Script (PowerShell)
# This script scans the frontend codebase for mock data usage patterns
# Requirements: 1.1, 1.2, 1.3, 1.4

$ErrorActionPreference = "Continue"

# Output file
$ReportFile = "mock-data-audit-report.txt"
$FrontendDir = "frontend/src"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Frontend Mock Data Audit" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Initialize report
@"
Frontend Mock Data Audit Report
Generated: $(Get-Date)
========================================

"@ | Out-File -FilePath $ReportFile -Encoding UTF8

# Counter variables
$MathRandomCount = 0
$GenerateSampleCount = 0
$HardcodedDataCount = 0

Write-Host "Scanning for Math.random() usage..." -ForegroundColor Yellow
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"1. Math.random() Usage (excluding tests and CSRF)" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"=================================================" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

# Find Math.random() calls
$MathRandomFiles = Get-ChildItem -Path $FrontendDir -Recurse -Include *.ts,*.tsx,*.js,*.jsx -File | 
    Where-Object { 
        $_.FullName -notmatch '__tests__' -and 
        $_.FullName -notmatch '\.test\.' -and 
        $_.FullName -notmatch '\.spec\.' 
    }

foreach ($file in $MathRandomFiles) {
    $content = Get-Content $file.FullName -Raw
    $lines = Get-Content $file.FullName
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match 'Math\.random\(\)') {
            # Skip CSRF token generation
            if ($line -match 'csrf|state.*=.*Math\.random') {
                continue
            }
            
            # Skip correlation ID generation (legitimate use)
            if ($line -match 'correlationId|correlation-id') {
                continue
            }
            
            $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")
            $lineNum = $i + 1
            
            Write-Host "  Found: ${relativePath}:${lineNum}" -ForegroundColor Red
            "  File: $relativePath" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
            "  Line: $lineNum" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
            "  Code: $line" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
            "" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
            
            $MathRandomCount++
        }
    }
}

if ($MathRandomCount -eq 0) {
    Write-Host "  ✓ No problematic Math.random() usage found" -ForegroundColor Green
    "  No problematic Math.random() usage found" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
} else {
    Write-Host "  ✗ Found $MathRandomCount problematic Math.random() calls" -ForegroundColor Red
}
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

Write-Host ""
Write-Host "Scanning for generateSampleData functions..." -ForegroundColor Yellow
"2. generateSampleData Functions" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"===============================" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

# Sample data patterns
$SampleDataPatterns = @(
    'generateSampleData',
    'generateMockData',
    'generateTestData',
    'generateSample',
    'createMockData',
    'createSampleData'
)

$SourceFiles = Get-ChildItem -Path $FrontendDir -Recurse -Include *.ts,*.tsx,*.js,*.jsx -File | 
    Where-Object { 
        $_.FullName -notmatch '__tests__' -and 
        $_.FullName -notmatch '\.test\.' -and 
        $_.FullName -notmatch '\.spec\.' -and
        $_.FullName -notmatch '__mocks__'
    }

foreach ($pattern in $SampleDataPatterns) {
    foreach ($file in $SourceFiles) {
        $lines = Get-Content $file.FullName
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            if ($line -match "\b$pattern\b") {
                $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")
                $lineNum = $i + 1
                
                Write-Host "  Found: ${relativePath}:${lineNum}" -ForegroundColor Red
                "  Pattern: $pattern" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                "  File: $relativePath" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                "  Line: $lineNum" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                "  Code: $line" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                "" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                
                $GenerateSampleCount++
            }
        }
    }
}

if ($GenerateSampleCount -eq 0) {
    Write-Host "  ✓ No generateSampleData functions found" -ForegroundColor Green
    "  No generateSampleData functions found" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
} else {
    Write-Host "  ✗ Found $GenerateSampleCount sample data generation functions" -ForegroundColor Red
}
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

Write-Host ""
Write-Host "Scanning for hardcoded test data..." -ForegroundColor Yellow
"3. Hardcoded Test Data" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"======================" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

# Hardcoded data patterns (simplified for PowerShell)
$HardcodedKeywords = @('mock', 'sample', 'dummy', 'fake', 'test')

foreach ($file in $SourceFiles) {
    # Skip type definition files
    if ($file.FullName -match 'types' -or $file.FullName -match '\.d\.ts') {
        continue
    }
    
    $lines = Get-Content $file.FullName
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        
        # Look for const declarations with suspicious keywords
        if ($line -match 'const\s+\w+\s*=') {
            foreach ($keyword in $HardcodedKeywords) {
                if ($line -match "\b$keyword\b" -and $line -match '[{[]') {
                    $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")
                    $lineNum = $i + 1
                    
                    Write-Host "  Found: ${relativePath}:${lineNum}" -ForegroundColor Red
                    "  File: $relativePath" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                    "  Line: $lineNum" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                    "  Code: $line" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                    "" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
                    
                    $HardcodedDataCount++
                    break
                }
            }
        }
    }
}

if ($HardcodedDataCount -eq 0) {
    Write-Host "  ✓ No obvious hardcoded test data found" -ForegroundColor Green
    "  No obvious hardcoded test data found" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
} else {
    Write-Host "  ✗ Found $HardcodedDataCount potential hardcoded test data instances" -ForegroundColor Red
}
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

# Calculate total issues
$TotalIssues = $MathRandomCount + $GenerateSampleCount + $HardcodedDataCount

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Summary" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"Summary" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"=======" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"Math.random() calls (excluding tests/CSRF): $MathRandomCount" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"Sample data generation functions: $GenerateSampleCount" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"Hardcoded test data instances: $HardcodedDataCount" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"Total issues found: $TotalIssues" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

Write-Host "Math.random() calls (excluding tests/CSRF): $MathRandomCount" -ForegroundColor Red
Write-Host "Sample data generation functions: $GenerateSampleCount" -ForegroundColor Red
Write-Host "Hardcoded test data instances: $HardcodedDataCount" -ForegroundColor Red
Write-Host "Total issues found: $TotalIssues" -ForegroundColor Red
Write-Host ""

if ($TotalIssues -eq 0) {
    Write-Host "✓ No mock data issues found! Code is production-ready." -ForegroundColor Green
    "✓ No mock data issues found! Code is production-ready." | Out-File -FilePath $ReportFile -Append -Encoding UTF8
} else {
    Write-Host "⚠ Found $TotalIssues mock data issues that need attention." -ForegroundColor Yellow
    "⚠ Found $TotalIssues mock data issues that need attention." | Out-File -FilePath $ReportFile -Append -Encoding UTF8
}

Write-Host ""
Write-Host "Report saved to: $ReportFile" -ForegroundColor Blue
Write-Host ""

# Specific component checks
Write-Host "Checking specific visualization components..." -ForegroundColor Yellow
"" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"4. Specific Component Analysis" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"==============================" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

$Components = @(
    "components/visualizations/ArchitectureGraph.tsx",
    "components/visualizations/DependencyGraphVisualization.tsx",
    "components/visualizations/Neo4jGraphVisualization.tsx",
    "components/visualizations/PerformanceDashboard.tsx"
)

foreach ($component in $Components) {
    $componentPath = Join-Path $FrontendDir $component
    if (Test-Path $componentPath) {
        Write-Host "  Analyzing: $component" -ForegroundColor Blue
        "" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        "Component: $component" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        "---" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        
        $content = Get-Content $componentPath -Raw
        
        # Check for sample data generation
        if ($content -match 'generateSample') {
            Write-Host "    ✗ Contains sample data generation" -ForegroundColor Red
            "  Status: Contains sample data generation" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        } else {
            Write-Host "    ✓ No sample data generation found" -ForegroundColor Green
            "  Status: No sample data generation found" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        }
        
        # Check for Math.random
        $randomMatches = ([regex]::Matches($content, 'Math\.random\(\)')).Count
        if ($randomMatches -gt 0) {
            Write-Host "    ✗ Contains $randomMatches Math.random() calls" -ForegroundColor Red
            "  Math.random() calls: $randomMatches" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        } else {
            Write-Host "    ✓ No Math.random() calls" -ForegroundColor Green
            "  Math.random() calls: 0" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        }
        
        # Check for API calls
        if ($content -match 'fetch|axios|api') {
            Write-Host "    ✓ Contains API calls" -ForegroundColor Green
            "  API integration: Yes" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        } else {
            Write-Host "    ⚠ No API calls detected" -ForegroundColor Yellow
            "  API integration: No" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
        }
    } else {
        Write-Host "  Component not found: $component" -ForegroundColor Yellow
        "Component: $component - NOT FOUND" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
    }
}

Write-Host ""
Write-Host "Audit complete!" -ForegroundColor Green
Write-Host ""
"========================================" | Out-File -FilePath $ReportFile -Append -Encoding UTF8
"End of Report" | Out-File -FilePath $ReportFile -Append -Encoding UTF8

exit 0
