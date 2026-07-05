"""
Fallback Rule
=============
Last-resort observation rule that fires when no specific rule reaches
the confidence threshold.

Observation Type : UNKNOWN_FAILURE
Base Severity    : (derived from log level only)

This rule always returns a confidence > 0 for any non-empty log so that
every log produces at least one observation. The confidence is calibrated
by the log level — ERROR/CRITICAL logs indicate a more certain failure
even when the pattern is unrecognized.
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog

# Confidence assigned by log level when no specific rule fires.
_LEVEL_FALLBACK_CONFIDENCE: dict[str, float] = {
    "CRITICAL": 0.55,
    "ERROR": 0.45,
    "WARNING": 0.30,
    "UNKNOWN": 0.30,
    "INFO": 0.20,
    "DEBUG": 0.10,
}


class UnknownFailureRule(ObservationRule):
    """
    Fires as a fallback for any log that no specific rule claims above threshold.

    The observation type is UNKNOWN_FAILURE and the confidence is determined
    solely by the log level. This ensures that every log entering the engine
    produces at least one structured observation.
    """

    @property
    def observation_type(self) -> str:
        return "UNKNOWN_FAILURE"

    @property
    def base_severity(self) -> str:
        # Severity is fully driven by the log level via effective_severity().
        # Return MEDIUM as a baseline so the escalation logic in base class
        # correctly promotes CRITICAL/ERROR logs.
        return "MEDIUM"

    def match_confidence(self, log: NormalizedLog) -> float:
        try:
            return _LEVEL_FALLBACK_CONFIDENCE.get(log.log_level, 0.25)
        except Exception:
            return 0.25

    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Unclassified failure detected in component '{log.component}' "
                f"(service: '{log.service}'). No specific pattern matched. "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Unclassified failure detected."
