# System Architecture — AdAtlas India

## 1. Purpose
Define the system topology, component interactions, data ingestion pipelines, execution queues, storage tiers, and failure recovery mechanisms for the AdAtlas platform.

## 2. Scope
Covers the end-to-end architecture encompassing the Next.js frontend with BFF, FastAPI REST services, Celery worker task queues, PostgreSQL 16 database, Redis 7 cache/broker, MinIO/S3 object storage, and external adapter boundaries.

## 3. Decisions (Link ADRs)
- **ADR-0001:** Multi-Adapter Collection Architecture (Adapter A, B, C).
- **ADR-0004:** Single-VM Containerized Topology in India Region.
- **ADR-0005:** Auth.js Session Management with BFF Signed JWT for FastAPI.
- **ADR-0012:** Modular Monolith with Asynchronous Task Queues over Microservices.
- **ADR-0013:** PostgreSQL Trigram & Full-Text Search First over External Search Clusters.

## 4. Detailed Design

### 4.1 Architectural Principles
1. **Modular Monolith + Asynchronous Workers:** Single unified codebase with clean domain separation (`collectors`, `pipeline`, `services`, `api`). Avoid distributed transaction overhead while isolating long-running extraction workloads in Celery.
2. **Pluggable Edge Adapters:** Every external data ingestion point conforms to a standard Python `Protocol` (`AdSourceAdapter`) with explicit capability declarations and cost estimations.
3. **Raw Payloads as Permanent Source of Truth:** Unmodified source payloads are compressed (zstd) and saved to object storage (`raw_payloads`). Normalized relational tables represent disposable projections re-derivable via `reprocess --from-raw`.
4. **Idempotence and Checkpointing:** Every pipeline stage is idempotent, relying on database-level constraints (`ON CONFLICT DO UPDATE`) and cursor checkpoints.
5. **Inference Provenance:** Algorithmic inferences (geo attribution, contact extraction, categorization) persist source evidence, confidence scores, and model version identifiers.
6. **Fail-Closed Privacy & Compliance:** The suppression registry is evaluated synchronously on both write and read paths.
7. **Strict Budget Boundaries:** Billable external API calls (provider queries, Google Places, LLMs) decrement central budget ledgers and halt automatically upon reaching quota.

### 4.2 System Component Topology

```mermaid
flowchart TD
    subgraph CLIENT["Client Layer"]
        BROWSER["Web Browser (Marketing Team)"]
    end

    subgraph INGRESS["Edge & Web Layer"]
        CADDY["Caddy Reverse Proxy (Auto-TLS)"]
        NEXT["Next.js App Router (BFF + SSR)"]
    end

    subgraph API_LAYER["Application Service Layer"]
        FASTAPI["FastAPI REST API (/api/v1)"]
    end

    subgraph QUEUES["Task Broker & Cache"]
        REDIS[("Redis 7 (Broker, Rate Limits, Locks)")]
    end

    subgraph WORKERS["Celery Distributed Workers"]
        W_COL["q.collect (Ingestion Workers)"]
        W_NORM["q.normalize (Parser Workers)"]
        W_GEO["q.geo (Attribution Workers)"]
        W_ENR["q.enrich (SSRF-Safe Polite Crawlers)"]
        W_CLS["q.classify (Category/Taxonomy Workers)"]
        W_ANA["q.analytics (Metric Aggregators)"]
        W_EXP["q.export (CSV/XLSX Compilers)"]
    end

    subgraph STORAGE["Persistence Tier"]
        PG[("PostgreSQL 16 (pg_trgm, unaccent, citext)")]
        S3[("Object Storage (MinIO / S3: Raw Payloads, Exports)")]
    end

    subgraph ADAPTERS["External Ingestion Adapters"]
        ADAPT_A["Adapter A: Meta Graph API (Official Political/Issue)"]
        ADAPT_B["Adapter B: Managed Provider (Commercial Ads)"]
        ADAPT_C["Adapter C: Playwright UI Scraper (Disabled / Standby)"]
        PLACES["Google Places API (New)"]
    end

    BROWSER -->|HTTPS| CADDY
    CADDY -->|Reverse Proxy| NEXT
    CADDY -->|Direct API / Static| FASTAPI
    NEXT -->|Signed JWT Bearer| FASTAPI

    FASTAPI -->|Read/Write| PG
    FASTAPI -->|Enqueue Tasks| REDIS
    FASTAPI -->|Signed URL Redirects| S3

    REDIS --> W_COL
    REDIS --> W_NORM
    REDIS --> W_GEO
    REDIS --> W_ENR
    REDIS --> W_CLS
    REDIS --> W_ANA
    REDIS --> W_EXP

    W_COL --> ADAPT_A
    W_COL --> ADAPT_B
    W_COL -.-> ADAPT_C
    W_COL --> S3
    W_COL --> PG

    W_NORM --> PG
    W_GEO --> PG
    W_GEO -.-> PLACES
    W_ENR --> PG
    W_CLS --> PG
    W_ANA --> PG
    W_EXP --> S3
    W_EXP --> PG
```

