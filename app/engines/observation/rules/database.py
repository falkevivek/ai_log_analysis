"""
Database Rules
==============
Detects database connectivity, timeout, and query failure patterns.

Observation Type : DATABASE_TIMEOUT
Base Severity    : HIGH
"""

from __future__ import annotations

from app.engines.observation.rules.base import ObservationRule
from app.schemas.domain import NormalizedLog


class DatabaseTimeoutRule(ObservationRule):
    """
    Fires when a log contains signals of database connectivity or query failures.

    Covers: connection timeouts, query failures, deadlocks, pool exhaustion,
    transaction errors, and lost database connections.
    """

    _KEYWORDS: tuple[tuple[str, float], ...] = (
        ("connection pool exhausted", 0.85),
        ("database connection failed", 0.80),
        ("database connection timeout", 0.80),
        ("db connection failed", 0.80),
        ("query timeout", 0.75),
        ("query execution failed", 0.75),
        ("database unavailable", 0.80),
        ("too many connections", 0.70),
        ("deadlock detected", 0.80),
        ("deadlock", 0.65),
        ("transaction failed", 0.60),
        ("transaction rollback", 0.60),
        ("connection pool", 0.50),
        ("connection timeout", 0.45),
        ("connection refused", 0.45),
        ("connection reset", 0.40),
        ("lost connection", 0.55),
        ("query failed", 0.50),
        ("sql error", 0.50),
        ("database error", 0.50),
        ("database", 0.15),
        ("timeout", 0.15),
        ("sql", 0.10),
        ("db", 0.10),
    )

    @property
    def observation_type(self) -> str:
        return "DATABASE_TIMEOUT"

    @property
    def base_severity(self) -> str:
        return "HIGH"

    def match_confidence(self, log: NormalizedLog) -> float:
        return self._compute_confidence(log.message, self._KEYWORDS)


    def describe(self, log: NormalizedLog) -> str:
        try:
            return (
                f"Database failure detected in component '{log.component}' "
                f"(service: '{log.service}'). "
                f"Log: {log.message[:150]}"
            )
        except Exception:
            return "Database failure detected."
