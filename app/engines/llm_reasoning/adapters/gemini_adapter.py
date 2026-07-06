"""
Gemini LLM Adapter
==================
Implements ``BaseLlmAdapter`` using the official Google GenAI Python SDK.

Configuration is read exclusively from environment variables — no secrets
are hardcoded anywhere in this file.

Environment Variables Required
------------------------------
GEMINI_API_KEY   : Google GenAI API key (required).
GEMINI_MODEL     : Model identifier (default: gemini-2.0-flash).

Isolation Contract
------------------
ONLY this module may import ``google.genai``.  No other engine, manager,
or orchestrator component may reference the Google GenAI SDK directly.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter
from app.exceptions.custom_exceptions import ConfigurationError, ServiceUnavailableError

logger = logging.getLogger("ai_analysis_engine.engines.llm_reasoning.adapters.gemini")

# ---------------------------------------------------------------------------
# Gemini SDK import — isolated to this module only
# ---------------------------------------------------------------------------
try:
    from google import genai  # type: ignore[import-untyped]
    from google.genai import types as genai_types  # type: ignore[import-untyped]
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]


class GeminiAdapter(BaseLlmAdapter):
    """
    LLM Adapter for Google Gemini models via the google-genai SDK.

    Parameters
    ----------
    api_key:
        Google GenAI API key.  Must be supplied — cannot be empty.
    model:
        Gemini model identifier (e.g. ``gemini-2.0-flash``).
    temperature:
        Sampling temperature.  Set to 0.0 for fully deterministic output.
    max_output_tokens:
        Maximum number of tokens in the model response.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.0,
        max_output_tokens: int = 2048,
    ) -> None:
        if not _GENAI_AVAILABLE:
            raise ConfigurationError(
                message=(
                    "The google-genai package is not installed. "
                    "Run: pip install google-genai"
                ),
                detail={"adapter": "GeminiAdapter"},
            )

        if not api_key or not api_key.strip():
            raise ConfigurationError(
                message=(
                    "GEMINI_API_KEY is missing or empty. "
                    "Set it in your .env file or environment before using the Gemini provider."
                ),
                detail={"adapter": "GeminiAdapter"},
            )

        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

        # Initialise the SDK client — credentials stay inside this adapter
        self._client = genai.Client(api_key=api_key)

        logger.info(
            "GeminiAdapter initialised | model=%s | temperature=%.1f",
            self._model,
            self._temperature,
        )

    # ------------------------------------------------------------------
    # BaseLlmAdapter implementation
    # ------------------------------------------------------------------

    def generate_diagnosis(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send prompts to Gemini and return the raw text response.

        The system prompt is passed via the ``system_instruction`` field
        of the generation config, keeping it separate from the user turn.

        Parameters
        ----------
        system_prompt:
            Model role and output format instructions.
        user_prompt:
            Serialised Evidence Package.

        Returns
        -------
        str
            Raw text content of the first candidate from the model response.

        Raises
        ------
        ServiceUnavailableError
            If the Gemini API call fails for any reason.
        """
        logger.info(
            "Dispatching diagnosis request to Gemini | model=%s", self._model
        )

        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self._temperature,
            max_output_tokens=self._max_output_tokens,
            response_mime_type="application/json",
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=config,
            )
        except Exception as exc:
            logger.error(
                "Gemini API call failed: %s", str(exc), exc_info=True
            )
            raise ServiceUnavailableError(
                message=f"Gemini provider is unavailable: {str(exc)}",
                detail={"adapter": "GeminiAdapter", "model": self._model},
            ) from exc

        raw_text: Optional[str] = None

        # Safely extract text from the response candidates
        try:
            raw_text = response.text
        except (AttributeError, ValueError):
            pass

        if not raw_text:
            # Defensive fallback: walk candidates manually
            try:
                raw_text = response.candidates[0].content.parts[0].text
            except (IndexError, AttributeError) as inner_exc:
                raise ServiceUnavailableError(
                    message="Gemini returned an empty or unreadable response.",
                    detail={"adapter": "GeminiAdapter", "model": self._model},
                ) from inner_exc

        logger.debug(
            "Gemini response received | chars=%d | preview=%s",
            len(raw_text),
            raw_text[:120],
        )
        return raw_text
