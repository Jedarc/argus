.PHONY: up dev down build migrate shell test lint

# Production
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

# Development (hot reload)
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Database
migrate:
	docker compose exec api alembic upgrade head

migration:
	docker compose exec api alembic revision --autogenerate -m "$(name)"

# Shell
shell:
	docker compose exec api bash

# Tests
test:
	docker compose exec api pytest tests/ -v

# Lint
lint:
	docker compose exec api ruff check src/api/
	docker compose exec api ruff format --check src/api/

format:
	docker compose exec api ruff format src/api/

# Logs
logs:
	docker compose logs -f api worker
