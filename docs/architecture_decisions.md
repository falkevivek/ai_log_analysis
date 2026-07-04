# Architecture Decision Records
# ================================
# Enterprise Intelligent Incident Diagnosis Platform — AI Analysis Engine

## ADR-001: Python 3.12 + FastAPI + Async SQLAlchemy

**Status**: Accepted

**Context**: Need a production-grade API framework that supports async I/O for
database and future LLM calls without blocking Uvicorn worker threads.

**Decision**: FastAPI with asyncpg driver and SQLAlchemy 2.0 async engine.

**Consequences**: All route handlers and repository methods must be `async def`.
Alembic (migrations) still requires a sync engine (psycopg2) which is also included.

---

## ADR-002: Pydantic v2 Settings

**Status**: Accepted

**Context**: Configuration must be environment-variable driven with type
validation and zero hard-coded values.

**Decision**: `pydantic-settings` BaseSettings with sub-settings groups
(DatabaseSettings, LoggingSettings, LLMSettings, AWSSettings).

**Consequences**: All settings are validated at startup. Missing required values
raise a clear `ValidationError`, not a cryptic `KeyError` at runtime.

---

## ADR-003: Consistent JSON Response Envelope

**Status**: Accepted

**Context**: API clients (future Frontend SDK, dashboard) must be able to
parse all responses without conditional logic.

**Decision**: Every response — success or error — wraps in `BaseResponse`
with `success: bool`, `timestamp`, `request_id`.

**Consequences**: Even 404s return a JSON body. HTTP status codes remain
accurate but are no longer the sole error communication mechanism.

---

## ADR-004: Typed Exception Hierarchy

**Status**: Accepted

**Context**: Exception handlers need to distinguish infrastructure errors from
domain errors without parsing message strings.

**Decision**: All custom exceptions inherit `AppBaseException` which carries
`error_code`, `http_status_code`, and `detail`.

**Consequences**: Adding a new exception type is trivial. The global handler
catches everything in one `except AppBaseException` clause.

---

## ADR-005: LLM Receives Structured Evidence, Not Raw Logs

**Status**: Accepted

**Context**: Sending thousands of raw log lines to an LLM is expensive,
slow, and produces low-quality reasoning due to noise.

**Decision**: The analysis pipeline progressively enriches logs through
Observation → Event → Timeline → Incident → Evidence stages before the LLM
ever sees any data.

**Consequences**: Each stage must be independently testable. The LLM prompt
is deterministic and auditable. Diagnosis quality improves as each engine matures.
