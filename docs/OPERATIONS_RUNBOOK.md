# Operations Runbook: AI-Based Code Reviewer Platform

## Executive Summary

This Operations Runbook provides comprehensive operational procedures, troubleshooting guides, and best practices for maintaining the AI-Based Code Reviewer platform. It serves as the primary reference for operations teams managing both Docker Compose (development/staging) and AWS production deployments.

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Target Audience**: Operations Engineers, DevOps Engineers, System Administrators, On-Call Engineers

**Requirements Addressed**:
- **Requirement 9.2**: Operations runbook with common troubleshooting procedures
- **Requirement 9.9**: Monitoring and alerting configuration guide

### Quick Reference

| Component | Health Check | Default Port | Logs Location |
|-----------|--------------|--------------|---------------|
| Backend API | `curl http://localhost:8000/health` | 8000 | `backend/logs/` |
| Frontend | `curl http://localhost:3000/api/health` | 3000 | Docker logs |
| PostgreSQL | `pg_isready -h localhost -p 5432` | 5432 | Docker logs |
| Redis | `redis-cli -p 6379 ping` | 6379 | Docker logs |
| Neo4j | `http://localhost:7474` | 7474, 7687 | `neo4j_logs/` |
| Celery Worker | Check logs | N/A | Docker logs |

### Emergency Contacts

