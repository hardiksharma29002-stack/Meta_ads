# Master Edge-Case Catalogue & Verification Matrix — AdAtlas India

## 1. Purpose
Provide an exhaustive, immutable catalogue of all anticipated edge cases, anomalies, failure scenarios, and legal constraints across the entire lifecycle of the AdAtlas platform, mapping each scenario to an owner implementation phase and verifiable test identifier.

## 2. Scope
Covers all system subsystems: external source collectors (SRC), geography engine (GEO), contact enrichment (CON), entity resolution (ENT), pipeline and operations (PIPE), search and UX (SRCH), application security (SEC), legal and compliance (LEG), and analytics (ANA).

## 3. Decisions (Link ADRs)
- **ADR-0001:** Source Fallback & Adapter C Disablement.
- **ADR-0002:** Data Minimization & Legal Boundaries.
- **ADR-0007:** Proxy-Based City Scoring Architecture.
- **ADR-0014:** Noisy-OR Geo-Attribution Engine.

## 4. Detailed Design: Edge-Case Verification Matrix

> **Test Types:** **U** = Unit · **I** = Integration · **C** = Contract · **P** = Property-Based · **E** = End-to-End · **S** = Security · **M** = Manual / Runbook Drill

### 4.1 Data Source and Meta-Specific Scenarios (SRC)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **SRC-01** | Official API returns only political/issue ads for India; commercial query returns empty | Maintain capability flags per adapter; Adapter A is never the sole commercial source; UI labels political ads separately | C | Phase 3 | `test_contract_adapter_a_capabilities` |
| **SRC-02** | Access token expires or becomes invalid mid-run | Long-lived token exchange; automatic pause on token error; alert operators; resume execution from cursor | I | Phase 3 | `test_collector_token_refresh_resume` |
| **SRC-03** | Upstream rate limit hit (undocumented limits) | Exponential backoff with full jitter; adaptive concurrency driven by rate headers; circuit breaker | I | Phase 3 | `test_collector_adaptive_backoff_429` |
| **SRC-04** | "Reduce the amount of data" API error on large pages | Automatically halve page size; drop optional heavy fields; retry query | I | Phase 3 | `test_collector_page_size_halving` |
| **SRC-05** | Pagination cursor expires, repeats, or enters infinite loop | Checkpoint last cursor and seen `meta_ad_id` set; deduplicate in memory; narrow timestamp window and restart | I | Phase 3 | `test_collector_cursor_loop_detection` |
| **SRC-06** | `ad_snapshot_url` carries a short-lived ephemeral token | Never persist signed snapshot URLs; store permanent permalink `https://www.facebook.com/ads/library/?id=<id>` | U | Phase 3 | `test_ad_permalink_canonicalization` |
| **SRC-07** | Provider returns partial data, renamed fields, or drops ads silently | Schema-version and required-field validators; row-count sanity check vs previous run ($\pm 40\%$ deviation triggers alert); canary queries | C | Phase 3 | `test_contract_provider_schema_drift` |
| **SRC-08** | Provider outage, deprecation, or unexpected price change | Provider registry with seamless fallback capability; operational failover runbook | M | Phase 12 | `runbook_provider_failover_drill` |
| **SRC-09** | Meta UI internal layout mutations (Adapter C) | Required-key drift detector; auto-disable collector after 5 consecutive failures; trigger high-severity alert | C | Phase 3 | `test_adapter_c_drift_detection` |
| **SRC-10** | Login wall, challenge interstitial, or CAPTCHA encountered | **Never attempt automated bypass.** Mark run status `blocked`; enter cool-down window $\ge 6$ hours; alert operator | I | Phase 3 | `test_collector_anti_bot_fail_closed` |
| **SRC-11** | Keyword search returns resellers/affiliates that merely mention brand | City search keys on advertiser-level attribution, not keyword matches; page-based query expansion | I | Phase 3 | `test_collector_reseller_keyword_isolation` |
| **SRC-12** | Same ad creative runs under multiple versions/pages (collation) | Extract and persist `collation_id`; count distinct creative content hashes | U | Phase 4 | `test_normalizer_collation_deduplication` |
| **SRC-13** | Carousel / DCO / catalogue ads containing template placeholders | Detect `{{...}}` pattern syntax; tag as template; exclude template tokens from classification | U | Phase 4 | `test_normalizer_template_placeholder_strip` |
| **SRC-14** | Inactive commercial ads vanish from library | Mark `disappeared_at` timestamp after two consecutive sweep misses; compute longevity from local observation history | I | Phase 3 | `test_collector_ad_disappearance_tracking` |
| **SRC-15** | Ad has no landing URL (lead form, Messenger, WhatsApp, call) | Valid advertiser; enrichment falls back to Google Places or ad WhatsApp CTA | I | Phase 3 | `test_collector_no_url_ad_handling` |
| **SRC-16** | Hindi / Bengali / Kannada / Marathi / Hinglish ad copy | Enforce UTF-8 NFC normalization; language identification via `lingua`; transliteration support; avoid ASCII-only regex | U | Phase 4 | `test_normalizer_indic_unicode_handling` |
| **SRC-17** | Extremely long text, emoji sequences, ZWJ, bidi marks | TEXT database columns; Unicode normalization; truncate only in UI summary views | U | Phase 4 | `test_normalizer_emoji_bidi_integrity` |
| **SRC-18** | Political / issue ads mixed into commercial results | Flag `ad_type = 'political_issue'`; render under separate UI tab; exclude from commercial contact enrichment | I | Phase 3 | `test_pipeline_political_ad_segregation` |
| **SRC-19** | Timezone mismatches (Meta UTC vs Indian users IST) | Persist all timestamps strictly in UTC; render in IST on UI; compute daily rollups on IST calendar day boundaries | U | Phase 3 | `test_normalizer_timezone_ist_rollups` |

