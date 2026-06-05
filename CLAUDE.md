# Argus — Claude Code Context

> Read this file first. It contains all architectural decisions and conventions for this project.

## What is Argus?

Argus is an open-source OSINT web platform. It aggregates multiple intelligence sources
(HudsonRock, Sherlock, Holehe, Subfinder, HIBP, Shodan, etc.) into a single interface.
Users create **investigations** with one or more **targets** (username, email, IP, domain, name).
Modules run in background jobs with real-time WebSocket progress and persistent caching.

## Current Status

**Scaffolding complete. Implementation pending.**

The following are fully defined and ready:
- `docs/FEATURES.md` — complete feature spec
- `docs/ARCHITECTURE.md` — stack, data model, directory structure
- `docs/MODULES.md` — all 11 modules documented
- `src/api/modules/base.py` — `BaseModule` and `ModuleResult` contracts
- `src/api/modules/*.py` — all 11 module stubs (raise NotImplementedError)
- `src/api/main.py` — FastAPI app skeleton
- `src/api/database.py` — SQLAlchemy + session setup
- `src/api/tasks.py` — Celery app setup
- `docker-compose.yml` + `docker-compose.dev.yml` + `Makefile`

**What needs to be built next (in order):**
1. SQLAlchemy models (`src/api/models/`) — including `system_config`
2. Alembic migrations (`alembic init`, initial migration)
3. Auth implementation (`src/api/routers/auth.py`) — bcrypt + JWT + cookie
4. `require_authenticated_user` FastAPI dependency
5. Module implementations (`src/api/modules/*.py`)
6. Celery task for module execution (`src/api/tasks.py`)
7. FastAPI routers (`src/api/routers/`)
8. WebSocket progress hub (`src/api/routers/ws.py`)
9. React UI (`src/ui/`) — including `/setup` and `/login` pages
10. Dockerfiles (`docker/`)

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python 3.12) |
| Task Queue | Celery + Redis |
| Database | PostgreSQL 16 + SQLAlchemy + Alembic |
| Real-time | WebSocket (FastAPI native) |
| Frontend | React + Vite + Tailwind + shadcn/ui |
| Containers | Docker + Docker Compose |

## Module System

Each module lives in `src/api/modules/<name>.py` and extends `BaseModule`:

```python
class BaseModule(ABC):
    name: str
    accepted_target_types: list[str]  # "username" | "email" | "ip" | "domain"
    requires_api_key: bool

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult: ...
```

`ModuleResult` has: `found: bool`, `data: dict`, `error: str | None`, `cached: bool`.

All modules are registered in `src/api/modules/__init__.py` as `ALL_MODULES`.

## Authentication

Single-user, password-only. Designed for self-hosted VPS deployments.

**Flow:**
1. First request to any protected route → `403 {"setup_required": true}` if no password is set
2. UI redirects to `/setup` → `POST /auth/setup` stores bcrypt hash in `system_config` → disabled forever after
3. `POST /auth/login {"password": "..."}` → JWT returned as httpOnly + Secure + SameSite=Strict cookie
4. FastAPI dependency `require_authenticated_user` guards all routes except `/health`, `/auth/*`
5. WebSocket auth via `?token=<jwt>` query param (httpOnly cookie not available on WS upgrade)
6. Password change increments `token_version` in `system_config` → all existing tokens immediately invalid

**Key:** `JWT_SECRET_KEY` in `.env` (never hardcode). `JWT_EXPIRY_HOURS` controls session length.

**Files:**
- `src/api/routers/auth.py` — all auth endpoints (stubs, raise NotImplementedError)
- `src/api/models/system_config.py` — stores `password_hash` and `token_version` rows

## Data Model

```
system_config   (key PK, value, updated_at)           ← password_hash, token_version
investigations  (id, name, notes, status, created_at)
targets         (id, investigation_id, type, value)
jobs            (id, investigation_id, target_id, module, status, started_at, finished_at, error)
results         (id, job_id, module, target_type, target_value, raw_json, found, cached, timestamp)
module_configs  (module, enabled, api_key_encrypted, cache_ttl_seconds)
```

Cache key: `(module, target_type, target_value)` — results are reused across investigations.

## Commit Convention

**Phased commits — one logical unit per commit. Never bundle unrelated changes.**

```
<type>(<scope>): <description>

Types:  feat | fix | refactor | test | docs | chore | style
Scopes: api | worker | ui | db | modules | docker | docs
```

Examples:
```
feat(db): add investigation and target models
feat(db): add job and result models with cache index
feat(modules): implement hudsonrock module
feat(api): add POST /investigations endpoint
feat(worker): wire module execution to celery task
feat(ui): add investigation list page
```

Phases per feature: data model → business logic → API layer → UI → tests → docs.

## Security Architecture

### Key files
- `src/api/security.py` — **IMPLEMENTED**: JWT creation/validation, bcrypt helpers, `require_authenticated_user` and `require_authenticated_user_ws` dependencies
- `src/api/validators.py` — **IMPLEMENTED**: `sanitize_target_value()`, `validate_password_strength()`, SSRF-blocking IP list
- `src/api/main.py` — **IMPLEMENTED**: `SecurityHeadersMiddleware`, CORS, rate limiting, OpenAPI gating

### Rules that must never be broken
1. **Every router registered on `app` must use `dependencies=[Depends(require_authenticated_user)]`** except `/health` and `/auth/*`
2. **Every target value from user input must pass through `sanitize_target_value(target_type, value)` before use**
3. **Subprocess calls in modules must use `shlex.quote()` or list-form args** — never f-string into a shell command
4. **`password_hash` and `api_key_encrypted` fields must never appear in any Pydantic response schema**
5. **SSRF**: modules that perform HTTP requests to user-supplied IPs/domains must call `_assert_not_private_ip()` before the request — the validator handles this for stored targets but modules must also guard direct calls
6. **CORS `ALLOWED_ORIGINS` must be set explicitly in `.env`** — the default `http://localhost:3000` is for local dev only

### Auth dependency usage
```python
# Protect an entire router:
app.include_router(router, dependencies=[Depends(require_authenticated_user)])

# Protect a single endpoint:
@router.get("/endpoint", dependencies=[Depends(require_authenticated_user)])

# WebSocket (token passed as ?token=<jwt> query param):
from api.security import require_authenticated_user_ws
require_authenticated_user_ws(token=token, database_session=session)
```

## Code Conventions

- **No abbreviations**: `target_value` not `val`, `database_session` not `db`, `api_key` not `key`
- **Guard clauses** over nested if-else (early return pattern)
- **No comments** unless the WHY is non-obvious
- **No hardcoded secrets** — environment variables only
- API keys stored encrypted (Fernet) — never returned to frontend raw
- All containers run as non-root

## Key Commands

```bash
make dev       # start with hot reload
make migrate   # run alembic upgrade head
make test      # pytest
make lint      # ruff check + format check
make shell     # bash into api container
```

## Environment

Copy `.env.example` to `.env` before starting. Optional module keys:
`HIBP_API_KEY`, `SHODAN_API_KEY`, `HUNTER_API_KEY`, `VT_API_KEY`.

## Important Files

| File | Purpose |
|------|---------|
| `docs/FEATURES.md` | Full feature spec — read before adding features |
| `docs/ARCHITECTURE.md` | Stack decisions and directory layout |
| `docs/MODULES.md` | Each module's inputs, outputs, TTL, dependencies |
| `src/api/modules/base.py` | Module contract — do not change without updating all modules |
| `DISCLAIMER.md` | Legal disclaimer — this is an OSINT security tool |
| `CONTRIBUTING.md` | Commit convention and phased development rules |
