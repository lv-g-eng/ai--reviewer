# API Gateway - Deployment Guide

> Step-by-step guide for deploying the API Gateway to various environments

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Docker Compose](#docker-compose)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Platforms](#cloud-platforms)
7. [Production Checklist](#production-checklist)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required
- Node.js 18.x or higher
- Redis 6.x or higher
- Docker (for containerized deployment)
- Git

### Optional
- Kubernetes cluster (for K8s deployment)
- Cloud provider account (AWS, GCP, Azure)
- CI/CD pipeline (GitHub Actions, GitLab CI)

---

## Local Development

### 1. Clone Repository

```bash
git clone <repository-url>
cd services/api-gateway
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Minimum Required Configuration**:
```bash
PORT=3000
NODE_ENV=development
JWT_SECRET=dev-secret-key
REDIS_URL=redis://localhost:6379
```

### 4. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Or using local Redis
redis-server
```

### 5. Start Gateway

```bash
# Development mode (hot reload)
npm run dev

# Or build and run
npm run build
npm start
```

### 6. Verify

```bash
curl http://localhost:3000/health
```

---

## Docker Deployment

### Build Image

```bash
# Build Docker image
docker build -t api-gateway:1.0.0 .

# Tag for registry
docker tag api-gateway:1.0.0 your-registry/api-gateway:1.0.0
```

### Run Container

```bash
docker run -d \
  --name api-gateway \
  -p 3000:3000 \
  --env-file .env \
  --restart unless-stopped \
  api-gateway:1.0.0
```

### With Environment Variables

```bash
docker run -d \
  --name api-gateway \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e PORT=3000 \
  -e JWT_SECRET=your-secret \
  -e REDIS_URL=redis://redis:6379 \
  -e AUTH_SERVICE_URL=http://auth-service:3001 \
  --restart unless-stopped \
  api-gateway:1.0.0
```

### View Logs

```bash
# Follow logs
docker logs -f api-gateway

# Last 100 lines
docker logs --tail 100 api-gateway
```

### Stop/Remove

```bash
# Stop container
docker stop api-gateway

# Remove container
docker rm api-gateway
```

---

## Docker Compose

### Basic Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - JWT_SECRET=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
      - AUTH_SERVICE_URL=http://auth-service:3001
      - CODE_REVIEW_ENGINE_URL=http://ai-service:3002
      - ARCHITECTURE_ANALYZER_URL=http://architecture-analyzer:3003
      - AGENTIC_AI_URL=http://ai-service:3004
      - PROJECT_MANAGER_URL=http://project-manager:3005
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - app-network

volumes:
  redis-data:

networks:
  app-network:
    driver: bridge
```

### Deploy

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api-gateway

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Scale Gateway

```bash
# Run 3 instances
docker-compose up -d --scale api-gateway=3
```

---

## Kubernetes Deployment

### 1. Create Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: api-gateway
```

```bash
kubectl apply -f namespace.yaml
```

### 2. Create Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-gateway-secrets
  namespace: api-gateway
type: Opaque
stringData:
  jwt-secret: your-super-secret-jwt-key
  redis-url: redis://redis:6379
```

```bash
kubectl apply -f secrets.yaml
```

### 3. Create ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-gateway-config
  namespace: api-gateway
data:
  NODE_ENV: "production"
  PORT: "3000"
  LOG_LEVEL: "warn"
  AUTH_SERVICE_URL: "http://auth-service:3001"
  CODE_REVIEW_ENGINE_URL: "http://ai-service:3002"
  ARCHITECTURE_ANALYZER_URL: "http://architecture-analyzer:3003"
  AGENTIC_AI_URL: "http://ai-service:3004"
  PROJECT_MANAGER_URL: "http://project-manager:3005"
```

```bash
kubectl apply -f configmap.yaml
```

### 4. Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: your-registry/api-gateway:1.0.0
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: api-gateway-config
        env:
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: api-gateway-secrets
              key: jwt-secret
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: api-gateway-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

```bash
kubectl apply -f deployment.yaml
```

### 5. Create Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: api-gateway
spec:
  selector:
    app: api-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

```bash
kubectl apply -f service.yaml
```

### 6. Create Ingress (Optional)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway
  namespace: api-gateway
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: api-gateway-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
```

```bash
kubectl apply -f ingress.yaml
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n api-gateway

# Check service
kubectl get svc -n api-gateway

# View logs
kubectl logs -f deployment/api-gateway -n api-gateway

# Check health
kubectl port-forward svc/api-gateway 3000:80 -n api-gateway
curl http://localhost:3000/health
```

---

## Cloud Platforms

### AWS (ECS/Fargate)

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name api-gateway
```

2. **Push Image**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag api-gateway:1.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/api-gateway:1.0.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/api-gateway:1.0.0
```

3. **Create Task Definition** (use AWS Console or CLI)

4. **Create ECS Service**

### Google Cloud (Cloud Run)

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/api-gateway

# Deploy
gcloud run deploy api-gateway \
  --image gcr.io/PROJECT_ID/api-gateway \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NODE_ENV=production,JWT_SECRET=secret
```

### Azure (Container Instances)

```bash
# Create resource group
az group create --name api-gateway-rg --location eastus

# Create container
az container create \
  --resource-group api-gateway-rg \
  --name api-gateway \
  --image your-registry/api-gateway:1.0.0 \
  --dns-name-label api-gateway \
  --ports 3000 \
  --environment-variables NODE_ENV=production JWT_SECRET=secret
```

---

## Production Checklist

### Pre-Deployment

- [ ] Update `.env` with production values
- [ ] Change `JWT_SECRET` to strong random value
- [ ] Set `NODE_ENV=production`
- [ ] Configure production service URLs
- [ ] Set appropriate `CORS_ALLOWED_ORIGINS`
- [ ] Configure rate limiting for production load
- [ ] Set `LOG_LEVEL=warn` or `LOG_LEVEL=error`
- [ ] Enable `TRUST_PROXY` if behind load balancer
- [ ] Configure Redis with authentication
- [ ] Review circuit breaker settings
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring tools

### Security

- [ ] JWT secret is strong and unique
- [ ] All secrets are in environment variables (not code)
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Helmet security headers are enabled
- [ ] Redis has authentication
- [ ] All service URLs use HTTPS
- [ ] Firewall rules are configured
- [ ] Security scanning completed

### Testing

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Property-based tests pass
- [ ] Performance tests meet requirements
- [ ] Load testing completed
- [ ] Security testing completed
- [ ] Manual testing in staging

### Infrastructure

- [ ] Redis cluster is set up
- [ ] Load balancer is configured
- [ ] Auto-scaling is configured
- [ ] Health checks are working
- [ ] Logging is configured
- [ ] Monitoring is set up
- [ ] Alerts are configured
- [ ] Backup strategy is in place

### Documentation

- [ ] README is up to date
- [ ] API documentation is complete
- [ ] Deployment guide is current
- [ ] Runbook is prepared
- [ ] Team is trained

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check gateway health
curl https://api.example.com/health

# Expected response
{
  "status": "healthy",
  "services": {
    "auth": "healthy",
    ...
  }
}
```

### Logs

```bash
# Docker
docker logs -f api-gateway

# Kubernetes
kubectl logs -f deployment/api-gateway -n api-gateway

# Local
tail -f logs/combined.log
```

### Metrics to Monitor

- Request rate (req/s)
- Response time (avg, p95, p99)
- Error rate (%)
- Circuit breaker state
- Rate limit hits
- Memory usage
- CPU usage
- Redis connection status

### Alerts

Set up alerts for:
- High error rate (>5%)
- High response time (>1s)
- Circuit breaker open
- High memory usage (>80%)
- Redis connection failures
- Service health check failures

### Maintenance

**Regular Tasks**:
- Review logs weekly
- Update dependencies monthly
- Rotate secrets quarterly
- Review and optimize configuration
- Performance testing before major releases

**Updates**:
```bash
# Pull latest code
git pull origin main

# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build

# Deploy
# (use your deployment method)
```

---

**Last Updated**: January 24, 2026  
**Version**: 1.0.0
