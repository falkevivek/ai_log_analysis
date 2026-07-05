"""
Base Context Provider Interface
================================
Defines the abstract interface that every context provider must implement.

Each provider is responsible for gathering one category of context details
(e.g., API schemas, deployment information, or historical references).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.domain import Incident


class BaseContextProvider(ABC):
    """Abstract base class for all context enrichment providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The unique identifier for this provider (e.g., 'API_METADATA_PROVIDER')."""
        ...

    @abstractmethod
    def enrich(self, incident: Incident) -> dict[str, Any]:
        """
        Fetch contextual data related to the incident.

        This method must catch all internal exceptions and return a dictionary
        of gathered facts (empty dict on failure) so the enrichment engine is robust.
        """
        ...
