# Local LLM Integration Guide

## Overview

This platform integrates local Large Language Models (LLMs) using GGUF format for efficient inference. The system uses three specialized models for different tasks:

1. **Qwen2.5-Coder-14B** - Code review and analysis
2. **DeepSeek-R1-Distill-Qwen-7B** - General purpose and architecture analysis
3. **Qwen3-VL-8B** - Vision and multimodal tasks

## Architecture

```
┌─────────────────┐
│  Frontend/API   │
└────────┬────────┘
         │
┌────────▼────────────────────────────────────┐
│         API Gateway / Backend               │
│  ┌──────────────────────────────────────┐  │
│  │      LLM Service (FastAPI)           │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │   llama-cpp-python             │  │  │
│  │  │   - Model Loading              │  │  │
│  │  │   - Inference Engine           │  │  │
│  │  │   - GPU Acceleration           │  │  │
│  │  └────────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │
┌────────▼────────┐
│  GGUF Models    │
│  (models/)      │
└─────────────────┘
```

## Models

### 1. Qwen2.5-Coder-14B-Instruct (Q4_0)
- **Purpose**: Code review, bug detection, security analysis
- **Size**: ~8GB
- **Context**: 8192 tokens
- **Use Cases**:
  - Code quality assessment
  - Security vulnerability detection
  - Performance optimization suggestions
  - Best practice recommendations

### 2. DeepSeek-R1-Distill-Qwen-7B (Q4_K_M)
- **Purpose**: General reasoning and architecture analysis
- **Size**: ~4.5GB
- **Context**: 4096 tokens
- **Use Cases**:
  - System architecture analysis
  - Design pattern identification
  - Scalability recommendations
  - Documentation generation

### 3. Qwen3-VL-8B-Instruct (Q4_K_M)
- **Purpose**: Visual analysis (future use)
- **Size**: ~5GB
- **Context**: 4096 tokens
- **Use Cases**:
  - Diagram analysis
  - UI/UX review
  - Visual documentation

## Installation

### Prerequisites

1. **GPU Support (Recommended)**
   - NVIDIA GPU with CUDA support
   - CUDA 12.1 or later
   - At least 8GB VRAM

2. **CPU-Only Mode**
   - 16GB+ RAM recommended
   - Multi-core processor

### Setup Steps

#### 1. Install Dependencies

**Backend (Python):**
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-llm.txt
```

**LLM Service:**
```bash
cd services/llm-service
pip install -r requirements.txt
```

#### 2. Configure Models

Add to `.env`:
```env
# LLM Configuration
MODELS_DIR=models
LLM_ENABLED=true
LLM_GPU_LAYERS=35  # Set to 0 for CPU-only
LLM_THREADS=8
LLM_CONTEXT_SIZE=4096
```

#### 3. Verify Models

Ensure your models are in the `models/` directory:
```
models/
├── Qwen2.5-Coder-14B-Instruct-Q4_0.gguf
├── DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf
└── Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf
```

## Usage

### Backend API Endpoints

#### 1. Analyze Code
```bash
POST /api/v1/llm/analyze-code
Content-Type: application/json
Authorization: Bearer <token>

{
  "code": "def hello():\n    print('Hello')",
  "language": "python",
  "analysis_type": "review"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "analysis": "Code quality assessment...",
    "issues": ["Missing docstring", "No type hints"],
    "suggestions": ["Add docstring", "Add type annotations"],
    "severity": "low"
  },
  "model": "code_review"
}
```

#### 2. Generate Text
```bash
POST /api/v1/llm/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "Explain dependency injection",
  "model_type": "general",
  "temperature": 0.3,
  "max_tokens": 512
}
```

#### 3. Analyze Architecture
```bash
POST /api/v1/llm/analyze-architecture
Content-Type: application/json
Authorization: Bearer <token>

{
  "components": ["API Gateway", "Auth Service", "Database"],
  "dependencies": [
    {"from": "API Gateway", "to": "Auth Service"},
    {"from": "Auth Service", "to": "Database"}
  ],
  "patterns": ["Microservices", "API Gateway"]
}
```

#### 4. List Models
```bash
GET /api/v1/llm/models
Authorization: Bearer <token>
```

#### 5. Load/Unload Models
```bash
POST /api/v1/llm/models/code_review/load
POST /api/v1/llm/models/code_review/unload
Authorization: Bearer <token>
```

### LLM Service Endpoints

The dedicated LLM service runs on port 8000:

```bash
# Health check
GET http://localhost:8000/health

# Analyze code
POST http://localhost:8000/analyze/code
{
  "code": "...",
  "language": "python",
  "analysis_type": "security"
}

# Generate text
POST http://localhost:8000/generate
{
  "prompt": "...",
  "model_type": "code_review"
}
```

### Code Review Engine Integration

The code-review-engine service automatically uses the LLM service:

```typescript
import { llmClient } from './llm-client';

