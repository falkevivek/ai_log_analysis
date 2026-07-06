"""
Default Evidence Providers for the MVP
=======================================
Implements metrics, security audit, and deployment evidence collectors.
"""

from __future__ import annotations

from typing import Any

from app.engines.evidence_builder.providers.base import BaseEvidenceProvider
from app.schemas.domain import Incident, Context


class MetricsEvidenceProvider(BaseEvidenceProvider):
    """Simulates lookup for system and database performance metrics."""

    @property
    def provider_name(self) -> str:
        return "METRICS_EVIDENCE_PROVIDER"

    def collect(self, incident: Incident, context: Context) -> dict[str, Any]:
        # Returns simulated resource metrics matched to components
        metrics = {
            "system_cpu_utilization_percent": 82.4,
            "system_memory_utilization_percent": 68.1,
            "active_db_connections": 94,
            "connection_pool_saturation_percent": 94.0
        }
        return {"supporting_metrics": metrics}


class DeploymentEvidenceProvider(BaseEvidenceProvider):
    """Simulates query for deployment versions and pipeline parameters."""

    @property
    def provider_name(self) -> str:
        return "DEPLOYMENT_EVIDENCE_PROVIDER"

    def collect(self, incident: Incident, context: Context) -> dict[str, Any]:
        # Reads deployment data from context configuration, fallback to default release notes
        deploy_info = {
            "version": context.config_metadata.get("active_deployment_version", "v1.42.0"),
            "commit_hash": context.config_metadata.get("commit_hash", "a8f9c2d1b7e4f3a"),
            "build_status": "SUCCESSFUL",
            "last_deploy_timestamp": "2026-07-05T08:00:00Z"
        }
        return {"deployment_info": deploy_info}


class SecurityEvidenceProvider(BaseEvidenceProvider):
    """Simulates lookup for security events (rate limiting, auth violations)."""

    @property
    def provider_name(self) -> str:
        return "SECURITY_EVIDENCE_PROVIDER"

    def collect(self, incident: Incident, context: Context) -> dict[str, Any]:
        security_metadata = {
            "ip_blocklist_triggers": 0,
            "rate_limit_violations": 12,
            "brute_force_score": 0.15,
            "security_alerts_active": False
        }
        return {"security_metadata": security_metadata}