### 4.2 Geography and Attribution Scenarios (GEO)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **GEO-01** | Brand name contains city ("Jaipur Rugs") but entity is national | Name-only signal capped at 0.50; requires secondary independent corroboration | U | Phase 5 | `test_geo_brand_name_capping` |
| **GEO-02** | Aliases and transliterations: Bombay/Mumbai, Calcutta/Kolkata, Bangalore/Bengaluru, New Delhi/Delhi/दिल्ली, जयपुर/Jaipur/Jaypur | `city_aliases` reference mapping + trigram fuzzy matching; comprehensive test coverage per alias | U | Phase 2, 5 | `test_geo_alias_vernacular_resolution` |
| **GEO-03** | Satellite suburbs (Gurugram, Noida, Navi Mumbai, Thane, Howrah, Salt Lake) | Alias classification `kind = 'satellite'`; controlled via explicit UI toggle; defaults per ADR-0009/0010 | U | Phase 2, 5 | `test_geo_satellite_suburb_resolution` |
| **GEO-04** | Generic locality names shared across cities ("Civil Lines", "Model Town") | Locality names never generate attribution points without explicit city/state context | U | Phase 5 | `test_geo_generic_locality_suppression` |
| **GEO-05** | National brand with corporate HQ in Mumbai advertising pan-India | Classify `scope = 'national'`; exclude from local city scorecards by default | I | Phase 5 | `test_geo_national_hq_filtering` |
| **GEO-06** | Multi-city chain or franchise operation | Many-to-many attribution links; track `branch_count`; weight counting so single entity never exceeds 1.0 total | I | Phase 5 | `test_geo_multicity_chain_weighting` |
| **GEO-07** | Conflicting signals (e.g. Jaipur PIN code, Mumbai landline) | Apply conflict rules; categorize as multi-city or downgrade confidence; route to admin review queue | U | Phase 5 | `test_geo_conflicting_signals_penalty` |
| **GEO-08** | Zero geographic signals (Instagram-only / WhatsApp-only) | Mark tier `weak`; attempt Google Places lookup; if unresolved, classify as "Unassigned" | I | Phase 5 | `test_geo_zero_signal_fallback` |
| **GEO-09** | Business relocates to another city | Re-evaluate attribution links every 90 days; maintain evidence observation timestamps | I | Phase 5 | `test_geo_relocation_reevaluation` |
| **GEO-10** | Mobile numbers used as spatial location evidence | **Strictly forbidden.** Only landline telephone STD area codes provide geographic attribution | U | Phase 5 | `test_geo_mobile_exclusion_as_evidence` |
| **GEO-11** | 6-digit numeric sequences that are not postal PIN codes (prices, order IDs) | Require proximate address context words ("PIN", "Pincode", "Address") + `pincode_city_map` hit | P | Phase 5 | `test_geo_pincode_contextual_validation` |
| **GEO-12** | Ad copy mentions city as destination ("Delhi to Jaipur cab") | Multi-mention directional filters; penalize transit phrasing; attribute at advertiser level | U | Phase 5 | `test_geo_transit_destination_filter` |
| **GEO-13** | Inconsistent population denominators (municipal vs urban agglomeration) | Standardize on official Ministry/Census urban agglomeration figures; record source and year | M | Phase 2 | `test_geo_population_denominators` |

