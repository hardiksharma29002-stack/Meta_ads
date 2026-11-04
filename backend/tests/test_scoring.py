"""Unit Tests for City Vitality Scoring Math & Median Ratio Scaling."""

from app.services.scoring import (
    CityRawMetrics,
    compute_median,
    normalize_metric_ratio,
    evaluate_city_cohort,
)


def test_median_calculation():
    """Verify median computation on odd and even arrays."""
    assert compute_median([10, 20, 30]) == 20
    assert compute_median([10, 20, 30, 40]) == 25.0


def test_normalize_metric_ratio():
    """Verify log2 median ratio mapping where median = 50, double = 100, half = 0."""
    # At exact median -> 50.0
    assert normalize_metric_ratio(20.0, 20.0) == 50.0

    # Double the median -> 100.0 (log2(2) = 1.0 -> 50 + 50)
    assert normalize_metric_ratio(40.0, 20.0) == 100.0

    # Half the median -> 0.0 (log2(0.5) = -1.0 -> 50 - 50)
    assert normalize_metric_ratio(10.0, 20.0) == 0.0


def test_city_cohort_evaluation_and_sufficiency():
    """Verify multi-city cohort scoring and sufficiency warning guard."""
    cohort = [
        CityRawMetrics(
            city_slug="jaipur",
            city_name="Jaipur",
            urban_population=3000000,
            active_advertisers=400,
            advertiser_density=13.3,
            growth_velocity=0.30,
            ad_longevity=40.0,
            creative_refresh=3.0,
            contact_coverage=0.80,
            smb_share=0.85,
            direct_response=0.50,
            category_diversity=0.85,
            competition_intensity=3.0,
            sample_size=120,  # >= MIN_SAMPLE (50)
        ),
        CityRawMetrics(
            city_slug="kolkata",
            city_name="Kolkata",
            urban_population=4500000,
            active_advertisers=200,
            advertiser_density=4.4,
            growth_velocity=0.15,
            ad_longevity=25.0,
            creative_refresh=2.0,
            contact_coverage=0.50,
            smb_share=0.75,
            direct_response=0.30,
            category_diversity=0.70,
            competition_intensity=2.5,
            sample_size=30,   # < MIN_SAMPLE (50) -> sufficiency warning!
        ),
    ]

    results = evaluate_city_cohort(cohort, profile_key="outreach")
    assert len(results) == 2
    # Jaipur should be sample_ok = True
    jaipur = next(r for r in results if r.city_slug == "jaipur")
    assert jaipur.sample_ok is True
    assert jaipur.composite_score > 50.0

    # Kolkata should trigger sufficiency warning
    kolkata = next(r for r in results if r.city_slug == "kolkata")
    assert kolkata.sample_ok is False
    assert kolkata.sufficiency_warning is not None

