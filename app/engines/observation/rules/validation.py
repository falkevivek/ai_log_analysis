"""
Validation Error Rule
======================
Detects data validation and schema constraint failure patterns.

Observation Type : VALIDATION_ERROR
Base Severity    : LOW
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class ValidationErrorRule(ObservationRule):
    """
    Fires when a log contains signals of input validation or schema constraint failures.

    Covers: Pydantic/schema validation errors, required field violations,
    constraint violations, format mismatches, and type errors.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("validation failed", 0.80),
        ("validation error", 0.80),
        ("schema validation failed", 0.85),
        ("schema validation error", 0.85),
        ("constraint violation", 0.75),
        ("missing required field", 0.75),
        ("required field missing", 0.75),
        ("invalid field value", 0.70),
        ("invalid value", 0.55),
        ("invalid field", 0.55),
        ("invalid format", 0.60),
        ("format mismatch", 0.60),
        ("format error", 0.50),
        ("field required", 0.55),
        ("value error", 0.50),
        ("type mismatch", 0.55),
        ("does not match", 0.35),
        ("validation", 0.15),
        ("invalid", 0.10),
    )

    @property
    def observation_type(self) -> str:
        return "VALIDATION_ERROR"

    @property
    def base_severity(self) -> str:
        return "LOW"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Validation error detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Validation error detected."
