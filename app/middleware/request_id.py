"""
Request ID Middleware
======================
Assigns a unique request ID to every incoming HTTP request.

The request ID is:
1. Taken from the ``X-Request-ID`` header if provided by an upstream gateway.
2. Generated as a UUID4 if no header is present.

The ID is:
* Attached to ``request.state.request_id`` for use in route handlers.
* Echoed back in the ``X-Request-ID`` response header for client-side correlation.
* Available (in a future sprint) via a ``ContextVar`` for inclusion in log records.

This middleware is the foundation of distributed tracing within the platform.
"""

from __future__ import annotations

import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ai_analysis_engine.middleware.request_id")

# ---------------------------------------------------------------------------
# Future extension point:  ContextVar for correlation ID in log records
# ---------------------------------------------------------------------------
# from contextvars import ContextVar
# correlation_id_ctx_var: ContextVar[str] = ContextVar("correlation_id", default="n/a")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that injects a unique request ID into every request.

    The ID propagates through the entire request lifecycle and appears in
    every log record produced during that request (once the logging filter
    reads from the ContextVar).
    """

    REQUEST_ID_HEADER: str = "X-Request-ID"

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        # Honour upstream ID if present; generate a fresh one otherwise.
        request_id: str = (
            request.headers.get(self.REQUEST_ID_HEADER) or str(uuid.uuid4())
        )

        # Attach to request state so route handlers can read it.
        request.state.request_id = request_id

        # Future: correlation_id_ctx_var.set(request_id)

        logger.debug("Request started | request_id=%s | path=%s", request_id, request.url.path)

        response: Response = await call_next(request)

        # Echo the ID back so clients can correlate with their own logs.
        response.headers[self.REQUEST_ID_HEADER] = request_id

        return response
