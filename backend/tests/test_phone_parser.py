"""Unit & Property Tests for Indian Phone Normalization & Indic Numerals."""

from app.pipeline.contact_enrichment import (
    validate_and_normalize_phone,
    normalize_indic_digits,
    validate_and_normalize_email,
)


def test_standard_indian_phone_formats():
    """Test standard Indian telephone formats across mobile, landline, and toll-free."""
    # Standard 10-digit mobile
    e164, subtype = validate_and_normalize_phone("9829012345")
    assert e164 == "+919829012345"
    assert subtype == "mobile"

    # Leading zero format
    e164, subtype = validate_and_normalize_phone("09829012345")
    assert e164 == "+919829012345"

    # With country code prefix
    e164, subtype = validate_and_normalize_phone("+91 98290-12345")
    assert e164 == "+919829012345"

    # Jaipur landline with STD 0141
    e164, subtype = validate_and_normalize_phone("0141-2365401")
    assert e164 == "+911412365401"
    assert subtype == "landline"

    # Toll-free 1800 number
    e164, subtype = validate_and_normalize_phone("1800-111-222")
    assert e164 == "+911800111222"
    assert subtype == "tollfree"


def test_indic_numeral_mapping():
    """Verify that Devanagari, Bengali, and Kannada digits map correctly to ASCII (CON-04)."""
    # Devanagari: ९८२९०१२३४५ -> 9829012345
    devanagari = "९८२९०१२३४५"
    mapped = normalize_indic_digits(devanagari)
    assert mapped == "9829012345"

    e164, _ = validate_and_normalize_phone(devanagari)
    assert e164 == "+919829012345"

    # Bengali: ৯৮২৯০১২৩৪৫ -> 9829012345
    bengali = "৯৮২৯০১২৩৪৫"
    assert normalize_indic_digits(bengali) == "9829012345"


def test_telemarketer_140_rejection():
    """Verify telemarketing 140-series prefixes are rejected (CON-03)."""
    e164, _ = validate_and_normalize_phone("1409829012")
    assert e164 is None


def test_email_validation_and_freemail_flag():
    """Verify email normalization and personal_data_risk classification (CON-07)."""
    # Role email
    email, domain, flags = validate_and_normalize_email("info@company.in")
    assert email == "info@company.in"
    assert "freemail" not in flags

    # Freemail address
    email, domain, flags = validate_and_normalize_email("business.sales@gmail.com")
    assert email == "business.sales@gmail.com"
    assert "personal_data_risk" in flags
    assert "freemail" in flags

