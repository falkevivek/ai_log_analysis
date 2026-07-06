"""
LLM Adapter Base Interface
==========================
Defines the single abstract contract that every LLM provider adapter must
fulfil. No provider-specific SDK, endpoint, or credential logic may appear
in this module.

Design Principles
-----------------
* **Interface Segregation** — one method only; adapters add nothing extra.
* **Dependency Inversion** — all upstream components (LlmReasoningEngine,
  LlmManager) depend on this abstraction, never on concrete providers.
* **Open/Closed** — adding a new LLM provider requires a new file in this
  package and a one-line entry in LlmManager. Zero existing code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLlmAdapter(ABC):
    """
    Generic, provider-independent LLM service interface.

    Every concrete adapter (Gemini, LocalLlama, Mock, …) must implement
    ``generate_diagnosis``.  No other public method is required.

    The method name ``call_llm`` is preserved as an alias so that the
    existing ``LlmReasoningEngine.diagnose`` call-site continues to work
    without modification.
    """

    @abstractmethod
    def generate_diagnosis(self, system_prompt: str, user_prompt: str) -> str:
        """
        Submit system and user prompts to the underlying LLM backend and
        return the raw text response.

        Parameters
        ----------
        system_prompt:
            Instruction block describing the model's role and output rules.
        user_prompt:
            The serialised Evidence Package for analysis.

        Returns
        -------
        str
            Raw text response from the model.  The caller (ResponseParser)
            is responsible for JSON extraction and validation.

        Raises
        ------
        ServiceUnavailableError
            When the underlying provider cannot be reached or returns a
            non-recoverable error.
        """

    # ------------------------------------------------------------------
    # Backward-compatibility alias
    # ------------------------------------------------------------------
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Alias for ``generate_diagnosis``.

        Preserves the ``call_llm`` contract used by the existing
        ``LlmReasoningEngine`` without requiring any change to that engine.
        """
        return self.generate_diagnosis(system_prompt, user_prompt)
