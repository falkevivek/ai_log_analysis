"""
Base Recommendation Strategy Interface
=======================================
Defines the abstract interface that every recommendation strategy must implement.

Strategies convert a Diagnosis and an Evidence Package into actionable recommendations
(e.g., using rule matching, LLM reasoning, or historical lookup).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.domain import Diagnosis, Evidence


class BaseRecommendationStrategy(ABC):
    """Abstract base class representing a pluggable recommendation generation algorithm."""

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """The unique identifier of the strategy (e.g., 'RULE_BASED_STRATEGY')."""
        ...

    @abstractmethod
    def recommend(self, diagnosis: Diagnosis, evidence: Evidence) -> dict[str, Any]:
        """
        Generate recommendations for the given diagnosis and evidence facts.

        Returns
        -------
        dict[str, Any]
            Dictionary of recommendation attributes (immediate_action, investigation_steps, etc.)
        """
        ...
