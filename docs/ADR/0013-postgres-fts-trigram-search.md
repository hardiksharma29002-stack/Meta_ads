# ADR-0013: PostgreSQL Trigram and Full-Text Search First over External Search Clusters

## Status
Accepted

## Date
2026-11-04

## Context
Advertiser search requires typo-tolerant fuzzy matching on business names (e.g. matching "Jaipur Rugs" from "Jaypur"), vernacular transliterations (e.g. "जयपुर"), and keyword filtering across millions of ad records. Introducing an external search cluster (Elasticsearch, OpenSearch, Meilisearch) adds operational overhead, dual-write synchronization bugs, memory demands, and additional cloud costs.

## Decision
1. Standardize on native PostgreSQL 16 capabilities utilizing the `pg_trgm`, `unaccent`, and `citext` extensions.
2. Build GIN trigram indexes on `advertisers.page_name_norm` and `city_aliases.alias` to power high-speed fuzzy search and typo resolution.
3. Utilize PostgreSQL full-text search (`tsvector` / `tsquery`) with English and Hindi configuration for keyword search across ad copy.
4. Establish an architectural review trigger: evaluate dedicated search clusters (e.g. Meilisearch) ONLY if search API p95 query latency exceeds 1.0 second or dataset volume exceeds 5,000,000 active ads.

## Consequences
- **Positive:** Zero additional operational infrastructure; transactional consistency between data updates and search index; simplified backups and disaster recovery.
- **Negative:** Complex multi-language stemming and phonetic matching are less advanced than dedicated enterprise search engines.
- **Compliance:** Eliminates the risk of PII escaping into secondary, un-encrypted search cluster nodes.

