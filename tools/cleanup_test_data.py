#!/usr/bin/env python3
"""
Script to clean up all test data from the project
"""
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


async def cleanup_database():
    """Clean up test data from databases"""
    print("🧹 Cleaning up database test data...")
    
    try:
        from app.database.postgresql import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # Remove test users (emails containing 'test' or 'example.com') - Using parameterized queries
            result = await session.execute(
                text("""
                    DELETE FROM users 
                    WHERE email LIKE :test_pattern 
                    OR email LIKE :example_pattern
                    RETURNING id
                """),
                {"test_pattern": "%test%", "example_pattern": "%example.com%"}
            )
            deleted_users = result.rowcount
            
            # Remove orphaned data
            await session.execute(text("DELETE FROM user_roles WHERE user_id NOT IN (SELECT id FROM users)"))
            await session.execute(text("DELETE FROM projects WHERE created_by NOT IN (SELECT id FROM users)"))
            await session.execute(text("DELETE FROM analysis_results WHERE project_id NOT IN (SELECT id FROM projects)"))
            await session.execute(text("DELETE FROM analysis_tasks WHERE project_id NOT IN (SELECT id FROM projects)"))
            
            await session.commit()
            
            print(f"  ✅ Removed {deleted_users} test users and related data")
            
    except Exception as e:
        print(f"  ⚠️  Database cleanup skipped: {e}")


async def cleanup_redis():
    """Clean up test data from Redis"""
    print("🧹 Cleaning up Redis test data...")
    
    try:
        from app.database.redis_db import get_redis
        
        redis = await get_redis()
        
        # Remove test tokens
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="*test*", count=100)
            if keys:
                await redis.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        
        print(f"  ✅ Removed {deleted} test keys from Redis")
        
    except Exception as e:
        print(f"  ⚠️  Redis cleanup skipped: {e}")


async def cleanup_neo4j():
    """Clean up test data from Neo4j"""
    print("🧹 Cleaning up Neo4j test data...")
    
    try:
        from app.database.neo4j_db import get_neo4j_driver
        
        driver = get_neo4j_driver()
        
        async with driver.session() as session:
            # Remove test projects
            result = await session.run(
                """
                MATCH (n)
                WHERE n.projectId CONTAINS 'test' OR n.projectId CONTAINS 'example'
                DETACH DELETE n
                RETURN count(n) as deleted
                """
            )
            record = await result.single()
            deleted = record["deleted"] if record else 0
            
            print(f"  ✅ Removed {deleted} test nodes from Neo4j")
            
    except Exception as e:
        print(f"  ⚠️  Neo4j cleanup skipped: {e}")


def cleanup_env_files():
    """Clean up sensitive data from environment files"""
    print("🧹 Cleaning up environment files...")
    
    env_files = [
        ".env",
        "backend/.env",
        "frontend/.env.local"
    ]
    
    template_content = {
        ".env": """# Database Configuration
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=ai_code_review
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_URL=

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j

# Security
JWT_SECRET=
SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# GitHub Integration
GITHUB_TOKEN=
GITHUB_WEBHOOK_SECRET=

# LLM API Keys (Optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4

# Celery Configuration
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
""",
        "backend/.env": """# Minimal configuration
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=
POSTGRES_PASSWORD=

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Security
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Optional APIs
GITHUB_TOKEN=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Celery
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=

# Performance
RATE_LIMIT_PER_MINUTE=60
""",
        "frontend/.env.local": """# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000

# Application Environment
NEXT_PUBLIC_APP_ENV=development
NODE_ENV=development
"""
    }
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write(template_content.get(env_file, ""))
            print(f"  ✅ Cleaned {env_file}")


def remove_test_files():
    """Remove test and temporary files"""
    print("🧹 Removing test files...")
    
    test_files = [
        "test-auth.py",
        "backend/test_app.py",
        "backend/test_minimal_app.py",
        "backend/test_ast_llm_integration.py",
        "backend/test_bcrypt_config_startup.py",
        "backend/test_config.py",
        "backend/test_jwt_revocation_manual.py",
        "backend/test_token_type_validation.py"
    ]
    
    removed = 0
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            removed += 1
            print(f"  ✅ Removed {file_path}")
    
    print(f"  ✅ Removed {removed} test files")


async def main():
    """Main cleanup function"""
    print("=" * 60)
    print("🧹 Starting Test Data Cleanup")
    print("=" * 60)
    print()
    
    # Clean databases
    await cleanup_database()
    await cleanup_redis()
    await cleanup_neo4j()
    
    # Clean files
    cleanup_env_files()
    remove_test_files()
    
    print()
    print("=" * 60)
    print("✅ Cleanup Complete!")
    print("=" * 60)
    print()
    print("⚠️  Important: Please update your .env files with actual values")
    print("   before running the application.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Cleanup failed: {e}")
        sys.exit(1)
