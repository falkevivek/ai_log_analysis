"""
LLM Integration Layer Smoke Test
=================================
Verifies the import chain and adapter selection without requiring any
external API or network access.  Run with:

    .venv\\Scripts\\python.exe scripts\\smoke_test_llm.py
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- 1. Settings now have LLM fields ----
print("[1/6] Importing Settings...", end=" ")
from app.config.settings import get_settings
settings = get_settings()
assert hasattr(settings, "llm_provider"), "llm_provider field missing from Settings"
assert hasattr(settings, "gemini_api_key"), "gemini_api_key field missing from Settings"
assert hasattr(settings, "gemini_model"), "gemini_model field missing from Settings"
assert hasattr(settings, "local_llm_endpoint"), "local_llm_endpoint field missing from Settings"
assert hasattr(settings, "local_llm_model"), "local_llm_model field missing from Settings"
assert hasattr(settings, "local_llm_timeout"), "local_llm_timeout field missing from Settings"
print(f"OK  (llm_provider='{settings.llm_provider}')")

# ---- 2. BaseLlmAdapter interface importable ----
print("[2/6] Importing BaseLlmAdapter...", end=" ")
from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter
assert hasattr(BaseLlmAdapter, "generate_diagnosis"), "generate_diagnosis method missing"
assert hasattr(BaseLlmAdapter, "call_llm"), "call_llm alias missing"
print("OK")

# ---- 3. MockAdapter produces deterministic output ----
print("[3/6] Testing MockAdapter...", end=" ")
from app.engines.llm_reasoning.adapters.mock_adapter import MockAdapter
import json
adapter = MockAdapter()
result = adapter.generate_diagnosis("system", "database connection pool exhausted")
parsed = json.loads(result)
assert "root_cause" in parsed, "root_cause missing from mock response"
assert "confidence" in parsed, "confidence missing from mock response"
assert "explanation" in parsed, "explanation missing from mock response"
assert "evidence_references" in parsed, "evidence_references missing from mock response"
assert 0.0 <= parsed["confidence"] <= 1.0, "confidence out of bounds"
print(f"OK  (root_cause='{parsed['root_cause'][:50]}...')")

# ---- 4. MockAdapter call_llm alias works ----
print("[4/6] Testing call_llm alias...", end=" ")
result2 = adapter.call_llm("system", "auth token expired oauth 401")
parsed2 = json.loads(result2)
assert "root_cause" in parsed2
print(f"OK  (keyword=auth -> root_cause='{parsed2['root_cause'][:50]}...')")

# ---- 5. LlmManager selects MockAdapter from config ----
print("[5/6] Testing LlmManager with mock provider...", end=" ")
os.environ["LLM_PROVIDER"] = "mock"
get_settings.cache_clear()
from app.engines.llm_reasoning.llm_manager import LlmManager
manager = LlmManager(get_settings())
selected = manager.get_adapter()
assert isinstance(selected, MockAdapter), f"Expected MockAdapter, got {type(selected)}"
print(f"OK  (returned {selected.__class__.__name__})")

# ---- 6. LlmReasoningEngine uses LlmManager by default ----
print("[6/6] Testing LlmReasoningEngine default wiring...", end=" ")
from app.engines.llm_reasoning.engine import LlmReasoningEngine
engine = LlmReasoningEngine()
assert isinstance(engine.llm_adapter, MockAdapter), (
    f"Expected MockAdapter in engine, got {type(engine.llm_adapter)}"
)
print(f"OK  (engine.llm_adapter={engine.llm_adapter.__class__.__name__})")

# ---- Backward-compat: old import paths ----
print("\n[compat] Verifying backward-compatible imports from adapter.py...", end=" ")
from app.engines.llm_reasoning.adapter import BaseLlmAdapter as B2, MetaLlamaAdapter
from app.engines.llm_reasoning import LlmReasoningEngine as E2, LlmManager as LM2
print("OK")

print("\n" + "=" * 60)
print("  ALL SMOKE TESTS PASSED")
print("  LLM Integration Layer wired correctly.")
print("  Active provider:", settings.llm_provider)
print("=" * 60)