| Role | Contact | Escalation Time |
|------|---------|-----------------|
| On-Call Engineer | Check PagerDuty | Immediate |
| DevOps Lead | [Contact Info] | 15 minutes |
| Backend Lead | [Contact Info] | 30 minutes |
| Incident Commander | [Contact Info] | 1 hour |

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Common Operational Tasks](#common-operational-tasks)
3. [Service Management](#service-management)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Backup and Restore Procedures](#backup-and-restore-procedures)
7. [Performance Optimization](#performance-optimization)
8. [Security Operations](#security-operations)
9. [Incident Response](#incident-response)
10. [Maintenance Procedures](#maintenance-procedures)


---

## System Architecture Overview

### Component Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer / Nginx                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐            ┌────────▼────────┐
│   Frontend      │            │   Backend API   │
│   (Next.js)     │            │   (FastAPI)     │
│   Port: 3000    │            │   Port: 8000    │
└─────────────────┘            └────────┬────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
           ┌────────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
           │   PostgreSQL    │ │     Redis      │ │     Neo4j      │
           │   Port: 5432    │ │   Port: 6379   │ │  Port: 7474    │
           │                 │ │                │ │  Port: 7687    │
           └─────────────────┘ └────────┬───────┘ └────────────────┘
                                        │
                               ┌────────▼────────┐
                               │ Celery Workers  │
                               │  (Background)   │
                               └─────────────────┘
```

### Service Descriptions

**Frontend (Next.js)**
- Serves user interface
- Communicates with Backend API
- Handles client-side routing and state management
- **Critical**: User-facing service

**Backend API (FastAPI)**
- REST API endpoints
- Business logic and orchestration
- Authentication and authorization
- **Critical**: Core application service

**PostgreSQL**
- Primary relational database
- Stores users, projects, analysis results, audit logs
- **Critical**: Data persistence layer

**Redis**
- Caching layer (session data, API responses)
- Celery message broker
- Rate limiting storage
- **Important**: Performance and background jobs

**Neo4j**
- Graph database for dependency relationships
- Stores code entity relationships
- Circular dependency detection
- **Important**: Architecture analysis features

**Celery Workers**
- Background task processing
- Long-running analysis jobs
- Scheduled tasks (cleanup, metrics)
- **Important**: Asynchronous operations

### Service Dependencies

| Service | Depends On | Can Start Without |
|---------|------------|-------------------|
| PostgreSQL | None | All |
| Redis | None | All |
| Neo4j | None | All |
| Backend | PostgreSQL, Redis, Neo4j | None (hard dependency) |
| Frontend | Backend | None (hard dependency) |
| Celery Worker | Redis, PostgreSQL, Neo4j | Backend (soft) |
| Nginx | Frontend, Backend | None (hard dependency) |


---

## Common Operational Tasks

### Starting Services

#### Docker Compose (Development/Staging)

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis neo4j

# Start with rebuild
docker-compose up -d --build

# View startup logs
docker-compose logs -f

# Check service status
docker-compose ps
```

#### AWS Production

```bash
# Check Auto Scaling Group status
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names ai-code-reviewer-prod-asg \
  --query 'AutoScalingGroups[0].[DesiredCapacity,MinSize,MaxSize,Instances[*].HealthStatus]'

# Check Load Balancer target health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw target_group_arn)

# Trigger instance refresh (rolling update)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name ai-code-reviewer-prod-asg \
  --preferences MinHealthyPercentage=90,InstanceWarmup=300
```

### Stopping Services

#### Docker Compose

```bash
# Stop all services (preserves data)
docker-compose stop

# Stop specific service
docker-compose stop backend

# Stop and remove containers (preserves volumes)
docker-compose down

# Stop and remove everything including volumes (DESTRUCTIVE)
docker-compose down -v
```

#### AWS Production

```bash
# Scale down to minimum capacity
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name ai-code-reviewer-prod-asg \
  --desired-capacity 2

# Suspend Auto Scaling (for maintenance)
aws autoscaling suspend-processes \
  --auto-scaling-group-name ai-code-reviewer-prod-asg \
  --scaling-processes HealthCheck AlarmNotification
```

### Checking Logs

#### Docker Compose

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs -f backend --tail=100

# View logs with timestamps
docker-compose logs -t backend

# Search logs for errors
docker-compose logs backend | grep -i error
docker-compose logs backend | grep -i exception
```

#### AWS Production

```bash
# View CloudWatch logs
aws logs tail /aws/ec2/ai-code-reviewer-prod --follow

# Query logs for errors
aws logs filter-log-events \
  --log-group-name /aws/ec2/ai-code-reviewer-prod \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Export logs to file
aws logs get-log-events \
  --log-group-name /aws/ec2/ai-code-reviewer-prod \
  --log-stream-name <stream-name> \
  --output json > logs.json
```

### Restarting Services

#### Docker Compose

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Restart with rebuild
docker-compose up -d --build --force-recreate backend

# Graceful restart (stop then start)
docker-compose stop backend && docker-compose up -d backend
```

#### AWS Production

```bash
# Terminate specific instance (Auto Scaling will replace)
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Force instance refresh (rolling restart)
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name ai-code-reviewer-prod-asg
```

### Checking Service Health

```bash
# Backend health check
curl -f http://localhost:8000/health || echo "Backend unhealthy"

# Frontend health check
curl -f http://localhost:3000/api/health || echo "Frontend unhealthy"

# PostgreSQL health check
docker exec ai_review_postgres pg_isready -U postgres

# Redis health check
docker exec ai_review_redis redis-cli ping

# Neo4j health check
curl -f http://localhost:7474 || echo "Neo4j unhealthy"

# All services health check script
./scripts/health-check-all.sh
```

### Viewing Resource Usage

```bash
# Docker resource usage
docker stats

# Specific container stats
docker stats ai_review_backend ai_review_postgres

# Disk usage
docker system df

# Volume usage
docker volume ls
du -sh $(docker volume inspect postgres_data --format '{{ .Mountpoint }}')
```


---

## Service Management

### Backend API Service

#### Configuration

**Environment Variables** (`.env` file):
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
REDIS_URL=redis://:password@redis:6379/0
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
JWT_SECRET=your-secret-key
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Common Operations

```bash
# View backend logs
docker-compose logs -f backend

# Execute command in backend container
docker exec -it ai_review_backend bash

# Run database migrations
docker exec ai_review_backend alembic upgrade head

# Check current migration version
docker exec ai_review_backend alembic current

# Rollback migration
docker exec ai_review_backend alembic downgrade -1

# Run Python shell
docker exec -it ai_review_backend python

# Test database connection
docker exec ai_review_backend python -c "from app.database.session import engine; print(engine.connect())"
```

#### Performance Tuning

```bash
# Check worker processes
docker exec ai_review_backend ps aux | grep uvicorn

# Monitor request rate
docker exec ai_review_backend tail -f /app/logs/access.log | grep -o "GET\|POST\|PUT\|DELETE" | uniq -c

# Check memory usage
docker stats ai_review_backend --no-stream
```

### Database Services

#### PostgreSQL Operations

```bash
# Connect to PostgreSQL
docker exec -it ai_review_postgres psql -U postgres -d ai_code_reviewer

# Backup database
docker exec ai_review_postgres pg_dump -U postgres ai_code_reviewer > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup.sql | docker exec -i ai_review_postgres psql -U postgres ai_code_reviewer

# Check database size
docker exec ai_review_postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('ai_code_reviewer'));"

# Check table sizes
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;"

# Check active connections
docker exec ai_review_postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Kill long-running queries
docker exec ai_review_postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
AND query_start < NOW() - INTERVAL '5 minutes';"

# Vacuum database
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "VACUUM ANALYZE;"
```

#### Redis Operations

```bash
# Connect to Redis
docker exec -it ai_review_redis redis-cli -a ${REDIS_PASSWORD}

# Check Redis info
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO

# Check memory usage
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO memory

# Check connected clients
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} CLIENT LIST

# Monitor commands in real-time
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} MONITOR

# Flush cache (DESTRUCTIVE - use with caution)
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} FLUSHDB

# Check cache hit rate
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO stats | grep keyspace
```

#### Neo4j Operations

```bash
# Access Neo4j browser
# Open http://localhost:7474 in browser

# Connect via cypher-shell
docker exec -it ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD}

# Check database size
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "
CALL apoc.meta.stats() YIELD nodeCount, relCount, labelCount
RETURN nodeCount, relCount, labelCount;"

# Check node counts by label
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "
MATCH (n)
RETURN labels(n) AS label, count(*) AS count
ORDER BY count DESC;"

# Clear all data (DESTRUCTIVE)
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "
MATCH (n) DETACH DELETE n;"

# Create indexes
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "
CREATE INDEX code_entity_name IF NOT EXISTS FOR (n:CodeEntity) ON (n.name);"
```

### Celery Workers

```bash
# View Celery worker logs
docker-compose logs -f celery_worker

# Check active tasks
docker exec ai_review_celery celery -A app.celery_config inspect active

# Check registered tasks
docker exec ai_review_celery celery -A app.celery_config inspect registered

# Check worker stats
docker exec ai_review_celery celery -A app.celery_config inspect stats

# Purge all tasks (DESTRUCTIVE)
docker exec ai_review_celery celery -A app.celery_config purge

# Restart workers
docker-compose restart celery_worker celery_beat
```


---

## Troubleshooting Guide

### Service Restart Issues

#### Problem: Services Keep Restarting

**Symptoms:**
- Docker containers show "Restarting" status
- Services appear in `docker-compose ps` but are not accessible
- Logs show repeated startup and crash cycles

**Common Causes:**

1. **Database Connection Failures**
2. **Missing Environment Variables**
3. **Port Conflicts**
4. **Resource Exhaustion**
5. **Configuration Errors**

**Diagnostic Steps:**

```bash
# 1. Check service status
docker-compose ps

# 2. View recent logs for failing service
docker-compose logs --tail=50 backend

# 3. Check for error patterns
docker-compose logs backend | grep -i "error\|exception\|failed\|fatal"

# 4. Check resource usage
docker stats --no-stream

# 5. Check port conflicts
netstat -tulpn | grep -E "8000|3000|5432|6379|7474|7687"

# 6. Verify environment variables
docker exec ai_review_backend env | grep -E "DATABASE_URL|REDIS_URL|NEO4J"
```

**Solutions:**

**Solution 1: Database Connection Issues**
```bash
# Check if databases are healthy
docker-compose ps postgres redis neo4j

# Wait for databases to be ready
docker-compose up -d postgres redis neo4j
sleep 30

# Restart dependent services
docker-compose restart backend celery_worker
```

**Solution 2: Missing Environment Variables**
```bash
# Verify .env file exists
ls -la .env

# Check for required variables
grep -E "POSTGRES_PASSWORD|REDIS_PASSWORD|NEO4J_PASSWORD|JWT_SECRET" .env

# Recreate services with updated environment
docker-compose up -d --force-recreate backend
```

**Solution 3: Port Conflicts**
```bash
# Find process using port
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill conflicting process
kill -9 <PID>

# Or change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use different host port
```

**Solution 4: Resource Exhaustion**
```bash
# Check Docker disk space
docker system df

# Clean up unused resources
docker system prune -a --volumes

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → Increase to 8GB

# Check system resources
free -h
df -h
```

**Solution 5: Configuration Errors**
```bash
# Validate docker-compose.yml
docker-compose config

# Check for syntax errors in application config
docker exec ai_review_backend python -c "from app.core.config import settings; print(settings)"

# Review application logs for config errors
docker-compose logs backend | grep -i "config\|settings"
```

### High Error Rate

#### Problem: API Returns 500 Errors

**Symptoms:**
- HTTP 500 Internal Server Error responses
- High error rate in logs
- Users unable to complete operations

**Diagnostic Steps:**

```bash
# 1. Check error rate
docker-compose logs backend | grep "500" | wc -l

# 2. View recent errors
docker-compose logs backend | grep -A 10 "ERROR"

# 3. Check database connectivity
docker exec ai_review_backend python -c "
from app.database.session import SessionLocal
db = SessionLocal()
print('Database connected:', db.execute('SELECT 1').scalar())
db.close()
"

# 4. Check external service connectivity
docker exec ai_review_backend python -c "
import redis
r = redis.from_url('redis://:${REDIS_PASSWORD}@redis:6379/0')
print('Redis connected:', r.ping())
"
```

**Solutions:**

**Solution 1: Database Connection Pool Exhausted**
```bash
# Check active connections
docker exec ai_review_postgres psql -U postgres -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;"

# Increase pool size in backend configuration
# Edit backend/app/database/session.py
# engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)

# Restart backend
docker-compose restart backend
```

**Solution 2: Memory Leak**
```bash
# Check memory usage over time
docker stats ai_review_backend --no-stream

# Restart service to free memory
docker-compose restart backend

# Monitor for memory growth
watch -n 5 'docker stats ai_review_backend --no-stream'
```

**Solution 3: Unhandled Exceptions**
```bash
# Review exception logs
docker-compose logs backend | grep -B 5 -A 10 "Traceback"

# Enable debug logging temporarily
docker exec ai_review_backend sed -i 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/' .env
docker-compose restart backend

# Review detailed logs
docker-compose logs -f backend
```

### Slow Response Times

#### Problem: API Response Time > 1 Second

**Symptoms:**
- Slow page loads
- Timeouts
- Poor user experience

**Diagnostic Steps:**

```bash
# 1. Measure response time
time curl -X GET http://localhost:8000/api/v1/projects

# 2. Check database query performance
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;"

# 3. Check cache hit rate
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO stats | grep keyspace_hits

# 4. Check system resources
docker stats --no-stream
```

**Solutions:**

**Solution 1: Missing Database Indexes**
```bash
# Identify slow queries
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 5;"

# Add indexes (example)
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
CREATE INDEX CONCURRENTLY idx_projects_user_id ON projects(user_id);
CREATE INDEX CONCURRENTLY idx_analysis_results_project_id ON analysis_results(project_id);"
```

**Solution 2: Cache Not Working**
```bash
# Check Redis connectivity
docker exec ai_review_backend python -c "
import redis
r = redis.from_url('redis://:${REDIS_PASSWORD}@redis:6379/0')
print('Redis ping:', r.ping())
print('Keys:', r.dbsize())
"

# Warm up cache
curl http://localhost:8000/api/v1/projects  # First request (slow)
curl http://localhost:8000/api/v1/projects  # Second request (should be fast)
```

**Solution 3: Resource Constraints**
```bash
# Increase container resources in docker-compose.yml
# deploy:
#   resources:
#     limits:
#       memory: 2G
#       cpus: '2'

# Apply changes
docker-compose up -d --force-recreate backend
```

### Database Connection Issues

#### Problem: Cannot Connect to Database

**Symptoms:**
- "Connection refused" errors
- "Could not connect to server" errors
- Backend fails to start

**Diagnostic Steps:**

```bash
# 1. Check if PostgreSQL is running
docker-compose ps postgres

# 2. Check PostgreSQL logs
docker-compose logs postgres | tail -50

# 3. Test connection from host
psql -h localhost -p 5432 -U postgres -d ai_code_reviewer

# 4. Test connection from backend container
docker exec ai_review_backend pg_isready -h postgres -p 5432
```

**Solutions:**

**Solution 1: PostgreSQL Not Started**
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for it to be ready
docker-compose logs -f postgres
# Wait for "database system is ready to accept connections"

# Restart backend
docker-compose restart backend
```

**Solution 2: Wrong Connection String**
```bash
# Verify DATABASE_URL format
# Correct: postgresql://user:password@postgres:5432/dbname
# Wrong: postgresql://user:password@localhost:5432/dbname (use 'postgres' not 'localhost')

# Update .env file
echo "DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/ai_code_reviewer" >> .env

# Recreate backend
docker-compose up -d --force-recreate backend
```

**Solution 3: Connection Pool Exhausted**
```bash
# Check active connections
docker exec ai_review_postgres psql -U postgres -c "
SELECT count(*) as connections, state
FROM pg_stat_activity
GROUP BY state;"

# Kill idle connections
docker exec ai_review_postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';"
```

### Redis Connection Issues

#### Problem: Cannot Connect to Redis

**Symptoms:**
- "Connection refused" errors
- Cache not working
- Celery tasks not processing

**Diagnostic Steps:**

```bash
# 1. Check if Redis is running
docker-compose ps redis

# 2. Test Redis connection
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} ping

# 3. Check Redis logs
docker-compose logs redis | tail -50

# 4. Verify password
echo $REDIS_PASSWORD
```

**Solutions:**

**Solution 1: Redis Not Started**
```bash
# Start Redis
docker-compose up -d redis

# Verify it's running
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} ping
```

**Solution 2: Wrong Password**
```bash
# Check password in .env
grep REDIS_PASSWORD .env

# Update REDIS_URL in .env
echo "REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0" >> .env

# Restart services
docker-compose restart backend celery_worker
```

**Solution 3: Redis Out of Memory**
```bash
# Check Redis memory usage
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO memory

# Flush cache if needed (DESTRUCTIVE)
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} FLUSHDB

# Increase maxmemory in docker-compose.yml
# command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 1gb
```


### Neo4j Connection Issues

#### Problem: Cannot Connect to Neo4j

**Symptoms:**
- "ServiceUnavailable" errors
- Graph visualization not working
- Architecture analysis fails

**Diagnostic Steps:**

```bash
# 1. Check if Neo4j is running
docker-compose ps neo4j

# 2. Check Neo4j logs
docker-compose logs neo4j | tail -100

# 3. Test connection
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "RETURN 1;"

# 4. Check browser interface
curl -f http://localhost:7474 || echo "Neo4j browser not accessible"
```

**Solutions:**

**Solution 1: Neo4j Not Fully Started**
```bash
# Neo4j takes 30-60 seconds to start
# Wait and check logs
docker-compose logs -f neo4j
# Wait for "Started."

# Test connection again
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} "RETURN 1;"
```

**Solution 2: Wrong Credentials**
```bash
# Check NEO4J_AUTH format in .env
# Correct format: NEO4J_AUTH=neo4j/your-password
grep NEO4J_AUTH .env

# Update if needed
echo "NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}" >> .env

# Recreate Neo4j (will reset data)
docker-compose stop neo4j
docker volume rm $(docker volume ls -q | grep neo4j)
docker-compose up -d neo4j
```

**Solution 3: Memory Issues**
```bash
# Check Neo4j memory settings
docker exec ai_review_neo4j cat /var/lib/neo4j/conf/neo4j.conf | grep memory

# Increase memory in docker-compose.yml
# NEO4J_server_memory_heap_max__size: 4G
# NEO4J_server_memory_pagecache_size: 2G

# Restart Neo4j
docker-compose up -d --force-recreate neo4j
```

### Celery Tasks Not Processing

#### Problem: Background Tasks Stuck

**Symptoms:**
- Analysis jobs not completing
- Tasks stuck in "pending" state
- No worker activity in logs

**Diagnostic Steps:**

```bash
# 1. Check if workers are running
docker-compose ps celery_worker celery_beat

# 2. Check worker logs
docker-compose logs celery_worker | tail -100

# 3. Check active tasks
docker exec ai_review_celery celery -A app.celery_config inspect active

# 4. Check registered tasks
docker exec ai_review_celery celery -A app.celery_config inspect registered

# 5. Check Redis queue
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} LLEN celery
```

**Solutions:**

**Solution 1: Workers Not Running**
```bash
# Start workers
docker-compose up -d celery_worker celery_beat

# Verify they're running
docker-compose logs -f celery_worker
```

**Solution 2: Workers Crashed**
```bash
# Check for errors in logs
docker-compose logs celery_worker | grep -i "error\|exception"

# Restart workers
docker-compose restart celery_worker celery_beat

# Monitor startup
docker-compose logs -f celery_worker
```

**Solution 3: Task Queue Backed Up**
```bash
# Check queue length
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} LLEN celery

