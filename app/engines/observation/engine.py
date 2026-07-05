"""
Observation Engine
==================
Stage 2 of the AI Analysis pipeline.

Transforms a NormalizedLog domain object into a structured Observation
domain object by matching it against active observation rules.

Responsibilities
----------------
1. Evaluate incoming NormalizedLog objects against a suite of modular detection rules.
2. Determine the matching rule with the highest confidence.
3. Fall back to UnknownFailureRule if no specific rule matches with sufficient confidence.
4. Construct and return a validated Observation domain object.
5. Handle batch processing of normalized logs.

This engine does NOT
--------------------
- Perform root cause analysis.
- Correlate logs across different sources.
- Group events or build timelines.
- Call LLM APIs or external services.

Interface contract
------------------
Input  → NormalizedLog (from app.schemas.domain)
Output → Observation   (from app.schemas.domain)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from app.engines.observation.rules import get_default_rules, get_fallback_rule
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import NormalizedLog, Observation

logger = logging.getLogger("ai_analysis_engine.engines.observation.engine")


class ObservationEngine:
    """
    Classifies NormalizedLog objects into Observation domain objects.

    This engine evaluates logs against registered ObservationRules.
    The rule with the highest confidence score is selected to produce
    the resulting Observation.
    """

    def __init__(self, confidence_threshold: float = 0.1) -> None:
        """
        Initialize the Observation Engine.

        Parameters
        ----------
        confidence_threshold:
            The minimum confidence score required to accept a specific rule's
            classification. If no rule meets this threshold, the engine
            falls back to the UnknownFailureRule.
        """
        self.rules = get_default_rules()
        self.fallback_rule = get_fallback_rule()
        self.confidence_threshold = confidence_threshold
        logger.info(
            "ObservationEngine initialized with %d rules (threshold: %.2f)",
            len(self.rules),
            self.confidence_threshold,
        )

    def process(self, log: NormalizedLog) -> Observation:
        """
        Analyze a single NormalizedLog and produce an Observation.

        Parameters
        ----------
        log:
            The NormalizedLog object to classify.

        Returns
        -------
        Observation
            The classified Observation.

        Raises
        ------
        ValidationError
            If the incoming log is invalid or if Pydantic validation fails
            for the constructed Observation.
        """
        if not log:
            raise ValidationError(
                message="Log input is None or invalid.",
                detail={"engine": "ObservationEngine"},
            )

        logger.debug("Classifying log | log_id=%s | service=%s", log.log_id, log.service)

        best_rule = None
        best_confidence = -1.0

        # Evaluate all specific rules to find the highest confidence match
        for rule in self.rules:
            try:
                conf = rule.match_confidence(log)
                if conf > best_confidence:
                    best_confidence = conf
                    best_rule = rule
            except Exception as exc:
                logger.error(
                    "Error running rule %s on log %s: %s",
                    rule.observation_type,
                    log.log_id,
                    str(exc),
                )

        # Check if the best match meets the threshold, otherwise use fallback
        if best_rule is None or best_confidence < self.confidence_threshold:
            logger.debug(
                "No rule met confidence threshold (best: %s with %.2f) for log %s. Using fallback.",
                best_rule.observation_type if best_rule else "None",
                best_confidence,
                log.log_id,
            )
            selected_rule = self.fallback_rule
            # Compute confidence score for fallback rule
            confidence = selected_rule.match_confidence(log)
        else:
            selected_rule = best_rule
            confidence = best_confidence

        # Determine other properties according to the selected rule
        observation_type = selected_rule.observation_type
        severity = selected_rule.effective_severity(log)
        description = selected_rule.describe(log)

        # Build the final Observation object conforming to the Pydantic contract
        try:
            observation = Observation(
                observation_id=str(uuid.uuid4()),
                type=observation_type,
                severity=severity,
                confidence=float(confidence),
                component=log.component,
                description=description,
                related_logs=[log],
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to build Observation domain contract: {str(exc)}",
                detail={"log_id": log.log_id},
            ) from exc

        logger.debug(
            "Observation created | observation_id=%s | type=%s | severity=%s | confidence=%.2f",
            observation.observation_id,
            observation.type,
            observation.severity,
            observation.confidence,
        )

        return observation

    def process_batch(self, logs: list[NormalizedLog]) -> list[Observation]:
        """
        Analyze a batch of NormalizedLog objects and produce a list of Observations.

        Parameters
        ----------
        logs:
            The list of NormalizedLog objects to classify.

        Returns
        -------
        list[Observation]
            A list of successfully generated Observation objects.
        """
        if not logs:
            logger.info("Empty batch received — returning empty list.")
            return []

        logger.info("Starting batch log classification | count=%d", len(logs))

        observations: list[Observation] = []
        failed_count = 0

        for log in logs:
            try:
                observations.append(self.process(log))
            except ValidationError as exc:
                failed_count += 1
                logger.warning(
                    "Log classification skipped | log_id=%s | service=%s | reason=%s",
                    log.log_id if log else "unknown",
                    log.service if log else "unknown",
                    exc.message,
                )
            except Exception as exc:
                failed_count += 1
                logger.error(
                    "Unexpected error during log classification | log_id=%s | error=%s",
                    log.log_id if log else "unknown",
                    str(exc),
                )

        logger.info(
            "Batch log classification complete | total=%d | observations=%d | failed=%d",
            len(logs),
            len(observations),
            failed_count,
        )

        return observations
