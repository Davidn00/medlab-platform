# MedLab Platform — Architecture

## Overview

MedLab Platform is a backend platform for biomedical laboratory
management inspired by a LIMS (Laboratory Information Management System).

The application follows a layered architecture designed to separate:

- HTTP/API concerns
- Business logic
- Data access
- Persistence
- Asynchronous processing
- Infrastructure

## High-Level Architecture

```mermaid
flowchart TD

    Client[API Client]

    API[FastAPI]

    Router[API Router]

    Service[Service Layer]

    Repository[Repository Layer]

    ORM[SQLAlchemy 2.0]

    DB[(PostgreSQL)]

    Redis[(Redis)]

    Celery[Celery Worker]

    Beat[Celery Beat]

    Client --> API
    API --> Router
    Router --> Service
    Service --> Repository
    Repository --> ORM
    ORM --> DB

    Service --> Redis
    Redis --> Celery

    Beat --> Redis
    Celery --> DB