# Technology Stack & Selection Rationale — AdAtlas India

## 1. Purpose
Document the chosen programming languages, application frameworks, persistence technologies, data processing libraries, and developer tooling for AdAtlas, detailing the evaluation rationale and explicitly rejected alternatives.

## 2. Scope
Applies to the entire engineering ecosystem, including `backend/`, `frontend/`, `infra/`, and CI/CD pipelines.

## 3. Decisions (Link ADRs)
- **ADR-0004:** India Region Cloud Hosting (Single VM + Managed PostgreSQL).
- **ADR-0005:** Auth.js & BFF JWT Token Model.
- **ADR-0012:** Modular Monolith Architecture over Microservices.
- **ADR-0013:** PostgreSQL Trigram & Full-Text Search.

## 4. Detailed Design

### 4.1 Dependency Governance & 14-Day Cool-Off Rule
To guard against supply-chain compromise, dependency confusion attacks, and unstable upstream releases (SEC-08):
- Every dependency in `pyproject.toml` and `package.json` must be strictly locked with cryptographic hashes (`uv.lock`, `pnpm-lock.yaml`).
- **Cool-off rule:** Any package version released within the trailing 14 days is prohibited from adoption unless addressing a critical zero-day vulnerability approved by lead engineers.

### 4.2 Core Stack Selection Matrix

| Layer / Need | Technology Selected | Rationale & Key Capabilities | Alternatives Considered & Rejected |
|---|---|---|---|
| **Backend Language** | **Python 3.12+** | Unrivaled ecosystem for web scraping, NLP, phone parsing, and data validation; native async support. | *Node.js / TypeScript:* Weaker NLP and telecom parsing libraries.<br>*Go:* Too low-level for complex heuristic web scraping pipelines. |
| **API Framework** | **FastAPI + Pydantic v2** | High-performance asynchronous execution, strict type validation, native OpenAPI schema generation. | *Django REST:* Heavy ORM overhead and sync legacy.<br>*Flask:* Lacks native async and type-safe schema validation. |
| **ORM & Migrations** | **SQLAlchemy 2.0 (Async) + Alembic** | Industry-standard enterprise async ORM, precise SQL control, clean schema migration management. | *SQLModel:* Immature tooling for complex joins.<br>*Prisma:* Complex integration with advanced Postgres FTS extensions. |
| **Worker Engine** | **Celery 5 + Redis + Celery Beat** | Mature distributed task processing, per-queue concurrency, token-bucket rate limiting, cron scheduling. | *Arq / Dramatiq:* Lacks mature enterprise monitoring tooling.<br>*Temporal:* Substantial operational complexity for v1 requirements. |
| **Database** | **PostgreSQL 16+** | Native support for `pg_trgm`, `unaccent`, and `citext`; high-efficiency relational model for joins and audit trails. | *MongoDB:* Poor relational join performance on advertisers, ads, and contacts. |
| **Cache & Task Broker** | **Redis 7** | In-memory queue broker, distributed advisory locking, token-bucket rate limiters. | *RabbitMQ:* Extra operational surface without adding needed value for v1. |
| **Object Storage** | **S3-Compatible (MinIO local, S3/R2 prod)** | Scalable, cost-effective storage for compressed raw payloads (`zstd`), HTML snapshots, and export files. | *PostgreSQL Blobs:* Database bloat and high backup latency. |
| **Search Engine** | **PostgreSQL FTS + Trigram (pg_trgm)** | Sufficient for up to 5M ads/advertisers; zero additional operational infrastructure required. | *Elasticsearch / Meilisearch:* Deferred until p95 query latency exceeds 1.0s or typo-tolerance proves inadequate. |
| **Frontend Framework** | **Next.js (App Router) + TypeScript Strict** | Server-side rendering (SSR), optimized layout caching, integrated BFF (Backend-for-Frontend) route handlers. | *Vite + React SPA:* Sub-optimal SEO and client-heavy initial page load times. |
| **Styling & UI Kit** | **Tailwind CSS + shadcn/ui** | Rapid prototyping, zero runtime CSS overhead, accessible Radix-based UI components. | *Chakra UI / Material UI:* Heavy runtime styling penalties. |
| **Client State & Tables** | **TanStack Query & TanStack Table (Virtualized)** | Robust query caching, automatic deduplication, smooth virtualized rendering of 1,000+ row advertiser tables. | *AG Grid:* Enterprise license fees and heavyweight bundle size. |
| **Authentication** | **Auth.js (Google OAuth)** | Seamless domain-restricted OAuth login; issues short-lived signed JWTs for FastAPI calls. | *Clerk / Auth0:* Recurring SaaS subscription costs.<br>*Keycloak:* Massive memory footprint. |
| **Reverse Proxy & Edge** | **Caddy Server** | Automatic Let's Encrypt TLS certificate provisioning, HTTP/3 support, simple configuration. | *Nginx:* Requires separate Certbot cron jobs and manual configuration. |

