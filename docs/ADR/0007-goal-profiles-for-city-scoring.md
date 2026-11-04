# ADR-0007: Goal-Driven Multi-Profile Framework for City Vitality Scoring

## Status
Accepted

## Date
2026-11-04

## Context
Commercial ad spend and impression volumes are withheld by Meta for all advertising outside the European Union (R2). Marketing stakeholders frequently ask "which city is the better market," but the definition of "better" fundamentally depends on commercial strategy (e.g. lead volume vs market sophistication vs competitive entry). Fabricating estimated spend figures would compromise organizational integrity.

## Decision
1. **Zero Spend Estimation:** Strictly refuse to model, project, or display "estimated commercial ad spend."
2. **Objective Proxy Metrics:** Establish 10 verifiable proxy metrics capturing advertiser scale (A), density (D), growth velocity (G), ad longevity (L), creative refresh (R), contact reachability (C), SMB share (S), direct response share (W), diversity (H), and competitive intensity (K).
3. **Three Goal Profiles:** Implement three standardized goal profiles with default weight distributions:
   - **Outreach Prospecting (Default):** Prioritizes contact reachability and SMB volume ($C: 0.30, S: 0.20, A: 0.20, G: 0.15, W: 0.15$).
   - **Market Maturity:** Prioritizes digital ad saturation and longevity ($A: 0.25, D: 0.20, L: 0.20, H: 0.20, R: 0.15$).
   - **Low-Competition Entry:** Prioritizes uncrowded, emerging growth markets ($(1-D): 0.30, (1-K): 0.25, G: 0.25, C: 0.20$).
4. **Interactive Customization:** Allow marketing users to adjust metric weights dynamically via frontend UI sliders.
5. **Data Sufficiency Guards:** Enforce a `MIN_SAMPLE` threshold (default 200 confirmed advertisers); under-sampled cities display greyed scores and explicit warning banners.

## Consequences
- **Positive:** Delivers defensible, transparent, and actionable market intelligence without fabricating non-existent spend numbers; adapts to varied business goals.
- **Negative:** Requires initial user education on interpreting proxy scores rather than conventional financial metrics.
- **Compliance:** Eliminates deceptive advertising analytics claims and ensures full analytical transparency.

