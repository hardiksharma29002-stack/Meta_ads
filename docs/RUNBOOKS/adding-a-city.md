# Operational Runbook: Onboarding a New Metropolitan City

## 1. Purpose
Define the configuration changes, demographic reference population seeding, postal code ingestion, and query scheduling required to expand AdAtlas to a new Indian city without requiring code modifications.

## 2. Trigger Conditions
- Business decision to onboard a sixth metropolitan market (e.g. Pune, Hyderabad, Ahmedabad, Chennai).

## 3. Severity & Authorization
- **Severity:** P3 (Routine Feature Expansion)
- **Authorization:** Marketing Lead and System Owner.

## 4. Execution Procedure

### Step 1: Collect Authoritative Demographic & Telephony Metadata
Compile verified jurisdictional parameters:
- `slug`: e.g. `pune`
- `name`: `Pune`
- `state_name`: `Maharashtra`
- `gst_state_code`: `27`
- `std_code`: `020`
- `urban_population`: `5057709` (from official Ministry of Housing & Urban Affairs / Census urban agglomeration data)
- `population_source`: `Census_UA_2011_MoHUA_Estimate`
- `population_year`: `2024`

### Step 2: Append Reference Data Configuration
1. Append entry to `data/seed/cities.yaml`:
   ```yaml
   - slug: pune
     name: Pune
     state_name: Maharashtra
     gst_state_code: "27"
     std_code: "020"
     lat: 18.52043
     lon: 73.85674
     urban_population: 5057709
     population_source: "MoHUA_UA_Estimate"
     population_year: 2024
     is_active: true
   ```
2. Append aliases to `data/seed/city_aliases.yaml`:
   ```yaml
   pune:
     - alias: "Poona"
       lang: "en"
       kind: "old_name"
     - alias: "पुणे"
       lang: "mr"
       kind: "transliteration"
     - alias: "Pimpri-Chinchwad"
       lang: "en"
       kind: "satellite"
   ```
3. Place official India Post 6-digit postal PIN code CSV under `data/seed/pincodes/pune.csv`.

### Step 3: Run Database Seed Command
Execute idempotent reference data population:
```bash
docker compose exec api python -m app.db.seed --cities --pincodes --aliases
```
Verify insertion via API:
```bash
curl -s http://localhost:8000/api/v1/cities | jq '.items[] | select(.slug=="pune")'
```

### Step 4: Run Dry-Run Query Sweep & Cost Estimation
Simulate discovery sweep for the new city:
```bash
docker compose exec worker python -m app.cli collect --city pune --dry-run
```
Review estimated ad volume, provider query cost, and ensure budget allowance in `budgets.scope = 'provider'`.

### Step 5: Schedule Automated Ingestion Cadence
Add the new city to Celery Beat discovery schedule in `backend/app/core/celery_schedule.py`.

## 5. Verification
- Confirm that search queries for the new city (`GET /api/v1/search?city=pune`) return active results.
- Verify that typo resolution (`GET /api/v1/cities/resolve?q=Poona`) resolves accurately.
- Assert that `/compare` includes the new city once `MIN_SAMPLE` confirmed advertisers are ingested.

