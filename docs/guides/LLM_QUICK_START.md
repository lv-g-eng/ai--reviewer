# LLM Integration - Quick Start

## 🚀 5-Minute Setup

### 1. Verify Models

Your models are already in place:
```
models/
├── Qwen2.5-Coder-14B-Instruct-Q4_0.gguf ✓
├── DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf ✓
└── Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf ✓
```

### 2. Configure Environment

Add to your `.env`:
```env
# Local LLM
MODELS_DIR=models
LLM_ENABLED=true
LLM_GPU_LAYERS=35  # 0 for CPU-only
LLM_THREADS=8
```

### 3. Start Services

**Option A: Docker (Recommended)**
```bash
docker-compose up llm-service
```

**Option B: Local Development**
```bash
# Install dependencies
cd backend
pip install -r requirements-llm.txt

# Start backend with LLM
python -m uvicorn app.main:app --reload
```

### 4. Test It

```bash
# Health check
curl http://localhost:8000/health

# Analyze code
curl -X POST http://localhost:8000/api/v1/llm/analyze-code \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "code": "def hello(): print(\"hi\")",
    "language": "python",
    "analysis_type": "review"
  }'
```

## 📊 Model Selection Guide

| Task | Model | Best For |
|------|-------|----------|
| Code Review | `code_review` | Bug detection, security, quality |
| Architecture | `general` | System design, patterns |
| Documentation | `general` | Explanations, summaries |
| Future: Diagrams | `vision` | Visual analysis |

## ⚡ Performance Tips

### GPU Mode (Fast)
```env
LLM_GPU_LAYERS=35
```
- Speed: ~50-100 tokens/sec
- Requires: NVIDIA GPU, 8GB+ VRAM

### CPU Mode (Slower)
```env
LLM_GPU_LAYERS=0
LLM_THREADS=8
```
- Speed: ~5-10 tokens/sec
- Requires: 16GB+ RAM

## 🔧 Common Issues

### "Model not found"
```bash
# Check models directory
ls models/

# Verify paths in .env
echo $MODELS_DIR
```

### "Out of memory"
```env
# Reduce GPU layers
LLM_GPU_LAYERS=20  # or 10, or 0

# Or use CPU mode
LLM_GPU_LAYERS=0
```

### "Service unavailable"
```bash
# Check if running
docker ps | grep llm-service

# Check logs
docker logs llm-service

# Restart
docker-compose restart llm-service
```

## 📚 API Examples

### Python
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/llm/analyze-code",
        json={
            "code": "function hello() { console.log('hi'); }",
            "language": "javascript",
            "analysis_type": "security"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
```

### TypeScript
```typescript
import { llmClient } from './llm-client';

const result = await llmClient.analyzeCode({
  code: 'SELECT * FROM users WHERE id = ' + userId,
  language: 'sql',
  analysis_type: 'security'
});

console.log(result.analysis.issues);
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/llm/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Explain SOLID principles",
    "model_type": "general",
    "max_tokens": 512
  }'
```

## 🎯 Use Cases

### 1. Code Review
```typescript
const review = await llmClient.analyzeCode({
  code: pullRequestCode,
  language: 'typescript',
  analysis_type: 'review'
});

// Get issues and suggestions
console.log(review.analysis.issues);
console.log(review.analysis.suggestions);
```

### 2. Security Scan
```typescript
const security = await llmClient.analyzeCode({
  code: userInputHandler,
  language: 'python',
  analysis_type: 'security'
});

// Check severity
if (security.analysis.severity === 'high') {
  alert('Critical security issues found!');
}
```

### 3. Architecture Analysis
```typescript
const insights = await llmClient.generate({
  prompt: `Analyze this architecture:
    - API Gateway
    - Auth Service
    - Database
    
    Identify scalability concerns.`,
  model_type: 'general'
});
```

## 📈 Monitoring

### Check Model Status
```bash
curl http://localhost:8000/api/v1/llm/models
```

### Load/Unload Models
```bash
# Load for faster first request
curl -X POST http://localhost:8000/api/v1/llm/models/code_review/load

# Unload to free memory
curl -X POST http://localhost:8000/api/v1/llm/models/code_review/unload
```

### Health Check
```bash
# Backend
curl http://localhost:8000/api/v1/llm/health

# LLM Service
curl http://localhost:8000/health
```

## 🔗 Next Steps

1. **Read Full Guide**: [LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)
2. **Integrate with Services**: Update code-review-engine and architecture-analyzer
3. **Optimize Performance**: Tune GPU layers and context size
4. **Monitor Usage**: Set up logging and metrics

## 💡 Pro Tips

1. **Lazy Loading**: Models load on first use (~30-60s delay)
2. **Prompt Engineering**: Better prompts = better results
3. **Context Size**: Larger context = more memory
4. **Batch Processing**: Analyze multiple files together
5. **Caching**: Cache common queries to save time

## 🆘 Need Help?

- **Documentation**: `docs/LLM_INTEGRATION_GUIDE.md`
- **Logs**: `docker logs llm-service`
- **Health**: `curl http://localhost:8000/health`
- **GPU Check**: `nvidia-smi`

## 🎉 You're Ready!

Your local LLM integration is set up. Start analyzing code with AI-powered insights!
