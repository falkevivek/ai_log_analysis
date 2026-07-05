"""
FastAPI Application Entry Point
================================
Constructs and configures the FastAPI application instance.

This module is the composition root. It wires together all platform components
without containing any business logic itself.

Responsibilities
----------------
1. Define the lifespan context (startup / shutdown hooks).
2. Configure logging during application startup lifespan.
3. Register middleware, exception handlers, and API routers.
4. Expose the ``app`` instance consumed by Uvicorn.

PostgreSQL Migration
--------------------
When PostgreSQL is introduced, replace the ``InMemoryStore`` import with
the PostgreSQL implementation and update the lifespan to open/close the
connection pool. No other file changes are required.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.logging import configure_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.storage.memory import InMemoryStore
from app.api.v1 import health as health_router

# Lazy-loaded logger. Module-level logger is fine to declare here,
# but it won't emit styled logs until configure_logging() executes inside lifespan.
logger = logging.getLogger("ai_analysis_engine.main")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle resources.

    Startup:
        Configure application logging from settings dynamically.
        Initialise the in-memory store and attach it to ``app.state``.
        Future: open PostgreSQL connection pool, warm ML model caches.

    Shutdown:
        Release any held resources.
        Future: close connection pool, flush queues.
    """
    settings = get_settings()

    # Move logging setup inside startup context so it runs dynamically
    # and has no side effects during import time.
    configure_logging(settings.log_level)

    logger.info("Starting %s v%s (%s)", settings.app_name, settings.app_version, settings.environment)

    # Attach the store to app.state so all route handlers can access it
    # via ``request.app.state.store`` without any dependency injection wiring.
    app.state.store = InMemoryStore()

    logger.info("Platform ready — storage: in-memory")

    yield

    logger.info("Shutting down %s", settings.app_name)


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_application() -> FastAPI:
    """
    Build and return a fully configured FastAPI application.

    Using a factory function (rather than module-level instantiation) makes it
    straightforward to create isolated application instances for testing or
    for future multi-tenant scenarios.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # CORS — must be registered before custom middleware.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (outermost = executes first on request, last on response).
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Global exception handlers.
    register_exception_handlers(app)

    # API routers.
    app.include_router(health_router.router, prefix=settings.api_prefix)

    # Future routers will be mounted here.
    return app


# Module-level instance consumed by Uvicorn.
app: FastAPI = create_application()