# Purge old tasks (DESTRUCTIVE)
docker exec ai_review_celery celery -A app.celery_config purge

# Scale up workers (add more containers)
docker-compose up -d --scale celery_worker=3
```

**Solution 4: Task Timeout**
```bash
# Check for long-running tasks
docker exec ai_review_celery celery -A app.celery_config inspect active

# Revoke stuck task
docker exec ai_review_celery celery -A app.celery_config revoke <task-id> --terminate

# Increase task timeout in celery config
# task_time_limit = 3600  # 1 hour
```

### High CPU Usage

#### Problem: CPU Usage > 80%

**Symptoms:**
- Slow response times
- System unresponsive
- High load average

**Diagnostic Steps:**

```bash
# 1. Check container CPU usage
docker stats --no-stream

# 2. Check system load
uptime

# 3. Identify CPU-intensive processes
docker exec ai_review_backend top -b -n 1

# 4. Check for runaway queries
docker exec ai_review_postgres psql -U postgres -c "
SELECT pid, query_start, state, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;"
```

**Solutions:**

**Solution 1: Runaway Database Query**
```bash
# Kill long-running query
docker exec ai_review_postgres psql -U postgres -c "
SELECT pg_terminate_backend(<pid>);"

# Add query timeout
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
ALTER DATABASE ai_code_reviewer SET statement_timeout = '30s';"
```

**Solution 2: Too Many Concurrent Requests**
```bash
# Check active connections
docker exec ai_review_backend netstat -an | grep :8000 | wc -l

