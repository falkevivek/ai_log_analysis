# Manual Testing Guide — Freeze Point 1

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| pip | latest |

No external services required (no PostgreSQL, no AWS, no LLM keys).

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected startup output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO     | ai_analysis_engine.main | Starting Enterprise Intelligent Incident Diagnosis Platform v1.0.0 (development)
INFO     | ai_analysis_engine.main | Platform ready — storage: in-memory
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Test Cases

### TC-01 — Liveness Probe

**URL:** `GET http://localhost:8000/api/v1/status`

**Expected Status:** `200 OK`

**Expected Body:**
```json
{
  "status": "ok"
}
```

**Acceptance Criteria:**
- [ ] Returns HTTP 200
- [ ] Body contains `{"status": "ok"}`
- [ ] Response time < 100ms

---

### TC-02 — Version Endpoint

**URL:** `GET http://localhost:8000/api/v1/version`

**Expected Status:** `200 OK`

**Expected Body:**
```json
{
  "success": true,
  "timestamp": "2026-07-04T09:00:00Z",
  "request_id": null,
  "message": "Version information retrieved successfully.",
  "data": {
    "app_name": "Enterprise Intelligent Incident Diagnosis Platform",
    "version": "1.0.0",
    "environment": "development",
    "python_version": "3.10.x",
    "uptime_seconds": 5.12
  }
}
```

**Acceptance Criteria:**
- [ ] Returns HTTP 200
- [ ] `success` is `true`
- [ ] `data.app_name` is non-empty
- [ ] `data.version` is `"1.0.0"`
- [ ] `data.environment` is `"development"`
- [ ] `data.uptime_seconds` is a positive number

---

### TC-03 — Full Health Check

**URL:** `GET http://localhost:8000/api/v1/health`

**Expected Status:** `200 OK`

**Expected Body:**
```json
{
  "success": true,
  "timestamp": "2026-07-04T09:00:00Z",
  "request_id": null,
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "storage": "in-memory",
    "storage_records": "0"
  },
  "uptime_seconds": 5.12
}
```

**Acceptance Criteria:**
- [ ] Returns HTTP 200
- [ ] `status` is `"healthy"`
- [ ] `components.storage` is `"in-memory"`
- [ ] `uptime_seconds` is a positive number
- [ ] No PostgreSQL connection required

---

### TC-04 — 404 Error Envelope

**URL:** `GET http://localhost:8000/api/v1/does-not-exist`

**Expected Status:** `404 Not Found`

**Expected Body:**
```json
{
  "success": false,
  "timestamp": "2026-07-04T09:00:00Z",
  "request_id": null,
  "error_code": "HTTP_404",
  "message": "Not Found",
  "detail": null,
  "path": "/api/v1/does-not-exist"
}
```

**Acceptance Criteria:**
- [ ] Returns HTTP 404
- [ ] `success` is `false`
- [ ] `error_code` is `"HTTP_404"`
- [ ] `path` matches the requested URL

---

### TC-05 — Request ID Propagation

**Request:**
```
GET http://localhost:8000/api/v1/status
X-Request-ID: barclays-test-001
```

**Acceptance Criteria:**
- [ ] Response headers contain `x-request-id: barclays-test-001`
- [ ] ID is echoed back unchanged

**Without header:**
- [ ] Response headers contain a generated UUID in `x-request-id`

---

### TC-06 — Interactive API Documentation

**URL:** `http://localhost:8000/docs`

**Acceptance Criteria:**
- [ ] Swagger UI loads without errors
- [ ] All 3 endpoints are listed: `/health`, `/version`, `/status`
- [ ] "Try it out" works for each endpoint

**URL:** `http://localhost:8000/redoc`
- [ ] ReDoc documentation loads

---

## How to Run Tests

### Option A — Browser
Open each URL above directly in your browser.

### Option B — curl
```bash
# TC-01
curl -s http://localhost:8000/api/v1/status

# TC-02
curl -s http://localhost:8000/api/v1/version | python -m json.tool

# TC-03
curl -s http://localhost:8000/api/v1/health | python -m json.tool

# TC-04
curl -s http://localhost:8000/api/v1/does-not-exist | python -m json.tool

# TC-05
curl -s -H "X-Request-ID: barclays-test-001" http://localhost:8000/api/v1/status -v 2>&1 | grep -i "x-request-id"
```

### Option C — Python one-liners
```bash
python -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:8000/api/v1/health'); print(json.dumps(json.loads(r.read()), indent=2))"
```

---

## Acceptance Criteria — Freeze Point 1

The implementation is accepted when ALL of the following are true:

| # | Criterion |
|---|---|
| 1 | Server starts cleanly with zero errors and zero external dependencies |
| 2 | `GET /api/v1/status` returns `{"status": "ok"}` HTTP 200 |
| 3 | `GET /api/v1/version` returns structured version info HTTP 200 |
| 4 | `GET /api/v1/health` reports `storage: in-memory` and `status: healthy` HTTP 200 |
| 5 | Any unknown route returns a consistent `ErrorResponse` JSON envelope HTTP 404 |
| 6 | `X-Request-ID` header is echoed back on every response |
| 7 | Swagger UI loads at `/docs` |
| 8 | ReDoc loads at `/redoc` |
| 9 | In-memory store is accessible to route handlers via `request.app.state.store` |
| 10 | No PostgreSQL, no AWS, no LLM credentials required to run |

---

## Transfer Checklist — Freeze Point 1

Before handing off to the next engineer:

- [ ] All TC-01 through TC-06 pass manually
- [ ] All Acceptance Criteria above are met
- [ ] `.env` file is created from `.env.example`
- [ ] `requirements.txt` installs cleanly into a fresh virtualenv
- [ ] `app/storage/memory.py` interface is documented (migration path clear)
- [ ] No empty placeholder directories exist in `app/`
- [ ] `app/main.py` PostgreSQL migration comment is present
- [ ] Swagger UI documents all endpoints correctly
