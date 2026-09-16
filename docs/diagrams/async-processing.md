
# Async Processing Diagram

    participant Client
    participant API as FastAPI
    participant Redis
    participant Worker as Celery Worker
    participant DB as PostgreSQL

    Client->>API: Request
    API->>Redis: Queue task
    Redis->>Worker: Deliver task
    Worker->>DB: Process data
    DB-->>Worker: Result
    Worker-->>Redis: Task result
    API->>Redis: Query task status
    Redis-->>API: Status
    API-->>Client: Response