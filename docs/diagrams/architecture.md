# Architecture Diagram

    Client[Client]

    API[FastAPI]

    V1[API v1]
    V2[API v2]

    Services[Service Layer]

    Repositories[Repository Layer]

    SQLAlchemy[SQLAlchemy 2.0]

    PostgreSQL[(PostgreSQL)]

    Client --> API
    API --> V1
    API --> V2

    V1 --> Services
    V2 --> Services

    Services --> Repositories
    Repositories --> SQLAlchemy
    SQLAlchemy --> PostgreSQL