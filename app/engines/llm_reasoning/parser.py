"""
Response Parser for the LLM Reasoning Engine
=============================================
Parses, sanitizes, and validates the raw text output from the LLM to ensure
compliance with the expected JSON structure.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.exceptions.custom_exceptions import ValidationError

logger = logging.getLogger("ai_analysis_engine.engines.llm_reasoning.parser")


class ResponseParser:
    """Parses raw text outputs into structured JSON objects with schema safety validations."""

    def parse_response(self, raw_output: str) -> dict[str, Any]:
        """
        Clean and parse raw JSON text output from LLM models.

        Parameters
        ----------
        raw_output:
            The raw text returned by the LLM adapter.

        Returns
        -------
        dict[str, Any]
            Parsed dictionary containing root_cause, confidence, explanation,
            and evidence_references.

        Raises
        ------
        ValidationError
            If the response is completely unparseable or violates core schema bounds.
        """
        if not raw_output or not raw_output.strip():
            raise ValidationError(
                message="Received empty output response from LLM adapter.",
                detail={"parser": "ResponseParser"}
            )

        logger.debug("Raw output received for parsing: %s", raw_output[:200])

        # Step 1: Clean markdown wrapping if present (e.g. ```json ... ```)
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            # Strip block markdown markers
            cleaned = re.sub(r"^```[a-zA-Z0-9]*\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)
            cleaned = cleaned.strip()

        # Step 2: Attempt parsing
        try:
            parsed_data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            # Fallback regex extraction for simple cases or raise
            logger.warning("Failed to decode JSON from output: %s. Attempting regex extract.", str(exc))
            parsed_data = self._regex_fallback_extract(cleaned)
            if not parsed_data:
                raise ValidationError(
                    message=f"LLM output could not be parsed as valid JSON: {str(exc)}",
                    detail={"raw_output": raw_output}
                ) from exc

        # Step 3: Validate field presence and type bounds
        # Root Cause field
        root_cause = parsed_data.get("root_cause")
        if not root_cause or not isinstance(root_cause, str):
            logger.warning("Missing or malformed root_cause. Applying fallback.")
            parsed_data["root_cause"] = str(root_cause) if root_cause else "Root cause unknown"

        # Confidence field
        confidence = parsed_data.get("confidence")
        try:
            parsed_data["confidence"] = float(confidence) if confidence is not None else 0.5
            # Force bounds check
            parsed_data["confidence"] = max(0.0, min(1.0, parsed_data["confidence"]))
        except (ValueError, TypeError):
            logger.warning("Failed to convert confidence '%s' to float. Defaulting to 0.5.", str(confidence))
            parsed_data["confidence"] = 0.5

        # Explanation field
        explanation = parsed_data.get("explanation")
        if not explanation or not isinstance(explanation, str):
            logger.warning("Missing or malformed explanation. Applying fallback.")
            parsed_data["explanation"] = str(explanation) if explanation else "Reasoning detail not provided."

        # Evidence references field
        refs = parsed_data.get("evidence_references")
        if not isinstance(refs, list):
            parsed_data["evidence_references"] = []
        else:
            # Ensure elements are strings
            parsed_data["evidence_references"] = [str(r) for r in refs]

        return parsed_data

    @staticmethod
    def _regex_fallback_extract(text: str) -> dict[str, Any] | None:
        """Regex helper to parse simple unstructured responses if JSON fails."""
        try:
            rc_match = re.search(r'"root_cause"\s*:\s*"([^"]+)"', text)
            conf_match = re.search(r'"confidence"\s*:\s*([0-9\.]+)', text)
            exp_match = re.search(r'"explanation"\s*:\s*"([^"]+)"', text)

            if rc_match and conf_match and exp_match:
                return {
                    "root_cause": rc_match.group(1),
                    "confidence": float(conf_match.group(1)),
                    "explanation": exp_match.group(1),
                    "evidence_references": []
                }
        except Exception:
            pass
        return None
