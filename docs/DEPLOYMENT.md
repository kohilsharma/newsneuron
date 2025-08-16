# NewsNeuron Deployment Guide

This guide covers deploying NewsNeuron to production environments, including cloud platforms, containerization, and best practices for a scalable deployment.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Frontend Deployment](#frontend-deployment)
- [Backend Deployment](#backend-deployment)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Container Deployment](#container-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

NewsNeuron follows a modern microservices architecture optimized for cloud deployment:

- **Frontend**: Static files deployed to Vercel/Netlify/CDN
- **Backend**: Containerized FastAPI application on cloud platforms
- **Databases**: Managed Supabase + Neo4j AuraDB
- **AI Services**: OpenAI/OpenRouter APIs
- **Monitoring**: Integrated logging and metrics

## 🛠️ Prerequisites

### Required Accounts & Services

- **Frontend Hosting**: [Vercel](https://vercel.com/) (recommended) or [Netlify](https://netlify.com/)
- **Backend Hosting**: [Railway](https://railway.app/), [Render](https://render.com/), or [Google Cloud Run](https://cloud.google.com/run)
- **Vector Database**: [Supabase](https://supabase.com/) (PostgreSQL + pgvector)
- **Graph Database**: [Neo4j AuraDB](https://neo4j.com/cloud/aura/)
- **AI Services**: [OpenAI](https://openai.com/) and/or [OpenRouter](https://openrouter.ai/)
- **Monitoring**: [Sentry](https://sentry.io/) (optional)

### Development Tools

- **Docker** (for containerization)
- **Vercel CLI** or **Railway CLI**
- **Git** (for version control)

## 🌐 Frontend Deployment

### Option 1: Vercel (Recommended)

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Configure Project

Create `vercel.json` in project root:

```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-url.railway.app/api/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "@api_base_url",
    "VITE_APP_NAME": "NewsNeuron",
    "VITE_API_VERSION": "v1"
  }
}
```

#### 3. Deploy

```bash
cd frontend
vercel --prod
```

#### 4. Set Environment Variables

In Vercel dashboard, add environment variables:

```env
VITE_API_BASE_URL=https://your-backend-url.railway.app
VITE_API_VERSION=v1
VITE_APP_NAME=NewsNeuron
VITE_ENABLE_DEBUG=false
VITE_SENTRY_DSN=your_sentry_dsn
```

### Option 2: Netlify

#### 1. Build Configuration

Create `netlify.toml`:

```toml
[build]
  base = "frontend/"
  publish = "frontend/dist"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-url.railway.app/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 2. Deploy

Connect your GitHub repository to Netlify and configure build settings.

## 🚀 Backend Deployment

### Option 1: Railway (Recommended)

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Configure Deployment

Create `railway.toml`:

```toml
[build]
  builder = "nixpacks"
  buildCommand = "pip install -r requirements.txt && python -m spacy download en_core_web_sm"

[deploy]
  startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  healthcheckPath = "/health"
  healthcheckTimeout = 100
  restartPolicyType = "always"
```

#### 3. Deploy

```bash
cd backend
railway login
railway init
railway up
```

#### 4. Set Environment Variables

```bash
railway vars set SUPABASE_URL="your_supabase_url"
railway vars set SUPABASE_ANON_KEY="your_supabase_key"
railway vars set NEO4J_URI="neo4j+s://your-aura-instance.databases.neo4j.io"
railway vars set NEO4J_USERNAME="neo4j"
railway vars set NEO4J_PASSWORD="your_password"
railway vars set OPENAI_API_KEY="your_openai_key"
railway vars set SECRET_KEY="your_secret_key"
railway vars set DEBUG="false"
```

### Option 2: Google Cloud Run

#### 1. Build Container

```bash
cd backend
docker build -t gcr.io/your-project/newsneuron-backend .
docker push gcr.io/your-project/newsneuron-backend
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy newsneuron-backend \
  --image gcr.io/your-project/newsneuron-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="SUPABASE_URL=your_url,NEO4J_URI=your_uri"
```

### Option 3: Render

#### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: newsneuron-backend
    env: python
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.8
      - key: SUPABASE_URL
        fromDatabase:
          name: supabase-config
          property: url
```

## 🗄️ Database Setup

### Supabase Configuration

#### 1. Create Supabase Project

```bash
# Install Supabase CLI
npm install -g supabase

# Login and create project
supabase login
supabase projects create newsneuron
```

#### 2. Enable pgvector Extension

In Supabase SQL Editor:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### 3. Run Database Schema

Execute the SQL schema from `backend/database/supabase_schema.sql` in the Supabase SQL Editor.

#### 4. Configure Row Level Security (RLS)

```sql
-- Enable RLS on tables
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth needs)
CREATE POLICY "Public articles are viewable by everyone" 
ON articles FOR SELECT 
USING (true);
```

### Neo4j AuraDB Setup

#### 1. Create AuraDB Instance

1. Go to [Neo4j AuraDB](https://console.neo4j.io/)
2. Create new instance
3. Choose region closest to your backend
4. Save connection credentials

#### 2. Configure Connection

```python
# Test connection
import os
from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME") 
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(username, password))

# Test query
with driver.session() as session:
    result = session.run("RETURN 'Hello, Neo4j!' as message")
    print(result.single()["message"])
```

## 🔧 Environment Configuration

### Production Environment Variables

#### Backend (.env.production)

```env
# Application
DEBUG=false
SECRET_KEY=your_super_secret_key_here
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# AI Services
OPENAI_API_KEY=sk-your_openai_key
OPENROUTER_API_KEY=sk-or-your_openrouter_key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
LOG_LEVEL=INFO

# Performance
REDIS_URL=redis://your-redis-instance.com:6379
MAX_WORKERS=4
```

#### Frontend (.env.production)

```env
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_API_VERSION=v1
VITE_APP_NAME=NewsNeuron
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
VITE_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project
```

### Security Best Practices

#### 1. Secret Management

```bash
# Use platform-specific secret management
# Railway
railway vars set SECRET_KEY="$(openssl rand -base64 32)"

# Vercel
vercel env add SECRET_KEY

# Google Cloud
gcloud secrets create secret-key --data-file=-
```

#### 2. CORS Configuration

```python
# app/config.py
from typing import List

class Settings(BaseSettings):
    cors_origins: List[str] = [
        "https://your-domain.vercel.app",
        "https://your-custom-domain.com"
    ]
    
    # Only allow localhost in development
    @validator('cors_origins', pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
```

## 🐳 Container Deployment

### Docker Configuration

#### Backend Dockerfile

```dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app/ ./app/
COPY data-processing/ ./data-processing/
COPY database/ ./database/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

#### Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - SUPABASE_URL=${SUPABASE_URL}
      - NEO4J_URI=${NEO4J_URI}
    depends_on:
      - postgres
      - neo4j
      - redis

  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: newsneuron
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  neo4j:
    image: neo4j:5.15
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  neo4j_data:
  redis_data:
```

### Kubernetes Deployment

#### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: newsneuron-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: newsneuron-backend
  template:
    metadata:
      labels:
        app: newsneuron-backend
    spec:
      containers:
      - name: backend
        image: your-registry/newsneuron-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: newsneuron-secrets
              key: supabase-url
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
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🔄 CI/CD Pipeline

### GitHub Actions

#### Frontend Deployment

```yaml
# .github/workflows/frontend.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
      
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
      
      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend
```

#### Backend Deployment

```yaml
# .github/workflows/backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Railway
        uses: railway/actions@v1
        with:
          service: newsneuron-backend
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Sentry Integration

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration(auto_enable=True)],
        traces_sample_rate=0.1,
        environment=settings.environment
    )
```

#### Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    checks = {}
    
    # Check Supabase connection
    try:
        supabase = get_supabase_client()
        await supabase.table('articles').select('id').limit(1).execute()
        checks['supabase'] = 'healthy'
    except Exception as e:
        checks['supabase'] = f'unhealthy: {str(e)}'
    
    # Check Neo4j connection
    try:
        driver = get_neo4j_driver()
        async with driver.session() as session:
            await session.run("RETURN 1")
        checks['neo4j'] = 'healthy'
    except Exception as e:
        checks['neo4j'] = f'unhealthy: {str(e)}'
    
    # Check OpenAI API
    try:
        response = await openai.models.list()
        checks['openai'] = 'healthy'
    except Exception as e:
        checks['openai'] = f'unhealthy: {str(e)}'
    
    all_healthy = all(status == 'healthy' for status in checks.values())
    
    return {
        'status': 'healthy' if all_healthy else 'degraded',
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }
```

### Logging Configuration

```python
# app/utils/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging for production"""
    
    # Create formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Disable uvicorn access logs in production
    if not settings.debug:
        logging.getLogger("uvicorn.access").disabled = True
```

## 🔒 Security Considerations

### 1. Environment Security

```python
# Validate environment variables
class Settings(BaseSettings):
    secret_key: str
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/chat/")
@limiter.limit("10/minute")
async def chat(request: Request, message: ChatMessage):
    # Implementation
    pass
```

### 3. Input Validation

```python
from pydantic import BaseModel, validator

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 10000:
            raise ValueError('Message too long')
        return v.strip()
```

## ⚡ Performance Optimization

### 1. Caching Strategy

```python
import redis
from functools import wraps

redis_client = redis.from_url(settings.redis_url)

def cache_result(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Compute and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
async def get_trending_topics():
    # Expensive computation
    pass
```

### 2. Database Optimization

```sql
-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_articles_embedding_vector 
ON articles USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX CONCURRENTLY idx_articles_published_date 
ON articles (published_date DESC);

CREATE INDEX CONCURRENTLY idx_conversations_user_id 
ON conversations (user_id);
```

### 3. Connection Pooling

```python
# app/database/supabase_client.py
from supabase import create_client
import asyncpg

class DatabasePool:
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    async def close(self):
        if self.pool:
            await self.pool.close()

db_pool = DatabasePool()
```

## 🐛 Troubleshooting

### Common Deployment Issues

#### 1. Container Build Failures

```bash
# Build with verbose output
docker build --progress=plain --no-cache -t newsneuron-backend .

# Check build logs
docker logs newsneuron-backend

# Shell into container for debugging
docker run -it newsneuron-backend /bin/bash
```

#### 2. Database Connection Issues

```python
# Test connections separately
async def test_connections():
    # Test Supabase
    try:
        supabase = get_supabase_client()
        result = await supabase.table('articles').select('count').execute()
        print(f"Supabase: OK")
    except Exception as e:
        print(f"Supabase error: {e}")
    
    # Test Neo4j
    try:
        driver = get_neo4j_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            print(f"Neo4j: OK")
    except Exception as e:
        print(f"Neo4j error: {e}")
```

#### 3. Memory Issues

```yaml
# Adjust resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

#### 4. Environment Variable Issues

```bash
# Debug environment variables
printenv | grep -E "(SUPABASE|NEO4J|OPENAI)"

# Validate environment in app
python -c "
from app.config import settings
print('Settings loaded successfully')
print(f'Supabase URL: {settings.supabase_url[:20]}...')
"
```

### Performance Issues

```bash
# Monitor resource usage
docker stats newsneuron-backend

# Check application metrics
curl https://your-app.railway.app/health

# Database query performance
# Use EXPLAIN ANALYZE for slow queries
```

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Supabase Production Checklist](https://supabase.com/docs/guides/platform/going-into-prod)
- [Neo4j Production Deployment](https://neo4j.com/docs/operations-manual/current/deployment/)

## 🤝 Support

For deployment-related issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review platform-specific documentation
3. Open an issue with deployment logs
4. Join our community discussions

---

**Happy Deploying! 🚀**
