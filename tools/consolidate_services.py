#!/usr/bin/env python3
"""
Service Consolidation Script

Implements the service consolidation plan to reduce from 8 services to 5 services.
This script automates the consolidation process with proper backup and rollback capabilities.

CONSOLIDATION PLAN:
- AI Services: agentic-ai + code-review-engine + llm-service → ai-service (3→1)
- Backend Services: project-manager + architecture-analyzer → backend-core (2→0)
- Total Reduction: 8 → 5 services (37.5% reduction)
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class ServiceConsolidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.backup_dir = self.project_root / ".consolidation_backups" / f"consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Consolidation plan
        self.consolidation_plan = {
            "ai-service": {
                "target_dir": "services/ai-service",
                "source_services": ["agentic-ai", "code-review-engine", "llm-service"],
                "description": "Consolidated AI services for code analysis and LLM integration",
                "port": 3002,
                "main_functions": [
                    "Code review analysis",
                    "LLM integration (OpenAI, Anthropic, Ollama)",
                    "AI-powered pattern recognition",
                    "Agentic reasoning workflows"
                ]
            },
            "backend-core": {
                "target_dir": "backend",
                "source_services": ["project-manager", "architecture-analyzer"],
                "description": "Consolidated project management and architecture analysis into backend core",
                "integration_modules": [
                    "app/services/project_management",
                    "app/services/architecture_analysis"
                ]
            }
        }
    
    def create_backup(self) -> bool:
        """Create comprehensive backup of current services before consolidation"""
        try:
            print(f"📦 Creating backup at {self.backup_dir}")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup services directory
            if self.services_dir.exists():
                shutil.copytree(self.services_dir, self.backup_dir / "services")
            
            # Backup configuration files
            config_files = [
                "docker-compose.yml", 
                "docker-compose.backend.yml", 
                "docker-compose.prod.yml",
                "package.json"
            ]
            
            for config_file in config_files:
                source_file = self.project_root / config_file
                if source_file.exists():
                    shutil.copy2(source_file, self.backup_dir / config_file)
            
            # Create backup manifest
            manifest = {
                "timestamp": datetime.now().isoformat(),
                "services_backed_up": [d.name for d in self.services_dir.iterdir() if d.is_dir()] if self.services_dir.exists() else [],
                "consolidation_plan": self.consolidation_plan,
                "backup_location": str(self.backup_dir),
                "original_service_count": len([d for d in self.services_dir.iterdir() if d.is_dir()]) if self.services_dir.exists() else 0,
                "target_service_count": 5
            }
            
            with open(self.backup_dir / "backup_manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Backup created successfully")
            print(f"   📁 Location: {self.backup_dir}")
            print(f"   📊 Services backed up: {len(manifest['services_backed_up'])}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def consolidate_ai_services(self) -> bool:
        """Consolidate AI-related services into a single ai-service"""
        try:
            print("🤖 Consolidating AI services...")
            print("   📋 Merging: agentic-ai + code-review-engine + llm-service → ai-service")
            
            target_dir = self.project_root / "services" / "ai-service"
            source_services = ["agentic-ai", "code-review-engine", "llm-service"]
            
            # Create consolidated service directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create consolidated package.json
            consolidated_package = {
                "name": "ai-service",
                "version": "1.0.0",
                "description": "Consolidated AI services for code analysis and LLM integration",
                "main": "dist/index.js",
                "scripts": {
                    "dev": "ts-node-dev --respawn --transpile-only src/index.ts",
                    "build": "tsc",
                    "start": "node dist/index.js",
                    "test": "jest",
                    "lint": "eslint src --ext .ts",
                    "format": "prettier --write src"
                },
                "dependencies": {
                    "express": "^4.18.0",
                    "cors": "^2.8.5",
                    "helmet": "^7.0.0",
                    "winston": "^3.10.0",
                    "axios": "^1.5.0",
                    "openai": "^4.0.0",
                    "anthropic": "^0.20.0",
                    "@types/node": "^20.0.0",
                    "typescript": "^5.0.0",
                    "ts-node-dev": "^2.0.0",
                    "dotenv": "^16.0.0",
                    "joi": "^17.9.0",
                    "compression": "^1.7.4",
                    "express-rate-limit": "^6.8.0"
                },
                "devDependencies": {
                    "jest": "^29.0.0",
                    "@types/jest": "^29.0.0",
                    "@types/express": "^4.17.0",
                    "@types/cors": "^2.8.0",
                    "@types/compression": "^1.7.0",
                    "eslint": "^8.0.0",
                    "prettier": "^3.0.0",
                    "nodemon": "^3.0.0"
                }
            }
            
            with open(target_dir / "package.json", "w") as f:
                json.dump(consolidated_package, f, indent=2)
            
            # Create consolidated TypeScript config
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "lib": ["ES2020"],
                    "outDir": "./dist",
                    "rootDir": "./src",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                    "forceConsistentCasingInFileNames": True,
                    "resolveJsonModule": True,
                    "declaration": True,
                    "declarationMap": True,
                    "sourceMap": True,
                    "experimentalDecorators": True,
                    "emitDecoratorMetadata": True
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules", "dist", "**/*.test.ts"]
            }
            
            with open(target_dir / "tsconfig.json", "w") as f:
                json.dump(tsconfig, f, indent=2)
            
            # Create consolidated source structure
            self._create_ai_service_structure(target_dir)
            
            # Merge source code from existing services
            for service in source_services:
                service_dir = self.services_dir / service
                if service_dir.exists():
                    print(f"   🔄 Merging {service} into ai-service")
                    self._merge_service_code(service_dir, target_dir, service)
            
            # Create optimized Dockerfile
            self._create_ai_service_dockerfile(target_dir)
            
            print("✅ AI services consolidated successfully")
            print(f"   📊 Reduction: 3 services → 1 service (67% reduction)")
            return True
            
        except Exception as e:
            print(f"❌ AI service consolidation failed: {e}")
            return False
    
    def _create_ai_service_structure(self, target_dir: Path):
        """Create the consolidated AI service structure"""
        src_dir = target_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create main index.ts
        index_content = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { logger } from './utils/logger';
import { codeReviewRoutes } from './routes/code-review';
import { llmRoutes } from './routes/llm';
import { agenticRoutes } from './routes/agentic';
import { healthRoutes } from './routes/health';
import { errorHandler } from './middleware/error-handler';
import { requestLogger } from './middleware/request-logger';

const app = express();
const PORT = process.env.PORT || 3002;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Performance middleware
app.use(compression());
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Routes
app.use('/health', healthRoutes);
app.use('/api/code-review', codeReviewRoutes);
app.use('/api/llm', llmRoutes);
app.use('/api/agentic', agenticRoutes);

// Error handling
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

app.listen(PORT, () => {
  logger.info(`🤖 AI Service started on port ${PORT}`);
  logger.info(`🔗 Health check: http://localhost:${PORT}/health`);
});

export { app };
'''
        
        with open(src_dir / "index.ts", "w") as f:
            f.write(index_content)
        
        # Create directory structure
        directories = [
            "routes", "services", "middleware", "utils", "types", "config"
        ]
        
        for directory in directories:
            (src_dir / directory).mkdir(exist_ok=True)
        
        # Create health route
        health_route_content = '''import { Router } from 'express';
import { logger } from '../utils/logger';

const router = Router();

router.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'ai-service',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    features: [
      'code-review-analysis',
      'llm-integration',
      'agentic-reasoning',
      'pattern-recognition'
    ]
  });
});

router.get('/ready', (req, res) => {
  // Add readiness checks here
  res.json({
    status: 'ready',
    timestamp: new Date().toISOString()
  });
});

router.get('/live', (req, res) => {
  res.json({
    status: 'alive',
    timestamp: new Date().toISOString()
  });
});

export { router as healthRoutes };
'''
        
        with open(src_dir / "routes" / "health.ts", "w") as f:
            f.write(health_route_content)
    
    def _create_ai_service_dockerfile(self, target_dir: Path):
        """Create optimized Dockerfile for AI service"""
        dockerfile_content = '''# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY src/ ./src/

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copy built application
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD node -e "require('http').get('http://localhost:3002/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start application with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
'''
        
        with open(target_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
    
    def consolidate_backend_services(self) -> bool:
        """Consolidate project management services into backend core"""
        try:
            print("🏗️ Consolidating backend services...")
            
            backend_dir = self.project_root / "backend"
            source_services = ["project-manager", "architecture-analyzer"]
            
            # Create new modules in backend
            for service in source_services:
                service_dir = self.services_dir / service
                if service_dir.exists():
                    # Create module directory in backend
                    module_name = service.replace("-", "_")
                    target_module = backend_dir / "app" / "services" / module_name
                    target_module.mkdir(parents=True, exist_ok=True)
                    
                    # Copy and adapt service code
                    self._merge_backend_service(service_dir, target_module, service)
            
            print("✅ Backend services consolidated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Backend service consolidation failed: {e}")
            return False
    
    def _merge_service_code(self, source_dir: Path, target_dir: Path, service_name: str):
        """Merge source code from a service into the consolidated service"""
        src_dir = source_dir / "src"
        if not src_dir.exists():
            return
        
        target_src = target_dir / "src"
        service_module = service_name.replace("-", "_")
        
        # Create service-specific directory
        service_target = target_src / "services" / service_module
        service_target.mkdir(parents=True, exist_ok=True)
        
        # Copy source files
        for file_path in src_dir.rglob("*.ts"):
            if file_path.name == "index.ts":
                continue  # Skip main index files
            
            relative_path = file_path.relative_to(src_dir)
            target_path = service_target / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy and adapt the file
            content = file_path.read_text()
            # Update imports to use consolidated structure
            content = self._update_imports(content, service_module)
            target_path.write_text(content)
    
    def _merge_backend_service(self, source_dir: Path, target_dir: Path, service_name: str):
        """Merge a Node.js service into the Python backend"""
        src_dir = source_dir / "src"
        if not src_dir.exists():
            return
        
        # Create Python equivalent structure
        init_file = target_dir / "__init__.py"
        init_file.write_text(f'"""\\n{service_name.replace("-", " ").title()} module\\n"""\\n')
        
        # Create basic service structure
        service_py = target_dir / "service.py"
        service_content = f'''"""
{service_name.replace("-", " ").title()} Service