// Analyze code
const result = await llmClient.analyzeCode({
  code: sourceCode,
  language: 'typescript',
  analysis_type: 'review'
});

// Check health
const health = await llmClient.healthCheck();
```

## Docker Deployment

### With GPU Support

```bash
# Build and run with GPU
docker-compose up llm-service

# Or with docker run
docker run --gpus all \
  -v $(pwd)/models:/app/models:ro \
  -p 8000:8000 \
  -e LLM_GPU_LAYERS=35 \
  llm-service
```

### CPU-Only Mode

Update `docker-compose.yml`:
```yaml
llm-service:
  environment:
    - LLM_GPU_LAYERS=0  # CPU only
  # Remove GPU reservation
```

## Performance Tuning

### GPU Configuration

**High VRAM (16GB+):**
```env
LLM_GPU_LAYERS=35  # Offload most layers
LLM_CONTEXT_SIZE=8192
```

**Medium VRAM (8-16GB):**
```env
LLM_GPU_LAYERS=20
LLM_CONTEXT_SIZE=4096
```

**Low VRAM (4-8GB):**
```env
LLM_GPU_LAYERS=10
LLM_CONTEXT_SIZE=2048
```

### CPU Configuration

```env
LLM_GPU_LAYERS=0
LLM_THREADS=8  # Match CPU cores
LLM_CONTEXT_SIZE=2048
```

### Memory Management

Models are loaded on-demand (lazy loading):
- First request loads the model (~30-60 seconds)
- Subsequent requests use cached model
- Unload models to free memory

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/llm/health

# LLM service health
curl http://localhost:8000/health
```

### Model Status

```bash
curl http://localhost:8000/api/v1/llm/models
```

**Response:**
```json
{
  "success": true,
  "models": {
    "code_review": {
      "type": "code_review",
      "loaded": true,
      "exists": true,
      "config": {
        "n_ctx": 8192,
        "n_threads": 8,
        "n_gpu_layers": 35
      }
    }
  }
}
```

## Troubleshooting

### Model Not Found

**Error:** `Model file not found: models/...`

**Solution:**
1. Verify models are in the correct directory
2. Check file permissions
3. Ensure correct file names

### Out of Memory

**Error:** `CUDA out of memory` or `Failed to allocate memory`

**Solution:**
1. Reduce `LLM_GPU_LAYERS`
2. Reduce `LLM_CONTEXT_SIZE`
3. Use smaller quantization (Q4_0 instead of Q4_K_M)
4. Unload unused models

### Slow Inference

**CPU Mode:**
- Increase `LLM_THREADS`
- Use smaller models
- Reduce `max_tokens`

**GPU Mode:**
- Increase `LLM_GPU_LAYERS`
- Check GPU utilization: `nvidia-smi`
- Ensure CUDA is properly installed

### Service Unavailable

**Error:** `LLM service health check failed`

**Solution:**
1. Check if LLM service is running: `docker ps`
2. Check logs: `docker logs llm-service`
3. Verify network connectivity
4. Check port 8000 is not in use

## Best Practices

### 1. Model Selection

- **Code Review**: Use `code_review` model
- **Architecture**: Use `general` model
- **Documentation**: Use `general` model

### 2. Prompt Engineering

**Good Prompt:**
```
Analyze this Python code for security vulnerabilities:

```python
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"
```

Identify SQL injection risks and provide fixes.
```

**Bad Prompt:**
```
check this code
```

### 3. Resource Management

- Load models only when needed
- Unload models during low usage
- Monitor memory usage
- Use appropriate context sizes

### 4. Error Handling

```typescript
try {
  const result = await llmClient.analyzeCode({
    code,
    language,
    analysis_type: 'review'
  });
} catch (error) {
  // Fallback to rule-based analysis
  console.error('LLM analysis failed:', error);
  return fallbackAnalysis(code);
}
```

## API Reference

### Model Types

```typescript
enum ModelType {
  CODE_REVIEW = 'code_review',
  GENERAL = 'general',
  VISION = 'vision'
}
```

### Analysis Types

```typescript
type AnalysisType = 'review' | 'security' | 'performance';
```

### Severity Levels

```typescript
type Severity = 'low' | 'medium' | 'high';
```

## Future Enhancements

1. **Streaming Responses**: Real-time token streaming
2. **Fine-tuning**: Custom models for specific codebases
3. **Caching**: Response caching for common queries
4. **Batch Processing**: Analyze multiple files simultaneously
5. **Model Switching**: Dynamic model selection based on task
6. **Quantization Options**: Support for different quantization levels

## Support

For issues or questions:
1. Check logs: `docker logs llm-service`
2. Review health endpoint: `/health`
3. Verify model files exist
4. Check GPU availability: `nvidia-smi`

## References

- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)
- [GGUF Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Qwen Models](https://github.com/QwenLM/Qwen)
- [DeepSeek Models](https://github.com/deepseek-ai/DeepSeek-Coder)
