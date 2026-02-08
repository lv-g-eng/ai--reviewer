# Ollama Setup Script for Local Models
# Run this script in PowerShell as Administrator

Write-Host "=== Ollama Setup for AI Code Review Platform ===" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is installed
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaInstalled) {
    Write-Host "Ollama not found. Installing via winget..." -ForegroundColor Yellow
    winget install Ollama.Ollama
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "Ollama installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Ollama is already installed." -ForegroundColor Green
    ollama --version
}

Write-Host ""
Write-Host "=== Creating Modelfiles ===" -ForegroundColor Cyan

# Create temp directory for modelfiles
$tempDir = "C:\temp\ollama-models"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir | Out-Null
}

$modelsPath = "D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture\models"

# Modelfile 1: Qwen2.5-Coder
Write-Host "Creating modelfile for Qwen2.5-Coder..." -ForegroundColor Yellow
$qwenModelfile = @"
FROM $modelsPath\Qwen2.5-Coder-14B-Instruct-Q4_0.gguf

PARAMETER temperature 0.3
PARAMETER num_ctx 8192
PARAMETER num_predict 4000

SYSTEM "You are an expert AI assistant specialized in code analysis and software engineering."
"@

$qwenModelfile | Out-File -FilePath "$tempDir\modelfile-qwen" -Encoding UTF8

# Modelfile 2: DeepSeek-R1
Write-Host "Creating modelfile for DeepSeek-R1..." -ForegroundColor Yellow
$deepseekModelfile = @"
FROM $modelsPath\DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf

PARAMETER temperature 0.5
PARAMETER num_ctx 8192
PARAMETER num_predict 4000

SYSTEM "You are an expert AI assistant specialized in complex reasoning and problem-solving."
"@

$deepseekModelfile | Out-File -FilePath "$tempDir\modelfile-deepseek" -Encoding UTF8

# Modelfile 3: Llama3.3
Write-Host "Creating modelfile for Llama3.3..." -ForegroundColor Yellow
$llamaModelfile = @"
FROM $modelsPath\Llama3.3-8B-Instruct-Thinking-Heretic-Uncensored-Claude-4.5-Opus-High-Reasoning.i1-Q4_K_M.gguf

PARAMETER temperature 0.7
PARAMETER num_ctx 8192
PARAMETER num_predict 4000

SYSTEM "You are a helpful AI assistant."
"@

$llamaModelfile | Out-File -FilePath "$tempDir\modelfile-llama" -Encoding UTF8

Write-Host "Modelfiles created in $tempDir" -ForegroundColor Green
Write-Host ""

# Start Ollama service
Write-Host "=== Starting Ollama Service ===" -ForegroundColor Cyan
Write-Host "Starting Ollama in background..." -ForegroundColor Yellow

Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5

Write-Host "Ollama service started!" -ForegroundColor Green
Write-Host ""

# Load models into Ollama
Write-Host "=== Loading Models into Ollama ===" -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Loading Qwen2.5-Coder (14B)..." -ForegroundColor Yellow
Set-Location $tempDir
ollama create qwen2.5-coder:14b -f modelfile-qwen

Write-Host "Loading DeepSeek-R1 (7B)..." -ForegroundColor Yellow
ollama create deepseek-r1:7b -f modelfile-deepseek

Write-Host "Loading Llama3.3 (8B)..." -ForegroundColor Yellow
ollama create llama3.3:8b -f modelfile-llama

Write-Host ""
Write-Host "=== Verifying Models ===" -ForegroundColor Cyan
ollama list

Write-Host ""
Write-Host "=== Testing Models ===" -ForegroundColor Cyan

Write-Host "Testing Qwen2.5-Coder..." -ForegroundColor Yellow
ollama run qwen2.5-coder:14b "Write a Python function to calculate fibonacci numbers. Keep it brief."

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your local models are now ready to use!" -ForegroundColor Green
Write-Host "Ollama is running at: http://localhost:11434" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available models:" -ForegroundColor Cyan
Write-Host "  - qwen2.5-coder:14b (Primary - Code Analysis)" -ForegroundColor White
Write-Host "  - deepseek-r1:7b (Secondary - Reasoning)" -ForegroundColor White
Write-Host "  - llama3.3:8b (Tertiary - General Purpose)" -ForegroundColor White
Write-Host ""
Write-Host "To test the API:" -ForegroundColor Yellow
Write-Host '  curl http://localhost:11434/api/generate -d ''{"model":"qwen2.5-coder:14b","prompt":"Hello"}''' -ForegroundColor Gray
Write-Host ""
Write-Host "To stop Ollama:" -ForegroundColor Yellow
Write-Host "  Stop-Process -Name ollama" -ForegroundColor Gray