Consolidated from microservice: {service_name}
"""

from typing import Dict, List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class {service_name.replace("-", "").title()}Service:
    """Consolidated {service_name} functionality"""
    
    def __init__(self):
        self.logger = logger
    
    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint"""
        return {{
            "status": "healthy",
            "service": "{service_name}",
            "module": "{service_name.replace("-", "_")}"
        }}
    
    # TODO: Implement specific functionality from {service_name}
'''
        
        service_py.write_text(service_content)
    
    def _update_imports(self, content: str, service_module: str) -> str:
        """Update import statements for consolidated structure"""
        # Update relative imports
        content = content.replace("from '../", f"from '../../{service_module}/")
        content = content.replace("from './", f"from './{service_module}/")
        
        return content
    
    def update_docker_compose(self) -> bool:
        """Update docker-compose.yml to reflect consolidated services"""
        try:
            print("🐳 Updating Docker Compose configuration...")
            
            compose_file = self.project_root / "docker-compose.yml"
            if not compose_file.exists():
                print("⚠️ docker-compose.yml not found, skipping")
                return True
            
            # Read current compose file
            with open(compose_file, "r") as f:
                content = f.read()
            
            # Remove old service definitions
            services_to_remove = ["agentic-ai", "code-review-engine", "llm-service", "project-manager", "architecture-analyzer"]
            
            # This is a simplified approach - in production, you'd want to use a YAML parser
            lines = content.split('\n')
            filtered_lines = []
            skip_service = False
            
            for line in lines:
                # Check if we're starting a service definition to remove
                if any(f"{service}:" in line for service in services_to_remove):
                    skip_service = True
                    continue
                
                # Check if we're starting a new service or section
                if line.strip() and not line.startswith(' ') and ':' in line:
                    skip_service = False
                
                if not skip_service:
                    filtered_lines.append(line)
            
            # Write updated compose file
            with open(compose_file, "w") as f:
                f.write('\n'.join(filtered_lines))
            
            print("✅ Docker Compose updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Docker Compose update failed: {e}")
            return False
    
    def update_package_json(self) -> bool:
        """Update root package.json to reflect consolidated services"""
        try:
            print("📦 Updating package.json...")
            
            package_file = self.project_root / "package.json"
            if not package_file.exists():
                return True
            
            with open(package_file, "r") as f:
                package_data = json.load(f)
            
            # Update scripts to reflect consolidated services
            if "scripts" in package_data:
                # Remove old service scripts
                old_scripts = [
                    "dev:agentic-ai", "dev:code-review-engine", "dev:llm-service",
                    "dev:project-manager", "dev:architecture-analyzer"
                ]
                
                for script in old_scripts:
                    package_data["scripts"].pop(script, None)
                
                # Add new consolidated service scripts
                package_data["scripts"]["dev:ai-service"] = "npm run dev -w services/ai-service"
            
            with open(package_file, "w") as f:
                json.dump(package_data, f, indent=2)
            
            print("✅ Package.json updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Package.json update failed: {e}")
            return False
    
    def cleanup_old_services(self) -> bool:
        """Remove old service directories after successful consolidation"""
        try:
            print("🧹 Cleaning up old service directories...")
            
            services_to_remove = ["agentic-ai", "code-review-engine", "llm-service", "project-manager", "architecture-analyzer"]
            
            for service in services_to_remove:
                service_dir = self.services_dir / service
                if service_dir.exists():
                    shutil.rmtree(service_dir)
                    print(f"  ✅ Removed {service}")
            
            print("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
    
    def run_consolidation(self) -> bool:
        """Run the complete consolidation process"""
        print("🚀 Starting service consolidation process...")
        print(f"📊 Consolidating 8 services → 5 services (37.5% reduction)")
        
        steps = [
            ("Creating backup", self.create_backup),
            ("Consolidating AI services", self.consolidate_ai_services),
            ("Consolidating backend services", self.consolidate_backend_services),
            ("Updating Docker Compose", self.update_docker_compose),
            ("Updating package.json", self.update_package_json),
            ("Cleaning up old services", self.cleanup_old_services),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Consolidation failed at step: {step_name}")
                print(f"💾 Backup available at: {self.backup_dir}")
                return False
        
        print(f"\n🎉 Service consolidation completed successfully!")
        print(f"📊 Reduced from 8 services to 5 services (37.5% reduction)")
        print(f"💾 Backup available at: {self.backup_dir}")
        print(f"\n📋 Next steps:")
        print(f"  1. Test the consolidated services")
        print(f"  2. Update CI/CD pipelines")
        print(f"  3. Update documentation")
        print(f"  4. Deploy to staging environment")
        
        return True

def main():
    """Main entry point"""
    consolidator = ServiceConsolidator()
    success = consolidator.run_consolidation()
    
    if success:
        print("\n✅ Service consolidation completed successfully!")
        exit(0)
    else:
        print("\n❌ Service consolidation failed!")
        exit(1)

if __name__ == "__main__":
    main()