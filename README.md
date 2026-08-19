# MedLab Platform

Backend API para gestión de laboratorios biomédicos,
inspirado en sistemas LIMS (Laboratory Information
Management System).

## Características

- JWT Authentication
- RBAC
- Gestión de usuarios
- Gestión de pacientes
- Gestión de muestras
- Gestión de pruebas de laboratorio
- Resultados
- Reportes PDF
- Auditoría
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Pytest
- Docker
- GitHub Actions

## Arquitectura

Router → Service → Repository → SQLAlchemy → PostgreSQL

## Stack tecnológico

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Argon2
- Pytest
- Docker
- GitHub Actions

## Ejecución

### 1. Clonar

```bash
git clone <repository-url>
cd MedLab-Platform