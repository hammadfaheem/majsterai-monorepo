"""HTTP middleware for cross-cutting concerns.

Included in ``main.py`` via ``app.add_middleware``.
"""

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Context variable so any logger inside a request can read the current ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign a unique ID to every inbound request.

    - Reads ``X-Request-ID`` from the client if present; otherwise generates one.
    - Stores it in ``request.state.request_id`` and ``request_id_var``.
    - Echoes it back in the ``X-Request-ID`` response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with method, path, status, and duration.

    Produces one structured log line per request at INFO level so that any
    JSON-aware log aggregator (Datadog, CloudWatch, GCP Logging, …) can index
    them without further parsing.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "")

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
