# Geo-Attribution Engine Specification — AdAtlas India

## 1. Purpose
Specify the multi-signal probabilistic engine responsible for attributing Meta advertisers to specific Indian cities with calibrated confidence scores, evidence provenance, conflict resolution, and quality evaluation standards.

## 2. Scope
Applies to the spatial analysis pipeline (`q.geo`), evaluating advertisers against the five core target cities (Mumbai, Delhi NCT, Jaipur, Kolkata, Bengaluru) and associated satellite territories.

## 3. Decisions (Link ADRs)
- **ADR-0008:** Google Places API Integration for High-Confidence Spatial Validation.
- **ADR-0009:** Delhi NCT Metropolitan Boundaries vs Satellite NCR Suburbs.
- **ADR-0010:** Mumbai Municipal Corporation Boundaries vs Satellite MMR Suburbs.
- **ADR-0014:** Noisy-OR Multi-Signal Attribution Combining Distinct Signal Classes.

## 4. Detailed Design

### 4.1 Signal Matrix & Weights
Because Meta does not expose geo-targeting parameters, attribution relies on evidence gathered from ad creative copy, landing page markup, public registrations, and external directory corroboration.

| Signal Code | Signal Description | Primary Extraction Source | Base Strength ($s_i$) | Quality Constraints & Validation Rules |
|---|---|---|---|---|
| `SIG_PLACES` | Google Places API Exact Match | Google Places API (New) | 0.90 | Requires business name + city query agreement, valid physical address, and matching local phone. |
| `SIG_JSONLD` | Structured Postal Address (`addressLocality`, `addressRegion`) | Advertiser Website Schema.org markup | 0.85 | Extracted from `LocalBusiness` or `PostalAddress` entities; locality must match `city_aliases`. |
| `SIG_PINCODE` | 6-Digit PIN Code in Address Context | Website text, Footer, Ad Copy | 0.85 | Must appear adjacent to contextual terms ("PIN", "Pincode", "Address"); must match `pincode_city_map`. |
| `SIG_FBPAGE` | Meta Page Address / City | Facebook Page "About" | 0.80 | **DISABLED BY DEFAULT (D2).** Activated only if explicit legal sign-off is granted. |
| `SIG_STDCODE` | Landline Area Code (`0141`, `022`, `011`, `033`, `080`) | Extracted Landline Contacts | 0.60 | Mobile numbers (9-series, 8-series, 7-series) carry ZERO geographic validity and are rejected. |
| `SIG_WEBTEXT` | City Mention in Website H1, Title, or Footer | Landing Page Metadata | 0.55 | Requires prominent placement (site title or corporate footer, not incidental blog text). |
| `SIG_ADTEXT` | City Mention in Ad Headline or Primary Text | Active Ad Copy | 0.50 | Capped at 0.50. Evaluated against directional filter (penalizing "delhi to jaipur" transit phrases). |
| `SIG_GSTIN` | GSTIN 2-Digit State Code Prefix | Website Footer | 0.30 | Identifies state jurisdiction (e.g., 08=Rajasthan, 27=Maharashtra). Provides state-level evidence only. |
| `SIG_LANG` | Vernacular Regional Ad Copy Language | Ad Body Text | 0.15 | Detects regional script (e.g., Bengali, Kannada). Weak corroborating signal; never sufficient alone. |
| `SIG_SEED` | Discovery Seed Query Association | Ingestion Task | 0.10 | Weakest artifact; merely reflects search origin. Never qualifies an advertiser independently. |

### 4.2 Probabilistic Scoring Algorithm (Noisy-OR)
For each candidate city $c$, the unadjusted probability $p(c)$ is calculated across all *distinct* signal types $K$:

$$p(c) = 1 - \prod_{k \in K} (1 - \max_{i \in k} s_i)$$

