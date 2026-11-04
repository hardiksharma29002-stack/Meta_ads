# Operational Runbook: Secret & Credential Rotation

## 1. Purpose
Safely rotate API credentials, cryptographic signing keys, database passwords, and third-party access tokens without causing application downtime.

## 2. Trigger Conditions
- Scheduled 90-day credential hygiene rotation.
- Suspected compromise, accidental git commit, or log exposure of an operational secret (SEC-06).
- Employee or contractor offboarding with access to production secrets.

## 3. Severity & Authorization
- **Severity:** P2 (Routine) / P1 (Compromise Response)
- **Authorization:** System Admin or Lead DevOps Engineer.

## 4. Execution Procedures

### 4.1 Rotating Google OAuth JWT Signing Secrets (ADR-0005)
1. Generate a new high-entropy 256-bit HMAC secret:
   ```bash
   openssl rand -hex 32
   ```
2. Update secret manager or environment variable:
   - Set `JWT_SECRET_PRIMARY=<new_secret>`
   - Set `JWT_SECRET_SECONDARY=<old_secret>` (enables grace period for in-flight 5-minute tokens).
3. Restart FastAPI and Next.js BFF containers:
   ```bash
   docker compose up -d --no-deps api frontend
   ```
4. After 10 minutes, remove `JWT_SECRET_SECONDARY` and restart containers.

### 4.2 Rotating PostgreSQL Database Credentials
1. Create a secondary administrative user in PostgreSQL:
   ```sql
   CREATE USER adatlas_app_v2 WITH PASSWORD '<new_secure_password>';
   GRANT ALL PRIVILEGES ON DATABASE adatlas_prod TO adatlas_app_v2;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adatlas_app_v2;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO adatlas_app_v2;
   ```
2. Update `DATABASE_URL` in environment configuration to use `adatlas_app_v2`.
3. Perform zero-downtime rolling restart of `api` and `worker` containers.
4. Verify application health check (`GET /readyz`).
5. Drop legacy user `adatlas_app` once all stale connections have terminated:
   ```sql
   DROP USER adatlas_app;
   ```

### 4.3 Rotating External API Tokens (Meta Graph API, Adapter B, Google Places)
1. Generate the replacement API token in the provider's developer dashboard.
2. Update the corresponding configuration variable (`META_ACCESS_TOKEN`, `ADAPTER_B_API_KEY`, `GOOGLE_PLACES_API_KEY`).
3. Execute single-query validation via CLI:
   ```bash
   docker compose exec worker python -m app.cli test-provider --adapter adapter_b --limit 1
   ```
4. Restart background worker processes:
   ```bash
   docker compose restart worker-collect worker-enrich
   ```
5. Revoke the superseded token in the upstream vendor dashboard.

## 5. Verification
- Confirm application logs show zero authentication errors.
- Confirm automated secret scanners (`gitleaks`) report zero unencrypted exposed secrets in code or configuration files.

