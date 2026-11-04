# Operational Runbook: Upstream Data Provider Failover

## 1. Purpose
Switch commercial ad ingestion from the primary third-party provider to an approved secondary provider or updated actor endpoint with minimal collection downtime.

## 2. Trigger Conditions
- Upstream provider experiences prolonged outage (> 12 hours) (SRC-08).
- Provider experiences unannounced schema breaking changes (> 5% parse errors).
- Commercial provider significantly alters pricing structure.

## 3. Severity & Authorization
- **Severity:** P1 (High)
- **Authorization:** System Admin or Collector Lead.

## 4. Execution Procedure

### Step 1: Pause Active Ingestion Jobs
Prevent partial runs during provider reconfiguration:
```bash
docker compose exec api python -m app.cli jobs pause --adapter adapter_b
```

### Step 2: Update Provider Adapter Configuration
1. Open environment configuration (`.env` or secret manager):
   ```bash
   # Switch active commercial provider target
   ADAPTER_B_PROVIDER=apify_backup_actor
   ADAPTER_B_API_KEY=sec_new_provider_token_xyz
   ADAPTER_B_RATE_LIMIT=50  # req/min
   ```
2. Validate provider credentials using a single dry-run test query:
   ```bash
   docker compose exec worker python -m app.cli test-provider --adapter adapter_b --limit 5
   ```

### Step 3: Run Contract Verification Suite
Verify that the secondary provider's payloads conform to normalized models:
```bash
docker compose exec worker pytest tests/collectors/test_adapter_b_contract.py
```

### Step 4: Resume Scheduled Ingestion
1. Re-enable the ingestion queue:
   ```bash
   docker compose exec api python -m app.cli jobs resume --adapter adapter_b
   ```
2. Trigger an incremental sweep:
   ```bash
   docker compose exec worker python -m app.cli collect --city jaipur --limit 100
   ```

## 5. Verification
- Verify Prometheus gauge: `rows_vs_previous_run_ratio` remains within acceptable bounds ($0.70 \le r \le 1.30$).
- Confirm zero unhandled parser exceptions in Sentry.

