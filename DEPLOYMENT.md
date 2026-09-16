# MedLab Platform — Deployment

## Deployment Architecture

MedLab Platform is designed to run as a containerized backend.

Production architecture:

GitHub
   │
   ▼
GitHub Actions
   │
   ├── Tests
   ├── Security Scan
   └── Docker Build
          │
          ▼
      Container Registry
          │
          ▼
        Cloud
          │
          ├── FastAPI
          ├── PostgreSQL
          ├── Redis
          ├── Celery Worker
          └── Celery Beat