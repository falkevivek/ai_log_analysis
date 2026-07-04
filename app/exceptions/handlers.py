"""
Global Exception Handlers
===========================
Registers exception handlers on the FastAPI application so every unhandled
exception produces a consistent JSON response envelope.

All error responses conform to ``ErrorResponse`` so API clients can rely on
a stable, predictable structure regardless of the error origin.

Handler registration order matters — more specific handlers must be
registered before more general ones.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.custom_exceptions import AppBaseException
from app.schemas.base import ErrorResponse

logger = logging.getLogger("ai_analysis_engine.exceptions")


# ---------------------------------------------------------------------------
# Handler functions
# ---------------------------------------------------------------------------

async def handle_app_exception(request: Request, exc: AppBaseException) -> JSONResponse:
    """Handle all exceptions that inherit from ``AppBaseException``."""
    logger.error(
        "Application exception | path=%s | error_code=%s | message=%s",
        request.url.path,
        exc.error_code,
        exc.message,
    )
    body = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        detail=exc.detail,
        path=str(request.url.path),
    )
    return JSONResponse(status_code=exc.http_status_code, content=body.model_dump(mode="json"))


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette HTTP exceptions (e.g. 404 from routing)."""
    logger.warning(
        "HTTP exception | path=%s | status=%d", request.url.path, exc.status_code
    )
    body = ErrorResponse(
        error_code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        path=str(request.url.path),
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump(mode="json"))


async def handle_validation_exception(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic request validation errors."""
    errors = [
        {
            "field": " → ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    logger.warning("Validation error | path=%s | errors=%s", request.url.path, errors)
    body = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request validation failed. See 'detail' for per-field errors.",
        detail=errors,
        path=str(request.url.path),
    )
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for any exception not matched by a more specific handler."""
    logger.critical(
        "Unhandled exception | path=%s | type=%s | error=%s",
        request.url.path,
        type(exc).__name__,
        str(exc),
        exc_info=True,
    )
    body = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. The engineering team has been notified.",
        path=str(request.url.path),
    )
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(AppBaseException, handle_app_exception)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, handle_validation_exception)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, handle_unhandled_exception)  # type: ignore[arg-type]
    logger.debug("Exception handlers registered.")
