"""
API Response Schemas
=====================
Shared Pydantic models that define the envelope shape of every API response.

Every endpoint — success or error — returns one of these types so that API
consumers can parse responses without conditional logic.

The ``success`` boolean lets clients branch on a single field rather than
inspecting HTTP status codes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Current UTC timestamp (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


class BaseResponse(BaseModel):
    """
    Root response envelope included in every API response.

    Attributes
    ----------
    success:
        ``True`` for 2xx responses, ``False`` for errors.
    timestamp:
        UTC timestamp when the response was produced.
    request_id:
        Correlation ID from the ``X-Request-ID`` header.
    """

    success: bool = Field(description="Whether the request succeeded")
    timestamp: datetime = Field(default_factory=_utc_now, description="UTC response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")

    model_config = {"populate_by_name": True}


class SuccessResponse(BaseResponse):
    """
    Envelope for successful API responses.

    Attributes
    ----------
    message:
        Human-readable confirmation message.
    data:
        Response payload — any serialisable type, or ``None``.
    """

    success: bool = Field(default=True)
    message: str = Field(description="Human-readable success message")
    data: Optional[Any] = Field(default=None, description="Response payload")


class ErrorResponse(BaseResponse):
    """
    Envelope for error API responses.

    Attributes
    ----------
    error_code:
        Machine-readable error identifier clients switch on.
    message:
        Human-readable error description.
    detail:
        Optional supplementary diagnostic information.
    path:
        The URL path that triggered the error.
    """

    success: bool = Field(default=False)
    error_code: str = Field(description="Machine-readable error identifier")
    message: str = Field(description="Human-readable error description")
    detail: Optional[Any] = Field(default=None, description="Supplementary diagnostic info")
    path: Optional[str] = Field(default=None, description="URL path that produced this error")


class HealthResponse(BaseResponse):
    """
    Response schema for ``GET /health``.

    Attributes
    ----------
    status:
        Overall platform status: ``"healthy"`` | ``"degraded"`` | ``"unhealthy"``.
    version:
        Application semantic version string.
    environment:
        Active deployment environment.
    components:
        Per-component status keyed by component name.
    uptime_seconds:
        Seconds elapsed since the application process started.
    """

    success: bool = Field(default=True)
    status: str = Field(description="Overall platform health status")
    version: str = Field(description="Application version")
    environment: str = Field(description="Active deployment environment")
    components: dict[str, str] = Field(
        default_factory=dict, description="Per-component status"
    )
    uptime_seconds: Optional[float] = Field(default=None, description="Process uptime in seconds")