# Add rate limiting (if not already configured)
# Restart backend
docker-compose restart backend
```

**Solution 3: Resource Limits Too High**
```bash
# Reduce CPU limits in docker-compose.yml
# deploy:
#   resources:
#     limits:
#       cpus: '1'

# Apply changes
docker-compose up -d --force-recreate
```

### High Memory Usage

#### Problem: Memory Usage > 85%

**Symptoms:**
- OOM (Out of Memory) errors
- Containers being killed
- Swap usage high

**Diagnostic Steps:**

```bash
# 1. Check container memory usage
docker stats --no-stream

# 2. Check system memory
free -h

# 3. Check for memory leaks
docker exec ai_review_backend ps aux --sort=-%mem | head -10

# 4. Check PostgreSQL memory
docker exec ai_review_postgres psql -U postgres -c "
SELECT pg_size_pretty(pg_database_size('ai_code_reviewer'));"
```

**Solutions:**

**Solution 1: Memory Leak in Application**
```bash
# Restart service to free memory
docker-compose restart backend

# Monitor memory growth
watch -n 10 'docker stats ai_review_backend --no-stream'

# If leak persists, review application code
docker-compose logs backend | grep -i "memory\|oom"
```

**Solution 2: Database Cache Too Large**
```bash
# Reduce PostgreSQL shared_buffers
# Edit docker-compose.yml
# POSTGRES_SHARED_BUFFERS: 128MB  # Reduce from 256MB

# Restart PostgreSQL
docker-compose up -d --force-recreate postgres
```

**Solution 3: Too Many Cached Objects**
```bash
# Clear Redis cache
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} FLUSHDB

# Reduce Redis maxmemory
# Edit docker-compose.yml
# command: redis-server --maxmemory 256mb

# Restart Redis
docker-compose up -d --force-recreate redis
```

### Disk Space Issues

#### Problem: Disk Space > 90% Full

**Symptoms:**
- "No space left on device" errors
- Cannot write logs
- Database operations fail

**Diagnostic Steps:**

```bash
# 1. Check disk usage
df -h

# 2. Check Docker disk usage
docker system df

# 3. Check volume sizes
docker volume ls
docker volume inspect postgres_data --format '{{ .Mountpoint }}'
du -sh $(docker volume inspect postgres_data --format '{{ .Mountpoint }}')

# 4. Check log sizes
du -sh backend/logs/
docker-compose logs --tail=0 | wc -l
```

**Solutions:**

**Solution 1: Clean Up Docker Resources**
```bash
# Remove unused containers, images, networks
docker system prune -a

# Remove unused volumes (CAREFUL - may delete data)
docker volume prune

# Remove old images
docker image prune -a --filter "until=720h"  # Older than 30 days
```

**Solution 2: Rotate Logs**
```bash
# Truncate large log files
truncate -s 0 backend/logs/app.log

# Configure log rotation in docker-compose.yml
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"

# Apply changes
docker-compose up -d --force-recreate
```

**Solution 3: Clean Up Old Data**
```bash
# Run data cleanup task
docker exec ai_review_backend python -c "
from app.tasks.data_cleanup import cleanup_old_analysis_results
cleanup_old_analysis_results.delay()
"

# Vacuum PostgreSQL
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "VACUUM FULL;"
```


---

## Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics

| Metric | Threshold | Alert Level | Action |
|--------|-----------|-------------|--------|
| API Error Rate | > 5% | Critical | Investigate errors immediately |
| API P95 Response Time | > 1s | Warning | Check database/cache performance |
| API P99 Response Time | > 2s | Critical | Immediate investigation |
| Request Rate | > 1000 req/s | Warning | Consider scaling |
| Active Users | > 500 | Info | Monitor capacity |

#### Infrastructure Metrics

| Metric | Threshold | Alert Level | Action |
|--------|-----------|-------------|--------|
| CPU Usage | > 80% | Warning | Investigate high CPU processes |
| CPU Usage | > 90% | Critical | Scale up or optimize |
| Memory Usage | > 85% | Warning | Check for memory leaks |
| Memory Usage | > 95% | Critical | Restart services or scale |
| Disk Usage | > 85% | Warning | Clean up old data |
| Disk Usage | > 95% | Critical | Immediate cleanup required |

#### Database Metrics

| Metric | Threshold | Alert Level | Action |
|--------|-----------|-------------|--------|
| PostgreSQL Connections | > 80 | Warning | Check connection pool |
| PostgreSQL Connections | > 95 | Critical | Kill idle connections |
| Query Response Time | > 500ms | Warning | Optimize slow queries |
| Cache Hit Rate | < 80% | Warning | Review caching strategy |
| Replication Lag | > 10s | Critical | Check replication health |

### Monitoring Setup

#### Docker Compose (Development/Staging)

**Prometheus + Grafana Setup:**

```bash
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

**Prometheus Configuration** (`monitoring/prometheus.yml`):

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

#### AWS Production

**CloudWatch Dashboards:**

```bash
# Create system health dashboard
aws cloudwatch put-dashboard \
  --dashboard-name ai-code-reviewer-prod-health \
  --dashboard-body file://monitoring/cloudwatch-dashboard-health.json

# Create performance dashboard
aws cloudwatch put-dashboard \
  --dashboard-name ai-code-reviewer-prod-performance \
  --dashboard-body file://monitoring/cloudwatch-dashboard-performance.json
```

**CloudWatch Alarms:**

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name prod-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts

# High response time alarm
aws cloudwatch put-metric-alarm \
  --alarm-name prod-high-response-time \
  --alarm-description "Alert when P95 response time exceeds 1 second" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 1.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts

# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name prod-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts

# Database connection alarm
aws cloudwatch put-metric-alarm \
  --alarm-name prod-db-connections-high \
  --alarm-description "Alert when database connections exceed 80" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:prod-alerts
```

### Alert Notification Channels

#### Email Notifications

```bash
# Create SNS topic
aws sns create-topic --name prod-alerts

