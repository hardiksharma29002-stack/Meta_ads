# ADR-0010: Geographical Boundary Definition: Mumbai City vs Mumbai Metropolitan Region (MMR)

## Status
Accepted

## Date
2026-11-04

## Context
"Mumbai" can be defined strictly as the municipal administrative districts (Mumbai City and Mumbai Suburban under the Brihanmumbai Municipal Corporation - BMC) or expanded to the wider Mumbai Metropolitan Region (MMR), which includes major satellite municipal corporations such as Thane, Navi Mumbai, Kalyan-Dombivli, and Mira-Bhayandar. While they share the Maharashtra state GST code (`27`) and telecom STD code (`022`), population denominators differ drastically (BMC ~12.5M vs MMR ~21M).

## Decision
1. **Core Mumbai Definition:** Define "Mumbai" strictly as the **BMC Municipal Corporation Area** (Mumbai City and Suburban districts, PIN prefixes `4000xx` through `400099`).
2. **Satellite Suburb Classification:** Classify Navi Mumbai, Thane, Kalyan, and Mira-Bhayandar as **"Mumbai MMR (Satellite)"** entities in `city_aliases` with `kind = 'satellite'`.
3. **UI Satellite Toggle:** By default, Mumbai queries evaluate core municipal territory. Provide an explicit UI toggle ("Include MMR Satellites") allowing users to incorporate satellite suburban advertisers without skewing core per-capita density calculations.

## Consequences
- **Positive:** Preserves clean population denominators; prevents suburban industrial areas from distorting city core vitality metrics; maintains consistency with ADR-0009.
- **Negative:** Users unfamiliar with administrative boundaries may wonder why a Thane business is filtered out of core Mumbai by default (mitigated by clear UI helper tooltips).
- **Compliance:** Conforms to official municipal administrative standards.

