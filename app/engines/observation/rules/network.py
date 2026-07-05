"""
Network Failure Rule
=====================
Detects network-layer failure patterns in normalized logs.

Observation Type : NETWORK_FAILURE
Base Severity    : HIGH
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class NetworkFailureRule(ObservationRule):
    """
    Fires when a log contains signals of network connectivity or transport failures.

    Covers: DNS failures, socket errors, SSL/TLS certificate issues,
    host unreachable events, connection resets, and general network failures.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("network failure", 0.80),
        ("network error", 0.70),
        ("network unreachable", 0.80),
        ("host unreachable", 0.80),
        ("dns resolution failed", 0.85),
        ("dns failure", 0.80),
        ("dns error", 0.75),
        ("socket error", 0.65),
        ("socket timeout", 0.65),
        ("ssl error", 0.65),
        ("ssl handshake failed", 0.80),
        ("tls error", 0.65),
        ("tls handshake", 0.65),
        ("certificate error", 0.65),
        ("certificate expired", 0.70),
        ("connection reset by peer", 0.70),
        ("connection refused", 0.50),
        ("connection reset", 0.45),
        ("no route to host", 0.75),
        ("connection timeout", 0.40),
        ("network", 0.10),
        ("certificate", 0.15),
    )

    @property
    def observation_type(self) -> str:
        return "NETWORK_FAILURE"

    @property
    def base_severity(self) -> str:
        return "HIGH"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Network failure detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Network failure detected."
