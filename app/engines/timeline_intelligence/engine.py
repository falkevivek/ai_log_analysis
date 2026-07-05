"""
Timeline Intelligence Engine
============================
Stage 5 of the AI Analysis pipeline.

Reconstructs the chronological execution journey of an application incident
from a set of independent Event objects. It aligns components against expected
execution flow templates, calculates overall duration, and identifies gaps (missing steps).

Responsibilities
----------------
1. Sort incoming Event objects chronologically.
2. Accumulate affected components and services.
3. Match the actual component sequence against configurable ExecutionFlowTemplates.
4. Detect missing execution steps/gaps.
5. Compute duration and produce a structured Timeline summary.

This engine does NOT
--------------------
- Perform root cause analysis.
- Connect timelines to external incidents (Stage 6 Incident Builder responsibilities).
- Interact with LLMs or generate fixes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Event, Timeline

logger = logging.getLogger("ai_analysis_engine.engines.timeline_intelligence.engine")


class ExecutionFlowTemplate(BaseModel):
    """Defines an expected sequence of component interactions for a system flow."""

    name: str = Field(..., description="Descriptive name of this execution path")
    expected_sequence: list[str] = Field(
        ...,
        description="Ordered list of component names representing the expected flow path"
    )


class TimelineConfig(BaseModel):
    """Configuration options for Timeline reconstruction rules."""

    # Set of expected service/execution flow templates
    templates: list[ExecutionFlowTemplate] = Field(
        default_factory=lambda: [
            ExecutionFlowTemplate(
                name="Standard Web Transaction Flow",
                expected_sequence=["web-ui", "api-gateway", "auth-service", "database"]
            ),
            ExecutionFlowTemplate(
                name="Frontend Page Rendering Flow",
                expected_sequence=["web-ui", "render-module", "api-gateway"]
            )
        ],
        description="Registered execution paths used to detect skipped or missing actions"
    )


def calculate_lcs_length(seq_a: list[str], seq_b: list[str]) -> int:
    """Calculate the length of the Longest Common Subsequence between two lists."""
    m, n = len(seq_a), len(seq_b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq_a[i - 1].strip().lower() == seq_b[j - 1].strip().lower():
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


class TimelineIntelligenceEngine:
    """Reconstructs the execution timeline from sorted Events."""

    def __init__(self, config: Optional[TimelineConfig] = None) -> None:
        self.config = config or TimelineConfig()
        logger.info(
            "TimelineIntelligenceEngine initialized with %d execution templates",
            len(self.config.templates)
        )

    def process_events(self, events: list[Event]) -> Timeline:
        """
        Build a chronologically ordered Timeline from a list of Events.

        Parameters
        ----------
        events:
            A list of Event domain objects.

        Returns
        -------
        Timeline
            A reconstructed Timeline.

        Raises
        ------
        ValidationError
            If the incoming events list is empty or if validation fails.
        """
        if not events:
            raise ValidationError(
                message="Cannot build a Timeline from an empty events list.",
                detail={"engine": "TimelineIntelligenceEngine"}
            )

        # Step 1: Remove duplicate events based on event_id
        unique_events_map: dict[str, Event] = {}
        for evt in events:
            if not evt or not evt.event_id:
                continue
            unique_events_map[evt.event_id] = evt

        sorted_events = sorted(
            unique_events_map.values(),
            key=lambda e: e.start_time
        )

        if not sorted_events:
            raise ValidationError(
                message="No valid unique events found to construct a Timeline.",
                detail={"engine": "TimelineIntelligenceEngine"}
            )

        # Step 2: Establish timeline time bounds
        start_time = sorted_events[0].start_time
        end_time = max(e.end_time for e in sorted_events)
        duration = float((end_time - start_time).total_seconds())

        # Step 3: Accumulate unique affected services and components
        services = set()
        components = set()
        actual_flow: list[str] = []

        for e in sorted_events:
            for s in e.affected_services:
                services.add(s)
            for c in e.affected_components:
                components.add(c)
                # Keep tracking of chronological components flow order
                if not actual_flow or actual_flow[-1] != c:
                    actual_flow.append(c)

        # Step 4: Template Matching & Missing Step Detection
        best_template = None
        best_match_count = 0

        for temp in self.config.templates:
            match_len = calculate_lcs_length(actual_flow, temp.expected_sequence)
            if match_len > best_match_count:
                best_match_count = match_len
                best_template = temp

        missing_steps: list[str] = []
        flow_name = "Custom System Execution Flow"

        if best_template:
            flow_name = best_template.name
            # Identify missing steps: expected components not present in actual flow
            expected_set = {c.strip().lower() for c in best_template.expected_sequence}
            actual_set = {c.strip().lower() for c in actual_flow}
            missing_steps = [c for c in best_template.expected_sequence if c.strip().lower() not in actual_set]

        # Step 5: Construct Timeline Summary
        summary = (
            f"Execution timeline reconstructed for '{flow_name}'. "
            f"Total duration: {duration:.2f}s, Gaps identified: "
            f"{len(missing_steps)} missing steps."
        )

        try:
            timeline = Timeline(
                timeline_id=str(uuid.uuid4()),
                events=sorted_events,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                affected_services=list(services),
                affected_components=list(components),
                execution_flow=actual_flow,
                missing_steps=missing_steps,
                timeline_summary=summary
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Timeline domain contract: {str(exc)}",
                detail={"timeline_start": start_time.isoformat()}
            ) from exc

        logger.info(
            "Timeline built | duration=%.2fs | events=%d | missing_steps=%d",
            duration,
            len(sorted_events),
            len(missing_steps)
        )
        return timeline
