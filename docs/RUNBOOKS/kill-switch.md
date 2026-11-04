# Operational Runbook: Emergency Collection Kill Switch

## 1. Purpose
Immediately halt all active data collection, web crawling, contact extraction, and external API calls across all worker instances within 60 seconds of trigger.

## 2. Trigger Conditions
- Receipt of an upstream legal cease-and-desist or formal regulatory notice (LEG-09).
- Runaway cloud billing or provider spend exhaustion (PIPE-08).
- Severe SSRF security anomaly or active intrusion investigation (SEC-01).
- Operator command during critical maintenance.

## 3. Severity & Authorization
- **Severity:** P0 (Critical Emergency)
- **Authorization:** System Admin, Compliance Officer, or Lead Engineer.

## 4. Execution Procedure

### Method A: Admin REST API Trigger (Fastest)
Submit an authenticated POST request to the admin kill-switch endpoint:
```bash
curl -X POST https://adatlas.in/api/v1/admin/kill-switch \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Emergency halt triggered by operator", "scope": "global"}'
```
*Effect:* Sets Redis global flag `kill_switch:global = true` with infinite TTL. Active Celery workers monitor this key every 5 seconds and exit immediately upon detection.

### Method B: Environment & Container Halt (Host Access)
If the API is unresponsive or network isolation is required, execute on the host:
```bash
# 1. SSH into production host
ssh admin@prod.adatlas.in

# 2. Stop Celery ingestion and enrichment workers immediately
docker compose stop worker-collect worker-enrich beat

# 3. Verify halted containers
docker compose ps
```

### Method C: Database Budget Zeroing
If workers fail to halt, force immediate budget exhaustion:
```sql
UPDATE budgets SET cap = 0.00, spent = 999999.00;
```

## 5. Verification & Health Check
1. Inspect running Celery tasks:
   ```bash
   docker compose exec worker celery -A app.workers.celery_app inspect active
   ```
   Assert that active task count is 0.
2. Check Prometheus metric: `collect_runs_total{status="halted"}` incremented.

## 6. Recovery & Deactivation
Once the root cause is resolved and authorization is granted:
```bash
# Remove Redis kill-switch flag
docker compose exec redis redis-cli DEL kill_switch:global

# Restart worker containers
docker compose up -d worker-collect worker-enrich beat
```

