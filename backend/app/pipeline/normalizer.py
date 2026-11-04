"""Payload Normalization & Sanitization Engine.

Implements Unicode NFC normalization, URL canonicalization, eTLD+1 extraction,
and content hash calculation (SHA-256).
Provides standard library urllib fallback if tldextract is not installed.
"""

import re
import unicodedata
import hashlib
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from app.collectors.base import RawAd

try:
    import tldextract

    def extract_registered_domain(url: str) -> str | None:
        ext = tldextract.extract(url)
        return ext.registered_domain.lower() if ext.registered_domain else None
except ImportError:
    def extract_registered_domain(url: str) -> str | None:
        try:
            netloc = urlparse(url).netloc.split(":")[0].lower()
            parts = netloc.split(".")
            if len(parts) >= 2:
                # Basic Indian ccTLD handling (e.g. example.co.in)
                if len(parts) >= 3 and parts[-2] in ("co", "com", "edu", "gov", "org") and parts[-1] == "in":
                    return ".".join(parts[-3:])
                return ".".join(parts[-2:])
            return netloc
        except Exception:
            return None


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "igshid", "mc_eid", "ref", "source", "_ga"
}

SUFFIX_PATTERN = re.compile(
    r"\b(pvt ltd|private limited|ltd|limited|inc|corp|co|official|llp)\b",
    re.IGNORECASE
)

PLACEHOLDER_REGEX = re.compile(r"\{\{.*?\}\}|<%.*?%>")


def normalize_unicode_text(text: str | None) -> str:
    """Normalize string to Unicode NFC and remove bidi/zero-width formatting."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text)
    norm = re.sub(r"[\u200B-\u200D\uFEFF\u200E\u200F]", "", norm)
    return norm.strip()


def normalize_page_name(name: str) -> str:
    """Produce searchable normalized page name: lowercase, stripped suffixes, unaccented."""
    text = normalize_unicode_text(name).lower()
    text = re.sub(r"\b(shree|sri|shri)\b", "shri", text)
    text = SUFFIX_PATTERN.sub("", text)
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def canonicalize_url(url: str | None) -> tuple[str | None, str | None]:
    """Strip marketing tracking parameters and extract eTLD+1 registered domain.
    
    Returns: (clean_url, registered_domain)
    """
    if not url:
        return None, None

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None, None

        query_params = parse_qsl(parsed.query, keep_blank_values=False)
        clean_params = [(k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS]
        clean_query = urlencode(clean_params)

        clean_url = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            clean_query,
            "",
        ))

        registered_domain = extract_registered_domain(clean_url)
        return clean_url, registered_domain
    except Exception:
        return url, None


def has_template_placeholders(text: str | None) -> bool:
    """Detect DCO template placeholders (e.g. {{product.name}})."""
    if not text:
        return False
    return bool(PLACEHOLDER_REGEX.search(text))


def compute_ad_content_hash(
    body: str | None,
    headline: str | None,
    cta: str | None,
    domain: str | None,
    media_type: str | None,
) -> bytes:
    """Compute SHA-256 fingerprint for distinct creative identification."""
    parts = [
        normalize_unicode_text(body or "").lower(),
        normalize_unicode_text(headline or "").lower(),
        (cta or "").strip().upper(),
        (domain or "").strip().lower(),
        (media_type or "").strip().lower(),
    ]
    raw_str = "|".join(parts)
    return hashlib.sha256(raw_str.encode("utf-8")).digest()
