from dataclasses import replace
from pathlib import Path

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY
from app.service import GuideService
from app.session_repository import SessionRepository


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")


def service(tmp_path, name):
    cfg = replace(
        base_settings,
        model_mode="deterministic",
        db_path=str(tmp_path / f"{name}.db"),
        cookie_secure=False,
    )
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))


def contact_ready(svc, sid):
    svc.chat(sid, FIXTURE_INITIAL)
    svc.chat(sid, FIXTURE_REPLY)
    svc.chat(sid, "No, eso es todo.")
    svc.proposal_action(sid, "continue")


def test_two_distinct_synthetic_contacts_without_exact_fixture_dependency(tmp_path):
    first = service(tmp_path, "first")
    contact_ready(first, "NO-PHONE")
    out = first.complete_registration(
        "NO-PHONE", "Ana Torres", "ana.torres@example.net",
        country_code="ES", country_name="España",
    )
    identity = out["summary"]["full_flow"]["qa_identity"]
    assert out["ok"] is True
    assert identity["name"] == "Ana Torres"
    assert identity["email"] == "ana.torres@example.net"
    assert identity["phone"] is None

    second = service(tmp_path, "second")
    contact_ready(second, "WITH-PHONE")
    out = second.complete_registration(
        "WITH-PHONE", "Mario Silva", "mario.silva@example.org",
        country_code="UY", country_name="Uruguay",
        phone_country_code="US", phone_country_name="Estados Unidos",
        phone_calling_code="+1", phone_national_number="2025550147",
    )
    identity = out["summary"]["full_flow"]["qa_identity"]
    assert out["ok"] is True
    assert identity["phone"]["international_number"] == "+12025550147"


def test_partial_phone_blocks_then_clearing_both_controls_allows_progress(tmp_path):
    svc = service(tmp_path, "partial")
    contact_ready(svc, "PARTIAL")
    blocked = svc.complete_registration(
        "PARTIAL", "Laura Méndez", "laura.mendez@example.com",
        country_code="MX", country_name="México",
        phone_country_code="US", phone_country_name="Estados Unidos",
        phone_calling_code="+1", phone_national_number="",
    )
    assert blocked["ok"] is False
    assert blocked["event"] == "PHONE_NUMBER_INVALID"
    assert blocked["summary"]["full_flow"]["state"] == "S2"

    cleared = svc.complete_registration(
        "PARTIAL", "Laura Méndez", "laura.mendez@example.com",
        country_code="MX", country_name="México",
    )
    assert cleared["ok"] is True
    assert cleared["summary"]["full_flow"]["qa_identity"]["phone"] is None


def test_public_cards_contract_has_empty_fields_grouped_phone_and_platform():
    for required in (
        'placeholder="Escribe tu nombre completo"',
        'placeholder="Escribe tu correo"',
        "Teléfono (opcional)",
        "Número de teléfono",
        "Completa el prefijo y el número, o borra ambos para omitir el teléfono.",
        "Plataforma de uso",
        "Plataforma de uso",
    ):
        assert required in APP
    assert "[object Object]" not in APP
    assert 'value="Juan Pérez"' not in APP
    assert 'value="juan.perez@example.com"' not in APP
    assert APP.count("<details>") >= 3
