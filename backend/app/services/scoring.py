"""City Vitality Scoring & Multi-Profile Comparison Service.

Implements Section 8 and ADR-0007:
10 objective proxy metrics, 3 goal profiles, median-ratio log2 normalization,
data-sufficiency guards, and factor explainability.
"""

import math
from typing import Any
from pydantic import BaseModel, Field


# Goal profile default weight matrices
GOAL_PROFILES = {
    "outreach": {
        "name": "Outreach Prospecting",
        "description": "Where can we reach the highest volume of responsive local business prospects?",
        "weights": {
            "contact_coverage": 0.30,   # C: Verified reachability
            "smb_share": 0.20,          # S: SMB proportion
            "active_advertisers": 0.20, # A: Total advertiser scale
            "growth_velocity": 0.15,    # G: 30-day new business growth
            "direct_response": 0.15,    # W: Conversational direct-action CTAs
        },
    },
    "maturity": {
        "name": "Market Maturity",
        "description": "Where is digital advertising on paid social most commercially established?",
        "weights": {
            "active_advertisers": 0.25, # A
            "advertiser_density": 0.20, # D: Advertisers per 100k population
            "ad_longevity": 0.20,       # L: Sustained active campaigns
            "category_diversity": 0.20, # H: 1 - HHI across industries
            "creative_refresh": 0.15,   # R: Creative A/B testing rate
        },
    },
    "low_competition": {
        "name": "Low-Competition Entry",
        "description": "Where is the market least crowded but experiencing rapid growth?",
        "weights": {
            "inv_density": 0.30,        # 1 - D: Low market saturation
            "inv_competition": 0.25,    # 1 - K: Low category crowding
            "growth_velocity": 0.25,    # G: High incoming velocity
            "contact_coverage": 0.20,   # C: Reachable leads
        },
    },
}

MIN_SAMPLE_THRESHOLD = 50  # Minimum sample size for statistical reliability in MVP


class CityRawMetrics(BaseModel):
    city_slug: str
    city_name: str
    urban_population: int
    active_advertisers: float   # A
    advertiser_density: float   # D (per 100k pop)
    growth_velocity: float      # G
    ad_longevity: float         # L (median days)
    creative_refresh: float     # R (creatives/adv)
    contact_coverage: float     # C (share with contact)
    smb_share: float            # S (ads <= 10)
    direct_response: float      # W (whatsapp/call CTAs)
    category_diversity: float   # H (1 - HHI)
    competition_intensity: float# K (ads/adv)
    sample_size: int            # Total confirmed advertisers observed


class CityScoreResult(BaseModel):
    city_slug: str
    city_name: str
    composite_score: float = Field(ge=0.0, le=100.0)
    sample_ok: bool
    sufficiency_warning: str | None = None
    raw_metrics: dict[str, Any]
    normalized_scores: dict[str, float]
    top_positive_factors: list[str]
    top_negative_factors: list[str]


def compute_median(values: list[float]) -> float:
    """Compute mathematical median of numeric array."""
    if not values:
        return 1.0
    s = sorted(values)
    mid = len(s) // 2
    if len(s) % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2.0
    return s[mid]


def normalize_metric_ratio(val: float, median_val: float) -> float:
    """Normalize using cross-city median ratio with log2 transform and clamping to [-1, +1].
    
    Mapped linearly to [0, 100] where median = 50.
    """
    if median_val <= 0 or val <= 0:
        return 50.0

    ratio = val / median_val
    try:
        log_val = math.log2(ratio)
    except ValueError:
        log_val = 0.0

    # Clamp to [-1.0, +1.0] (halving = 0, doubling = 100)
    clamped = max(-1.0, min(1.0, log_val))
    return round(50.0 + (clamped * 50.0), 2)


