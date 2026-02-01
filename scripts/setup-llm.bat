@echo off
REM Setup script for LLM integration (Windows)

echo Setting up Local LLM Integration...

REM Check if models directory exists
if not exist "models" (
    echo Creating models directory...
    mkdir models
)

REM Check for model files
echo.
echo Checking for model files...

set MODELS=Qwen2.5-Coder-14B-Instruct-Q4_0.gguf DeepSeek-R1-Distill-Qwen-7B-Uncensored.i1-Q4_K_M.gguf Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf

for %%m in (%MODELS%) do (
    if exist "models\%%m" (
        echo [OK] Found: %%m
    ) else (
        echo [MISSING] %%m
    )
)

REM Check Python
echo.
echo Checking Python...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found
    
    REM Check llama-cpp-python
    python -c "import llama_cpp" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] llama-cpp-python installed
    ) else (
        echo [WARNING] llama-cpp-python not installed
        echo Installing llama-cpp-python...
        
        REM Check for CUDA
        nvidia-smi >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] NVIDIA GPU detected
            echo Installing with CUDA support...
            set CMAKE_ARGS=-DLLAMA_CUBLAS=on
            pip install llama-cpp-python
        ) else (
            echo [WARNING] No NVIDIA GPU detected
            echo Installing CPU-only version...
            pip install llama-cpp-python
        )
    )
) else (
    echo [ERROR] Python not found
    echo Please install Python 3.8 or later
    exit /b 1
)

REM Check GPU
echo.
echo Checking GPU...

nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] NVIDIA GPU detected
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo.
    echo Recommended configuration:
    echo   LLM_GPU_LAYERS=35
    echo   LLM_THREADS=8
) else (
    echo [WARNING] No NVIDIA GPU detected
    echo CPU-only mode will be used
    echo Recommended configuration:
    echo   LLM_GPU_LAYERS=0
    echo   LLM_THREADS=%NUMBER_OF_PROCESSORS%
)

REM Check Docker
echo.
echo Checking Docker...

docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker found
) else (
    echo [WARNING] Docker not found
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file...
    copy .env.example .env
    echo [OK] .env file created
    echo Please update the configuration in .env
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Ensure all model files are in the 'models\' directory
echo 2. Update .env with your configuration
echo 3. Start the LLM service:
echo    - Docker: docker-compose up llm-service
echo    - Local: cd services\llm-service ^&^& python -m uvicorn src.main:app
echo.
echo For more information, see: docs\LLM_INTEGRATION_GUIDE.md

pause
