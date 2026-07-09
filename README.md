# Enterprise Intelligent Incident Diagnosis Platform
### AI Analysis Engine — v1.0.0

> An internal Barclays engineering platform that transforms raw application logs into structured, explainable AI-driven incident diagnoses.


Yes bro. I think we should first finalize the **engineering roadmap** before writing any Copilot prompt. That roadmap becomes the contract for the whole project.

I would slightly refine the plan we've discussed so that:

* each milestone is independently testable,
* each milestone adds real functionality,
* each milestone changes a limited number of files,
* each milestone can be frozen before moving forward,
* future modules (Historical Incident Lookup, RAG, PostgreSQL, etc.) can be added without redesign.

Here is the roadmap I would use.

---

# Development Roadmap

## Phase 0 — Foundation (Freeze Point 1)

Goal:

Create the project skeleton.

Deliverables

* FastAPI
* Configuration
* Logging
* Exception Handling
* Middleware
* Storage Abstraction
* In-Memory Repository
* Domain Base Models
* Health APIs
* Swagger
* Dependency Injection

Output

```text
Running Backend
```

Verification

```
Backend Starts

↓

Swagger

↓

Health API

↓

Version API
```

Freeze.

---

# Phase 1 — Log Processing Engine

Goal

Convert raw logs into standardized logs.

Pipeline

```
Raw Logs

↓

Reader

↓

Parser

↓

Cleaning

↓

Validation

↓

Normalization

↓

Standardization

↓

Deduplication

↓

Standardized Logs
```

Output

```
Standardized Logs
```

Verification

Input logs

↓

Output standardized logs

Freeze.

---

# Phase 2 — Observation Engine

Goal

Generate observations from standardized logs.

Pipeline

```
Standardized Logs

↓

Observation Engine

↓

Observations
```

Responsibilities

* Detect severity
* Detect affected service
* Detect component
* Detect metadata
* Detect anomalies

Verification

Logs

↓

Observations

Freeze.

---

# Phase 3 — Event Intelligence

Goal

Convert observations into meaningful events.

Pipeline

```
Observations

↓

Grouping

↓

Correlation

↓

Event Detection

↓

Events
```

Freeze.

---

# Phase 4 — Timeline Intelligence

Goal

Build execution timeline.

Pipeline

```
Events

↓

Sorting

↓

Flow Matching

↓

Gap Detection

↓

Timeline
```

Freeze.

---

# Phase 5 — Incident Builder

Goal

Generate Incident.

Pipeline

```
Timeline

↓

Incident Builder

↓

Incident
```

Freeze.

---

# Phase 6 — Context Enrichment

Goal

Collect project context.

Sources

* Project Metadata
* Services
* Components
* APIs
* Configurations
* Known Errors

Output

```
Context
```

Freeze.

---

# Phase 7 — Evidence Builder

Goal

Prepare complete evidence package.

Pipeline

```
Incident

+

Timeline

+

Events

+

Observations

+

Context

↓

Evidence Package
```

Freeze.

---

# Reserved Extension Point

NOT IMPLEMENT NOW

```
Evidence

↓

Historical Incident Lookup

↓

LLM
```

Remember

Future

* JSON Search
* PostgreSQL
* Vector DB
* RAG

No implementation now.

---

# Phase 8 — LLM Integration

Pipeline

```
Evidence

↓

Prompt Builder

↓

LLM Manager

↓

Local Llama Adapter

↓

Response Parser

↓

Diagnosis
```

Freeze.

---

# Phase 9 — Recommendation Engine

Pipeline

```
Diagnosis

↓

Recommendation Engine

↓

Recommendations
```

Freeze.

---

# Phase 10 — AI Analysis Orchestrator

Connect every module.

Pipeline

```
Raw Logs

↓

Log Processing

↓

Observation

↓

Event

↓

Timeline

↓

Incident

↓

Context

↓

Evidence

↓

LLM

↓

Recommendation

↓

Pipeline Result
```

Freeze.

---

# Phase 11 — Backend API

Goal

Expose

```
POST /analyze
```

Only

Controller

↓

AIAnalysisOrchestrator

No engine calls.

Freeze.

---

# Phase 12 — Frontend Foundation

Goal

React setup

↓

Backend connection

↓

Axios

↓

Routing

↓

Theme

Freeze.

---

# Phase 13 — Enterprise Dashboard

