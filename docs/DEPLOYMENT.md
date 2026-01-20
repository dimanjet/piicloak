# PIICloak Deployment Guide

Production deployment guides for various platforms.

---

## Quick Deployment Options

| Platform | Complexity | Time | Best For |
|----------|------------|------|----------|
| Docker | ⭐ Easy | 5 min | Quick start, testing |
| Docker Compose | ⭐ Easy | 10 min | Single server deployment |
| Kubernetes | ⭐⭐⭐ Advanced | 30 min | Production, scaling |
| AWS ECS | ⭐⭐ Medium | 20 min | AWS infrastructure |
| GCP Cloud Run | ⭐ Easy | 15 min | Serverless, auto-scaling |
| Azure Container | ⭐⭐ Medium | 20 min | Azure infrastructure |

---

## Docker Deployment

### Basic Docker

```bash
# Build
docker build -t piicloak .

# Run
docker run -d \
  --name piicloak \
  -p 8000:8000 \
  -e PIICLOAK_API_KEY=your-secret-key \
  --restart unless-stopped \
  piicloak
```

### With Volume for Logs

```bash
docker run -d \
  --name piicloak \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -e PIICLOAK_API_KEY=your-secret-key \
  --restart unless-stopped \
  piicloak
```

---

## Docker Compose

### Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  piicloak:
    image: dimanjet/piicloak:latest
    container_name: piicloak
    ports:
      - "8000:8000"
    environment:
      - PIICLOAK_HOST=0.0.0.0
      - PIICLOAK_PORT=8000
      - PIICLOAK_WORKERS=8
      - PIICLOAK_API_KEY=${PIICLOAK_API_KEY}
      - PIICLOAK_CORS_ORIGINS=https://yourdomain.com
      - PIICLOAK_LOG_LEVEL=WARNING
      - PIICLOAK_ENABLE_METRICS=true
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
```

**Deploy:**

```bash
# Set API key
export PIICLOAK_API_KEY=$(openssl rand -hex 32)

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale
docker-compose -f docker-compose.prod.yml up -d --scale piicloak=3
```

---

## Kubernetes Deployment

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: piicloak
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: piicloak-config
  namespace: piicloak
data:
  PIICLOAK_HOST: "0.0.0.0"
  PIICLOAK_PORT: "8000"
  PIICLOAK_WORKERS: "4"
  PIICLOAK_LOG_LEVEL: "INFO"
  PIICLOAK_SCORE_THRESHOLD: "0.4"
  PIICLOAK_ENABLE_METRICS: "true"
```

### Secret

```bash
# Create secret
kubectl create secret generic piicloak-secret \
  --from-literal=PIICLOAK_API_KEY=$(openssl rand -hex 32) \
  -n piicloak
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: piicloak
  namespace: piicloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: piicloak
  template:
    metadata:
      labels:
        app: piicloak
    spec:
      containers:
      - name: piicloak
        image: dimanjet/piicloak:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: piicloak-config
        - secretRef:
            name: piicloak-secret
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: piicloak-service
  namespace: piicloak
spec:
  selector:
    app: piicloak
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: piicloak-hpa
  namespace: piicloak
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: piicloak
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deploy to Kubernetes:**

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n piicloak
kubectl get svc -n piicloak

# View logs
kubectl logs -f deployment/piicloak -n piicloak

# Scale manually
kubectl scale deployment piicloak --replicas=5 -n piicloak
```

---

## AWS Deployment

### AWS ECS (Elastic Container Service)

**1. Create ECR Repository:**

```bash
aws ecr create-repository --repository-name piicloak
```

**2. Build and Push:**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t piicloak .

# Tag
docker tag piicloak:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/piicloak:latest

# Push
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/piicloak:latest
```

**3. Create Task Definition:**

```json
{
  "family": "piicloak",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "piicloak",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/piicloak:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PIICLOAK_WORKERS", "value": "4"},
        {"name": "PIICLOAK_LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {
          "name": "PIICLOAK_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:piicloak-api-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/piicloak",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**4. Create Service:**

```bash
aws ecs create-service \
  --cluster my-cluster \
  --service-name piicloak-service \
  --task-definition piicloak \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

---

## GCP Deployment

### Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/piicloak

# Deploy
gcloud run deploy piicloak \
  --image gcr.io/PROJECT_ID/piicloak \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PIICLOAK_WORKERS=4 \
  --set-secrets PIICLOAK_API_KEY=piicloak-api-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

---

## Azure Deployment

### Azure Container Instances

```bash
# Create resource group
az group create --name piicloak-rg --location eastus

# Deploy
az container create \
  --resource-group piicloak-rg \
  --name piicloak \
  --image dimanjet/piicloak:latest \
  --dns-name-label piicloak-unique \
  --ports 8000 \
  --environment-variables \
    PIICLOAK_WORKERS=4 \
    PIICLOAK_LOG_LEVEL=INFO \
  --secure-environment-variables \
    PIICLOAK_API_KEY=your-secret-key \
  --cpu 2 \
  --memory 4
```

---

## Monitoring & Observability

### Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'piicloak'
    static_configs:
      - targets: ['piicloak:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

Import dashboard ID: (to be created on Grafana.com)

**Key Metrics:**
- Request rate
- Error rate
- Response time (p50, p95, p99)
- PII entities detected
- Worker CPU/Memory usage

---

## Load Balancing

### Nginx

```nginx
upstream piicloak {
    least_conn;
    server piicloak-1:8000;
    server piicloak-2:8000;
    server piicloak-3:8000;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://piicloak;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 180s;
    }

    location /health {
        access_log off;
        proxy_pass http://piicloak/health;
    }
}
```

---

## SSL/TLS

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Backup & Disaster Recovery

PIICloak is stateless - no data backup needed!

**Configuration Backup:**
```bash
# Backup environment variables
env | grep PIICLOAK > piicloak.env

# Backup Kubernetes manifests
kubectl get all -n piicloak -o yaml > backup.yaml
```

---

## Security Checklist

- [ ] Enable API key authentication
- [ ] Use HTTPS only
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Use secrets management (not env vars in code)
- [ ] Run as non-root user
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity
- [ ] Use network policies (Kubernetes)
- [ ] Enable pod security policies

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs piicloak

# Common issues:
# - spaCy model not downloaded
# - Insufficient memory
# - Port already in use
```

### High memory usage

1. Reduce workers
2. Use smaller spaCy model
3. Increase container memory limit

### Slow responses

1. Scale horizontally (more replicas)
2. Increase workers per container
3. Use caching at load balancer
4. Optimize score_threshold