# Subscribe email addresses
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:prod-alerts \
  --protocol email \
  --notification-endpoint ops-team@example.com

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:prod-alerts \
  --protocol email \
  --notification-endpoint oncall@example.com
```

#### Slack Notifications

**Using AWS Chatbot:**

1. Go to AWS Chatbot console
2. Configure Slack workspace
3. Create Slack channel (e.g., #production-alerts)
4. Link SNS topic to Slack channel

**Using Webhook (Alternative):**

```bash
# Add Lambda function to forward SNS to Slack
# See: monitoring/lambda/sns-to-slack.py

# Create Lambda function
aws lambda create-function \
  --function-name sns-to-slack \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://sns-to-slack.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-sns-to-slack

# Subscribe Lambda to SNS
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:prod-alerts \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:ACCOUNT:function:sns-to-slack
```

### Monitoring Dashboards

#### Grafana Dashboard (Docker Compose)

Access: http://localhost:3001

**Key Panels:**
- API Request Rate (requests/second)
- API Response Time (P50, P95, P99)
- Error Rate (%)
- Active Users
- Database Connections
- Cache Hit Rate
- CPU Usage (%)
- Memory Usage (%)
- Disk Usage (%)

#### CloudWatch Dashboard (AWS Production)

Access: AWS Console → CloudWatch → Dashboards

**System Health Dashboard:**
- Service Health Status
- Error Rate by Endpoint
- Active User Sessions
- Uptime Percentage

**Performance Dashboard:**
- API Response Time (P50, P95, P99)
- Request Throughput
- Database Query Performance
- Cache Hit/Miss Ratio

**Infrastructure Dashboard:**
- EC2 CPU Utilization
- EC2 Memory Utilization
- RDS CPU/Memory/Connections
- ElastiCache CPU/Memory/Evictions
- Auto Scaling Group Metrics

### Log Aggregation

#### Docker Compose

```bash
# View aggregated logs
docker-compose logs -f

# Filter by service
docker-compose logs -f backend frontend

# Search logs
docker-compose logs | grep -i "error"

# Export logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

#### AWS Production (CloudWatch Logs)

```bash
# Tail logs
aws logs tail /aws/ec2/ai-code-reviewer-prod --follow

# Filter logs
aws logs filter-log-events \
  --log-group-name /aws/ec2/ai-code-reviewer-prod \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# Query logs with CloudWatch Insights
aws logs start-query \
  --log-group-name /aws/ec2/ai-code-reviewer-prod \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20'
```

### Health Check Endpoints

#### Backend Health Check

```bash
# Basic health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00Z",
#   "version": "1.0.0",
#   "checks": {
#     "database": "healthy",
#     "redis": "healthy",
#     "neo4j": "healthy"
#   }
# }
```

#### Detailed Health Check

```bash
# Detailed health check with dependencies
curl http://localhost:8000/health/detailed

# Expected response:
# {
#   "status": "healthy",
#   "components": {
#     "database": {
#       "status": "healthy",
#       "response_time_ms": 5,
#       "connections": 12
#     },
#     "redis": {
#       "status": "healthy",
#       "response_time_ms": 2,
#       "memory_used_mb": 45
#     },
#     "neo4j": {
#       "status": "healthy",
#       "response_time_ms": 8,
#       "node_count": 1523
#     }
#   }
# }
```


---

## Backup and Restore Procedures

### Backup Strategy

**Backup Schedule:**
- **Production**: Daily at 02:00 UTC
- **Staging**: Daily at 03:00 UTC
- **Development**: Weekly (manual)

**Retention Policy:**
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

### PostgreSQL Backup

#### Manual Backup

```bash
# Full database backup
docker exec ai_review_postgres pg_dump -U postgres -Fc ai_code_reviewer > \
  backups/postgres_$(date +%Y%m%d_%H%M%S).dump

# SQL format backup (human-readable)
docker exec ai_review_postgres pg_dump -U postgres ai_code_reviewer > \
  backups/postgres_$(date +%Y%m%d_%H%M%S).sql

# Backup specific tables
docker exec ai_review_postgres pg_dump -U postgres -t users -t projects ai_code_reviewer > \
  backups/postgres_tables_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker exec ai_review_postgres pg_dump -U postgres ai_code_reviewer | gzip > \
  backups/postgres_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Automated Backup Script

```bash
#!/bin/bash
# File: scripts/backup-postgres.sh

BACKUP_DIR="backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/postgres_${TIMESTAMP}.dump"
RETENTION_DAYS=7

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Perform backup
docker exec ai_review_postgres pg_dump -U postgres -Fc ai_code_reviewer > ${BACKUP_FILE}

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup successful: ${BACKUP_FILE}"
    
    # Compress backup
    gzip ${BACKUP_FILE}
    
    # Upload to S3 (production)
    if [ "$ENVIRONMENT" = "production" ]; then
        aws s3 cp ${BACKUP_FILE}.gz s3://ai-code-reviewer-backups/postgres/${TIMESTAMP}.dump.gz
    fi
    
    # Clean up old backups
    find ${BACKUP_DIR} -name "*.dump.gz" -mtime +${RETENTION_DAYS} -delete
    
    echo "Backup completed successfully"
else
    echo "Backup failed!"
    exit 1
fi
```

#### Schedule Automated Backup

```bash
# Add to crontab
crontab -e

# Run daily at 2 AM
0 2 * * * /path/to/scripts/backup-postgres.sh >> /var/log/postgres-backup.log 2>&1
```

### PostgreSQL Restore

#### Restore from Backup

```bash
# Stop backend services
docker-compose stop backend celery_worker

# Drop existing database (DESTRUCTIVE)
docker exec ai_review_postgres psql -U postgres -c "DROP DATABASE IF EXISTS ai_code_reviewer;"

# Create new database
docker exec ai_review_postgres psql -U postgres -c "CREATE DATABASE ai_code_reviewer;"

# Restore from custom format backup
cat backups/postgres_20240115_020000.dump | \
  docker exec -i ai_review_postgres pg_restore -U postgres -d ai_code_reviewer

# Or restore from SQL backup
cat backups/postgres_20240115_020000.sql | \
  docker exec -i ai_review_postgres psql -U postgres -d ai_code_reviewer

# Restart services
docker-compose up -d backend celery_worker

# Verify restore
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "\dt"
```

#### Point-in-Time Recovery (AWS RDS)

```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier ai-code-reviewer-prod-postgres \
  --target-db-instance-identifier ai-code-reviewer-restored \
  --restore-time 2024-01-15T10:30:00Z

# Wait for restore to complete
aws rds wait db-instance-available \
  --db-instance-identifier ai-code-reviewer-restored

# Update application to use restored database
# Update DATABASE_URL in Secrets Manager
```

### Redis Backup

#### Manual Backup

```bash
# Trigger Redis save
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} BGSAVE

# Wait for save to complete
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} LASTSAVE

# Copy RDB file
docker cp ai_review_redis:/data/dump.rdb backups/redis_$(date +%Y%m%d_%H%M%S).rdb
```

#### Automated Backup Script

```bash
#!/bin/bash
# File: scripts/backup-redis.sh

BACKUP_DIR="backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"

