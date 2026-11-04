# Operational Runbook: Selective Data Purging by Ingestion Source

## 1. Purpose
Selectively and completely expunge all ad records, derived contacts, and raw payloads originating from a specific upstream data vendor or adapter following a contractual dispute, vendor termination, or copyright challenge.

## 2. Trigger Conditions
- Termination of contract with a commercial scraper vendor (LEG-09).
- Upstream platform copyright or terms-of-service challenge targeting an individual collection adapter.
- Discovery that an upstream vendor delivered corrupted or unauthorized data batches.

## 3. Severity & Authorization
- **Severity:** P1 (High)
- **Authorization:** Legal Counsel and Lead System Architect.

## 4. Execution Procedure

### Step 1: Pre-Execution Safety Snapshot
Execute an immediate database snapshot before running mass deletions:
```bash
docker compose exec infra-db pg_dump -U adatlas -d adatlas_prod | gzip > /backups/pre_purge_snapshot.sql.gz
```

### Step 2: Disable Target Source Adapter
Prevent subsequent ingestion runs from writing new records under the source:
```bash
# Update configuration
ADAPTER_B_ENABLED=false
```
Restart API and Beat containers to apply changes.

### Step 3: Execute Purge CLI Command
Run the parameterized source purge tool:
```bash
docker compose exec api python -m app.cli purge-source \
  --source adapter_b \
  --dry-run
```
Inspect the output summary:
- Total ads to be expunged.
- Total associated contacts without secondary evidence to be removed.
- Total raw payload S3 objects to be deleted.

Once verified, re-run with `--execute`:
```bash
docker compose exec api python -m app.cli purge-source \
  --source adapter_b \
  --execute
```

### Step 4: Re-Evaluate Downstream Rollups
Trigger immediate recalculation of daily analytics and city scorecards to reflect expunged records:
```bash
docker compose exec worker python -m app.cli analytics rollup --recalculate --days 30
```

## 5. Verification
- Verify SQL assertion: `SELECT count(*) FROM ads WHERE source = 'adapter_b';` returns `0`.
- Verify S3 raw payload bucket contains zero objects under prefix `raw/adapter_b/`.
- Confirm system audit entry recorded in `audit_log`.