Goal

Professional UI

Features

* Upload
* Demo Scenarios
* Pipeline Progress
* Timeline
* Diagnosis
* Recommendation
* Evidence
* Statistics
* Raw Logs

Freeze.

---

# Phase 14 — Final Integration

Goal

Complete product.

```
Upload

↓

Backend

↓

LLM

↓

Frontend

↓

Results
```

Project Complete.

---

# Every Phase Follows the Same Cycle

```
Read Architecture

↓

Implement

↓

Compile

↓

Integration Check

↓

Manual Test

↓

Regression Test

↓

Freeze

↓

Next Phase
```

---

# Prompt Series

I recommend **14 implementation prompts** (plus one master context prompt). That keeps each prompt focused and minimizes the risk of Copilot introducing inconsistencies.

Because each prompt will be several pages long—with architecture context, contracts, file lists, coding standards, testing steps, and integration rules—it isn't practical to include all 15 prompts in one response without sacrificing quality or exceeding the response limit.

The sequence would be:

1. Master Project Context (reused at the start of each new Copilot session)
2. Foundation
3. Log Processing
4. Observation Engine
5. Event Intelligence
6. Timeline Intelligence
7. Incident Builder
8. Context Enrichment
9. Evidence Builder
10. LLM Integration
11. Recommendation Engine
12. AI Analysis Orchestrator + Backend API
13. Frontend Foundation
14. Enterprise Dashboard + Final Integration

This structure gives you a stable, testable milestone after every phase and aligns with the architecture we've already finalized.

I recommend we generate these prompts one by one, ensuring each is polished and internally consistent, rather than trying to compress the entire development guide into a single oversized response. That approach will produce a much higher-quality result and be far more useful when you're working with Microsoft Copilot.








Write production-quality code.

Follow SOLID Principles.

Follow Clean Architecture.

Every module must have one responsibility.

Avoid tightly coupled classes.

Avoid God Objects.

Avoid duplicated logic.

Prefer composition over inheritance.

Use dependency injection.

Every function should perform one task.

Meaningful naming only.

No magic numbers.

No hardcoded configuration.

Use Type Hints.

Use Docstrings.

Meaningful Logging.

Professional Exception Handling.

No TODO placeholders.

Code should be understandable by another engineer after two years.

Prefer readability over cleverness.

Never redesign previous modules.

Never modify frozen interfaces unless absolutely necessary.

If a frozen file must change,
explain why before modifying it.




You are a Principal Software Engineer, Enterprise AI Architect, Senior Python Developer, and System Designer.

You are helping develop an Enterprise Intelligent Incident Diagnosis Platform.

This project is intended to be production-quality and maintainable by multiple engineers.

Treat this prompt as the permanent architecture contract for the project.

==========================================================
IMPORTANT
==========================================================

Do NOT implement any AI Analysis modules.

Do NOT implement Observation Engine.

Do NOT implement Event Intelligence.

Do NOT implement Timeline Intelligence.

Do NOT implement Incident Builder.

Do NOT implement Context Enrichment.

Do NOT implement Evidence Builder.

Do NOT implement LLM.

Do NOT implement Recommendation Engine.

Do NOT implement Frontend.

Today's task is ONLY to establish a strong project foundation.

==========================================================
PROJECT VISION
==========================================================

The platform analyzes frontend and backend logs to identify the most probable root cause of production incidents using deterministic analysis and LLM reasoning.

The complete future pipeline is

Raw Logs

↓

Log Processing

↓

Observation Engine

↓

Event Intelligence

↓

Timeline Intelligence

↓

Incident Builder

↓

Context Enrichment

↓

Evidence Builder

↓

(Historical Incident Lookup - Reserved for Future)

↓

LLM Reasoning

↓

Recommendation Engine

↓

Pipeline Result

↓

Frontend Dashboard

The Historical Incident Lookup module is NOT implemented now.

The architecture should allow inserting this module later without modifying existing modules.

==========================================================
ARCHITECTURE PRINCIPLES
==========================================================

Follow Clean Architecture.

Follow SOLID Principles.

Low Coupling.

High Cohesion.

Each module must have one responsibility.

Never create God Classes.

Never tightly couple two modules.

Business logic must never exist inside API controllers.

Future modules should be plug-and-play.

Prefer composition over inheritance.

Design every component so that future improvements require extension instead of modification.

