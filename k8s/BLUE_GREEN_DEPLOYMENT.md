# Blue-Green Deployment for AI Code Review Platform

This document describes the blue-green deployment strategy for the AI Code Review Platform.

## Overview

Blue-green deployment allows for zero-downtime deployments by maintaining two identical production environments:

- **Blue**: Current production environment
- **Green**: New version to be deployed

## Architecture

```
                    ┌─────────────┐
                    │   User      │
                    └──────┬──────┘
                           │
                    ┌────────▼────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                           │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
      ┌─────▼─────┐      │          ┌─────▼─────┐
      │   Blue     │      │          │   Green    │
      │  (v1.0)   │      │          │  (v1.1)   │
      └────────────┘      │          └────────────┘
            │                  │                  │
      ┌─────▼─────┐      │          ┌─────▼─────┐
      │  Postgres  │      │          │  Postgres  │
      │  (Primary) │      │          │ (Replica) │
      └────────────┘      │          └────────────┘
            │                  │                  │
      ┌─────▼─────┐      │          ┌─────▼─────┐
      │   Redis    │      │          │   Redis    │
      │  (Primary) │      │          │  (Replica) │
      └────────────┘      │          └────────────┘
                           │
                    ┌──────▼──────┐
                    │  Shared DB  │
                    │   (Neo4j)  │
                    └─────────────┘
```

## Prerequisites

- Kubernetes cluster with at least 3 nodes
- Storage provisioner with ReadWriteMany access
- Ingress controller (NGINX recommended)
- GitOps tool (ArgoCD or Flux recommended)

## Deployment Process

### Phase 1: Prepare Green Environment

```bash
# 1. Create green namespace
kubectl create namespace ai-review-green

# 2. Deploy green environment
kubectl apply -f k8s/ --namespace=ai-review-green

# 3. Wait for green environment to be ready
kubectl wait --for=condition=available --timeout=5m \
  deployment/backend -n ai-review-green
kubectl wait --for=condition=available --timeout=5m \
  deployment/frontend -n ai-review-green
```

### Phase 2: Health Check

```bash
# Check green environment health
kubectl get pods -n ai-review-green
kubectl exec -n ai-review-green deployment/backend -- \
  curl http://localhost:8000/health

# Check database connections
kubectl exec -n ai-review-green deployment/backend -- \
  python -c "from app.database.postgresql import engine; print(engine.url)"
```

### Phase 3: Switch Traffic

```yaml
# Update ingress to route traffic to green
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-review-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: '100' # 100% to green
spec:
  rules:
    - host: api.ai-review.com
      http:
        paths:
          - path: /
            backend:
              service:
                name: ai-review-green-backend
                port:
                  number: 8000
```

### Phase 4: Monitor

```bash
# Monitor green environment for issues
kubectl logs -f deployment/backend -n ai-review-green
kubectl logs -f deployment/frontend -n ai-review-green

# Check metrics
kubectl top pods -n ai-review-green
kubectl top nodes
```

### Phase 5: Rollback (if needed)

```bash
# If issues detected, switch back to blue
kubectl annotate ingress ai-review-ingress \
  nginx.ingress.kubernetes.io/canary="0"  # 100% to blue

# Remove green environment
kubectl delete namespace ai-review-green
```

## Kubernetes Manifests

### Backend Deployment (Blue)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-blue
  namespace: ai-review-blue
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
      version: blue
  template:
    metadata:
      labels:
        app: backend
        version: blue
    spec:
      containers:
        - name: backend
          image: ghcr.io/your-org/ai-review-backend:v1.0
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: 'production'
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-secret
                  key: url
          resources:
            requests:
              memory: '1Gi'
              cpu: '1'
            limits:
              memory: '2Gi'
              cpu: '2'
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

### Backend Deployment (Green)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-green
  namespace: ai-review-green
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
      version: green
  template:
    metadata:
      labels:
        app: backend
        version: green
    spec:
      containers:
        - name: backend
          image: ghcr.io/your-org/ai-review-backend:v1.1
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: 'production'
          resources:
            requests:
              memory: '1Gi'
              cpu: '1'
            limits:
              memory: '2Gi'
              cpu: '2'
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

### Service (Blue and Green)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-blue
  namespace: ai-review-blue
spec:
  selector:
    app: backend
    version: blue
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: backend-green
  namespace: ai-review-green
spec:
  selector:
    app: backend
    version: green
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

### Ingress with Traffic Split

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-review-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: '50' # 50% blue, 50% green
    nginx.ingress.kubernetes.io/canary-by-header: 'x-canary: always'
spec:
  rules:
    - host: api.ai-review.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend-blue
                port:
                  number: 8000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend-green
                port:
                  number: 8000
```

## Deployment Scripts

### Automated Deployment Script

```bash
#!/bin/bash
# deploy-blue-green.sh

set -e

BLUE_VERSION="${1:-v1.0}"
GREEN_VERSION="${2:-v1.1}"

