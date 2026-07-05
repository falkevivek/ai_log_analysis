"""
Correlation Group Schema
=========================
Defines the data contract representing a group of correlated observations
that belong to the same execution flow.

These schemas are pure Pydantic models for data transfer across the pipeline.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.domain import Observation


class CorrelationGroup(BaseModel):
    """Represents a set of observations correlated by an identifier or heuristic rule."""

    correlation_id: str = Field(..., description="Unique identifier for this correlated group")
    related_observations: list[Observation] = Field(default_factory=list, description="List of observations in the group")
    correlation_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level of this correlation (0.0 to 1.0)")
    correlation_method: str = Field(..., description="The method/rule used to establish this correlation")
    start_time: datetime = Field(..., description="Earliest timestamp among the grouped observations")
    end_time: datetime = Field(..., description="Latest timestamp among the grouped observations")
