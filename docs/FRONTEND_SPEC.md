# Frontend Architecture & UI/UX Specification — AdAtlas India

## 1. Purpose
Define the client-side user experience, page route hierarchy, component structure, state contracts, accessibility standards, and typography requirements for the AdAtlas Next.js web application.

## 2. Scope
Applies to the entire `frontend/` repository codebase, covering all public, authenticated, and administrative views.

## 3. Decisions (Link ADRs)
- **ADR-0005:** Auth.js Session BFF Pattern.
- **ADR-0007:** Goal-Driven Weight Sliders in Comparison Views.

## 4. Detailed Design

### 4.1 Application Route Map
| Route Path | View Type | Core Functionality & Primary Components |
|---|---|---|
| `/` | Public / Auth | **Hero Discovery:** City selector dropdown with intelligent typeahead alias resolution, category selector, keyword search bar, saved searches quick-access drawer. |
| `/city/[slug]` | Authenticated | **City Intelligence & Advertiser Directory:** Virtualized table of attributed advertisers, left-side filter rail (categories, active ad volume, contact types, scope, satellite toggle), active-filter chips, data snapshot freshness badge, CSV/XLSX export modal. |
| `/advertiser/[id]` | Authenticated | **Advertiser Deep-Dive:** Brand identity summary, "Why this city?" evidence drawer, chronological ad history with copy/thumbnails/Meta permalinks, verified contact cards with confidence meters and provenance links, feedback submission modal ("Wrong contact", "Wrong city"). |
| `/compare` | Authenticated | **City Vitality Benchmark:** Multi-city picker (2–5 cities), goal profile selector (Outreach, Maturity, Low Competition), interactive weight sliders, composite scorecards, radar charts and comparative bar visualizations, raw metric table, explainability "Why this city scored higher" panel, insufficient-data warning banners. |
| `/exports` | Authenticated | **Export Center:** Chronological history of user-requested exports, row count summaries, signed expiring download links (7-day validity). |
| `/optout` | Public | **Public Suppression Portal:** Self-service form allowing businesses or individuals to submit takedown requests for phones, emails, domains, or Meta pages with OTP/email verification. |
| `/admin/jobs` | Admin | Real-time monitoring of Celery collection batches, cursor checkpoints, and error rates. |
| `/admin/budgets` | Admin | Spend caps, month-to-date API consumption, and emergency collection kill switch. |
| `/admin/review` | Admin | Human review queues for conflicting geo attributions (GEO-07) and ambiguous entity merges (ENT-02). |
| `/admin/dead-letters`| Admin | Inspection and replay interface for failed queue tasks. |

### 4.2 City Results Wireframe & Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  AdAtlas     [ Jaipur ▾ ]  [ Search keyword... ]  [ All Categories ▾ ]  (User) │
├───────────────┬──────────────────────────────────────────────────────────┤
│ FILTERS       │ 1,284 Active Advertisers in Jaipur                       │
│ ☑ Confirmed   │ Snapshot refreshed: 2 hours ago   [ ⬇ Export to CSV/XLSX ]│
│ ☑ Probable    │ Active filters: [ Local & Regional ✕ ] [ Has Phone ✕ ]    │
│ Scope:        ├──────────────────────────────────────────────────────────┤
│ (•) Local     │ Page Name          Category    Ads  First Seen  Contacts │
│ ( ) Regional  │ ──────────────────────────────────────────────────────── │
│ ( ) All India │ Example Jewellers  Jewellery    14  12 Aug 2026 ☎ ✉ 💬 🌐│
│               │ Pink City Coaching Education     6  03 Oct 2026 ☎ ✉    🌐│
│ Contact Type: │ Royal Decor Hub    Furniture     9  15 Sep 2026 ☎    💬 🌐│
│ ☑ Phone       │ Jaipur Craft Villa Handicrafts   4  28 Oct 2026 ☎ ✉ 💬 🌐│
│ ☑ WhatsApp    │ ...                                                      │
│ ☐ Email       ├──────────────────────────────────────────────────────────┤
│               │ [ Reveal Selected Contacts (Consumes 4 / 200 Daily Quota) ]│
│ ☐ New in 30d  │ Keyset pagination: < Prev  |  Next > (Showing 1-20 of 1284) │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### 4.3 Component State Management & Visual Contracts
Every data-driven UI component must explicitly handle five discrete visual states:
1. **Loading State:** Skeleton wireframes matching exact component layout dimensions. Pulse animations. Full-page spinner screens are prohibited.
2. **Empty State:** Distinctive, helpful empty states specifying *why* zero results matched:
   - "No advertisers found matching current filters. Try removing the 'New in last 30 days' filter."
   - Provide a one-click "Reset All Filters" button (SRCH-02).
