# Event classification rules package
# This acts as the single catalog for all active event classifiers.

from __future__ import annotations

from app.engines.event_intelligence.rules.base import EventRule
from app.engines.event_intelligence.rules.login_failure import UserLoginFailureRule
from app.engines.event_intelligence.rules.ui_failure import UiRenderingFailureRule


def get_default_event_rules() -> list[EventRule]:
    """Return the list of active event classification rules."""
    return [
        UserLoginFailureRule(),
        UiRenderingFailureRule(),
    ]


__all__ = [
    "EventRule",
    "get_default_event_rules",
    "UserLoginFailureRule",
    "UiRenderingFailureRule",
]
