#!/bin/bash

# Comprehensive Project Restructuring Script
# This script reorganizes the project to reduce redundancy and improve maintainability

echo "🚀 Starting comprehensive project restructuring..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create new directory structure
create_directory_structure() {
    print_status "Creating new directory structure..."

    mkdir -p restructured/{
        # Core application directories
        backend,
        frontend,

        # Documentation
        docs/{
            api,
            deployment,
            user,
            development
        },

        # Configuration and scripts
        config/{
            docker,
            ci-cd,
            monitoring,
            security
        },

        scripts/{
            build,
            deploy,
            test,
            maintenance
        },

        # Infrastructure
        infrastructure/{
            docker,
            kubernetes,
            terraform,
            monitoring
        },

        # Testing
        tests/{
            unit,
            integration,
            e2e,
            performance
        },

        # Tools and utilities
        tools/{
            development,
            deployment,
            monitoring
        }
    }

    print_success "Directory structure created"
}

# Move and organize documentation files
organize_documentation() {
    print_status "Organizing documentation files..."

    # API documentation
    cp docs/*.md restructured/docs/api/ 2>/dev/null || true
    cp backend/docs/*.md restructured/docs/api/ 2>/dev/null || true

    # Deployment documentation
    cp DEPLOYMENT.md restructured/docs/deployment/ 2>/dev/null || true
    cp QUICK_START_DOCKER.md restructured/docs/deployment/ 2>/dev/null || true
    cp QUICK_START_PRODUCTION*.md restructured/docs/deployment/ 2>/dev/null || true
    cp PRODUCTION_*.md restructured/docs/deployment/ 2>/dev/null || true
    cp docker-compose*.yml restructured/infrastructure/docker/ 2>/dev/null || true

    # User documentation
    cp README.md restructured/docs/user/ 2>/dev/null || true
    cp QUICK_START.md restructured/docs/user/ 2>/dev/null || true
    cp TRANSFER_OF_KNOWLEDGE.md restructured/docs/user/ 2>/dev/null || true

    # Development documentation
    cp *.md restructured/docs/development/ 2>/dev/null || true

    print_success "Documentation organized"
}

# Organize configuration files
organize_configuration() {
    print_status "Organizing configuration files..."

    # Docker configurations
    cp docker-compose*.yml restructured/infrastructure/docker/ 2>/dev/null || true
    cp docker-compose*.yaml restructured/infrastructure/docker/ 2>/dev/null || true
    cp Dockerfile* restructured/infrastructure/docker/ 2>/dev/null || true
    cp docker/* restructured/infrastructure/docker/ 2>/dev/null || true
    cp nginx/* restructured/infrastructure/docker/ 2>/dev/null || true

    # CI/CD configurations
    cp .github/* restructured/config/ci-cd/ 2>/dev/null || true
    cp renovate.json restructured/config/ci-cd/ 2>/dev/null || true

    # Monitoring configurations
    cp monitoring/* restructured/infrastructure/monitoring/ 2>/dev/null || true
    cp GITHUB_OAUTH_SETUP.md restructured/config/security/ 2>/dev/null || true
    cp SSL_SETUP.md restructured/config/security/ 2>/dev/null || true

    print_success "Configuration files organized"
}

# Organize scripts
organize_scripts() {
    print_status "Organizing scripts..."

    # Build scripts
    cp scripts/* restructured/scripts/ 2>/dev/null || true
    cp package.json restructured/scripts/build/ 2>/dev/null || true
    cp frontend/package.json restructured/scripts/build/ 2>/dev/null || true
    cp backend/requirements.txt restructured/scripts/build/ 2>/dev/null || true

    # Deployment scripts
    cp terraform/* restructured/infrastructure/terraform/ 2>/dev/null || true
    cp k8s/* restructured/infrastructure/kubernetes/ 2>/dev/null || true

    print_success "Scripts organized"
}

# Organize testing files
organize_testing() {
    print_status "Organizing testing files..."

    cp tests/* restructured/tests/unit/ 2>/dev/null || true
    cp frontend/__tests__/* restructured/tests/unit/ 2>/dev/null || true
    cp backend/tests/* restructured/tests/unit/ 2>/dev/null || true
    cp test_* restructured/tests/integration/ 2>/dev/null || true
    cp jest.config.js restructured/tests/unit/ 2>/dev/null || true
    cp load_testing/* restructured/tests/performance/ 2>/dev/null || true

    print_success "Testing files organized"
}

# Move core application files
move_core_applications() {
    print_status "Moving core application files..."

    # Backend
    cp -r backend/* restructured/backend/ 2>/dev/null || true

    # Frontend
    cp -r frontend/* restructured/frontend/ 2>/dev/null || true

    print_success "Core applications moved"
}

# Create cleanup script
create_cleanup_script() {
    print_status "Creating cleanup script..."

    cat > restructured/cleanup.sh << 'EOF'
#!/bin/bash

echo "🧹 Cleaning up redundant files..."

# Remove redundant documentation files
find . -name "*.md" -type f | grep -E "(CLEANUP|PHASE|CHECKPOINT|VERIFICATION|AUDIT|DELIVERY)" | xargs rm -f

# Remove redundant backup files
find . -name "*.backup" -o -name "*~" -o -name ".DS_Store" | xargs rm -f

# Remove empty directories
find . -type d -empty -delete

# Remove redundant configuration files
find . -name ".*" -type f | grep -v -E "(\.gitignore|\.dockerignore|\.env|\.prettierrc|\.eslintrc)" | xargs rm -f

echo "✅ Cleanup completed"
EOF

    chmod +x restructured/cleanup.sh

    print_success "Cleanup script created"
}

# Create new root files
create_root_files() {
    print_status "Creating new root configuration files..."

    # Create new package.json
    cat > restructured/package.json << 'EOF'
{
  "name": "ai-code-review-platform",
  "version": "1.0.0",
  "description": "AI-powered code review and architecture analysis platform",
  "private": true,
  "workspaces": [
    "frontend",
    "backend"
  ],
  "scripts": {
    "dev": "npm run dev --workspace=frontend",
    "build": "npm run build --workspace=frontend && npm run build --workspace=backend",
    "start": "npm run start --workspace=frontend",
    "test": "npm run test --workspace=frontend && npm run test --workspace=backend",
    "lint": "npm run lint --workspace=frontend",
    "docker:build": "./scripts/deploy/docker-build.sh",
    "docker:up": "./scripts/deploy/docker-up.sh",
    "docker:down": "./scripts/deploy/docker-down.sh"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
EOF

    # Create new README.md
    cat > restructured/README.md << 'EOF'
# AI-Based Quality Check on Project Code and Architecture

A comprehensive platform for automated code review and architecture analysis using AI.

## Quick Start

### Development
```bash
npm install
npm run dev
```

### Production
```bash
npm run docker:build
npm run docker:up
```

## Project Structure

```
restructured/
├── backend/           # FastAPI backend application
├── frontend/          # Next.js frontend application
├── docs/             # Documentation
│   ├── api/          # API documentation
│   ├── deployment/   # Deployment guides
│   ├── user/         # User guides
│   └── development/  # Development docs
├── config/           # Configuration files
├── scripts/          # Build and deployment scripts
├── infrastructure/   # Docker, K8s, Terraform configs
├── tests/            # Test suites
└── tools/            # Development and deployment tools
```

## Documentation

- [API Documentation](./docs/api/)
- [Deployment Guide](./docs/deployment/)
- [User Guide](./docs/user/)
- [Development Guide](./docs/development/)

## Contributing

See [CONTRIBUTING.md](./docs/development/CONTRIBUTING.md) for development guidelines.
EOF

    # Create new .gitignore
    cat > restructured/.gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Next.js
.next/
out/
build/
dist/

# Production builds
restructured/
!restructured/package.json
!restructured/README.md

# Environment variables
.env*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/
.nyc_output/

# Temporary files
*.tmp
*.temp
EOF

    print_success "Root files created"
}

# Main execution
main() {
    echo "🔄 Starting comprehensive project restructuring..."
    echo "==============================================="

    create_directory_structure
    organize_documentation
    organize_configuration
    organize_scripts
    organize_testing
    move_core_applications
    create_cleanup_script
    create_root_files

    echo ""
    echo "🎉 Project restructuring completed!"
    echo "==================================="
    echo ""
    echo "New structure created in: restructured/"
    echo ""
    echo "Next steps:"
    echo "1. Review the restructured directory"
    echo "2. Test the applications: cd restructured && npm install && npm run dev"
    echo "3. Run cleanup: ./cleanup.sh"
    echo "4. Update CI/CD pipelines to use new structure"
    echo ""
    echo "Original files are preserved for rollback if needed."
}

# Run main function
main "$@"
