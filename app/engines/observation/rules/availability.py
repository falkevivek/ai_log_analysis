"""
Availability Rules
==================
Detects service unavailability and missing/empty response patterns.

Observation Types:
  SERVICE_UNAVAILABLE  — base severity HIGH
  MISSING_RESPONSE     — base severity MEDIUM
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class ServiceUnavailableRule(ObservationRule):
    """
    Fires when a log contains signals that a service is down or unavailable.

    Covers: service shutdowns, circuit breaker open events, health check failures,
    HTTP 503 errors, and general service-down patterns.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("service unavailable", 0.90),
        ("service not available", 0.90),
        ("service is down", 0.90),
        ("service down", 0.85),
        ("service stopped", 0.75),
        ("circuit breaker open", 0.85),
        ("circuit breaker tripped", 0.85),
        ("circuit breaker", 0.60),
        ("health check failed", 0.75),
        ("readiness check failed", 0.75),
        ("liveness check failed", 0.75),
        ("dependency unavailable", 0.80),
        ("503 service unavailable", 0.85),
        ("503", 0.30),
        ("not available", 0.35),
        ("unavailable", 0.40),
        ("shutdown", 0.30),
    )

    @property
    def observation_type(self) -> str:
        return "SERVICE_UNAVAILABLE"

    @property
    def base_severity(self) -> str:
        return "HIGH"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)

    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Service unavailability detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Service unavailability detected."


class MissingResponseRule(ObservationRule):
    """
    Fires when a log contains signals of a missing, empty, or null response.

    Covers: 404 not found, empty response bodies, null response objects,
    and missing resource patterns.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("no response received", 0.85),
        ("response missing", 0.80),
        ("empty response body", 0.80),
        ("null response", 0.75),
        ("empty response", 0.70),
        ("no response", 0.65),
        ("404 not found", 0.70),
        ("resource not found", 0.65),
        ("not found", 0.35),
        ("missing response", 0.75),
        ("response is null", 0.75),
        ("response is empty", 0.75),
        ("404", 0.25),
        ("missing", 0.15),
    )

    @property
    def observation_type(self) -> str:
        return "MISSING_RESPONSE"

    @property
    def base_severity(self) -> str:
        return "MEDIUM"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Missing or empty response detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Missing or empty response detected."
