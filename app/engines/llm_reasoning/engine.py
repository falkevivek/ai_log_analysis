"""
LLM Reasoning Engine
====================
Stage 9 of the AI Analysis pipeline.

Orchestrates the conversion of an Evidence package into a structured Prompt,
dispatches it via model-independent LLM Adapters, validates responses using a
schema-safe ResponseParser, and instantiates the final Diagnosis domain model.

Responsibilities
----------------
1. Receive a validated Evidence package.
2. Build deterministic system and user prompts via PromptBuilder.
3. Call the LLM backend adapter (selected at runtime by LlmManager from LLM_PROVIDER config).
4. Parse and sanitize response strings using ResponseParser.
5. Create a validated Diagnosis domain object populated with timestamps.

This engine does NOT
--------------------
- Generate recommendations or action plans (relegated to Stage 10).
- Establish feedback learning loops (relegated to Stage 11).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.engines.llm_reasoning.prompt_builder import PromptBuilder
from app.engines.llm_reasoning.adapter import BaseLlmAdapter
from app.engines.llm_reasoning.llm_manager import LlmManager
from app.engines.llm_reasoning.parser import ResponseParser
from app.exceptions.custom_exceptions import ValidationError
from app.schemas.domain import Evidence, Diagnosis

logger = logging.getLogger("ai_analysis_engine.engines.llm_reasoning.engine")


class LlmReasoningEngine:
    """Orchestrator coordinator executing the LLM incident root cause analysis."""

    def __init__(
        self,
        prompt_builder: Optional[PromptBuilder] = None,
        llm_adapter: Optional[BaseLlmAdapter] = None,
        response_parser: Optional[ResponseParser] = None
    ) -> None:
        """
        Initialize the LLM Reasoning Engine.

        Parameters
        ----------
        prompt_builder:
            Custom PromptBuilder block. Defaults to system templates.
        llm_adapter:
            Model-independent client adapter.  Defaults to the provider
            selected by ``LlmManager`` from the ``LLM_PROVIDER`` env var.
        response_parser:
            JSON parser and sanitizer rules.
        """
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm_adapter = llm_adapter or LlmManager().get_adapter()
        self.response_parser = response_parser or ResponseParser()
        logger.info(
            "LlmReasoningEngine coordinator initialized (adapter class: %s)",
            self.llm_adapter.__class__.__name__
        )

    def diagnose(self, evidence: Evidence) -> Diagnosis:
        """
        Diagnose the root cause from an Evidence Package.

        Parameters
        ----------
        evidence:
            Unified Evidence Package containing all gathered operational facts.

        Returns
        -------
        Diagnosis
            The validated Diagnosis domain object.

        Raises
        ------
        ValidationError
            If the evidence is empty or invalid, or if response validation fails.
        """
        if not evidence:
            raise ValidationError(
                message="Cannot perform AI reasoning on an empty or missing Evidence Package.",
                detail={"engine": "LlmReasoningEngine"}
            )

        logger.info(
            "Initiating AI Diagnosis reasoning | confidence=%.2f | services=%s",
            evidence.evidence_confidence,
            evidence.affected_services
        )

        # Step 1: Construct system and user prompts
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(evidence)

        # Step 2: Dispatch to LLM Adapter
        try:
            raw_response = self.llm_adapter.call_llm(system_prompt, user_prompt)
        except Exception as exc:
            raise ValidationError(
                message=f"LLM Adapter communication failed during execution: {str(exc)}",
                detail={"engine": "LlmReasoningEngine"}
            ) from exc

        # Step 3: Parse and sanitize raw LLM output
        parsed_data = self.response_parser.parse_response(raw_response)

        # Step 4: Build validated Diagnosis model
        try:
            diagnosis = Diagnosis(
                root_cause=parsed_data["root_cause"],
                confidence=parsed_data["confidence"],
                explanation=parsed_data["explanation"],
                evidence_references=parsed_data["evidence_references"],
                generated_at=datetime.now(timezone.utc)
            )
        except Exception as exc:
            raise ValidationError(
                message=f"Failed to validate Diagnosis domain contract: {str(exc)}",
                detail={"parsed_data": parsed_data}
            ) from exc

        logger.info(
            "Incident diagnosis established | root_cause='%s' | confidence=%.2f",
            diagnosis.root_cause,
            diagnosis.confidence
        )
        return diagnosis
