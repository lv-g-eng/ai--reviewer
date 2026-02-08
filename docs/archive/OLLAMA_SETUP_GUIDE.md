# Ollama Setup Guide for Local Models

## Quick Start (Automated)

Run the PowerShell setup script:

```powershell
# Run as Administrator
.\setup_ollama.ps1
```

This will:
1. Install Ollama (if not installed)
2. Create modelfiles for your local models
3. Load models into Ollama
4. Start the Ollama service
5. Test the models

## Manual Setup

### Step 1: Install Ollama

```powershell
# Using winget
winget install Ollama.Ollama

# Verify installation
ollama --version
```

### Step 2: Start Ollama Service

```powershell
# Start Ollama in background
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden

# Or in a separate terminal
ollama serve
```

### Step 3: Load Your Models

Create modelfiles and load them:

#### Qwen2.5-Coder (Primary - Code Analysis)

```powershell
# Create modelfile
@"
FROM D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture\models\Qwen2.5-Coder-14B-Instruct-Q4_0.gguf
PARAMETER temperature 0.3
PARAMETER num_ctx 8192
SYSTEM "You are an expert code analyzer."
"@ | Out-File modelfile-qwen

# Load into Ollama
ollama create qwen2.5-coder:14b -f modelfile-qwen
```

#### DeepSeek-R1 (Secondary - Reasoning)

```powershell
# Create modelfile
@"
FROM D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture\models\DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf
PARAMETER temperature 0.5
PARAMETER num_ctx 8192
SYSTEM "You are an expert reasoning assistant."
"@ | Out-File modelfile-deepseek

# Load into Ollama
ollama create deepseek-r1:7b -f modelfile-deepseek
```

#### Llama3.3 (Tertiary - General Purpose)

```powershell
# Create modelfile
@"
FROM D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture\models\Llama3.3-8B-Instruct-Thinking-Heretic-Uncensored-Claude-4.5-Opus-High-Reasoning.i1-Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
SYSTEM "You are a helpful AI assistant."
"@ | Out-File modelfile-llama

# Load into Ollama
ollama create llama3.3:8b -f modelfile-llama
```

### Step 4: Verify Models

```powershell
# List loaded models
ollama list

# Test a model
ollama run qwen2.5-coder:14b "Write a hello world function in Python"
```

## Testing the API

```powershell
# Test with curl
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5-coder:14b","prompt":"Hello"}'

# Test with PowerShell
Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body '{"model":"qwen2.5-coder:14b","prompt":"Hello","stream":false}' -ContentType "application/json"
```

## Troubleshooting

### Ollama not starting
```powershell
# Check if Ollama is running
Get-Process ollama -ErrorAction SilentlyContinue

# Kill and restart
Stop-Process -Name ollama -Force
ollama serve
```

### Model not loading
- Verify the GGUF file path is correct
- Check file permissions
- Ensure enough disk space (models are large)

### API not responding
```powershell
# Check if Ollama is listening
Test-NetConnection -ComputerName localhost -Port 11434
```

## Configuration for the Platform

Once Ollama is running, the Agentic AI Service is already configured to use it:

```python
# In backend/app/services/agentic_ai_service.py
service = create_agentic_ai_service(
    ollama_base_url="http://localhost:11434"
)
```

The service will automatically:
1. Try Qwen2.5-Coder first (best for code)
2. Fallback to DeepSeek-R1 if needed
3. Fallback to Llama3.3 as last resort

## Next Steps

After Ollama is set up:

1. ✅ Ollama installed and running
2. ✅ Models loaded
3. ⏭️ Run property tests (Task 6.2)
4. ⏭️ Integrate with Code Review Service (Task 2.8)

## Useful Commands

```powershell
# List models
ollama list

# Remove a model
ollama rm qwen2.5-coder:14b

# Show model info
ollama show qwen2.5-coder:14b

# Stop Ollama
Stop-Process -Name ollama

# Check Ollama logs
# Logs are in: %LOCALAPPDATA%\Ollama\logs
```