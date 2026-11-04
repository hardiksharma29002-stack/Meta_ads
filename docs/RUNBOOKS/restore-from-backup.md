# Operational Runbook: Database & Storage Disaster Recovery

## 1. Purpose
Execute a complete, verified point-in-time recovery (PITR) of the PostgreSQL relational database and MinIO/S3 object storage after host hardware failure, data corruption, or catastrophic loss.

## 2. Trigger Conditions
- Production database host storage corruption or catastrophic cloud VM termination.
- Accidental destructive query or unintended mass deletion of core tables.
- Mandatory scheduled quarterly disaster recovery drill (SEC-11).

## 3. Severity & Authorization
- **Severity:** P0 (Critical Service Outage) / P3 (Scheduled Drill)
- **Authorization:** Lead Infrastructure Engineer or System Admin.

## 4. Execution Procedure

### Step 1: Halt Application Ingestion & Web Traffic
Prevent partial writes during restoration:
```bash
docker compose stop api worker-collect worker-enrich beat
```

### Step 2: Provision Isolated Recovery Database Target
To protect existing volumes during investigation, restore to a clean target container or isolated staging host:
```bash
docker compose up -d infra-db-restore
```

### Step 3: Download Latest Encrypted Backup Artifact
Retrieve the latest daily snapshot from encrypted cloud storage:
```bash
aws s3 cp s3://adatlas-backups-ap-south-1/postgres/daily/2026-11-04_full.sql.gz.enc /tmp/backup.enc

# Decrypt backup volume using KMS master key
aws kms decrypt --ciphertext-blob fileb:///tmp/backup.enc --output text --query Plaintext | base64 -d > /tmp/backup.sql.gz
```

### Step 4: Execute Database Restoration
Stream decrypted dump into the target database engine:
```bash
gunzip -c /tmp/backup.sql.gz | docker compose exec -T infra-db psql -U adatlas -d adatlas_prod
```

### Step 5: Restore Object Storage State (MinIO / S3)
Verify raw payload object storage integrity. If bucket objects were lost, restore from cross-region replication bucket:
```bash
aws s3 sync s3://adatlas-raw-replicated/ s3://adatlas-raw-prod/ --delete
```

### Step 6: Post-Restore Data Integrity Verification
Execute diagnostic verification queries:
```sql
-- 1. Verify city reference table count (strictly 5 cities)
SELECT count(*) FROM cities WHERE is_active = TRUE;

-- 2. Verify advertiser and contact table row counts
SELECT count(*) FROM advertisers;
SELECT count(*) FROM contacts;

-- 3. Verify suppression registry integrity
SELECT count(*) FROM suppression WHERE verified = TRUE;
```

### Step 7: Re-Link Application & Resume Services
1. Update database connection string to point to the restored instance.
2. Restart application containers:
   ```bash
   docker compose up -d api worker-collect worker-enrich beat frontend
   ```
3. Run smoke test:
   ```bash
   curl -s https://adatlas.in/api/v1/healthz | jq .
   ```

## 5. Recovery SLA Benchmarks
- Recovery Point Objective (RPO): $\le 24\text{ hours}$ (daily snapshot) / $\le 15\text{ minutes}$ with WAL streaming.
- Recovery Time Objective (RTO): $\le 2\text{ hours}$ to complete full database rebuild and service resumption.