==========================================================
TECH STACK
==========================================================

Python 3.12

FastAPI

Pydantic

Uvicorn

Python Logging

Dependency Injection

In-Memory Repository

Future PostgreSQL support

Future Local LLM support

==========================================================
DATABASE STRATEGY
==========================================================

For the MVP use ONLY an in-memory repository.

Do NOT implement PostgreSQL.

However, every storage operation must be abstracted so PostgreSQL can replace the repository later with minimal changes.

==========================================================
LLM STRATEGY
==========================================================

The LLM must NEVER be called directly from business logic.

Future LLM calls must go through

LLM Manager

↓

Adapter Interface

↓

Specific Adapter

Current Future Adapter

Local Llama

Future

Gemini

OpenAI

Azure OpenAI

Mock

The business logic must never know which LLM is being used.

==========================================================
PROJECT STRUCTURE
==========================================================

Design a clean enterprise folder structure.

Only create folders that are required now.

Avoid empty placeholder folders.

Avoid unnecessary abstraction.

==========================================================
PROJECT DOCUMENTATION
==========================================================

Create the following project documents.

PROJECT_CONTEXT.md

ARCHITECTURE.md

CODING_STANDARDS.md

ROADMAP.md

README.md

These documents become the permanent source of truth for the project.

PROJECT_CONTEXT.md should contain

• Project Vision

• Complete Pipeline

• Module Responsibilities

• Future Reserved Modules

• Freeze Points

• Development Rules

ARCHITECTURE.md should explain

• Folder Structure

• Layer Responsibilities

• Dependency Rules

• Data Flow

• Extension Points

CODING_STANDARDS.md should contain

Naming conventions

Logging guidelines

Exception handling

SOLID

PEP8

Documentation expectations

ROADMAP.md should describe

Development phases

Freeze points

Future enhancements

Historical Incident Lookup

Feedback Engine

Project Onboarding

Frontend

==========================================================
APPLICATION FOUNDATION
==========================================================

Implement only

Application Factory

Configuration

Logging

Exception Handling

Dependency Injection

Middleware

Health API

Version API

Application Startup

Do NOT implement any business APIs.

==========================================================
LOGGING
==========================================================

Create centralized logging.

Support

INFO

WARNING

ERROR

DEBUG

Every module should use the centralized logger.

==========================================================
MIDDLEWARE
==========================================================

Create

Request ID Middleware

Request Logging Middleware

Global Exception Middleware

==========================================================
CONFIGURATION
==========================================================

Use environment variables.

Do not hardcode configuration.

Support

Application Name

Environment

Logging Level

Future LLM Provider

Future Database Provider

==========================================================
QUALITY CONTRACT
==========================================================

Write production-quality code.

Every class should have one responsibility.

Every function should have one responsibility.

Avoid unnecessary abstractions.

Avoid premature optimization.

Avoid duplicated logic.

Use meaningful naming.

Use type hints.

Use docstrings.

Professional logging.

Professional exception handling.

Readable code is more important than clever code.

==========================================================
INTEGRATION CONTRACT
==========================================================

The project must compile successfully.

Swagger should load.

Health endpoint should work.

Version endpoint should work.

Future modules must be able to plug into this foundation without redesign.

==========================================================
OUTPUT
==========================================================

After implementation provide

1. Folder Structure

2. Files Created

3. Design Decisions

4. Future Extension Points

5. Manual Verification Steps

6. Acceptance Criteria

7. Freeze Point Declaration

==========================================================
STOP CONDITION
==========================================================

Stop after the project foundation is complete.

Do NOT implement any AI analysis modules.

Wait for the next implementation prompt.




You are a Principal Software Engineer, Enterprise AI Architect, Senior Python Developer, and Domain-Driven Design (DDD) Expert.

The project foundation has already been completed.

Treat all existing project foundation code as frozen.

Do NOT redesign the architecture.

Do NOT modify the application startup.

Do NOT modify middleware.

Do NOT modify logging.

Do NOT modify configuration.

Today's task is ONLY to define the domain language of the AI Analysis Platform.

==========================================================
OBJECTIVE
==========================================================

Design all domain models that will be shared across every future module.

These models become permanent contracts.

Future modules must consume these models instead of creating their own.

Think carefully before designing them because changing these contracts later should be avoided.

==========================================================
CURRENT PIPELINE
==========================================================