### 4.3 Search Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User Browser
    participant N as Next.js BFF
    participant A as FastAPI Service
    participant R as Redis Cache
    participant P as PostgreSQL

    U->>N: Search "Jaipur" + Category="Jewellery"
    N->>A: GET /api/v1/search?city=Jaipur&category=jewellery (Auth Header: JWT)
    A->>A: Validate JWT, check user role (viewer+)
    A->>P: Query city_aliases for "Jaipur" (exact + trigram match)
    P-->>A: Resolved city_id = 3 (slug: jaipur)
    A->>R: Check query cache for (city_id, filter_hash, cursor)
    alt Cache Hit
        R-->>A: Cached results JSON
    else Cache Miss
        A->>P: Keyset query on advertiser_city_links JOIN advertisers
        P-->>A: Raw rows (masked contacts, tier, confidence, ad_count)
        A->>R: Store query result (TTL: 300s)
    end
    A-->>N: 200 OK (Paginated Advertisers with Masked Contacts)
    N-->>U: Render virtualized results table

    U->>N: Click "Reveal Contacts" for Advertiser #18231
    N->>A: POST /api/v1/advertisers/18231/contacts/reveal
    A->>P: Verify daily reveal quota (users.reveal_quota_daily)
    alt Quota Exceeded
        A-->>N: 429 Quota Exceeded (ProblemDetails)
    else Quota Available
        A->>P: Check suppression table for contacts
        A->>P: Insert into audit_log (user_id, action="reveal", target_id=18231)
        A->>P: Decrement user quota counter
        P-->>A: Full contact details + evidence
        A-->>N: 200 OK (Unmasked phone, email, WhatsApp + provenance)
        N-->>U: Display unmasked contact modal
    end
```

### 4.4 Job Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> pending: Celery Beat schedules job
    pending --> running: Worker claims task (Redis lock acquired)
    running --> succeeded: Cursor reaches end / batch complete
    running --> partial: Ingested items committed; rate limit paused run
    running --> failed: Unexpected exception / network abort
    running --> blocked: Upstream challenge or 429 detected
    failed --> pending: Retried with exponential backoff
    blocked --> pending: Cool-down elapsed (>= 6 hours)
    pending --> cancelled: Operator cancels job via Admin API
    running --> cancelled: Kill switch triggered (SIGTERM handled)
    succeeded --> [*]
    cancelled --> [*]
```

### 4.5 Task Queue Routing & Capacity Planning
| Queue Name | Routing Key | Concurrency | Target Rate Limit | Task Purpose |
|---|---|---|---|---|
| `q.collect` | `collect.#` | 2–4 workers | Dynamic based on provider quota | Ingest raw ad batches from Adapter A/B |
| `q.normalize` | `normalize.#` | 4–8 workers | CPU bound (high) | Parse payloads, compute content hashes, canonicalize URLs |
| `q.geo` | `geo.#` | 4 workers | 100 req/min (Places API capped) | Calculate multi-signal city attribution scores |
| `q.enrich` | `enrich.#` | 8–16 workers | 1 req / 2s / domain (token bucket) | Crawl target websites via SSRF-safe polite fetcher |
| `q.classify` | `classify.#` | 4 workers | Batched / local rules | Map ad copy to category taxonomy |
| `q.analytics` | `analytics.#` | 2 workers | Scheduled nightly | Aggregate daily metrics and compute city scores |
| `q.export` | `export.#` | 2 workers | On demand | Stream CSV/XLSX exports to S3 |

### 4.6 Failure Modes & Self-Healing
- **Worker Crash Mid-Task:** Celery tasks run with `acks_late=True`. Redis leases expire, and the reaper process re-enqueues unacknowledged jobs from the last stored cursor checkpoint (PIPE-02).
- **Poison Payloads:** If an item fails processing across 3 consecutive retry attempts, it is routed to the `dead_letters` table along with full stack traces and input arguments (PIPE-03).
- **Transient Network Partitions:** All database and Redis connection pools implement automatic reconnection with exponential backoff and connection health checks.

## 5. Edge-Case IDs Referenced
- `PIPE-01` (Idempotent upsert handling)
- `PIPE-02` (Worker crash mid-run recovery)
- `PIPE-03` (Poison message isolation in dead_letters)
- `PIPE-08` (Budget runaway protection)
- `PIPE-11` (Scheduler overlap locking)
- `SEC-01` (SSRF guard on all worker crawling)

## 6. Open Questions
- Final decision on production message broker persistence (Redis AOF vs AWS SQS/ElastiCache) prior to Phase 12 deployment.

## 7. Acceptance Checklist
- [x] Full component architecture diagram provided in Mermaid format.
- [x] Search request flow and contact reveal sequence diagram documented.
- [x] Ingestion lifecycle state diagram mapped.
- [x] Task queues, rate limits, and capacity plan defined.
- [x] Failure recovery mechanisms and dead-letter routing specified.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

