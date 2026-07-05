# AI Analysis Pipeline — Engine Contracts

**Document Type:** Architecture Contract
**Status:** Approved for Implementation
**Foundation:** Freeze Point 1 (Complete) + Domain Contracts (Complete)

---

## Pipeline Flow

```
Raw Log
↓
Log Processing Engine         [app/engines/log_processing/]
↓
Normalized Log
↓
Observation Engine            [app/engines/observation/]
↓
Observation
↓
Event Intelligence Engine     [app/engines/event_intelligence/]
↓
Event
↓
Timeline Intelligence Engine  [app/engines/timeline_intelligence/]
↓
Timeline
↓
Incident Builder              [app/engines/incident_builder/]
↓
Incident
↓
Context Builder               [app/engines/context_builder/]
↓
Context
↓
Evidence Builder              [app/engines/evidence_builder/]
↓
Evidence
↓
LLM Reasoning Engine          [app/engines/llm_reasoning/]
↓
Diagnosis
↓
Recommendation Engine         [app/engines/recommendation/]
↓
Recommendation
↓
Learning Engine               [app/engines/learning/]
↓
(Feedback loop → Log Processing Engine)
```

---

## ENGINE-01 — Log Processing Engine

**Path:** `app/engines/log_processing/`

**Purpose:**
Transform a raw, unstructured `RawLog` into a clean `NormalizedLog`.

**Input:** `RawLog`
**Output:** `NormalizedLog`

**Responsibilities:**
- Parse and validate the incoming `RawLog`
- Normalize timestamps to UTC ISO 8601
- Normalize casing of service, component, log_level
- Extract log template pattern
- Extract variable parameters from log message

**Failure Conditions:**
- Missing `log_id` or `timestamp` → raise `ValidationError`
- Empty `message` → raise `ValidationError`
- Template extraction fails → set `template=None`, continue
- Unknown `log_level` → normalize to `"UNKNOWN"`, do not reject

**Success Criteria:**
- Output passes `NormalizedLog` Pydantic validation
- `timestamp` is UTC ISO 8601
- `log_id` matches the source `RawLog.log_id`

---

## ENGINE-02 — Observation Engine

**Path:** `app/engines/observation/`

**Purpose:**
Detect meaningful patterns and anomalies across a batch of `NormalizedLog` objects. Produce `Observation` records.

**Input:** `list[NormalizedLog]`
**Output:** `list[Observation]`

**Responsibilities:**
- Group logs by service and component
- Detect known error patterns (auth failure, DB timeout, slow API, etc.)
- Assign severity (LOW, MEDIUM, HIGH, CRITICAL) and confidence (0.0–1.0)
- Link observations to triggering logs via `related_logs`

**Failure Conditions:**
- Empty input → return `[]`, do not raise
- No patterns matched → return `[]`, do not raise
- Confidence calculation fails → set `confidence=0.0`, continue

**Success Criteria:**
- Each output passes `Observation` Pydantic validation
- `confidence` strictly within `[0.0, 1.0]`
- `severity` is one of LOW, MEDIUM, HIGH, CRITICAL

---

## ENGINE-03 — Event Intelligence Engine

**Path:** `app/engines/event_intelligence/`

**Purpose:**
Cluster `Observation` objects into discrete logical `Event` groups based on temporal proximity and semantic correlation.

**Input:** `list[Observation]`
**Output:** `list[Event]`

**Responsibilities:**
- Group observations by configurable time window
- Group by component and service correlation
- Assign descriptive `event_name` to each group
- Calculate `start_time` and `end_time` from grouped timestamps

**Failure Conditions:**
- Empty input → return `[]`, do not raise
- Time window failure → assign `start_time = end_time = earliest_timestamp`
- No grouping possible → fall back to single chronological group

**Success Criteria:**
- Each output passes `Event` Pydantic validation
- Every input `Observation` appears in exactly one `Event`
- `start_time` ≤ `end_time` on every `Event`

---

