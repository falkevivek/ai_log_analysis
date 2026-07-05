"""
Observation Rule Base
======================
Defines the abstract contract that every observation detection rule must implement.

Extension Guide
---------------
To add a new observation category:
  1. Create a new module in app/engines/observation/rules/
  2. Subclass ObservationRule and implement all abstract members
  3. Add an instance of the new class to get_default_rules() in rules/__init__.py

No changes to the engine, classifier, or any other file are required.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from app.schemas.domain import NormalizedLog

# ---------------------------------------------------------------------------
# Severity utilities shared by all rules
# ---------------------------------------------------------------------------

_SEVERITY_RANK: dict[str, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

# Maps a canonical log level to the minimum severity an observation should carry.
_LEVEL_TO_SEVERITY: dict[str, str] = {
    "DEBUG": "LOW",
    "INFO": "LOW",
    "WARNING": "MEDIUM",
    "ERROR": "HIGH",
    "CRITICAL": "CRITICAL",
    "UNKNOWN": "MEDIUM",
}


class ObservationRule(ABC):
    """
    Abstract base class for every observation detection rule.

    Each concrete rule corresponds to exactly one observation type and is
    fully responsible for three things:
      1. Stating its canonical observation_type string.
      2. Computing a confidence score [0.0, 1.0] for a given NormalizedLog.
      3. Generating a human-readable description of the observation.

    The effective_severity() method is provided as a concrete helper that
    escalates severity when the log level implies a higher level than the
    rule's own base_severity. Subclasses may override it if needed.

    Rules must never raise exceptions — all failure cases must return safe
    default values (0.0 confidence, fallback description string).
    """

    @property
    @abstractmethod
    def observation_type(self) -> str:
        """Canonical observation type string (e.g., 'AUTHENTICATION_FAILURE')."""
        ...

    @property
    @abstractmethod
    def base_severity(self) -> str:
        """Default severity when this rule fires: LOW | MEDIUM | HIGH | CRITICAL."""
        ...

    @abstractmethod
    def match_confidence(self, log: NormalizedLog) -> float:
        """
        Evaluate the log and return a confidence score in [0.0, 1.0].

        Return 0.0  → this rule does not apply to the log.
        Return >0.0 → degree of certainty that this rule applies.

        This method must never raise. Catch all internal errors and return 0.0.
        """
        ...

    @abstractmethod
    def describe(self, log: NormalizedLog) -> str:
        """
        Return a human-readable description of the detected observation.

        This method must never raise. Return a safe fallback string on error.
        """
        ...

    def effective_severity(self, log: NormalizedLog) -> str:
        """
        Return the effective severity for this observation.

        Takes the higher of the rule's base_severity and the severity implied
        by the log's log_level, so a CRITICAL-level log always escalates the
        observation to at least CRITICAL severity.
        """
        level_severity = _LEVEL_TO_SEVERITY.get(log.log_level, "MEDIUM")
        rule_rank = _SEVERITY_RANK.get(self.base_severity, 2)
        level_rank = _SEVERITY_RANK.get(level_severity, 2)
        return level_severity if level_rank > rule_rank else self.base_severity

    def _compute_confidence(self, message: str, keywords: tuple[tuple[str, float], ...]) -> float:
        """
        Computes the matching confidence for a log message against a list of weighted keywords.
        Ensures whole-word/boundary matching to prevent false positives on substring matches.
        """
        try:
            msg = message.lower()
            score = 0.0
            for kw, weight in keywords:
                pattern = re.escape(kw)
                if kw and kw[0].isalnum():
                    pattern = r'\b' + pattern
                if kw and kw[-1].isalnum():
                    pattern = pattern + r'\b'
                
                if re.search(pattern, msg):
                    score += weight
            return min(1.0, score)
        except Exception:
            return 0.0

