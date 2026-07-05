"""
Event Intelligence Engine
===========================
Stage 4 of the AI Analysis pipeline.

Receives multiple Observation objects, groups them into logical clusters
representing execution flows (using the CorrelationEngine), and classifies
each cluster into a unified Event contract using configurable event rules.

Responsibilities
----------------
1. Receive independent Observations.
2. Group them using the CorrelationEngine.
3. For each group, determine start_time, end_time, severity, affected_services,
   and affected_components.
4. Classify the grouped observations using registered EventRules.
5. Package the cluster into a validated Event object.

This engine does NOT
--------------------
- Perform root cause analysis.
- Connect events into timelines (Stage 5 responsibilities).
- Interact with LLMs or build incidents.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.engines.correlation import CorrelationEngine, CorrelationConfig
from app.engines.event_intelligence.rules import get_default_event_rules, EventRule
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Observation, Event, NormalizedLog

logger = logging.getLogger("ai_analysis_engine.engines.event_intelligence.engine")

_SEVERITY_ORDER: dict[str, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

_REVERSE_SEVERITY: dict[int, str] = {
    1: "LOW",
    2: "MEDIUM",
    3: "HIGH",
    4: "CRITICAL",
}


class EventIntelligenceEngine:
    """Groups related observations and classifies them into logical Event objects."""

    def __init__(
        self,
        rules: Optional[list[EventRule]] = None,
        correlation_config: Optional[CorrelationConfig] = None
    ) -> None:
        """
        Initialize the Event Intelligence Engine.

        Parameters
        ----------
        rules:
            Optional list of custom EventRule objects for event classification.
            If None, defaults to registered rules.
        correlation_config:
            Optional CorrelationConfig to customize correlation behavior.
        """
        self.rules = rules if rules is not None else get_default_event_rules()
        self.correlation_engine = CorrelationEngine(correlation_config)
        logger.info(
            "EventIntelligenceEngine initialized with %d classification rules",
            len(self.rules)
        )

    def process_observations(self, observations: list[Observation]) -> list[Event]:
        """
        Correlate and group observations into logical Events.

        Parameters
        ----------
        observations:
            A list of Observation objects.

        Returns
        -------
        list[Event]
            A list of constructed Event objects.
        """
        if not observations:
            logger.info("Empty observations list — returning empty list.")
            return []

        # Remove duplicates
        unique_obs_map: dict[str, Observation] = {}
        for obs in observations:
            if not obs or not obs.observation_id:
                continue
            unique_obs_map[obs.observation_id] = obs

        unique_obs = list(unique_obs_map.values())
        if not unique_obs:
            return []

        # Step 1: Correlate independent observations into execution flows (CorrelationGroups)
        correlation_groups = self.correlation_engine.correlate(unique_obs)

        events: list[Event] = []

        # Step 2: Transform each CorrelationGroup into a structured Event
        for group in correlation_groups:
            obs_list = group.related_observations
            if not obs_list:
                continue

            # Determine Event timing boundaries
            all_timestamps = []
            for obs in obs_list:
                for log in obs.related_logs:
                    all_timestamps.append(log.timestamp)

            if all_timestamps:
                start_time = min(all_timestamps)
                end_time = max(all_timestamps)
            else:
                start_time = group.start_time
                end_time = group.end_time

            # Determine Event Severity (highest severity rank)
            highest_rank = 1
            for obs in obs_list:
                rank = _SEVERITY_ORDER.get(obs.severity.upper(), 1)
                if rank > highest_rank:
                    highest_rank = rank
            severity = _REVERSE_SEVERITY.get(highest_rank, "LOW")

            # Gather affected services and components
            services = set()
            components = set()
            for obs in obs_list:
                components.add(obs.component)
                for log in obs.related_logs:
                    services.add(log.service)

            # Classify using registered rules
            best_rule = None
            best_score = 0.0
            for rule in self.rules:
                try:
                    score = rule.match(obs_list)
                    if score > best_score:
                        best_score = score
                        best_rule = rule
                except Exception as exc:
                    logger.error(
                        "Error running event rule %s: %s",
                        rule.event_type,
                        str(exc)
                    )

            if best_rule is not None and best_score >= 0.5:
                event_name = best_rule.event_name
                event_type = best_rule.event_type
            else:
                # Fallback event classification
                event_name = "General System Degradation"
                event_type = "SYSTEM_DEGRADATION"

            try:
                event = Event(
                    event_id=str(uuid.uuid4()),
                    event_name=event_name,
                    event_type=event_type,
                    severity=severity,
                    observations=obs_list,
                    start_time=start_time,
                    end_time=end_time,
                    affected_services=list(services),
                    affected_components=list(components)
                )
                events.append(event)
            except Exception as exc:
                logger.error("Failed to build Event contract: %s", str(exc))
                # Propagate validation errors in strict mode
                raise ValidationError(
                    message=f"Failed to build Event contract: {str(exc)}",
                    detail={"correlation_id": group.correlation_id}
                ) from exc

        logger.info(
            "Event grouping complete | events_out=%d",
            len(events)
        )
        return events