mkdir -p ${BACKUP_DIR}

# Trigger background save
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} BGSAVE

# Wait for save to complete
sleep 5

# Copy RDB file
docker cp ai_review_redis:/data/dump.rdb ${BACKUP_FILE}

# Compress
gzip ${BACKUP_FILE}

echo "Redis backup completed: ${BACKUP_FILE}.gz"
```

### Redis Restore

```bash
# Stop Redis
docker-compose stop redis

# Copy backup to Redis data directory
docker cp backups/redis_20240115_020000.rdb ai_review_redis:/data/dump.rdb

# Start Redis
docker-compose up -d redis

# Verify data
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} DBSIZE
```

### Neo4j Backup

#### Manual Backup

```bash
# Export all data to Cypher statements
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} \
  "CALL apoc.export.cypher.all('backup.cypher', {format: 'cypher-shell'})" > \
  backups/neo4j_$(date +%Y%m%d_%H%M%S).cypher

# Or copy data directory (requires stopping Neo4j)
docker-compose stop neo4j
docker cp ai_review_neo4j:/data backups/neo4j_data_$(date +%Y%m%d_%H%M%S)
docker-compose up -d neo4j
```

#### Automated Backup Script

```bash
#!/bin/bash
# File: scripts/backup-neo4j.sh

BACKUP_DIR="backups/neo4j"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/neo4j_${TIMESTAMP}.cypher"

mkdir -p ${BACKUP_DIR}

# Export to Cypher
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} \
  "CALL apoc.export.cypher.all('/tmp/backup.cypher', {format: 'cypher-shell'})"

# Copy from container
docker cp ai_review_neo4j:/tmp/backup.cypher ${BACKUP_FILE}

# Compress
gzip ${BACKUP_FILE}

echo "Neo4j backup completed: ${BACKUP_FILE}.gz"
```

### Neo4j Restore

```bash
# Stop services using Neo4j
docker-compose stop backend celery_worker

# Clear existing data
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} \
  "MATCH (n) DETACH DELETE n"

# Restore from Cypher backup
gunzip -c backups/neo4j_20240115_020000.cypher.gz | \
  docker exec -i ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD}

# Restart services
docker-compose up -d backend celery_worker

# Verify restore
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} \
  "MATCH (n) RETURN count(n) AS node_count"
```

### Complete System Backup

```bash
#!/bin/bash
# File: scripts/backup-all.sh

BACKUP_ROOT="backups/full"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p ${BACKUP_DIR}

echo "Starting full system backup: ${TIMESTAMP}"

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
docker exec ai_review_postgres pg_dump -U postgres -Fc ai_code_reviewer > \
  ${BACKUP_DIR}/postgres.dump

# Backup Redis
echo "Backing up Redis..."
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} BGSAVE
sleep 5
docker cp ai_review_redis:/data/dump.rdb ${BACKUP_DIR}/redis.rdb

# Backup Neo4j
echo "Backing up Neo4j..."
docker exec ai_review_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD} \
  "CALL apoc.export.cypher.all('/tmp/backup.cypher', {format: 'cypher-shell'})"
docker cp ai_review_neo4j:/tmp/backup.cypher ${BACKUP_DIR}/neo4j.cypher

# Backup configuration
echo "Backing up configuration..."
cp .env ${BACKUP_DIR}/env.backup
cp docker-compose.yml ${BACKUP_DIR}/docker-compose.yml

# Create archive
echo "Creating archive..."
cd ${BACKUP_ROOT}
tar -czf ${TIMESTAMP}.tar.gz ${TIMESTAMP}/
rm -rf ${TIMESTAMP}/

# Upload to S3 (production)
if [ "$ENVIRONMENT" = "production" ]; then
    aws s3 cp ${TIMESTAMP}.tar.gz s3://ai-code-reviewer-backups/full/${TIMESTAMP}.tar.gz
fi

echo "Full system backup completed: ${BACKUP_ROOT}/${TIMESTAMP}.tar.gz"
```

### Backup Verification

```bash
#!/bin/bash
# File: scripts/verify-backup.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

echo "Verifying backup: ${BACKUP_FILE}"

# Test PostgreSQL backup
if [[ $BACKUP_FILE == *.dump ]]; then
    pg_restore --list ${BACKUP_FILE} > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ PostgreSQL backup is valid"
    else
        echo "✗ PostgreSQL backup is corrupted"
        exit 1
    fi
fi

# Test Redis backup
if [[ $BACKUP_FILE == *.rdb ]]; then
    redis-check-rdb ${BACKUP_FILE}
    if [ $? -eq 0 ]; then
        echo "✓ Redis backup is valid"
    else
        echo "✗ Redis backup is corrupted"
        exit 1
    fi
fi

echo "Backup verification completed successfully"
```

### Disaster Recovery

For complete disaster recovery procedures, see:
- **Disaster Recovery Plan**: `docs/DISASTER_RECOVERY_PLAN.md`
- **DR Procedures**: `terraform/DISASTER_RECOVERY_PROCEDURES.md`
- **DR Quick Reference**: `terraform/DR_QUICK_REFERENCE.md`

**Quick DR Steps:**

1. **Assess Disaster Scope**
2. **Activate DR Team**
3. **Restore from Latest Backups**
4. **Verify Data Integrity**
5. **Update DNS to DR Environment**
6. **Monitor and Validate**


---

## Performance Optimization

### Database Performance

#### Identify Slow Queries

```bash
# Enable pg_stat_statements extension
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c \
  "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# View slowest queries
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;"

# Reset statistics
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c \
  "SELECT pg_stat_statements_reset();"
```

#### Add Missing Indexes

```bash
# Identify missing indexes
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats
WHERE schemaname = 'public'
AND n_distinct > 100
ORDER BY n_distinct DESC;"

# Create indexes
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
CREATE INDEX CONCURRENTLY idx_projects_user_id ON projects(user_id);
CREATE INDEX CONCURRENTLY idx_analysis_results_project_id ON analysis_results(project_id);
CREATE INDEX CONCURRENTLY idx_code_entities_file_path ON code_entities(file_path);
CREATE INDEX CONCURRENTLY idx_audit_logs_user_id_timestamp ON audit_logs(user_id, timestamp);"
```

#### Optimize Connection Pool

```bash
# Check current connections
docker exec ai_review_postgres psql -U postgres -c "
SELECT 
  count(*) as total_connections,
  state,
  wait_event_type
FROM pg_stat_activity
GROUP BY state, wait_event_type;"

# Tune connection pool in backend
# Edit backend/app/database/session.py
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=20,        # Base connections
#     max_overflow=10,     # Additional connections under load
#     pool_pre_ping=True,  # Verify connections
#     pool_recycle=3600    # Recycle every hour
# )
```

#### Vacuum and Analyze

```bash
# Analyze tables for query planner
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "ANALYZE;"

# Vacuum to reclaim space
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "VACUUM;"

# Full vacuum (requires exclusive lock)
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "VACUUM FULL;"

# Auto-vacuum settings
docker exec ai_review_postgres psql -U postgres -c "
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_naptime = '1min';
SELECT pg_reload_conf();"
```

### Cache Optimization

#### Monitor Cache Performance

```bash
# Check Redis memory usage
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO memory

