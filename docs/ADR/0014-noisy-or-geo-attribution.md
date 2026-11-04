# ADR-0014: Noisy-OR Probabilistic Engine for Multi-Signal Geo-Attribution

## Status
Accepted

## Date
2026-11-04

## Context
Meta Ad Library does not expose advertiser geographic targeting parameters, requiring city attribution to be inferred from noisy, heterogeneous signals: Google Places API matches, Schema.org JSON-LD tags, 6-digit postal PIN codes, landline STD codes, website titles, and ad copy mentions. Simple heuristic voting models fail to account for signal reliability, while complex machine learning classifiers lack explainability and require massive training sets.

## Decision
1. Implement a probabilistic **Noisy-OR** Bayesian combination model to evaluate candidate city associations:
   $$p(c) = 1 - \prod_{k \in K} (1 - \max_{i \in k} s_i)$$
2. Assign calibrated base strength weights ($s_i$) reflecting signal reliability (e.g. Google Places = 0.90, JSON-LD = 0.85, PIN Code = 0.85, STD code = 0.60, Ad text = 0.50).
3. Enforce signal-class deduplication: multiple observations of the identical signal type collapse to a single maximum strength factor to prevent artificial inflation.
4. Establish clear attribution tiers:
   - **Confirmed:** $p \ge 0.75$
   - **Probable:** $0.40 \le p < 0.75$
   - **Weak:** $p < 0.40$
5. Implement conflict resolution: when two distinct cities achieve $p \ge 0.60$, classify entity as multi-city, penalize standalone confidence, and route ambiguous cases to the admin review queue.

## Consequences
- **Positive:** Mathematically rigorous, highly explainable, transparent to marketing users, and easily tunable without retraining neural models.
- **Negative:** Requires initial manual calibration of base signal weights against the 300+ labeled benchmark evaluation dataset.
- **Compliance:** Satisfies algorithmic transparency and explainability standards by preserving detailed evidence arrays for every attribution link.

