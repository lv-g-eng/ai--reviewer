# Manual Testing Script for API Gateway
Write-Host "=== API Gateway Manual Testing ===" -ForegroundColor Green

$baseUrl = "http://localhost:3000"
$headers = @{
    'Content-Type' = 'application/json'
    'User-Agent' = 'Manual-Test/1.0'
}

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$Description
    )
    
    Write-Host "`n--- Testing: $Description ---" -ForegroundColor Yellow
    Write-Host "Method: $Method"
    Write-Host "URL: $Url"
    
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
        Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Headers: $($response.Headers | ConvertTo-Json -Compress)"
        Write-Host "Response: $($response.Content)"
        
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content
            Headers = $response.Headers
        }
    }
    catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { "N/A" }
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Status Code: $statusCode"
        
        return @{
            Success = $false
            StatusCode = $statusCode
            Error = $_.Exception.Message
        }
    }
}

# Test 1: Health Check
Test-Endpoint -Method "GET" -Url "$baseUrl/health" -Headers $headers -Description "Health Check"

# Test 2: Projects Service Endpoints
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/projects" -Headers $headers -Description "List Projects"
Test-Endpoint -Method "POST" -Url "$baseUrl/api/v1/projects" -Headers $headers -Body '{"name":"test-project","description":"Test project"}' -Description "Create Project"
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/projects/123" -Headers $headers -Description "Get Project by ID"

# Test 3: Reviews Service Endpoints  
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/reviews" -Headers $headers -Description "List Reviews"
Test-Endpoint -Method "POST" -Url "$baseUrl/api/v1/reviews" -Headers $headers -Body '{"projectId":"123","type":"code"}' -Description "Create Review"

# Test 4: Architecture Service Endpoints
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/architecture/123" -Headers $headers -Description "Get Architecture"
Test-Endpoint -Method "POST" -Url "$baseUrl/api/v1/architecture/123/scan" -Headers $headers -Description "Trigger Architecture Scan"

# Test 5: Queue Service Endpoints
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/queue" -Headers $headers -Description "List Queue Items"
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/queue/123" -Headers $headers -Description "Get Queue Item"

# Test 6: Admin Service Endpoints
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/admin/users" -Headers $headers -Description "List Users (Admin)"
Test-Endpoint -Method "GET" -Url "$baseUrl/api/v1/admin/settings" -Headers $headers -Description "Get Settings (Admin)"

# Test 7: Authentication Endpoints
Test-Endpoint -Method "POST" -Url "$baseUrl/api/auth/login" -Headers $headers -Body '{"email":"test@example.com","password":"password"}' -Description "Login"
Test-Endpoint -Method "POST" -Url "$baseUrl/api/auth/register" -Headers $headers -Body '{"email":"test@example.com","password":"password","name":"Test User"}' -Description "Register"

# Test 8: Webhook Endpoints
Test-Endpoint -Method "POST" -Url "$baseUrl/api/webhooks/github" -Headers $headers -Body '{"action":"push","repository":{"name":"test"}}' -Description "GitHub Webhook"

Write-Host "`n=== Manual Testing Complete ===" -ForegroundColor Green