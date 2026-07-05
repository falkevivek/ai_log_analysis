# Context Providers package init

from __future__ import annotations

from app.engines.context_enrichment.providers.base import BaseContextProvider
from app.engines.context_enrichment.providers.onboarding_placeholders import (
    OnboardingProjectProvider,
    ApiMetadataProvider,
    KnownErrorsProvider,
    HistoricalReferencesProvider,
    ConfigurationMetadataProvider,
)

def get_default_context_providers() -> list[BaseContextProvider]:
    """Return the registered default providers list."""
    return [
        OnboardingProjectProvider(),
        ApiMetadataProvider(),
        KnownErrorsProvider(),
        HistoricalReferencesProvider(),
        ConfigurationMetadataProvider(),
    ]

__all__ = [
    "BaseContextProvider",
    "get_default_context_providers",
    "OnboardingProjectProvider",
    "ApiMetadataProvider",
    "KnownErrorsProvider",
    "HistoricalReferencesProvider",
    "ConfigurationMetadataProvider",
]
