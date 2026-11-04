# ADR-0002: Compliance Boundaries & Legal Sign-off for Business Contact Enrichment

## Status
Accepted

## Date
2026-11-04

## Context
Indian DPDP Act 2023 and DPDP Rules 2025 mandate strict data minimization, purpose limitation, and consent/lawful processing grounds. Extracting contact data from social media platforms or guessing personal contact information poses severe regulatory, ethical, and reputational liabilities.

## Decision
1. **Ethical Enrichment Boundary:** Limit contact enrichment strictly to public B2B contact details directly published by businesses on their own corporate web domains (landing pages, Schema.org JSON-LD, footers, `/contact` pages).
2. **Prohibited Scraping Vectors:** Facebook Page "About" tab scraping and Instagram profile bio crawling are permanently **DISABLED BY DEFAULT**.
3. **Synthetic Contact Prohibition:** Synthetic email guessing (`first.last@domain.com`) and intrusive SMTP probing are strictly forbidden.
4. **Data Minimization:** PAN and Aadhaar collection is forbidden. GSTIN numbers must have the PAN portion discarded immediately; store only the 2-digit state code prefix.
5. **Mandatory Counsel Sign-Off Gate:** Production launch is gated upon formal written legal sign-off from qualified human counsel confirming the lawful B2B processing basis.

## Consequences
- **Positive:** Protects the organization from DPDP regulatory penalties (up to ₹250 crore); establishes an indisputable audit trail of public provenance.
- **Negative:** Advertiser contact coverage is constrained to businesses with an active, discoverable public web domain or Places listing.
- **Compliance:** Enforces privacy by design across all extraction and storage components.

