# REST API Specification — AdAtlas India

## 1. Purpose
Define the HTTP interface, resource endpoints, request parameters, response schemas, error models, and role-based permissions for the AdAtlas backend service.

## 2. Scope
Applies to all external and BFF-accessible endpoints under the `/api/v1` namespace, including public compliance forms, internal marketing operations, and administrative controls.

## 3. Decisions (Link ADRs)
- **ADR-0005:** Auth.js Bearer JWT Verification & RBAC Permissions.
- **ADR-0013:** Keyset Pagination & PostgreSQL Trigram Search API.

## 4. Detailed Design

### 4.1 General API Conventions
- **Base Route:** `/api/v1`
- **Transport & Security:** HTTPS only; strict CORS configuration; mandatory `X-Request-Id` header returned on every response.
- **Content Types:** `application/json` default; RFC 9457 `application/problem+json` for error states.
- **Pagination Strategy:** Keyset / cursor-based pagination (`cursor: string`, `limit: integer`). Default limit: 20; maximum limit: 100.
- **Timestamps:** ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SSZ`).
- **Contact Masking Default:** Standard search and profile endpoints deliver masked contacts (`+91 98•••• ••21`, `in••••@domain.com`). Unmasking requires an explicit POST to the reveal endpoint.

### 4.2 Role-Based Access Control (RBAC) Matrix
| Endpoint Group | Viewer | Marketing | Compliance | Admin | Public |
|---|---|---|---|---|---|
| City Discovery & Search (`/cities`, `/search`) | Yes | Yes | Yes | Yes | No |
| Advertiser Detail & Masked Contacts | Yes | Yes | Yes | Yes | No |
| Contact Reveal (`/contacts/reveal`) | No | Yes (Quota) | Yes (Audit) | Yes (Audit) | No |
| CSV/XLSX Export Generation | No | Yes (Quota) | Yes | Yes | No |
| Public Opt-Out & Takedown (`/optout`) | Yes | Yes | Yes | Yes | Yes |
| Admin Operations (`/admin/*`) | No | No | Read-Only | Full Access | No |

### 4.3 Endpoint Catalog

#### 4.3.1 Reference & Search
- **`GET /api/v1/cities`**
  - *Description:* List active cities, state codes, STD area codes, and data snapshot freshness.
  - *Role:* `viewer+`
- **`GET /api/v1/cities/resolve?q={alias}`**
  - *Description:* Resolves arbitrary text (e.g. "Bombay", "Jaypur", "Pink City", "जयपुर") to a normalized `city_id` using exact and trigram matching. Returns "Did you mean?" suggestions when confidence is moderate.
  - *Role:* `viewer+`
- **`GET /api/v1/search`**
  - *Description:* Search and filter attributed advertisers.
  - *Query Parameters:*
    - `city` (string, required): City slug or alias.
    - `q` (string, optional): Keyword query matched against page name or body text.
    - `category` (string[], optional): L1/L2 category filter.
    - `tier` (string, default: `confirmed,probable`): Attribution tier filter.
    - `scope` (string, default: `local,regional`): Geographic operational scope.
    - `has_phone` (bool, optional): Require verified phone presence.
    - `has_email` (bool, optional): Require verified email presence.
    - `has_whatsapp` (bool, optional): Require WhatsApp CTA or verified number.
    - `active_ads_min` / `active_ads_max` (int, optional): Active ad volume bounds.
    - `first_seen_after` (date, optional): Filter newly active advertisers.
    - `cta` (string[], optional): Filter by CTA types (e.g. `WHATSAPP`, `CALL_NOW`).
    - `language` (string[], optional): Filter by ad languages.
    - `include_satellite` (bool, default: `false`): Include peripheral suburbs.
    - `sort` (enum: `relevance`, `active_ads`, `newest`, `contact_score`).
    - `cursor` (string, optional): Keyset pagination token.
    - `limit` (int, default: 20, max: 100).
  - *Role:* `viewer+`

#### 4.3.2 Advertiser Details & Contacts
- **`GET /api/v1/advertisers/{id}`**
  - *Description:* Full advertiser profile, page details, categories, attributed city links, confidence score, and supporting evidence list.
  - *Role:* `viewer+`
- **`GET /api/v1/advertisers/{id}/ads`**
  - *Description:* Chronological ad history, status (active/inactive), copy, headline, CTA, landing domain, and Meta permalink.
  - *Role:* `viewer+`
- **`GET /api/v1/advertisers/{id}/contacts`**
  - *Description:* List associated contacts in **masked format** with verification status, subtype, confidence, and risk flags.
  - *Role:* `viewer+`
- **`POST /api/v1/advertisers/{id}/contacts/reveal`**
  - *Description:* Requests full, unmasked contact information for a specific advertiser.
  - *Mechanism:* Checks daily reveal quota (`users.reveal_quota_daily`), queries suppression registry, logs an immutable entry in `audit_log`, decrements remaining quota, and returns plaintext contacts with full provenance URLs.
  - *Role:* `marketing+`
- **`POST /api/v1/advertisers/{id}/feedback`**
  - *Description:* Submit feedback regarding erroneous city attribution or incorrect phone/email data.
  - *Payload:* `{"kind": "wrong_city" | "wrong_contact" | "do_not_contact", "details": string}`
  - *Role:* `marketing+`

#### 4.3.3 City Comparison & Insights
- **`GET /api/v1/compare`**
  - *Description:* Multi-city comparison matrix.
  - *Query Parameters:* `cities` (comma-separated slugs), `profile` (`outreach` | `maturity` | `low_competition`), optional custom `weights` (`C:0.3,S:0.2...`).
  - *Response:* Scores (0–100), raw proxy metrics, top positive/negative contributing factors, and sufficiency warning banners (`sample_ok: false`).
  - *Role:* `viewer+`
- **`GET /api/v1/insights/city/{slug}`**
  - *Description:* City dashboard analytics: trailing 90-day advertiser growth time series, category concentration HHI, and top emerging advertisers.
  - *Role:* `viewer+`

#### 4.3.4 Exports & Saved Searches
- **`POST /api/v1/exports`**
  - *Description:* Enqueue an asynchronous export job for a filtered advertiser search.
  - *Payload:* Filter parameters identical to `/search`, plus `format` (`csv` | `xlsx`).
  - *Response:* `{"export_id": "uuid", "status": "pending"}`
  - *Role:* `marketing+`
- **`GET /api/v1/exports/{id}`**
  - *Description:* Check export generation status. Returns a signed, time-limited S3 download URL (expires in 15 minutes) upon completion.
  - *Role:* `marketing+` (Row-level ownership enforced)

#### 4.3.5 Compliance & Public Opt-Out
- **`POST /api/v1/optout`**
  - *Description:* **Public endpoint.** Enables business owners or individuals to submit a suppression request for a phone number, email, domain, or Meta page.
  - *Payload:* `{"kind": "phone" | "email" | "domain" | "page", "value": string, "reason": string}`
  - *Workflow:* Validates rate limits, sends verification token/link to the contact, and on verification, hashes the target value into `suppression` and purges raw records from `contacts`.
  - *Role:* `public` (Rate limited: 5 requests / IP / hour)

#### 4.3.6 Operations & Administration
- **`GET /api/v1/admin/jobs`** · **`POST /api/v1/admin/jobs`** · **`POST /api/v1/admin/jobs/{id}/cancel`**
  - *Description:* Inspect active scrape runs, schedule manual sweeps, or cancel in-flight jobs.
- **`GET /api/v1/admin/budgets`** · **`PUT /api/v1/admin/budgets/{scope}`**
  - *Description:* Inspect and configure spend caps for Adapter B, Google Places, and LLM inference.
- **`POST /api/v1/admin/kill-switch`**
  - *Description:* Emergency global collection halt. Immediately halts active Celery ingestion workers.
- **`GET /api/v1/admin/dead-letters`** · **`POST /api/v1/admin/dead-letters/{id}/replay`**
  - *Description:* Inspect poison task payloads and replay tasks after bug remediation.
- **`GET /healthz`** · **`GET /readyz`** · **`GET /metrics`**
  - *Description:* Infrastructure liveness probe, database/redis readiness check, and Prometheus metric scrape endpoint.

### 4.4 RFC 9457 Error Response Format
All 4xx and 5xx responses must return `application/problem+json`:
```json
{
  "type": "https://errors.adatlas.in/quota-exceeded",
  "title": "Daily Reveal Quota Exceeded",
  "status": 429,
  "detail": "You have revealed 200 of your allotted 200 contacts for today. Quota resets at 00:00 UTC.",
  "instance": "/api/v1/advertisers/18231/contacts/reveal",
  "request_id": "req_01JBM84PX2Z8K7W"
}
```

## 5. Edge-Case IDs Referenced
- `SRCH-01` (Typo/alias city resolution with trigram)
- `SRCH-03` (Keyset pagination for deep result sets)
- `SRCH-05` (Contact reveal quota and rate limiting)
- `SEC-04` (Parameterized database query enforcement)
- `SEC-07` (IDOR authorization check on export downloads)
- `LEG-01` (Public opt-out endpoint processing)

## 6. Open Questions
- Generating OpenAPI 3.1 specification schema (`docs/openapi.json`) during Phase 1 FastAPI setup.

## 7. Acceptance Checklist
- [x] All REST endpoints, verbs, paths, and query parameters cataloged.
- [x] Keyset pagination standards specified.
- [x] Contact masking and quota reveal flow documented.
- [x] Public opt-out API and verification workflow specified.
- [x] RFC 9457 error schema and RBAC permission matrix defined.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

