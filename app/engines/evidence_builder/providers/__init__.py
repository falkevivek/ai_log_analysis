# Evidence Providers package init

from __future__ import annotations

from app.engines.evidence_builder.providers.base import BaseEvidenceProvider
from app.engines.evidence_builder.providers.defaults import (
    MetricsEvidenceProvider,
    DeploymentEvidenceProvider,
    SecurityEvidenceProvider,
)

def get_default_evidence_providers() -> list[BaseEvidenceProvider]:
    """Return the registered default evidence providers list."""
    return [
        MetricsEvidenceProvider(),
        DeploymentEvidenceProvider(),
        SecurityEvidenceProvider(),
    ]

__all__ = [
    "BaseEvidenceProvider",
    "get_default_evidence_providers",
    "MetricsEvidenceProvider",
    "DeploymentEvidenceProvider",
    "SecurityEvidenceProvider",
]
