from __future__ import annotations
import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger("endrian.mailer")


def send_email(
    *,
    sender_email: str,
    app_password: str,
    to_email: str,
    subject: str,
    body: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    timeout: float = 10.0,
) -> Optional[str]:
    """Sends a plain-text email via SMTP (Gmail by default, STARTTLS).

    Returns None on success, or an error message string on failure. Never
    raises — a transient SMTP problem must not break the caller's request.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(body)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.send_message(msg)
        return None
    except Exception as exc:  # noqa: BLE001 - any SMTP/network failure is reported, not raised
        logger.warning("Email send failed to %s: %s", to_email, exc)
        return f"{type(exc).__name__}: {exc}"
