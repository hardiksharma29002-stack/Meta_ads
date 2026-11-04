"""Entity Resolution & Operational Scope Classifier.

Identifies potential duplicate Meta Pages belonging to the identical business
and classifies geographical scope (local, regional, national).
"""

try:
    from rapidfuzz import fuzz
except ImportError:
    from difflib import SequenceMatcher

    class _FuzzFallback:
        @staticmethod
        def ratio(s1: str, s2: str) -> float:
            return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio() * 100

        @staticmethod
        def token_sort_ratio(s1: str, s2: str) -> float:
            t1 = " ".join(sorted(str(s1).lower().split()))
            t2 = " ".join(sorted(str(s2).lower().split()))
            return SequenceMatcher(None, t1, t2).ratio() * 100

    fuzz = _FuzzFallback()
from app.db.models import Advertiser, Contact


def compute_entity_similarity(name_a: str, name_b: str) -> float:
    """Compute token sort ratio similarity between two business names."""
    return fuzz.token_sort_ratio(name_a, name_b)


def should_suggest_merge(
    adv_a: Advertiser,
    adv_b: Advertiser,
    contacts_a: list[Contact] | None = None,
    contacts_b: list[Contact] | None = None,
) -> tuple[bool, str]:
    """Evaluate whether two advertisers share strong signals indicating common ownership.
    
    Returns: (should_merge, reason)
    """
    if adv_a.id == adv_b.id:
        return False, "identical"

    # Signal 1: Shared primary web domain
    if adv_a.primary_domain and adv_b.primary_domain:
        if adv_a.primary_domain == adv_b.primary_domain:
            return True, f"Shared domain: {adv_a.primary_domain}"

    # Signal 2: Shared verified contact value
    if contacts_a and contacts_b:
        hashes_a = {c.value_hash for c in contacts_a if c.type in ("phone", "email")}
        hashes_b = {c.value_hash for c in contacts_b if c.type in ("phone", "email")}
        common = hashes_a.intersection(hashes_b)
        if common:
            return True, "Shared verified phone or email"

    # Signal 3: Very high name similarity + partial domain agreement
    sim = compute_entity_similarity(adv_a.page_name_norm, adv_b.page_name_norm)
    if sim >= 92.0:
        return True, f"High name similarity ({sim:.1f}%)"

    return False, "insufficient_signals"


def classify_advertiser_scope(city_count: int, has_multistate_gst: bool = False) -> str:
    """Classify advertiser operational footprint into local, regional, or national."""
    if has_multistate_gst or city_count >= 5:
        return "national"
    elif city_count >= 2:
        return "regional"
    elif city_count == 1:
        return "local"
    return "unknown"
