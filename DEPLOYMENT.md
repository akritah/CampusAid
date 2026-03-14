# CampusAid Deployment Guide

Complete guide for deploying CampusAid to production.

## 📋 Pre-Deployment Checklist

- [ ] Backend tests passing
- [ ] Frontend builds successfully
- [ ] ML model trained and tested
- [ ] Database configured
- [ ] Environment variables set
- [ ] Security review completed

## 🔧 Production Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://username:password@host:5432/campusaid

# Security
SECRET_KEY=your-secret-key-here-min-32-chars

# CORS (update with your frontend URL)
ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional: Whisper API
OPENAI_API_KEY=your-api-key-if-using-whisper-api
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## 🐳 Docker Deployment

### Backend Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Train model on startup (or copy pre-trained model)
RUN python train_classifier.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: campusaid
      POSTGRES_USER: campusaid_user
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://campusaid_user:secure_password_here@postgres:5432/campusaid
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./backend/models:/app/models

  frontend:
    build: ./frontend/campusaid
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## ☁️ Cloud Deployment Options

### Option 1: Heroku

#### Backend (Heroku)

1. Create Heroku app:
```bash
heroku create campusaid-backend
```

2. Add PostgreSQL:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
```

4. Deploy:
```bash
git push heroku main
```

#### Frontend (Vercel)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd frontend/campusaid
vercel --prod
```

3. Set environment variable in Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://campusaid-backend.herokuapp.com
```

### Option 2: AWS

#### Backend (AWS Elastic Beanstalk)

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
cd backend
eb init -p python-3.10 campusaid-backend
```

3. Create environment:
```bash
eb create campusaid-backend-env
```

4. Set environment variables:
```bash
eb setenv DATABASE_URL=your-rds-url
```

#### Frontend (AWS Amplify)

1. Connect GitHub repository
2. Configure build settings:
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend/campusaid
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/campusaid/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/campusaid/node_modules/**/*
```

### Option 3: DigitalOcean

#### Using App Platform

1. Create new app from GitHub
2. Configure components:
   - Backend: Python app on port 8000
   - Frontend: Node.js app on port 3000
   - Database: Managed PostgreSQL

3. Set environment variables in dashboard

## 🔒 Security Hardening

### Backend Security

1. **Update CORS settings** in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)
```

2. **Add rate limiting**:
```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

3. **Enable HTTPS only**:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Database Security

1. **Use strong passwords**
2. **Enable SSL connections**
3. **Restrict network access**
4. **Regular backups**

```bash
# PostgreSQL backup
pg_dump -h hostname -U username campusaid > backup.sql

# Restore
psql -h hostname -U username campusaid < backup.sql
```

## 📊 Monitoring

### Backend Logging

Add structured logging:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'campusaid.log',
    maxBytes=10000000,
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logging.getLogger().addHandler(handler)
```

### Health Checks

Set up monitoring for:
- `/health` endpoint (should return 200)
- Database connectivity
- ML model availability
- Disk space
- Memory usage

### Error Tracking

Consider integrating:
- Sentry for error tracking
- Datadog for performance monitoring
- CloudWatch (AWS) or equivalent

## 🚀 Performance Optimization

### Backend

1. **Enable caching**:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="campusaid")
```

2. **Database connection pooling**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

3. **Async database queries** (optional):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
```

### Frontend

1. **Enable Next.js optimizations**:
```javascript
// next.config.mjs
export default {
  compress: true,
  images: {
    domains: ['your-cdn-domain.com'],
  },
  swcMinify: true,
}
```

2. **Add CDN for static assets**

3. **Enable caching headers**

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy CampusAid

on:
  push:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python test_endpoints.py

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend/campusaid
          npm ci
      - name: Build
        run: |
          cd frontend/campusaid
          npm run build

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
```

## 📝 Post-Deployment

1. **Verify all endpoints**:
```bash
python backend/test_endpoints.py
```

2. **Test authentication flow**

3. **Submit test complaints**

4. **Check admin dashboard**

5. **Monitor logs for errors**

6. **Set up alerts**

## 🆘 Rollback Plan

If deployment fails:

1. **Revert to previous version**:
```bash
git revert HEAD
git push
```

2. **Restore database backup** if needed

3. **Check logs** for root cause

4. **Fix issues** in development

5. **Re-deploy** after testing

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Test database connectivity
4. Review security settings
5. Contact team lead if needed

---

**Remember**: Always test in staging before production deployment!
