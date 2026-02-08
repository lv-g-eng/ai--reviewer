# Ollama Setup - Complete Guide

## What I've Created for You

I've prepared everything you need to set up Ollama with your local models:

### 📄 Files Created

1. **`setup_ollama.ps1`** - Automated setup script
   - Installs Ollama
   - Creates modelfiles
   - Loads your 3 models
   - Starts the service
   - Tests everything

2. **`test_ollama.ps1`** - Verification script
   - Checks if Ollama is installed
   - Verifies service is running
   - Lists loaded models
   - Tests the API
   - Provides status summary

3. **`OLLAMA_SETUP_GUIDE.md`** - Detailed manual guide
   - Step-by-step instructions
   - Manual setup commands
   - Troubleshooting tips
   - Configuration details

## Quick Start (Recommended)

### Option 1: Automated Setup (Easiest)

```powershell
# Open PowerShell as Administrator
# Navigate to project directory
cd D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture

# Run setup script
.\setup_ollama.ps1
```

This will take 5-10 minutes depending on your system.

### Option 2: Manual Setup

Follow the instructions in `OLLAMA_SETUP_GUIDE.md`

## After Setup

### Verify Everything Works

```powershell
# Run verification script
.\test_ollama.ps1
```

You should see:
- ✓ Ollama is installed
- ✓ Ollama service is running
- ✓ qwen2.5-coder:14b is loaded
- ✓ deepseek-r1:7b is loaded
- ✓ llama3.3:8b is loaded
- ✓ API is working!

## Your Models Configuration

The Agentic AI Service is configured to use these models in priority order:

### 1. Qwen2.5-Coder (14B) - PRIMARY
- **Purpose**: Code analysis, review, and suggestions
- **Temperature**: 0.3 (focused, deterministic)
- **Context**: 8192 tokens
- **Best for**: 
  - Clean Code violation detection
  - Code quality analysis
  - Refactoring suggestions

### 2. DeepSeek-R1 (7B) - SECONDARY
- **Purpose**: Complex reasoning and problem-solving
- **Temperature**: 0.5 (balanced)
- **Context**: 8192 tokens
- **Best for**:
  - Architectural analysis
  - Decision simulation
  - Pattern recognition

### 3. Llama3.3 (8B) - TERTIARY
- **Purpose**: General purpose fallback
- **Temperature**: 0.7 (creative)
- **Context**: 8192 tokens
- **Best for**:
  - Natural language generation
  - Explanations
  - General queries

## How It Works

### Automatic Failover

The system tries models in order:

```
Request → Qwen2.5-Coder (try)
            ↓ (if fails)
          DeepSeek-R1 (try)
            ↓ (if fails)
          Llama3.3 (try)
            ↓ (if fails)
          Error returned
```

### Circuit Breaker Protection

- If a model fails 3 times, it's temporarily disabled
- Prevents wasting time on broken models
- Automatically re-enables after cooldown

## Testing the Setup

### Test 1: Basic API Call

```powershell
# Test Qwen2.5-Coder
ollama run qwen2.5-coder:14b "Write a Python function to reverse a string"
```

### Test 2: API via HTTP

```powershell
$body = @{
    model = "qwen2.5-coder:14b"
    prompt = "Explain what Clean Code means"
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
```

### Test 3: Python Integration

```python
# Test from Python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5-coder:14b",
        "prompt": "Hello from Python!",
        "stream": False
    }
)

print(response.json()["response"])
```

## Integration with Platform

The Agentic AI Service (`backend/app/services/agentic_ai_service.py`) is already configured:

```python
from app.services.agentic_ai_service import create_agentic_ai_service

# Create service (automatically uses Ollama)
service = create_agentic_ai_service()

# Use the service
violations = await service.analyze_clean_code_violations(
    code=source_code,
    file_path="app/main.py",
    language="python"
)
```

## Troubleshooting

### Issue: Ollama won't start

```powershell
# Check if already running
Get-Process ollama

# Kill and restart
Stop-Process -Name ollama -Force
ollama serve
```

### Issue: Models not loading

```powershell
# Check model file exists
Test-Path "D:\Desktop\AI-Based-Quality-Check-On-Project-Code-And-Architecture\models\Qwen2.5-Coder-14B-Instruct-Q4_0.gguf"

# Try loading manually
ollama create qwen2.5-coder:14b -f modelfile-qwen
```

### Issue: API not responding

```powershell
# Test connection
Test-NetConnection -ComputerName localhost -Port 11434

# Check Ollama logs
# Logs location: %LOCALAPPDATA%\Ollama\logs
```

### Issue: Out of memory

- Close other applications
- Try smaller models first
- Increase virtual memory (pagefile)

## Performance Tips

### For Best Performance:

1. **Use SSD**: Models load faster from SSD
2. **Enough RAM**: 16GB+ recommended for 14B models
3. **GPU**: If you have NVIDIA GPU, Ollama will use it automatically
4. **Close other apps**: Free up RAM for models

### Expected Response Times:

- **Qwen2.5-Coder (14B)**: 2-5 seconds per request
- **DeepSeek-R1 (7B)**: 1-3 seconds per request
- **Llama3.3 (8B)**: 1-3 seconds per request

## Next Steps

Once Ollama is set up and verified:

1. ✅ **Ollama Setup Complete**
2. ⏭️ **Run Task 6.2**: Write property tests for multi-provider support
3. ⏭️ **Run Task 2.8**: Integrate Agentic AI with Code Review Service
4. ⏭️ **Test End-to-End**: Full code review with AI analysis

## Useful Commands

```powershell
# List all models
ollama list

# Show model details
ollama show qwen2.5-coder:14b

# Remove a model
ollama rm qwen2.5-coder:14b

# Pull a model from Ollama library
ollama pull codellama

# Stop Ollama
Stop-Process -Name ollama

# Start Ollama
ollama serve
```

## Resources

- **Ollama Documentation**: https://github.com/ollama/ollama
- **Ollama API**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Model Library**: https://ollama.ai/library

## Support

If you encounter issues:

1. Check `OLLAMA_SETUP_GUIDE.md` for detailed troubleshooting
2. Run `.\test_ollama.ps1` to diagnose problems
3. Check Ollama logs in `%LOCALAPPDATA%\Ollama\logs`

## Summary

You now have:
- ✅ Automated setup script (`setup_ollama.ps1`)
- ✅ Verification script (`test_ollama.ps1`)
- ✅ Detailed manual guide (`OLLAMA_SETUP_GUIDE.md`)
- ✅ Agentic AI Service configured to use local models
- ✅ Automatic failover between 3 models
- ✅ Circuit breaker protection

**Ready to proceed with implementation!** 🚀
