from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY
from app.main import app
from app.service import GuideService
from app.session_repository import SessionRepository


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")
PHONE_CASES = [
    {"country_code":"CL","country_name":"Chile","calling_code":"+56","national_number":"212345678"},
    {"country_code":"AR","country_name":"Argentina","calling_code":"+54","national_number":"1123456789"},
    {"country_code":"US","country_name":"Estados Unidos","calling_code":"+1","national_number":"2025550199"},
]


def service(tmp_path, name="v043"):
    cfg = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / f"{name}.db"), cookie_secure=False)
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))


def contact_ready(svc, sid):
    svc.chat(sid, FIXTURE_INITIAL)
    svc.chat(sid, FIXTURE_REPLY)
    svc.chat(sid, "No, eso es todo.")
    svc.proposal_action(sid, "continue")


def register(svc, sid, name, email, fixture=None):
    kwargs = {"country_code": "CL", "country_name": "Chile"}
    if fixture:
        kwargs.update(
            phone_country_code=fixture["country_code"],
            phone_country_name=fixture["country_name"],
            phone_calling_code=fixture["calling_code"],
            phone_national_number=fixture["national_number"],
        )
    return svc.complete_registration(sid, name, email, **kwargs)


def test_two_distinct_contacts_and_multiple_structurally_valid_phones(tmp_path):
    svc = service(tmp_path)
    contact_ready(svc, "EMPTY")
    empty = register(svc, "EMPTY", "Ana Torres", "ana.torres@pruebas.test")
    assert empty["ok"] is True and empty["summary"]["full_flow"]["qa_identity"]["phone"] is None

    names = ["Mario Silva", "Lucía Fuentes", "Tomás Rojas"]
    for index, fixture in enumerate(PHONE_CASES):
        sid = f"PHONE-{index}"
        contact_ready(svc, sid)
        out = register(svc, sid, names[index], f"contacto{index}@dominio.test", fixture)
        phone = out["summary"]["full_flow"]["qa_identity"]["phone"]
        assert out["ok"] is True
        assert phone["international_number"] == fixture["calling_code"] + fixture["national_number"]


def test_invalid_email_format_then_any_valid_domain_is_recoverable(tmp_path):
    svc = service(tmp_path, "email")
    contact_ready(svc, "EMAIL")
    bad_format = register(svc, "EMAIL", "Ana Torres", "correo-invalido")
    assert bad_format["event"] == "EMAIL_FORMAT_INVALID"
    assert bad_format["summary"]["full_flow"]["state"] == "S2"
    accepted = register(svc, "EMAIL", "Ana Torres", "ana@correo.cl")
    assert accepted["ok"] is True and accepted["summary"]["full_flow"]["state"] == "S5"


def test_partial_phone_then_clear_recovers_without_new_conversation(tmp_path):
    svc = service(tmp_path, "partial")
    contact_ready(svc, "PARTIAL")
    blocked = svc.complete_registration(
        "PARTIAL", "Laura Méndez", "laura@example.com",
        country_code="CL", country_name="Chile",
        phone_country_code="US", phone_country_name="Estados Unidos", phone_calling_code="+1",
    )
    assert blocked["ok"] is False and blocked["summary"]["full_flow"]["state"] == "S2"
    cleared = register(svc, "PARTIAL", "Laura Méndez", "laura@example.com")
    assert cleared["ok"] is True and cleared["summary"]["full_flow"]["qa_identity"]["phone"] is None


def test_fastapi_422_is_structured_and_same_session_can_retry():
    with TestClient(app) as client:
        client.post("/api/chat", json={"message": FIXTURE_INITIAL})
        client.post("/api/chat", json={"message": FIXTURE_REPLY})
        client.post("/api/chat", json={"message": "No, eso es todo."})
        client.post("/api/full-flow/proposal/action", json={"action": "continue"})
        malformed = client.post("/api/full-flow/registration", json={"name": "Ana Torres", "email": "ana@example.com", "country_code": "", "country_name": ""})
        assert malformed.status_code == 422 and isinstance(malformed.json()["detail"], list)
        assert client.get("/api/session").json()["full_flow"]["state"] == "S2"
        valid = client.post("/api/full-flow/registration", json={"name": "Ana Torres", "email": "ana@example.com", "country_code": "CL", "country_name": "Chile"})
        assert valid.status_code == 200 and valid.json()["summary"]["full_flow"]["state"] == "S5"


def test_frontend_contract_preserves_form_and_never_stringifies_structured_errors():
    for required in (
        "Nombre completo", "Escribe tu nombre completo", "contact-form-grid",
        "detailFields", "preserveForm:true", "aria-autocomplete=\"list\"",
        "ArrowDown", "ArrowUp", "Utiliza únicamente datos ficticios",
    ):
        assert required in APP
    assert "new Error(body.message||body.detail" not in APP
    assert "[object Object]" not in APP
    assert "qaPhoneSamples" not in APP
    assert "EMAIL_QA_DOMAIN_REQUIRED" not in APP
    assert "flagEmoji" not in APP
    assert "aria-label=\"${escapeHtml(x.name)}, ${escapeHtml(x.code)} ${escapeHtml(x.calling_code)}\"" in APP
    assert ".contact-form-grid{align-items:start}" in STYLES
