"""
Prompt Builder for the LLM Reasoning Engine
============================================
Converts a structured Evidence Package into clean System and User prompts
following deterministic templates suitable for LLM reasoning.
"""

from __future__ import annotations

import json
from app.schemas.domain import Evidence


class PromptBuilder:
    """Serializes Evidence Packages into system and user prompt strings."""

    def build_system_prompt(self) -> str:
        """
        Generate the deterministic System prompt with strict instructions.
        """
        return (
            "You are an expert Enterprise Site Reliability Engineer and AI Diagnosis Agent.\n"
            "Your task is to identify the root cause of the incident based ONLY on the provided Evidence Package.\n\n"
            "Strict Guidelines:\n"
            "1. Use only the provided evidence. Do not assume, guess, or extrapolate facts.\n"
            "2. Never hallucinate. If details are missing or insufficient to locate the exact cause, "
            "explicitly state that the evidence is insufficient and adjust your confidence level downward.\n"
            "3. State your explanation step-by-step, referencing specific observation IDs or log timestamps.\n"
            "4. Do NOT propose recommendations, quick fixes, or permanent solutions. Only focus on diagnosis.\n"
            "5. You MUST output your final answer as a raw JSON object with the following fields:\n"
            "   - \"root_cause\": (string) Concise summary of the identified core issue.\n"
            "   - \"confidence\": (float between 0.0 and 1.0) Your confidence score based on evidence clarity.\n"
            "   - \"explanation\": (string) Step-by-step reasoning explaining the issue.\n"
            "   - \"evidence_references\": (array of strings) Unique observation IDs or component labels used.\n"
        )

    def build_user_prompt(self, evidence: Evidence) -> str:
        """
        Format the Evidence Package into a structured readable layout.
        """
        # Convert dictionaries and complex fields to formatted JSON strings
        metrics_str = json.dumps(evidence.supporting_metrics, indent=2)
        api_str = json.dumps(evidence.api_metadata, indent=2)
        config_str = json.dumps(evidence.config_metadata, indent=2)
        deploy_str = json.dumps(evidence.deployment_info, indent=2)
        meta_str = json.dumps(evidence.additional_metadata, indent=2)

        return (
            "Evidence Package under analysis:\n"
            "=================================\n\n"
            f"Environment: {evidence.environment}\n"
            f"Evidence Collection Confidence Score: {evidence.evidence_confidence:.2f}\n\n"
            "System Overview:\n"
            "----------------\n"
            f"- Affected Services: {', '.join(evidence.affected_services) if evidence.affected_services else 'none'}\n"
            f"- Affected Components: {', '.join(evidence.affected_components) if evidence.affected_components else 'none'}\n\n"
            "Incident Summary:\n"
            "-----------------\n"
            f"{evidence.incident_summary}\n\n"
            "Timeline:\n"
            "---------\n"
            f"Timeline Summary: {evidence.timeline_summary}\n"
            f"{evidence.event_summary}\n\n"
            "Observations Log:\n"
            "-----------------\n"
            f"{evidence.observation_summary}\n\n"
            "Known Errors & Signatures:\n"
            "--------------------------\n"
            f"- Errors Matched: {', '.join(evidence.known_errors) if evidence.known_errors else 'none'}\n"
            f"- Matched Signature Codes: {', '.join(evidence.error_codes) if evidence.error_codes else 'none'}\n\n"
            "Historical Incident Tickets:\n"
            "----------------------------\n"
            f"- Historical References: {', '.join(evidence.historical_references) if evidence.historical_references else 'none'}\n\n"
            "API Gateway Metadata:\n"
            "---------------------\n"
            f"{api_str}\n\n"
            "Configuration Settings:\n"
            "-----------------------\n"
            f"{config_str}\n\n"
            "Deployment Information:\n"
            "-----------------------\n"
            f"{deploy_str}\n\n"
            "Supporting Metrics:\n"
            "-------------------\n"
            f"{metrics_str}\n\n"
            "Additional Context Metadata:\n"
            "----------------------------\n"
            f"{meta_str}\n\n"
            "Analyze the above evidence step-by-step and return your structured JSON diagnosis."
        )
