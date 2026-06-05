# Argus

> *Nothing escapes the many eyes.*

Argus is an open-source OSINT platform that aggregates multiple intelligence sources into a single web interface. It runs investigations against usernames, emails, IPs, domains, and names — in parallel, with real-time progress, persistent caching, and a modular plugin system.

---

## Features

- **Modular** — each data source is an independent module; enable or disable per investigation
- **Background processing** — jobs run via Celery with real-time WebSocket progress
- **Smart caching** — results are persisted and reused across investigations (configurable TTL)
- **API key management** — optional modules stay inactive until a key is provided
- **Entity graph** — visualizes relationships between discovered entities
- **Docker-first** — one command to start the full stack

→ See [docs/FEATURES.md](docs/FEATURES.md) for the full feature list.

---

## Modules

### Phase 1 — Free (no API key)

| Module | Input | Source |
|--------|-------|--------|
| `hudsonrock` | username, email | cavalier.hudsonrock.com |
| `sherlock` | username | Sherlock Project |
| `whatsmyname` | username | WebBreacher/WhatsMyName |
| `holehe` | email | megadose/holehe |
| `ipinfo` | ip | ipinfo.io |
| `whois` | domain | python-whois |
| `subfinder` | domain | projectdiscovery/subfinder |

### Phase 2 — Optional (API key required)

| Module | Input | Key |
|--------|-------|-----|
| `hibp` | email | `HIBP_API_KEY` |
| `shodan` | ip, domain | `SHODAN_API_KEY` |
| `hunter_io` | domain | `HUNTER_API_KEY` |
| `virustotal` | ip, domain | `VT_API_KEY` |

→ See [docs/MODULES.md](docs/MODULES.md) for full module documentation.

---

## Quick Start

```bash
git clone https://github.com/Jedarc/argus
cd argus
cp .env.example .env
docker compose up
```

The UI will be available at `http://localhost:3000`.

---

## Development

```bash
# Start all services with hot reload
make dev

# Run database migrations
make migrate

# Run tests
make test

# Open a shell in the API container
make shell
```

---

## Tech Stack

- **Backend:** FastAPI (Python 3.12) + Celery + Redis
- **Frontend:** React + Vite + Tailwind CSS + shadcn/ui
- **Database:** PostgreSQL 16 + SQLAlchemy + Alembic
- **Infrastructure:** Docker + Docker Compose

→ See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture documentation.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to uphold its standards.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Argus is intended for **authorized security research, fraud response, and defensive use only**.
Users are solely responsible for ensuring their use complies with applicable laws (LGPD, GDPR, CFAA, etc.).
The authors accept no liability for misuse. See [DISCLAIMER.md](DISCLAIMER.md) for the full disclaimer.
