# 📋 Deployment Checklist

Use this checklist to prepare the Agentic Tree application for production deployment.

## Pre-Deployment Review

- [ ] Read [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
- [ ] Review architecture in [README.md](README.md)
- [ ] Understand environment variables (see `.env.example`)
- [ ] Familiarize with CI/CD pipeline (.github/workflows/)

## Security Configuration

### Secrets Management
- [ ] Move `SECRET_KEY` to a secrets manager (AWS Secrets Manager, Vault, etc.)
- [ ] Store `OPENAI_API_KEY` in secrets manager (if using LLM)
- [ ] Store database credentials in secrets manager
- [ ] Never commit `.env` files to version control
- [ ] Use `.gitignore` to exclude secrets

### TLS/HTTPS
- [ ] Obtain SSL/TLS certificate (Let's Encrypt, Digicert, etc.)
- [ ] Configure HTTPS on your reverse proxy (Nginx, CloudFlare, AWS ALB)
- [ ] Enforce HTTPS redirect (HTTP → HTTPS)
- [ ] Enable HSTS header (Strict-Transport-Security)
- [ ] Set secure cookie flags (HttpOnly, Secure, SameSite)

### CORS Configuration
- [ ] Update `allow_origins` in [backend/venv/main.py](backend/venv/main.py) with production frontend URL
  ```python
  allow_origins=["https://yourdomain.com"],
  ```
- [ ] Test CORS from frontend

### Rate Limiting
- [ ] Replace in-memory rate limiter with Redis (for distributed systems)
- [ ] Adjust `RATE_LIMIT` and `RATE_WINDOW_SECONDS` if needed
- [ ] Test rate limiting under load

## Database Setup

### PostgreSQL Production Database
- [ ] Provision PostgreSQL 14+ instance (AWS RDS, Azure Database, etc.)
- [ ] Create a new database: `agentic_tree_db`
- [ ] Create a dedicated database user (not `postgres`)
- [ ] Set strong password for database user
- [ ] Restrict database access to backend server only
- [ ] Enable database backups and point-in-time recovery
- [ ] Enable encryption at rest (if supported)

### Run Migrations
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/agentic_tree_db"
python -m alembic upgrade head
```

- [ ] Verify migrations completed successfully
- [ ] Check database tables exist: `users`, `tree_sessions`, `chat_messages`
- [ ] Verify alembic_version table (tracks migrations)

## Backend Configuration

### Environment Variables
Set these in your deployment platform (AWS ECS, Heroku, Azure, etc.):

```ini
# Database
DATABASE_URL=postgresql://user:pass@host:5432/agentic_tree_db

# Security
SECRET_KEY=<strong-random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# LLM (optional)
USE_LLM_AGENT=1
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Rate Limiting
RATE_LIMIT=100
RATE_WINDOW_SECONDS=60

# Logging
LOG_LEVEL=INFO
```

- [ ] Generate new `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Store `DATABASE_URL` in secrets manager
- [ ] Store `OPENAI_API_KEY` in secrets manager (if using LLM)
- [ ] Verify all env vars are set in deployment platform

### Logging & Monitoring
- [ ] Set up centralized logging (DataDog, ELK, CloudWatch, etc.)
- [ ] Configure log aggregation to capture uvicorn logs
- [ ] Set up alerts for error logs
- [ ] Enable Prometheus metrics (optional, see [README_OBSERVABILITY.md](backend/README_OBSERVABILITY.md))
- [ ] Set up dashboards for monitoring

### Health Checks
- [ ] Create health check endpoint: `GET /` (returns `{"message": "Backend is working 🚀"}`)
- [ ] Configure load balancer health check to use `/`
- [ ] Test health check endpoint

## Frontend Configuration

### Build Optimization
```bash
cd frontend
npm install
npm run build
```

- [ ] Verify production build completes without errors
- [ ] Check bundle size (target: < 500KB gzipped)
- [ ] Review build output in `dist/` folder

### Environment Variables
Create `frontend/.env.production`:
```ini
VITE_API_URL=https://api.yourdomain.com
```

- [ ] Update `VITE_API_URL` to production backend URL
- [ ] Verify frontend can connect to backend

### CDN & Static Hosting
- [ ] Deploy `dist/` folder to CDN or static hosting (S3, CloudFront, Netlify, Vercel)
- [ ] Configure caching headers (cache static assets for 1 year, html for 1 hour)
- [ ] Enable gzip compression
- [ ] Set up redirect from root to index.html (for client-side routing)

### SSL/TLS for Frontend
- [ ] Enable HTTPS on frontend domain
- [ ] Redirect HTTP → HTTPS

## CI/CD Pipeline

### GitHub Actions
- [ ] Review `.github/workflows/ci.yml`
- [ ] Ensure tests pass locally: `pytest backend/tests`
- [ ] Ensure frontend builds: `npm run build`
- [ ] Add secrets to GitHub repo settings:
  - [ ] `REGISTRY_PASSWORD` (if using Docker registry)
  - [ ] `DEPLOYMENT_KEY` (if deploying to VPS)
  - [ ] Any other deployment credentials

### Docker & Registry
- [ ] Build Docker images:
  ```bash
  docker build -t myregistry/backend:latest ./backend
  docker build -t myregistry/frontend:latest ./frontend
  ```
- [ ] Push to Docker registry (Docker Hub, AWS ECR, etc.)
- [ ] Test images locally:
  ```bash
  docker run -p 8000:8000 myregistry/backend:latest
  ```

## Deployment Platform

### Option A: AWS (ECS + RDS + CloudFront)
- [ ] Create ECS cluster
- [ ] Create ECS task definitions for backend
- [ ] Create ECS service with auto-scaling
- [ ] Create RDS PostgreSQL instance
- [ ] Create CloudFront distribution for frontend
- [ ] Configure Route 53 DNS
- [ ] Enable CloudWatch monitoring

### Option B: Heroku
- [ ] Create Heroku app: `heroku create myapp-backend`
- [ ] Add PostgreSQL add-on: `heroku addons:create heroku-postgresql:standard-0`
- [ ] Deploy backend: `git push heroku main`
- [ ] Deploy frontend to Vercel or Netlify

### Option C: Self-Hosted (DigitalOcean, Linode, etc.)
- [ ] Provision VPS (2GB+ RAM, 50GB+ disk)
- [ ] Install Docker and Docker Compose
- [ ] Clone repo and configure `.env`
- [ ] Run `docker-compose up -d`
- [ ] Set up Nginx reverse proxy with SSL
- [ ] Configure firewall (ufw/Security Groups)
- [ ] Set up auto-backups for database

## Load Testing & Performance

- [ ] Load test backend: `ab -c 10 -n 1000 http://localhost:8000/`
- [ ] Verify rate limiting works under load
- [ ] Monitor response times and resource usage
- [ ] Test with realistic tree sizes (100+ nodes)
- [ ] Verify LLM API responses stay within budget

## Final Verification

### API Testing
```bash
# Register
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123"}'

# Create tree
curl -X POST https://yourdomain.com/api/trees \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Test Tree", "tree_data": null}'

# Chat
curl -X POST https://yourdomain.com/api/chat \
  -H "Authorization: Bearer <token>" \
  -d '{"tree_id": 1, "message": "What is the height?"}'
```

- [ ] Register endpoint works
- [ ] Login endpoint works
- [ ] Token refresh works
- [ ] Create/read trees works
- [ ] Insert/delete nodes works
- [ ] Search works
- [ ] Chat works (rule-based)
- [ ] Chat works (LLM, if enabled)

### Frontend Testing
- [ ] Access frontend URL in browser
- [ ] Register new account
- [ ] Login
- [ ] Create a tree
- [ ] Insert nodes
- [ ] Search for nodes
- [ ] Run traversals
- [ ] Test chat (rule-based)
- [ ] Test chat (LLM, if enabled)
- [ ] Test logout
- [ ] Test token refresh (let token expire, perform action)

### Security Testing
- [ ] Test CORS: requests from wrong origin should fail
- [ ] Test rate limiting: 61st request within window should be rejected
- [ ] Test unauthorized access: request without token should fail
- [ ] Test SQL injection: tree names with quotes/special chars should be safe
- [ ] Test XSS: chat responses with HTML should be escaped
- [ ] Verify secrets are not exposed in logs or error messages

## Monitoring & Alerting

- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure alerts for:
  - [ ] Backend service down
  - [ ] High error rate (> 1%)
  - [ ] High response time (> 5s)
  - [ ] Database connection errors
  - [ ] Rate limit exceeded
  - [ ] LLM API errors (if enabled)
- [ ] Set up log alerts for ERROR and CRITICAL messages
- [ ] Monitor OpenAI API costs (if using LLM)

## Backup & Disaster Recovery

- [ ] Enable automated database backups (daily)
- [ ] Test backup restoration procedure
- [ ] Store backups in geo-redundant location
- [ ] Document recovery procedures
- [ ] Set RTO (Recovery Time Objective) and RPO (Recovery Point Objective)

## Documentation

- [ ] Update deployment docs with your specific architecture
- [ ] Create runbook for common operations (restart, scale, debug)
- [ ] Document how to add team members
- [ ] Create incident response plan

## Launch Approval

- [ ] ✅ All checklist items completed
- [ ] ✅ Security review passed
- [ ] ✅ Performance testing passed
- [ ] ✅ Integration testing passed
- [ ] ✅ Team lead approval
- [ ] ✅ Operations team approval

**Status**: Ready to deploy! 🚀

---

**Last Updated**: February 24, 2026  
**Version**: 1.0  
**Deployed By**: ___________  
**Date Deployed**: ___________
