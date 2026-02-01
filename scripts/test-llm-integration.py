#!/usr/bin/env python3
"""
Test script for LLM integration
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from app.services.llm_service import llm_service, ModelType
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and dependencies are installed")
    sys.exit(1)


async def test_initialization():
    """Test LLM service initialization"""
    print("🔧 Testing LLM service initialization...")
    try:
        await llm_service.initialize()
        print("✅ LLM service initialized")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_health_check():
    """Test health check"""
    print("\n🏥 Testing health check...")
    try:
        health = await llm_service.health_check()
        print(f"✅ Health check passed")
        print(f"   Initialized: {health['initialized']}")
        for model_type, status in health['models'].items():
            print(f"   {model_type}:")
            print(f"     - Configured: {status['configured']}")
            print(f"     - Exists: {status['exists']}")
            print(f"     - Loaded: {status['loaded']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


async def test_model_info():
    """Test getting model info"""
    print("\n📊 Testing model info...")
    try:
        for model_type in ModelType:
            info = await llm_service.get_model_info(model_type)
            print(f"✅ {model_type.value}:")
            print(f"   Path: {info.get('path', 'N/A')}")
            print(f"   Exists: {info.get('exists', False)}")
            print(f"   Loaded: {info.get('loaded', False)}")
        return True
    except Exception as e:
        print(f"❌ Model info failed: {e}")
        return False


async def test_code_analysis():
    """Test code analysis"""
    print("\n🔍 Testing code analysis...")
    
    test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""
    
    try:
        print("   Analyzing Python code...")
        result = await llm_service.analyze_code(
            code=test_code,
            language="python",
            analysis_type="review"
        )
        
        print("✅ Code analysis completed")
        print(f"   Severity: {result.get('severity', 'N/A')}")
        print(f"   Issues found: {len(result.get('issues', []))}")
        print(f"   Suggestions: {len(result.get('suggestions', []))}")
        
        if result.get('analysis'):
            print(f"\n   Analysis preview:")
            preview = result['analysis'][:200]
            print(f"   {preview}...")
        
        return True
    except Exception as e:
        print(f"❌ Code analysis failed: {e}")
        print(f"   This is expected if models are not loaded yet")
        return False


async def test_architecture_insights():
    """Test architecture insights"""
    print("\n🏗️  Testing architecture insights...")
    
    architecture_data = {
        "components": ["API Gateway", "Auth Service", "Database"],
        "dependencies": [
            {"from": "API Gateway", "to": "Auth Service"},
            {"from": "Auth Service", "to": "Database"}
        ],
        "patterns": ["Microservices", "API Gateway Pattern"]
    }
    
    try:
        print("   Generating architecture insights...")
        result = await llm_service.generate_architecture_insights(architecture_data)
        
        print("✅ Architecture insights generated")
        if result.get('insights'):
            preview = result['insights'][:200]
            print(f"\n   Insights preview:")
            print(f"   {preview}...")
        
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Architecture insights failed: {e}")
        print(f"   This is expected if models are not loaded yet")
        return False


async def test_model_loading():
    """Test model loading"""
    print("\n📦 Testing model loading...")
    
    try:
        print("   Loading code review model...")
        success = await llm_service.load_model(ModelType.CODE_REVIEW)
        
        if success:
            print("✅ Model loaded successfully")
            print("   Note: First load takes 30-60 seconds")
            return True
        else:
            print("❌ Model loading failed")
            return False
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 LLM Integration Test Suite")
    print("=" * 60)
    
    # Check configuration
    print(f"\n⚙️  Configuration:")
    print(f"   Models Directory: {settings.MODELS_DIR}")
    print(f"   LLM Enabled: {settings.LLM_ENABLED}")
    print(f"   GPU Layers: {settings.LLM_GPU_LAYERS}")
    print(f"   Threads: {settings.LLM_THREADS}")
    
    # Check if models directory exists
    models_dir = Path(settings.MODELS_DIR)
    if not models_dir.exists():
        print(f"\n❌ Models directory not found: {models_dir}")
        print("   Please create the directory and add model files")
        return
    
    print(f"\n📁 Models directory: {models_dir.absolute()}")
    model_files = list(models_dir.glob("*.gguf"))
    print(f"   Found {len(model_files)} GGUF files:")
    for model_file in model_files:
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"   - {model_file.name} ({size_mb:.1f} MB)")
    
    if not model_files:
        print("\n⚠️  No GGUF model files found!")
        print("   Please add model files to the models/ directory")
        print("   See docs/LLM_INTEGRATION_GUIDE.md for details")
    
    # Run tests
    results = []
    
    results.append(("Initialization", await test_initialization()))
    results.append(("Health Check", await test_health_check()))
    results.append(("Model Info", await test_model_info()))
    
    # Only run inference tests if models exist
    if model_files:
        print("\n⚠️  Inference tests will load models (may take time)")
        response = input("   Run inference tests? (y/N): ")
        
        if response.lower() == 'y':
            results.append(("Model Loading", await test_model_loading()))
            results.append(("Code Analysis", await test_code_analysis()))
            results.append(("Architecture Insights", await test_architecture_insights()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! LLM integration is working correctly.")
    elif passed > 0:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ All tests failed. Please check your configuration.")
    
    print("\n💡 Next steps:")
    print("   1. Ensure model files are in the models/ directory")
    print("   2. Configure .env with LLM settings")
    print("   3. Start the LLM service: docker-compose up llm-service")
    print("   4. See docs/LLM_QUICK_START.md for more information")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
