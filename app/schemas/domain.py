"""
AI Analysis Core Domain Contracts
===================================
Defines the immutable data models that act as communication contracts
between all stages of the AI Analysis pipeline.

These models are purely data contracts and contain no business logic,
database mappings, or external library dependencies other than Pydantic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class RawLog(BaseModel):
    """Represents the original log ingested from an external system."""

    log_id: str = Field(..., description="Unique identifier for the raw log")
    timestamp: datetime = Field(..., description="Original log timestamp")
    source: str = Field(..., description="Origin source system of the log")
    service: str = Field(..., description="Name of the service emitting the log")
    component: str = Field(..., description="Sub-component or module within the service")
    log_level: str = Field(..., description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    message: str = Field(..., description="The raw unparsed log message text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary extra log metadata")


class NormalizedLog(BaseModel):
    """Represents a clean, structured log after preprocessing and normalization."""

    log_id: str = Field(..., description="Unique identifier corresponding to the log")
    timestamp: datetime = Field(..., description="Standardized log timestamp")
    service: str = Field(..., description="Standardized service name")
    component: str = Field(..., description="Standardized component name")
    log_level: str = Field(..., description="Standardized log level name")
    message: str = Field(..., description="Cleaned log message body")
    template: Optional[str] = Field(None, description="Optional identified log pattern/template ID")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Extracted parameters/variables from log text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context or tag metadata")


class Observation(BaseModel):
    """Represents a meaningful finding or log anomaly extracted by analysis."""

    observation_id: str = Field(..., description="Unique identifier of the observation")
    type: str = Field(..., description="Observation type, e.g., AUTHENTICATION_FAILURE, DATABASE_TIMEOUT")
    severity: str = Field(..., description="Severity classification, e.g., LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level of observation accuracy (0.0 to 1.0)")
    component: str = Field(..., description="Affected system component")
    description: str = Field(..., description="Human-readable description of what was observed")
    related_logs: list[NormalizedLog] = Field(default_factory=list, description="Collection of logs supporting this observation")


class Event(BaseModel):
    """Represents a grouping of related observations forming a single logical event."""

    event_id: str = Field(..., description="Unique event identifier")
    event_name: str = Field(..., description="Descriptive name of the event")
    event_type: str = Field(..., description="The type/classification of the event")
    severity: str = Field(..., description="Event severity: LOW, MEDIUM, HIGH, CRITICAL")
    observations: list[Observation] = Field(default_factory=list, description="Observations included in this event")
    start_time: datetime = Field(..., description="Start timestamp of the event")
    end_time: datetime = Field(..., description="End timestamp of the event")
    affected_services: list[str] = Field(default_factory=list, description="List of services impacted by this event")
    affected_components: list[str] = Field(default_factory=list, description="List of components impacted by this event")



class Timeline(BaseModel):
    """Represents an ordered sequence of events over a time window."""

    timeline_id: str = Field(..., description="Unique timeline identifier")
    events: list[Event] = Field(default_factory=list, description="Ordered list of events in this timeline")
    start_time: datetime = Field(..., description="Overall start window of the timeline")
    end_time: datetime = Field(..., description="Overall end window of the timeline")
    duration: float = Field(..., description="Total duration of the timeline in seconds")
    affected_services: list[str] = Field(default_factory=list, description="Unique services involved in this timeline")
    affected_components: list[str] = Field(default_factory=list, description="Unique components involved in this timeline")
    execution_flow: list[str] = Field(default_factory=list, description="Reconstructed chronological component execution path")
    missing_steps: list[str] = Field(default_factory=list, description="Identified missing steps or execution gaps in the flow")
    timeline_summary: str = Field(..., description="A short summary description of the sequence")



class IncidentMetadata(BaseModel):
    """Structured incident metadata that can grow over time."""
    category: str = Field("unknown", description="Operational category of the incident")
    priority: str = Field("unknown", description="Business priority level")
    environment: str = Field("unknown", description="Deployment environment")
    application: str = Field("unknown", description="Affected application name")
    project: str = Field("unknown", description="Affected project name")
    tags: list[str] = Field(default_factory=list, description="Supplemental tags for categorization")


class Incident(BaseModel):
    """Represents a high-level operational incident under investigation."""

    incident_id: str = Field(..., description="Unique incident identifier")
    timeline_id: str = Field(..., description="The ID of the linked timeline")
    timeline: Timeline = Field(..., description="Timeline of events associated with this incident")
    start_time: datetime = Field(..., description="Incident start timestamp")
    end_time: datetime = Field(..., description="Incident end timestamp")
    duration: float = Field(..., description="Incident duration in seconds")
    severity: str = Field(..., description="Incident severity classification, e.g. CRITICAL, HIGH, MEDIUM, LOW")
    status: str = Field(..., description="Status of the incident investigation (e.g. ACTIVE, CLOSED)")
    summary: str = Field(..., description="A concise natural-language summary of the incident")
    affected_services: list[str] = Field(default_factory=list, description="Services impacted by this incident")
    affected_components: list[str] = Field(default_factory=list, description="Components impacted by this incident")
    related_events_count: int = Field(..., description="Number of related events")
    related_observations_count: int = Field(..., description="Number of related observations")
    created_at: datetime = Field(..., description="Timestamp when the incident record was created")
    incident_metadata: IncidentMetadata = Field(default_factory=IncidentMetadata, description="Extensible metadata tags")



class Context(BaseModel):
    """Represents the environment-specific project onboarding context."""

    incident: Incident = Field(..., description="The Incident being enriched")
    project_name: str = Field(..., description="Name of the onboarded project")
    environment: str = Field(..., description="Deployment environment: production, staging, development")
    application: str = Field(..., description="Onboarded application name")
    services: list[str] = Field(default_factory=list, description="Services related to the incident")
    components: list[str] = Field(default_factory=list, description="Components related to the incident")
    api_metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata related to API endpoints involved")
    known_errors: list[str] = Field(default_factory=list, description="Standard error code definitions or matches")
    historical_references: list[str] = Field(default_factory=list, description="References to historical incidents")
    config_metadata: dict[str, Any] = Field(default_factory=dict, description="Related configuration files/settings details")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context parameters")



class Evidence(BaseModel):
    """Represents the complete package of collected facts ready for AI reasoning."""

    observations: list[Observation] = Field(default_factory=list, description="Anomalies and observations collected")
    timeline: Timeline = Field(..., description="The timeline context of events")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Relevant metrics datasets during the incident window")
    historical_references: list[str] = Field(default_factory=list, description="IDs of past similar incident records")
    known_errors: list[str] = Field(default_factory=list, description="Known error database reference matches")


class Diagnosis(BaseModel):
    """Represents the output reasoning from the AI diagnosis engine."""

    root_cause: str = Field(..., description="Identified core root cause of the incident")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level of diagnosis (0.0 to 1.0)")
    explanation: str = Field(..., description="Detailed markdown explanation detailing reasoning and evidence chain")


class Recommendation(BaseModel):
    """Represents operational recommendations for remediation."""

    immediate_action: str = Field(..., description="Suggested quick-fix or mitigation action to restore service")
    permanent_solution: str = Field(..., description="Suggested long-term root cause resolution")
    additional_notes: Optional[str] = Field(None, description="Optional extra engineering or diagnostic notes")
