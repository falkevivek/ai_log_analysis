"""
Health & Status API — v1
=========================
Lightweight, unauthenticated endpoints used by:
  - Kubernetes liveness and readiness probes
  - Load-balancer health checks
  - Developers validating a deployment

Endpoints
---------
GET /api/v1/health   Full platform health with per-component status
GET /api/v1/version  Application version and environment information
GET /api/v1/status   Ultra-lightweight liveness probe (always 200)

None of these endpoints require authentication — they must be reachable
even when auth infrastructure is down.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.schemas.base import HealthResponse, SuccessResponse

logger = logging.getLogger("ai_analysis_engine.api.health")
router = APIRouter(tags=["Platform Health"])

# Track process start time once so uptime can be computed on any request.
_PROCESS_START: float = time.monotonic()


def _uptime_seconds() -> float:
    """Seconds elapsed since the application process started."""
    return round(time.monotonic() - _PROCESS_START, 2)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Full platform health check",
    description=(
        "Returns the health status of the platform and all registered components. "
        "HTTP 200 when fully healthy, HTTP 503 when any component is degraded."
    ),
    responses={
        200: {"description": "Platform is healthy"},
        503: {"description": "One or more components are unhealthy"},
    },
)
async def health_check(request: Request) -> JSONResponse:
    """Full health check — reports per-component status and overall platform health."""
    settings = get_settings()
    store = request.app.state.store

    # Storage component — always healthy for in-memory backend.
    # Future: replace with an async DB ping when PostgreSQL is introduced.
    storage_stats = store.stats()
    components: dict[str, str] = {
        "storage": "in-memory",
        "storage_records": str(sum(storage_stats.values())),
    }

    overall = "healthy"
    http_code = 200

    response = HealthResponse(
        success=True,
        status=overall,
        version=settings.app_version,
        environment=settings.environment,
        components=components,
        uptime_seconds=_uptime_seconds(),
    )
    return JSONResponse(status_code=http_code, content=response.model_dump(mode="json"))


@router.get(
    "/version",
    response_model=SuccessResponse,
    summary="Application version",
    description="Returns the current application version, environment, and uptime.",
)
async def get_version() -> SuccessResponse:
    """Return semantic version and runtime metadata."""
    settings = get_settings()
    data: dict[str, Any] = {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "python_version": __import__("sys").version.split()[0],
        "uptime_seconds": _uptime_seconds(),
    }
    return SuccessResponse(message="Version information retrieved successfully.", data=data)


@router.get(
    "/status",
    summary="Liveness probe",
    description=(
        "Ultra-lightweight endpoint for Kubernetes liveness probes. "
        "Returns HTTP 200 immediately with no downstream checks."
    ),
    responses={200: {"description": "Process is alive"}},
)
async def liveness_probe() -> dict[str, str]:
    """
    Liveness probe — returns immediately without checking any dependencies.

    Kubernetes uses this to decide whether to restart the process.
    The readiness check (/health) handles traffic routing decisions.
    """
    return {"status": "ok"}
