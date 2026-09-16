
# Deployment Diagram

    GitHub[GitHub Repository]

    CI[GitHub Actions CI]

    Registry[GitHub Container Registry]

    Cloud[Cloud Infrastructure]

    API[FastAPI]

    PostgreSQL[(PostgreSQL)]

    Redis[(Redis)]

    Worker[Celery Worker]

    Beat[Celery Beat]

    GitHub --> CI
    CI --> Registry
    Registry --> Cloud

    Cloud --> API
    Cloud --> Worker
    Cloud --> Beat

    API --> PostgreSQL
    API --> Redis

    Worker --> PostgreSQL
    Worker --> Redis

    Beat --> Redis