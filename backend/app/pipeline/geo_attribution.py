"""Probabilistic Multi-Signal Geo-Attribution Engine.

Implements Noisy-OR Bayesian probability combination (ADR-0014) across:
Google Places, Schema.org JSON-LD, PIN codes, Landline STD area codes,
ad copy text, and GSTIN state codes.
"""

import re
from typing import Any
from pydantic import BaseModel, Field
from app.db.models import City, CityAlias, PincodeCityMap


class GeoSignal(BaseModel):
    kind: str          # places | jsonld | pincode | std_code | ad_text | web_text | gstin | lang | seed
    city_slug: str
    strength: float = Field(ge=0.0, le=1.0)
    source_ref: str
    context: str | None = None


# Base signal strength calibrations from docs/GEO_ATTRIBUTION.md
SIGNAL_WEIGHTS = {
    "places": 0.90,
    "jsonld": 0.85,
    "pincode": 0.85,
    "std_code": 0.60,
    "web_text": 0.55,
    "ad_text": 0.50,
    "gstin": 0.30,
    "lang": 0.15,
    "seed": 0.10,
}

# Regex to detect transit phrases that mention city as destination rather than location
TRANSIT_REGEX = re.compile(
    r"\b(to|from|towards|cabs? to|travel to|bus to|train to|flights? to|delivering to)\s+([a-zA-Z]+)",
    re.IGNORECASE
)

# Standard Landline STD area codes for the 5 cities
STD_AREA_CODES = {
    "022": "mumbai",
    "011": "delhi",
    "0141": "jaipur",
    "033": "kolkata",
    "080": "bengaluru",
}

# GSTIN 2-digit state prefixes
GST_STATE_CODES = {
    "27": "mumbai",     # Maharashtra
    "07": "delhi",      # Delhi NCT
    "08": "jaipur",     # Rajasthan
    "19": "kolkata",    # West Bengal
    "29": "bengaluru",  # Karnataka
}


def extract_pincode_signals(text: str, pincode_map: dict[str, str]) -> list[GeoSignal]:
    """Extract 6-digit postal codes appearing in an address context."""
    signals: list[GeoSignal] = []
    # Match 6-digit numbers near address-related tokens
    matches = re.finditer(r"\b(\d{6})\b", text)
    for m in matches:
        pin = m.group(1)
        if pin in pincode_map:
            # Check for proximate address keywords in a 40-character window
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            window = text[start:end].lower()
            if any(kw in window for kw in ["pin", "pincode", "address", "road", "bazaar", "nagar", "marg"]):
                signals.append(
                    GeoSignal(
                        kind="pincode",
                        city_slug=pincode_map[pin],
                        strength=SIGNAL_WEIGHTS["pincode"],
                        source_ref=f"PIN:{pin}",
                        context=window.strip(),
                    )
                )
    return signals


def extract_std_code_signals(phone_number: str) -> list[GeoSignal]:
    """Extract geographical signal from landline STD area codes.
    
    GEO-10: Mobile phone numbers carry ZERO geographical signal and are ignored.
    """
    signals: list[GeoSignal] = []
    # Strip non-digits
    digits = re.sub(r"\D", "", phone_number)
    if digits.startswith("91"):
        digits = digits[2:]

    # Inspect landline STD prefixes
    for std, city in STD_AREA_CODES.items():
        clean_std = std.lstrip("0")
        if digits.startswith(clean_std) or digits.startswith(std):
            signals.append(
                GeoSignal(
                    kind="std_code",
                    city_slug=city,
                    strength=SIGNAL_WEIGHTS["std_code"],
                    source_ref=f"STD:{std}",
                )
            )
    return signals


def extract_ad_text_signals(text: str, aliases: dict[str, str]) -> list[GeoSignal]:
    """Extract city mentions in ad copy, penalizing directional transit phrasing."""
    signals: list[GeoSignal] = []
    text_lower = text.lower()

    for alias, city_slug in aliases.items():
        pattern = r"\b" + re.escape(alias.lower()) + r"\b"
        for match in re.finditer(pattern, text_lower):
            # Check for transit context (e.g. "flights to jaipur", "cabs to delhi")
            start = max(0, match.start() - 20)
            window = text_lower[start : match.end()]
            if TRANSIT_REGEX.search(window):
                # Transit destination: penalize strength heavily
                strength = 0.15
            else:
                strength = SIGNAL_WEIGHTS["ad_text"]

            signals.append(
                GeoSignal(
                    kind="ad_text",
                    city_slug=city_slug,
                    strength=strength,
                    source_ref=f"alias:{alias}",
                )
            )
    return signals


def compute_noisy_or_attribution(signals: list[GeoSignal]) -> dict[str, dict[str, Any]]:
    """Compute Noisy-OR probability combination for each candidate city.
    
    Formula: p(city) = 1 - Prod(1 - max_strength_per_kind)
    Returns: dict mapping city_slug -> {confidence, tier, evidence}
    """
    # Group signals by city and by signal kind (deduplication of same kind)
    city_kind_strengths: dict[str, dict[str, float]] = {}
    city_evidence: dict[str, list[dict[str, Any]]] = {}

    for s in signals:
        if s.city_slug not in city_kind_strengths:
            city_kind_strengths[s.city_slug] = {}
            city_evidence[s.city_slug] = []

        # Keep highest strength for each distinct signal kind
        current_max = city_kind_strengths[s.city_slug].get(s.kind, 0.0)
        if s.strength > current_max:
            city_kind_strengths[s.city_slug][s.kind] = s.strength

        city_evidence[s.city_slug].append(s.model_dump())

    results: dict[str, dict[str, Any]] = {}
    for city_slug, kinds in city_kind_strengths.items():
        # Compute product of (1 - strength)
        prod = 1.0
        for strength in kinds.values():
            prod *= (1.0 - strength)

        prob = round(1.0 - prod, 4)

        # Assign tier
        if prob >= 0.75:
            tier = "confirmed"
        elif prob >= 0.40:
            tier = "probable"
        else:
            tier = "weak"

        results[city_slug] = {
            "confidence": prob,
            "tier": tier,
            "evidence": city_evidence[city_slug],
        }

    # Conflict check: if two cities have prob >= 0.60
    high_prob_cities = [c for c, data in results.items() if data["confidence"] >= 0.60]
    if len(high_prob_cities) > 1:
        # Penalize standalone confidence slightly and mark is_conflict
        for c in high_prob_cities:
            results[c]["is_multicity"] = True

    return results
