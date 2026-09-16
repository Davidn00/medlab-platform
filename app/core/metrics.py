"""
Métricas Prometheus de MedLab Platform.
"""

from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "medlab_http_requests_total",
    "Total de solicitudes HTTP.",
    ["method", "path", "status"],
)


HTTP_REQUEST_DURATION = Histogram(
    "medlab_http_request_duration_seconds",
    "Duración de solicitudes HTTP.",
    ["method", "path"],
)


CELERY_TASKS_TOTAL = Counter(
    "medlab_celery_tasks_total",
    "Total de ejecuciones de tareas Celery.",
    ["task", "status"],
)
