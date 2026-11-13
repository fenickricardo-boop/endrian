from dataclasses import replace
from pathlib import Path

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY, QA_CONDITIONS
from app.service import GuideService
from app.session_repository import SessionRepository


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")


def service(tmp_path):
    cfg = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / "v045.db"), cookie_secure=False)
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))


def pending_payment(svc, sid):
    svc.chat(sid, FIXTURE_INITIAL)
    svc.chat(sid, FIXTURE_REPLY)
    svc.chat(sid, "No, eso es todo.")
    svc.proposal_action(sid, "continue")
    svc.complete_registration(
        sid, "Alex Prueba", "alex@laboratorio.test",
        country_code="CL", country_name="Chile",
        phone_country_code="AR", phone_country_name="Argentina",
        phone_calling_code="+54", phone_national_number="1123456799",
    )
    svc.complete_contracting(sid, {"contract_terms_accepted": True, "privacy_authorization_accepted": True})
    started = svc.create_or_reuse_payment_attempt(sid)
    svc.payment_return(sid)
    return started["summary"]["full_flow"]["payment_qa"]["reference"]


def test_visual_copy_and_alignment_contract():
    assert "<strong>Nombre completo</strong>" in APP
    assert "Conservamos tu solicitud. No necesitas intentar pagar nuevamente." in APP
    assert "esperamos la confirmación del backend" not in APP
    assert ".phone-field{color:#bad1dc;font-size:12px;line-height:1.5}" in STYLES
    assert ".phone-controls .country-picker-input{height:38px" in STYLES
    assert ".phone-controls .country-picker-list button{font-size:12px}" in STYLES


def test_updated_external_service_condition_is_exact_and_versioned():
    expected = "El precio no incluye suscripciones, licencias ni consumo de servicios externos. Si tu agente los necesita, te indicaremos cuáles y sus costos antes del pago."
    assert expected in QA_CONDITIONS
    assert "Las dependencias y los servicios externos se informan por separado." not in QA_CONDITIONS


def test_private_confirmation_creates_one_order_and_email_preview(tmp_path):
    svc = service(tmp_path)
    reference = pending_payment(svc, "PAYMENT")
    before = svc.summary("PAYMENT")["full_flow"]
    assert before["state"] == "S6" and before["order_qa"] is None

    confirmed = svc.qa_payment_resolve("PAYMENT", reference, "confirmed")
    flow = confirmed["summary"]["full_flow"]
    order_id = flow["order_qa"]["order_id"]
    assert flow["state"] == "S7" and flow["order_qa"]["status"] == "RECIBIDA"
    assert "<strong>Estado</strong><span>Pedido recibido</span>" in APP
    assert "<h2>Pago confirmado</h2>" in APP
    assert flow["email_preview"]["sent"] is False
    assert flow["order_qa"]["construction_request_snapshot"]["contact"]["name"] == "Alex Prueba"

    repeated = svc.qa_payment_resolve("PAYMENT", reference, "confirmed")
    after = repeated["summary"]["full_flow"]
    assert repeated["ok"] is False and after["order_qa"]["order_id"] == order_id
    replay = svc.order_replay("PAYMENT")
    assert replay["same_order"] is True and replay["summary"]["full_flow"]["order_qa"]["order_id"] == order_id
