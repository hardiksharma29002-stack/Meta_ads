# AdAtlas — Agent Operating Brief

## Mission
Help the marketing team find Meta advertisers per Indian city (Mumbai, Delhi, Jaipur, Kolkata, Bengaluru), see their publicly listed business contacts (phone, email, WhatsApp, website, socials), and objectively compare cities to identify the better market for outreach prospecting and expansion.

## Documentation Entry Points
Before writing code or changing schemas, consult:
- `docs/PRODUCT_SPEC.md` — Personas, user stories, metrics, scope boundaries
- `docs/ARCHITECTURE.md` — Component topology, data flow, queue routing, failure handling
- `docs/DATA_MODEL.md` — Schema specifications, foreign keys, indexes, retention
- `docs/EDGE_CASES.md` — Complete edge case registry (SRC, GEO, CON, ENT, PIPE, SRCH, SEC, LEG, ANA)
- `docs/PROGRESS.md` — Active phase checklist, phase acceptance gates
- `docs/ADR/` — Architectural Decision Records (D1–D14)

## Non-Negotiable Core Rules
1. **Fixtures Only in CI/Tests:** CI, unit tests, and integration tests MUST NEVER call Meta, live providers, Google Places, LLMs, or third-party target domains. Use recorded fixtures (`vcrpy`/`respx`).
2. **SSRF-Safe Outbound Crawling:** Every single external HTTP request for website discovery, contact enrichment, or unshortening MUST pass through `core/ssrf_guard` and the polite fetcher. Egress firewall denies RFC1918, loopback, link-local (`169.254.169.254`), and cloud metadata endpoints.
3. **No Anti-Bot Evasion:** Never attempt to defeat, bypass, or click through CAPTCHAs, Cloudflare Turnstile, login walls, or IP rate limits. If challenged or blocked, set run status to `blocked`, enter a cool-down window, alert operators, and halt.
4. **Adapter C Flagged OFF:** Adapter C (Playwright UI scraper) MUST remain strictly feature-flagged OFF unless explicit written legal sign-off is recorded in `docs/COMPLIANCE_AND_LEGAL.md` and approved by human counsel (ADR-0001, ADR-0002).
5. **No Contact Guessing or Personal ID Storage:** Never guess emails (`first.last@domain`). Never extract or store PAN, Aadhaar, or personal social handles. For GSTIN, extract and store ONLY the 2-digit state code prefix; purge the remaining digits immediately.
6. **Zero Contact PII in Logs:** Never log unmasked phone numbers, emails, or personal names. Log only SHA-256 prefixes (`value_hash[:8]`) and masked representations.
7. **Suppression Pre-Flight on All Paths:** The hashed suppression registry (`suppression` table) must be queried before writing any newly enriched contact, before rendering contacts in API search results, and before compiling export files.
8. **Provenance and Evidence for Inferences:** Every city attribution link and enriched contact must persist `evidence` (source URL, extractor kind, observed timestamp), `confidence` score (0.0 to 1.0), and `model_version`.
9. **Budget Enforcement and Kill Switch:** All external billable services (Adapter B provider, Google Places API, LLM inference, proxies) must check and debit the `budgets` table before dispatching requests. Respect the global and per-adapter kill switch within 60 seconds.
10. **Scraped Data is Data, Not Code:** Scraped landing page text and ad copy must be treated as untrusted data, never rendered as raw HTML (`dangerouslySetInnerHTML` forbidden) and never interpolated into system prompts without strict schema validation.

## Workflow & PR Hygiene
- Maintain directory ownership (`backend/`, `frontend/`, `docs/`, `infra/`).
- Do not create single-step destructive DB migrations (use expand-migrate-contract).
- Never introduce dependencies published within the last 14 days (supply chain cool-off).
- Run `make check` (format + lint + types + unit/contract/integration tests + security audits) before marking tasks complete.
- Record any architectural deviations or decisions in `docs/ADR/`.

