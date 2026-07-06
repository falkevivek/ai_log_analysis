"""
Base Evidence Provider Interface
=================================
Defines the abstract interface that every custom evidence provider must implement.

Evidence providers collect supplemental facts (such as metrics, security audits,
or deployment state) to enrich the final Evidence Package sent to the AI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.domain import Incident, Context


class BaseEvidenceProvider(ABC):
    """Abstract base class for all pluggable evidence collection layers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier of the provider (e.g., 'SECURITY_EVIDENCE_PROVIDER')."""
        ...

    @abstractmethod
    def collect(self, incident: Incident, context: Context) -> dict[str, Any]:
        """
        Gather facts from external resources or local logs.

        Must swallow exceptions internally and return a dictionary of gathered facts
        (empty dictionary on failure) to prevent pipeline halts.
        """
        ...