## ENGINE-04 — Timeline Intelligence Engine

**Path:** `app/engines/timeline_intelligence/`

**Purpose:**
Sort and package a list of `Event` objects into a single chronological `Timeline`.

**Input:** `list[Event]`
**Output:** `Timeline`

**Responsibilities:**
- Sort events chronologically by `start_time` ascending
- Calculate `Timeline.start_time` from earliest event
- Calculate `Timeline.end_time` from latest event
- Generate unique `timeline_id`

**Failure Conditions:**
- Empty input → raise `ValidationError`
- `start_time > end_time` after sort → raise `ValidationError`

**Success Criteria:**
- Output passes `Timeline` Pydantic validation
- Events are in ascending `start_time` order
- `Timeline.start_time` == earliest event start

---

## ENGINE-05 — Incident Builder

**Path:** `app/engines/incident_builder/`

**Purpose:**
Wrap a completed `Timeline` into a formal `Incident` record and persist it to storage.

**Input:** `Timeline`
**Output:** `Incident`

**Responsibilities:**
- Extract unique affected services from the timeline
- Generate unique `incident_id`
- Set `status = "ACTIVE"` and `created_at = UTC now`
- Persist to storage via `StorageInterface.save()`

**Failure Conditions:**
- Invalid `Timeline` → raise `ValidationError`
- No services identified → set `affected_services = []`, do not raise
- Storage write fails → raise `StorageError`

**Success Criteria:**
- Output passes `Incident` Pydantic validation
- `Incident` is persisted in storage before being returned
- `status` is `"ACTIVE"` on creation

---

## ENGINE-06 — Context Builder

**Path:** `app/engines/context_builder/`

**Purpose:**
Build project-specific context from settings or the onboarding store (future sprint).

**Input:** `Incident`
**Output:** `Context`

**Responsibilities:**
- Load project context from settings or onboarding service
- Populate `project_name`, `environment`, `application`, `metadata`

**Failure Conditions:**
- Config missing → use settings defaults, do not raise
- `project_name` empty → raise `ConfigurationError`
- Onboarding service unavailable (future) → raise `ServiceUnavailableError`

**Success Criteria:**
- Output passes `Context` Pydantic validation
- `project_name`, `environment`, `application` are non-empty strings

---

## ENGINE-07 — Evidence Builder

**Path:** `app/engines/evidence_builder/`

**Purpose:**
Assemble the complete `Evidence` package from incident data, metrics, history, and known errors. This is the sole input to the LLM.

**Input:** `Incident` + `Context`
**Output:** `Evidence`

**Responsibilities:**
- Collect all `Observation` objects from `Incident.timeline`
- Fetch metrics for the incident time window (future)
- Retrieve historical incident references
- Load known error database matches

**Failure Conditions:**
- `Incident` or `Context` is None → raise `ValidationError`
- Metrics store unavailable → set `metrics={}`, log WARNING, continue
- Historical store unavailable → set `historical_references=[]`, continue
- Known error DB unavailable → set `known_errors=[]`, continue

**Success Criteria:**
- Output passes `Evidence` Pydantic validation
- `observations` and `timeline` match the input `Incident`
- External enrichment failures are logged at WARNING, not raised

---

## ENGINE-08 — LLM Reasoning Engine

**Path:** `app/engines/llm_reasoning/`

**Purpose:**
Submit structured evidence to an LLM provider and parse the response into a `Diagnosis`.

**Input:** `Evidence`
**Output:** `Diagnosis`

**Responsibilities:**
- Construct a structured, deterministic prompt from `Evidence`
- Submit to LLM provider (OpenAI, Bedrock, etc.)
- Retry up to 3 times with exponential backoff on network failure
- Parse and validate LLM response into `Diagnosis`
- Never log LLM API keys

**Failure Conditions:**
- `Evidence` is None → raise `ValidationError`
- LLM unreachable after 3 retries → raise `ServiceUnavailableError`
- Malformed LLM response → raise `ValidationError` with raw response in detail
- Empty `root_cause` → raise `ValidationError`
- `confidence` unparseable → default to `0.5`, log WARNING

