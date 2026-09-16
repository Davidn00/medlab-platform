
# Authentication Diagram

    participant Client
    participant API as FastAPI
    participant Auth as Authentication
    participant DB as PostgreSQL

    Client->>API: POST /api/v1/auth/login
    API->>Auth: Validate credentials
    Auth->>DB: Find user
    DB-->>Auth: User
    Auth->>Auth: Verify Argon2 password
    Auth->>Auth: Generate JWT
    Auth-->>Client: Access Token

    Client->>API: Request + Bearer Token
    API->>Auth: Validate JWT
    Auth->>Auth: Check role
    Auth-->>API: Authorized user
    API-->>Client: Response

Roles:
    ADMIN
 ├── User management
 ├── Laboratory management
 └── Administrative operations

TECHNICIAN
 ├── Samples
 ├── Laboratory processing
 └── Equipment operations

DOCTOR
 ├── Patient information
 ├── Laboratory results
 └── Reports