def evaluate_city_cohort(
    cities: list[CityRawMetrics],
    profile_key: str = "outreach",
    custom_weights: dict[str, float] | None = None,
) -> list[CityScoreResult]:
    """Score and rank cohort of cities against specified goal profile."""
    profile = GOAL_PROFILES.get(profile_key, GOAL_PROFILES["outreach"])
    weights = custom_weights or profile["weights"]

    # Compute cross-city medians for all metrics
    medians = {
        "active_advertisers": compute_median([c.active_advertisers for c in cities]),
        "advertiser_density": compute_median([c.advertiser_density for c in cities]),
        "growth_velocity": compute_median([c.growth_velocity for c in cities]),
        "ad_longevity": compute_median([c.ad_longevity for c in cities]),
        "creative_refresh": compute_median([c.creative_refresh for c in cities]),
        "contact_coverage": compute_median([c.contact_coverage for c in cities]),
        "smb_share": compute_median([c.smb_share for c in cities]),
        "direct_response": compute_median([c.direct_response for c in cities]),
        "category_diversity": compute_median([c.category_diversity for c in cities]),
        "competition_intensity": compute_median([c.competition_intensity for c in cities]),
    }

    results: list[CityScoreResult] = []

    for c in cities:
        # Calculate individual normalized metric scores (0 - 100)
        norm_scores = {
            "active_advertisers": normalize_metric_ratio(c.active_advertisers, medians["active_advertisers"]),
            "advertiser_density": normalize_metric_ratio(c.advertiser_density, medians["advertiser_density"]),
            "growth_velocity": normalize_metric_ratio(c.growth_velocity, medians["growth_velocity"]),
            "ad_longevity": normalize_metric_ratio(c.ad_longevity, medians["ad_longevity"]),
            "creative_refresh": normalize_metric_ratio(c.creative_refresh, medians["creative_refresh"]),
            "contact_coverage": normalize_metric_ratio(c.contact_coverage, medians["contact_coverage"]),
            "smb_share": normalize_metric_ratio(c.smb_share, medians["smb_share"]),
            "direct_response": normalize_metric_ratio(c.direct_response, medians["direct_response"]),
            "category_diversity": normalize_metric_ratio(c.category_diversity, medians["category_diversity"]),
            "competition_intensity": normalize_metric_ratio(c.competition_intensity, medians["competition_intensity"]),
            "inv_density": 100.0 - normalize_metric_ratio(c.advertiser_density, medians["advertiser_density"]),
            "inv_competition": 100.0 - normalize_metric_ratio(c.competition_intensity, medians["competition_intensity"]),
        }

        # Weighted composite score
        total_weight = sum(weights.values())
        score_sum = sum(norm_scores[m] * w for m, w in weights.items() if m in norm_scores)
        final_score = round(score_sum / total_weight, 1) if total_weight > 0 else 50.0

        # Sufficiency guard
        sample_ok = c.sample_size >= MIN_SAMPLE_THRESHOLD
        warning = None if sample_ok else f"Sample size ({c.sample_size}) below threshold ({MIN_SAMPLE_THRESHOLD}); scores greyed out."

        # Compute factor explainability
        contributions = [
            (m, (norm_scores[m] - 50.0) * weights[m])
            for m in weights if m in norm_scores
        ]
        contributions.sort(key=lambda x: x[1], reverse=True)

        positives = [f"{m.replace('_', ' ').capitalize()} (+{round(v, 1)})" for m, v in contributions if v > 0][:2]
        negatives = [f"{m.replace('_', ' ').capitalize()} ({round(v, 1)})" for m, v in contributions if v < 0][-2:]

        results.append(
            CityScoreResult(
                city_slug=c.city_slug,
                city_name=c.city_name,
                composite_score=final_score,
                sample_ok=sample_ok,
                sufficiency_warning=warning,
                raw_metrics=c.model_dump(),
                normalized_scores=norm_scores,
                top_positive_factors=positives or ["Standard baseline performance"],
                top_negative_factors=negatives or ["No significant drag detected"],
            )
        )

    # Sort results by composite score descending
    results.sort(key=lambda x: x.composite_score, reverse=True)
    return results
