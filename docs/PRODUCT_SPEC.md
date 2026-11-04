# Product Specification — AdAtlas India

## 1. Purpose
Define the business requirements, target personas, user stories, feature scope, and success criteria for AdAtlas, an intelligence platform tracking Meta advertisers across five key Indian cities to enable compliant B2B marketing research and city-level comparative analysis.

## 2. Scope
- **In-Scope (v1):**
  - Tracking advertising activity across five designated Indian metropolitan centers: Mumbai, Delhi (NCT), Jaipur, Kolkata, and Bengaluru.
  - Multi-adapter collection: official Meta Graph API for political/issue ads (Adapter A), managed compliant third-party data providers for commercial ads (Adapter B).
  - High-precision automated city attribution engine combining multi-signal evidence.
  - Ethical B2B contact enrichment limited strictly to business-published digital properties (domain landing pages, schema.org JSON-LD, public corporate contacts).
  - Multi-profile city vitality comparison ("which city is better") using objective proxy metrics.
  - Role-Based Access Control (RBAC), daily reveal quotas, audit logging, formula-safe CSV/XLSX export generation, and public opt-out processing.
- **Out-of-Scope (v1):**
  - Commercial ad spend or impression modeling (Meta does not publish commercial ad spend outside the EU; fabricating estimates is strictly forbidden).
  - Direct communication or outreach execution (no automated email sending, bulk WhatsApp messaging, SMS dispatch, or dialers).
  - Scraping logged-in Facebook sessions, personal social profiles, or private groups.
  - Enriching political figures, candidates, or private individuals.
  - Cities outside the initial five (onboarding handled via configuration workflows in future phases).

## 3. Decisions (Link ADRs)
- **ADR-0001:** Multi-Adapter Data Sourcing (Adapter B primary for commercial ads, Adapter C off).
- **ADR-0002:** Compliance Boundary & Legal Sign-off for Contact Enrichment.
- **ADR-0007:** Goal-Driven Multi-Profile City Scoring Framework.
- **ADR-0009 & ADR-0010:** Metropolitan Boundaries (Delhi NCT vs. NCR; Mumbai City vs. MMR).

## 4. Detailed Design

### 4.1 Target Personas
| Persona | Role | Key Needs & Primary Workflows |
|---|---|---|
| **Marketing Executive** | List Builder & Prospector | Searches specific cities, filters active advertisers by category and contact availability, reveals verified contacts within daily quotas, exports clean lists. |
| **Marketing Lead** | Strategic Planner | Compares cities across business goals, reviews category saturation and growth velocity, inspects proxy score explanations to allocate marketing budgets. |
| **Admin / Data Engineer** | System Operator | Configures and monitors collection jobs, manages provider spend caps, monitors pipeline health and dead letters, executes kill switch if needed. |
| **Compliance Officer** | Legal & Privacy Guardian | Processes opt-out requests, verifies suppression list integrity, audits contact reveal activities, oversees DPDP readiness. |

### 4.2 User Stories
- **US-01 (City Discovery):** As a marketing executive, I can select a city (or input an alias such as "Jaypur", "Bombay", or "जयपुर") to view active advertisers attributed to that city with active ad counts, primary category, first-seen date, and contact indicators.
- **US-02 (Advertiser Detail):** As a marketing executive, I can open an advertiser profile to inspect its ad history, creative copy, landing URLs, and verified contact channels with full provenance and confidence scores.
- **US-03 (Granular Filtering):** As a marketing executive, I can filter advertisers by category, phone/email/WhatsApp presence, active ad volume, recent entry (past 30 days), language, and platform.
- **US-04 (Compliant Export):** As a marketing executive, I can export filtered advertiser records to CSV or XLSX format, ensuring suppressed or opted-out contacts are never included.
- **US-05 (City Comparison):** As a marketing lead, I can compare the five cities across customizable goal profiles (Outreach Prospecting, Market Maturity, Low-Competition Entry) with explainable component breakdowns and sufficiency warnings.
- **US-06 (Operational Control):** As an admin, I can inspect crawl job progress, track expenditure against API budgets, replay failed tasks, and trigger a global collection kill switch.
- **US-07 (Public Opt-Out):** As a business representative, I can submit an opt-out request via a public form to permanently remove and suppress our business contacts from search and export.

### 4.3 Success Metrics & Performance Targets
| Metric | Target | Verification Method |
|---|---|---|
| Search API Latency (50 results) | p95 < 800 ms | Load testing (`k6`) against 1M synthetic records |
| Confirmed City Attribution Precision | >= 90 % | Benchmarked against 300+ human-labeled evaluation dataset |
| Contact Verification Precision | >= 95 % (for conf >= 0.8) | Human audit sample of 200+ extracted contacts |
| Indian Phone Normalization Rate | >= 95 % valid E.164 | Automated parsing test with `phonenumbers` |
| T1 Advertiser Refresh Cadence | <= 24 hours | Celery Beat schedule metrics |
| Suppressed Contacts in Exports | **0 (Zero Tolerance)** | Automated CI security & export pipeline tests |

## 5. Edge-Case IDs Referenced
- `SRC-01` (Official API restrictions on commercial ads)
- `GEO-02` (City alias and vernacular handling)
- `CON-01` (Advertisers with no web footprint)
- `SRCH-01` (Typo-tolerant city search)
- `LEG-01` (Opt-out and suppression propagation)

## 6. Open Questions
- None blocking Phase 0. Ongoing legal review (D2) will formalize production go-live policies.

## 7. Acceptance Checklist
- [x] Personas and user stories documented with clear scope boundaries.
- [x] Measurable performance targets and precision thresholds defined.
- [x] In-scope vs out-of-scope boundaries explicitly stated.
- [x] Cross-references to ADRs and Edge Cases verified.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

