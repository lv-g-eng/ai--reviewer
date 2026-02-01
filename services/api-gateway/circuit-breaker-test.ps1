# Circuit Breaker Test Script
Write-Host "=== Circuit Breaker Test ===" -ForegroundColor Green

$baseUrl = "http://localhost:3000"
$headers = @{
    'Content-Type' = 'application/json'
    'User-Agent' = 'CircuitBreaker-Test/1.0'
    'Authorization' = 'Bearer fake-token-for-testing'  # Add fake token to bypass auth
}

function Test-CircuitBreaker {
    param(
        [string]$Endpoint,
        [int]$RequestCount,
        [string]$Description
    )
    
    Write-Host "`n--- Testing Circuit Breaker: $Description ---" -ForegroundColor Yellow
    Write-Host "Endpoint: $Endpoint"
    Write-Host "Sending $RequestCount requests to trigger circuit breaker..."
    
    $results = @()
    
    for ($i = 1; $i -le $RequestCount; $i++) {
        $startTime = Get-Date
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl$Endpoint" -Method GET -Headers $headers -TimeoutSec 10
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            
            $result = @{
                Request = $i
                StatusCode = $response.StatusCode
                Duration = $duration
                Success = $true
                Response = $response.Content
            }
            Write-Host "Request $i`: ✅ $($response.StatusCode) (${duration}ms)" -ForegroundColor Green
        }
        catch {
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "Error" }
            
            $result = @{
                Request = $i
                StatusCode = $statusCode
                Duration = $duration
                Success = $false
                Error = $_.Exception.Message
            }
            
            if ($statusCode -eq 503) {
                Write-Host "Request $i`: ❌ 503 Service Unavailable (${duration}ms)" -ForegroundColor Red
            } elseif ($statusCode -eq 429) {
                Write-Host "Request $i`: ❌ 429 Rate Limited (${duration}ms)" -ForegroundColor Yellow
                break  # Stop if rate limited
            } else {
                Write-Host "Request $i`: ❌ $statusCode (${duration}ms)" -ForegroundColor Red
            }
        }
        $results += $result
        Start-Sleep -Milliseconds 200  # Small delay between requests
    }
    
    return $results
}

# Test Circuit Breaker with different endpoints
Write-Host "Testing circuit breaker behavior with unavailable backend services..."

# Test 1: Projects service (should trigger circuit breaker after several failures)
$projectResults = Test-CircuitBreaker -Endpoint "/api/v1/projects" -RequestCount 8 -Description "Projects Service Circuit Breaker"

# Wait for circuit breaker to potentially open
Write-Host "`nWaiting 5 seconds to observe circuit breaker state..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Test 2: More requests to see if circuit breaker is open (should fail fast)
$fastFailResults = Test-CircuitBreaker -Endpoint "/api/v1/projects" -RequestCount 3 -Description "Circuit Breaker Fast Fail"

# Summary
Write-Host "`n=== Circuit Breaker Test Summary ===" -ForegroundColor Green

Write-Host "Initial requests (should show normal failure times):"
$initialRequests = $projectResults | Select-Object -First 5
foreach ($req in $initialRequests) {
    Write-Host "  Request $($req.Request): $($req.StatusCode) - $([math]::Round($req.Duration, 0))ms"
}

Write-Host "`nLater requests (should show circuit breaker behavior):"
$laterRequests = $projectResults | Select-Object -Last 3
foreach ($req in $laterRequests) {
    Write-Host "  Request $($req.Request): $($req.StatusCode) - $([math]::Round($req.Duration, 0))ms"
}

Write-Host "`nFast fail requests (should be very quick if circuit is open):"
foreach ($req in $fastFailResults) {
    Write-Host "  Request $($req.Request): $($req.StatusCode) - $([math]::Round($req.Duration, 0))ms"
}

# Calculate average response times
$avgInitial = ($initialRequests | Measure-Object -Property Duration -Average).Average
$avgLater = ($laterRequests | Measure-Object -Property Duration -Average).Average
$avgFastFail = ($fastFailResults | Measure-Object -Property Duration -Average).Average

Write-Host "`nAverage Response Times:"
Write-Host "  Initial requests: $([math]::Round($avgInitial, 0))ms"
Write-Host "  Later requests: $([math]::Round($avgLater, 0))ms"  
Write-Host "  Fast fail requests: $([math]::Round($avgFastFail, 0))ms"

if ($avgFastFail -lt ($avgInitial * 0.5)) {
    Write-Host "✅ Circuit breaker appears to be working (fast fail detected)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Circuit breaker behavior unclear" -ForegroundColor Yellow
}