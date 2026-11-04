"""Unit Tests for Normalization, Content Hashing & URL Canonicalization."""

from app.pipeline.normalizer import (
    normalize_unicode_text,
    normalize_page_name,
    canonicalize_url,
    compute_ad_content_hash,
    has_template_placeholders,
)


def test_unicode_nfc_and_zero_width_strip():
    """Verify Unicode NFC and zero-width/bidi stripping (SRC-17)."""
    raw = "Jaipur\u200B Craft\u200E Villa"
    norm = normalize_unicode_text(raw)
    assert norm == "Jaipur Craft Villa"


def test_page_name_normalization():
    """Verify company suffix stripping and lowercase transformation."""
    raw = "Example Jewellers Pvt Ltd Official"
    norm = normalize_page_name(raw)
    assert "pvt ltd" not in norm
    assert "official" not in norm
    assert norm == "example jewellers"


def test_url_canonicalization_and_etld():
    """Verify stripping of tracking params and extraction of eTLD+1."""
    url = "https://www.example.co.in/products/handicrafts?utm_source=fb&utm_medium=cpc&fbclid=12345"
    clean_url, domain = canonicalize_url(url)
    assert "utm_source" not in clean_url
    assert "fbclid" not in clean_url
    assert domain == "example.co.in"


def test_template_placeholder_detection():
    """Verify DCO template placeholder detection (SRC-13)."""
    assert has_template_placeholders("Buy {{product.name}} in {{city}} today!") is True
    assert has_template_placeholders("Standard retail advertisement copy") is False


def test_ad_content_hash_deterministic():
    """Verify that SHA-256 content hash is deterministic."""
    h1 = compute_ad_content_hash("Ad text", "Headline", "SHOP_NOW", "brand.in", "image")
    h2 = compute_ad_content_hash("Ad text", "Headline", "SHOP_NOW", "brand.in", "image")
    assert h1 == h2
    assert len(h1) == 32

