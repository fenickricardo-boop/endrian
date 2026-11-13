from __future__ import annotations
import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+ ?@ ?[A-Z0-9.-]+ ?\. ?[A-Z]{2,}\b", re.I)
RUT_RE = re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}\s*-\s*[0-9Kk]\b|\b\d{7,8}\s*-\s*[0-9Kk]\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?56\s*)?(?:9\s*)?\d{4}[\s-]?\d{4}(?!\d)")
CARD_RE = re.compile(r"\b(?:\d[ .-]*?){13,19}\b")


def contains_obvious_personal_data(text: str) -> bool:
    return any(rx.search(text or "") for rx in (EMAIL_RE, RUT_RE, PHONE_RE, CARD_RE))
