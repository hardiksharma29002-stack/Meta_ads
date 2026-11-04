---
description: Step-by-step workflow for configuring and onboarding a new city into the AdAtlas platform.
---

# Workflow: Adding a New City to AdAtlas

## Objective
Expand coverage beyond the initial five cities (Mumbai, Delhi, Jaipur, Kolkata, Bengaluru) through data-driven configuration without altering core application code.

## Execution Steps

### 1. Gather Demographic & Geopolitical Reference Data
Verify and collect the following authoritative attributes:
- `slug`: Lowercase URL-safe identifier (e.g., `pune`, `hyderabad`).
- `name`: Official display name.
- `state_name`: Official state name.
- `gst_state_code`: 2-digit GST state prefix (e.g., `27` for Maharashtra, `36` for Telangana).
- `std_code`: Landline telephone STD area code (e.g., `020` for Pune, `040` for Hyderabad).
- `lat` & `lon`: Geographical center coordinates.
- `urban_population`: Official Census / Ministry of Housing & Urban Affairs population count.
- `population_source` & `population_year`: Attribution metadata.

### 2. Update Reference Seed Files
1. Append the city entry to `data/seed/cities.yaml`.
2. Add comprehensive alias mappings to `data/seed/city_aliases.yaml`:
   - Historical / alternate colonial names (e.g., Poona -> Pune).
   - Vernacular script spellings in regional languages (e.g., पुणे, ஹைதராபாத்).
   - English phonetic variants and common typos.
   - Core commercial localities and industrial zones.
   - Satellite cities and peripheral suburbs (marked `satellite: true`).
3. Import postal PIN code mappings into `data/seed/pincodes/<slug>.csv` (verified against India Post open data).

### 3. Apply Seeds to Database
Execute the idempotent seed command:
```bash
docker compose exec api python -m app.db.seed --cities
```
Verify insertion via SQL or API:
```bash
curl -s http://localhost:8000/api/v1/cities | jq .
curl -s "http://localhost:8000/api/v1/cities/resolve?q=<alias>" | jq .
```

### 4. Configure Crawl Cadence & Seed Queries
1. Generate discovery seed queries combining the new city aliases with category keywords in `backend/app/pipeline/seed_queries.py`.
2. Run a dry-run sweep to project volume and cost:
   ```bash
   docker compose exec worker python -m app.cli collect --city <slug> --dry-run
   ```
3. Initialize the tiered refresh schedule in Celery Beat.

