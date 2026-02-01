# LLM Service

Dedicated microservice for local Large Language Model inference using GGUF models.

## Features

- **Local Inference**: Run LLMs locally without external API calls
- **GPU Acceleration**: CUDA support for fast inference
- **Multiple Models**: Support for code review, general, and vision models
- **REST API**: Simple HTTP API for integration
- **Lazy Loading**: Models load on-demand to save memory
- **Health Monitoring**: Built-in health checks and status endpoints

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MODELS_DIR=../../models
export LLM_GPU_LAYERS=35
export LLM_THREADS=8

# Run service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build
docker build -t llm-service -f Dockerfile ../..

# Run with GPU
docker run --gpus all \
  -v $(pwd)/../../models:/app/models:ro \
  -p 8000:8000 \
  -e LLM_GPU_LAYERS=35 \
  llm-service

# Run CPU-only
docker run \
  -v $(pwd)/../../models:/app/models:ro \
  -p 8000:8000 \
  -e LLM_GPU_LAYERS=0 \
  llm-service
```

### Docker Compose

```bash
# Start all services including LLM
docker-compose up llm-service

# Or start everything
docker-compose up
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Generate Text
```bash
POST /generate
{
  "prompt": "Explain dependency injection",
  "model_type": "general",
  "temperature": 0.3,
  "max_tokens": 512
}
```

### Analyze Code
```bash
POST /analyze/code
{
  "code": "def hello(): print('hi')",
  "language": "python",
  "analysis_type": "review"
}
```

### Analyze Architecture
```bash
POST /analyze/architecture
{
  "components": ["API", "Database"],
  "dependencies": [{"from": "API", "to": "Database"}],
  "patterns": ["REST"]
}
```

### List Models
```bash
GET /models
```

### Load/Unload Models
```bash
POST /models/{model_type}/load
POST /models/{model_type}/unload
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | `llm-service` | Service name |
| `PORT` | `8000` | HTTP port |
| `MODELS_DIR` | `/app/models` | Models directory |
| `LLM_THREADS` | `8` | CPU threads |
| `LLM_GPU_LAYERS` | `35` | GPU layers (0=CPU) |
| `LOG_LEVEL` | `INFO` | Logging level |

### Model Configuration

Models are configured in `src/llm_manager.py`:

```python
ModelType.CODE_REVIEW: LLMConfig(
    model_path="Qwen2.5-Coder-14B-Instruct-Q4_0.gguf",
    n_ctx=8192,
    n_gpu_layers=35,
    temperature=0.1,
)
```

## Models

Place GGUF model files in the `models/` directory:

- `Qwen2.5-Coder-14B-Instruct-Q4_0.gguf` - Code review
- `DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf` - General
- `Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf` - Vision

## Performance

### GPU Mode (Recommended)

- **Requirements**: NVIDIA GPU, CUDA 12.1+, 8GB+ VRAM
- **Speed**: ~50-100 tokens/second
- **Configuration**: `LLM_GPU_LAYERS=35`

### CPU Mode

- **Requirements**: 16GB+ RAM, multi-core CPU
- **Speed**: ~5-10 tokens/second
- **Configuration**: `LLM_GPU_LAYERS=0`

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "ai-service",
  "health": {
    "initialized": true,
    "models": {
      "code_review": {
        "loaded": true,
        "configured": true,
        "exists": true
      }
    }
  }
}
```

### Logs

```bash
# Docker logs
docker logs llm-service

# Follow logs
docker logs -f llm-service
```

## Troubleshooting

### Model Not Loading

1. Check model file exists: `ls models/`
2. Check file permissions
3. Verify MODELS_DIR path
4. Check logs for errors

### Out of Memory

1. Reduce `LLM_GPU_LAYERS`
2. Reduce context size in config
3. Use smaller quantization
4. Unload unused models

### Slow Performance

**GPU:**
- Increase `LLM_GPU_LAYERS`
- Check GPU usage: `nvidia-smi`
- Verify CUDA installation

**CPU:**
- Increase `LLM_THREADS`
- Use smaller models
- Reduce max_tokens

## Development

### Project Structure

```
services/ai-service/
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── llm_manager.py   # Model management
│   └── config.py        # Configuration
├── Dockerfile
├── requirements.txt
└── README.md
```

### Adding New Models

1. Add model file to `models/`
2. Add configuration in `llm_manager.py`:
```python
ModelType.NEW_MODEL: LLMConfig(
    model_path="new-model.gguf",
    n_ctx=4096,
    ...
)
```
3. Update enum in `llm_manager.py`

## Integration

### Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/analyze/code",
        json={
            "code": "def hello(): pass",
            "language": "python",
            "analysis_type": "review"
        }
    )
    result = response.json()
```

### TypeScript

```typescript
import { llmClient } from './llm-client';

const result = await llmClient.analyzeCode({
  code: 'function hello() {}',
  language: 'javascript',
  analysis_type: 'review'
});
```

### cURL

```bash
curl -X POST http://localhost:8000/analyze/code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): pass",
    "language": "python",
    "analysis_type": "review"
  }'
```

## License

See main project LICENSE file.
