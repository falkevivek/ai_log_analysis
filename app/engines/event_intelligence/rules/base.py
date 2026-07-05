"""
Event Classification Rule Base
==============================
Defines the abstract interface for classifying grouped observations into events.

Extension Guide
---------------
To register a new type of Event:
  1. Create a concrete class subclassing EventRule.
  2. Implement `event_name`, `event_type`, and the `match` evaluation function.
  3. Register the rule in `rules/__init__.py`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from app.schemas.domain import Observation


class EventRule(ABC):
    """Abstract interface that event classification rules must implement."""

    @property
    @abstractmethod
    def event_name(self) -> str:
        """The user-facing name for this event, e.g., 'User Login Failure'."""
        ...

    @property
    @abstractmethod
    def event_type(self) -> str:
        """The semantic category code of the event, e.g., 'USER_LOGIN_FAILURE'."""
        ...

    @abstractmethod
    def match(self, observations: list[Observation]) -> float:
        """
        Evaluate a group of correlated observations.

        Returns a confidence score in [0.0, 1.0]. A score of 0.0 means the
        observations do not belong to this event category.
        """
        ...
