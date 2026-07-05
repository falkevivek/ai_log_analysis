"""
Placeholder Context Providers for the MVP
==========================================
Implements in-memory placeholder providers for gathering context.
These can be replaced by actual Project Onboarding queries in later sprints.
"""

from __future__ import annotations

from typing import Any

from app.engines.context_enrichment.providers.base import BaseContextProvider
from app.schemas.domain import Incident


class OnboardingProjectProvider(BaseContextProvider):
    """Provides project, environment, and application mapping details."""

    @property
    def provider_name(self) -> str:
        return "PROJECT_PROVIDER"

    def enrich(self, incident: Incident) -> dict[str, Any]:
        # Reads from the incident's built-in metadata, fallback to onboarding defaults
        meta = incident.incident_metadata
        project = meta.project if meta.project and meta.project != "unknown" else "Enterprise Retail Banking System"
        environment = meta.environment if meta.environment and meta.environment != "unknown" else "production"
        application = meta.application if meta.application and meta.application != "unknown" else "payments-processor"
        return {
            "project_name": project,
            "environment": environment,
            "application": application
        }



class ApiMetadataProvider(BaseContextProvider):
    """Simulates looking up API gateway endpoints mapping for components."""

    @property
    def provider_name(self) -> str:
        return "API_METADATA_PROVIDER"

    def enrich(self, incident: Incident) -> dict[str, Any]:
        api_maps = {
            "auth-filter": {
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "rate_limit": "100req/min",
                "auth_type": "Bearer Token"
            },
            "database": {
                "connection_pool": "pg-pool-01",
                "max_connections": 100,
                "read_replica": "enabled"
            }
        }
        
        enriched: dict[str, Any] = {}
        for comp in incident.affected_components:
            comp_clean = comp.lower().strip()
            if comp_clean in api_maps:
                enriched[comp_clean] = api_maps[comp_clean]
        return {"api_metadata": enriched}


class KnownErrorsProvider(BaseContextProvider):
    """Simulates database lookup for component error code definitions."""

    @property
    def provider_name(self) -> str:
        return "KNOWN_ERRORS_PROVIDER"

    def enrich(self, incident: Incident) -> dict[str, Any]:
        error_definitions = {
            "auth-filter": ["ERR_AUTH_EXPIRED_TOKEN", "ERR_CREDENTIALS_MISMATCH"],
            "database": ["ERR_POOL_EXHAUSTED", "ERR_CONNECTION_TIMEOUT"],
            "api-gateway": ["ERR_GATEWAY_TIMEOUT", "ERR_UPSTREAM_SERVICE_DOWN"]
        }

        found_codes = []
        for comp in incident.affected_components:
            comp_clean = comp.lower().strip()
            if comp_clean in error_definitions:
                found_codes.extend(error_definitions[comp_clean])
        return {"known_errors": sorted(list(set(found_codes)))}


class HistoricalReferencesProvider(BaseContextProvider):
    """Simulates query for previous similar incident records."""

    @property
    def provider_name(self) -> str:
        return "HISTORICAL_REFERENCES_PROVIDER"

    def enrich(self, incident: Incident) -> dict[str, Any]:
        # Returns simulated historical references depending on components
        references = []
        if "database" in incident.affected_components:
            references.append("INC-2026-0043")  # DB Timeout issue
        if "auth-filter" in incident.affected_components:
            references.append("INC-2026-0105")  # Auth Gateway Lockout
        return {"historical_references": references}


class ConfigurationMetadataProvider(BaseContextProvider):
    """Provides active configs, deployment variables, and timeouts."""

    @property
    def provider_name(self) -> str:
        return "CONFIGURATION_METADATA_PROVIDER"

    def enrich(self, incident: Incident) -> dict[str, Any]:
        return {
            "config_metadata": {
                "active_deployment_version": "v1.42.0",
                "commit_hash": "a8f9c2d1b7e4f3a",
                "http_timeout_seconds": 15.0,
                "retry_policy": "exponential_backoff_3"
            }
        }
