# ADR-0008: Google Places API Integration for Spatial Validation and Contact Fallback

## Status
Accepted

## Date
2026-11-04

## Context
Many local Indian advertisers lack standalone corporate websites (relying solely on Instagram handles or WhatsApp CTAs), leaving geo attribution and contact extraction incomplete. Google Places API (New) provides authoritative, verified business listings with physical postal addresses, telephone numbers, and geographic coordinates, but incurs per-query API costs ($17–$32 per 1,000 requests depending on SKU).

## Decision
1. Integrate the Google Places API (New) Text Search service as an authorized enrichment and spatial validation source.
2. **Selective Triggering:** Google Places queries are not run across the entire advertiser universe. Invocations are restricted to:
   - Top candidates in the "probable" geo attribution tier ($0.40 \le p < 0.75$) to resolve city association.
   - High-activity advertisers with zero discoverable website contacts.
3. **Hard Monthly Budget Ceiling:** Enforce a strict monthly spend cap in `budgets.scope = 'places'` (default $100.00 / month, approx. 3,000–5,000 queries).
4. **Hermetic CI Mocking:** All automated tests must run against recorded response cassettes; live Google Places calls are forbidden in CI runs.

## Consequences
- **Positive:** Significantly boosts contact discovery and geo precision for local retail, dining, coaching, and SMB advertisers lacking modern websites.
- **Negative:** Introduces recurring API costs; requires ongoing budget quota monitoring.
- **Compliance:** Utilizes authorized public Google Maps developer APIs, adhering strictly to Google terms and caching rules.

