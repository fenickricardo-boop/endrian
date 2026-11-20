from __future__ import annotations
import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+ ?@ ?[A-Z0-9.-]+ ?\. ?[A-Z]{2,}\b", re.I)
RUT_RE = re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}\s*-\s*[0-9Kk]\b|\b\d{7,8}\s*-\s*[0-9Kk]\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?56\s*)?(?:9\s*)?\d{4}[\s-]?\d{4}(?!\d)")
CARD_RE = re.compile(r"\b(?:\d[ .-]*?){13,19}\b")

# IETF-reserved domains (RFC 2606) that can never resolve to a real mailbox.
# This project's own documented synthetic QA identity (e.g. "nombre@example.invalid")
# relies on one of these, so an email using them is never real PII.
_EXAMPLE_EMAIL_DOMAINS = {"example.com", "example.net", "example.org", "example.invalid"}


def contains_obvious_personal_data(text: str) -> bool:
    text = text or ""
    if any(rx.search(text) for rx in (RUT_RE, PHONE_RE, CARD_RE)):
        return True
    for match in EMAIL_RE.finditer(text):
        domain = match.group(0).split("@", 1)[-1].strip(" .").lower()
        if domain not in _EXAMPLE_EMAIL_DOMAINS:
            return True
    return False
