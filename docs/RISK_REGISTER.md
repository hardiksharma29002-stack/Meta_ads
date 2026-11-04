# Risk Register & Mitigation Strategy — AdAtlas India

## 1. Purpose
Identify, assess, monitor, and document mitigation strategies for legal, technical, operational, and financial risks threatening the AdAtlas platform.

## 2. Scope
Applies across all development phases and production operations, covering data collection, attribution accuracy, privacy regulations, infrastructure costs, and system security.

## 3. Decisions (Link ADRs)
- **ADR-0001:** Source Vendor Abstraction & Kill Switch.
- **ADR-0002:** Legal Gating of Scraping Operations.
- **ADR-0006:** LLM Spend Capping.
- **ADR-0007:** Proxy Metric Transparency to Mitigate Misleading Rankings.

## 4. Detailed Design: Comprehensive Risk Assessment Matrix

| # | Risk Description | Likelihood | Impact | Overall Severity | Engineering Mitigation Strategy | Ongoing Monitoring & Alerting | Owner |
|---|---|---|---|---|---|---|---|
| **K1** | **Meta or Provider Legal/Technical Block:** Meta updates anti-scraping enforcement or upstream provider faces legal injunction, halting data flow. | Medium | High | **High** | Multi-adapter architecture; emergency collection kill switch; ability to purge data per source adapter within minutes; legal counsel review before production go-live (D2); backup provider on standby. | `collect_runs_total{status="blocked"}`; provider health check probes. | System Owner |
| **K2** | **Erroneous City Attribution:** National brands or regional chains misattributed to local city directories, skewing ranking accuracy. | Medium | High | **High** | Multi-signal Noisy-OR model requiring corroboration; brand-name signal capped at 0.50; CI gate enforcing $\ge 90\%$ precision on 300+ labeled benchmark set; admin review queue for ambiguous cases. | `geo_tier_count`; benchmark regression reports in CI. | Pipeline Lead |
| **K3** | **Third-Party / Web Agency Contact Pollution:** Phone numbers of web design firms or payment gateways extracted instead of actual business contacts. | High | Medium | **High** | Keyword proximity exclusion ("Designed by...", "Theme by..."); cross-domain frequency threshold ($> 5$ domains flags `shared_third_party`); human precision audit target $\ge 95\%$. | `contacts_flagged_shared_total`; user feedback submissions (`/feedback`). | Enrichment Lead |
| **K4** | **Privacy / DPDP Regulatory Complaint:** Individual or regulator alleges unlawful personal data harvesting or failure to honor opt-out. | Low–Med | High | **High** | Strict minimization (no PAN, GSTIN state only); hashed suppression registry enforced pre-flight across ingestion, search, and export; public verified opt-out SLA $\le 7$ days; 72-hour breach runbook. | `optout_requests_pending_total`; suppression check failure counter. | Compliance Officer |
| **K5** | **Cloud & Provider Cost Runaway:** Unbounded keyword crawls or high Places/LLM query volume causes unexpected infrastructure expense. | Medium | Medium | **Medium** | Enforce daily/monthly spend caps in `budgets` table; `--dry-run` cost projection required for sweeps; prioritize page-expansion over keyword sweeps; automated alerts at 80% and 100% budget. | `budget_spent_ratio{scope}`; automated cloud billing alarms. | System Admin |
| **K6** | **Scraper / Provider Schema Mutation:** Upstream Meta layout changes break parsing pipelines, corrupting database records. | High | Medium | **High** | Shared adapter contract tests run daily; raw-first architecture preserving compressed payloads in S3; drift detection auto-halts ingestion upon $> 5\%$ parse errors; `reprocess --from-raw` CLI. | `parse_failures_total`; row-count deviation alerts ($\pm 40\%$). | Collector Lead |
| **K7** | **Sparse Data Skews Small-City Comparison:** Smaller markets (e.g. Jaipur, Kolkata) suffer statistical distortion in comparison scorecards. | Medium | Medium | **Medium** | Normalize metrics per 100k urban residents; enforce `MIN_SAMPLE` (200) data-sufficiency guard; grey out scores and display prominent warning banners for under-sampled cohorts. | `sample_ok` boolean metric; city advertiser volume gauges. | Analytics Lead |
| **K8** | **Over-Reliance on Proxy Scores:** Users interpret proxy vitality scores as exact ad spend metrics despite commercial spend unavailability. | Medium | Medium | **Medium** | Transparent UI score breakdown showing raw component values; prominent disclaimer copy: *"Based on Meta Ad Library activity. Commercial spend is not published by Meta and is not estimated."* | User onboarding surveys; quarterly feedback reviews. | Product Lead |
| **K9** | **Security Vulnerability Exploited (SSRF, XSS, Injection):** Malicious ad content or target landing page exploits internal infrastructure. | Low | High | **High** | Mandatory pre-connect IP validation in `core.ssrf_guard`; egress firewall denying private ranges; React JSX auto-escaping; CSV formula-injection prefixing; automated `gitleaks` and audit scans. | `ssrf_blocked_total`; security vulnerability scans in CI. | Security Lead |
| **K10** | **Agent / Engineering Drift:** Multiple autonomous agents introduce conflicting patterns, schema deviations, or undocumented hacks. | Medium | Medium | **Medium** | Monorepo directory ownership rules; authoritative Phase 0 docs; mandatory `make check` quality gate; strict requirement to record architectural changes in `docs/ADR/`. | PR compliance checks; ADR log reviews. | Architect Lead |

## 5. Edge-Case IDs Referenced
- `SRC-08` (Provider outage and failover)
- `GEO-01` (Brand name misattribution)
- `CON-05` (Web agency contact pollution)
- `CON-18` (Shared contact detection)
- `PIPE-08` (Budget cap enforcement)
- `SRCH-11` (Insufficient-sample city warnings)
- `SEC-01` (SSRF security incident)
- `LEG-01` (Opt-out processing failure)
- `ANA-07` (Commercial spend disclosure)

## 6. Open Questions
- None. All 10 major project risks are accounted for with active mitigations and operational owners.

## 7. Acceptance Checklist
- [x] All 10 core project risks (K1–K10) cataloged.
- [x] Likelihood, impact, and severity ratings assigned.
- [x] Engineering mitigation strategies and monitoring metrics documented.
- [x] Clear owner roles assigned for every risk.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

