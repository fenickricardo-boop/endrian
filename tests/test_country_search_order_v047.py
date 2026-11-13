from pathlib import Path
from dataclasses import replace

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY
from app.service import GuideService
from app.session_repository import SessionRepository

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

def service(tmp_path):
    cfg = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / "v047.db"), cookie_secure=False)
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))

def pending(svc, sid):
    svc.chat(sid, FIXTURE_INITIAL); svc.chat(sid, FIXTURE_REPLY); svc.chat(sid, "No, eso es todo.")
    svc.proposal_action(sid, "continue")
    svc.complete_registration(sid, "Persona Sintética", "persona@correo.test", country_code="CL", country_name="Chile")
    svc.complete_contracting(sid, {"contract_terms_accepted": True, "privacy_authorization_accepted": True})
    out = svc.create_or_reuse_payment_attempt(sid); svc.payment_return(sid)
    return out["summary"]["full_flow"]["payment_qa"]["reference"]

def test_country_search_normalizes_case_accents_and_requires_confirmation():
    assert "function normalizedSearch(value)" in APP
    assert ".normalize('NFD')" in APP
    assert "normalizedSearch(`${b.dataset.name} ${b.dataset.code} ${b.dataset.callingCode}`).includes(q)" in APP
    assert "if(e.key==='Enter'&&!list.hidden)" in APP
    assert "choose(first)" in APP
    assert "input.addEventListener('input',filter)" in APP

def test_confirmed_order_card_is_snapshot_driven_and_complete(tmp_path):
    svc = service(tmp_path); ref = pending(svc, "ORDER-V047")
    before = svc.summary("ORDER-V047")["full_flow"]
    assert before["state"] == "S6" and before["order_qa"] is None
    first = svc.qa_payment_resolve("ORDER-V047", ref, "confirmed")["summary"]["full_flow"]
    order = first["order_qa"]; snapshot = order["construction_request_snapshot"]
    assert first["state"] == "S7" and order["status"] == "RECIBIDA"
    assert snapshot["payment_status"] == "CONFIRMADO" and snapshot["immutable"] is True
    assert snapshot["conversation_evidence_included"] is False
    assert snapshot["amount"] == 89 and snapshot["currency"] == "USD"
    assert "<h2>Pago confirmado</h2>" in APP
    assert "Tu pedido fue recibido correctamente." in APP
    assert "Pago de prueba, sin cobro real" in APP
    assert "ENDRIAN preparará, comprobará y entregará tu solución" in APP
    repeated = svc.qa_payment_resolve("ORDER-V047", ref, "confirmed")
    assert repeated["ok"] is False
    replay = svc.order_replay("ORDER-V047")
    assert replay["same_order"] is True and replay["order"]["order_id"] == order["order_id"]
    recovered = svc.summary("ORDER-V047")["full_flow"]
    assert recovered["order_qa"]["order_id"] == order["order_id"]
    assert recovered["email_preview"]["sent"] is False
