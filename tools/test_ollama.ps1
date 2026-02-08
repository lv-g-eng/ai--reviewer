# Test Ollama Setup
# Quick verification script

Write-Host "=== Testing Ollama Setup ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if Ollama is installed
Write-Host "[1/5] Checking Ollama installation..." -ForegroundColor Yellow
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "  ✓ Ollama is installed" -ForegroundColor Green
    ollama --version
} else {
    Write-Host "  ✗ Ollama is NOT installed" -ForegroundColor Red
    Write-Host "  Run: winget install Ollama.Ollama" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Check if Ollama service is running
Write-Host "[2/5] Checking Ollama service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Ollama service is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama service is NOT running" -ForegroundColor Red
    Write-Host "  Run: ollama serve" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 3: List available models
Write-Host "[3/5] Checking loaded models..." -ForegroundColor Yellow
$models = ollama list
Write-Host $models

$hasQwen = $models -match "qwen2.5-coder"
$hasDeepseek = $models -match "deepseek-r1"
$hasLlama = $models -match "llama3.3"

if ($hasQwen) {
    Write-Host "  ✓ qwen2.5-coder:14b is loaded" -ForegroundColor Green
} else {
    Write-Host "  ✗ qwen2.5-coder:14b is NOT loaded" -ForegroundColor Red
}

if ($hasDeepseek) {
    Write-Host "  ✓ deepseek-r1:7b is loaded" -ForegroundColor Green
} else {
    Write-Host "  ✗ deepseek-r1:7b is NOT loaded" -ForegroundColor Red
}

if ($hasLlama) {
    Write-Host "  ✓ llama3.3:8b is loaded" -ForegroundColor Green
} else {
    Write-Host "  ✗ llama3.3:8b is NOT loaded" -ForegroundColor Red
}

Write-Host ""

# Test 4: Test API with a simple request
Write-Host "[4/5] Testing Ollama API..." -ForegroundColor Yellow
if ($hasQwen) {
    try {
        $body = @{
            model = "qwen2.5-coder:14b"
            prompt = "Say 'Hello from Ollama!'"
            stream = $false
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        
        if ($response.response) {
            Write-Host "  ✓ API is working!" -ForegroundColor Green
            Write-Host "  Response: $($response.response)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ✗ API test failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ⊘ Skipping API test (no models loaded)" -ForegroundColor Yellow
}

Write-Host ""

# Test 5: Summary
Write-Host "[5/5] Summary" -ForegroundColor Yellow
Write-Host ""

if ($ollama -and $response -and ($hasQwen -or $hasDeepseek -or $hasLlama)) {
    Write-Host "✓ Ollama is ready to use!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor Cyan
    Write-Host "  1. Run the Agentic AI Service tests" -ForegroundColor White
    Write-Host "  2. Start the backend server" -ForegroundColor White
    Write-Host "  3. Test code analysis features" -ForegroundColor White
} else {
    Write-Host "✗ Ollama setup is incomplete" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "  1. Run setup_ollama.ps1 to complete setup" -ForegroundColor White
    Write-Host "  2. Or follow OLLAMA_SETUP_GUIDE.md for manual setup" -ForegroundColor White
}

Write-Host ""
