"""
Performance Rule
================
Detects slow response and performance degradation patterns.

Observation Type : SLOW_RESPONSE
Base Severity    : LOW
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class SlowResponseRule(ObservationRule):
    """
    Fires when a log contains signals of performance degradation or slow responses.

    Covers: high latency events, response time threshold breaches,
    performance degradation warnings, and slow query/request patterns.

    Note: This rule intentionally has LOW base_severity because slow responses
    are warnings rather than hard failures. The effective_severity() in the base
    class will escalate to HIGH if the log_level is ERROR.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("performance degraded", 0.80),
        ("performance degradation", 0.80),
        ("latency spike", 0.80),
        ("high latency", 0.75),
        ("slow response", 0.80),
        ("slow request", 0.75),
        ("slow query", 0.75),
        ("response time exceeded", 0.80),
        ("exceeded threshold", 0.60),
        ("exceeded sla", 0.75),
        ("exceeded timeout", 0.60),
        ("took too long", 0.60),
        ("taking too long", 0.60),
        ("response time", 0.40),
        ("request duration", 0.40),
        ("processing time", 0.35),
        ("degraded performance", 0.75),
        ("under load", 0.40),
        ("overloaded", 0.45),
        ("cpu high", 0.40),
        ("memory pressure", 0.40),
        ("latency", 0.25),
        ("slow", 0.15),
        ("degraded", 0.20),
    )

    @property
    def observation_type(self) -> str:
        return "SLOW_RESPONSE"

    @property
    def base_severity(self) -> str:
        return "LOW"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Performance degradation or slow response detected in component "
                f"'{log.component}' (service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Slow response or performance degradation detected."
