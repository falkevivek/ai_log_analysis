"""
Authentication Failure Rule
============================
Detects authentication and authorization failure patterns in normalized logs.

Observation Type : AUTHENTICATION_FAILURE
Base Severity    : HIGH
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class AuthenticationFailureRule(ObservationRule):
    """
    Fires when a log contains signals of authentication or authorization failure.

    Covers: failed logins, invalid credentials, token expiry, access denial,
    account lockout, and HTTP 401/403 status patterns.
    """

    # (phrase_to_match_in_lowercase_message, weight)
    # Weights are additive — total is capped at 1.0.
    # Multi-word phrases carry higher weight than single generic keywords.
    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("authentication failed", 0.70),
        ("login failed", 0.65),
        ("invalid credentials", 0.65),
        ("bad credentials", 0.65),
        ("invalid password", 0.65),
        ("account locked", 0.60),
        ("account disabled", 0.60),
        ("auth failure", 0.60),
        ("access denied", 0.55),
        ("permission denied", 0.55),
        ("unauthorized access", 0.60),
        ("unauthorized", 0.45),
        ("invalid token", 0.55),
        ("token expired", 0.50),
        ("token invalid", 0.55),
        ("session expired", 0.45),
        ("session invalid", 0.45),
        ("forbidden", 0.40),
        ("401", 0.25),
        ("403", 0.25),
        ("authentication", 0.15),
        ("login", 0.10),
    )

    @property
    def observation_type(self) -> str:
        return "AUTHENTICATION_FAILURE"

    @property
    def base_severity(self) -> str:
        return "HIGH"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Authentication failure detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Authentication failure detected."