# Check cache hit rate
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO stats | grep keyspace

# Calculate hit rate
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} INFO stats | \
  awk '/keyspace_hits|keyspace_misses/ {print}' | \
  awk '{sum+=$2} END {print "Hit rate:", (NR>0 ? sum/NR*100 : 0) "%"}'

# Check top keys by memory
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} --bigkeys
```

#### Optimize Cache Strategy

```bash
# Set appropriate TTL for cached data
# Short-lived data (5 minutes)
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} SETEX user:session:123 300 "session_data"

# Medium-lived data (1 hour)
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} SETEX api:response:projects 3600 "cached_response"

# Long-lived data (24 hours)
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} SETEX analysis:result:456 86400 "analysis_data"

# Configure eviction policy
# Edit docker-compose.yml
# command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

#### Cache Warming

```bash
# Warm up cache after restart
curl http://localhost:8000/api/v1/projects  # Cache projects
curl http://localhost:8000/api/v1/users/me  # Cache user data

# Automated cache warming script
#!/bin/bash
# File: scripts/warm-cache.sh

echo "Warming up cache..."

# Warm up common endpoints
curl -s http://localhost:8000/api/v1/projects > /dev/null
curl -s http://localhost:8000/api/v1/analysis/recent > /dev/null

echo "Cache warming completed"
```

### Application Performance

#### Profile API Endpoints

```bash
# Enable profiling in backend
# Add middleware to measure request time

# View slowest endpoints
docker-compose logs backend | grep "Request completed" | \
  awk '{print $NF, $(NF-1)}' | sort -rn | head -20

# Profile specific endpoint
time curl -X GET http://localhost:8000/api/v1/projects
```

#### Optimize Background Tasks

```bash
# Check Celery task performance
docker exec ai_review_celery celery -A app.celery_config inspect stats

# Monitor task execution time
docker-compose logs celery_worker | grep "Task.*succeeded" | \
  awk '{print $NF}' | sort -rn | head -10

# Increase worker concurrency
# Edit docker-compose.yml
# command: celery -A app.celery_config worker --concurrency=4
```

#### Reduce Response Size

```bash
# Enable gzip compression in backend
# Add middleware in backend/app/main.py
# from fastapi.middleware.gzip import GZipMiddleware
# app.add_middleware(GZipMiddleware, minimum_size=1000)

# Paginate large responses
# Add pagination to API endpoints
# GET /api/v1/projects?page=1&per_page=20
```

### Frontend Performance

#### Optimize Bundle Size

```bash
# Analyze bundle size
cd frontend
npm run build
npm run analyze

# Check bundle sizes
ls -lh .next/static/chunks/

# Optimize images
# Use next/image component for automatic optimization
```

#### Enable Caching

```bash
# Configure Next.js caching
# Edit next.config.js
# module.exports = {
#   async headers() {
#     return [
#       {
#         source: '/static/:path*',
#         headers: [
#           {
#             key: 'Cache-Control',
#             value: 'public, max-age=31536000, immutable',
#           },
#         ],
#       },
#     ]
#   },
# }
```

### Network Performance

#### Enable HTTP/2

```bash
# Configure Nginx for HTTP/2
# Edit nginx/nginx.conf
# listen 443 ssl http2;
```

#### Configure CDN

```bash
# Use CloudFront for static assets (AWS)
aws cloudfront create-distribution \
  --origin-domain-name app.example.com \
  --default-root-object index.html

# Update frontend to use CDN URLs
# NEXT_PUBLIC_CDN_URL=https://d123456.cloudfront.net
```

### Resource Limits

#### Optimize Container Resources

```bash
# Monitor resource usage
docker stats --no-stream

# Adjust limits in docker-compose.yml based on actual usage
# deploy:
#   resources:
#     limits:
#       memory: 1G
#       cpus: '1'
#     reservations:
#       memory: 512M
#       cpus: '0.5'
```


---

## Security Operations

### Security Monitoring

#### Check for Security Vulnerabilities

```bash
# Scan Docker images
docker scan ai_review_backend
docker scan ai_review_frontend

# Scan Python dependencies
cd backend
pip-audit

# Scan Node.js dependencies
cd frontend
npm audit
npm audit fix

# Run OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000 \
  -r zap-report.html
```

#### Monitor Failed Login Attempts

```bash
# Check audit logs for failed logins
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  timestamp,
  user_id,
  action,
  ip_address,
  details
FROM audit_logs
WHERE action = 'login_failed'
AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 20;"

# Check for brute force attempts
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  ip_address,
  COUNT(*) as failed_attempts
FROM audit_logs
WHERE action = 'login_failed'
AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;"
```

#### Review Access Logs

```bash
# Check recent API access
docker-compose logs backend | grep "GET\|POST\|PUT\|DELETE" | tail -100

# Check for suspicious patterns
docker-compose logs backend | grep -E "401|403|404|500" | tail -50

# Check for SQL injection attempts
docker-compose logs backend | grep -i "select\|union\|drop\|insert" | grep -v "INFO"
```

### Access Management

#### User Management

```bash
# List all users
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT id, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;"

# Disable user account
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
UPDATE users SET is_active = false WHERE email = 'user@example.com';"

# Reset user password
docker exec ai_review_backend python -c "
from app.services.auth import hash_password
print(hash_password('new_password'))
"

# Update password in database
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
UPDATE users SET password_hash = '<hashed_password>' WHERE email = 'user@example.com';"
```

#### Role Management

```bash
# List user roles
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT u.email, r.name as role
FROM users u
JOIN roles r ON u.role_id = r.id
ORDER BY r.name, u.email;"

# Change user role
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
UPDATE users 
SET role_id = (SELECT id FROM roles WHERE name = 'admin')
WHERE email = 'user@example.com';"
```

### SSL/TLS Management

#### Check Certificate Expiration

```bash
# Check certificate expiration (AWS ACM)
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID \
  --query 'Certificate.[DomainName,NotAfter]'

# Check local certificate
openssl x509 -in nginx/ssl/cert.pem -noout -dates

# Set up expiration alert (30 days before)
aws cloudwatch put-metric-alarm \
  --alarm-name ssl-cert-expiring \
  --alarm-description "SSL certificate expiring in 30 days" \
  --metric-name DaysToExpiry \
  --namespace AWS/CertificateManager \
  --statistic Minimum \
  --period 86400 \
  --threshold 30 \
  --comparison-operator LessThanThreshold
```

#### Renew SSL Certificate

```bash
# Request new certificate (AWS ACM)
aws acm request-certificate \
  --domain-name app.example.com \
  --validation-method DNS

# Or use Let's Encrypt (local)
certbot certonly --standalone -d app.example.com

# Update Nginx configuration
cp /etc/letsencrypt/live/app.example.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/app.example.com/privkey.pem nginx/ssl/key.pem

# Reload Nginx
docker-compose exec nginx nginx -s reload
```

### Secrets Management

#### Rotate Secrets

```bash
# Generate new JWT secret
NEW_JWT_SECRET=$(openssl rand -base64 64)

# Update in .env file
sed -i "s/JWT_SECRET=.*/JWT_SECRET=${NEW_JWT_SECRET}/" .env

# Update in AWS Secrets Manager (production)
aws secretsmanager update-secret \
  --secret-id ai-code-reviewer/prod/backend \
  --secret-string "{\"JWT_SECRET\": \"${NEW_JWT_SECRET}\"}"

# Restart services
docker-compose restart backend

# Invalidate all existing tokens
docker exec ai_review_redis redis-cli -a ${REDIS_PASSWORD} FLUSHDB
```

