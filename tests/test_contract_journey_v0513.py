from dataclasses import replace
import json
from pathlib import Path

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY, SPECIAL_FIXTURE_INITIAL
from app.service import GuideService
from app.session_repository import SessionRepository


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")


def service(tmp_path, name="v0513"):
    cfg = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / f"{name}.db"), cookie_secure=False)
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))


def summary_ready(svc, sid):
    first = svc.chat(sid, FIXTURE_INITIAL)
    assert first["event"] == "FIXTURE_MATERIAL_QUESTION"
    ready = svc.chat(sid, FIXTURE_REPLY)
    assert ready["event"] == "FIXTURE_DEFINITION_READY"
    return svc.confirmation_action(sid, "confirm")


def pending_payment(svc, sid):
    summary_ready(svc, sid)
    svc.proposal_action(sid, "continue")
    contact = svc.complete_registration(
        sid,
        "Alex Prueba",
        "alex.prueba@example.net",
        country_code="CL",
        country_name="Chile",
    )
    assert contact["event"] == "PREPAYMENT_DATA_READY"
    accepted = svc.complete_contracting(
        sid,
        {"contract_terms_accepted": True, "privacy_authorization_accepted": True},
    )
    assert accepted["summary"]["payment_gate"]["payment_enabled"] is True
    return svc.payment_start(sid)


def test_standard_journey_is_catalog_consistent_and_snapshot_driven(tmp_path):
    svc = service(tmp_path)
    summary = summary_ready(svc, "STANDARD")["summary"]["full_flow"]
    request = summary["solution_request_versions"][-1]
    quote = summary["quotations"][-1]
    public = summary["client_output"]
    assert summary["state"] == "S5"
    assert request["validated_agent"] == "especializado"
    assert request["service_label"] == "ENDRIAN Especializado"
    assert request["route"] == "STANDARD"
    assert quote["amount"] == 89 and quote["currency"] == "USD"
    assert public["service"] == "ENDRIAN Especializado"
    assert public["scope"] and public["deliverables"] and public["information_input"]
    assert public["materials_needed"] and public["limits"]

    started = pending_payment(svc, "PAID")
    payment = started["summary"]["full_flow"]["payment_qa"]
    assert payment["service_label"] == "ENDRIAN Especializado" and payment["amount"] == 89
    confirmed = svc.qa_payment_resolve("PAID", payment["reference"], "confirmed")
    flow = confirmed["summary"]["full_flow"]
    order = flow["order_qa"]
    snapshot = order["construction_request_snapshot"]
    assert flow["state"] == "S7" and order["status"] == "RECIBIDA"
    assert snapshot["solution_title"] == "Solución para gestión de atención por correo"
    assert snapshot["service_label"] == "ENDRIAN Especializado"
    assert snapshot["amount"] == 89 and snapshot["currency"] == "USD"
    assert snapshot["platform_label"] and snapshot["delivery_window"]
    encoded = json.dumps(snapshot, ensure_ascii=False).lower()
    assert "transcript" not in encoded and FIXTURE_INITIAL.lower() not in encoded
    replay = svc.order_replay("PAID")
    assert replay["same_order"] is True and replay["order"]["order_id"] == order["order_id"]


def test_special_journey_has_review_without_automatic_price_or_payment(tmp_path):
    svc = service(tmp_path, "special")
    ready = svc.chat("SPECIAL", SPECIAL_FIXTURE_INITIAL)
    assert ready["summary"]["full_flow"]["state"] == "S4"
    summary = svc.confirmation_action("SPECIAL", "confirm")["summary"]["full_flow"]
    assert summary["state"] == "S5"
    assert summary["solution_request_versions"][-1]["route"] == "SPECIAL_REVIEW"
    assert summary["quotations"] == []
    assert summary["payment_qa"]["status"] == "NO_INICIADO"


def test_unsupported_deterministic_input_does_not_fake_understanding_or_loop(tmp_path):
    svc = service(tmp_path, "fallback")
    out = svc.chat("FALLBACK", "Necesito preparar propuestas de trabajo con mis propios criterios")
    assert out["event"] == "DETERMINISTIC_SCRIPT_REQUIRED"
    assert out["summary"]["full_flow"]["state"] == "S1"
    assert out["summary"]["full_flow"]["orientation_summary"] is None
    assert out["summary"]["full_flow"]["client_output"] is None
    assert "no generó una comprensión ni un resumen" in out["message"]
    repeated = svc.chat("FALLBACK", "Muéstrame el resumen")
    assert repeated["event"] == "DETERMINISTIC_SCRIPT_REQUIRED"
    assert repeated["summary"]["full_flow"]["orientation_summary"] is None


def test_visible_contract_contains_authorized_controls_and_no_old_active_offer():
    for text in (
        "Definición de tu solicitud",
        "Revisión y pago",
        "¿Esto refleja bien lo que necesitas o quieres cambiar algo?",
        "Sí, preparar mi resumen",
        "Servicio recomendado",
        "Qué incluye",
        "Volver a la conversación",
        "Esta verificación es simulada y no valida un pago real.",
        "Finalizar conversación",
    ):
        assert text in APP
    for removed in (
        "Necesidad comprendida",
        "Por qué encaja",
        "Alcance concreto",
        "Materiales o información necesarios",
        "Límites relevantes",
    ):
        assert removed not in APP
    assert "USD 20" not in APP
    assert "Agente Profesional" not in APP

