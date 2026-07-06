"""
Mock LLM Adapter
================
Implements ``BaseLlmAdapter`` with fully deterministic, in-memory responses.

No network I/O is performed.  Responses are driven by keyword matching
against the user prompt so that different Evidence Packages return
contextually appropriate mock diagnoses.

Use Cases
---------
* Local development — no API key required.
* Unit and integration testing — no external dependencies.
* CI / CD pipeline execution — fully hermetic.

Setting
-------
Set ``LLM_PROVIDER=mock`` in your ``.env`` file to activate this adapter.
"""

from __future__ import annotations

import json
import logging

from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter

logger = logging.getLogger(
    "ai_analysis_engine.engines.llm_reasoning.adapters.mock"
)

# ---------------------------------------------------------------------------
# Deterministic response fixtures
# ---------------------------------------------------------------------------

_MOCK_DATABASE_DIAGNOSIS = {
    "root_cause": "Database connection pool exhaustion on PostgreSQL instances",
    "confidence": 0.92,
    "explanation": (
        "The transaction flow indicates a timeout waiting for available "
        "database connection pool slots.  The configured pool size of 20 "
        "connections was saturated during auth-gateway query spikes, causing "
        "cascading client-API timeouts.  Observation IDs obs-db-01 and "
        "obs-db-02 confirm sustained wait-time anomalies on the pg_stat_activity "
        "view, with zero idle connections available for over 90 seconds."
    ),
    "evidence_references": ["obs-db-01", "obs-db-02"],
}

_MOCK_AUTH_DIAGNOSIS = {
    "root_cause": "Expired OAuth token rejection in the validation gateway filter",
    "confidence": 0.88,
    "explanation": (
        "The incident timeline originates with validation failures inside the "
        "authorization filter chain.  HTTP 401 response codes with error body "
        "'token_expired' match the pattern for client credentials whose refresh "
        "cycle failed silently.  Observation obs-auth-01 records a burst of "
        "401 errors at T+0s preceding all downstream failures."
    ),
    "evidence_references": ["obs-auth-01"],
}

_MOCK_NETWORK_DIAGNOSIS = {
    "root_cause": "Upstream service TCP connection timeout on payment-service calls",
    "confidence": 0.79,
    "explanation": (
        "Repeated connection-reset events are logged across three microservice "
        "boundaries.  The timeline shows a stepwise latency increase starting "
        "at the network edge, propagating inward to the API gateway.  "
        "Observation obs-net-01 records socket timeout at 30 000 ms — matching "
        "the default client connect-timeout — indicating the upstream payment "
        "service stopped accepting new TCP connections."
    ),
    "evidence_references": ["obs-net-01", "obs-net-02"],
}

_MOCK_MEMORY_DIAGNOSIS = {
    "root_cause": "JVM heap exhaustion causing Out-Of-Memory kill on the analytics pod",
    "confidence": 0.85,
    "explanation": (
        "The pod-restart sequence in the timeline coincides with container "
        "OOM-kill events in the cluster node logs.  Heap allocation traces "
        "show a monotonically increasing retained-objects curve over 4 hours "
        "prior to failure, consistent with a memory leak in the report "
        "aggregation batch job.  Observation obs-mem-01 records the OOMKilled "
        "exit code."
    ),
    "evidence_references": ["obs-mem-01"],
}

_MOCK_GENERAL_DIAGNOSIS = {
    "root_cause": "General upstream microservice latency degradation",
    "confidence": 0.70,
    "explanation": (
        "The execution-sequence timeline demonstrates elevated response latency "
        "across multiple components with no specific database, gateway, or "
        "network timeout signatures matched in the provided evidence.  "
        "Confidence is intentionally moderate — the evidence package does not "
        "contain sufficient discriminating signals for a high-confidence "
        "root-cause attribution."
    ),
    "evidence_references": [],
}


class MockAdapter(BaseLlmAdapter):
    """
    Deterministic in-memory LLM adapter for development and testing.

    Keyword matching against the lower-cased user prompt selects the most
    contextually appropriate fixture response.  The matching priority is:

    1. ``database`` / ``db`` / ``postgres`` / ``pool`` → database diagnosis
    2. ``auth`` / ``token`` / ``oauth`` / ``401``      → auth diagnosis
    3. ``network`` / ``tcp`` / ``socket`` / ``timeout`` → network diagnosis
    4. ``memory`` / ``heap`` / ``oom`` / ``leak``       → memory diagnosis
    5. (default)                                        → general diagnosis
    """

    def __init__(self) -> None:
        logger.info(
            "MockAdapter initialised — all responses are deterministic in-memory fixtures."
        )

    # ------------------------------------------------------------------
    # BaseLlmAdapter implementation
    # ------------------------------------------------------------------

    def generate_diagnosis(self, system_prompt: str, user_prompt: str) -> str:
        """
        Return a deterministic JSON diagnosis string based on user_prompt keywords.

        Parameters
        ----------
        system_prompt:
            Ignored in mock mode (accepted to satisfy the interface).
        user_prompt:
            Evidence Package text used for keyword-based fixture selection.

        Returns
        -------
        str
            A JSON-serialised diagnosis fixture string.
        """
        fixture = self._select_fixture(user_prompt)
        raw_json = json.dumps(fixture, indent=2)

        logger.info(
            "MockAdapter returning fixture diagnosis | root_cause='%s' | confidence=%.2f",
            fixture["root_cause"],
            fixture["confidence"],
        )
        logger.debug("MockAdapter response payload:\n%s", raw_json)
        return raw_json

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_fixture(user_prompt: str) -> dict:
        """
        Select the most relevant diagnosis fixture based on keyword priority.

        Parameters
        ----------
        user_prompt:
            The serialised Evidence Package user prompt.

        Returns
        -------
        dict
            A copy of the selected diagnosis fixture dictionary.
        """
        prompt_lower = user_prompt.lower()

        if any(kw in prompt_lower for kw in ("database", "postgres", " db ", "pool", "connection pool")):
            return dict(_MOCK_DATABASE_DIAGNOSIS)

        if any(kw in prompt_lower for kw in ("auth", "token", "oauth", "401", "unauthorized")):
            return dict(_MOCK_AUTH_DIAGNOSIS)

        if any(kw in prompt_lower for kw in ("network", "tcp", "socket", "connection reset", "timeout")):
            return dict(_MOCK_NETWORK_DIAGNOSIS)

        if any(kw in prompt_lower for kw in ("memory", "heap", "oom", "out of memory", "leak")):
            return dict(_MOCK_MEMORY_DIAGNOSIS)

        return dict(_MOCK_GENERAL_DIAGNOSIS)
