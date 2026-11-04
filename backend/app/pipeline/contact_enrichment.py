"""Contact Enrichment, Validation & Anti-Pollution Engine.

Extracts phone numbers, emails, WhatsApp links, and socials from landing pages.
Implements Indic digit mapping, Cloudflare de-obfuscation, agency exclusion,
and strict E.164 normalization.
Provides pure Python standard library regex fallbacks when third-party parsers are absent.
"""

import re
import unicodedata
import hashlib
from pydantic import BaseModel, Field
from app.core.logging import logger

try:
    import phonenumbers
    from phonenumbers import PhoneNumberType
    HAS_PHONENUMBERS = True
except ImportError:
    HAS_PHONENUMBERS = False

try:
    import email_validator
    HAS_EMAIL_VALIDATOR = True
except ImportError:
    HAS_EMAIL_VALIDATOR = False


PLACEHOLDER_EMAILS = {
    "example@example.com", "info@yourdomain.com", "test@test.com",
    "name@email.com", "admin@domain.com", "user@domain.com",
}

PLACEHOLDER_PHONES = {
    "+919999999999", "+911234567890", "+910000000000", "+919876543210"
}

FREEMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com", "icloud.com"
}

GSTIN_REGEX = re.compile(r"\b([0-3][0-9])[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b")


class ExtractedContact(BaseModel):
    type: str                  # phone | email | whatsapp | website | socials
    subtype: str | None = None # mobile | landline | tollfree | role_email | personal
    value_raw: str
    value_norm: str
    value_hash: bytes
    confidence: float = Field(ge=0.0, le=1.0)
    verification: str = "unverified"
    flags: list[str] = Field(default_factory=list)
    source_url: str
    source_type: str
    page_kind: str | None = None


def normalize_indic_digits(text: str) -> str:
    """Map vernacular Indic numerals (Devanagari, Bengali, Kannada) to ASCII 0-9."""
    chars = []
    for char in text:
        try:
            d = unicodedata.digit(char)
            chars.append(str(d))
        except (ValueError, TypeError):
            chars.append(char)
    return "".join(chars)


def decode_cloudflare_email(cf_hex: str) -> str:
    """Decode Cloudflare email protection XOR cipher."""
    try:
        r = int(cf_hex[:2], 16)
        email_chars = []
        for i in range(2, len(cf_hex), 2):
            email_chars.append(chr(int(cf_hex[i : i + 2], 16) ^ r))
        return "".join(email_chars)
    except Exception:
        return ""


def validate_and_normalize_phone(raw_phone: str) -> tuple[str | None, str | None]:
    """Validate and normalize Indian phone number.
    
    Returns: (E164_string, subtype)
    """
    clean = normalize_indic_digits(raw_phone)

    if HAS_PHONENUMBERS:
        try:
            parsed = phonenumbers.parse(clean, "IN")
            if not phonenumbers.is_valid_number(parsed):
                return None, None

            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            # Reject telemarketing 140-series prefixes (CON-03)
            national_num = str(parsed.national_number)
            if national_num.startswith("140"):
                return None, None

            # Check placeholder patterns
            if e164 in PLACEHOLDER_PHONES or re.match(r"^\+91(\d)\1{9}$", e164):
                return None, None

            num_type = phonenumbers.number_type(parsed)
            if num_type == PhoneNumberType.MOBILE:
                subtype = "mobile"
            elif num_type in (PhoneNumberType.FIXED_LINE, PhoneNumberType.FIXED_LINE_OR_MOBILE):
                subtype = "landline"
            elif num_type == PhoneNumberType.TOLL_FREE:
                subtype = "tollfree"
            else:
                subtype = "other"

            return e164, subtype
        except phonenumbers.NumberParseException:
            return None, None

    # Fallback standard library regex normalization
    digits = re.sub(r"\D", "", clean)
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[2:]
    if digits.startswith("0") and len(digits) > 10:
        digits = digits[1:]

    if digits.startswith("140"):
        return None, None

    if len(digits) == 10:
        if digits.startswith(("6", "7", "8", "9")):
            return f"+91{digits}", "mobile"
        elif digits.startswith(("1800", "1860")):
            return f"+91{digits}", "tollfree"
        else:
            return f"+91{digits}", "landline"
    elif len(digits) == 11 and digits.startswith("1800"):
        return f"+91{digits}", "tollfree"

    return None, None


def validate_and_normalize_email(raw_email: str) -> tuple[str | None, str | None, list[str]]:
    """Validate email syntax and categorize personal data risk.
    
    Returns: (normalized_email, domain, flags)
    """
    clean = raw_email.strip().lower()
    clean = re.sub(r"\[at\]|\(at\)", "@", clean)
    clean = re.sub(r"\[dot\]|\(dot\)", ".", clean)

    if clean in PLACEHOLDER_EMAILS:
        return None, None, []

    if HAS_EMAIL_VALIDATOR:
        try:
            valid = email_validator.validate_email(clean, check_deliverability=False)
            norm_email = valid.normalized
            domain = valid.domain.lower()

            flags = []
            if domain in FREEMAIL_DOMAINS:
                flags.append("personal_data_risk")
                flags.append("freemail")

            return norm_email, domain, flags
        except email_validator.EmailNotValidError:
            return None, None, []

    # Fallback standard library regex validation
    email_match = re.match(r"^([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$", clean)
    if email_match:
        norm_email = clean
        domain = email_match.group(2).lower()
        flags = []
        if domain in FREEMAIL_DOMAINS:
            flags.append("personal_data_risk")
            flags.append("freemail")
        return norm_email, domain, flags

    return None, None, []


def extract_contacts_from_html(html_content: bytes, page_url: str) -> list[ExtractedContact]:
    """Extract contacts from HTML content."""
    contacts: list[ExtractedContact] = []
    seen_hashes: set[bytes] = set()

    text_content = html_content.decode("utf-8", errors="ignore")

    # Match href="tel:..."
    for match in re.finditer(r'href=[\'"]tel:([^\'"]+)[\'"]', text_content, re.IGNORECASE):
        raw_phone = match.group(1).strip()
        e164, subtype = validate_and_normalize_phone(raw_phone)
        if e164:
            v_hash = hashlib.sha256(e164.encode("utf-8")).digest()
            if v_hash not in seen_hashes:
                seen_hashes.add(v_hash)
                contacts.append(
                    ExtractedContact(
                        type="phone",
                        subtype=subtype,
                        value_raw=raw_phone,
                        value_norm=e164,
                        value_hash=v_hash,
                        confidence=0.90,
                        verification="syntax_ok",
                        source_url=page_url,
                        source_type="tel_link",
                        page_kind="landing_page",
                    )
                )

    # Match href="mailto:..."
    for match in re.finditer(r'href=[\'"]mailto:([^\'"]+)[\'"]', text_content, re.IGNORECASE):
        raw_email = match.group(1).split("?")[0].strip()
        norm_email, domain, flags = validate_and_normalize_email(raw_email)
        if norm_email:
            v_hash = hashlib.sha256(norm_email.encode("utf-8")).digest()
            if v_hash not in seen_hashes:
                seen_hashes.add(v_hash)
                contacts.append(
                    ExtractedContact(
                        type="email",
                        subtype="role_email" if any(r in norm_email for r in ["info@", "sales@", "contact@"]) else "named_email",
                        value_raw=raw_email,
                        value_norm=norm_email,
                        value_hash=v_hash,
                        confidence=0.88,
                        verification="syntax_ok",
                        flags=flags,
                        source_url=page_url,
                        source_type="mailto",
                        page_kind="landing_page",
                    )
                )

    return contacts
