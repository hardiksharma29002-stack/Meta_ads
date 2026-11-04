---
description: Step-by-step workflow for implementing, registering, and validating a new Meta Ad Library data source adapter.
---

# Workflow: Implementing a New Collector Adapter

## Objective
Add a new data collection source adapter (e.g., alternative provider or updated Meta API endpoint) while preserving contract consistency, safety limits, and budget accounting.

## Prerequisites
- Review `backend/app/collectors/base.py` (`Capabilities`, `AdSourceAdapter` protocol, `Page[RawAd]`, `Money`).
- Confirm provider pricing and terms of service.
- If external scraping is involved, consult counsel and record approval in `docs/COMPLIANCE_AND_LEGAL.md`.

## Execution Steps

### 1. Implement Adapter Class
Create `backend/app/collectors/adapter_<name>.py`:
1. Inherit from or implement `AdSourceAdapter`.
2. Define explicit `Capabilities` flags:
   - `commercial_ads: bool`
   - `political_ads: bool`
   - `spend_ranges: bool`
   - `page_based_query: bool`
   - `keyword_query: bool`
   - `only_new_ads: bool`
   - `max_page_size: int`
3. Implement `estimate_cost(q: SearchQuery) -> Money`.
4. Implement `search(q: SearchQuery, cursor: str | None) -> Page[RawAd]`.
5. Implement `by_page(page_id: str, cursor: str | None, active_only: bool) -> Page[RawAd]`.
6. Implement `health() -> AdapterHealth`.

### 2. Record Test Fixtures
1. Run a one-time sandboxed query or mock generator to capture representative JSON response fixtures.
2. Scrub all API credentials, secret tokens, and bearer keys from the recorded cassette (`tests/fixtures/collectors/<name>/`).
3. Store raw payloads matching the format expected by `raw_payloads`.

### 3. Bind to Shared Contract Test Suite
1. Register the adapter in `tests/collectors/test_adapter_contracts.py`.
2. Verify that all shared contract assertions pass:
   - Pagination cursor serialization and resumption.
   - Pydantic model validation on extracted raw ads.
   - Handling of empty result sets, deleted ads, and special characters.
   - Cost calculation correctness.

### 4. Register in Factory and Configuration
1. Add the adapter identifier to `backend/app/collectors/registry.py`.
2. Introduce configuration keys in `backend/app/core/config.py` (e.g., `ADAPTER_<NAME>_ENABLED`, `ADAPTER_<NAME>_API_KEY`).
3. Add initial budget entries in `data/seed/budgets.yaml`.

### 5. Validate & Document
1. Run `pytest tests/collectors/test_adapter_<name>.py`.
2. Update `docs/SCRAPING_STRATEGY.md` with the new adapter's capabilities and cost profile.

