# Operational Runbook: Opt-Out & Regulatory Takedown Processing

## 1. Purpose
Handle, verify, and execute manual or automated data subject takedown requests, Do-Not-Contact notices, and right-to-be-forgotten petitions under the Indian DPDP Act 2023.

## 2. Trigger Conditions
- Receipt of an automated verified request via the public `/optout` portal (LEG-01).
- Formal email request to `compliance@adatlas.in` requiring manual review.
- Judicial or regulatory erasure order from the Data Protection Board of India (LEG-02).

## 3. Severity & Authorization
- **Severity:** P2 (Standard SLA $\le 7$ days) / P1 (Judicial order $\le 24$ hours).
- **Authorization:** Compliance Officer or System Admin.

## 4. Execution Procedure

### Step 1: Verify Ownership of the Contact
- If submitted via the public portal: assert that the cryptographic OTP or email confirmation token was verified.
- If received via email: request verification by requiring a response from the corresponding corporate domain address.

### Step 2: Compute Cryptographic Hash
Normalize the target identifier (E.164 phone number, lowercase email, or clean domain) and calculate its SHA-256 hash:
```bash
docker compose exec api python -m app.cli hash-value --kind phone --value "+919829012345"
# Output: a1b2c3d4...
```

### Step 3: Insert into Suppression Registry
Persist the hash into the `suppression` table:
```sql
INSERT INTO suppression (value_hash, kind, reason, requested_at, verified)
VALUES (
  decode('a1b2c3d4...', 'hex'),
  'phone',
  'user_optout_verified',
  now(),
  TRUE
) ON CONFLICT (value_hash) DO UPDATE SET verified = TRUE;
```

### Step 4: Purge Active Contact & Derived Records
Permanently delete all occurrences of the contact from the primary database:
```sql
-- Delete associated evidence records
DELETE FROM contact_evidence
WHERE contact_id IN (SELECT id FROM contacts WHERE value_hash = decode('a1b2c3d4...', 'hex'));

-- Delete contact records
DELETE FROM contacts
WHERE value_hash = decode('a1b2c3d4...', 'hex');
```

If full advertiser entity erasure is legally demanded (LEG-02):
```bash
docker compose exec api python -m app.cli erase-advertiser --meta-page-id "<PAGE_ID>" --reason "legal_takedown"
```

## 5. Verification
1. Verify via API search that the contact or advertiser returns 404 Not Found.
2. Verify that subsequent ingestion runs skip the suppressed entity.
3. Log the verified takedown in `audit_log` without storing plaintext PII.

