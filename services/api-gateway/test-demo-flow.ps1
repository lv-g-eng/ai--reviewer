# Test Demo Flow Script
# Validates the complete demo flow before presentation

Write-Host "=== API Gateway Demo Flow Test ===" -ForegroundColor Green
Write-Host "Testing complete demo flow to ensure everything works correctly" -ForegroundColor Gray
Write-Host ""

$baseUrl = "http://localhost:3000"
$testResults = @()

function Test-DemoFlow {
    param(
        [string]$TestName,
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [int]$ExpectedStatus = 200,
        [bool]$ShouldSucceed = $true
    )
    
    Write-Host "Testing: $TestName" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ PASS - Status: $($response.StatusCode)" -ForegroundColor Green
            $testResults += @{ Test = $TestName; Result = "PASS"; Status = $response.StatusCode }
        } else {
            Write-Host "  ❌ FAIL - Expected: $ExpectedStatus, Got: $($response.StatusCode)" -ForegroundColor Red
            $testResults += @{ Test = $TestName; Result = "FAIL"; Status = $response.StatusCode }
        }
    }
    catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Error" }
        
        if (-not $ShouldSucceed -and $statusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ PASS - Expected failure: $statusCode" -ForegroundColor Green
            $testResults += @{ Test = $TestName; Result = "PASS"; Status = $statusCode }
        } else {
            Write-Host "  ❌ FAIL - Error: $statusCode" -ForegroundColor Red
            $testResults += @{ Test = $TestName; Result = "FAIL"; Status = $statusCode }
        }
    }
}

# Create demo JWT token
$userToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vQGV4YW1wbGUuY29tIiwibmFtZSI6IkRlbW8gVXNlciIsInJvbGUiOiJ1c2VyIn0.demo-signature"
$userHeaders = @{
    'Content-Type' = 'application/json'
    'Authorization' = "Bearer $userToken"
}

# Test 1: Health Check
Test-DemoFlow -TestName "Health Check" -Method "GET" -Url "$baseUrl/health"

# Test 2: Authentication
Test-DemoFlow -TestName "Unauthenticated Access" -Method "GET" -Url "$baseUrl/api/v1/projects" -ExpectedStatus 401 -ShouldSucceed $false

# Test 3: Authenticated Access
Test-DemoFlow -TestName "Authenticated Access" -Method "GET" -Url "$baseUrl/api/v1/projects" -Headers $userHeaders

# Test 4: Request Validation
$validProject = '{"name":"Demo Project","description":"Test project","repositoryUrl":"https://github.com/demo/test"}'
Test-DemoFlow -TestName "Valid Project Creation" -Method "POST" -Url "$baseUrl/api/v1/projects" -Headers $userHeaders -Body $validProject -ExpectedStatus 201

# Test 5: Invalid Request
$invalidProject = '{"description":"Missing name"}'
Test-DemoFlow -TestName "Invalid Project Creation" -Method "POST" -Url "$baseUrl/api/v1/projects" -Headers $userHeaders -Body $invalidProject -ExpectedStatus 400 -ShouldSucceed $false

# Summary
Write-Host ""
Write-Host "=== Demo Flow Test Results ===" -ForegroundColor Green
$passCount = ($testResults | Where-Object { $_.Result -eq "PASS" }).Count
$totalCount = $testResults.Count

foreach ($result in $testResults) {
    $color = if ($result.Result -eq "PASS") { "Green" } else { "Red" }
    Write-Host "  $($result.Test): $($result.Result)" -ForegroundColor $color
}

Write-Host ""
Write-Host "Overall Result: $passCount/$totalCount tests passed" -ForegroundColor $(if ($passCount -eq $totalCount) { "Green" } else { "Red" })

if ($passCount -eq $totalCount) {
    Write-Host "✅ Demo flow is ready for presentation!" -ForegroundColor Green
} else {
    Write-Host "❌ Demo flow has issues that need to be resolved" -ForegroundColor Red
}