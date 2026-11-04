# ADR-0011: Data Retention Schedules & Automated Lifecycle Pruning

## Status
Accepted

## Date
2026-11-04

## Context
Under Indian DPDP Act 2023 principles of storage limitation, personal and business data must not be retained indefinitely once the original processing purpose has concluded. Additionally, retaining uncompressed scraper payloads and temporary export files indefinitely inflates database and object storage costs.

## Decision
Establish the following tiered automated retention policies:
1. **Raw Scraper Payloads (`raw_payloads`):** Retained in S3/MinIO for **90 days**. Payloads older than 90 days are pruned automatically by cloud object lifecycle rules unless marked for active audit replay.
2. **Unverified Contacts:** If an unverified contact has not been re-verified or corroborated across subsequent crawls within **12 months**, it is deleted from the `contacts` table.
3. **Audit Log Records (`audit_log`):** Retained for **24 months** to maintain compliance verification trails under DPDP guidelines, after which records are archived to cold storage.
4. **Export Artifacts (`exports`):** Exported CSV and Excel spreadsheets stored in S3 expire and are permanently deleted after **7 days**. Download URLs are signed with 15-minute expirations.
5. **Suppression Registry (`suppression`):** Retained **indefinitely** as cryptographic SHA-256 hashes (`value_hash`) to guarantee that opted-out entities are never re-ingested or re-contacted in future crawls.

## Consequences
- **Positive:** Complies with data minimization and storage limitation mandates; controls storage bloat and cloud hosting expenses.
- **Negative:** Historical raw payloads older than 90 days cannot be re-parsed if an algorithm update is introduced later (normalized tables remain intact).
- **Compliance:** Enforces technical alignment with statutory data retention and erasure expectations.

