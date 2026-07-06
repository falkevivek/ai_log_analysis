# API v1 package
# Version 1 of the public REST API surface.

from app.api.v1.onboarding import router as onboarding_router

__all__ = ["onboarding_router"]

