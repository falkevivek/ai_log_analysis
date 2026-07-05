"""
UI Rendering Failure Event Rule
===============================
Matches correlated observations indicating frontend component errors or JavaScript
exceptions.
"""

from __future__ import annotations

from app.engines.event_intelligence.rules.base import EventRule
from app.schemas.domain import Observation


class UiRenderingFailureRule(EventRule):
    """
    Fires when React/Vue crashes occur alongside JavaScript exceptions.
    """

    @property
    def event_name(self) -> str:
        return "UI Rendering Failure"

    @property
    def event_type(self) -> str:
        return "UI_RENDERING_FAILURE"

    def match(self, observations: list[Observation]) -> float:
        if not observations:
            return 0.0

        types = {obs.type for obs in observations}

        has_ui = "UI_RENDERING_FAILURE" in types
        has_js = "JAVASCRIPT_EXCEPTION" in types

        if has_ui and has_js:
            return 1.0

        if has_ui or has_js:
            return 0.8

        return 0.0
