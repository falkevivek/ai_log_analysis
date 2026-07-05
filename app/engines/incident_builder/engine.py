"""
Incident Builder Engine
=======================
Stage 6 of the AI Analysis pipeline.

Transforms a reconstructed Timeline into a formal Incident domain object.
Calculates duration, aggregates services/components, dynamically determines
severity based on configurable rules, and attaches extensible IncidentMetadata.

Responsibilities
----------------
1. Receive a Timeline object.
2. Initialize an Incident with a unique ID and status.
3. Compute start_time, end_time, and duration from the Timeline.
4. Calculate Incident severity based on configurable SeverityEvaluationRules.
5. Aggregate affected services and components from the Timeline.
6. Count total events and observations involved.
7. Generate a natural language incident summary.
8. Attach structured extensible metadata (category, priority, env, project, tags).

This engine does NOT
--------------------
- Perform root cause analysis.
- Connect to LLMs or suggest fixes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from pydantic import BaseModel, Field

from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Timeline, Incident, IncidentMetadata

logger = logging.getLogger("ai_analysis_engine.engines.incident_builder.engine")


class SeverityThresholdRule(BaseModel):
    """Configurable rule to promote incident severity based on threshold metrics."""

    max_duration_low_seconds: float = 30.0
    max_duration_medium_seconds: float = 120.0
    critical_components: list[str] = Field(default_factory=lambda: ["database", "auth-service"])
    critical_severity_trigger_count: int = 5


class IncidentConfig(BaseModel):
    """Configuration options for Incident builder and metadata defaults."""

    # Default metadata fields that can be overridden by custom onboarding configuration
    default_category: str = "software"
    default_priority: str = "P3"
    default_environment: str = "production"
    default_application: str = "core-banking"
    default_project: str = "ai-analysis-pipeline"
    default_tags: list[str] = Field(default_factory=list)

    # Status value for newly created incidents
    initial_status: str = "ACTIVE"

    # Severity rules
    severity_rules: SeverityThresholdRule = Field(default_factory=SeverityThresholdRule)


class IncidentBuilder:
    """Consolidates Timeline data and creates a structured Incident object."""

    def __init__(
        self,
        config: Optional[IncidentConfig] = None,
        custom_severity_calculator: Optional[Callable[[Timeline, IncidentConfig], str]] = None
    ) -> None:
        """
        Initialize the Incident Builder.

        Parameters
        ----------
        config:
            Optional IncidentConfig with metadata defaults and severity rules.
        custom_severity_calculator:
            Optional custom function to compute severity. Allows onboarding clients
            to inject custom logic without editing the core engine.
        """
        self.config = config or IncidentConfig()
        self.severity_calculator = custom_severity_calculator or self._calculate_default_severity
        logger.info(
            "IncidentBuilder initialized (default env: %s, initial status: %s)",
            self.config.default_environment,
            self.config.initial_status
        )

    def build_incident(
        self,
        timeline: Timeline,
        metadata_overrides: Optional[dict[str, Any]] = None
    ) -> Incident:
        """
        Build an Incident from a Timeline.

        Parameters
        ----------
        timeline:
            The reconstructed execution Timeline.
        metadata_overrides:
            Optional overrides for the IncidentMetadata fields.

        Returns
        -------
        Incident
            The constructed and validated Incident object.

        Raises
        ------
        ValidationError
            If the timeline is invalid or if validation fails.
        """
        if not timeline:
            raise ValidationError(
                message="Cannot build an Incident from an empty or missing Timeline.",
                detail={"engine": "IncidentBuilder"}
            )

        logger.debug("Building Incident for timeline: %s", timeline.timeline_id)

        # Step 1: Calculate time-related properties
        start_time = timeline.start_time
        end_time = timeline.end_time
        duration = timeline.duration

        # Step 2: Aggregate affected services and components
        services = sorted(list(set(timeline.affected_services)))
        components = sorted(list(set(timeline.affected_components)))

        # Step 3: Compute related counts
        related_events_count = len(timeline.events)
        related_observations_count = sum(len(e.observations) for e in timeline.events)

        # Step 4: Determine Severity using the configured calculator
        severity = self.severity_calculator(timeline, self.config)

        # Step 5: Construct extensible IncidentMetadata
        overrides = metadata_overrides or {}
        incident_metadata = IncidentMetadata(
            category=overrides.get("category", self.config.default_category),
            priority=overrides.get("priority", self.config.default_priority),
            environment=overrides.get("environment", self.config.default_environment),
            application=overrides.get("application", self.config.default_application),
            project=overrides.get("project", self.config.default_project),
            tags=overrides.get("tags", self.config.default_tags)
        )

        # Step 6: Generate Summary
        summary = (
            f"Incident detected in environment '{incident_metadata.environment}' "
            f"for application '{incident_metadata.application}'. "
            f"Impacted services: {', '.join(services) if services else 'none'}. "
            f"Timeline spans {duration:.2f} seconds containing {related_events_count} events "
            f"and {related_observations_count} observations. Severity: {severity}."
        )

        try:
            incident = Incident(
                incident_id=str(uuid.uuid4()),
                timeline_id=timeline.timeline_id,
                timeline=timeline,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                severity=severity,
                status=self.config.initial_status,
                summary=summary,
                affected_services=services,
                affected_components=components,
                related_events_count=related_events_count,
                related_observations_count=related_observations_count,
                created_at=datetime.now(timezone.utc),
                incident_metadata=incident_metadata
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Incident domain contract: {str(exc)}",
                detail={"timeline_id": timeline.timeline_id}
            ) from exc

        logger.info(
            "Incident constructed successfully | ID=%s | severity=%s | status=%s",
            incident.incident_id,
            incident.severity,
            incident.status
        )
        return incident

    @staticmethod
    def _calculate_default_severity(timeline: Timeline, config: IncidentConfig) -> str:
        """
        Default rule-based severity calculator.

        Rules:
        - CRITICAL: if total observations count >= critical_severity_trigger_count or any critical components are impacted.
        - HIGH: if duration > max_duration_medium_seconds.
        - MEDIUM: if duration > max_duration_low_seconds.
        - LOW: default baseline.
        """
        rules = config.severity_rules
        obs_count = sum(len(e.observations) for e in timeline.events)

        # Check critical components
        actual_components_lower = {c.lower().strip() for c in timeline.affected_components}
        critical_components_lower = {c.lower().strip() for c in rules.critical_components}
        critical_intersect = actual_components_lower.intersection(critical_components_lower)

        # Determine severity level
        if obs_count >= rules.critical_severity_trigger_count or critical_intersect:
            return "CRITICAL"
        elif timeline.duration > rules.max_duration_medium_seconds:
            return "HIGH"
        elif timeline.duration > rules.max_duration_low_seconds:
            return "MEDIUM"
        else:
            return "LOW"
