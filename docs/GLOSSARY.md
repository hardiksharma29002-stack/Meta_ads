# Domain & Technical Glossary — AdAtlas India

## 1. Purpose
Define unambiguous, standardized definitions for domain terminology, advertising concepts, mathematical models, and architectural components utilized across AdAtlas.

## 2. Scope
Applies universally across documentation, backend code comments, database schema naming, API schemas, and frontend user interfaces.

## 3. Decisions (Link ADRs)
- **ADR-0001:** Definition of Ingestion Adapters.
- **ADR-0007:** Definition of Proxy Metrics.
- **ADR-0014:** Definition of Geo Attribution Tiers.

## 4. Detailed Design: Terminology Definitions

| Term | Domain Category | Formal Definition |
|---|---|---|
| **Ad (Meta Ad)** | Advertising | A single individual advertising delivery record issued under a unique `meta_ad_id` by Meta, associated with a start date, end date, creative copy, and delivery platforms. |
| **Creative** | Advertising | The unique substantive visual and textual content of an advertisement. Multiple ad deliveries sharing the exact same body copy, headline, CTA, and landing domain share an identical `content_hash` and represent one creative. |
| **Collation** | Advertising | Meta's internal clustering mechanism where minor variations of an ad (e.g. running across Instagram Stories vs Facebook Feed) are grouped under a shared `collation_id`. |
| **Page / Advertiser** | Entity | The official Meta Facebook Page running the advertising campaigns, identified uniquely by `meta_page_id`. |
| **Entity Group** | Entity | A cluster of multiple Meta Pages identified through entity resolution as belonging to the identical parent commercial business (sharing primary domain, phone, or verified registration). |
| **Attribution Tier** | Geography | The probabilistic confidence category linking an advertiser to a metropolitan city: `confirmed` ($\ge 0.75$), `probable` ($0.40 \le p < 0.75$), or `weak` ($< 0.40$). |
| **Operational Scope** | Geography | The geographical scale of an advertiser's physical operations: `local` (single metro area), `regional` (2–4 neighboring cities or single state), `national` (pan-India presence), or `unknown`. |
| **Suppression** | Compliance | The hashed do-not-contact registry (`suppression` table) storing SHA-256 hashes of telephone numbers, email addresses, domains, or Meta pages that have opted out or requested legal erasure. |
| **Adapter** | Architecture | A pluggable source module implementing the `AdSourceAdapter` protocol, abstracting external communication with Meta Graph API (Adapter A), third-party providers (Adapter B), or headless scrapers (Adapter C). |
| **Raw Payload** | Architecture | The untouched, un-parsed JSON or HTML response returned by an upstream collection source, compressed via zstd and permanently preserved in object storage for diagnostic audit and pipeline replay. |
| **Right-Censored Ad Longevity** | Analytics | Statistical survival analysis methodology handling advertisements that are still actively running at the time of observation (their ultimate delivery stop date is unknown and censored). |
| **Winsorization** | Analytics | Statistical transformation that caps extreme outlier values at a specified percentile (e.g. capping individual advertiser active ad volume at the 95th percentile) to prevent spam floods from distorting aggregate city metrics. |
| **Noisy-OR Combiner** | Mathematics | A probabilistic Bayesian model used to aggregate independent pieces of uncertain evidence to determine the overall probability that an advertiser belongs to a specific city. |
| **Polite Fetcher** | Web Scraping | An asynchronous HTTP client that enforces strict domain rate limits (token bucket), respects `robots.txt`, enforces timeout/size caps, and mandates pre-connect SSRF IP validation. |
| **BFF (Backend-for-Frontend)** | Architecture | Next.js API route handlers acting as an intermediary between the browser client and the backend FastAPI service, handling session cookies and signing short-lived JWT tokens. |
| **DPDP Act & Rules** | Legal | The Digital Personal Data Protection Act, 2023 and associated DPDP Rules, 2025 establishing India's statutory data protection and privacy framework. |

## 5. Edge-Case IDs Referenced
- `ANA-02` (Collation vs distinct creative definitions)
- `ANA-06` (Right-censoring methodology)
- `GEO-06` (Attribution tiers and scope)
- `LEG-01` (Suppression registry terminology)

## 6. Open Questions
- None.

## 7. Acceptance Checklist
- [x] All 16 key technical and domain terms defined.
- [x] Category classifications and cross-references provided.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

