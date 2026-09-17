## MedLab Platform

MedLab Platform is a professional backend platform 
for biomedical laboratory management inspired by a LIMS
(Laboratory Information Management System).

The project demonstrates the design and implementation of a
production-oriented Python backend with REST APIs, authentication,
role-based access control, asynchronous processing, biomedical
equipment management, calibration management, notifications,
report generation, testing, observability and containerized deployment.

---

# Features

## Backend

- FastAPI
- Python 3.13
- REST API
- API versioning
- Pydantic
- SQLAlchemy 2.0
- Alembic

## Authentication & Security

- JWT authentication
- OAuth2-compatible login
- Argon2 password hashing
- Role-Based Access Control
- Security headers
- CORS
- Trusted Host validation
- Login rate limiting
- Audit logging

## Laboratory Management

- Patient management
- Sample management
- Laboratory tests
- Laboratory results
- PDF reports
- Data exports

## Biomedical Equipment

- Biomedical equipment management
- Equipment lifecycle
- Calibration management
- Calibration history
- Maintenance management
- Maintenance schedules
- Maintenance records

## Asynchronous Processing

- Redis
- Celery
- Celery Worker
- Celery Beat
- Asynchronous PDF generation
- Asynchronous laboratory processing
- Automated calibration monitoring
- Automated notifications
- Retry policies
- Fault tolerance

## Analytics

- Dashboard statistics
- Laboratory analytics
- Data filtering
- Date ranges
- CSV export
- Excel export
- JSON export
- PDF export

## Observability

- Structured application logging
- Request IDs
- HTTP metrics
- Prometheus metrics
- Health checks
- Liveness
- Readiness
- Celery task monitoring

## DevOps

- Docker
- Docker Compose
- Production Docker image
- Non-root production container
- GitHub Actions
- Automated testing
- Ruff
- Bandit
- Pytest
- Docker image publishing

---

# Architecture

MedLab follows a layered backend architecture:

        Client
        │
        ▼
        FastAPI Router
        │
        ▼
        Service Layer
        │
        ▼
        Repository Layer
        │
        ▼
        SQLAlchemy
        │
        ▼
        PostgreSQL

Procesamiento asíncrono:

        FastAPI
        │
        ▼
        Redis
        │
        ▼
        Celery Worker
        │
        ├── Laboratory processing
        ├── PDF reports
        ├── Notifications
        └── Calibration automation

Tareas programadas:

        Celery Beat
        │
        ▼
        Redis
        │
        ▼
        Celery Worker
