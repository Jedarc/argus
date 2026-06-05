# Argus — Architecture

## Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + Vite + Tailwind + shadcn/ui | Production-ready component library, consistent dark-mode design system |
| Backend | FastAPI (Python 3.12) | OSINT ecosystem is Python-native — zero impedance with subprocess tools |
| Task Queue | Celery + Redis | Reliable background jobs with trackable progress |
| Cache / Broker | Redis | Job queue broker + in-memory result cache |
| Database | PostgreSQL 16 | Structured result storage, relational queries |
| ORM | SQLAlchemy + Alembic | Type-safe queries, clean migrations |
| Real-time | WebSocket (FastAPI native) | Module progress streamed to the UI without polling |
| Containerization | Docker + Docker Compose | One command to start the full environment |

## Services

```
argus/
├── api/       FastAPI — REST endpoints + WebSocket hub
├── worker/    Celery workers — module execution
├── ui/        React — Vite dev server or nginx in production
├── postgres/  PostgreSQL 16
└── redis/     Redis 7
```

## Investigation Flow

```
User creates investigation + targets
             │
             ▼
API resolves applicable modules per target type
             │
             ▼
Jobs enqueued in Redis (one job per module × target)
             │
    ┌────────┴────────┐
    │                 │
Cache hit?        Cache miss?
    │                 │
Return DB         Celery worker picks up job
result            │
                  ├── HTTP module  → calls external API
                  └── CLI module   → subprocess (Sherlock, Holehe, Subfinder…)
                             │
                    Normalized result → saved to PostgreSQL
                             │
                    WebSocket event → UI updates progress in real time
```

## Data Model (simplified)

```sql
investigations   -- id, name, notes, status, created_at, updated_at
targets          -- id, investigation_id, type, value
jobs             -- id, investigation_id, target_id, module, status, started_at, finished_at, error
results          -- id, job_id, module, target_type, target_value, raw_json, found, cached, timestamp
module_configs   -- module, enabled, api_key_encrypted, cache_ttl_seconds
```

## Module Interface

Every module implements the same contract:

```python
class BaseModule:
    name: str
    accepted_target_types: list[str]
    requires_api_key: bool

    def run(self, target_value: str, api_key: str | None) -> ModuleResult: ...
```

Adding a new module requires only:
1. Creating `src/api/modules/<name>.py` extending `BaseModule`
2. Registering it in `src/api/modules/__init__.py`

The system auto-discovers registered modules and exposes them in the settings panel.

## Security

- API keys stored with Fernet symmetric encryption — never in plaintext
- Keys are never returned to the frontend (`configured: true/false` only)
- `.env` excluded from version control (`.gitignore`)
- All containers run as non-root (`USER app`)
- Input validated at API boundaries (Pydantic models)

## Directory Structure

```
argus/
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── tasks.py
│   │   ├── routers/
│   │   │   ├── investigations.py
│   │   │   ├── modules.py
│   │   │   └── ws.py
│   │   ├── modules/
│   │   │   ├── base.py
│   │   │   ├── hudsonrock.py
│   │   │   ├── sherlock.py
│   │   │   ├── whatsmyname.py
│   │   │   ├── holehe.py
│   │   │   ├── ipinfo.py
│   │   │   ├── whois_module.py
│   │   │   ├── subfinder.py
│   │   │   ├── hibp.py
│   │   │   ├── shodan.py
│   │   │   ├── hunter_io.py
│   │   │   └── virustotal.py
│   │   └── models/
│   │       ├── investigation.py
│   │       ├── target.py
│   │       ├── job.py
│   │       ├── result.py
│   │       └── module_config.py
│   └── ui/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Investigation.tsx
│       │   │   └── Settings.tsx
│       │   └── components/
│       ├── index.html
│       ├── vite.config.ts
│       └── package.json
├── tests/
├── docs/
│   ├── FEATURES.md
│   ├── ARCHITECTURE.md
│   └── MODULES.md
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── ui.Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── Makefile
├── CLAUDE.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── README.md
```
