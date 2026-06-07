# Argus

> *Nothing escapes the many eyes.*

Self-hosted OSINT platform. Runs investigations against usernames, emails, IPs, and domains by aggregating multiple intelligence sources in parallel — with background processing, persistent caching, and a modular API-key system.

---

## Quick Start

```bash
git clone git@github.com:Jedarc/argus.git && cd argus
cp .env.example .env
```

Edit `.env` — two values are required:

```env
POSTGRES_PASSWORD=<strong-password>
JWT_SECRET_KEY=<run: python3 -c "import secrets; print(secrets.token_hex(32))">
```

```bash
docker compose up -d
```

Open `http://localhost:3000`, complete the one-time password setup, and you're in. Migrations run automatically on startup. Optional module keys (`HIBP_API_KEY`, `SHODAN_API_KEY`, etc.) can be added later in the Settings panel.

---

## Modules

**Phase 1 — no API key required:** `hudsonrock` · `sherlock` · `whatsmyname` · `holehe` · `ipinfo` · `whois` · `subfinder`

**Phase 2 — optional API key:** `hibp` · `shodan` · `hunter_io` · `virustotal`

→ [docs/MODULES.md](docs/MODULES.md)

---

## Stack

FastAPI + Celery + Redis · PostgreSQL · React + Vite + Tailwind · Docker Compose

→ [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Development

```bash
make dev        # hot reload (api + worker + ui)
make test       # pytest
make lint       # ruff
make migration name=<description>   # generate alembic migration
make shell      # bash into api container
```

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. All CI checks (lint, tests, docker build) must pass.

## License · Disclaimer

MIT — see [LICENSE](LICENSE). This tool is for **authorized security research only**. See [DISCLAIMER.md](DISCLAIMER.md).
