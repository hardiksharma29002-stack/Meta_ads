"""Structured Logging with Mandatory PII Redaction Filter.

Satisfies SEC-10: Plaintext phone numbers and emails are never logged;
log lines output SHA-256 hash prefixes instead.
Provides standard library fallback if structlog is not yet installed.
"""

import re
import hashlib
import logging
from typing import Any

# Regular expressions for identifying contact PII
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}")


def mask_contact_string(text: str) -> str:
    """Mask email addresses and phone numbers in a string with their SHA-256 prefix."""
    if not isinstance(text, str):
        return text

    def mask_email(match):
        val = match.group(0).lower()
        h = hashlib.sha256(val.encode("utf-8")).hexdigest()[:8]
        return f"[EMAIL:sha256_{h}]"

    def mask_phone(match):
        val = re.sub(r"\D", "", match.group(0))
        h = hashlib.sha256(val.encode("utf-8")).hexdigest()[:8]
        return f"[PHONE:sha256_{h}]"

    text = EMAIL_REGEX.sub(mask_email, text)
    text = PHONE_REGEX.sub(mask_phone, text)
    return text


def pii_redaction_processor(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Recursively scrub contact PII from log dictionary values."""
    for key, value in list(event_dict.items()):
        if isinstance(value, str):
            event_dict[key] = mask_contact_string(value)
        elif isinstance(value, dict):
            event_dict[key] = pii_redaction_processor(logger, method_name, value)
    return event_dict


class FallbackLogger:
    """Standard library logging fallback implementing structlog-style keyword logging."""
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        self._log = logging.getLogger("adatlas")

    def info(self, event: str, **kwargs):
        msg = f"{event} {mask_contact_string(str(kwargs))}" if kwargs else event
        self._log.info(msg)

    def warn(self, event: str, **kwargs):
        msg = f"{event} {mask_contact_string(str(kwargs))}" if kwargs else event
        self._log.warning(msg)

    def error(self, event: str, **kwargs):
        msg = f"{event} {mask_contact_string(str(kwargs))}" if kwargs else event
        self._log.error(msg)


try:
    import structlog

    def setup_logging():
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                pii_redaction_processor,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    setup_logging()
    logger = structlog.get_logger()
except ImportError:
    def setup_logging():
        pass

    logger = FallbackLogger()
