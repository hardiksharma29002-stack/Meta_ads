---
description: Privacy principles, DPDP Act/Rules compliance, data minimization, suppression enforcement, and sensitive data handling.
globs: ["**/*"]
alwaysApply: true
---

# Data Privacy & Regulatory Compliance Standards

## 1. Data Minimization Principles (LEG-03)
AdAtlas is designed specifically to gather public B2B business contact information. The storage of sensitive personal or government identifiers is strictly prohibited by schema and code constraints:
- **No National Identifiers:** Never extract, scrape, or store PAN (Permanent Account Number), Aadhaar, voter identity, or passport details.
- **GSTIN Handling:** When extracting a business's Goods and Services Tax Identification Number (GSTIN), extract and persist ONLY the first two digits (the official Indian state code, e.g., "08" for Rajasthan, "27" for Maharashtra). The remaining 13 alphanumeric characters contain the taxpayer's PAN and must be dropped immediately.
- **No Personal Social Profiles:** Restrict social link extraction to verified corporate/business pages (LinkedIn company pages, business Instagram profiles, official YouTube channels, Facebook brand pages). Never crawl personal user profiles or extract private individuals' friend lists.

## 2. No Synthetic Contact Generation
- **Never Guess Contact Details:** Never synthesize, interpolate, or guess emails based on employee naming patterns (e.g., `first.last@company.com`). If an email address is not visibly published on the business's own web domain, mark the contact status as `no_public_contact` (CON-01).
- **No Invasive SMTP Probing:** Validate email addresses exclusively via syntax verification (`email-validator`) and domain DNS MX record lookups (`dnspython`). Never execute interactive SMTP `RCPT TO` handshakes or dictionary verification against mail exchangers (CON-16).

## 3. Suppression & Opt-Out Enforcement (LEG-01, LEG-02)
- **Hashed Suppression Registry:** All opt-out requests, takedown notices, and do-not-contact flags are stored as SHA-256 hashes (`value_hash`) in the `suppression` table. Raw contact strings are wiped upon verification.
- **Pre-Flight Checks:** Every pipeline worker, API endpoint, and export compiler MUST query the suppression registry:
  1. *Before Contact Enrichment Write:* If `sha256(norm(value))` exists in `suppression`, abort write immediately.
  2. *Before API Response Delivery:* Filter out any contact matching the suppression hash.
  3. *Before Export File Generation:* Assert that zero suppressed values appear in the resulting CSV or Excel file.
- **Crawl Persistence:** Opt-outs must survive subsequent automated crawls. A suppressed entity must never be re-introduced or re-activated by future data collection runs.

## 4. Zero PII in Logging & Diagnostics (SEC-10)
- Structured application logs (`structlog`) and metrics collectors MUST NOT contain plain-text contact information, phone numbers, email addresses, or individual names.
- When logging diagnostic details about a contact record, output only its database identifier, contact type, and a truncated hash prefix: `value_hash_prefix=sha256(val)[:8]`.
- Automated test suites must include regex interceptors on log handlers to verify that no PII escapes into stdout or log aggregators.

## 5. Personal-Data-Risk Classification (CON-07, CON-08)
Enriched contacts must be classified with risk tags to inform outreach policies and quotas:
- `free_mail`: Webmail addresses (`@gmail.com`, `@yahoo.com`, `@outlook.com`).
- `personal_data_risk`: Numbers or emails identified as belonging to named corporate officers (e.g., "Grievance Officer: Rohit Sharma") or sole proprietors rather than generic department desks (`sales@`, `info@`, toll-free 1800 numbers).
- Advertisers flagged with `personal_data_risk` require elevated export permissions and are subject to lower daily reveal thresholds.

## 6. Indian DPDP Compliance Roadmap
- Maintain full audit trails of when, where, and how each contact datum was discovered (`contact_evidence` table).
- Provide a public, rate-limited `/optout` endpoint enabling any business or individual to request immediate deletion and suppression.
- Prepare incident response runbooks to support potential breach reporting within the 72-hour window mandated by the DPDP Rules 2025.

