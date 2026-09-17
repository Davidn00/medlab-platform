## MedLab Platform — Cloud Deployment

MedLab Platform is deployed as a containerized FastAPI backend.

## Cloud Architecture

                         GitHub
                           │
                           ▼
                    GitHub Actions
                           │
              ┌────────────┼────────────┐
              │            │            │
            Ruff         Bandit       Pytest
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                     Docker Build
                           │
                           ▼
                        Render
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      FastAPI Web Service         Key Value / Valkey
             │                           │
       ┌─────┼─────┐                     │
       │     │     │                     │
     API  Worker  Beat                   │
       │     │     │                     │
       └─────┴─────┴─────────────────────┘
                           │
                           ▼
                    Neon PostgreSQL