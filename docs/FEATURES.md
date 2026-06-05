# Argus — Features

> *Nothing escapes the many eyes.*

## Investigations

- Create named investigations with one or multiple targets
- Each target has a declared type: `username`, `email`, `phone`, `ip`, `domain`, `name`
- Multiple targets per investigation (e.g. username + email for the same subject)
- Investigation status lifecycle: `pending` → `running` → `completed` / `partial`
- Free-text notes per investigation
- Event timeline ordered by discovery timestamp

## OSINT Modules

- Modular architecture: each data source is an independent, self-contained module
- Modules can be enabled or disabled globally or per investigation
- Modules requiring an API key remain disabled until the key is configured
- Each module declares which target types it accepts (e.g. `holehe` accepts `email`)
- Background execution via job queue (Celery + Redis)
- Real-time progress streamed over WebSocket (per-module progress bar in the UI)
- Configurable timeout per module
- Automatic retry on transient failures (max 2 attempts)

### Phase 1 — No API key required

| Module | Input | Returns |
|--------|-------|---------|
| `hudsonrock` | username, email | Infostealer infections, exposed logins, IPs |
| `sherlock` | username | Profiles found across 400+ platforms |
| `whatsmyname` | username | Profiles via WhatsMyName JSON database |
| `holehe` | email | Services where the email is registered |
| `ipinfo` | ip | Geolocation, ASN, carrier |
| `whois` | domain | Registrant, dates, nameservers |
| `subfinder` | domain | Passively discovered subdomains |

### Phase 2 — API key required

| Module | Input | Returns |
|--------|-------|---------|
| `hibp` | email | Have I Been Pwned breach list |
| `shodan` | ip, domain | Exposed services, banners, CVEs |
| `hunter_io` | domain | Corporate emails associated with a domain |
| `virustotal` | ip, domain, hash | Reputation score, detections, reports |

## Cache and Result Reuse

- All results are persisted with `(module, target_type, target_value, timestamp)` as the cache key
- Before running a module, Argus checks for a valid cached result (configurable TTL per module)
- Default TTLs: HudsonRock 7 days · Sherlock 1 day · WhatsMyName 1 day · WHOIS 3 days
- `force_refresh` flag bypasses cache and forces re-execution
- Results are automatically shared across investigations that query the same target

## Dashboard and Visualization

- Overview page listing all investigations with status badges and timestamps
- Investigation detail page with a panel per module:
  - Progress bar while the module runs
  - Result badge: `hit` / `not found` / `skipped` / `error` / `cached`
  - Inline result expansion
- Entity graph: targets and discovered entities as nodes, relationships as edges
- Chronological timeline of all findings within an investigation
- Automatic flagging of high-value findings (infostealer hits, known breaches, etc.)

## Module Settings

- Settings panel listing all registered modules
- Per-module status indicator: `active` / `inactive` / `awaiting key`
- Secure API key input (stored AES-encrypted in the database, never returned to the frontend)
- "Test Connection" button per module
- Per-module cache TTL override

## Export

- Export full investigation results as JSON
- Export investigation summary as Markdown
- (Phase 2) Export structured PDF report

## Infrastructure

- Single command to start the full stack: `docker compose up`
  - Services: `api`, `worker`, `ui`, `postgres`, `redis`
- API keys and secrets managed via `.env` (see `.env.example`)
- Health checks on all services
- Persistent PostgreSQL volume
- Hot reload in development (`--reload` for FastAPI, Vite dev server for the UI)
