"""
Project Onboarding Providers
============================
Defines the client provider interfaces that AI engines use to consume
onboarding configurations without accessing onboarding storage directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.onboarding.schemas import ProjectOnboardingConfig
from app.storage.base import StorageInterface


class OnboardingProviderInterface(ABC):
    """Abstract interface exposing onboarding configs to the pipeline engines."""

    @abstractmethod
    async def get_project_config(self, project_id: str) -> Optional[ProjectOnboardingConfig]:
        """Fetch project configuration by unique slug identifier."""
        ...

    @abstractmethod
    async def get_project_config_by_name(
        self,
        project_name: str,
        environment: str
    ) -> Optional[ProjectOnboardingConfig]:
        """Fetch project configuration matching the name and environment tier."""
        ...


class StoreOnboardingProvider(OnboardingProviderInterface):
    """Concrete provider retrieving onboarding parameters from abstract StorageInterface."""

    def __init__(self, store: StorageInterface) -> None:
        """
        Initialize the provider with a storage repository backend.
        """
        self.store = store

    async def get_project_config(self, project_id: str) -> Optional[ProjectOnboardingConfig]:
        record = await self.store.get("projects", project_id)
        if not record:
            return None
        return ProjectOnboardingConfig(**record)

    async def get_project_config_by_name(
        self,
        project_name: str,
        environment: str
    ) -> Optional[ProjectOnboardingConfig]:
        records = await self.store.list("projects")
        for record in records:
            if (
                record.get("project_name", "").strip().lower() == project_name.strip().lower()
                and record.get("environment", "").strip().lower() == environment.strip().lower()
            ):
                return ProjectOnboardingConfig(**record)
        return None
