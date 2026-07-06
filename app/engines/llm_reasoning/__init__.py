# LLM Reasoning Engine package
# Exposes the engine, all adapter classes, the LlmManager, and parsing utilities.

from app.engines.llm_reasoning.engine import LlmReasoningEngine
from app.engines.llm_reasoning.llm_manager import LlmManager
from app.engines.llm_reasoning.prompt_builder import PromptBuilder
from app.engines.llm_reasoning.parser import ResponseParser

# Adapter interface and concrete implementations
from app.engines.llm_reasoning.adapters import (
    BaseLlmAdapter,
    GeminiAdapter,
    LocalLlamaAdapter,
    MockAdapter,
)

# Backward-compat alias (was previously defined directly in adapter.py)
from app.engines.llm_reasoning.adapter import MetaLlamaAdapter

__all__ = [
    # Engine
    "LlmReasoningEngine",
    # Manager
    "LlmManager",
    # Builder / Parser
    "PromptBuilder",
    "ResponseParser",
    # Adapters
    "BaseLlmAdapter",
    "GeminiAdapter",
    "LocalLlamaAdapter",
    "MetaLlamaAdapter",
    "MockAdapter",
]