### 4.3 Contact Extraction and Enrichment Scenarios (CON)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **CON-01** | Advertiser possesses no web domain | Fall back to Google Places API; check ad WhatsApp CTA; otherwise mark `no_public_contact`. **Never guess emails.** | I | Phase 6 | `test_enrich_no_website_fallback` |
| **CON-02** | Obfuscated emails (`[at]`, `(dot)`, entities, `data-cfemail`, JS concat) | De-obfuscate standard textual patterns; decode Cloudflare hex; flag image-only text as `contact_in_image` | U/P | Phase 6 | `test_enrich_email_deobfuscation` |
| **CON-03** | Indian phone number formats (`+91 98...`, `098...`, `91-98...`, `(0141) 2...`, `1800...`, 140-series) | Parse with `phonenumbers` region `IN`; categorize subtype; reject invalid checksums; discard telemarketing 140-series | P | Phase 6 | `test_enrich_phone_normalization_formats` |
| **CON-04** | Vernacular Indic numerals (०१२३, ০১২৩, ೦೧೨೩) | Map to ASCII digits via `unicodedata.digit` prior to regex parsing | U | Phase 6 | `test_enrich_indic_digit_mapping` |
| **CON-05** | Contact belongs to web agency, theme developer, or gateway support | Proximity exclusion ("Designed by...", "Developed by"); cross-domain frequency threshold $\to$ `shared_third_party` | U | Phase 6 | `test_enrich_agency_attribution_filter` |
| **CON-06** | Placeholder dummy contact data (`example@domain.com`, `9999999999`, `1234567890`) | Denylist matching + repeated digit pattern heuristics | P | Phase 6 | `test_enrich_placeholder_rejection` |
| **CON-07** | Freemail webmail addresses (`@gmail.com`, `@yahoo.com`, `@outlook.com`) | Assign flag `personal_data_risk`; apply stricter export quotas and policy warnings | U | Phase 6 | `test_enrich_freemail_flagging` |
| **CON-08** | Named grievance officer or personal executive contact | Extract role metadata; treat with elevated personal privacy standards; respect opt-out | U | Phase 6 | `test_enrich_named_officer_handling` |
| **CON-09** | JS-rendered pages, cookie walls, or geo-blocked corporate websites | Static fetch first; Playwright headless fallback within budget; else mark `unreachable`; no evasion | I | Phase 6 | `test_enrich_js_rendering_fallback` |
| **CON-10** | Parked domains, expired domains, or mismatched site ownership | Parked-page heuristics; fuzzy string match between page name and domain $< 0.6 \to$ `domain_mismatch`, drop | U | Phase 6 | `test_enrich_parked_domain_rejection` |
| **CON-11** | Shorteners, redirect hops, tracking parameters, marketplaces, link-in-bio | Follow redirects $\le 5$ hops; classify destination; reject marketplaces; extract outbound anchors from link-in-bio | I | Phase 6 | `test_enrich_redirect_unshortening` |
| **CON-12** | Destination redirect targets private IP or cloud metadata endpoint | Immediately abort connection; route through `core.ssrf_guard` (SEC-01) | S | Phase 6 | `test_ssrf_redirect_to_private_ip` |
| **CON-13** | Massive pages, crawler traps, or compression bombs | Enforce 2 MB decompressed body cap; depth 1 limit; max 8 pages/domain/run; 10s connection timeout | I | Phase 6 | `test_enrich_crawler_trap_containment` |
| **CON-14** | `robots.txt` disallows crawler or contact directories | Strictly respect robots rules; log `robots_blocked`; fall back to Google Places API | I | Phase 6 | `test_enrich_robots_txt_compliance` |
| **CON-15** | WhatsApp deep-links containing prefilled text payloads | Extract and parse destination phone number; classify as `whatsapp`; never interactively probe WhatsApp | U | Phase 6 | `test_enrich_whatsapp_deeplink_parsing` |
| **CON-16** | Syntactically valid email with dead or missing mail exchanger | Verify DNS MX records; optional paid deliverability verifier; **no SMTP RCPT probing** | I | Phase 6 | `test_enrich_email_mx_verification` |
| **CON-17** | Contacts change or expire over time | Automated 90-day re-verification schedule; assign `stale` flag upon failure; retain history | I | Phase 6 | `test_enrich_contact_staleness_cycle` |
| **CON-18** | Same phone number appears across numerous unrelated advertisers | Detect cross-domain frequency $> 5$; assign `shared_contact` flag; exclude from city coverage metric | U | Phase 6 | `test_enrich_shared_contact_detection` |
| **CON-19** | Contact belongs to a branch located in an alternative city | Attach contact to corresponding city link record when branch locality is identified | I | Phase 6 | `test_enrich_branch_contact_attachment` |
| **CON-20** | GSTIN identifier discovered on target website | Extract and store **only the 2-digit state code**; permanently drop remaining characters (PAN) | U | Phase 6 | `test_enrich_gstin_state_code_only` |

