---
description: Testing standards, coverage gates, hermetic test fixtures, security test suites, and data quality evaluations.
globs: ["**/tests/**/*", "e2e/**/*"]
alwaysApply: false
---

# Testing Strategy & Quality Verification Standards

## 1. Hermetic Testing Principle
The test suite must be 100% self-contained and reproducible offline:
- **No External Network Dependencies:** Under no circumstances should test runs dispatch requests to live Meta APIs, third-party scrapers, Google Places, LLMs, or target business websites.
- **Mocking & Replay:** Use recorded HTTP cassettes (`vcrpy` with credential scrubbing) or mock dispatchers (`respx` for httpx).
- **Transient Infrastructure:** Integration tests must spin up lightweight, ephemeral container instances (PostgreSQL 16, Redis 7, MinIO) via `testcontainers` or Docker Compose test profiles.

## 2. Test Layer Hierarchy

### 2.1 Unit & Property-Based Tests (`pytest`, `hypothesis`)
- Test individual extraction functions, text normalizers, Indic transliterators, and score combiners across extreme inputs.
- Property-based testing with `hypothesis` for:
  - Phone parser handling bizarre formatting, missing prefixes, and Indic numerals (CON-03, CON-04).
  - URL unshortening and parameter stripping (CON-11).
  - Noisy-OR probability math and conflicting signal deduplication (GEO-07).
  - CSV formula-injection prefixing (SEC-03).

### 2.2 Adapter Contract Tests (`vcrpy`, `respx`)
- All collectors (Adapter A, Adapter B, Adapter C) must run against a unified, shared contract test suite.
- Contract suites assert that normalized output adheres strictly to Pydantic models regardless of underlying source variance.
- Incorporate schema-drift detection fixtures to trigger automated alerts when raw source structures mutate.

### 2.3 Integration & Idempotency Tests
- Verify pipeline worker stages (`collect` -> `normalize` -> `geo` -> `enrich` -> `classify` -> `analytics`).
- **Idempotency Gate:** Running the exact same ingestion and enrichment batch twice against a populated database must produce zero duplicate rows and zero unexpected version increments.
- **Raw-First Replay:** Execute `reprocess --from-raw` on stored payloads and verify that derived tables are reconstructed identically.

### 2.4 Security Test Suite
- **SSRF Test Suite:** Dedicated test suite verifying that `core.ssrf_guard` rejects:
  - `127.0.0.1` and `localhost`
  - `169.254.169.254` (cloud metadata)
  - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
  - IPv6 mapped addresses (`::ffff:127.0.0.1`)
  - HTTP redirects leading from public IPs to private IPs (SEC-01)
- **Injection Suite:** Payloads testing SQL injection, React JSX XSS vectors, and CSV formula escapes.
- **RBAC & IDOR:** Role-based boundary tests ensuring viewers cannot reveal contacts or access foreign export artifacts (SEC-07).

### 2.5 End-to-End Tests (`playwright`)
- Cover complete user journeys in the web frontend:
  1. Search city ("Jaipur" / "Jaypur" / "जयपुर") -> verify results match city attribution.
  2. Filter by category, active ads, and contact availability.
  3. Reveal masked contact -> assert quota decrement and audit entry creation.
  4. Submit opt-out form -> assert immediate contact suppression from UI and exports.

### 2.6 Data Quality & Precision Benchmarks
- **Geo Attribution Benchmark:** A human-labeled evaluation dataset of >= 300 advertisers (60 per city) must run in CI. Confirmed-tier precision must achieve >= 90%.
- **Contact Precision Sample:** A human-audited set of >= 200 extracted contacts must maintain >= 95% precision for confidence scores >= 0.8.

## 3. Coverage Thresholds & Gates
- **Critical Modules (>= 95% line coverage):**
  - `backend/app/core/ssrf_guard.py`
  - `backend/app/services/suppression.py`
  - `backend/app/pipeline/phone_parser.py`
  - `backend/app/pipeline/email_validator.py`
- **Pipeline & Services (>= 80% line coverage):**
  - Normalization, geo attribution, and scoring services.
- **Single Quality Gate:** Every pull request must pass `make check` without warnings or suppressed errors before merging.