#### Rules of Combination:
1. **Deduplication of Signal Classes:** If multiple signals of the same kind are observed (e.g. two separate PIN code occurrences for Jaipur), only the highest-strength signal of that kind is included in the product to prevent artificial confidence inflation.
2. **Conflict & Multi-City Penalty:**
   - If two distinct cities $c_1$ and $c_2$ both achieve $p \ge 0.60$, the advertiser is flagged as **Multi-City**:
     - Both links are retained in `advertiser_city_links`.
     - The city with the higher confidence score is designated `is_primary = true`.
     - The advertiser's `scope` is set to `regional` or `national` (unless website store-locator confirms separate distinct branch locations).
     - Conflicting records without branch confirmation are routed to `admin/review/geo` (GEO-07).
3. **Attribution Tiers:**
   - **Confirmed Tier ($p \ge 0.75$):** High confidence. Qualified for city results and lead prospecting by default.
   - **Probable Tier ($0.40 \le p < 0.75$):** Moderate confidence. Displayed in UI with a "Probable" indicator; filterable by users.
   - **Weak Tier ($p < 0.40$):** Inconclusive evidence. Excluded from city search results and city comparison aggregations by default.

### 4.3 Scope Classification
Advertisers are categorized into four geographical operational scopes:
- **Local:** Physical operation concentrated exclusively within a single city/metro area.
- **Regional:** Presence spanning 2–4 neighboring metropolitan regions or a single Indian state.
- **National:** Pan-India presence, multi-state store locators, national brand awareness, or widespread multi-language advertising campaigns.
- **Unknown:** Inadequate spatial data to establish operational scope.

### 4.4 Evaluation Set & Benchmark Protocol
To ensure high precision and prevent model degradation:
- **Benchmark Corpus:** Maintain a human-labeled evaluation dataset (`data/evaluation/geo_eval_set.json`) containing **>= 300 verified advertisers** (strictly 60 per target city, spanning local SMBs, regional chains, and national brands).
- **Quality Gate:** Automated CI runs must calculate precision and recall across the benchmark dataset:
  - **Confirmed-Tier Precision:** Must maintain **>= 90%**.
  - Any pull request reducing confirmed-tier precision below 90% fails the build.
- **90-Day Drift Evaluation:** Advertiser attribution links are re-evaluated every 90 days to capture business relocations or expansion (GEO-09).

## 5. Edge-Case IDs Referenced
- `GEO-01` (Brand name includes city e.g. "Jaipur Rugs" but is national)
- `GEO-02` (City aliases, phonetic variations, and vernacular spellings)
- `GEO-03` (Satellite suburbs: Noida, Gurgaon, Navi Mumbai, Thane, Salt Lake)
- `GEO-04` (Ambiguous generic locality names e.g. "Civil Lines", "Model Town")
- `GEO-05` (National brand with Mumbai HQ advertising pan-India)
- `GEO-06` (Multi-city franchise and branch attribution)
- `GEO-07` (Conflicting geo evidence resolution)
- `GEO-08` (Zero geo signal handling)
- `GEO-09` (Relocating businesses and 90-day re-evaluation)
- `GEO-10` (Mobile numbers forbidden as geo signals)
- `GEO-11` (6-digit numbers that are not PIN codes)
- `GEO-12` (Directional travel phrasing e.g. "Delhi to Jaipur cab")
- `GEO-13` (Standardized urban population denominators)

## 6. Open Questions
- Establishing an optimal threshold for Google Places API validation to maximize attribution accuracy while remaining strictly within the monthly Places budget cap.

## 7. Acceptance Checklist
- [x] Multi-signal weight matrix and evidence sources specified.
- [x] Noisy-OR mathematical formula and conflict resolution rules defined.
- [x] Attribution tiers (`confirmed`, `probable`, `weak`) and scope classifications defined.
- [x] Evaluation benchmark methodology (>= 300 labeled advertisers, >= 90% precision) established.
- [x] All 13 GEO edge-case IDs cross-referenced.

## 8. Last Updated
- Date: 2026-11-04
- Version: 1.0 (Phase 0 Baseline)

