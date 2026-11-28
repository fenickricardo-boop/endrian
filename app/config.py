from __future__ import annotations
from dataclasses import dataclass, field
import os
import secrets


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


# Environments treated as open local/QA development — no app-wide credential
# is required. Anything else (staging, production, a typo of either, ...)
# fails closed and requires STAGING_ACCESS_USER/PASSWORD. QA_CONTROLLED_TEST_ONLY
# is the documented local launcher mode (START_LAB_QA.bat / .env.example),
# bound to 127.0.0.1 by the operator and separately gated on its own
# QA_CONTROL_USER/PASSWORD for the /qa-control admin endpoints.
OPEN_APP_ENVS = {"local", "qa_controlled_test_only"}


def _session_secret_default() -> str:
    # Falls back to a per-process random secret so unsigned/forged session
    # cookies are always rejected, even if SESSION_SECRET is not configured.
    return os.getenv("SESSION_SECRET", "") or secrets.token_hex(32)


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    model_mode: str = os.getenv("MODEL_MODE", "deterministic").strip().lower()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    # "-lite" has its own, far less restrictive free-tier daily quota than
    # the full "flash" line (the latter is capped at ~20 requests/day on a
    # free API key) and was validated to produce the same structured output
    # reliably for this narrow extraction task.
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    max_output_tokens: int = _int("OPENAI_MAX_OUTPUT_TOKENS", 700)
    # Gemini's "thinking" tokens are billed against the same output budget as
    # the actual JSON answer, so it needs a higher ceiling than OpenAI's
    # reasoning-effort-based accounting to avoid truncating mid-response.
    gemini_max_output_tokens: int = _int("GEMINI_MAX_OUTPUT_TOKENS", 2048)
    # Real order-confirmation email via Gmail SMTP. Optional: unset by
    # default, in which case no email is ever sent (unchanged behavior).
    gmail_sender_email: str = os.getenv("GMAIL_SENDER_EMAIL", "")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD", "")
    session_ttl_seconds: int = _int("SESSION_TTL_SECONDS", 86400)
    max_turns_per_session: int = _int("MAX_TURNS_PER_SESSION", 30)
    ip_requests_per_minute: int = _int("IP_REQUESTS_PER_MINUTE", 60)
    session_requests_per_minute: int = _int("SESSION_REQUESTS_PER_MINUTE", 45)
    db_path: str = os.getenv("QA_DB_PATH", "data/qa_sessions.db")
    cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "endrian_qa_session")
    cookie_secure: bool = _bool("COOKIE_SECURE", os.getenv("APP_ENV", "local") != "local")
    staging_user: str = os.getenv("STAGING_ACCESS_USER", "")
    staging_password: str = os.getenv("STAGING_ACCESS_PASSWORD", "")
    qa_control_user: str = os.getenv("QA_CONTROL_USER", "")
    qa_control_password: str = os.getenv("QA_CONTROL_PASSWORD", "")
    qa_auto_registration: bool = _bool("QA_EPHEMERAL_REGISTRATION", True)
    session_secret: str = field(default_factory=_session_secret_default)
    # Only trust X-Forwarded-For when the deployment explicitly runs behind a
    # known reverse proxy; otherwise it is a client-controlled, spoofable header.
    trust_proxy_headers: bool = _bool("TRUST_PROXY_HEADERS", False)

    @property
    def real_model_enabled(self) -> bool:
        return self.model_mode in {"real", "gemini"}

    @property
    def email_enabled(self) -> bool:
        return bool(self.gmail_sender_email and self.gmail_app_password)

    @property
    def qa_control_enabled(self) -> bool:
        return self.app_env.strip().upper() == "QA_CONTROLLED_TEST_ONLY"

    @property
    def basic_auth_required(self) -> bool:
        return self.app_env.strip().lower() not in OPEN_APP_ENVS


def validate_runtime_settings(cfg: "Settings") -> None:
    env = cfg.app_env.strip().lower()
    # Fail-closed by default: any environment outside the explicit open-env
    # allowlist must present access credentials. Previously only the exact
    # string "staging" required them, so a typo'd or unrecognized APP_ENV
    # (e.g. "production") silently fell through to an unauthenticated
    # deployment.
    if env not in OPEN_APP_ENVS:
        label = "Staging access" if env == "staging" else f"Non-local deployment ({cfg.app_env!r}) access"
        missing = []
        if not cfg.staging_user:
            missing.append("STAGING_ACCESS_USER")
        if not cfg.staging_password:
            missing.append("STAGING_ACCESS_PASSWORD")
        if missing:
            raise RuntimeError(
                f"{label} is fail-closed. Missing required secret(s): " + ", ".join(missing)
            )
        if not cfg.cookie_secure:
            raise RuntimeError(f"{label} requires COOKIE_SECURE=true")
    # QA_CONTROL_USER/PASSWORD are not mandatory at startup: QA_CONTROLLED_TEST_ONLY
    # is also the documented zero-config local launcher mode (START_LAB_QA.bat,
    # bound to 127.0.0.1 with no reverse proxy in front). When left unset, the
    # /qa-control gate in app/main.py falls back to a loopback-only check, which
    # is sound only for that bare localhost scenario. Any QA_CONTROLLED_TEST_ONLY
    # deployment that is NOT a bare localhost process (behind a reverse proxy,
    # a container port-forward, etc.) MUST set both, or the admin endpoints are
    # unprotected for that deployment.


settings = Settings()
