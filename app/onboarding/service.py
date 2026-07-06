"""
Project Onboarding Service
==========================
Coordinates the CRUD service logic for registering, updating, listing, and
deleting onboarding configs in the data storage layers.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.onboarding.schemas import ProjectOnboardingConfig
from app.storage.base import StorageInterface
from app.exceptions.custom_exceptions import ValidationError

logger = logging.getLogger("ai_analysis_engine.onboarding.service")


class OnboardingService:
    """Handles CRUD commands on onboarding configs."""

    def __init__(self, store: StorageInterface) -> None:
        self.store = store

    async def register_project(self, config: ProjectOnboardingConfig) -> ProjectOnboardingConfig:
        """Insert a new project configuration. Fails if project_id exists."""
        existing = await self.store.get("projects", config.project_id)
        if existing:
            raise ValidationError(
                message=f"Project with ID '{config.project_id}' is already registered.",
                detail={"project_id": config.project_id}
            )
        
        # Save record (InMemoryStore assigns id, but we map slug id manually as database key)
        record = config.model_dump()
        record["id"] = config.project_id
        
        saved = await self.store.save("projects", record)
        logger.info("Project '%s' successfully registered.", config.project_id)
        return ProjectOnboardingConfig(**saved)

    async def update_project(
        self,
        project_id: str,
        config: ProjectOnboardingConfig
    ) -> ProjectOnboardingConfig:
        """Update an existing configuration. Fails if not registered."""
        existing = await self.store.get("projects", project_id)
        if not existing:
            raise ValidationError(
                message=f"Project with ID '{project_id}' does not exist.",
                detail={"project_id": project_id}
            )

        record = config.model_dump()
        record["id"] = project_id
        
        saved = await self.store.save("projects", record)
        logger.info("Project '%s' successfully updated.", project_id)
        return ProjectOnboardingConfig(**saved)

    async def get_project(self, project_id: str) -> Optional[ProjectOnboardingConfig]:
        """Fetch project details by slug ID."""
        record = await self.store.get("projects", project_id)
        if not record:
            return None
        return ProjectOnboardingConfig(**record)

    async def list_projects(self) -> list[ProjectOnboardingConfig]:
        """List all active onboarding configurations."""
        records = await self.store.list("projects")
        return [ProjectOnboardingConfig(**r) for r in records]

    async def delete_project(self, project_id: str) -> bool:
        """Remove a project registration. Returns True if deleted."""
        deleted = await self.store.delete("projects", project_id)
        if deleted:
            logger.info("Project '%s' deleted successfully.", project_id)
        return deleted
