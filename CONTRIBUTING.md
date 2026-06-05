# Contributing to Argus

Thank you for your interest in contributing. This document covers how to get started, the branching model, and commit conventions.

---

## Getting Started

1. Fork the repository and clone your fork
2. Copy `.env.example` to `.env`
3. Start the development environment: `make dev`
4. Create a feature branch from `main`: `git checkout -b feat/your-feature`

---

## Commit Convention

This project uses **phased, semantic commits**. Each commit must map to a single, well-defined unit of work. Never bundle unrelated changes into one commit.

### Format

```
<type>(<scope>): <short description>
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or module |
| `fix` | Bug fix |
| `refactor` | Code change with no behavior change |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build, CI, dependencies, tooling |
| `style` | Formatting only (no logic change) |

### Scopes

Use the affected area as the scope: `api`, `worker`, `ui`, `db`, `modules`, `docker`, `docs`.

### Examples

```
feat(modules): add hudsonrock username module
feat(api): add investigation creation endpoint
feat(ui): add per-module progress bar component
fix(worker): handle infostealer timeout gracefully
refactor(modules): extract base HTTP fetch into BaseModule
test(modules): add hudsonrock unit tests
docs(modules): document holehe module parameters
chore(docker): add healthcheck to postgres service
```

---

## Phased Development

Features should be committed in logical phases that can be reviewed and reverted independently:

1. **Data model** — database schema / migration
2. **Business logic** — service / module implementation
3. **API layer** — endpoints, serialization
4. **UI** — components, pages
5. **Tests** — unit and integration coverage
6. **Docs** — update relevant documentation

Avoid squashing these phases into one commit. A reviewer should be able to understand
what changed at each layer by reading the git log.

---

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- All commits in the PR must follow the convention above
- Include a brief description of what changed and why
- Reference any related issues: `Closes #123`
- Make sure `make test` passes before opening a PR

---

## Adding a New Module

See the "Adding a New Module" section in [docs/MODULES.md](docs/MODULES.md).

Each module addition should be one PR with commits following this sequence:
1. `feat(modules): scaffold <name> module class`
2. `feat(modules): implement <name> run logic`
3. `test(modules): add <name> module tests`
4. `docs(modules): document <name> module`

---

## Code Style

- Follow PEP 8 for Python; run `ruff` before committing
- No abbreviations in identifiers (`request` not `req`, `database` not `db`)
- Prefer descriptive, long names over short ambiguous ones
- Apply early returns (guard clauses) to reduce nesting
- No hardcoded secrets — use environment variables

---

## Reporting Issues

Open a GitHub Issue with:
- A clear title
- Steps to reproduce
- Expected vs. actual behavior
- Environment info (OS, Docker version, Python version)
