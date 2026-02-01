#!/bin/bash
# Setup script for LLM integration

set -e

echo "🚀 Setting up Local LLM Integration..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if models directory exists
if [ ! -d "models" ]; then
    echo -e "${YELLOW}⚠️  Models directory not found. Creating...${NC}"
    mkdir -p models
fi

# Check for model files
echo -e "\n${GREEN}📦 Checking for model files...${NC}"

MODELS=(
    "Qwen2.5-Coder-14B-Instruct-Q4_0.gguf"
    "DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf"
    "Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf"
)

MISSING_MODELS=()

for model in "${MODELS[@]}"; do
    if [ -f "models/$model" ]; then
        echo -e "${GREEN}✓${NC} Found: $model"
    else
        echo -e "${RED}✗${NC} Missing: $model"
        MISSING_MODELS+=("$model")
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  Missing models detected!${NC}"
    echo "Please download the following models and place them in the 'models/' directory:"
    for model in "${MISSING_MODELS[@]}"; do
        echo "  - $model"
    done
    echo ""
    echo "You can download models from:"
    echo "  - Hugging Face: https://huggingface.co/models"
    echo "  - TheBloke's GGUF models: https://huggingface.co/TheBloke"
    echo ""
fi

# Check Python dependencies
echo -e "\n${GREEN}🐍 Checking Python dependencies...${NC}"

if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 found"
    
    # Check if llama-cpp-python is installed
    if python3 -c "import llama_cpp" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} llama-cpp-python installed"
    else
        echo -e "${YELLOW}⚠️  llama-cpp-python not installed${NC}"
        echo "Installing llama-cpp-python..."
        
        # Check for CUDA
        if command -v nvidia-smi &> /dev/null; then
            echo -e "${GREEN}✓${NC} NVIDIA GPU detected, installing with CUDA support..."
            CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
        else
            echo -e "${YELLOW}⚠️  No NVIDIA GPU detected, installing CPU-only version...${NC}"
            pip install llama-cpp-python
        fi
    fi
else
    echo -e "${RED}✗${NC} Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check GPU availability
echo -e "\n${GREEN}🎮 Checking GPU availability...${NC}"

if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓${NC} NVIDIA GPU detected"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
    echo "Recommended configuration:"
    echo "  LLM_GPU_LAYERS=35"
    echo "  LLM_THREADS=8"
else
    echo -e "${YELLOW}⚠️  No NVIDIA GPU detected${NC}"
    echo "CPU-only mode will be used."
    echo "Recommended configuration:"
    echo "  LLM_GPU_LAYERS=0"
    echo "  LLM_THREADS=$(nproc)"
fi

# Check Docker
echo -e "\n${GREEN}🐳 Checking Docker...${NC}"

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker found"
    
    # Check for NVIDIA Docker runtime
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo -e "${GREEN}✓${NC} NVIDIA Docker runtime available"
    else
        echo -e "${YELLOW}⚠️  NVIDIA Docker runtime not available${NC}"
        echo "GPU acceleration in Docker will not work."
        echo "Install nvidia-docker2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not found${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${GREEN}📝 Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created from .env.example"
    echo "Please update the configuration in .env"
fi

# Summary
echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure all model files are in the 'models/' directory"
echo "2. Update .env with your configuration"
echo "3. Start the LLM service:"
echo "   - Docker: docker-compose up llm-service"
echo "   - Local: cd services/llm-service && python -m uvicorn src.main:app"
echo ""
echo "For more information, see: docs/LLM_INTEGRATION_GUIDE.md"
