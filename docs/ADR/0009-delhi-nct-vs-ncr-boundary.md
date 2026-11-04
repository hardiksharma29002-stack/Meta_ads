# ADR-0009: Geographical Boundary Definition: Delhi NCT vs National Capital Region (NCR)

## Status
Accepted

## Date
2026-11-04

## Context
When analyzing "Delhi," advertisers and commercial businesses frequently span the National Capital Territory of Delhi (NCT, including New Delhi) and the broader National Capital Region (NCR), which encompasses major satellite cities in neighboring states (Gurugram and Faridabad in Haryana; Noida and Ghaziabad in Uttar Pradesh). Treating NCR as a single monolithic entity skews urban population density denominators (NCT ~16M vs NCR ~46M) and conflates different state tax/legal jurisdictions (GST 07 for Delhi vs 06 for Haryana vs 09 for UP).

## Decision
1. **Core Delhi Definition:** Define "Delhi" strictly as the **National Capital Territory of Delhi (NCT)** (GST state code `07`, landline STD code `011`, PIN code prefix `110xxx`).
2. **Satellite Suburb Classification:** Classify Gurugram (STD `0124`), Noida/Ghaziabad (STD `0120`), and Faridabad (STD `0129`) as **"Delhi NCR (Satellite)"** entities in `city_aliases` with `kind = 'satellite'`.
3. **UI Satellite Toggle:** By default, city search and comparison views reflect core Delhi NCT. Provide an explicit UI toggle ("Include NCR Satellites") allowing users to expand results to include surrounding satellite territories without distorting core baseline metrics.

## Consequences
- **Positive:** Ensures statistical integrity for population density metrics; eliminates state tax jurisdiction ambiguity; gives users granular control over suburban boundaries.
- **Negative:** Requires maintaining separate alias and PIN code tables for Haryana and UP satellite districts.
- **Compliance:** Aligns with official Census and Ministry of Urban Affairs jurisdictional boundaries.

