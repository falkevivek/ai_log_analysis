"""
User Login Failure Event Rule
=============================
Matches correlated observations indicating authentication timeouts or database/API
failures during user login flows.
"""

from __future__ import annotations

from app.engines.event_intelligence.rules.base import EventRule
from app.schemas.domain import Observation


class UserLoginFailureRule(EventRule):
    """
    Fires when auth failures combine with database/API errors.
    """

    @property
    def event_name(self) -> str:
        return "User Login Failure"

    @property
    def event_type(self) -> str:
        return "USER_LOGIN_FAILURE"

    def match(self, observations: list[Observation]) -> float:
        if not observations:
            return 0.0

        types = {obs.type for obs in observations}

        has_auth = "AUTHENTICATION_FAILURE" in types
        has_db = "DATABASE_TIMEOUT" in types
        has_api = "API_FAILURE" in types
        has_avail = "SERVICE_UNAVAILABLE" in types

        # Scenario 1: Authentication failure coupled with database/API/Availability issue
        if has_auth and (has_db or has_api or has_avail):
            return 1.0

        # Scenario 2: Just authentication failure (likely simpler credential issues)
        if has_auth:
            return 0.8

        return 0.0
