# Production Deployment Guide

This guide covers deploying the AI-Based Quality Check system to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Production Deployment](#docker-production-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Security Considerations](#security-considerations)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: Minimum 4 cores (8 cores recommended)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: Minimum 50GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS recommended), macOS, or Windows with WSL2

### Software Requirements

- Docker Engine 24.0+ and Docker Compose 2.20+
- Git 2.30+
- SSL certificates (Let's Encrypt recommended)
- Domain name with DNS configured

## Environment Configuration

### 1. Create Production Environment File

Copy the production template:

```bash
cp .env.production.template .env.production
```

### 2. Configure Required Variables

Edit `.env.production` and set all required values:

```bash
# Database Configuration
POSTGRES_USER=your_secure_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=ai_review_prod

# Redis Configuration
REDIS_DB=0

# Neo4j Configuration
NEO4J_AUTH=neo4j/your_secure_neo4j_password
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_neo4j_password

# Security Keys (Generate with: openssl rand -hex 32)
JWT_SECRET=your_jwt_secret_here
SECRET_KEY=your_secret_key_here
SESSION_SECRET=your_session_secret_here

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_CALLBACK_URL=https://yourdomain.com/api/github/callback
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. Generate Secure Keys

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate secret key
openssl rand -hex 32

# Generate session secret
openssl rand -hex 32
```

## Docker Production Deployment

### 1. SSL Certificate Setup

For production, use Let's Encrypt certificates:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

For development, use self-signed certificates (already configured).

### 2. Build Production Images

```bash
# Build backend with production Dockerfile
docker build -f backend/Dockerfile.prod -t ai-review-backend:prod ./backend

# Build frontend with production Dockerfile
docker build -f frontend/Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1 \
  --build-arg NEXT_PUBLIC_BACKEND_URL=https://yourdomain.com \
  --build-arg NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id \
  -t ai-review-frontend:prod ./frontend
```

### 3. Deploy with Docker Compose

```bash
# Use production compose file
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 4. Database Migrations

```bash
# Run database migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Verify migration
docker-compose -f docker-compose.production.yml exec backend alembic current
```

### 5. Health Checks

```bash
# Check backend health
curl https://yourdomain.com/health

# Check frontend health
curl https://yourdomain.com/api/health

# Check all services
docker-compose -f docker-compose.production.yml ps
```

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

Create `k8s/` directory with the following files:

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-review-prod
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-review-config
  namespace: ai-review-prod
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  POSTGRES_HOST: "postgres-service"
  REDIS_HOST: "redis-service"
  NEO4J_URI: "bolt://neo4j-service:7687"
```

#### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-review-secrets
  namespace: ai-review-prod
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your_secure_password"
  JWT_SECRET: "your_jwt_secret"
  SECRET_KEY: "your_secret_key"
```

### 2. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/neo4j.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n ai-review-prod
kubectl get services -n ai-review-prod
```

## Security Considerations

### 1. Network Security

- Use HTTPS only (enforce with HSTS headers)
- Configure firewall rules to restrict access
- Use private networks for database connections
- Enable rate limiting on API endpoints

### 2. Application Security

- Keep all dependencies updated
- Use non-root users in containers
- Enable read-only root filesystem where possible
- Scan images for vulnerabilities regularly

```bash
# Scan images with Trivy
trivy image ai-review-backend:prod
trivy image ai-review-frontend:prod
```

### 3. Database Security

- Use strong passwords (minimum 32 characters)
- Enable SSL/TLS for database connections
- Restrict database access to application network only
- Regular security audits and updates

### 4. Secrets Management

- Never commit secrets to version control
- Use environment variables or secret management tools
- Rotate secrets regularly
- Use different secrets for each environment

## Monitoring and Logging

### 1. Application Logs

```bash
# View backend logs
docker-compose -f docker-compose.production.yml logs -f backend

# View frontend logs
docker-compose -f docker-compose.production.yml logs -f frontend

# View all logs
docker-compose -f docker-compose.production.yml logs -f
```

### 2. Performance Monitoring

Access the performance dashboard at:
```
https://yourdomain.com/performance
```

Monitor:
- API response times
- Database query performance
- Cache hit rates
- System resource usage

### 3. Health Monitoring

Set up automated health checks:

```bash
# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/health)
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/health)

if [ "$BACKEND_HEALTH" != "200" ] || [ "$FRONTEND_HEALTH" != "200" ]; then
    echo "Health check failed!"
    exit 1
fi
echo "All services healthy"
EOF

chmod +x health-check.sh

# Add to crontab for monitoring
crontab -e
# Add: */5 * * * * /path/to/health-check.sh
```

## Backup and Recovery

### 1. Database Backup

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres \
  pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup Neo4j
docker-compose -f docker-compose.production.yml exec neo4j \
  neo4j-admin database dump neo4j --to-path=/backups
```

### 2. Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
docker-compose -f docker-compose.production.yml exec -T postgres \
  pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > "$BACKUP_DIR/postgres_$DATE.sql.gz"

# Neo4j backup
docker-compose -f docker-compose.production.yml exec neo4j \
  neo4j-admin database dump neo4j --to-path=/backups

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 3. Restore from Backup

```bash
# Restore PostgreSQL
gunzip < backup_20240101_120000.sql.gz | \
  docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U $POSTGRES_USER $POSTGRES_DB

# Restore Neo4j
docker-compose -f docker-compose.production.yml exec neo4j \
  neo4j-admin database load neo4j --from-path=/backups
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.production.yml restart
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Check Neo4j is running
docker-compose -f docker-compose.production.yml exec neo4j cypher-shell "RETURN 1"

# Verify network connectivity
docker-compose -f docker-compose.production.yml exec backend ping postgres
```

#### 3. High Memory Usage

```bash
# Check memory usage
docker stats

# Adjust resource limits in docker-compose.production.yml
# Restart services with new limits
docker-compose -f docker-compose.production.yml up -d
```

#### 4. SSL Certificate Issues

```bash
# Verify certificate files exist
ls -la nginx/ssl/

# Check certificate validity
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Regenerate self-signed certificate if needed
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- PostgreSQL: Analyze tables
ANALYZE;

-- Create indexes for frequently queried columns
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_analyses_project_id ON analyses(project_id);
```

#### 2. Redis Cache Optimization

```bash
# Monitor cache hit rate
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO stats

# Adjust maxmemory policy if needed
docker-compose -f docker-compose.production.yml exec redis \
  redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. Application Optimization

- Enable HTTP/2 in nginx
- Configure proper caching headers
- Use CDN for static assets
- Enable gzip compression

### Getting Help

- Check logs: `docker-compose -f docker-compose.production.yml logs -f`
- Review health endpoints: `/health` and `/api/health`
- Monitor performance dashboard: `/performance`
- Check system resources: `docker stats`

## Maintenance

### Regular Tasks

1. **Daily**: Monitor logs and health checks
2. **Weekly**: Review performance metrics and optimize
3. **Monthly**: Update dependencies and security patches
4. **Quarterly**: Review and rotate secrets

### Update Procedure

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Rebuild images
docker-compose -f docker-compose.production.yml build

# 4. Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# 5. Restart services with zero downtime
docker-compose -f docker-compose.production.yml up -d --no-deps --build backend
docker-compose -f docker-compose.production.yml up -d --no-deps --build frontend

# 6. Verify deployment
curl https://yourdomain.com/health
```

## Support

For issues and questions:
- Check documentation in `/docs`
- Review logs and error messages
- Contact system administrator
