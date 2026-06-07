# Argus — Claude Code Context

Self-hosted OSINT platform. FastAPI + Celery + PostgreSQL + React. Single-user, password-protected.

---

## Current Status

Scaffolding complete. Core infrastructure implemented. Feature endpoints pending.

**Implemented (ready to use):**
- `src/api/security.py` — JWT + bcrypt + `require_authenticated_user` dependency
- `src/api/validators.py` — input sanitization + SSRF protection
- `src/api/resilience.py` — `@with_retry`, `@with_timeout`, `is_retryable_error`
- `src/api/logging_config.py` — structlog, JSON in prod, colored in DEBUG
- `src/api/models/` — all 6 SQLAlchemy models (system_config, investigation, target, job, result, module_config)
- `src/api/modules/base.py` — `BaseModule` + `ModuleResult` contracts
- `src/api/modules/*.py` — 11 module stubs (`raise NotImplementedError`)
- `src/api/routers/auth.py` — endpoint stubs with Pydantic validation wired
- Docker Compose, Dockerfiles, Alembic, React scaffold

**Build order for next session:**
1. Alembic initial migration (`make migration name=initial-schema`)
2. Implement auth endpoints (`routers/auth.py` — all raise NotImplementedError)
3. Implement modules one by one (start with `hudsonrock`, `sherlock`)
4. Celery task (`tasks.py` — skeleton commented in the file)
5. API routers (`investigations.py`, `modules.py`, `ws.py`)
6. React UI pages (`/setup`, `/login`, `Dashboard`, `Investigation`, `Settings`)
7. Dockerfiles polish (currently functional but minimal)

---

## Non-Negotiable Rules

1. **Every router on `app` requires `dependencies=[Depends(require_authenticated_user)]`** — except `/health` and `/auth/*`
2. **Every target value from user input passes through `sanitize_target_value(type, value)`** before use
3. **Subprocess calls use list-form args** — never f-string into a shell command
4. **`password_hash` and `api_key_encrypted` never appear in any Pydantic response schema**
5. **`ALLOWED_ORIGINS` must be set explicitly in `.env`** — default is for local dev only

---

## Key Patterns

```python
# Protect a router
app.include_router(router, prefix="/api/v1", dependencies=[Depends(require_authenticated_user)])

# Validate user input
from api.validators import sanitize_target_value
clean = sanitize_target_value("email", raw_email)

# Resilient module
from api.resilience import with_retry, with_timeout
@with_timeout(seconds=60)
@with_retry(max_attempts=3, wait_min_seconds=1, wait_max_seconds=30)
def run(self, target_value, api_key=None): ...

# Structured log
from api.logging_config import get_logger
log = get_logger(__name__).bind(module="hudsonrock", target=target_value)
log.info("module_started")
log.error("module_failed", error=str(exc), exc_info=True)

# WebSocket auth (token passed as ?token=<jwt>)
from api.security import require_authenticated_user_ws
require_authenticated_user_ws(token=token, database_session=session)
```

---

## Auth Flow

1. First request → `403 {"setup_required": true}` if no password set → UI redirects to `/setup`
2. `POST /auth/setup` → bcrypt hash stored in `system_config` → endpoint returns 404 forever after
3. `POST /auth/login` → JWT in httpOnly + Secure + SameSite=Strict cookie
4. Password change → `token_version` incremented → all sessions immediately invalid

---

## Data Model

```
system_config   (key, value)                      ← password_hash, token_version
investigations  (id, name, notes, status)
targets         (id, investigation_id, type, value)
jobs            (id, investigation_id, target_id, module, status, started_at, finished_at, error)
results         (id, job_id, module, target_type, target_value, raw_json, found, cached, timestamp)
module_configs  (module, enabled, api_key_encrypted, cache_ttl_seconds)
```

Cache key: `(module, target_type, target_value)` — index on `results` table.

---

## Commit Convention

Phased commits — one unit per commit. Never bundle unrelated changes.

```
<type>(<scope>): <description>
Types:  feat | fix | refactor | test | docs | chore
Scopes: api | worker | ui | db | modules | docker | docs
```

Phases per feature: `db` model → `api` business logic → `api` endpoint → `ui` → `test` → `docs`

---

## Commands

```bash
make dev                          # hot reload
make test                         # pytest
make lint                         # ruff check + format check
make migration name=<description> # generate migration
make migrate                      # apply migrations
make shell                        # bash into api container
```

---

## Environment

Required: `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`
Optional modules: `HIBP_API_KEY`, `SHODAN_API_KEY`, `HUNTER_API_KEY`, `VT_API_KEY`
Celery uses Redis DB `/1` (broker) and `/2` (results) — isolated from app data on `/0`.

→ Full docs: [docs/FEATURES.md](docs/FEATURES.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/MODULES.md](docs/MODULES.md)
