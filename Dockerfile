# ---------------------------------------------------------
# Imagen base
# ---------------------------------------------------------

FROM python:3.13-slim


# ---------------------------------------------------------
# Variables de entorno de Python
# ---------------------------------------------------------

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Hace que los logs aparezcan inmediatamente
ENV PYTHONUNBUFFERED=1


# ---------------------------------------------------------
# Directorio de trabajo
# ---------------------------------------------------------

WORKDIR /app


# ---------------------------------------------------------
# Instalar dependencias
# ---------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ---------------------------------------------------------
# Copiar código de la aplicación
# ---------------------------------------------------------

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .


# ---------------------------------------------------------
# Puerto de FastAPI
# ---------------------------------------------------------

EXPOSE 8000


# ---------------------------------------------------------
# Comando para iniciar FastAPI
# ---------------------------------------------------------

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]