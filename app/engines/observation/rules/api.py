"""
API Failure Rule
=================
Detects API-level failure patterns in normalized logs.

Observation Type : API_FAILURE
Base Severity    : MEDIUM
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class ApiFailureRule(ObservationRule):
    """
    Fires when a log contains signals of an API endpoint or HTTP service failure.

    Covers: 5xx HTTP errors, bad gateway, API call failures, request timeouts,
    and general API-level error patterns.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("internal server error", 0.75),
        ("500 internal server", 0.80),
        ("502 bad gateway", 0.80),
        ("504 gateway timeout", 0.80),
        ("api call failed", 0.75),
        ("api request failed", 0.75),
        ("api error", 0.65),
        ("api failure", 0.70),
        ("endpoint not responding", 0.70),
        ("endpoint error", 0.60),
        ("endpoint failed", 0.65),
        ("request failed", 0.45),
        ("request timeout", 0.45),
        ("bad gateway", 0.55),
        ("gateway timeout", 0.55),
        ("upstream error", 0.55),
        ("http error", 0.40),
        ("response error", 0.35),
        ("500", 0.20),
        ("502", 0.20),
        ("504", 0.20),
        ("api", 0.10),
    )

    @property
    def observation_type(self) -> str:
        return "API_FAILURE"

    @property
    def base_severity(self) -> str:
        return "MEDIUM"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"API failure detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "API failure detected."
