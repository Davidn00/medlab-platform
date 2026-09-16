
# Database Diagram


    USERS ||--o{ AUDIT_LOGS : creates
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ MAINTENANCES : creates

    PATIENTS ||--o{ SAMPLES : has

    SAMPLES ||--o{ LABORATORY_TESTS : contains

    BIOMEDICAL_EQUIPMENT ||--o{ CALIBRATIONS : has
    BIOMEDICAL_EQUIPMENT ||--o{ LABORATORY_TESTS : performs
    BIOMEDICAL_EQUIPMENT ||--o{ MAINTENANCES : receives
    BIOMEDICAL_EQUIPMENT ||--o{ MAINTENANCE_RECORDS : has
    BIOMEDICAL_EQUIPMENT ||--o{ MAINTENANCE_SCHEDULES : has
    BIOMEDICAL_EQUIPMENT ||--o{ EQUIPMENT_LIFECYCLE_EVENTS : has

    USERS {
        uuid id PK
        string full_name
        string email
        string hashed_password
        string role
        boolean is_active
    }

    PATIENTS {
        uuid id PK
        string medical_record
        string first_name
        string last_name
        date birth_date
        string gender
        string email
    }

    SAMPLES {
        uuid id PK
        string sample_code
        uuid patient_id FK
        string sample_type
        string status
        datetime collected_at
        datetime received_at
    }

    LABORATORY_TESTS {
        uuid id PK
        uuid sample_id FK
        uuid equipment_id FK
        string test_name
        string result_value
        string unit
        string reference_range
        string status
    }

    BIOMEDICAL_EQUIPMENT {
        uuid id PK
        string name
        string manufacturer
        string model
        string serial_number
        string location
        string status
    }

    CALIBRATIONS {
        uuid id PK
        uuid equipment_id FK
        datetime calibration_date
        datetime next_calibration_date
        string performed_by
        string status
    }

    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        string notification_type
        string title
        string message
        boolean is_read
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string entity_name
        string entity_id
        string action
        string description
        datetime created_at
    }