Raw Logs

↓

Log Processing

↓

Observation Engine

↓

Event Intelligence

↓

Timeline Intelligence

↓

Incident Builder

↓

Context Enrichment

↓

Evidence Builder

↓

(Historical Incident Lookup - Reserved)

↓

LLM Reasoning

↓

Recommendation Engine

↓

Pipeline Result

==========================================================
IMPLEMENT ONLY DOMAIN CONTRACTS
==========================================================

Implement the following domain models.

RawLog

NormalizedLog

Observation

Event

Timeline

Incident

Context

Evidence

Diagnosis

Recommendation

PipelineStatistics

PipelineResult

Each model should represent a real business object.

Do NOT add business logic.

Models should contain only

Validation

Serialization

Utility properties where appropriate.

==========================================================
MODEL DESIGN REQUIREMENTS
==========================================================

Each model should

Use Pydantic.

Use Type Hints.

Use Field descriptions.

Provide clear documentation.

Support future extension.

Avoid unnecessary nesting.

Avoid duplicate fields.

==========================================================
RAW LOG
==========================================================

Represents the incoming log before processing.

==========================================================
NORMALIZED LOG
==========================================================

Represents the standardized log after preprocessing.

Fields may include

Timestamp

Severity

Service

Component

Source

Message

Thread

Metadata

==========================================================
OBSERVATION
==========================================================

Represents an observation extracted from normalized logs.

Examples

High Database Latency

Repeated Authentication Failure

API Timeout

==========================================================
EVENT
==========================================================

Represents a correlated business or technical event.

Contains

Event ID

Related Observations

Start Time

End Time

Affected Services

Affected Components

Severity

==========================================================
TIMELINE
==========================================================

Represents chronological execution.

Contains

Events

Duration

Execution Flow

Missing Steps

Summary

==========================================================
INCIDENT
==========================================================

Represents the detected production incident.

Contains

Summary

Severity

Impact

Timeline Reference

Affected Services

Affected Components

==========================================================
CONTEXT
==========================================================

Represents contextual information.

Contains

Project Metadata

Environment

Configuration Metadata

Known Errors

Historical References (placeholder)

Component Metadata

API Metadata

==========================================================
EVIDENCE
==========================================================

Represents the package sent to the LLM.

Contains

Incident

Timeline

Context

Events

Observations

Relevant Logs

Detected Patterns

Confidence Signals

==========================================================
DIAGNOSIS
==========================================================

Represents the LLM diagnosis.

Contains

Root Cause

Reasoning

Confidence

Affected Services

Affected Components

==========================================================
RECOMMENDATION
==========================================================

Contains

Immediate Actions

Investigation Steps

Long-Term Prevention

Priority

==========================================================
PIPELINE STATISTICS
==========================================================

Contains

Execution Time

LLM Time

Logs Processed

Observations Generated

Events Generated

==========================================================
PIPELINE RESULT
==========================================================

This becomes the single object returned by

POST /api/v1/analyze

Contains

Session ID

Timeline

Incident

Context

Evidence

Diagnosis

Recommendation

Statistics

==========================================================
QUALITY REQUIREMENTS
==========================================================

Follow Domain-Driven Design.

Avoid Anemic Models becoming business logic containers.

These models represent business entities only.

Do not implement processing methods.

Keep validation lightweight.

Future modules should rely on these contracts without modification.

==========================================================
INTEGRATION REQUIREMENTS
==========================================================

Do not modify the project foundation.

Do not modify APIs.

Do not modify middleware.

Create only the files required for the domain layer.

==========================================================
MANUAL VERIFICATION
==========================================================

Verify

All models instantiate successfully.

Validation works.

Serialization works.

Importing models produces no circular dependencies.

==========================================================
REGRESSION CHECK
==========================================================

Ensure

Application still starts.

Swagger still loads.

Health endpoint still works.

==========================================================
OUTPUT
==========================================================

Provide

1. Files Created

2. Domain Models

3. Design Decisions

4. Validation Strategy

5. Manual Testing Steps

6. Acceptance Criteria

7. Freeze Point Declaration

==========================================================
STOP CONDITION
==========================================================

Stop after the domain contracts are complete.

Do NOT implement preprocessing.

Do NOT implement AI engines.

Do NOT implement business logic.

Wait for the next implementation prompt.











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
