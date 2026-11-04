---
description: Procedure for safely replaying stored raw payloads through updated normalization, geo-attribution, and enrichment pipelines.
---

# Workflow: Reprocessing Data from Raw Payloads

## Objective
Rebuild or re-derive normalized database tables (`advertisers`, `ads`, `advertiser_city_links`, `contacts`) from compressed raw payloads stored in S3/MinIO after bug fixes, schema changes, or algorithm updates.

## Guiding Principle
Raw payloads stored in object storage are the permanent source of truth; relational tables are projections that can be recomputed at will.

## Execution Steps

### 1. Identify Target Scope
Determine whether the reprocessing run targets:
- A specific adapter: `--adapter <name>`
- A specific date range: `--since 2026-10-01 --until 2026-11-01`
- A specific city or advertiser set: `--city jaipur` or `--advertiser-id <id>`
- Specific pipeline stages: `--stages normalize,geo` or `--all`

### 2. Verify Database Backup
Confirm that an automated or manual database snapshot exists prior to initiating a large-scale backfill:
```bash
docker compose exec infra-db pg_dump -U adatlas -d adatlas_prod | gzip > backup_pre_reprocess.sql.gz
```

### 3. Execute Reprocess CLI
Run the reprocessor within the worker container with target version tagging:
```bash
docker compose exec worker python -m app.cli reprocess \
  --from-raw \
  --adapter adapter_b \
  --pipeline-version v2.1 \
  --batch-size 500 \
  --dry-run
```
Review the projected payload count and estimated processing duration. Once verified, rerun without `--dry-run`.

### 4. Monitor Ingestion & Verification
1. Watch pipeline metrics via Prometheus/Grafana:
   - `reprocess_payloads_processed_total`
   - `reprocess_records_upserted_total`
   - `reprocess_errors_total`
2. Assert idempotency: verify that existing verified contact records or manual user overrides are preserved.