### 4.3 Data Collection, Extraction & NLP Tooling

| Need | Library / Tool | Function & Role |
|---|---|---|
| **Polite HTTP Client** | `httpx` (Custom Client) | Async client wrapped with `core.ssrf_guard` IP checks, redirect controls, and timeout enforcement. |
| **HTML Parser** | `selectolax` + `extruct` | Blazing-fast Modest engine for CSS selectors; `extruct` extracts schema.org JSON-LD and microdata. |
| **Headless Browser Fallback** | `Playwright` (Chromium) | Budget-capped fallback for dynamic JS-rendered contact pages. Sandboxed and recycled periodically. |
| **Phone Number Parsing** | `phonenumbers` | Strict E.164 normalization, type classification (mobile, landline, toll-free) for the `IN` region. |
| **Email Validation** | `email-validator` + `dnspython` | RFC-compliant syntax verification and domain MX record existence. **Zero SMTP RCPT probing.** |
| **Domain Normalization** | `tldextract` | Accurate extraction of registered domain (eTLD+1) avoiding confusion with multi-part ccTLDs (`.co.in`). |
| **Fuzzy Matching** | `rapidfuzz` | High-speed C++ string distance algorithms for entity resolution and name-vs-domain agreement. |
| **Indic Transliteration** | `indic-transliteration` + `unidecode` | Normalizing vernacular Hindi, Bengali, Kannada, and Marathi spellings into phonetic Latin representations. |
| **Language Identification** | `lingua-language-detector` | Accurate script and language classification across English, Hinglish, and regional Indian languages. |
| **Data Quality Verification** | `pandera` + `polars` | Schema enforcement on ingestion batches, golden-dataset evaluation, and metric aggregation. |
| **Validation API** | Google Places API (New) | Authorized verification of physical addresses, landline phones, and geographic coordinates. |
| **Optional LLM Fallback** | Gemini 1.5 Flash / Claude 3.5 Haiku | Cached, budget-capped fallback for unstructured taxonomy categorization. Never receives contact data. |

### 4.4 Technologies Deliberately Excluded
- **Scrapy:** Too rigid to integrate cleanly into Celery's budget-enforcing task pipeline and custom SSRF socket wrappers.
- **Selenium:** Significantly slower and less stable than Playwright in headless containerized environments.
- **Lead Generation Scraping from Marketplaces (IndiaMART, JustDial):** High legal exposure, separate aggressive terms of service, and low data fresh-rate compared to primary advertiser websites.
- **Facebook Page "About" Scraping:** High risk of Meta account bans and bot-detection challenges; disabled by default under ADR-0002.
- **Synthetic Email Guessing Engines:** Generating unverified patterns (`firstname.lastname@domain.com`) fabricates personal data and violates compliance principles.

## 5. Edge-Case IDs Referenced
- `CON-03` (Phone normalization with phonenumbers)
- `CON-16` (Email validation without SMTP probing)
- `SEC-01` (Custom httpx SSRF transport)
- `SEC-08` (Supply-chain cool-off enforcement)

## 6. Open Questions
- Final evaluation between Polars and Pandas for nightly analytics aggregations once initial data volumes are established in Phase 2.

## 7. Acceptance Checklist
- [x] Complete technology selection matrix documented with architectural rationales.
- [x] Supply chain 14-day cool-off rule established.
- [x] Explicitly rejected technologies and non-choices recorded.
- [x] Data extraction, NLP, and verification libraries cataloged.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

