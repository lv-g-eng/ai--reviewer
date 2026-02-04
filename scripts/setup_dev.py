#!/usr/bin/env python3
"""
Cross-platform development environment setup script.
Replaces: setup-dev.ps1 and setup-dev.sh
"""
import sys
import os
import subprocess
import shutil
from pathlib import Path


def run_command(cmd: list, cwd: Path = None, description: str = "", check: bool = True) -> bool:
    """Run a command and return success status."""
    if description:
        print(f"\n{description}...")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            print(f"  ✗ Failed")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed with exit code {e.returncode}")
        if e.stderr:
            print(f"  Error: {e.stderr[:200]}")
        return False
    except FileNotFoundError:
        print(f"  ✗ Command not found: {cmd[0]}")
        return False


def check_prerequisites():
    """Check if required tools are installed."""
    print("\n🔍 Checking prerequisites...")
    
    tools = {
        'node': ['node', '--version'],
        'npm': ['npm', '--version'],
        'python': ['python', '--version'],
        'docker': ['docker', '--version'],
        'git': ['git', '--version']
    }
    
    missing = []
    
    for tool, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"  ✓ {tool}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ✗ {tool}: not found")
            missing.append(tool)
    
    if missing:
        print(f"\n⚠️  Missing tools: {', '.join(missing)}")
        print("  Please install them before continuing")
        return False
    
    return True


def setup_backend():
    """Setup backend environment."""
    print("\n🐍 Setting up backend...")
    
    backend_dir = Path.cwd() / 'backend'
    
    if not backend_dir.exists():
        print(f"  ✗ Backend directory not found: {backend_dir}")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / 'venv'
    if not venv_dir.exists():
        if not run_command(
            [sys.executable, '-m', 'venv', 'venv'],
            cwd=backend_dir,
            description="  Creating virtual environment"
        ):
            return False
    else:
        print("  ✓ Virtual environment already exists")
    
    # Determine pip path
    if sys.platform == 'win32':
        pip_path = venv_dir / 'Scripts' / 'pip.exe'
    else:
        pip_path = venv_dir / 'bin' / 'pip'
    
    # Install dependencies
    if not run_command(
        [str(pip_path), 'install', '--no-cache-dir', '-r', 'requirements.txt'],
        cwd=backend_dir,
        description="  Installing Python dependencies"
    ):
        return False
    
    # Copy environment file if needed
    env_file = backend_dir / '.env'
    env_example = backend_dir / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  ✓ Created .env from .env.example")
        print("  ⚠️  Please edit backend/.env with your configuration")
    
    return True


def setup_frontend():
    """Setup frontend environment."""
    print("\n⚛️  Setting up frontend...")
    
    frontend_dir = Path.cwd() / 'frontend'
    
    if not frontend_dir.exists():
        print(f"  ✗ Frontend directory not found: {frontend_dir}")
        return False
    
    # Install dependencies
    if not run_command(
        ['npm', 'install'],
        cwd=frontend_dir,
        description="  Installing npm dependencies"
    ):
        return False
    
    # Copy environment file if needed
    env_file = frontend_dir / '.env.local'
    env_example = frontend_dir / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  ✓ Created .env.local from .env.example")
        print("  ⚠️  Please edit frontend/.env.local with your configuration")
    
    return True


def setup_docker():
    """Setup Docker services."""
    print("\n🐳 Setting up Docker services...")
    
    # Check if docker-compose.yml exists
    compose_file = Path.cwd() / 'docker-compose.yml'
    
    if not compose_file.exists():
        print(f"  ✗ docker-compose.yml not found")
        return False
    
    # Pull images
    if not run_command(
        ['docker-compose', 'pull'],
        description="  Pulling Docker images"
    ):
        return False
    
    print("  ℹ️  To start services, run: docker-compose up -d")
    
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("AI Code Review Platform - Development Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites check failed")
        return 1
    
    # Setup components
    success = True
    
    if not setup_backend():
        print("\n⚠️  Backend setup had issues")
        success = False
    
    if not setup_frontend():
        print("\n⚠️  Frontend setup had issues")
        success = False
    
    if not setup_docker():
        print("\n⚠️  Docker setup had issues")
        success = False
    
    # Print summary
    print("\n" + "=" * 60)
    if success:
        print("✓ Development environment setup complete!")
        print("\n📝 Next steps:")
        print("  1. Edit .env files with your configuration")
        print("  2. Start services: docker-compose up -d")
        print("  3. Run migrations: cd backend && alembic upgrade head")
        print("  4. Start backend: cd backend && uvicorn app.main:app --reload")
        print("  5. Start frontend: cd frontend && npm run dev")
    else:
        print("✗ Setup completed with some issues")
        print("  Please review the errors above and fix them")
    
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
