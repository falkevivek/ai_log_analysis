"""
LLM Manager — Provider Factory
================================
Single point of authority for selecting the active LLM adapter at runtime.

This is the ONLY module in the platform that reads ``LLM_PROVIDER`` from
configuration and knows which concrete adapter is in use.  All upstream
components (engines, orchestrator, API handlers) receive only the
``BaseLlmAdapter`` abstraction and are completely provider-unaware.

Supported Provider Values (LLM_PROVIDER env var)
-------------------------------------------------
``gemini``      → GeminiAdapter  (Google GenAI SDK)
``local_llama`` → LocalLlamaAdapter (Barclays on-premises; placeholder)
``mock``        → MockAdapter    (deterministic in-memory; default)

Adding a New Provider
---------------------
1. Implement a new file ``adapters/<provider>_adapter.py`` implementing
   ``BaseLlmAdapter.generate_diagnosis``.
2. Import it here and add its ``LLM_PROVIDER`` key to ``_PROVIDER_MAP``.
3. Update ``app/config/settings.py`` with any new env vars it needs.
4. Update ``.env.example`` and ``docs/LLM_SWITCH_GUIDE.md``.
No other file in the platform requires modification.
"""

from __future__ import annotations

import logging

from app.config.settings import Settings, get_settings
from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter
from app.engines.llm_reasoning.adapters.gemini_adapter import GeminiAdapter
from app.engines.llm_reasoning.adapters.local_llama_adapter import LocalLlamaAdapter
from app.engines.llm_reasoning.adapters.mock_adapter import MockAdapter
from app.exceptions.custom_exceptions import ConfigurationError

logger = logging.getLogger("ai_analysis_engine.engines.llm_reasoning.llm_manager")

# Enumeration of all supported provider keys.
_SUPPORTED_PROVIDERS = frozenset({"gemini", "local_llama", "mock"})


class LlmManager:
    """
    Factory / service that constructs and returns the correct ``BaseLlmAdapter``
    based on the ``LLM_PROVIDER`` configuration value.

    The manager is designed to be instantiated once per application lifecycle
    (at startup) and its ``get_adapter()`` result injected wherever an
    ``LlmReasoningEngine`` is constructed.

    Parameters
    ----------
    settings:
        The application ``Settings`` instance.  Defaults to the cached
        singleton returned by ``get_settings()``.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._provider = self._settings.llm_provider.lower().strip()
        logger.info(
            "LlmManager initialised | selected provider='%s'", self._provider
        )

    def get_adapter(self) -> BaseLlmAdapter:
        """
        Construct and return the active LLM adapter.

        The adapter instance is freshly constructed on every call.
        For singleton behaviour, cache the result in the caller.

        Returns
        -------
        BaseLlmAdapter
            The concrete adapter for the configured LLM provider.

        Raises
        ------
        ConfigurationError
            If ``LLM_PROVIDER`` is set to an unsupported value, or if
            required provider-specific configuration is missing.
        """
        if self._provider not in _SUPPORTED_PROVIDERS:
            raise ConfigurationError(
                message=(
                    f"Unsupported LLM_PROVIDER value: '{self._provider}'. "
                    f"Supported values are: {sorted(_SUPPORTED_PROVIDERS)}."
                ),
                detail={
                    "llm_provider": self._provider,
                    "supported": sorted(_SUPPORTED_PROVIDERS),
                },
            )

        adapter = self._build_adapter()
        logger.info(
            "LlmManager returned adapter | class=%s", adapter.__class__.__name__
        )
        return adapter

    # ------------------------------------------------------------------
    # Private factory methods
    # ------------------------------------------------------------------

    def _build_adapter(self) -> BaseLlmAdapter:
        """Dispatch to the correct private factory based on provider key."""
        if self._provider == "gemini":
            return self._build_gemini_adapter()
        if self._provider == "local_llama":
            return self._build_local_llama_adapter()
        # Default / mock
        return self._build_mock_adapter()

    def _build_gemini_adapter(self) -> GeminiAdapter:
        """
        Construct a ``GeminiAdapter`` from settings.

        Raises
        ------
        ConfigurationError
            If ``GEMINI_API_KEY`` is absent or empty.
        """
        api_key = self._settings.gemini_api_key or ""
        if not api_key.strip():
            raise ConfigurationError(
                message=(
                    "LLM_PROVIDER=gemini requires GEMINI_API_KEY to be set. "
                    "Add it to your .env file: GEMINI_API_KEY=AIza..."
                ),
                detail={"provider": "gemini"},
            )
        logger.info(
            "Building GeminiAdapter | model=%s", self._settings.gemini_model
        )
        return GeminiAdapter(
            api_key=api_key,
            model=self._settings.gemini_model,
        )

    def _build_local_llama_adapter(self) -> LocalLlamaAdapter:
        """
        Construct a ``LocalLlamaAdapter`` from settings.

        Raises
        ------
        ConfigurationError
            If ``LOCAL_LLM_ENDPOINT`` is absent or empty.
        """
        endpoint = self._settings.local_llm_endpoint or ""
        if not endpoint.strip():
            raise ConfigurationError(
                message=(
                    "LLM_PROVIDER=local_llama requires LOCAL_LLM_ENDPOINT to be set. "
                    "Add it to your .env file: "
                    "LOCAL_LLM_ENDPOINT=http://llama-server.internal:8080/v1/chat/completions"
                ),
                detail={"provider": "local_llama"},
            )
        logger.info(
            "Building LocalLlamaAdapter | endpoint=%s | model=%s",
            endpoint,
            self._settings.local_llm_model,
        )
        return LocalLlamaAdapter(
            endpoint_url=endpoint,
            model=self._settings.local_llm_model,
            timeout_seconds=self._settings.local_llm_timeout,
        )

    @staticmethod
    def _build_mock_adapter() -> MockAdapter:
        """Construct a ``MockAdapter`` with no configuration required."""
        logger.info("Building MockAdapter — no external configuration required.")
        return MockAdapter()
