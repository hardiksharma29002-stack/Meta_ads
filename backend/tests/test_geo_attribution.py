"""Unit Tests for Multi-Signal Geo-Attribution (GEO-01 to GEO-13)."""

from app.pipeline.geo_attribution import (
    GeoSignal,
    compute_noisy_or_attribution,
    extract_std_code_signals,
    extract_ad_text_signals,
)


def test_noisy_or_single_signal():
    """Verify single signal attribution probability."""
    signals = [
        GeoSignal(kind="pincode", city_slug="jaipur", strength=0.85, source_ref="PIN:302001")
    ]
    res = compute_noisy_or_attribution(signals)
    assert "jaipur" in res
    assert res["jaipur"]["confidence"] == 0.85
    assert res["jaipur"]["tier"] == "confirmed"


def test_noisy_or_signal_deduplication():
    """Verify that multiple signals of the exact same kind do NOT artificially inflate confidence."""
    signals = [
        GeoSignal(kind="pincode", city_slug="jaipur", strength=0.85, source_ref="PIN:302001"),
        GeoSignal(kind="pincode", city_slug="jaipur", strength=0.85, source_ref="PIN:302020"),
    ]
    res = compute_noisy_or_attribution(signals)
    # Strength of same kind collapses to max (0.85), not 1 - (1-0.85)^2 = 0.9775
    assert res["jaipur"]["confidence"] == 0.85


def test_noisy_or_combining_distinct_signals():
    """Verify combining distinct signal kinds: PIN (0.85) + STD code (0.60)."""
    signals = [
        GeoSignal(kind="pincode", city_slug="jaipur", strength=0.85, source_ref="PIN:302001"),
        GeoSignal(kind="std_code", city_slug="jaipur", strength=0.60, source_ref="STD:0141"),
    ]
    res = compute_noisy_or_attribution(signals)
    # p = 1 - (1 - 0.85) * (1 - 0.60) = 1 - 0.15 * 0.40 = 1 - 0.06 = 0.94
    assert round(res["jaipur"]["confidence"], 2) == 0.94
    assert res["jaipur"]["tier"] == "confirmed"


def test_landline_std_code_extraction():
    """Verify landline STD code resolves accurately to city (GEO-10)."""
    signals = extract_std_code_signals("0141-2365401")
    assert len(signals) == 1
    assert signals[0].city_slug == "jaipur"

    # Mumbai landline 022
    signals = extract_std_code_signals("+91-22-26458901")
    assert any(s.city_slug == "mumbai" for s in signals)


def test_transit_destination_downweighting():
    """Verify transit destination phrasing is heavily penalized (GEO-12)."""
    aliases = {"jaipur": "jaipur"}
    # Standard location mention
    normal = extract_ad_text_signals("Showroom located in Jaipur city", aliases)
    assert normal[0].strength == 0.50

    # Destination transit phrase: "cabs to jaipur"
    transit = extract_ad_text_signals("Book cheap cabs to Jaipur today", aliases)
    assert transit[0].strength == 0.15

