# Deployment Guide

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Setup](#production-setup)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## Local Development

### Prerequisites

- Python 3.8+
- pip or conda
- Git

### Installation

```bash
# Clone repository
cd QNN_Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API
cd app/api
python flask_api.py
```

The API will be available at `http://localhost:5000`

## Docker Deployment

### Build Docker Image

```bash
docker build -t qnn-volatility:latest .
```

### Run Single Container

```bash
docker run -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=production \
  qnn-volatility:latest
```

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- QNN API on port 5000
- PostgreSQL for logging (optional)

**Check status:**
```bash
docker-compose ps
docker-compose logs qnn-api
```

**Stop services:**
```bash
docker-compose down
```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS (Recommended)

1. **Push image to ECR:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag qnn-volatility:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/qnn-volatility:latest

docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/qnn-volatility:latest
```

2. **Create ECS Cluster:**
```bash
aws ecs create-cluster --cluster-name qnn-cluster
```

3. **Register Task Definition:**
```bash
aws ecs register-task-definition \
  --family qnn-prediction-task \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 2048 \
  --memory 4096 \
  --container-definitions file://task-definition.json
```

4. **Create Service:**
```bash
aws ecs create-service \
  --cluster qnn-cluster \
  --service-name qnn-api \
  --task-definition qnn-prediction-task \
  --desired-count 2 \
  --launch-type FARGATE
```

#### Option 2: AWS Lambda

```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cd package
zip -r ../qnn-lambda.zip .
cd ..
zip qnn-lambda.zip -r app/

# Upload to AWS Lambda
aws lambda create-function \
  --function-name qnn-predictor \
  --runtime python3.10 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role \
  --handler app.api.flask_api.app \
  --zip-file fileb://qnn-lambda.zip
```

### Google Cloud Deployment

#### Cloud Run

```bash
# Build and push to Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT/qnn-volatility:latest

# Deploy to Cloud Run
gcloud run deploy qnn-api \
  --image gcr.io/YOUR_PROJECT/qnn-volatility:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars FLASK_ENV=production
```

### Azure Deployment

#### Container Instances

```bash
az group create --name qnn-group --location eastus

az container create \
  --resource-group qnn-group \
  --name qnn-api \
  --image myregistry.azurecr.io/qnn-volatility:latest \
  --cpu 2 \
  --memory 4 \
  --port 5000 \
  --environment-variables FLASK_ENV=production
```

## Production Setup

### 1. Environment Configuration

Create `.env` file:

```env
FLASK_ENV=production
API_HOST=0.0.0.0
API_PORT=5000
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db:5432/qnn_logs
```

### 2. Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

Run with:
```bash
gunicorn --config gunicorn_config.py app.api.flask_api:app
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/qnn-api`:

```nginx
upstream qnn_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/certificate.crt;
    ssl_certificate_key /etc/ssl/private/key.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Logging
    access_log /var/log/nginx/qnn_access.log;
    error_log /var/log/nginx/qnn_error.log;

    # Proxy configuration
    location / {
        proxy_pass http://qnn_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    location /api/v1/predict {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://qnn_backend;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=1r/s;
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/qnn-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Systemd Service

Create `/etc/systemd/system/qnn-api.service`:

```ini
[Unit]
Description=QNN Volatility Prediction API
After=network.target

[Service]
Type=notify
User=qnn-app
WorkingDirectory=/opt/qnn-project
ExecStart=/opt/qnn-project/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --access-logfile /var/log/qnn/access.log \
    --error-logfile /var/log/qnn/error.log \
    app.api.flask_api:app

Restart=always
RestartSec=10
SyslogIdentifier=qnn-api

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable qnn-api
sudo systemctl start qnn-api
sudo systemctl status qnn-api
```

## Monitoring & Maintenance

### Health Monitoring

```bash
# Check API health
curl http://localhost:5000/api/v1/health

# Monitor with uptime
watch -n 5 'curl -s http://localhost:5000/api/v1/health | jq'
```

### Log Monitoring

```bash
# View logs
tail -f logs/api.log

# Search logs
grep "ERROR" logs/*.log

# Log rotation (logrotate)
echo "/opt/qnn-project/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 qnn-app qnn-app
    sharedscripts
}" | sudo tee /etc/logrotate.d/qnn-api
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats qnn-api

# Python memory profiling
pip install memory-profiler
python -m memory_profiler example_predictions.py
```

### Backup & Recovery

```bash
# Backup model and data
tar -czf qnn-backup-$(date +%Y%m%d).tar.gz \
    model/ data/ logs/ config/

# Restore
tar -xzf qnn-backup-20231201.tar.gz
```

### Updates & Patching

```bash
# Update dependencies safely
pip install --upgrade -r requirements.txt --dry-run
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker build --no-cache -t qnn-volatility:latest .
docker push YOUR_REGISTRY/qnn-volatility:latest

# Update running services
docker-compose up -d --pull always
```

## Troubleshooting

### API Not Responding

```bash
# Check service status
systemctl status qnn-api

# Check logs
tail -f logs/api.log

# Test endpoint
curl -v http://localhost:5000/api/v1/health
```

### Model Loading Error

```bash
# Verify model file
ls -lah model/model_volatility.h5

# Test model loading
python -c "import tensorflow as tf; m=tf.keras.models.load_model('model/model_volatility.h5')"
```

### Memory Issues

```bash
# Increase container memory
docker run -m 8g qnn-volatility:latest

# Monitor memory usage
docker stats
```

## Security Best Practices

1. **API Key Authentication:**
   - Add API key validation in Flask
   - Use environment variables for secrets

2. **HTTPS/TLS:**
   - Always use HTTPS in production
   - Use Let's Encrypt for certificates

3. **Rate Limiting:**
   - Implement per-IP rate limiting
   - Use middleware like Flask-Limiter

4. **Input Validation:**
   - Validate all inputs
   - Sanitize data

5. **Secrets Management:**
   - Never commit secrets
   - Use AWS Secrets Manager, HashiCorp Vault, etc.

6. **Access Control:**
   - Implement role-based access control (RBAC)
   - Audit API access

## Support

For deployment issues, refer to:
- Docker documentation: https://docs.docker.com
- Nginx documentation: https://nginx.org/en/docs
- Flask deployment: https://flask.palletsprojects.com/en/2.3.x/deployment/
