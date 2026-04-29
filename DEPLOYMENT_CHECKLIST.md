# Deployment Checklist

## Pre-Deployment

- [ ] All model files present (`model_volatility.h5`, `scaler.pkl`)
- [ ] Data files verified (`data_clean.csv`)
- [ ] Python version compatible (3.8+)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Verification script passed: `python verify_deployment.py`
- [ ] Environment variables configured: `.env` created from `.env.example`
- [ ] Logs directory created: `mkdir -p logs`

## Testing

- [ ] API tests pass: `pytest tests/test_api.py -v`
- [ ] Predictor tests pass: `pytest tests/test_predictor.py -v`
- [ ] All tests pass: `pytest -v --cov=app`
- [ ] Health endpoint works: `curl http://localhost:5000/api/v1/health`
- [ ] Single prediction works: tested with cURL
- [ ] Batch prediction works: tested with sample data
- [ ] SHAP explanation works: `python example_shap_explanation.py`

## Local Deployment

- [ ] API starts without errors: `python app/api/flask_api.py`
- [ ] API responds to requests on `http://localhost:5000`
- [ ] API documentation accessible at `/api/v1`
- [ ] All endpoints tested manually

## Docker Deployment

- [ ] Dockerfile builds successfully: `docker build -t qnn-volatility:latest .`
- [ ] Container runs: `docker run -p 5000:5000 qnn-volatility:latest`
- [ ] Health check passes: `curl http://localhost:5000/api/v1/health`
- [ ] Docker Compose works: `docker-compose up -d`

## Production Deployment

### Pre-Production

- [ ] Environment set to production: `FLASK_ENV=production`
- [ ] Debug mode disabled: `DEBUG=false`
- [ ] Logging level appropriate: `LOG_LEVEL=INFO`
- [ ] Secret key configured: `SECRET_KEY` in `.env`
- [ ] Database configured (if using): `DATABASE_URL` in `.env`

### Gunicorn Setup

- [ ] Gunicorn installed: `pip install gunicorn`
- [ ] Test with Gunicorn: `gunicorn --bind 0.0.0.0:5000 app.api.flask_api:app`
- [ ] Systemd service created: `/etc/systemd/system/qnn-api.service`
- [ ] Systemd service enabled: `systemctl enable qnn-api`

### Nginx Configuration

- [ ] Nginx installed
- [ ] Nginx config created: `/etc/nginx/sites-available/qnn-api`
- [ ] Nginx config enabled: `ln -s` to sites-enabled
- [ ] SSL certificates obtained: Let's Encrypt
- [ ] SSL configured in Nginx
- [ ] Nginx tested: `nginx -t`
- [ ] Nginx restarted: `systemctl restart nginx`

### Monitoring

- [ ] Logging configured and working
- [ ] Log rotation configured: logrotate
- [ ] Health checks set up
- [ ] Monitoring/alerting configured
- [ ] Error tracking configured (Sentry, etc.)

### Security

- [ ] API key authentication implemented
- [ ] CORS configured appropriately
- [ ] Rate limiting implemented
- [ ] Input validation complete
- [ ] SSL/TLS configured
- [ ] Security headers set in Nginx
- [ ] Secrets not in code (using .env)

### Backup & Recovery

- [ ] Backup procedure documented
- [ ] Model files backed up
- [ ] Database backed up (if applicable)
- [ ] Recovery procedure tested

## Cloud Deployment

### AWS

- [ ] AWS account configured
- [ ] IAM roles created
- [ ] ECR repository created (for ECS)
- [ ] Image pushed to ECR (if using ECS)
- [ ] ECS cluster created (if using ECS)
- [ ] RDS database created (if needed)
- [ ] Load balancer configured (if needed)
- [ ] Auto-scaling configured (if needed)

### Google Cloud

- [ ] GCP project created
- [ ] Container Registry configured
- [ ] Image pushed to registry (if using GKE)
- [ ] Cloud Run service deployed (if using Cloud Run)
- [ ] Cloud Storage configured (if needed)

### Azure

- [ ] Azure account configured
- [ ] Container Registry created
- [ ] Image pushed to registry
- [ ] App Service created
- [ ] Database created (if needed)

## Post-Deployment

- [ ] API accessible from internet
- [ ] SSL certificate valid
- [ ] Health endpoint accessible
- [ ] Sample predictions work
- [ ] Logging working correctly
- [ ] Monitoring/alerts working
- [ ] Backup tested
- [ ] Performance acceptable
- [ ] Load testing passed (if needed)

## Documentation

- [ ] README updated with deployment URL
- [ ] API documentation accessible
- [ ] Deployment guide completed
- [ ] Runbook created
- [ ] Contact information provided
- [ ] Known issues documented

## Handoff

- [ ] Team trained on deployment
- [ ] Incident response procedures documented
- [ ] Escalation path defined
- [ ] On-call rotation established
- [ ] Documentation location communicated

---

## Sign-Off

- Deployer: _________________ Date: _________
- Reviewer: _________________ Date: _________
- Approved by: ______________ Date: _________

## Notes

```
[Space for deployment notes, issues encountered, resolutions]
