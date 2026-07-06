# Enterprise Intelligent Incident Diagnosis Platform
### AI Analysis Engine — v1.0.0

> An internal Barclays engineering platform that transforms raw application logs into structured, explainable AI-driven incident diagnoses.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [LLM Architecture](#llm-architecture)
- [Folder Structure](#folder-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Configuration Reference](#configuration-reference)
- [LLM Provider Switching](#llm-provider-switching)
- [Future Modules](#future-modules)
- [Contributing](#contributing)

---

## Overview

The **AI Analysis Engine** is the core intelligence layer of the platform. It accepts raw frontend and backend logs, progressively enriches them through a pipeline of analysis engines, and produces a structured diagnosis that tells engineers:

- **What** happened (Root Cause)
- **Why** it happened (Evidence)
- **How confident** we are (Confidence Score)
- **What to do** about it (Recommendation)

### The Diagnosis Pipeline

```
Raw Logs
   ↓
Observation Engine    → extracts structured observations
   ↓
Event Engine          → groups observations into events
   ↓
Timeline Engine       → builds execution timeline
   ↓
Incident Engine       → identifies incidents within timeline
   ↓
Evidence Engine       → gathers supporting evidence
   ↓
Context Engine        → enriches with project/historical knowledge
   ↓
Reasoning Engine      → drives LLM reasoning over evidence
   ↓
Confidence Engine     → scores diagnosis confidence
   ↓
Recommendation Engine → generates actionable fix recommendations
   ↓
Structured Diagnosis  ← the output
```

> **Current Status**: Foundation phase. The pipeline structure is in place. Engines will be implemented in subsequent sprints.

---

## LLM Architecture

The LLM Integration Layer decouples all business logic from any specific LLM provider.

```
Evidence Package
      ↓
PromptBuilder        ← provider-independent, serialises Evidence to text
      ↓
LlmManager           ← reads LLM_PROVIDER from .env, constructs adapter
      ↓
BaseLlmAdapter       ← abstract interface (one method: generate_diagnosis)
      ↓
┌─────────────────────────────────────────────────┐
│  GeminiAdapter  │  LocalLlamaAdapter  │  MockAdapter  │
│  (Google GenAI) │  (Barclays office)  │  (dev / CI)   │
└─────────────────────────────────────────────────┘
      ↓
ResponseParser       ← provider-independent JSON validation
      ↓
Diagnosis domain object
```

### Provider Isolation Contract

| Rule | Enforcement |
|---|---|
| Only `GeminiAdapter` may import `google.genai` | Module-level import guard |
| Only `LocalLlamaAdapter` may contain Llama HTTP client code | No other file references it |
| Only `LlmManager` reads `LLM_PROVIDER` | All other modules receive `BaseLlmAdapter` |
| `LlmReasoningEngine` depends on the interface, not concretions | Constructor injection |

### Running with Gemini

```dotenv
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-key...
GEMINI_MODEL=gemini-2.0-flash
```

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Running with Mock (Default — No API Key Needed)

```dotenv
# .env
LLM_PROVIDER=mock
```

```bash
uvicorn app.main:app --reload
```

### Future Local Llama Support (Barclays Office)

```dotenv
# .env  (office PC)
LLM_PROVIDER=local_llama
LOCAL_LLM_ENDPOINT=http://llama-server.barclays.internal:8080/v1/chat/completions
LOCAL_LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
```

Implement `_execute_request` in `local_llama_adapter.py`. No other file changes.
See [`docs/LLM_SWITCH_GUIDE.md`](docs/LLM_SWITCH_GUIDE.md) for the full migration guide.

---

## Architecture

The platform follows **Clean Architecture** with strict layer separation:

```
┌─────────────────────────────────────────────┐
│                   API Layer                  │  FastAPI routers, request validation
├─────────────────────────────────────────────┤
│                Service Layer                 │  Business logic orchestration
├─────────────────────────────────────────────┤
│                Engine Layer                  │  Analysis pipeline engines (plug-and-play)
├─────────────────────────────────────────────┤
│              Repository Layer                │  Data access (SQLAlchemy)
├─────────────────────────────────────────────┤
│              Infrastructure Layer            │  Database, logging, config
└─────────────────────────────────────────────┘
```

**Key principles:**
- Every module has a single responsibility
- Dependencies flow inward — outer layers depend on inner layers, never the reverse
- All engines are independently injectable via FastAPI `Depends`
- LLM receives structured evidence, not raw logs

---

## Folder Structure

```
ai-analysis-engine/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── health.py          # Health, version, status endpoints
│   │
│   ├── config/
│   │   └── settings.py            # Pydantic-settings configuration
│   │
│   ├── core/
│   │   └── logging.py             # Centralised logging setup
│   │
│   ├── database/
│   │   ├── base.py                # SQLAlchemy Base + TimestampMixin
│   │   └── session.py             # Async engine, session factory, Depends
│   │
│   ├── models/                    # ORM models (added per sprint)
│   ├── schemas/
│   │   └── base.py                # BaseResponse, SuccessResponse, ErrorResponse, HealthResponse
│   │
│   ├── repository/                # Data-access layer (added per sprint)
│   ├── services/                  # Business logic (added per sprint)
│   │
│   ├── engines/                   # Analysis pipeline engines (added per sprint)
│   │   # Future: observation.py, event.py, timeline.py, incident.py
│   │   # Future: evidence.py, context.py, reasoning.py, confidence.py
│   │
│   ├── prompts/                   # LLM prompt templates (added per sprint)
│   │
│   ├── utils/
│   │   ├── date_utils.py          # Timezone-aware datetime helpers
│   │   ├── json_utils.py          # Platform JSON encoder/decoder
│   │   └── logger_utils.py        # Logger factory
│   │
│   ├── middleware/
│   │   ├── request_id.py          # X-Request-ID injection
│   │   └── request_logging.py     # Structured access logging
│   │
│   ├── exceptions/
│   │   ├── custom_exceptions.py   # Typed exception hierarchy
│   │   └── handlers.py            # Global FastAPI exception handlers
│   │
│   ├── dependencies/
│   │   └── database.py            # DatabaseSession type alias
│   │
│   └── main.py                    # Application composition root
│
├── tests/
│   ├── conftest.py                # Shared fixtures
│   ├── test_health_api.py         # Health endpoint tests
│   ├── test_configuration.py      # Settings tests
│   └── test_database.py           # Database layer tests
│
├── docs/                          # Architecture documentation
├── scripts/
│   ├── init_db.py                 # Database connectivity validation
│   └── init_db.sql                # PostgreSQL extension setup
│
├── requirements.txt
├── pyproject.toml                 # pytest, black, isort, mypy, ruff config
├── .env.example
├── Dockerfile                     # Multi-stage production image
├── docker-compose.yml             # Local development stack
└── README.md
```

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.12+ |
| Framework | FastAPI | 0.115.5 |
| ASGI Server | Uvicorn | 0.32.1 |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy (async) | 2.0.36 |
| Async Driver | asyncpg | 0.30.0 |
| Migrations | Alembic | 1.14.0 |
| Validation | Pydantic v2 | 2.9.2 |
| Configuration | pydantic-settings | 2.6.1 |
| LLM (Dev) | Google GenAI SDK | ≥1.19.0 |
| LLM (Office) | Local Meta-Llama (httpx) | — |
| HTTP Client | httpx | ≥0.28.0 |
| Testing | pytest + pytest-asyncio | 8.3.4 |
| Containerisation | Docker + Compose | — |

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16 (or Docker)
- Git

### Local Setup (Without Docker)

```bash
# 1. Clone and enter the project
cd ai-analysis-engine

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Initialise database
python scripts/init_db.py

# 6. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Local Setup (With Docker)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env — set DB_PASSWORD at minimum

# 2. Start all services
docker compose up -d

# 3. Check logs
docker compose logs -f api

# 4. Verify health
curl http://localhost:8000/api/v1/health
```

### Verify Installation

```bash
# Liveness probe
curl http://localhost:8000/api/v1/status

# Full health check
curl http://localhost:8000/api/v1/health | python -m json.tool

# Version info
curl http://localhost:8000/api/v1/version | python -m json.tool

# Interactive API docs
open http://localhost:8000/docs
```

---

## Development Workflow

### Running Tests

```bash
# All tests (unit only — no live DB required)
pytest

# Exclude integration tests explicitly
pytest -m "not integration"

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health_api.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Integration tests (requires live PostgreSQL)
pytest -m integration
```

### Code Quality

```bash
# Format
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
ruff check app/ tests/

# Type check
mypy app/
```

### Adding a New Engine

1. Create `app/engines/<engine_name>.py`
2. Define an interface/protocol in `app/engines/<engine_name>.py`
3. Add the concrete implementation
4. Register as a FastAPI dependency in `app/dependencies/`
5. Mount to the appropriate service in `app/services/`
6. Add tests in `tests/`

---

## API Reference

### Foundation Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/status` | Liveness probe | None |
| `GET` | `/api/v1/health` | Full health + component status | None |
| `GET` | `/api/v1/version` | Version and environment info | None |

### Response Envelope

All responses use a consistent JSON envelope:

**Success:**
```json
{
  "success": true,
  "timestamp": "2025-01-15T14:30:00+00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "...",
  "data": { }
}
```

**Error:**
```json
{
  "success": false,
  "timestamp": "2025-01-15T14:30:00+00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "Human-readable description",
  "detail": null,
  "path": "/api/v1/example"
}
```

---

## LLM Provider Switching

Changing the active LLM provider requires **only `.env` changes** — zero code modifications.

| Environment | `LLM_PROVIDER` | Additional vars needed |
|---|---|---|
| Local development (offline) | `mock` | None |
| Local development (AI responses) | `gemini` | `GEMINI_API_KEY` |
| Barclays Office (no internet) | `local_llama` | `LOCAL_LLM_ENDPOINT` |

### Full Environment Variable Reference

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `mock` | Active LLM provider |
| `GEMINI_API_KEY` | _(empty)_ | Google GenAI API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `LOCAL_LLM_ENDPOINT` | _(empty)_ | Barclays Llama server URL |
| `LOCAL_LLM_MODEL` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | Model in request payload |
| `LOCAL_LLM_TIMEOUT` | `30.0` | HTTP timeout seconds |
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Root log level |
| `API_PREFIX` | `/api/v1` | URL prefix for all v1 routes |

See [`docs/LLM_SWITCH_GUIDE.md`](docs/LLM_SWITCH_GUIDE.md) for the complete operational guide.

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` / `testing` |
| `DEBUG` | `false` | Enable debug mode (never `true` in production) |
| `DB_HOST` | `localhost` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `ai_analysis_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | _(required)_ | Database password |
| `DB_POOL_SIZE` | `10` | Connection pool size |
| `LOG_LEVEL` | `INFO` | Root log level |
| `LOG_FILE_ENABLED` | `true` | Enable rotating log file |
| `LOG_FILE_PATH` | `logs/app.log` | Log file location |

See [`.env.example`](.env.example) for the complete list including LLM and AWS placeholders.

---

## Future Modules

| Sprint | Module | Status |
|---|---|---|
| Foundation | Project setup, DB, Health API | ✅ **Complete** |
| Sprint 2 | Observation Engine | ✅ **Complete** |
| Sprint 3 | Event + Timeline Engine | ✅ **Complete** |
| Sprint 4 | Incident + Evidence Engine | ✅ **Complete** |
| Sprint 5 | Context + Knowledge Base | ✅ **Complete** |
| Sprint 6 | LLM Integration Layer (Gemini + Mock + LocalLlama) | ✅ **Complete** |
| Sprint 7 | Recommendation Engine | ✅ **Complete** |
| Sprint 8 | Frontend SDK integration | 🔜 Planned |
| Sprint 9 | Backend SDK integration | 🔜 Planned |
| Sprint 10 | AWS CloudWatch integration | 🔜 Planned |

---

## Contributing

This is an internal Barclays platform. All contributions must pass:

1. `pytest` – all tests green
2. `mypy app/` – zero type errors
3. `ruff check app/` – zero lint violations
4. `black --check app/` – code formatted
5. Peer review by a senior engineer before merge

---

*Enterprise Intelligent Incident Diagnosis Platform — Barclays Engineering Platform Team*
