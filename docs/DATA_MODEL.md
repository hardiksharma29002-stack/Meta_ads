# Database Data Model & Schema Specification — AdAtlas India

## 1. Purpose
Define the authoritative relational data schema, integrity constraints, indexing strategies, entity-relationship diagrams, and retention schedules for the AdAtlas PostgreSQL database.

## 2. Scope
Covers all persistent relational tables across reference data, core entities, contact enrichment, operations/ingestion, analytics aggregates, and application security.

## 3. Decisions (Link ADRs)
- **ADR-0002:** Data Minimization & Exclusion of PAN from GSTIN Storage.
- **ADR-0011:** Data Retention Schedules across Raw, Operational, and Contact Tiers.
- **ADR-0013:** Trigram & Full-Text Search Indexing in PostgreSQL.

## 4. Detailed Design

### 4.1 Entity-Relationship Overview

```mermaid
erDiagram
    CITIES ||--o{ CITY_ALIASES : has
    CITIES ||--o{ PINCODE_CITY_MAP : covers
    CITIES ||--o{ ADVERTISER_CITY_LINKS : attributed_to
    CITIES ||--o{ CITY_METRICS_DAILY : aggregates
    CATEGORIES ||--o{ CATEGORIES : parent_of
    CATEGORIES ||--o{ ADVERTISERS : classifies
    ADVERTISERS ||--o{ ADVERTISER_NAME_HISTORY : tracks
    ADVERTISERS ||--o{ ADVERTISER_CITY_LINKS : linked_with
    ADVERTISERS ||--o{ ADS : runs
    ADVERTISERS ||--o{ CONTACTS : owns
    CONTACTS ||--o{ CONTACT_EVIDENCE : corroborated_by
    SCRAPE_JOBS ||--o{ RAW_PAYLOADS : stores
    USERS ||--o{ AUDIT_LOG : generates
    USERS ||--o{ EXPORTS : requests
    USERS ||--o{ SAVED_SEARCHES : saves

    CITIES {
        int id PK
        string slug UK
        string name
        string state_name
        string gst_state_code
        string std_code
        int urban_population
    }

    ADVERTISERS {
        bigint id PK
        string meta_page_id UK
        string page_name
        string page_name_norm
        string primary_domain
        int active_ad_count
        string status
    }

    ADS {
        bigint id PK
        string meta_ad_id UK
        bigint advertiser_id FK
        string source
        string ad_type
        string status
        bytea content_hash
    }

    CONTACTS {
        bigint id PK
        bigint advertiser_id FK
        string type
        string subtype
        string value_norm
        bytea value_hash UK
        float confidence
        string verification
    }

    SUPPRESSION {
        bytea value_hash PK
        string kind
        string reason
        timestamp requested_at
    }
```

### 4.2 Comprehensive DDL Schema

