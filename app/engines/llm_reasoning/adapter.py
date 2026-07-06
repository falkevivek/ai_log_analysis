"""
LLM Adapter Compatibility Shim
================================
This module is the backward-compatibility bridge between the original
``adapter.py`` import surface (used by ``LlmReasoningEngine``) and the new
``adapters/`` package introduced in the LLM Integration Layer sprint.

All classes previously defined here are now re-exported from the new package.
No module that already imports from this path needs to change.

DO NOT add any provider-specific logic here.
All concrete adapter implementations live in ``adapters/``.
"""

from __future__ import annotations

# Re-export the new interface and all concrete adapters so that any existing
# import of the form:
#     from app.engines.llm_reasoning.adapter import BaseLlmAdapter, MetaLlamaAdapter
# continues to resolve without modification.

from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter
from app.engines.llm_reasoning.adapters.mock_adapter import MockAdapter
from app.engines.llm_reasoning.adapters.gemini_adapter import GeminiAdapter
from app.engines.llm_reasoning.adapters.local_llama_adapter import LocalLlamaAdapter

# ---------------------------------------------------------------------------
# MetaLlamaAdapter backward-compat alias
# ---------------------------------------------------------------------------
# The original engine.py references MetaLlamaAdapter as the legacy default.
# We alias it to LocalLlamaAdapter so historical imports do not break.
# The LlmReasoningEngine now defaults to LlmManager().get_adapter(), so this
# alias is only exercised if code explicitly instantiates MetaLlamaAdapter().
# ---------------------------------------------------------------------------
MetaLlamaAdapter = LocalLlamaAdapter  # noqa: N816 — intentional alias

__all__ = [
    "BaseLlmAdapter",
    "GeminiAdapter",
    "LocalLlamaAdapter",
    "MetaLlamaAdapter",
    "MockAdapter",
]
