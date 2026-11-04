---
description: Project mission, scope boundaries, repo structure, development commands, and documentation navigation.
globs: ["**/*"]
alwaysApply: true
---

# Project Context & Engineering Standards

## 1. Mission & Objective
AdAtlas is an intelligence and prospecting platform designed to discover businesses actively advertising on Meta (Facebook & Instagram) across five priority Indian metropolitan markets:
- Mumbai (Maharashtra)
- Delhi (National Capital Territory)
- Jaipur (Rajasthan)
- Kolkata (West Bengal)
- Bengaluru (Karnataka)

The system extracts verified public business contact information (phone, email, WhatsApp, website, socials) from advertiser-published web properties and provides comparative scoring to evaluate market vitality.

## 2. Non-Goals & Strict Boundaries
- **No Commercial Ad Spend Estimates:** Meta does not disclose spend or impression figures for commercial ads outside the EU. City comparisons MUST use proxy metrics (density, growth, ad longevity, creative cadence, contact reachability). Never invent, model, or project ad spend for commercial campaigns.
- **No Direct Outreach Capabilities:** AdAtlas is strictly an analytical intelligence and list-building research tool. It does not send emails, trigger WhatsApp messages, dispatch SMS, or dial numbers.
- **No Logged-In Scraping:** The platform never logs into Facebook/Instagram personal accounts or crawls private groups, closed communities, or personal user profiles.
- **No Political Candidate or Individual Enrichment:** Political/issue campaigns (Adapter A) are ingested for market context, but candidates and individuals running non-commercial ads are never enriched with personal contact data.
- **No Asset Mirroring:** Do not store or redistribute raw creative video/audio assets. Persist ad copy, metadata, an internal low-res thumbnail, and canonical Meta permalinks only.

## 3. Repository Architecture
```
admeta/
├── .agents/
│   ├── rules/          # System rules enforced across tool invocations
│   └── workflows/      # Operational playbooks for routine engineering tasks
├── backend/            # FastAPI, Celery workers, pipeline modules
│   └── app/
│       ├── api/        # REST endpoints and RFC 9457 error handlers
│       ├── collectors/ # AdSourceAdapter implementations (Adapter A, B, C)
│       ├── core/       # Config, SSRF guard, security, logging
│       ├── db/         # SQLAlchemy 2.0 async models and Alembic migrations
│       ├── pipeline/   # Normalization, geo attribution, enrichment, classification
│       ├── services/   # Business logic, city scoring, exports, suppression
│       └── workers/    # Celery tasks and queue routing
├── data/
│   └── seed/           # Reference tables, PIN maps, category taxonomy YAML
├── docs/               # Authoritative specifications, ADRs, runbooks
│   ├── ADR/            # Architecture Decision Records (0001..0014)
│   └── RUNBOOKS/       # Operational incident response and maintenance guides
├── frontend/           # Next.js App Router, Tailwind, shadcn/ui, TanStack
├── infra/              # Docker Compose, Caddyfile, network isolation configs
└── scripts/            # Database seeding, evaluation benchmarks, utility scripts
```

## 4. Standard Operational Commands
- `make up`: Start all local Docker services (PostgreSQL 16, Redis 7, MinIO, Mailpit, API, Worker, Beat, Frontend).
- `make down`: Halt containers and preserve volume state.
- `make check`: Master quality gate (format, lint, type-check, unit tests, contract tests, security linters, gitleaks).
- `make test`: Run backend and frontend test suites against recorded fixtures.
- `make migrate`: Apply pending Alembic schema revisions.
- `make seed`: Populate reference data (cities, aliases, PIN codes, categories).

## 5. Source of Truth
The documentation suite located under `docs/` is the formal project contract. Whenever requirements, schema designs, or pipeline logic diverge from code, the documentation must be referenced or formally revised via an ADR in `docs/ADR/`.