```sql
-- Required Extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS citext;

-- ============================================================================
-- 1. REFERENCE DATA
-- ============================================================================

CREATE TABLE cities (
  id SMALLSERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,                       -- e.g., 'mumbai', 'jaipur'
  name TEXT NOT NULL,                             -- e.g., 'Jaipur'
  state_name TEXT NOT NULL,                       -- e.g., 'Rajasthan'
  gst_state_code CHAR(2) NOT NULL,                 -- e.g., '08'
  std_code TEXT NOT NULL,                          -- e.g., '0141'
  lat NUMERIC(8,5),
  lon NUMERIC(8,5),
  urban_population INT,
  population_source TEXT,
  population_year SMALLINT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE city_aliases (
  city_id SMALLINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  alias CITEXT NOT NULL,
  lang TEXT,                                       -- 'en', 'hi', 'bn', 'kn', 'mr'
  kind TEXT NOT NULL,                              -- 'name' | 'old_name' | 'transliteration' | 'locality' | 'satellite'
  PRIMARY KEY (city_id, alias)
);
CREATE INDEX idx_city_aliases_trgm ON city_aliases USING gin (alias gin_trgm_ops);

CREATE TABLE pincode_city_map (
  pincode CHAR(6) PRIMARY KEY,
  city_id SMALLINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  locality TEXT,
  is_core BOOLEAN NOT NULL DEFAULT TRUE            -- FALSE indicates satellite / suburb
);
CREATE INDEX idx_pincode_city ON pincode_city_map (city_id);

CREATE TABLE categories (
  id SMALLSERIAL PRIMARY KEY,
  parent_id SMALLINT REFERENCES categories(id) ON DELETE SET NULL,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  taxonomy_version SMALLINT NOT NULL DEFAULT 1
);

-- ============================================================================
-- 2. CORE ADVERTISER & AD ENTITIES
-- ============================================================================

CREATE TABLE advertisers (
  id BIGSERIAL PRIMARY KEY,
  meta_page_id TEXT UNIQUE NOT NULL,
  page_name TEXT NOT NULL,
  page_name_norm TEXT NOT NULL,                    -- lower, unaccented, stripped suffixes
  page_url TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  primary_domain TEXT,
  category_id SMALLINT REFERENCES categories(id) ON DELETE SET NULL,
  category_conf REAL,
  scope TEXT DEFAULT 'unknown',                   -- 'local' | 'regional' | 'national' | 'unknown'
  risk_flags TEXT[] NOT NULL DEFAULT '{}',         -- e.g., {'scam', 'gambling', 'political'}
  entity_group_id BIGINT,                          -- Cluster ID for merged duplicates
  status TEXT NOT NULL DEFAULT 'active',           -- 'active' | 'dormant' | 'suppressed' | 'merged'
  active_ad_count INT NOT NULL DEFAULT 0,
  total_ad_count INT NOT NULL DEFAULT 0,
  first_seen_at TIMESTAMPTZ NOT NULL,
  last_seen_at TIMESTAMPTZ NOT NULL,
  version INT NOT NULL DEFAULT 1                   -- Optimistic locking counter
);
CREATE INDEX idx_adv_name_norm_trgm ON advertisers USING gin (page_name_norm gin_trgm_ops);
CREATE INDEX idx_adv_primary_domain ON advertisers (primary_domain);
CREATE INDEX idx_adv_status_active_ads ON advertisers (status, active_ad_count DESC);

CREATE TABLE advertiser_name_history (
  advertiser_id BIGINT NOT NULL REFERENCES advertisers(id) ON DELETE CASCADE,
  page_name TEXT NOT NULL,
  seen_from TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (advertiser_id, page_name)
);

CREATE TABLE advertiser_city_links (
  advertiser_id BIGINT NOT NULL REFERENCES advertisers(id) ON DELETE CASCADE,
  city_id SMALLINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  tier TEXT NOT NULL,                              -- 'confirmed' | 'probable' | 'weak'
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  branch_count SMALLINT DEFAULT 1,
  evidence JSONB NOT NULL,                         -- Array of {kind, strength, source_ref, observed_at}
  model_version TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (advertiser_id, city_id)
);
CREATE INDEX idx_acl_city_tier_conf ON advertiser_city_links (city_id, tier, confidence DESC);

CREATE TABLE ads (
  id BIGSERIAL PRIMARY KEY,
  meta_ad_id TEXT UNIQUE NOT NULL,
  advertiser_id BIGINT NOT NULL REFERENCES advertisers(id) ON DELETE CASCADE,
  source TEXT NOT NULL,                            -- Adapter name e.g., 'adapter_a', 'adapter_b'
  ad_type TEXT NOT NULL,                           -- 'commercial' | 'political_issue'
  status TEXT NOT NULL,                            -- 'active' | 'inactive' | 'disappeared'
  delivery_start TIMESTAMPTZ,
  delivery_stop TIMESTAMPTZ,
  first_seen_at TIMESTAMPTZ NOT NULL,
  last_seen_at TIMESTAMPTZ NOT NULL,
  disappeared_at TIMESTAMPTZ,
  body_text TEXT,
  headline TEXT,
  cta TEXT,
  landing_url TEXT,
  landing_domain TEXT,
  media_type TEXT,
  platforms TEXT[],
  languages TEXT[],
  collation_id TEXT,
  collation_count INT DEFAULT 1,
  content_hash BYTEA NOT NULL,                     -- SHA-256 of normalized body, headline, CTA, domain
  -- Political / Issue Transparency Attributes (Official API only)
  spend_lower BIGINT,
  spend_upper BIGINT,
  impressions_lower BIGINT,
  impressions_upper BIGINT,
  currency TEXT,
  raw_payload_id BIGINT,
  schema_version SMALLINT NOT NULL DEFAULT 1
);
CREATE INDEX idx_ads_advertiser_status ON ads (advertiser_id, status);
CREATE INDEX idx_ads_landing_domain ON ads (landing_domain);
CREATE INDEX idx_ads_content_hash ON ads (content_hash);

-- Partitioned observation log for historical longevity tracking
CREATE TABLE ad_observations (
  ad_id BIGINT NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  run_id BIGINT NOT NULL,
  PRIMARY KEY (ad_id, observed_at)
) PARTITION BY RANGE (observed_at);

-- ============================================================================
-- 3. CONTACT ENRICHMENT & SUPPRESSION
-- ============================================================================

CREATE TABLE contacts (
  id BIGSERIAL PRIMARY KEY,
  advertiser_id BIGINT NOT NULL REFERENCES advertisers(id) ON DELETE CASCADE,
  city_id SMALLINT REFERENCES cities(id) ON DELETE SET NULL,
  type TEXT NOT NULL CHECK (type IN ('phone','email','whatsapp','website','instagram','facebook','linkedin','youtube','x')),
  subtype TEXT,                                    -- 'mobile' | 'landline' | 'tollfree' | 'role_email' | 'free_mail'
  value_raw TEXT NOT NULL,
  value_norm TEXT NOT NULL,                        -- E.164 phone, lower email, clean URL
  value_hash BYTEA NOT NULL,                       -- sha256(value_norm)
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  verification TEXT NOT NULL DEFAULT 'unverified', -- 'unverified' | 'syntax_ok' | 'mx_ok' | 'places_match' | 'manual'
  flags TEXT[] NOT NULL DEFAULT '{}',              -- 'shared_third_party', 'personal_data_risk', 'stale'
  first_seen_at TIMESTAMPTZ NOT NULL,
  last_seen_at TIMESTAMPTZ NOT NULL,
  last_verified_at TIMESTAMPTZ,
  UNIQUE (advertiser_id, type, value_hash)
);
CREATE INDEX idx_contacts_hash ON contacts (value_hash);
CREATE INDEX idx_contacts_adv_type ON contacts (advertiser_id, type);

CREATE TABLE contact_evidence (
  id BIGSERIAL PRIMARY KEY,
  contact_id BIGINT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  source_url TEXT NOT NULL,
  source_type TEXT NOT NULL,                       -- 'website' | 'jsonld' | 'tel_link' | 'mailto' | 'wa_link' | 'places'
  page_kind TEXT,                                  -- 'contact' | 'about' | 'footer' | 'home' | 'privacy'
  fetched_at TIMESTAMPTZ NOT NULL,
  raw_payload_id BIGINT
);
CREATE INDEX idx_evidence_contact ON contact_evidence (contact_id);

CREATE TABLE suppression (
  value_hash BYTEA PRIMARY KEY,                    -- sha256(normalized_value)
  kind TEXT NOT NULL,                              -- 'phone' | 'email' | 'domain' | 'page'
  reason TEXT NOT NULL,                            -- 'opt_out' | 'legal_takedown' | 'dnd'
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  expires_at TIMESTAMPTZ
);

-- ============================================================================
-- 4. OPERATIONS & COST CONTROL
-- ============================================================================

CREATE TABLE scrape_jobs (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,                              -- 'sweep' | 'page_expansion' | 'refresh'
  adapter TEXT NOT NULL,
  params JSONB NOT NULL,
  status TEXT NOT NULL,                            -- 'pending' | 'running' | 'succeeded' | 'partial' | 'failed' | 'blocked'
  cursor TEXT,
  attempt SMALLINT NOT NULL DEFAULT 0,
  budget_cap NUMERIC(12,2),
  cost_spent NUMERIC(12,2) NOT NULL DEFAULT 0.00,
  stats JSONB NOT NULL DEFAULT '{}',
  error TEXT,
  heartbeat_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  idempotency_key TEXT UNIQUE
);

CREATE TABLE raw_payloads (
  id BIGSERIAL PRIMARY KEY,
  job_id BIGINT REFERENCES scrape_jobs(id) ON DELETE SET NULL,
  adapter TEXT NOT NULL,
  schema_version SMALLINT NOT NULL,
  s3_key TEXT NOT NULL,
  sha256 BYTEA NOT NULL,
  bytes INT NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE dead_letters (
  id BIGSERIAL PRIMARY KEY,
  queue TEXT NOT NULL,
  task TEXT NOT NULL,
  payload JSONB NOT NULL,
  error TEXT NOT NULL,
  attempts SMALLINT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  replayed_at TIMESTAMPTZ
);

CREATE TABLE budgets (
  scope TEXT PRIMARY KEY,                          -- 'provider' | 'places' | 'llm' | 'proxy'
  period TEXT NOT NULL,                            -- 'monthly' | 'daily'
  cap NUMERIC(12,2) NOT NULL,
  spent NUMERIC(12,2) NOT NULL DEFAULT 0.00,
  resets_at TIMESTAMPTZ NOT NULL
);

-- ============================================================================
-- 5. ANALYTICS & CITY SCORING
-- ============================================================================

CREATE TABLE city_metrics_daily (
  city_id SMALLINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  day DATE NOT NULL,
  scope TEXT NOT NULL,                             -- 'all' | 'local' | 'regional'
  active_advertisers INT NOT NULL,
  new_advertisers_30d INT NOT NULL,
  active_ads INT NOT NULL,
  distinct_creatives INT NOT NULL,
  median_longevity_days REAL,
  creative_refresh_rate REAL,
  contact_coverage REAL,
  smb_share REAL,
  whatsapp_cta_share REAL,
  category_hhi REAL,
  sample_ok BOOLEAN NOT NULL DEFAULT TRUE,
  metrics_version TEXT NOT NULL,
  PRIMARY KEY (city_id, day, scope)
);

-- ============================================================================
-- 6. APPLICATION, USERS & AUDIT
-- ============================================================================

CREATE TABLE users (
  id UUID PRIMARY KEY,
  email CITEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('viewer', 'marketing', 'admin', 'compliance')),
  reveal_quota_daily INT NOT NULL DEFAULT 200,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,                            -- 'reveal' | 'export' | 'search' | 'optout_verify'
  target_type TEXT,
  target_id TEXT,
  meta JSONB,
  ip INET,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_user_action ON audit_log (user_id, action, at DESC);

CREATE TABLE exports (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  params JSONB NOT NULL,
  row_count INT,
  status TEXT NOT NULL,                            -- 'pending' | 'processing' | 'ready' | 'failed'
  s3_key TEXT,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE saved_searches (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  params JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.3 Data Retention & Archival Policy (ADR-0011)
- **Raw Payloads (`raw_payloads`):** Retained in S3/MinIO for **90 days**. Payloads older than 90 days are deleted unless tied to an active audit investigation.
- **Unverified Contacts:** If an unverified contact has not been corroborated or re-verified within **12 months**, it is deleted from the `contacts` table.
- **Audit Logs (`audit_log`):** Preserved for **24 months** to maintain comprehensive compliance records under Indian DPDP guidelines.
- **Export Artifacts (`exports`):** S3 export files expire and are permanently wiped after **7 days**.
- **Suppression Records (`suppression`):** Retained indefinitely as cryptographic hashes (`value_hash`) to ensure permanent compliance with takedown notices.

## 5. Edge-Case IDs Referenced
- `ENT-01` (Advertiser name history tracking)
- `GEO-02` (City alias trigram indexing)
- `CON-03` (Phone normalization and subtype tracking)
- `CON-20` (GSTIN storage restricted to state code)
- `LEG-01` (Suppression table and hash-based joins)
- `PIPE-01` (Idempotent upsert keys and hashes)

## 6. Open Questions
- Optimal partitioning interval for `ad_observations` (monthly vs quarterly) once live production data volume is benchmarked in Phase 3.

## 7. Acceptance Checklist
- [x] Full DDL provided with extensions, primary keys, and foreign keys.
- [x] Mermaid ER diagram accurately maps all tables and relationships.
- [x] Trigram and GIN indexes configured for fuzzy text search.
- [x] GSTIN PAN exclusion and contact masking safeguards encoded.
- [x] Data retention schedule explicitly defined across all data tiers.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