### 4.4 Entity Resolution Scenarios (ENT)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **ENT-01** | Meta Page renamed by business owner | Natural primary key is `meta_page_id`; track name changes in `advertiser_name_history` | U | Phase 4 | `test_entity_page_rename_history` |
| **ENT-02** | Same business operates multiple distinct Meta Pages | Generate merge suggestions when pages share primary domain, phone, or high name similarity; admin review queue | I | Phase 4 | `test_entity_merge_suggestions` |
| **ENT-03** | Digital marketing agency pages advertising for client roster | Assign category `agency`; flag appropriately; remain valid prospecting leads | U | Phase 4, 7 | `test_entity_agency_classification` |
| **ENT-04** | Scam / impersonation / MLM / adult / real-money gambling / crypto ads | Detect and assign `risk_flags`; exclude completely from lead lists; never enrich contacts | I | Phase 4, 7 | `test_entity_scam_risk_quarantine` |
| **ENT-05** | Government bodies, public utilities, political parties, or NGOs | Assign separate non-commercial category; exclude from sales outreach prospecting leads | U | Phase 4, 7 | `test_entity_govt_ngo_quarantine` |
| **ENT-06** | Meta Page deleted or advertising campaigns halted | Transition status to `dormant`; maintain records; avoid hard deletion | I | Phase 4 | `test_entity_dormant_transition` |
| **ENT-07** | Sole proprietorship named after an individual | Permitted as business identity; flagged for sensitive personal data handling during opt-out | U | Phase 4 | `test_entity_sole_proprietor_flagging` |

