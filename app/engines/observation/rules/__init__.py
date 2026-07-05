# Observation Rules package
#
# This file is the SINGLE registration point for all observation rules.
#
# To add a new observation category:
#   1. Create a new module in this directory (e.g., rules/new_type.py)
#   2. Subclass ObservationRule and implement the three abstract members
#   3. Import and append an instance to the list returned by get_default_rules()
#
# No other file needs modification.

from __future__ import annotations

from app.engines.observation.rules.api import ApiFailureRule
from app.engines.observation.rules.auth import AuthenticationFailureRule
from app.engines.observation.rules.availability import (
    MissingResponseRule,
    ServiceUnavailableRule,
)
from app.engines.observation.rules.base import ObservationRule
from app.engines.observation.rules.database import DatabaseTimeoutRule
from app.engines.observation.rules.fallback import UnknownFailureRule
from app.engines.observation.rules.network import NetworkFailureRule
from app.engines.observation.rules.performance import SlowResponseRule
from app.engines.observation.rules.ui import JavaScriptExceptionRule, UiRenderingFailureRule
from app.engines.observation.rules.validation import ValidationErrorRule


def get_default_rules() -> list[ObservationRule]:
    """
    Return the ordered list of active observation rules.

    The classifier evaluates ALL rules independently and picks the one with the
    highest confidence — rule order does not affect the result. However, placing
    more specific rules first improves readability and debugging.
    """
    return [
        AuthenticationFailureRule(),
        DatabaseTimeoutRule(),
        ApiFailureRule(),
        NetworkFailureRule(),
        ValidationErrorRule(),
        UiRenderingFailureRule(),
        JavaScriptExceptionRule(),
        SlowResponseRule(),
        ServiceUnavailableRule(),
        MissingResponseRule(),
    ]


def get_fallback_rule() -> ObservationRule:
    """Return the fallback rule used when no specific rule reaches threshold."""
    return UnknownFailureRule()


__all__ = [
    "ObservationRule",
    "get_default_rules",
    "get_fallback_rule",
    "AuthenticationFailureRule",
    "DatabaseTimeoutRule",
    "ApiFailureRule",
    "NetworkFailureRule",
    "ValidationErrorRule",
    "UiRenderingFailureRule",
    "JavaScriptExceptionRule",
    "SlowResponseRule",
    "ServiceUnavailableRule",
    "MissingResponseRule",
    "UnknownFailureRule",
]