**Success Criteria:**
- Output passes `Diagnosis` Pydantic validation
- `confidence` within `[0.0, 1.0]`
- LLM API key never appears in any log output

---

## ENGINE-09 — Recommendation Engine

**Path:** `app/engines/recommendation/`

**Purpose:**
Derive actionable `Recommendation` objects from the `Diagnosis` output, optionally enriched with known playbooks.

**Input:** `Diagnosis`
**Output:** `Recommendation`

**Responsibilities:**
- Derive `immediate_action` from `root_cause`
- Derive `permanent_solution` from `explanation`
- Enrich with playbook store (future)
- Populate `additional_notes` where available

**Failure Conditions:**
- `Diagnosis` is None → raise `ValidationError`
- `root_cause` is empty → raise `ValidationError`
- Playbook store unavailable → skip enrichment, set `additional_notes=None`

**Success Criteria:**
- Output passes `Recommendation` Pydantic validation
- `immediate_action` and `permanent_solution` are non-empty strings

---

## ENGINE-10 — Learning Engine

**Path:** `app/engines/learning/`

**Purpose:**
Persist the complete pipeline outcome as a learning record for future retrieval and similarity matching.

**Input:** `Recommendation` + `Incident` + `Diagnosis`
**Output:** None (side-effect: writes to storage)

**Responsibilities:**
- Persist `Incident`, `Evidence`, `Diagnosis`, `Recommendation` as a linked learning record
- Index `root_cause` for future similarity search
- Populate known error database with newly identified patterns
- Close the feedback loop — data produced here improves future runs

**Failure Conditions:**
- Any input is None → raise `ValidationError`
- Storage write fails → raise `StorageError` — must not be swallowed
- Index update fails → log WARNING, do not raise

**Success Criteria:**
- Learning record is persisted in storage
- `Incident.incident_id` is the primary key of the learning record
- No input objects are mutated

---

## Folder Mapping

```
app/
└── engines/
    ├── log_processing/engine.py      # ENGINE-01
    ├── observation/engine.py         # ENGINE-02
    ├── event_intelligence/engine.py  # ENGINE-03
    ├── timeline_intelligence/engine.py # ENGINE-04
    ├── incident_builder/engine.py    # ENGINE-05
    ├── context_builder/engine.py     # ENGINE-06
    ├── evidence_builder/engine.py    # ENGINE-07
    ├── llm_reasoning/engine.py       # ENGINE-08
    ├── recommendation/engine.py      # ENGINE-09
    └── learning/engine.py            # ENGINE-10
```

---

## Exception Reference

| Exception | Used When |
|---|---|
| `ValidationError` | Data contract violation — required field missing or invalid value |
| `StorageError` | Storage read/write failure |
| `ServiceUnavailableError` | External service (LLM, AWS, Onboarding) unreachable |
| `ConfigurationError` | Missing or invalid application configuration |

All exceptions are defined in `app/exceptions/custom_exceptions.py`.

---

## Future Extension Points

| Extension | Engine | Notes |
|---|---|---|
| Drain3 log parsing | ENGINE-01 | Replace regex with Drain3 parser |
| ML-based observation detection | ENGINE-02 | Replace rules with a trained model |
| PostgreSQL storage | ENGINE-05, ENGINE-10 | Swap `InMemoryStore` — no engine API changes |
| AWS Bedrock LLM | ENGINE-08 | Swap OpenAI client for Boto3 — no contract changes |
| Project Onboarding API | ENGINE-06 | Replace settings defaults with HTTP call |
| CloudWatch metrics | ENGINE-07 | Add metrics client behind `metrics` field |
| Vector DB similarity search | ENGINE-10 | Add pgvector or Pinecone behind `StorageInterface` |
| Async task queue | All engines | Wrap each engine in Celery / AWS SQS |
