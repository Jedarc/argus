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
1. SQLAlchemy models (`src/api/models/`)
2. Alembic migrations (`alembic init`, initial migration)
3. Module implementations (`src/api/modules/*.py`)
4. Celery task for module execution (`src/api/tasks.py`)
5. FastAPI routers (`src/api/routers/`)
6. WebSocket progress hub (`src/api/routers/ws.py`)
7. React UI (`src/ui/`)
8. Dockerfiles (`docker/`)

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

## Data Model

```
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
