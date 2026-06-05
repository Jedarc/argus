.PHONY: up dev down build migrate migration shell test lint format logs setup

# ── Setup (first time) ───────────────────────────────────────────────────────
setup:
	@test -f .env || (cp .env.example .env && echo "✓ .env created — edit it before running 'make up'")

# ── Production ───────────────────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build --no-cache

# ── Development (hot reload) ─────────────────────────────────────────────────
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# ── Database ─────────────────────────────────────────────────────────────────
# Migrations run automatically on 'make up' via the API entrypoint.
# Use these targets to generate or run migrations manually.
migrate:
	docker compose exec api alembic -c api/alembic.ini upgrade head

migration:
	@test -n "$(name)" || (echo "Usage: make migration name=<description>" && exit 1)
	docker compose exec api alembic -c api/alembic.ini revision --autogenerate -m "$(name)"

# ── Shell ────────────────────────────────────────────────────────────────────
shell:
	docker compose exec api bash

# ── Tests ────────────────────────────────────────────────────────────────────
test:
	docker compose exec api pytest tests/ -v

# ── Lint / Format ────────────────────────────────────────────────────────────
lint:
	docker compose exec api ruff check src/api/
	docker compose exec api ruff format --check src/api/

format:
	docker compose exec api ruff format src/api/

# ── Logs ─────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f api worker
