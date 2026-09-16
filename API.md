# MedLab Platform — API

## Base URLs

Development:
http://localhost:8188


Production:
https://your-domain

Interactive Documentation
/docs
/redoc
/openapi.json

Swagger UI:
/docs

API Versioning
MedLab supports:
/api/v1
/api/v2

Authentication
Login
POST /api/v1/auth/login

Users
GET /users/me
GET /users/{user_id}
GET /users/
POST /users/

Patients
POST /api/v1/patients
GET /api/v1/patients
GET /api/v1/patients/{patient_id}
PATCH /api/v1/patients/{patient_id}
DELETE /api/v1/patients/{patient_id}

Samples
POST /api/v1/samples
GET /api/v1/samples
GET /api/v1/samples/{sample_id}
GET /api/v1/samples/patient/{patient_id}
PATCH /api/v1/samples/{sample_id}
DELETE /api/v1/samples/{sample_id}

Laboratory Tests
POST /api/v1/laboratory-tests
GET /api/v1/laboratory-tests/{test_id}
GET /api/v1/laboratory-tests/sample/{sample_id}
PATCH /api/v1/laboratory-tests/{test_id}
DELETE /api/v1/laboratory-tests/{test_id}
POST /api/v1/laboratory-tests/{test_id}/process

Biomedical Equipment
POST /api/v1/biomedical-equipment
GET /api/v1/biomedical-equipment
GET /api/v1/biomedical-equipment/{equipment_id}
PUT /api/v1/biomedical-equipment/{equipment_id}
DELETE /api/v1/biomedical-equipment/{equipment_id}
GET /api/v1/biomedical-equipment/{equipment_id}/calibrations

Calibrations
POST /api/v1/calibrations
GET /api/v1/calibrations
GET /api/v1/calibrations/expiring
GET /api/v1/calibrations/expired
GET /api/v1/calibrations/{calibration_id}
PUT /api/v1/calibrations/{calibration_id}
DELETE /api/v1/calibrations/{calibration_id}

Notifications
GET /api/v1/notifications
PATCH /api/v1/notifications/{notification_id}/read

Maintenance
Maintenance and equipment lifecycle operations are available
through API v2.

/api/v2/maintenance
/api/v2/lifecycle

Dashboard
GET /api/v1/dashboard/statistics

Analytics
GET /api/v1/analytics

Exports
GET /api/v1/exports/{resource}

Reports
POST /api/v1/reports/sample/{sample_id}
GET /api/v1/reports/tasks/{task_id}
GET /api/v1/reports/sample/{sample_id}/pdf

Tasks
POST /api/v1/tasks/test
GET /api/v1/tasks/{task_id}

Health
GET /health
GET /health/live
GET /health/ready
GET /health/db
GET /health/redis

Metrics
Prometheus metrics:
GET /metrics


API v2

Version 2 currently exposes newer equipment,
calibration, maintenance, lifecycle, notification,
patient, sample and laboratory-test functionality.
Version information:
GET /api/v2/version