---
description: Conventions and architectural rules for Python backend development, FastAPI, SQLAlchemy 2.0, Celery, and Pydantic v2.
globs: ["backend/**/*"]
alwaysApply: false
---

# Python Backend Engineering Standards

## 1. Environment & Tooling
- **Python Version:** 3.12+ pinned.
- **Package Management:** `uv` for lightning-fast, reproducible dependency locking (`uv.lock`).
- **Code Hygiene:** `ruff` for linting and formatting (replaces Black, Flake8, isort). Target line length: 100 characters.
- **Type Checking:** Strict type checking with `mypy` or `pyright`. All functions, methods, parameters, and return types must carry explicit type annotations.

## 2. API Design (FastAPI & Pydantic v2)
- **Base Route:** All API endpoints must be prefixed with `/api/v1`.
- **Schemas:** Use Pydantic v2 `BaseModel` with strict validation. Config dicts must specify `extra = "forbid"` on API request/response models, while raw collector ingestion models may use `extra = "allow"`.
- **Error Format:** Errors must conform to RFC 9457 `application/problem+json` (`type`, `title`, `status`, `detail`, `instance`, `request_id`).
- **Request Tracing:** Every incoming request must generate or propagate an `X-Request-Id` header, logged via `structlog` contextvars.
- **Pagination:** Search and list endpoints must employ keyset/cursor-based pagination (`cursor`, `limit`). Standard default limit: 20, maximum limit: 100.
- **Data Protection:** Contact values returned in standard search or summary endpoints must be masked (e.g., `+91 98•••• ••21`). Full unmasked contact records are restricted to authenticated `/reveal` operations with rate-limiting and audit logging.

## 3. Database & ORM (SQLAlchemy 2.0 Async + Alembic)
- **Async Only:** Use `AsyncSession` with `asyncpg`. Never block the event loop with synchronous queries.
- **Parameterized Queries:** All database interactions must use SQLAlchemy query expressions or parameterized statements. Raw string concatenation or unsanitized SQL text is strictly forbidden (SEC-04).
- **Migration Discipline:** Schema migrations must follow an expand-migrate-contract sequence. Never perform single-step destructive drops or non-backward-compatible column renames in production.
- **Optimistic Concurrency:** State-mutating tables (`advertisers`, `scrape_jobs`) must implement a `version: int` column for optimistic locking (SRCH-09).
- **Trigram & FTS:** Leverage PostgreSQL extensions (`pg_trgm`, `unaccent`, `citext`) for text search and alias resolution. Use GiST or GIN trigram indexes for fuzzy advertiser matching.

## 4. Asynchronous Pipeline & Workers (Celery + Redis)
- **Queue Segregation:** Direct tasks to dedicated queues:
  - `q.collect` — Ingestion runs and adapter executions
  - `q.normalize` — Text sanitization and payload parsing
  - `q.geo` — Multi-signal spatial attribution scoring
  - `q.enrich` — SSRF-safe landing page crawling and contact extraction
  - `q.classify` — Category taxonomy and risk tagging
  - `q.analytics` — Daily metric aggregations and city scoring
  - `q.export` — CSV/XLSX generation
  - `q.default` — Routine background tasks
- **Idempotency:** Every task must be idempotent. Use unique database constraints, `ON CONFLICT DO UPDATE`, or Redis distributed locks with key expiry.
- **Poison Message Handling:** Cap retries with exponential backoff and jitter. Unrecoverable failures must route to the `dead_letters` table for diagnostic inspection and operator replay.
- **Backpressure:** Celery Beat schedulers must inspect queue depth before enqueueing new extraction batches.

## 5. Security & Privacy Defaults
- **SSRF Guard:** Never issue external HTTP calls using naked `httpx` or `requests`. Always use `core.ssrf_guard.PoliteFetcher`.
- **Log Sanitation:** Never write unmasked contact values (phones, emails) or secret API tokens to log handlers. Use SHA-256 hashes or truncated prefixes (`hash[:8]`).