#### Rotate Database Passwords

```bash
# Generate new password
NEW_DB_PASSWORD=$(openssl rand -base64 32)

# Update PostgreSQL password
docker exec ai_review_postgres psql -U postgres -c \
  "ALTER USER postgres WITH PASSWORD '${NEW_DB_PASSWORD}';"

# Update .env file
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${NEW_DB_PASSWORD}/" .env

# Update DATABASE_URL
sed -i "s|postgresql://postgres:.*@|postgresql://postgres:${NEW_DB_PASSWORD}@|" .env

# Restart services
docker-compose restart backend celery_worker
```

### Audit Logging

#### Query Audit Logs

```bash
# View recent audit events
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  timestamp,
  user_id,
  action,
  resource_type,
  resource_id,
  ip_address
FROM audit_logs
ORDER BY timestamp DESC
LIMIT 50;"

# Export audit logs for compliance
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
COPY (
  SELECT * FROM audit_logs
  WHERE timestamp >= '2024-01-01'
  AND timestamp < '2024-02-01'
) TO STDOUT WITH CSV HEADER" > audit_logs_jan2024.csv
```

#### Monitor Suspicious Activity

```bash
# Check for privilege escalation attempts
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT *
FROM audit_logs
WHERE action LIKE '%role%'
OR action LIKE '%permission%'
ORDER BY timestamp DESC
LIMIT 20;"

# Check for data export attempts
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT *
FROM audit_logs
WHERE action = 'data_export'
ORDER BY timestamp DESC
LIMIT 20;"
```

---

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| **P1 - Critical** | Complete outage, data loss | 15 minutes | Immediate |
| **P2 - High** | Major feature broken, high error rate | 1 hour | 30 minutes |
| **P3 - Medium** | Minor feature broken, degraded performance | 4 hours | 2 hours |
| **P4 - Low** | Cosmetic issue, no user impact | 24 hours | N/A |

### Incident Response Workflow

1. **Detect**: Alert triggered or issue reported
2. **Assess**: Determine severity and impact
3. **Respond**: Execute appropriate runbook
4. **Communicate**: Update stakeholders
5. **Resolve**: Fix the issue
6. **Document**: Create incident report
7. **Review**: Post-mortem meeting

### Incident Communication

#### Status Page Updates

```bash
# Update status page (example using Statuspage.io API)
curl -X PATCH https://api.statuspage.io/v1/pages/PAGE_ID/incidents/INCIDENT_ID \
  -H "Authorization: OAuth YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "status": "investigating",
      "body": "We are investigating reports of slow response times."
    }
  }'
```

#### Slack Notifications

```bash
# Send incident notification to Slack
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚨 P1 INCIDENT: Complete service outage",
    "attachments": [{
      "color": "danger",
      "fields": [
        {"title": "Severity", "value": "P1 - Critical", "short": true},
        {"title": "Status", "value": "Investigating", "short": true},
        {"title": "Impact", "value": "All users affected"},
        {"title": "Incident Commander", "value": "@john.doe"}
      ]
    }]
  }'
```

### Post-Incident Review

#### Incident Report Template

```markdown
# Incident Report: [Brief Description]

**Date**: 2024-01-15
**Severity**: P1 - Critical
**Duration**: 2 hours 15 minutes
**Incident Commander**: John Doe

## Summary
Brief description of what happened.

## Timeline
- 10:00 UTC: Alert triggered for high error rate
- 10:05 UTC: Incident declared, team notified
- 10:15 UTC: Root cause identified (database connection pool exhausted)
- 10:30 UTC: Fix deployed (increased pool size)
- 11:00 UTC: Service restored
- 12:15 UTC: Monitoring confirmed stable

## Root Cause
Detailed explanation of what caused the incident.

## Impact
- Users affected: ~500 active users
- Requests failed: ~2,000 requests
- Revenue impact: Estimated $X

## Resolution
Steps taken to resolve the incident.

## Action Items
- [ ] Increase connection pool size (Owner: DevOps, Due: 2024-01-20)
- [ ] Add alert for connection pool usage (Owner: DevOps, Due: 2024-01-22)
- [ ] Update runbook with this scenario (Owner: Ops, Due: 2024-01-25)

## Lessons Learned
What we learned and how to prevent similar incidents.
```

---

## Maintenance Procedures

### Scheduled Maintenance

#### Maintenance Window

**Standard Maintenance Window:**
- **Day**: Sunday
- **Time**: 02:00 - 06:00 UTC (low traffic period)
- **Frequency**: Monthly (first Sunday)

#### Pre-Maintenance Checklist

- [ ] Schedule maintenance window (7 days notice)
- [ ] Notify users via email and status page
- [ ] Create backup of all databases
- [ ] Test changes in staging environment
- [ ] Prepare rollback plan
- [ ] Verify on-call engineer availability
- [ ] Update runbook with maintenance steps

#### Maintenance Procedure

```bash
# 1. Enable maintenance mode
docker-compose exec nginx nginx -s reload  # Load maintenance page

# 2. Stop accepting new requests
docker-compose stop frontend

# 3. Wait for in-flight requests to complete
sleep 60

# 4. Stop backend services
docker-compose stop backend celery_worker

# 5. Perform maintenance (e.g., database migration)
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -f migration.sql

# 6. Start services
docker-compose up -d backend celery_worker frontend

# 7. Verify health
./scripts/health-check-all.sh

# 8. Disable maintenance mode
docker-compose exec nginx nginx -s reload

# 9. Monitor for issues
docker-compose logs -f
```

### Database Maintenance

#### Routine Maintenance Tasks

```bash
# Weekly: Analyze tables
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "ANALYZE;"

# Monthly: Vacuum database
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "VACUUM;"

# Quarterly: Reindex
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "REINDEX DATABASE ai_code_reviewer;"

# Check for bloat
docker exec ai_review_postgres psql -U postgres -d ai_code_reviewer -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;"
```

### Log Rotation

```bash
# Configure log rotation
cat > /etc/logrotate.d/ai-code-reviewer <<EOF
/var/log/ai-code-reviewer/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        docker-compose restart backend
    endscript
}
EOF

# Test log rotation
logrotate -f /etc/logrotate.d/ai-code-reviewer
```

---

## Related Documentation

- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Disaster Recovery Plan**: `docs/DISASTER_RECOVERY_PLAN.md`
- **Architecture Documentation**: `docs/architecture/`
- **API Documentation**: `http://localhost:8000/docs`
- **Monitoring Dashboards**: `http://localhost:3001` (Grafana)

---

## Document Maintenance

**Review Schedule**: Quarterly  
**Next Review**: 2024-04-15  
**Owner**: Operations Team  
**Contact**: ops@example.com

**Change Log**:

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 1.0 | Initial operations runbook | Operations Team |

---

**END OF OPERATIONS RUNBOOK**

For emergency support, contact the on-call engineer via PagerDuty or check the #production-alerts Slack channel.
