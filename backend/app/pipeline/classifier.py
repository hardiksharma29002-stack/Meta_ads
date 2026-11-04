"""Taxonomy Classification & Risk Flagging Service.

Classifies ad copy into two-level category taxonomy using deterministic
rules first, with an optional cached free-tier LLM fallback.
Assigns risk tags (scam, gambling, political, govt).
"""

import re
from typing import Any
from app.core.logging import logger

# Deterministic keyword mapping for L1 / L2 taxonomy
TAXONOMY_RULES = {
    "jewellery": {
        "slug": "jewellery",
        "name": "Jewellery & Accessories",
        "keywords": ["jewellery", "kundan", "polki", "gold", "diamond", "silver", "necklace", "bangles", "earrings", "solitaire", "jewelers"],
    },
    "education-coaching": {
        "slug": "education-coaching",
        "name": "Education & Career",
        "keywords": ["coaching", "neet", "jee", "iit", "upsc", "classes", "admissions", "school", "college", "university", "faculty", "foundation batch"],
    },
    "fashion-apparel": {
        "slug": "fashion-apparel",
        "name": "Fashion & Apparel",
        "keywords": ["saree", "bridal", "lehenga", "suit", "kurti", "apparel", "clothing", "menswear", "ethnic wear", "handloom", "textiles"],
    },
    "food-hospitality": {
        "slug": "food-hospitality",
        "name": "Food, Dining & Hospitality",
        "keywords": ["restaurant", "cafe", "bakery", "sweets", "dining", "bar", "resort", "hotel", "catering", "buffet", "dine-in"],
    },
    "healthcare-clinics": {
        "slug": "healthcare-clinics",
        "name": "Healthcare & Wellness",
        "keywords": ["dental", "clinic", "hospital", "dentist", "aligners", "implants", "ayurveda", "homoeopathy", "gym", "fitness", "crossfit"],
    },
    "real-estate": {
        "slug": "real-estate",
        "name": "Real Estate & Construction",
        "keywords": ["bhk", "apartment", "villa", "plots", "real estate", "flats", "interior design", "architecture", "residences", "commercial space"],
    },
    "b2b-services": {
        "slug": "b2b-services",
        "name": "B2B, Logistics & IT",
        "keywords": ["software", "cloud", "saas", "agency", "digital marketing", "manufacturing", "packers and movers", "logistics", "ca", "tax"],
    },
}

# Risk detection patterns
RISK_RULES = {
    "gambling": re.compile(r"\b(casino|rummy|teen patti|betting|win cash daily|aviator game|stake)\b", re.IGNORECASE),
    "scam": re.compile(r"\b(work from home earn 50000|guaranteed return 100%|crypto double|task earning)\b", re.IGNORECASE),
    "political": re.compile(r"\b(bjp|congress|aap|election|vote for|parliament|mla|mp|political campaign)\b", re.IGNORECASE),
}


def classify_ad_category(headline: str | None, body: str | None) -> tuple[str, str, float]:
    """Classify ad content into primary category.
    
    Returns: (category_slug, category_name, confidence)
    """
    text = f"{headline or ''} {body or ''}".lower()

    best_match = ("b2b-services", "B2B, Logistics & IT", 0.50)
    highest_score = 0

    for cat_slug, info in TAXONOMY_RULES.items():
        score = sum(1 for kw in info["keywords"] if kw in text)
        if score > highest_score:
            highest_score = score
            best_match = (info["slug"], info["name"], min(0.95, 0.60 + (score * 0.10)))

    return best_match


def detect_risk_flags(headline: str | None, body: str | None) -> list[str]:
    """Detect and assign compliance risk flags (ENT-04, LEG-07)."""
    text = f"{headline or ''} {body or ''}"
    flags: list[str] = []

    for risk_kind, pattern in RISK_RULES.items():
        if pattern.search(text):
            flags.append(risk_kind)

    return flags

