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
system_config    -- key (PK), value, updated_at          ← password_hash, token_version
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

## Authentication Flow

```
First run (no password configured)
        │
        ▼
Any protected request → 403 {"setup_required": true}
        │
        ▼
UI redirects to /setup
        │
        ▼
POST /auth/setup {"password": "..."}
→ bcrypt hash stored in system_config
→ setup endpoint permanently disabled
        │
        ▼
Subsequent requests
        │
POST /auth/login {"password": "..."}
→ verify bcrypt hash
→ return signed JWT in httpOnly cookie
        │
        ▼
FastAPI dependency require_authenticated_user
→ validates JWT on every protected route
→ WebSocket auth via ?token=<jwt> query param
```

**Token invalidation:** changing the password increments `token_version` in `system_config`.
All existing JWTs embed the version at issue time — mismatches are rejected immediately.

## Security

### Authentication
- Single-user: bcrypt-hashed password in `system_config`, JWT sessions
- JWT in httpOnly + Secure + SameSite=Strict cookie — XSS cannot read it
- Token invalidation via `token_version` counter — no blocklist needed
- `/auth/setup` returns 404 after first use — endpoint effectively disappears
- All credential errors return the same generic message — no user enumeration
- Login rate-limited to 10 attempts/minute per IP (slowapi)

### Input Validation (`src/api/validators.py`)
- Every target value passes through `sanitize_target_value()` before persistence or module execution
- Per-type validation: email regex, IP address parsing, domain RFC 1123, username ASCII printable, phone E.164
- **SSRF protection**: private/loopback/reserved IP ranges (RFC 1918, 1700, 3927, etc.) are blocked for `ip` and `domain` targets
- Domains must not include protocol prefix, paths, or credentials
- Password strength enforced at setup and change-password: min 12 chars, upper + lower + digit + special

### Transport and Headers (`src/api/main.py`)
- CORS restricted to explicit `ALLOWED_ORIGINS` — never wildcard
- Only `GET POST PUT DELETE` methods allowed; `Content-Type` and `Authorization` headers only
- `SecurityHeadersMiddleware` sets on every response:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: no-referrer`
  - `Content-Security-Policy: default-src 'self'` (tightened per resource type)
  - `Cache-Control: no-store, no-cache, must-revalidate, private` — prevents proxies and browsers from caching investigation results
  - `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- OpenAPI docs (`/docs`, `/openapi.json`) disabled in production (`DEBUG=false`)
- Global rate limit: 200 requests/minute per IP across all endpoints

### Data Protection
- Module API keys stored with Fernet symmetric encryption — never returned to the frontend
- `system_config` password hash never included in any API response
- All containers run as non-root (`USER app`)
- `.env` excluded from version control

## Directory Structure

```
argus/
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── tasks.py
│   │   ├── routers/
│   │   │   ├── auth.py
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
│   │       ├── system_config.py
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
