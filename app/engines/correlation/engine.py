"""
Correlation Engine
==================
Stage 3 of the AI Analysis pipeline.

Responsible for identifying relationships between independent observations.
Groups observations into correlated execution flows using explicit trace metadata
or configurable heuristics (time window and service flow relations).

Responsibilities
----------------
1. Extract correlation identifiers (Trace ID, Session ID, etc.) from log metadata/parameters.
2. Group observations sharing the same explicit identifier (High Confidence).
3. Apply configurable heuristics (Time Window & Service Flow) for observations without IDs.
4. Calculate correlation confidence based on method used.
5. Ensure zero information loss — ungrouped observations form single-node groups.

This engine does NOT
--------------------
- Perform AI reasoning or LLM queries.
- Build incident timelines or diagnosis reports.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.domain import Observation, NormalizedLog
from app.schemas.correlation import CorrelationGroup
from app.exceptions.custom_exceptions import ValidationError

logger = logging.getLogger("ai_analysis_engine.engines.correlation.engine")


class CorrelationConfig(BaseModel):
    """Configuration schema for the Correlation Engine rules."""

    # Ordered list of metadata/parameter keys to search for explicit correlation
    identifier_keys: list[str] = Field(
        default_factory=lambda: ["trace_id", "correlation_id", "request_id", "session_id", "user_id"],
        description="Keys checked inside metadata or parameters for exact match grouping"
    )

    # Time window boundary (in seconds) for heuristic temporal grouping
    time_window_seconds: float = Field(
        default=60.0,
        description="Maximum temporal gap allowed between related observations"
    )

    # Directed component dependency graph representing service flows.
    # Key: component, Value: list of components it interacts with/depends on.
    component_flow: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list representing allowed service execution flows"
    )

    # Confidence scores for different matching strategies
    confidence_explicit_match: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence_service_flow: float = Field(default=0.8, ge=0.0, le=1.0)
    confidence_temporal_only: float = Field(default=0.6, ge=0.0, le=1.0)
    confidence_ungrouped: float = Field(default=0.3, ge=0.0, le=1.0)


# Helper utility functions for observation analysis
def get_observation_time_range(obs: Observation) -> tuple[datetime, datetime]:
    """Return the earliest and latest log timestamp in an observation."""
    if not obs.related_logs:
        now = datetime.now(timezone.utc)
        return now, now
    timestamps = [log.timestamp for log in obs.related_logs]
    return min(timestamps), max(timestamps)


def extract_identifiers_from_observation(obs: Observation, keys: list[str]) -> dict[str, set[str]]:
    """Scan all related logs to extract non-empty values for given identifier keys."""
    extracted: dict[str, set[str]] = {k: set() for k in keys}
    for log in obs.related_logs:
        # Check both metadata and parameters dicts
        for data_source in (log.metadata, log.parameters):
            if not data_source:
                continue
            for key in keys:
                val = data_source.get(key)
                if val is not None:
                    cleaned = str(val).strip()
                    if cleaned:
                        extracted[key].add(cleaned)
    return extracted


class CorrelationEngine:
    """Independent engine that groups observations based on identifiers and heuristics."""

    def __init__(self, config: Optional[CorrelationConfig] = None) -> None:
        self.config = config or CorrelationConfig()
        logger.info(
            "CorrelationEngine initialized with %d identifier keys (window: %.1fs)",
            len(self.config.identifier_keys),
            self.config.time_window_seconds
        )

    def correlate(self, observations: list[Observation]) -> list[CorrelationGroup]:
        """
        Group observations into correlated execution flows.

        Ensures that every observation is placed in at least one CorrelationGroup
        so that no data is lost during Stage 3 transformation.

        Parameters
        ----------
        observations:
            A list of Observation domain objects.

        Returns
        -------
        list[CorrelationGroup]
            A list of grouped observations with correlation metadata.
        """
        if not observations:
            logger.info("Empty observations list — returning empty list.")
            return []

        # Remove duplicate observations based on ID to avoid processing errors
        unique_obs_map: dict[str, Observation] = {}
        for obs in observations:
            if obs.observation_id not in unique_obs_map:
                unique_obs_map[obs.observation_id] = obs
            else:
                logger.debug("Duplicate observation discarded | id=%s", obs.observation_id)

        remaining_obs = list(unique_obs_map.values())
        groups: list[CorrelationGroup] = []

        # -------------------------------------------------------------------
        # Phase 1: Explicit Identifier Matching
        # -------------------------------------------------------------------
        # Map of identifier_key -> identifier_value -> list of observation_ids
        for key in self.config.identifier_keys:
            # We track observations matched in this iteration to avoid overlapping same-key matches
            val_to_obs: dict[str, list[Observation]] = {}
            for obs in remaining_obs:
                ids = extract_identifiers_from_observation(obs, [key])
                for val in ids[key]:
                    val_to_obs.setdefault(val, []).append(obs)

            # Produce groups for keys with >= 1 observations
            for val, grouped_list in val_to_obs.items():
                # Extract observations that are still in remaining_obs
                valid_group_obs = [o for o in grouped_list if o in remaining_obs]
                if not valid_group_obs:
                    continue

                # Gather start/end times
                all_times = []
                for o in valid_group_obs:
                    t_start, t_end = get_observation_time_range(o)
                    all_times.extend([t_start, t_end])

                group = CorrelationGroup(
                    correlation_id=f"EXPLICIT-{key.upper()}-{val}",
                    related_observations=valid_group_obs,
                    correlation_confidence=self.config.confidence_explicit_match,
                    correlation_method=f"EXPLICIT_MATCH_{key.upper()}",
                    start_time=min(all_times),
                    end_time=max(all_times)
                )
                groups.append(group)

                # Remove correlated observations from the pool of remaining
                for o in valid_group_obs:
                    remaining_obs.remove(o)

        # -------------------------------------------------------------------
        # Phase 2: Heuristic Service Flow Matching
        # -------------------------------------------------------------------
        # If component dependencies are defined, group remaining observations
        # that satisfy both temporal proximity and component flow.
        if remaining_obs and self.config.component_flow:
            flow_groups = self._correlate_heuristics(
                remaining_obs,
                use_service_flow=True
            )
            for group in flow_groups:
                groups.append(group)
                for o in group.related_observations:
                    remaining_obs.remove(o)

        # -------------------------------------------------------------------
        # Phase 3: Heuristic Temporal Proximity Matching
        # -------------------------------------------------------------------
        # Group any leftover observations based on timestamp proximity alone.
        if remaining_obs:
            temporal_groups = self._correlate_heuristics(
                remaining_obs,
                use_service_flow=False
            )
            for group in temporal_groups:
                groups.append(group)
                for o in group.related_observations:
                    remaining_obs.remove(o)

        # -------------------------------------------------------------------
        # Phase 4: Fallback for Ungrouped Observations
        # -------------------------------------------------------------------
        # Any remaining isolated observations are packaged as single groups
        for obs in remaining_obs:
            t_start, t_end = get_observation_time_range(obs)
            group = CorrelationGroup(
                correlation_id=f"HEURISTIC-UNGROUPED-{uuid.uuid4()}",
                related_observations=[obs],
                correlation_confidence=self.config.confidence_ungrouped,
                correlation_method="UNGROUPED_FALLBACK",
                start_time=t_start,
                end_time=t_end
            )
            groups.append(group)

        logger.info(
            "Correlation complete | observations_in=%d | groups_out=%d",
            len(observations),
            len(groups)
        )
        return groups

    def _correlate_heuristics(
        self,
        observations: list[Observation],
        use_service_flow: bool
    ) -> list[CorrelationGroup]:
        """
        Groups observations using a graph-based connected components algorithm.

        Two observations have a relationship if:
        1. They occur within time_window_seconds of each other.
        2. (Optional) Their components form a valid service flow connection.
        """
        # Build adjacency list representation of the graph
        n = len(observations)
        adj: dict[int, list[int]] = {i: [] for i in range(n)}

        # Helper to check if component flow connection exists
        def is_flow_valid(c1: str, c2: str) -> bool:
            c1_clean = c1.strip().lower()
            c2_clean = c2.strip().lower()
            if c1_clean == c2_clean:
                return True
            # Check directed flows c1 -> c2 or c2 -> c1
            flow_forward = self.config.component_flow.get(c1_clean, [])
            flow_backward = self.config.component_flow.get(c2_clean, [])
            return c2_clean in flow_forward or c1_clean in flow_backward

        for i in range(n):
            obs_i = observations[i]
            t_start_i, t_end_i = get_observation_time_range(obs_i)

            for j in range(i + 1, n):
                obs_j = observations[j]
                t_start_j, t_end_j = get_observation_time_range(obs_j)

                # Check temporal constraint: start time gap between observations
                time_gap = abs((t_start_i - t_start_j).total_seconds())
                if time_gap <= self.config.time_window_seconds:
                    if not use_service_flow or is_flow_valid(obs_i.component, obs_j.component):
                        adj[i].append(j)
                        adj[j].append(i)

        # Find connected components using Depth-First Search (DFS)
        visited = [False] * n
        components: list[list[int]] = []

        for i in range(n):
            if not visited[i]:
                component: list[int] = []
                stack = [i]
                while stack:
                    curr = stack.pop()
                    if not visited[curr]:
                        visited[curr] = True
                        component.append(curr)
                        for neighbor in adj[curr]:
                            if not visited[neighbor]:
                                stack.append(neighbor)
                components.append(component)

        # Build CorrelationGroup objects from components
        groups: list[CorrelationGroup] = []
        for comp in components:
            # We only generate groups for components containing >= 2 nodes.
            # Single isolated nodes will be resolved in the final fallback phase.
            if len(comp) < 2:
                continue

            grouped_obs = [observations[idx] for idx in comp]

            # Collect start and end times
            all_times = []
            for o in grouped_obs:
                t_start, t_end = get_observation_time_range(o)
                all_times.extend([t_start, t_end])

            method = "HEURISTIC_SERVICE_FLOW" if use_service_flow else "HEURISTIC_TEMPORAL_PROXIMITY"
            confidence = self.config.confidence_service_flow if use_service_flow else self.config.confidence_temporal_only

            group = CorrelationGroup(
                correlation_id=f"HEURISTIC-{method}-{uuid.uuid4()}",
                related_observations=grouped_obs,
                correlation_confidence=confidence,
                correlation_method=method,
                start_time=min(all_times),
                end_time=max(all_times)
            )
            groups.append(group)

        return groups
