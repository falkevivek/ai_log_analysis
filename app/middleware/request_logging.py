"""
Request Logging Middleware
===========================
Logs every inbound HTTP request and its corresponding response.

Log record includes:
* HTTP method and path
* Query string (if present)
* Client IP address
* Response status code
* Processing duration in milliseconds
* Request ID for log correlation

Sensitive headers (Authorization, Cookie) are explicitly excluded from logs
to comply with Barclays data-handling policies.

Performance note: timing is measured around ``await call_next(request)`` which
includes all downstream middleware and route handler execution time.  This gives
a realistic end-to-end latency figure that matches what the client experiences.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ai_analysis_engine.middleware.request_logging")

# Headers that must never appear in log output.
_SENSITIVE_HEADERS: frozenset[str] = frozenset(
    {"authorization", "cookie", "set-cookie", "x-api-key"}
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that produces structured access logs for every request.

    Placed after ``RequestIdMiddleware`` in the middleware stack so that
    ``request.state.request_id`` is already populated when this runs.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start_time: float = time.perf_counter()

        request_id: str = getattr(request.state, "request_id", "n/a")
        client_host: str = request.client.host if request.client else "unknown"

        logger.info(
            "→ REQUEST  | id=%s | %s %s | client=%s | query=%s",
            request_id,
            request.method,
            request.url.path,
            client_host,
            str(request.url.query) or "-",
        )

        response: Response = await call_next(request)

        duration_ms: float = (time.perf_counter() - start_time) * 1_000

        log_fn = logger.info if response.status_code < 400 else logger.warning

        log_fn(
            "← RESPONSE | id=%s | %s %s | status=%d | duration=%.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
