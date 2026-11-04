# Operational Runbook: Upstream Schema Drift Response

## 1. Purpose
Diagnose, patch, and deploy updated parsing models when Meta Ad Library or third-party data providers alter raw payload structures.

## 2. Trigger Conditions
- Prometheus alert `SchemaDriftDetected` fires (`parse_failures_total` > 5% of batch) (SRC-07, SRC-09).
- Automated canary contract tests fail in CI.

## 3. Severity & Authorization
- **Severity:** P2 (Medium) to P1 (High)
- **Authorization:** Collector Lead or Pipeline Engineer.

## 4. Execution Procedure

### Step 1: Capture Drifted Payloads
Download sample failed raw payloads from the dead-letter queue or S3 raw store:
```bash
docker compose exec api python -m app.cli dump-failed-payloads --adapter adapter_b --limit 10 --output /tmp/drifted_samples.json
```

### Step 2: Analyze Structural Mutations
Inspect JSON keys and compare against Pydantic models in `backend/app/collectors/models.py`:
- Identify renamed fields (e.g. `ad_creative_body` renamed to `ad_body_text`).
- Identify new required fields or altered data types (e.g. string converted to array).

### Step 3: Update Pydantic Ingestion Models
1. Update raw adapter schema in `backend/app/collectors/schemas/`:
   ```python
   # Support both legacy and mutated upstream key names
   body_text: str | None = Field(default=None, validation_alias=AliasChoices("ad_body_text", "body", "ad_creative_body"))
   ```
2. Increment `schema_version` counter in the corresponding adapter module.

### Step 4: Record Updated Golden Test Fixtures
Save the captured sample as a versioned test fixture:
```bash
cp /tmp/drifted_samples.json tests/fixtures/collectors/adapter_b/v2_mutation.json
```
Run the contract test suite to assert full compatibility:
```bash
uv run pytest tests/collectors/test_adapter_b_contract.py
```

### Step 5: Deploy & Replay Failed Batches
1. Deploy updated code to staging and production.
2. Replay isolated failures from the `dead_letters` table:
   ```bash
   docker compose exec api python -m app.cli dead-letters replay --queue q.normalize
   ```

## 5. Verification
- Confirm that `parse_failures_total` metric drops back to zero.
- Assert that downstream normalization tasks process successfully.

