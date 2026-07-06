"""
Evidence Builder Engine
=======================
Stage 8 of the AI Analysis pipeline.

Consolidates all technical evidence and onboarding context parameters into a
single structured Evidence contract. Gathers extra facts (metrics, security logs,
deployment state) using replaceable BaseEvidenceProviders.

Responsibilities
----------------
1. Receive Incident and Context objects.
2. Verify structural validity of input arguments.
3. Compute structured summaries for incidents, timelines, events, and observations.
4. Coordinate execution across registered pluggable BaseEvidenceProviders.
5. Swallows provider exceptions internally for pipeline resilience.
6. Calculate overall collection confidence based on source accuracy metrics.
7. Construct and return a validated Evidence package ready for LLM consumption.

This engine does NOT
--------------------
- Connect to or prompt LLM APIs.
- Diagnose incidents or suggest fixes.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.engines.evidence_builder.providers import get_default_evidence_providers, BaseEvidenceProvider
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Incident, Context, Evidence, Observation

logger = logging.getLogger("ai_analysis_engine.engines.evidence_builder.engine")


class EvidenceBuilder:
    """Orchestrates evidence providers and builds the unified Evidence Package."""

    def __init__(self, providers: Optional[list[BaseEvidenceProvider]] = None) -> None:
        """
        Initialize the Evidence Builder.

        Parameters
        ----------
        providers:
            Optional list of pluggable BaseEvidenceProvider objects.
            If None, defaults to the registered metrics and deployment providers.
        """
        self.providers = providers if providers is not None else get_default_evidence_providers()
        logger.info(
            "EvidenceBuilder initialized with %d collection providers",
            len(self.providers)
        )

    def build_evidence(self, incident: Incident, context: Context) -> Evidence:
        """
        Consolidate Incident and Context into a structured Evidence Package.

        Parameters
        ----------
        incident:
            The formal Incident domain object.
        context:
            The enriched Context domain object.

        Returns
        -------
        Evidence
            The validated structured Evidence Package.

        Raises
        ------
        ValidationError
            If the incoming arguments are missing or invalid, or if Pydantic
            validation fails.
        """
        if not incident:
            raise ValidationError(
                message="Cannot build evidence from a null or missing Incident.",
                detail={"engine": "EvidenceBuilder"}
            )
        if not context:
            raise ValidationError(
                message="Cannot build evidence from a null or missing Context.",
                detail={"engine": "EvidenceBuilder"}
            )

        logger.debug("Assembling Evidence Package for incident: %s", incident.incident_id)

        # Step 1: Consolidate timestamps and basic metrics from Incident/Context
        environment = context.environment or incident.incident_metadata.environment or "production"
        affected_services = sorted(list(set(incident.affected_services).union(set(context.services))))
        affected_components = sorted(list(set(incident.affected_components).union(set(context.components))))
        known_errors = sorted(list(set(context.known_errors)))
        historical_references = sorted(list(set(context.historical_references)))
        api_metadata = dict(context.api_metadata)
        config_metadata = dict(context.config_metadata)

        # Step 2: Extract observations and compute structured summaries
        timeline = incident.timeline
        observations: list[Observation] = []
        obs_summary_lines: list[str] = []
        evt_summary_lines: list[str] = []

        # Parse timeline events chronologically
        for idx, evt in enumerate(timeline.events):
            evt_line = (
                f"- Event [{evt.event_id}]: '{evt.event_name}' (Type: {evt.event_type}, Severity: {evt.severity}) "
                f"spanned from {evt.start_time.isoformat()} to {evt.end_time.isoformat()} "
                f"impacting components: {', '.join(evt.affected_components)}."
            )
            evt_summary_lines.append(evt_line)

            for obs in evt.observations:
                observations.append(obs)
                obs_line = (
                    f"- Observation [{obs.observation_id}]: Type: {obs.type}, Severity: {obs.severity}, "
                    f"Confidence: {obs.confidence:.2f} in component '{obs.component}'. "
                    f"Description: {obs.description}"
                )
                obs_summary_lines.append(obs_line)

        # Remove duplicate observations if any
        unique_obs_map: dict[str, Observation] = {}
        for o in observations:
            unique_obs_map[o.observation_id] = o
        deduped_observations = list(unique_obs_map.values())

        # Build natural-language text summaries
        incident_summary = incident.summary
        timeline_summary = timeline.timeline_summary
        event_summary = "\n".join(evt_summary_lines) if evt_summary_lines else "No events captured."
        observation_summary = "\n".join(obs_summary_lines) if obs_summary_lines else "No observations captured."

        # Step 3: Run pluggable evidence providers sequentially
        supporting_metrics: dict[str, Any] = {}
        deployment_info: dict[str, Any] = {}
        additional_metadata: dict[str, Any] = {}

        for provider in self.providers:
            try:
                data = provider.collect(incident, context)
                if not data:
                    continue

                for key, val in data.items():
                    if key == "supporting_metrics" and isinstance(val, dict):
                        supporting_metrics.update(val)
                    elif key == "deployment_info" and isinstance(val, dict):
                        deployment_info.update(val)
                    elif key == "additional_metadata" and isinstance(val, dict):
                        additional_metadata.update(val)
                    else:
                        # Swallow other fields into additional_metadata to keep extensible
                        additional_metadata[key] = val

            except Exception as exc:
                logger.warning(
                    "Evidence provider %s failed during collection: %s. Continuing.",
                    provider.provider_name,
                    str(exc)
                )

        # Merge remaining additional metadata from context if not already present
        for key, val in context.metadata.items():
            if key not in additional_metadata:
                additional_metadata[key] = val

        # Step 4: Compute overall collection confidence score
        # Rules: Average of all observation confidences, fallback to 1.0 if empty
        if deduped_observations:
            avg_obs_conf = sum(o.confidence for o in deduped_observations) / len(deduped_observations)
            evidence_confidence = float(min(1.0, max(0.0, avg_obs_conf)))
        else:
            evidence_confidence = 1.0

        # Compile error codes from observations and context
        error_codes = sorted(list(set(known_errors)))

        try:
            evidence = Evidence(
                incident_summary=incident_summary,
                timeline_summary=timeline_summary,
                event_summary=event_summary,
                observation_summary=observation_summary,
                affected_services=affected_services,
                affected_components=affected_components,
                error_codes=error_codes,
                api_metadata=api_metadata,
                config_metadata=config_metadata,
                environment=environment,
                known_errors=known_errors,
                historical_references=historical_references,
                deployment_info=deployment_info,
                supporting_metrics=supporting_metrics,
                evidence_confidence=evidence_confidence,
                additional_metadata=additional_metadata,
                timeline=timeline,
                observations=deduped_observations
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Evidence domain contract: {str(exc)}",
                detail={"incident_id": incident.incident_id}
            ) from exc

        logger.info(
            "Evidence Package successfully constructed | incident_id=%s | confidence=%.2f",
            incident.incident_id,
            evidence.evidence_confidence
        )
        return evidence
