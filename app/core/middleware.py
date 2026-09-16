"""
Middleware de observabilidad y seguridad.

MedLab Platform
"""

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS_TOTAL,
)

logger = logging.getLogger("medlab.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Registra cada petición HTTP con:

    - request_id
    - método
    - path
    - status code
    - duración
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            "HTTP request started | request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            duration = time.perf_counter() - start_time

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                path=request.url.path,
            ).observe(duration)

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "HTTP request completed | "
                "request_id=%s method=%s path=%s status=%s duration=%.4fs",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

            return response

        except Exception:
            duration = time.perf_counter() - start_time

            logger.exception(
                "HTTP request failed | request_id=%s method=%s path=%s duration=%.4fs",
                request_id,
                request.method,
                request.url.path,
                duration,
            )

            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Añade headers HTTP de seguridad.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
