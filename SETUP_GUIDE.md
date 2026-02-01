# Complete Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git
- PostgreSQL client (optional, for manual operations)

## Step-by-Step Setup

### 1. Clean Up Test Data

```bash
# Run the automated cleanup script
python scripts/cleanup_test_data.py

# This will:
# - Remove test users from database
# - Clear test data from Redis
# - Clean Neo4j test nodes
# - Sanitize environment files
# - Delete standalone test scripts
```

### 2. Configure Environment Variables

#### Generate Secure Keys

```bash
# JWT Secret (32 bytes hex)
openssl rand -hex 32

# NextAuth Secret (base64)
openssl rand -base64 32

# Webhook Secret
openssl rand -hex 20
```

#### Update .env (Root Directory)

```bash
# Database Configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=ai_code_review
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://your_db_user:your_secure_password_here@postgres:5432/ai_code_review

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_URL=redis://:your_redis_password_here@redis:6379

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j

# Security - Use generated keys from above
JWT_SECRET=your_generated_jwt_secret_here
SECRET_KEY=your_generated_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# LLM API Keys (Optional)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4

# Celery Configuration
CELERY_BROKER_URL=redis://:your_redis_password_here@redis:6379/0
CELERY_RESULT_BACKEND=redis://:your_redis_password_here@redis:6379/1

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### Update backend/.env

```bash
# Copy relevant values from root .env
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_code_review
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password_here

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

JWT_SECRET=your_generated_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

CELERY_BROKER_URL=redis://:your_redis_password_here@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:your_redis_password_here@localhost:6379/2

RATE_LIMIT_PER_MINUTE=60
```

#### Update frontend/.env.local

```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_generated_nextauth_secret_here

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000

# Application Environment
NEXT_PUBLIC_APP_ENV=development
NODE_ENV=development
```

### 3. Get GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:org` - Read organization data
4. Generate and copy the token
5. Add to `.env` files as `GITHUB_TOKEN`

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Run Database Migrations

```bash
# Navigate to backend
cd backend

# Run migrations
alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U your_db_user -d ai_code_review -c "\dt"
```

Expected tables:
- users
- roles
- permissions
- user_roles
- role_permissions
- projects
- analysis_results
- analysis_tasks
- user_preferences
- project_metrics
- audit_logs
- **repositories** (new)

### 6. Create First User

```bash
# Using the API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User"
  }'
```

### 7. Test Repository Management

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!"
  }' | jq -r '.access_token')

# Validate a repository
curl -X GET "http://localhost:8000/api/v1/repositories/validate?repository_url=https://github.com/facebook/react.git" \
  -H "Authorization: Bearer $TOKEN"

# Add a repository
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/facebook/react.git",
    "branch": "main",
    "auto_update": false,
    "description": "React library"
  }'
```

### 8. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Check frontend (if running)
open http://localhost:3000

# Check database connections
python backend/check-services.py
```

## Verification Checklist

- [ ] All services running (postgres, redis, neo4j, backend)
- [ ] Database migrations completed
- [ ] No test data in databases
- [ ] Environment variables configured
- [ ] GitHub token working
- [ ] User registration successful
- [ ] User login successful
- [ ] Repository validation working
- [ ] Repository addition working
- [ ] API documentation accessible

## Common Issues

### Issue: Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Issue: Redis Connection Failed

```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Issue: Neo4j Connection Failed

```bash
# Check if Neo4j is running
docker-compose ps neo4j

# Check logs
docker-compose logs neo4j

# Access Neo4j browser
open http://localhost:7474
```

### Issue: GitHub API Rate Limit

```bash
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Wait for reset or use authenticated requests
```

### Issue: Migration Fails

```bash
# Check current migration version
cd backend
alembic current

# Downgrade if needed
alembic downgrade -1

# Upgrade again
alembic upgrade head
```

## Development Workflow

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Database Operations

```bash
# Create new migration
cd backend
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secrets (32+ characters)
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Enable database authentication
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Enable rate limiting
- [ ] Review CORS settings
- [ ] Disable DEBUG mode

### Environment Configuration

```bash
# Production .env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
NEO4J_PASSWORD=$(openssl rand -base64 32)

# Use production URLs
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXTAUTH_URL=https://yourdomain.com
```

### Docker Compose Production

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# Neo4j health
curl http://localhost:7474/db/data/
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Metrics

```bash
# If Prometheus is configured
open http://localhost:9090

# If Grafana is configured
open http://localhost:3001
```

## Backup and Restore

### PostgreSQL Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U your_db_user ai_code_review > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U your_db_user ai_code_review < backup_20260121.sql
```

### Neo4j Backup

```bash
# Backup
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j_$(date +%Y%m%d).dump

# Restore
docker-compose exec neo4j neo4j-admin load --from=/backups/neo4j_20260121.dump --database=neo4j --force
```

### Redis Backup

```bash
# Backup
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb backup_redis_$(date +%Y%m%d).rdb

# Restore
docker cp backup_redis_20260121.rdb $(docker-compose ps -q redis):/data/dump.rdb
docker-compose restart redis
```

## Support

### Documentation

- [Repository Management Guide](docs/REPOSITORY_MANAGEMENT.md)
- [Data Cleanup Guide](docs/DATA_CLEANUP_GUIDE.md)
- [Quick Start](REPOSITORY_MANAGEMENT_QUICKSTART.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

### Getting Help

1. Check documentation
2. Review error logs
3. Search existing issues
4. Create new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Relevant logs

## Next Steps

1. ✅ Complete setup following this guide
2. 📖 Read [Repository Management Guide](docs/REPOSITORY_MANAGEMENT.md)
3. 🧪 Test repository management features
4. 🚀 Deploy to production (when ready)
5. 📊 Set up monitoring and alerts
6. 🔄 Configure automated backups
