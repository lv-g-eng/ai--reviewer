# Error Handling Test Script
Write-Host "=== Error Handling Test ===" -ForegroundColor Green

$baseUrl = "http://localhost:3000"

function Test-ErrorScenario {
    param(
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$Description,
        [int]$ExpectedStatus
    )
    
    Write-Host "`n--- Testing: $Description ---" -ForegroundColor Yellow
    Write-Host "Expected Status: $ExpectedStatus"
    
    try {
        $params = @{
            Uri = "$baseUrl$Endpoint"
            Method = $Method
            Headers = $Headers
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content)"
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "✅ Expected status code received" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Unexpected status code" -ForegroundColor Yellow
        }
    }
    catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { 0 }
        $responseBody = ""
        
        if ($_.Exception.Response) {
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($stream)
                $responseBody = $reader.ReadToEnd()
                $reader.Close()
                $stream.Close()
            } catch {
                $responseBody = "Could not read response body"
            }
        }
        
        Write-Host "Status: $statusCode" -ForegroundColor Red
        Write-Host "Response: $responseBody" -ForegroundColor Red
        
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "✅ Expected status code received" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Unexpected status code (expected $ExpectedStatus, got $statusCode)" -ForegroundColor Yellow
        }
    }
}

# Test 1: 404 Not Found
Test-ErrorScenario -Method "GET" -Endpoint "/nonexistent-endpoint" -Description "404 Not Found" -ExpectedStatus 404

# Test 2: 401 Unauthorized (no token)
Test-ErrorScenario -Method "GET" -Endpoint "/api/v1/projects" -Headers @{'Content-Type'='application/json'} -Description "401 Unauthorized (No Token)" -ExpectedStatus 401

# Test 3: 401 Unauthorized (invalid token)
Test-ErrorScenario -Method "GET" -Endpoint "/api/v1/projects" -Headers @{'Content-Type'='application/json'; 'Authorization'='Bearer invalid-token'} -Description "401 Unauthorized (Invalid Token)" -ExpectedStatus 401

# Test 4: 400 Bad Request (invalid JSON)
Test-ErrorScenario -Method "POST" -Endpoint "/api/v1/projects" -Headers @{'Content-Type'='application/json'; 'Authorization'='Bearer fake-token'} -Body "invalid-json" -Description "400 Bad Request (Invalid JSON)" -ExpectedStatus 400

# Test 5: 405 Method Not Allowed
Test-ErrorScenario -Method "PATCH" -Endpoint "/health" -Description "405 Method Not Allowed" -ExpectedStatus 405

# Test 6: 413 Payload Too Large (if implemented)
$largeBody = "x" * 50000  # 50KB body
Test-ErrorScenario -Method "POST" -Endpoint "/api/v1/projects" -Headers @{'Content-Type'='application/json'; 'Authorization'='Bearer fake-token'} -Body $largeBody -Description "413 Payload Too Large" -ExpectedStatus 413

# Test 7: 503 Service Unavailable (backend down)
Test-ErrorScenario -Method "GET" -Endpoint "/health" -Description "503 Service Unavailable (Backend Down)" -ExpectedStatus 503

Write-Host "`n=== Error Handling Test Complete ===" -ForegroundColor Green