### 4.5 Pipeline and Operational Scenarios (PIPE)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **PIPE-01** | Task delivered multiple times by message broker | Idempotent database upserts; `ON CONFLICT DO UPDATE` comparing content hashes | I | Phase 3, 4 | `test_pipeline_idempotent_task_delivery` |
| **PIPE-02** | Celery worker crashes mid-execution | Cursor checkpoints persisted; worker heartbeat; reaper re-enqueues orphaned jobs | I | Phase 3, 11| `test_pipeline_worker_crash_recovery` |
| **PIPE-03** | Poison message causes unhandled worker crash | Retries capped at 3 with exponential backoff; route to `dead_letters` table; operator replay CLI | I | Phase 3 | `test_pipeline_dead_letter_routing` |
| **PIPE-04** | Extraction parser bug resolved in newer code release | CLI `reprocess --from-raw --version N` rebuilds derived normalized tables from S3 | I | Phase 4 | `test_pipeline_reprocess_from_raw` |
| **PIPE-05** | Upstream provider introduces unexpected raw fields | Raw payload model configured with `extra='allow'`; normalized model strict; unknown field alert | C | Phase 4 | `test_pipeline_unknown_field_tolerance` |
| **PIPE-06** | Reprocessing backfill runs concurrently with live scheduled refresh | PostgreSQL advisory locks per advertiser; prioritize real-time refresh queues | I | Phase 4 | `test_pipeline_advisory_lock_concurrency` |
| **PIPE-07** | Queue backlog expands beyond processing threshold | Backpressure: scheduler pauses new collection jobs when queue depth exceeds threshold | I | Phase 3 | `test_pipeline_queue_backpressure_halt` |
| **PIPE-08** | Cost runaway across provider, proxy, Places, or LLM APIs | Daily and monthly spending caps in `budgets` table; hard code stop; alert operator; kill switch | I | Phase 3, 11| `test_pipeline_budget_cap_enforcement` |
| **PIPE-09** | Database migration executed during active traffic | Strict expand-migrate-contract methodology; zero destructive single-step migrations | M | Phase 11 | `test_migration_expand_contract_drill` |
| **PIPE-10** | Playwright memory leaks or zombie Chromium instances | Recycle browser process every 50 pages; container resource limits; watchdog script | I | Phase 11 | `test_browser_pool_process_recycling` |
| **PIPE-11** | Celery Beat scheduler overlap or clock skew | Distributed Redis lock; ensure exactly one active executing instance per job key | I | Phase 3 | `test_pipeline_scheduler_redis_lock` |
| **PIPE-12** | Partial collection run success | Mark job status `partial`; log per-stage completion metrics; downstream consumes committed rows | I | Phase 11 | `test_pipeline_partial_job_handling` |
| **PIPE-13** | Exceptionally large raw API response payloads | Compress via zstd; upload to S3; store cryptographic hash and S3 object key in DB | U | Phase 3 | `test_pipeline_s3_raw_payload_storage` |

### 4.6 Search and User Experience Scenarios (SRCH)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **SRCH-01** | Typo, dialect alias, or Indic city search ("Jaypur", "Bombay", "जयपुर") | Resolve via `city_aliases` + trigram search; provide "Did you mean?" suggestions | E | Phase 8, 9 | `test_search_city_alias_resolution` |
| **SRCH-02** | Search filters yield zero matching advertisers | Render friendly empty state explaining active filter impact; provide "Reset Filters" action | E | Phase 9 | `test_ui_empty_state_actionable_reset` |
| **SRCH-03** | Query matches extremely large result set (> 10,000 advertisers) | Enforce keyset pagination; maximum page size 100; virtualized table rendering in UI | I | Phase 8, 9 | `test_search_keyset_virtualized_render` |
| **SRCH-04** | City crawl snapshot is out of date (> 14 days) | Prominent stale-data warning badge on city dashboard; background refresh enqueue | E | Phase 8, 9 | `test_ui_stale_data_warning_banner` |
| **SRCH-05** | Malicious insider attempts bulk contact harvesting | Mask contacts by default; enforce daily per-user reveal quotas; audit log; anomaly alerts | S | Phase 8, 10| `test_security_contact_reveal_quota_limit` |
| **SRCH-06** | Large export request (> 10,000 records) | Asynchronous Celery export job; streaming CSV write; cap at 50k without admin override; expiring S3 link | I | Phase 10 | `test_export_async_streaming_generation` |
| **SRCH-07** | Indic scripts render improperly or fail ligatures | Load Google Noto webfonts; set explicit container `lang` attributes | E | Phase 9 | `test_ui_indic_font_rendering` |
| **SRCH-08** | City dashboard queries exhibit high latency | Precompute daily rollups; maintain PostgreSQL materialized views; 5-minute Redis cache | I | Phase 8 | `test_search_city_cache_p95_budget` |
| **SRCH-09** | Concurrent category modifications by two users | Optimistic concurrency control via `version` column; return 409 Conflict | I | Phase 8 | `test_api_optimistic_locking_conflict` |
| **SRCH-10** | Mobile viewports and screen reader compatibility | Fully responsive mobile CSS; keyboard navigable controls; WCAG 2.2 AA accessibility | E | Phase 9 | `test_ui_wcag_accessibility_audit` |
| **SRCH-11** | City cohort contains sparse data in comparison view | Display insufficient-sample warning banner; grey out scorecards for cities with $< 200$ sample | E | Phase 9 | `test_ui_insufficient_sample_banner` |

