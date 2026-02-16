# Docker Deployment Guide

This guide explains how to run the Multi-Model AI Chat System using Docker.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)
- `.env` file with your `GOOGLE_API_KEY`

## Quick Start

### 1. Set up environment variables

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_api_key_here
```

### 2. Build and run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Stop the application

```bash
# Stop services
docker-compose down

# Stop and remove volumes (clears stored data)
docker-compose down -v
```

## Architecture

The Docker setup consists of two services:

### Backend Service
- **Container**: `ai-chat-backend`
- **Port**: 8000
- **Image**: Python 3.11-slim
- **Features**:
  - FastAPI application
  - LangChain with Google Gemini
  - ChromaDB vector store
  - PDF processing with RAG

### Frontend Service
- **Container**: `ai-chat-frontend`
- **Port**: 80
- **Image**: Multi-stage (Node 18 + Nginx Alpine)
- **Features**:
  - React application
  - Nginx web server
  - Reverse proxy to backend

## Network Configuration

Both services are connected via a bridge network `ai-chat-network`:
- Frontend communicates with backend via `/api` proxy
- Backend is accessible at `http://backend:8000` internally
- External access: Frontend (port 80), Backend (port 8000)

## Volume Management

### Backend Volumes
- `./data:/app/data` - PDF uploads and documents
- `./vectorstore:/app/vectorstore` - ChromaDB embeddings
- `./.env:/app/.env` - Environment variables

### Named Volumes
- `data` - Persistent data storage
- `vectorstore` - Persistent vector embeddings

## Health Checks

Both services have health checks configured:

### Backend
```bash
curl http://localhost:8000/health
```

### Frontend
```bash
curl http://localhost/health
```

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild specific service
```bash
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

### Shell access
```bash
# Backend container
docker exec -it ai-chat-backend /bin/bash

# Frontend container
docker exec -it ai-chat-frontend /bin/sh
```

### Check service status
```bash
docker-compose ps
```

### Restart services
```bash
docker-compose restart
```

## Production Considerations

### Security
1. **Don't commit `.env` file** - Use environment variables or secrets management
2. **Use HTTPS** - Add SSL/TLS certificates to nginx
3. **Update security headers** - Configure CSP, HSTS in nginx
4. **Limit resource usage** - Add memory/CPU limits in docker-compose.yml

### Example resource limits:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Scaling
To run multiple backend instances:
```bash
docker-compose up -d --scale backend=3
```

### Monitoring
Add healthcheck monitoring:
```bash
docker inspect --format='{{.State.Health.Status}}' ai-chat-backend
docker inspect --format='{{.State.Health.Status}}' ai-chat-frontend
```

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

### Build failures
```bash
# Clean build (remove cache)
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all
```

### Volume permission issues
```bash
# Linux: Fix permissions
sudo chown -R $USER:$USER ./data ./vectorstore
```

### Reset everything
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove orphan containers
docker-compose down --remove-orphans

# Rebuild from scratch
docker-compose up --build --force-recreate
```

## Environment Variables

### Backend (.env)
- `GOOGLE_API_KEY` - Required: Your Google Gemini API key
- `HOST` - Optional: Default 0.0.0.0
- `PORT` - Optional: Default 8000

### Frontend (build-time)
- `VITE_API_URL` - Optional: Override API URL (default: /api in production)

## File Structure
```
.
├── Dockerfile                 # Backend Dockerfile
├── docker-compose.yml         # Multi-service orchestration
├── .dockerignore              # Backend exclusions
├── .env                       # Environment variables
├── app/                       # Backend source
├── frontend/
│   ├── Dockerfile             # Frontend Dockerfile
│   ├── .dockerignore          # Frontend exclusions
│   ├── nginx.conf             # Nginx configuration
│   └── src/                   # React source
├── data/                      # PDF uploads (volume)
└── vectorstore/               # ChromaDB data (volume)
```

## Development vs Production

### Development (without Docker)
```bash
# Backend
cd d:\UNIVERSITY\IT\External\Assignment-Arctiq-Solutions
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Production (with Docker)
```bash
docker-compose up -d --build
```

---

**Note**: The Docker setup uses multi-stage builds for the frontend to minimize image size. The final frontend image only contains the built React app served by Nginx (~50MB vs ~1GB with node_modules).
