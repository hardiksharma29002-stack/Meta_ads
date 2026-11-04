# ADR-0001: Commercial Ad Collection Strategy via Pluggable Multi-Adapter Architecture

## Status
Accepted

## Date
2026-11-04

## Context
Meta's official Ad Library API outside the EU/UK exclusively returns political and issue ads (R1). Commercial product/service campaigns in India are visible only on the public web interface. Developing and operating a custom headless browser scraper (Adapter C) carries high technical fragility (R7) and legal exposure under Meta's Terms of Service (R5). Conversely, relying exclusively on a single third-party provider creates vendor lock-in and availability risks.

## Decision
1. Implement a pluggable multi-adapter architecture conforming to the `AdSourceAdapter` interface.
2. Ingest political and issue advertisements via the official Meta Graph API `/ads_archive` (**Adapter A**).
3. Ingest Indian commercial advertisements via licensed, managed third-party data providers (**Adapter B**, e.g., Apify Ad Library actors) with explicit per-result cost accounting.
4. Build our own Playwright-based headless Chromium collector (**Adapter C**) as an emergency capability, but enforce a hard configuration flag keeping it **STRICTLY OFF** (`ADAPTER_C_ENABLED=false`) until human counsel grants explicit written approval (D1, D2).
5. Persist a `source` tag on every ad and contact row to allow selective data purging per provider.

## Consequences
- **Positive:** Minimizes legal exposure; eliminates daily scraper maintenance overhead; enables seamless vendor switching.
- **Negative:** Commercial ingestion incurs per-result vendor costs ($0.40–$5.00 per 1,000 ads); requires strict budget monitoring.
- **Compliance:** Aligns with legal risk mitigation principles and enables instant compliance with potential platform cease-and-desist notices.