### 4.7 Security and Threat Mitigation Scenarios (SEC)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **SEC-01** | SSRF targeting private IPs, AWS/GCP metadata (`169.254.169.254`), or loopback | Pre-connect DNS IP resolution; reject private/link-local/loopback IPs; re-validate redirects | S | Phase 6 | `test_security_ssrf_egress_blocking` |
| **SEC-02** | Stored XSS via malicious ad body copy or advertiser name | Rely solely on React JSX automatic escaping; forbid `dangerouslySetInnerHTML`; strict CSP | S | Phase 9 | `test_security_xss_payload_escaping` |
| **SEC-03** | CSV / Excel formula injection in export files | Prefix cells starting with dangerous trigger characters (`=`, `+`, `-`, `@`, tab, CR) with single quote | S | Phase 10 | `test_security_csv_formula_injection_guard` |
| **SEC-04** | SQL injection attempts via search filters | Parameterized queries enforced via SQLAlchemy ORM; automated linter rejects raw SQL strings | S | Phase 8 | `test_security_sql_injection_defense` |
| **SEC-05** | Prompt injection attacks contained within scraped HTML | LLM has zero executable tools and zero access to secrets; validate structured JSON output; strip HTML | S | Phase 6 | `test_security_prompt_injection_isolation` |
| **SEC-06** | Secrets or API tokens committed to repository or logs | Redaction filters in `structlog`; automated `gitleaks` checks in CI; `.env.example` templates | S | Phase 11 | `test_security_secret_leak_prevention` |
| **SEC-07** | Insecure Direct Object References (IDOR) on export artifacts | Validate user ownership of requested export UUID; RBAC permission checks | S | Phase 8, 10| `test_security_idor_export_authorization` |
| **SEC-08** | Malicious or compromised upstream dependency version | Strictly lock dependency hashes; enforce 14-day cool-off rule on new releases; automated audits | S | Phase 11 | `test_security_supply_chain_audit` |
| **SEC-09** | Malicious exploits in client sites during headless browser fetch | Run Playwright in unprivileged, sandboxed Docker container; disable downloads; non-root user | S | Phase 6 | `test_security_browser_sandbox_isolation` |
| **SEC-10** | Personal PII leaked to application stdout or log aggregators | Contact phone and email strings scrubbed from loggers; log only SHA-256 prefixes | U | Phase 6 | `test_security_log_pii_redaction_filter` |
| **SEC-11** | Database backups contain unprotected personal contact data | Enforce AES-256 encryption on backup volumes; role-based access; automated 90-day retention | M | Phase 12 | `test_security_backup_encryption_audit` |
| **SEC-12** | Brute-force credential stuffing or public opt-out flooding | Redis IP rate limiting; cryptographic verification links sent via email/SMS | S | Phase 10 | `test_security_optout_rate_limiting` |

### 4.8 Legal and Regulatory Compliance Scenarios (LEG)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **LEG-01** | Business submits valid opt-out or takedown request | Verify requester identity; write hash to `suppression`; purge raw contacts; block re-crawling | E | Phase 10 | `test_legal_optout_suppression_cycle` |
| **LEG-02** | Data principal exercises full "right to be forgotten" / erasure | Cascade erasure across `contacts` and `advertisers`; retain only cryptographic suppression hash | I | Phase 10 | `test_legal_complete_erasure_cascade` |
| **LEG-03** | Data minimization violation (PAN, Aadhaar, personal accounts) | Database schema strictly forbids; regex extractor excludes; automated CI check | U | Phase 6 | `test_legal_national_id_exclusion` |
| **LEG-04** | Commercial lead data misused beyond defined B2B purpose | User terms of service agreement; export audit watermarking; logging of revealed records | M | Phase 10 | `test_legal_export_watermark_present` |
| **LEG-05** | National Do-Not-Disturb (DND) / TRAI telecom telemarketing rules | Include `dnd_status` column in export schema; UI warning reminding users of TRAI compliance | M | Phase 12 | `test_legal_dnd_status_export_column` |
| **LEG-06** | WhatsApp Business outbound messaging policy compliance | Mandatory UI notice clarifying WhatsApp opt-in rules; zero integrated messaging features | M | Phase 12 | `test_legal_whatsapp_policy_disclaimer` |
| **LEG-07** | High-risk sensitive categories (loans, credit, medical, political) | Assign sensitive risk flag; exclude from general marketing lead lists by default | I | Phase 7 | `test_legal_sensitive_category_isolation` |
| **LEG-08** | Ad creative copyright and intellectual property protection | Persist ad copy text, low-res thumbnail, and canonical Meta permalink only; no media mirroring | M | Phase 12 | `test_legal_creative_permalink_only` |
| **LEG-09** | Legal notice or platform cease-and-desist received | Trigger global collection kill switch; disable specific adapter; execute `purge-by-source` | M | Phase 12 | `test_legal_kill_switch_purge_drill` |
| **LEG-10** | Security incident or personal data breach occurs | Follow formalized incident response runbook; prepare report within DPDP 72-hour notification SLA | M | Phase 12 | `runbook_breach_response_drill` |

