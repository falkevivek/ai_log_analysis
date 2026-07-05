"""
Context Enrichment Engine
=========================
Stage 7 of the AI Analysis pipeline.

Enriches a built Incident object with all available contextual information
gathered by multiple independent and pluggable ContextProviders.

Responsibilities
----------------
1. Receive an Incident object.
2. Coordinate execution across registered ContextProviders.
3. Catch provider exceptions internally to ensure enrichment never crashes.
4. Merge and map gathered contextual fields.
5. Produce a validated Context domain object ready for the Evidence Builder.

This engine does NOT
--------------------
- Perform root cause diagnosis.
- Query LLM APIs or suggest fixes.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.engines.context_enrichment.providers import get_default_context_providers, BaseContextProvider
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Incident, Context

logger = logging.getLogger("ai_analysis_engine.engines.context_enrichment.engine")


class ContextEnrichmentEngine:
    """Orchestrates ContextProviders to enrich an Incident with operational context."""

    def __init__(self, providers: Optional[list[BaseContextProvider]] = None) -> None:
        """
        Initialize the Context Enrichment Engine.

        Parameters
        ----------
        providers:
            Optional custom list of ContextProvider objects.
            If None, defaults to the registered default onboarding providers.
        """
        self.providers = providers if providers is not None else get_default_context_providers()
        logger.info(
            "ContextEnrichmentEngine initialized with %d providers",
            len(self.providers)
        )

    def enrich_incident(self, incident: Incident) -> Context:
        """
        Gather context and enrich the Incident.

        Parameters
        ----------
        incident:
            The Incident domain object to enrich.

        Returns
        -------
        Context
            The validated Context object representing enriched incident facts.

        Raises
        ------
        ValidationError
            If the input incident is invalid or if Pydantic validation fails.
        """
        if not incident:
            raise ValidationError(
                message="Cannot enrich a null or empty Incident.",
                detail={"engine": "ContextEnrichmentEngine"}
            )

        logger.debug("Enriching incident context | incident_id=%s", incident.incident_id)

        # Initialize consolidated context dictionary
        context_data: dict[str, Any] = {
            "services": list(incident.affected_services),
            "components": list(incident.affected_components),
            "api_metadata": {},
            "known_errors": [],
            "historical_references": [],
            "config_metadata": {},
            "metadata": {}
        }

        # Run each provider sequentially, swallowing exceptions for resilience
        for provider in self.providers:
            try:
                data = provider.enrich(incident)
                if not data:
                    continue

                # Merge gathered fields into the target context map
                for key, val in data.items():
                    if key in ("project_name", "environment", "application"):
                        context_data[key] = val
                    elif key == "api_metadata":
                        context_data["api_metadata"].update(val)
                    elif key == "config_metadata":
                        context_data["config_metadata"].update(val)
                    elif key == "known_errors" and isinstance(val, list):
                        context_data["known_errors"].extend(val)
                    elif key == "historical_references" and isinstance(val, list):
                        context_data["historical_references"].extend(val)
                    elif key == "metadata" and isinstance(val, dict):
                        context_data["metadata"].update(val)
                    else:
                        # Append any other unmapped fields to metadata
                        context_data["metadata"][key] = val

            except Exception as exc:
                logger.warning(
                    "Context provider %s failed during execution: %s. Continuing.",
                    provider.provider_name,
                    str(exc)
                )

        # Ensure required fields have fallbacks if no provider supplied them
        project_name = context_data.get("project_name", incident.incident_metadata.project or "Unknown Project")
        environment = context_data.get("environment", incident.incident_metadata.environment or "production")
        application = context_data.get("application", incident.incident_metadata.application or "Unknown Application")

        # De-duplicate lists
        context_data["known_errors"] = sorted(list(set(context_data["known_errors"])))
        context_data["historical_references"] = sorted(list(set(context_data["historical_references"])))

        try:
            context = Context(
                incident=incident,
                project_name=project_name,
                environment=environment,
                application=application,
                services=context_data["services"],
                components=context_data["components"],
                api_metadata=context_data["api_metadata"],
                known_errors=context_data["known_errors"],
                historical_references=context_data["historical_references"],
                config_metadata=context_data["config_metadata"],
                metadata=context_data["metadata"]
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Context domain contract: {str(exc)}",
                detail={"incident_id": incident.incident_id}
            ) from exc

        logger.info(
            "Incident context enriched | incident_id=%s | project=%s | env=%s",
            incident.incident_id,
            context.project_name,
            context.environment
        )
        return context
