# ADR-0004: India Region Cloud Infrastructure & Single-VM Production Topology

## Status
Accepted

## Date
2026-11-04

## Context
Indian data privacy guidelines and corporate governance recommend domestic data localization for datasets containing business entities and contact references in India. Furthermore, for the initial MVP stage (five cities, estimated $\le 500,000$ active ads), deploying a complex Kubernetes cluster introduces excessive operational friction and infrastructure overhead.

## Decision
1. Deploy production infrastructure within an Indian cloud region: AWS Mumbai (`ap-south-1`) or GCP Mumbai (`asia-south1`).
2. Adopt a single-VM containerized topology (4 vCPU / 16 GB RAM) orchestrated via Docker Compose, fronted by Caddy Server for automated TLS.
3. Decouple database persistence by utilizing a cloud-managed PostgreSQL 16 service with automated daily backups and 7-day Point-In-Time Recovery (PITR).
4. Persist raw payloads and file exports in S3-compatible cloud object storage within the same geographic region.

## Consequences
- **Positive:** Complies with data sovereignty norms; minimizes network latency to Indian target domains; drastically lowers monthly cloud infrastructure spend ($< \$150/\text{month}$).
- **Negative:** Single-VM compute requires vertical scaling before considering horizontal auto-scaling in future phases.
- **Compliance:** Satisfies domestic data handling and compliance recommendations under DPDP frameworks.

