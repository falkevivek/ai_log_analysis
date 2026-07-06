"""
Local Llama LLM Adapter — Barclays Office Placeholder
======================================================
Implements ``BaseLlmAdapter`` for the future Barclays on-premises
Meta-Llama-3.1-8B-Instruct deployment.

Current Status
--------------
This adapter compiles and is wired into the LlmManager, but the actual
HTTP request to the local inference server is intentionally left as a
placeholder (see ``_execute_request``).

When the office LLM endpoint becomes available, only the
``_execute_request`` method needs to be implemented.  No other file in
the platform requires modification.

Environment Variables (Future)
------------------------------
LOCAL_LLM_ENDPOINT : Full URL of the chat-completions REST endpoint.
LOCAL_LLM_MODEL    : Model name sent in the request payload.
LOCAL_LLM_TIMEOUT  : HTTP request timeout in seconds.

Isolation Contract
------------------
ONLY this module may contain local-Llama HTTP client code.
No other engine, manager, or orchestrator component may reference
local-LLM internals directly.
"""

from __future__ import annotations

import logging

from app.engines.llm_reasoning.adapters.base import BaseLlmAdapter
from app.exceptions.custom_exceptions import ServiceUnavailableError

logger = logging.getLogger(
    "ai_analysis_engine.engines.llm_reasoning.adapters.local_llama"
)


class LocalLlamaAdapter(BaseLlmAdapter):
    """
    LLM Adapter for the Barclays on-premises Meta-Llama inference server.

    The adapter is fully wired and compile-correct.  The request execution
    body is a placeholder pending network access to the Barclays office LLM.

    Parameters
    ----------
    endpoint_url:
        Full REST URL of the local inference server's chat-completions route.
        Example: ``http://llama-server.barclays.internal:8080/v1/chat/completions``
    model:
        Model identifier sent in the request payload.
    timeout_seconds:
        HTTP request timeout.  Increase for slow office-network inference.
    """

    def __init__(
        self,
        endpoint_url: str,
        model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct",
        timeout_seconds: float = 30.0,
    ) -> None:
        # TODO (Barclays migration):
        #   Validate endpoint_url is reachable during startup health-check.
        #   Raise ConfigurationError if the server cannot be contacted.

        self._endpoint_url = endpoint_url
        self._model = model
        self._timeout_seconds = timeout_seconds

        logger.info(
            "LocalLlamaAdapter initialised | endpoint=%s | model=%s",
            self._endpoint_url,
            self._model,
        )

    # ------------------------------------------------------------------
    # BaseLlmAdapter implementation
    # ------------------------------------------------------------------

    def generate_diagnosis(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send prompts to the local Llama inference server and return the
        raw text response.

        Parameters
        ----------
        system_prompt:
            Model role and output format instructions.
        user_prompt:
            Serialised Evidence Package.

        Returns
        -------
        str
            Raw text content from the model response.

        Raises
        ------
        ServiceUnavailableError
            If the local inference server is unreachable or returns an error.
        """
        logger.info(
            "Dispatching diagnosis request to Local Llama | endpoint=%s | model=%s",
            self._endpoint_url,
            self._model,
        )

        payload = self._build_request_payload(system_prompt, user_prompt)
        raw_text = self._execute_request(payload)

        logger.debug(
            "Local Llama response received | chars=%d | preview=%s",
            len(raw_text),
            raw_text[:120],
        )
        return raw_text

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_request_payload(
        self, system_prompt: str, user_prompt: str
    ) -> dict:
        """
        Construct the OpenAI-compatible chat-completions request payload.

        TODO (Barclays migration):
            Adjust the payload structure if the Barclays Llama server uses
            a non-standard request schema (e.g. different field names,
            additional required headers, or a proprietary envelope format).
        """
        return {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

    def _build_request_headers(self) -> dict[str, str]:
        """
        Construct HTTP headers for the local inference server request.

        TODO (Barclays migration):
            Add authentication headers here.  Options include:
            - Bearer token:  ``"Authorization": f"Bearer {token}"``
            - API key header: ``"X-API-Key": api_key``
            - mTLS client certificate (configure on the httpx.Client instead)

            Read credentials from environment variables only — never
            hardcode secrets in this method.
        """
        return {
            "Content-Type": "application/json",
            # TODO: add auth header when Barclays endpoint credentials are provided
        }

    def _execute_request(self, payload: dict) -> str:
        """
        Perform the HTTP POST to the local Llama inference endpoint.

        TODO (Barclays migration):
            Replace the ``raise NotImplementedError`` below with the actual
            httpx (or requests) HTTP call.  Reference implementation:

            import httpx
            headers = self._build_request_headers()
            with httpx.Client(timeout=self._timeout_seconds) as client:
                response = client.post(
                    self._endpoint_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                resp_json = response.json()
                return resp_json["choices"][0]["message"]["content"]

            Wrap the call in a try/except and raise ServiceUnavailableError
            on network failure or non-200 HTTP status codes.
        """
        # Placeholder — remove this block when implementing the real request
        raise ServiceUnavailableError(
            message=(
                "LocalLlamaAdapter._execute_request is not yet implemented. "
                "This adapter is a Barclays office placeholder. "
                "Set LLM_PROVIDER=mock or LLM_PROVIDER=gemini for development."
            ),
            detail={
                "adapter": "LocalLlamaAdapter",
                "endpoint": self._endpoint_url,
                "migration_guide": "See docs/LLM_SWITCH_GUIDE.md",
            },
        )
