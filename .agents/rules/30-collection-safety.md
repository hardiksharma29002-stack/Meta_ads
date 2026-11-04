---
description: Mandatory safety, security, and operational constraints for all data collection and external web fetching.
globs: ["**/*"]
alwaysApply: true
---

# Collection Safety & Infrastructure Protection

## 1. Mandatory SSRF Guard (SEC-01)
Every outbound network connection initiated by background workers, website scrapers, contact enrichers, or redirect unshorteners MUST route through the dedicated `core.ssrf_guard` module. Direct invocations of `urllib`, `requests`, naked `httpx`, or socket libraries are strictly forbidden.

### Required Validation Steps:
1. **Scheme & Port Restrictions:** Permit only `http` and `https` protocols on destination ports `80` and `443`.
2. **DNS Resolution & IP Validation:** Resolve domain names prior to socket connection and inspect all returned IP addresses. Immediately drop connections resolving to:
   - IPv4 loopback (`127.0.0.0/8`)
   - IPv4 private networks (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
   - Link-local and cloud metadata addresses (`169.254.0.0/16`, specifically AWS/GCP metadata `169.254.169.254`)
   - IPv6 equivalents: loopback (`::1`), unique local (`fc00::/7`), link-local (`fe80::/10`), IPv4-mapped IPv6 addresses (`::ffff:0:0/96`).
3. **Redirect Validation:** Re-validate target IP addresses at every redirect hop (maximum 5 hops permitted).
4. **Transport Isolation:** In containerized deployments, crawler and enrichment tasks must run within isolated network namespaces where host access and private VPC routes are denied at the firewall level.

## 2. Zero Anti-Bot Evasion (SRC-10)
AdAtlas enforces strict compliance with ethical and legal data collection boundaries:
- **Never bypass CAPTCHAs:** Do not incorporate automated solving services, OCR workarounds, audio challenge solvers, or human-in-the-loop CAPTCHA farms for Meta or external targets.
- **No Login-Wall Penetration:** Do not simulate credentials, session tokens, or automated authentication to bypass Meta login walls.
- **Respect Blocks & Cool-Down:** If an upstream data provider or target domain responds with a 403 Forbidden, 429 Too Many Requests, or bot-detection challenge, the worker must mark the task `blocked`, back off exponentially, log an alert, and respect a minimum 6-hour cool-down period.

## 3. Adapter C (Playwright UI Collector) Enforcement (D1, D2)
- Adapter C (custom headless Chromium scraper for Meta Ad Library) is created for emergency fallback capability only.
- It MUST remain disabled (`ADAPTER_C_ENABLED=false`) in all environments until explicit written legal authorization from human counsel is committed to `docs/COMPLIANCE_AND_LEGAL.md` and ratified via ADR-0002.
- Commercial ad ingestion must rely exclusively on managed, contractually compliant third-party data providers (Adapter B).

## 4. Hard Spend Budgets & Cost Caps (PIPE-08)
External billable services (Adapter B API calls, Google Places API requests, optional LLM inferences, and proxy bandwidth) must be throttled by code-level budget limits:
- Each service must check remaining allowances in the `budgets` table before initiating billable calls.
- Ingestion jobs must support a `--dry-run` flag that prints estimated ad volume, API unit costs, and projected spend before execution.
- If a daily or monthly budget cap reaches 80%, an operational warning is logged; if it reaches 100%, subsequent calls are blocked immediately.

## 5. Global Kill Switch & Source Purge (LEG-09)
- Operators must have the ability to halt all collection activity within 60 seconds via an admin API call (`POST /admin/kill-switch`) or environment toggle (`COLLECTION_ENABLED=false`).
- Each ad and contact record must preserve its source adapter provenance. In the event of an upstream licensing dispute or legal notice, the system must support selective data purging via `make purge-source SOURCE=<adapter_name>`.

## 6. Hermetic Test Discipline
Unit, contract, property, and integration tests MUST be entirely self-contained. Under no circumstances should test runs attempt live network requests against Meta, external providers, Google Places, or arbitrary business websites. All HTTP responses must be mocked or served via pre-recorded fixtures (`vcrpy` or `respx`).