echo "Deploying Blue-Green: Blue=$BLUE_VERSION, Green=$GREEN_VERSION"

# 1. Tag and push images
echo "Tagging images..."
docker tag ai-review-backend:$BLUE_VERSION ai-review-backend:blue
docker tag ai-review-backend:$GREEN_VERSION ai-review-backend:green
docker tag ai-review-frontend:$BLUE_VERSION ai-review-frontend:blue
docker tag ai-review-frontend:$GREEN_VERSION ai-review-frontend:green

docker push ai-review-backend:blue
docker push ai-review-backend:green
docker push ai-review-frontend:blue
docker push ai-review-frontend:green

# 2. Deploy green environment
echo "Deploying green environment..."
kubectl apply -f k8s/green/ --namespace=ai-review-green

# 3. Wait for green to be ready
echo "Waiting for green environment..."
kubectl wait --for=condition=available --timeout=10m \
  deployment/backend-green -n ai-review-green
kubectl wait --for=condition=available --timeout=10m \
  deployment/frontend-green -n ai-review-green

# 4. Health check
echo "Health checking green environment..."
sleep 10

GREEN_HEALTH=$(kubectl exec -n ai-review-green deployment/backend-green -- \
  curl -s http://localhost:8000/health | jq -r '.status')

if [ "$GREEN_HEALTH" != "healthy" ]; then
  echo "Green environment health check failed!"
  echo "Rolling back to blue..."
  kubectl annotate ingress ai-review-ingress \
    nginx.ingress.kubernetes.io/canary="0"
  exit 1
fi

echo "Green environment is healthy!"

# 5. Gradual traffic shift
echo "Shifting traffic to green..."
for percentage in 10 25 50 75 100; do
  kubectl annotate ingress ai-review-ingress \
    nginx.ingress.kubernetes.io/canary="$percentage"
  echo "Traffic: $percentage% to green"
  sleep 30
done

echo "Deployment complete! 100% traffic to green version $GREEN_VERSION"

# 6. Optional: Remove old blue after stabilization period
# echo "Waiting for stabilization period..."
# sleep 1800  # 30 minutes
# echo "Removing old blue environment..."
# kubectl delete namespace ai-review-blue
```

### Rollback Script

```bash
#!/bin/bash
# rollback.sh

set -e

echo "Rolling back to blue environment..."

# 1. Switch all traffic to blue
kubectl annotate ingress ai-review-ingress \
  nginx.ingress.kubernetes.io/canary="0"

# 2. Remove green environment
echo "Removing green environment..."
kubectl delete namespace ai-review-green --timeout=60s

echo "Rollback complete!"
```

## Monitoring

### Metrics to Monitor

1. **Response Time**: Average API response time
2. **Error Rate**: 5xx errors per minute
3. **Throughput**: Requests per second
4. **Database Connections**: Active database connections
5. **CPU/Memory Usage**: Resource utilization

### Alerting Rules

```yaml
groups:
  - name: blue-green-deployment
    rules:
      - alert: HighErrorRateGreen
        expr: |
          rate(http_requests_total{version="green",status=~"5.."}[5m]) > 10
        for: 10m
        labels:
          severity: critical
          environment: green
        annotations:
          summary: 'High error rate in green environment'
          description: 'Green environment experiencing high error rate, consider rollback'

      - alert: SlowResponseTimeGreen
        expr: |
          histogram_quantile(0.95, http_request_duration_seconds{version="green"}) > 1
        for: 5m
        labels:
          severity: warning
          environment: green
        annotations:
          summary: 'Slow response time in green environment'
          description: '95th percentile response time > 1s in green environment'
```

## Best Practices

1. **Database Migrations**: Run migrations on blue environment before green deployment
2. **Data Consistency**: Ensure both environments can read/write to the same database
3. **Monitoring**: Monitor both environments during deployment
4. **Rollback Plan**: Have a tested rollback plan ready
5. **Testing**: Test green environment thoroughly before switching traffic
6. **Stabilization Period**: Wait for stabilization period before removing blue

## Troubleshooting

### Green Environment Not Starting

```bash
# Check pod status
kubectl get pods -n ai-review-green

# Check pod logs
kubectl logs -f deployment/backend-green -n ai-review-green

# Describe pod for details
kubectl describe pod <pod-name> -n ai-review-green
```

### Traffic Not Switching

```bash
# Check ingress configuration
kubectl get ingress ai-review-ingress -o yaml

# Check nginx ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Database Connection Issues

```bash
# Check database services
kubectl get svc -n ai-review-blue
kubectl get svc -n ai-review-green

# Check database endpoints
kubectl get endpoints -n ai-review-blue
kubectl get endpoints -n ai-review-green
```

## Cost Considerations

- **Infrastructure Cost**: Running both blue and green temporarily doubles infrastructure cost
- **Storage Cost**: Additional storage for green environment
- **Network Cost**: Additional network traffic during deployment
- **Recommendation**: Keep deployment window short (30-60 minutes）

---

**Last Updated**: 2026-03-09
**Version**: 1.0
