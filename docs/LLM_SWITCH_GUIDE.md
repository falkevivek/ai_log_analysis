# LLM Provider Switching Guide

> **Enterprise Intelligent Incident Diagnosis Platform — Barclays Engineering**

This guide explains how to switch between LLM providers. Switching providers
requires **only a `.env` file change** — no business logic, no engine code,
no orchestrator code, and no pipeline code requires modification.

---

## Architecture Recap

```
LlmReasoningEngine
        │
        ▼
   LlmManager          ← reads LLM_PROVIDER from .env
        │
        ▼
BaseLlmAdapter (interface)
        │
   ┌────┴────────────────────────┐
   │             │               │
GeminiAdapter  LocalLlamaAdapter  MockAdapter
(internet)     (Barclays office)  (development)
```

**The isolation guarantee:** No engine above `LlmManager` knows or cares
which concrete adapter is active. Only `LlmManager` reads the `LLM_PROVIDER`
variable. Only the specific adapter file imports the specific SDK.

---

## Current Development Environment (Personal Laptop)

### Using Mock (Default — No API Key Required)

```dotenv
# .env
LLM_PROVIDER=mock
```

- No internet required.
- No API key required.
- Deterministic, keyword-driven responses.
- Safe for CI/CD pipelines.

### Using Gemini (Google GenAI)

**Step 1 — Obtain an API key**

1. Visit [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account.
3. Click **Get API Key → Create API key**.
4. Copy the key (it starts with `AIza...`).

**Step 2 — Update `.env`**

```dotenv
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-key-here...
GEMINI_MODEL=gemini-2.0-flash
```

**Step 3 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 — Start the server**

```bash
uvicorn app.main:app --reload
```

**Step 5 — Verify**

Submit a POST request to `/api/v1/analyse` with sample logs.
The `diagnosis.root_cause` field will contain a Gemini-generated response.

---

## Future Production Environment (Barclays Office PC)

### Switching to Local Llama

**What changes:**

| Item | Development | Barclays Office |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | `local_llama` |
| `GEMINI_API_KEY` | Set | Not needed |
| `LOCAL_LLM_ENDPOINT` | Not needed | Set to internal server URL |
| `LOCAL_LLM_MODEL` | Not needed | `meta-llama/Meta-Llama-3.1-8B-Instruct` |
| Internet required | Yes | **No** |

**Step 1 — Update `.env` on the Barclays office PC**

```dotenv
# .env  (Barclays Office)
LLM_PROVIDER=local_llama
LOCAL_LLM_ENDPOINT=http://llama-server.barclays.internal:8080/v1/chat/completions
LOCAL_LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
LOCAL_LLM_TIMEOUT=30.0
```

**Step 2 — Implement the HTTP request in `LocalLlamaAdapter`**

Open `app/engines/llm_reasoning/adapters/local_llama_adapter.py`.

Find the `_execute_request` method and replace the placeholder `raise`
with the actual HTTP call:

```python
import httpx

def _execute_request(self, payload: dict) -> str:
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
```

Add any Barclays-specific auth headers in `_build_request_headers`.

**Step 3 — Install dependencies**

```bash
pip install -r requirements.txt
```

> `httpx` is already listed in `requirements.txt` — no additional packages needed.

**Step 4 — Start the server**

```bash
uvicorn app.main:app --reload
```

---

## Files That Do NOT Require Modification

When switching providers, the following files are **completely unchanged**:

| File | Reason |
|---|---|
| `app/orchestrator/pipeline.py` | Calls `LlmReasoningEngine` by interface only |
| `app/engines/llm_reasoning/engine.py` | Depends on `BaseLlmAdapter` abstraction |
| `app/engines/llm_reasoning/prompt_builder.py` | Provider-independent prompt assembly |
| `app/engines/llm_reasoning/parser.py` | Provider-independent JSON parsing |
| `app/engines/evidence_builder/` | No LLM awareness |
| `app/engines/recommendation/` | No LLM awareness |
| `app/engines/observation/` | No LLM awareness |
| `app/engines/context_enrichment/` | No LLM awareness |
| `app/schemas/domain.py` | Domain models unchanged |
| `app/api/` | HTTP layer unchanged |
| All other engines | No LLM awareness |

**Business logic remains 100% unchanged when switching LLM providers.**

---

## Configuration Variable Reference

| Variable | Required For | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | Always | `mock` | Active provider: `gemini` / `local_llama` / `mock` |
| `GEMINI_API_KEY` | `gemini` | _(empty)_ | Google GenAI API key |
| `GEMINI_MODEL` | `gemini` | `gemini-2.0-flash` | Gemini model identifier |
| `LOCAL_LLM_ENDPOINT` | `local_llama` | _(empty)_ | Full URL of Barclays Llama server |
| `LOCAL_LLM_MODEL` | `local_llama` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | Model name in request payload |
| `LOCAL_LLM_TIMEOUT` | `local_llama` | `30.0` | HTTP timeout in seconds |

---

## Adding a Third Provider (Future)

To add a new provider (e.g. OpenAI, Azure OpenAI, AWS Bedrock):

1. Create `app/engines/llm_reasoning/adapters/<provider>_adapter.py`
   implementing `BaseLlmAdapter.generate_diagnosis`.
2. Import it in `app/engines/llm_reasoning/llm_manager.py` and add its
   key to `_SUPPORTED_PROVIDERS` and `_build_adapter`.
3. Add required env vars to `app/config/settings.py`.
4. Update `.env.example` and this guide.

**No other file requires modification.**

---

## Transfer Checklist — Moving to Barclays Office PC

- [ ] Copy the entire `ai-analysis-engine/` directory to the office PC
- [ ] Create Python virtual environment: `python -m venv .venv`
- [ ] Activate venv: `.venv\Scripts\activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` from template: `copy .env.example .env`
- [ ] Set `LLM_PROVIDER=local_llama` in `.env`
- [ ] Set `LOCAL_LLM_ENDPOINT` to the Barclays inference server URL
- [ ] Implement `_execute_request` in `local_llama_adapter.py` (one method)
- [ ] Add auth headers in `_build_request_headers` if required
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Verify: POST to `/api/v1/analyse` — confirm `diagnosis` is populated

---

*Enterprise Intelligent Incident Diagnosis Platform — Barclays Engineering Platform Team*
