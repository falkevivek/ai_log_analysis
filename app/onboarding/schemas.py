"""
Project Onboarding Pydantic Schemas
==================================
Defines the structure for Barclays application configuration onboarding.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ServiceMetadata(BaseModel):
    """Lists services, components and API endpoint signatures for the application."""

    services: list[str] = Field(default_factory=list, description="List of service names")
    components: list[str] = Field(default_factory=list, description="List of components/modules")
    api_endpoints: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Registered API endpoint routing and verification details"
    )


class SeverityRule(BaseModel):
    """Maps errors or logs patterns to severity levels."""

    pattern: str = Field(..., description="Regular expression pattern to match")
    severity: str = Field(..., description="Target severity level: LOW, MEDIUM, HIGH, CRITICAL")


class ErrorDefinition(BaseModel):
    """Configures standard error codes, categories, and severity rules."""

    error_codes: list[str] = Field(default_factory=list, description="Standard error code identifiers")
    error_categories: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Key: category, Value: list of associated error codes"
    )
    severity_rules: list[SeverityRule] = Field(
        default_factory=list,
        description="Rules determining log level/component severity upgrades"
    )


class FlowDefinition(BaseModel):
    """Specifies the expected chronological sequence of services/components."""

    expected_service_flow: list[str] = Field(
        default_factory=list,
        description="Ordered sequence of service names representing typical transaction journey"
    )
    expected_component_flow: list[str] = Field(
        default_factory=list,
        description="Ordered sequence of component names representing typical transaction journey"
    )


class CustomPattern(BaseModel):
    """Defines custom observation extraction rules."""

    name: str = Field(..., description="Descriptive identifier of the anomaly type")
    keywords: list[str] = Field(..., description="List of trigger words matching this anomaly")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    severity: str = Field("MEDIUM", description="Resulting observation severity")


class ProjectOnboardingConfig(BaseModel):
    """Top-level configuration schema for onboarding a Barclays application."""

    # Project identification metadata
    project_id: str = Field(..., description="Unique slug identifying the project (e.g. 'retail-banking')")
    project_name: str = Field(..., description="Barclays application portfolio project name")
    application_name: str = Field(..., description="Name of the specific service application")
    environment: str = Field("production", description="Deployment environment tier: production, staging, development")
    team_name: str = Field(..., description="Owner team name")
    contact_info: str = Field(..., description="Contact email or chat channel references")

    # Metadata configurations
    service_metadata: ServiceMetadata = Field(default_factory=ServiceMetadata)
    error_definitions: ErrorDefinition = Field(default_factory=ErrorDefinition)
    flow_definitions: FlowDefinition = Field(default_factory=FlowDefinition)

    # Pluggable Engine override rules templates
    observation_patterns: list[CustomPattern] = Field(default_factory=list)
    event_templates: list[dict[str, Any]] = Field(default_factory=list)
    timeline_templates: list[dict[str, Any]] = Field(default_factory=list)
    recommendation_rules: list[dict[str, Any]] = Field(default_factory=list)

    # Model parameters override options
    llm_configuration: dict[str, Any] = Field(default_factory=dict, description="LLM adapter system/user prompt overrides")