3. **Error State:** Non-technical error message displaying the unique `request_id` for operator support and an inline "Retry" button.
4. **Stale Data Warning:** If a city's latest crawl snapshot is older than 14 days, a yellow warning banner appears above results: *"Data for this city was last refreshed on [Date]. A refresh job is scheduled."* (SRCH-04).
5. **Data Sufficiency Banner:** On the comparison view, if a city has `< MIN_SAMPLE` confirmed advertisers, display a greyed card with the banner: *"Insufficient sample size for statistically reliable comparative scoring."* (ANA-01, SRCH-11).

### 4.4 Typography, Indic Scripts & Accessibility
- **Font Strategy:**
  - Latin text: `Noto Sans`
  - Devanagari script (Hindi, Marathi): `Noto Sans Devanagari`
  - Bengali script: `Noto Sans Bengali`
  - Kannada script: `Noto Sans Kannada`
- **Script Handling:** UI containers rendering regional languages must declare appropriate HTML `lang` attributes (e.g. `<span lang="hi">जयपुर</span>`) to ensure correct font glyph rendering and screen reader pronunciation (SRCH-07).
- **WCAG 2.2 AA Compliance:**
  - High-contrast color palette (contrast ratio $\ge 4.5:1$ for normal text).
  - State must not be communicated solely by color (e.g., green vs red); use explicit text labels and semantic icons.
  - Full keyboard navigability across search inputs, filter checkboxes, and virtualized table rows.

### 4.5 Security & Data Presentation Safeguards
- **No Raw HTML Execution:** Never render ad copy or scraped web snippets via `dangerouslySetInnerHTML`. Rely solely on standard React JSX string escaping to eliminate XSS risks (SEC-02).
- **Mandatory Comparison Disclosure Copy:** On `/compare` and all scorecard modules, display the permanent notice:
  > *"Based on Meta Ad Library activity. Commercial ad spend and impressions are not published by Meta outside the EU and are not estimated."*

## 5. Edge-Case IDs Referenced
- `SRCH-01` (Typo and vernacular city search resolution)
- `SRCH-02` (Helpful empty states and suggestions)
- `SRCH-03` (Virtualized table rendering for high-volume datasets)
- `SRCH-04` (Stale data warning indicators)
- `SRCH-05` (Contact masking and reveal quota UX)
- `SRCH-07` (Indic script typography rendering)
- `SRCH-10` (Responsive mobile layout and WCAG accessibility)
- `SRCH-11` (Insufficient-sample city comparison banners)
- `SEC-02` (XSS elimination via JSX escaping)
- `ANA-07` (Commercial spend disclosure copy)

## 6. Open Questions
- Finalizing the choice of visualization library (Recharts vs ECharts) during Phase 9 frontend prototype benchmarking.

## 7. Acceptance Checklist
- [x] Application route map and component roles specified.
- [x] Text wireframe illustrating city results layout created.
- [x] Five discrete component states (Loading, Empty, Error, Stale, Insufficient) defined.
- [x] Typography stack and Indic script language attributes established.
- [x] Accessibility and XSS prevention requirements documented.
- [x] All 10 referenced edge-case IDs cross-referenced.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

