# Docker Deployment Guide

This guide explains how to run the ML Pipeline using Docker Compose.

## Architecture

The system consists of three services:

1. **MLflow Tracking Server** (Port 5000)
   - Experiment tracking and model registry
   - SQLite backend store
   - Local artifact storage

2. **FastAPI Backend** (Port 8000)
   - REST API for pipeline operations
   - LangGraph workflow execution
   - MLflow integration

3. **Streamlit Frontend** (Port 8501)
   - Interactive web UI
   - Pipeline monitoring dashboard
   - Data loading interface

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ available RAM
- (Optional) AWS credentials for Bedrock agents

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# AWS Configuration (optional, for Bedrock agents)
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEMPERATURE=0.0
BEDROCK_MAX_TOKENS=4096

# MLflow Configuration (handled by docker-compose)
MLFLOW_TRACKING_URI=http://mlflow:5000

# Pipeline Configuration
DEFAULT_DATA_PATH=data/raw/train.csv
DEFAULT_TARGET_COLUMN=target
OUTPUT_DIR=outputs
```

### 2. Prepare Data Directory

Create data directory and add your training data:

```bash
mkdir -p data/raw
cp /path/to/your/data.csv data/raw/train.csv
```

### 3. Build and Start Services

```bash
# Build images and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Access Services

Once all services are healthy:

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/api/docs
- **MLflow UI**: http://localhost:5000

## Usage

### Using the Streamlit Dashboard

1. Open http://localhost:8501 in your browser
2. Configure pipeline settings in the sidebar:
   - Data path: `data/raw/train.csv`
   - Target column name
   - MLflow experiment name
   - Test set size and random state
3. Click "🚀 Load Data & Start Pipeline"
4. Monitor pipeline progress in real-time

### Using the API Directly

Load data via API:

```bash
curl -X POST "http://localhost:8000/api/pipeline/load-data" \
  -H "Content-Type: application/json" \
  -d '{
    "data_path": "data/raw/train.csv",
    "target_column": "target",
    "experiment_name": "my_experiment",
    "test_size": 0.2,
    "random_state": 42
  }'
```

Check pipeline state:

```bash
curl "http://localhost:8000/api/pipeline/state/{pipeline_run_id}"
```

List all pipeline runs:

```bash
curl "http://localhost:8000/api/pipeline/runs"
```

## Docker Compose Commands

### Start Services

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mlflow

# Follow logs
docker-compose logs -f backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Service Health

```bash
# Check status
docker-compose ps

# Check health
docker inspect ml-pipeline-backend --format='{{.State.Health.Status}}'
```

## Volume Management

### Data Persistence

Data is persisted in the following volumes:

- `./data`: Training and test data
- `./outputs`: Model artifacts, plots, reports
- `./mlruns`: MLflow tracking data
- `./mlartifacts`: MLflow artifacts

### Backup Data

```bash
# Backup MLflow data
tar -czf mlflow-backup.tar.gz mlruns/ mlartifacts/

# Backup outputs
tar -czf outputs-backup.tar.gz outputs/
```

### Clean Volumes

```bash
# Remove all data (WARNING: Deletes all experiments)
rm -rf mlruns/ mlartifacts/ outputs/

# Remove specific experiment
rm -rf mlruns/{experiment_id}/
```

## Troubleshooting

### Services Won't Start

Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

Common issues:
- Port conflicts (8000, 8501, 5000 already in use)
- Insufficient memory
- Missing environment variables

### Backend Health Check Fails

```bash
# Check backend logs
docker-compose logs backend

# Check MLflow connection
docker-compose exec backend curl http://mlflow:5000/health

# Restart backend
docker-compose restart backend
```

### Frontend Can't Connect to Backend

Check network connectivity:
```bash
# Test from frontend container
docker-compose exec frontend curl http://backend:8000/health
```

If fails, check docker network:
```bash
docker network inspect ml_pipeline_ml-pipeline-network
```

### MLflow Database Locked

If you see "database is locked" errors:

```bash
# Stop all services
docker-compose down

# Remove lock files
rm mlruns/mlflow.db-wal mlruns/mlflow.db-shm

# Restart
docker-compose up
```

### Out of Memory

Increase Docker memory limit:
- Docker Desktop → Settings → Resources → Memory
- Recommended: 4GB minimum, 8GB optimal

### AWS Credentials Not Working

For Bedrock agents, mount AWS credentials:

```yaml
# Add to backend service in docker-compose.yml
volumes:
  - ~/.aws:/root/.aws:ro
```

Or use environment variables:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Development Mode

### Hot Reload

Backend has hot reload enabled by default. To modify code:

1. Edit files in `api/`, `core/`, `nodes/`, etc.
2. Backend automatically reloads
3. Refresh browser to see changes

### Local Development

To run services locally without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Start MLflow
mlflow server --host 0.0.0.0 --port 5000

# Start backend (new terminal)
cd /path/to/ml_pipeline
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (new terminal)
cd /path/to/ml_pipeline
streamlit run frontend/streamlit_app.py
```

Update API URL in `frontend/streamlit_app.py`:
```python
API_BASE_URL = "http://localhost:8000/api"  # Local development
```

## Production Deployment

For production deployment, modify `docker-compose.yml`:

1. **Remove --reload** from backend command
2. **Add resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

3. **Configure CORS** properly in `api/main.py`
4. **Use external database** for MLflow (PostgreSQL/MySQL)
5. **Use S3/Azure/GCS** for artifact storage
6. **Add authentication** to all services
7. **Use HTTPS** with reverse proxy (nginx/traefik)

## Scaling

### Horizontal Scaling (Multiple Backend Instances)

```yaml
backend:
  # ... existing config
  deploy:
    replicas: 3
```

Add load balancer (nginx) in front.

### Vertical Scaling

Increase resource limits in docker-compose.yml or use Kubernetes for advanced orchestration.

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats ml-pipeline-backend ml-pipeline-frontend mlflow-server

# Disk usage
docker system df
```

### Application Metrics

- MLflow UI: http://localhost:5000 - View all experiments and runs
- FastAPI Metrics: Add `/metrics` endpoint with prometheus
- Streamlit: Built-in performance monitoring

## Cleanup

### Remove Everything

```bash
# Stop and remove containers, networks
docker-compose down

# Remove volumes (data)
docker-compose down -v

# Remove images
docker rmi $(docker images -q ml_pipeline*)

# Clean Docker system
docker system prune -a --volumes
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Review troubleshooting section above
3. Check service health: `docker-compose ps`
4. Verify network connectivity between services
