# Rate Limiting Test Script
Write-Host "=== Rate Limiting Test ===" -ForegroundColor Green

$baseUrl = "http://localhost:3000"
$headers = @{
    'Content-Type' = 'application/json'
    'User-Agent' = 'RateLimit-Test/1.0'
}

function Test-RateLimit {
    param(
        [string]$Endpoint,
        [int]$RequestCount,
        [string]$Description
    )
    
    Write-Host "`n--- Testing Rate Limit: $Description ---" -ForegroundColor Yellow
    Write-Host "Endpoint: $Endpoint"
    Write-Host "Sending $RequestCount requests..."
    
    $results = @()
    
    for ($i = 1; $i -le $RequestCount; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl$Endpoint" -Method GET -Headers $headers -TimeoutSec 5
            $result = @{
                Request = $i
                StatusCode = $response.StatusCode
                RateLimitRemaining = $response.Headers['X-RateLimit-Remaining']
                RateLimitReset = $response.Headers['X-RateLimit-Reset']
                Success = $true
            }
            Write-Host "Request $i`: ✅ $($response.StatusCode)" -ForegroundColor Green
        }
        catch {
            $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Error" }
            $result = @{
                Request = $i
                StatusCode = $statusCode
                Success = $false
                Error = $_.Exception.Message
            }
            if ($statusCode -eq 429) {
                Write-Host "Request $i`: ❌ 429 (Rate Limited)" -ForegroundColor Red
            } else {
                Write-Host "Request $i`: ❌ $statusCode" -ForegroundColor Red
            }
        }
        $results += $result
        Start-Sleep -Milliseconds 100  # Small delay between requests
    }
    
    return $results
}

# Test 1: General API Rate Limit (should be 10 requests per minute based on our config)
$generalResults = Test-RateLimit -Endpoint "/health" -RequestCount 15 -Description "General API Rate Limit"

# Wait a moment
Write-Host "`nWaiting 5 seconds before next test..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Test 2: Auth Rate Limit (should be 3 requests per minute based on our config)
$authResults = Test-RateLimit -Endpoint "/api/auth/login" -RequestCount 8 -Description "Auth Rate Limit"

# Summary
Write-Host "`n=== Rate Limiting Test Summary ===" -ForegroundColor Green
Write-Host "General API Limit Test:"
$successCount = ($generalResults | Where-Object { $_.Success -eq $true }).Count
$rateLimitedCount = ($generalResults | Where-Object { $_.StatusCode -eq 429 }).Count
Write-Host "  - Successful requests: $successCount"
Write-Host "  - Rate limited requests: $rateLimitedCount"

Write-Host "`nAuth API Limit Test:"
$authSuccessCount = ($authResults | Where-Object { $_.Success -eq $true }).Count
$authRateLimitedCount = ($authResults | Where-Object { $_.StatusCode -eq 429 }).Count
Write-Host "  - Successful requests: $authSuccessCount"
Write-Host "  - Rate limited requests: $authRateLimitedCount"