### 4.9 Analytics and Market Intelligence Scenarios (ANA)

| ID | Scenario | Required Handling | Test | Owner Phase | Test ID |
|---|---|---|---|---|---|
| **ANA-01** | Small-sample cities (e.g. Jaipur vs Mumbai) distort comparison | Use per-capita and per-advertiser ratios; enforce `MIN_SAMPLE`; grey out under-sampled scores | U | Phase 7 | `test_analytics_small_sample_guards` |
| **ANA-02** | Ad counts inflated by identical collation variants | Group by `collation_id` and content hash; count distinct advertisers and creative variants | U | Phase 7 | `test_analytics_collation_deduplication` |
| **ANA-03** | Spam floods of automated, near-identical ad variants | Deduplicate by text content hash; winsorize advertiser active ad counts at $p95$ | U | Phase 7 | `test_analytics_spam_flood_winsorization` |
| **ANA-04** | Seasonal advertising spikes (Diwali, festive sales, IPL) | Compare identical historical trailing windows; display contextual holiday annotations | M | Phase 7 | `test_analytics_seasonality_windowing` |
| **ANA-05** | Mumbai corporate HQ misattribution inflates metropolitan score | Scope filter defaults strictly to local + regional advertisers; national campaigns segregated | I | Phase 7 | `test_analytics_hq_bias_segregation` |
| **ANA-06** | Right-censored ad longevity (active ads have not yet stopped) | Restrict analysis to ads launched $\ge 30$ days ago; treat running ads as right-censored | U | Phase 7 | `test_analytics_right_censored_longevity` |
| **ANA-07** | User or stakeholder demand to view commercial ad spend | **Strictly refuse.** Display permanent UI disclosure clarifying Meta does not publish spend | E | Phase 7, 9 | `test_analytics_no_spend_disclosure_copy` |
| **ANA-08** | Score instability resulting from small five-city cohort | Normalize using cross-city median ratio scaling with $\log_2$ clamping; show raw values | U | Phase 7 | `test_analytics_median_ratio_stability` |
| **ANA-09** | Different snapshot freshness across evaluated cities | Enforce uniform snapshot alignment: comparison requires identical calculation timestamp | I | Phase 7 | `test_analytics_snapshot_alignment_gate` |
| **ANA-10** | Business category taxonomy evolves or introduces sub-sectors | Version category taxonomy; execute background backfill task to update historical records | I | Phase 7 | `test_analytics_taxonomy_version_backfill` |

## 5. Edge-Case IDs Referenced
- All 115 edge-case IDs cataloged across Sections 4.1 through 4.9 above.

## 6. Open Questions
- None. Every ID from Section 12 is accounted for with an owner phase and designated test identifier.

## 7. Acceptance Checklist
- [x] All 19 SRC edge cases mapped with owner phase and test ID.
- [x] All 13 GEO edge cases mapped with owner phase and test ID.
- [x] All 20 CON edge cases mapped with owner phase and test ID.
- [x] All 7 ENT edge cases mapped with owner phase and test ID.
- [x] All 13 PIPE edge cases mapped with owner phase and test ID.
- [x] All 11 SRCH edge cases mapped with owner phase and test ID.
- [x] All 12 SEC edge cases mapped with owner phase and test ID.
- [x] All 10 LEG edge cases mapped with owner phase and test ID.
- [x] All 10 ANA edge cases mapped with owner phase and test ID.
- [x] Exactly 115 edge-case rows populated without omissions.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

