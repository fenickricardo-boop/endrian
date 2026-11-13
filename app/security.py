from __future__ import annotations
import base64
import hmac
from fastapi import Request
from fastapi.responses import JSONResponse


def basic_auth_ok(request: Request, expected_user: str, expected_password: str) -> bool:
    # Never treat a missing staging credential as an open-access fallback.
    if not expected_user or not expected_password:
        return False
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(auth[6:]).decode("utf-8")
        user, password = raw.split(":", 1)
    except Exception:
        return False
    return hmac.compare_digest(user, expected_user) and hmac.compare_digest(password, expected_password)


def unauthorized_response() -> JSONResponse:
    return JSONResponse(
        {"detail": "Staging access required"},
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="ENDRIAN QA"'},
    )
