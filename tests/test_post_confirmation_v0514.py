from copy import deepcopy
from dataclasses import replace
from io import BytesIO
import json

from pypdf import PdfReader

from app.config import settings as base_settings
from app.customer_confirmation import (
    TEMPLATE_VERSION,
    build_confirmation,
    build_internal_notice,
    build_internal_view,
    render_contract_pdf,
    render_email_html,
    render_internal_html,
    render_internal_notice_html,
)
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY
from app.service import GuideService
from app.session_repository import SessionRepository


def service(tmp_path):
    cfg = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / "v0514.db"), cookie_secure=False)
    return GuideService(cfg, SessionRepository(cfg.db_path, ttl_seconds=3600))


def archived_new_order(tmp_path):
    svc = service(tmp_path)
    sid = "POST-CONFIRMATION-V0514"
    svc.chat(sid, FIXTURE_INITIAL)
    svc.chat(sid, FIXTURE_REPLY)
    svc.confirmation_action(sid, "confirm")
    svc.proposal_action(sid, "continue")
    svc.complete_registration(sid, "Ana Sintética", "ana.sintetica@example.net", country_code="CL", country_name="Chile")
    svc.complete_contracting(sid, {"contract_terms_accepted": True, "privacy_authorization_accepted": True})
    started = svc.payment_start(sid)
    reference = started["summary"]["full_flow"]["payment_qa"]["reference"]
    flow = svc.qa_payment_resolve(sid, reference, "confirmed")["summary"]["full_flow"]
    order_id = flow["order_qa"]["order_id"]
    return svc, sid, order_id, svc.archived_order(order_id)


def pdf_text(payload):
    return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(payload)).pages)


def test_three_representations_are_snapshot_derived_and_do_not_mutate_archive(tmp_path):
    svc, _, order_id, archived = archived_new_order(tmp_path)
    before = deepcopy(archived)
    confirmation = build_confirmation(archived)
    internal = build_internal_view(archived)
    notice = build_internal_notice(confirmation)
    assert archived == before
    assert confirmation["template_version"] == TEMPLATE_VERSION
    assert confirmation["order_id"] == internal["order_id"] == notice["order_id"] == order_id
    assert confirmation["snapshot_sha256"] == internal["snapshot_sha256"]
    assert confirmation["solution_title"] == "Solución para gestión de atención por correo"
    assert confirmation["service"] == "ENDRIAN Especializado"
    assert confirmation["amount"] == 89 and confirmation["currency"] == "USD"
    assert svc.archived_order(order_id) == before


def test_customer_email_is_concise_unsent_and_has_no_internal_or_legacy_terms(tmp_path):
    _, _, _, archived = archived_new_order(tmp_path)
    data = build_confirmation(archived)
    html = render_email_html(data)
    assert data["sent"] is False and data["provider"] is None
    assert data["subject"].startswith("Pedido confirmado · Orden END-")
    assert "copia de contratación de prueba" in html
    assert "Corrección ficticia" not in html and "7 días" not in html
    assert "item_id" not in html and "transcript" not in html.lower()
    assert "Características contratadas" not in html


def test_pdf_contains_compact_customer_detail_without_operational_material_status(tmp_path):
    _, _, _, archived = archived_new_order(tmp_path)
    data = build_confirmation(archived)
    text = pdf_text(render_contract_pdf(data))
    for expected in (
        "Detalle y condiciones de tu pedido",
        "Solución para gestión de atención por correo",
        "ENDRIAN Especializado",
        "Qué incluye tu pedido",
        "Plataforma y modalidad de entrega",
        "Condiciones específicas acordadas",
        "USD 89",
        "QA-TERMS-0.1",
    ):
        assert expected in text
    for removed in (
        "Necesidad y objetivo confirmados",
        "Alcance acordado",
        "Materiales e información",
        "No existe constancia de recepción",
        "Sin confirmar",
        "Snapshot",
        "Plantilla ENDRIAN",
    ):
        assert removed not in text
    assert "Corrección ficticia" not in text and "7 días naturales" not in text
    assert "transcript" not in text.lower() and "item_id" not in text


def test_internal_view_and_notice_are_private_honest_and_unsent(tmp_path):
    _, _, _, archived = archived_new_order(tmp_path)
    internal = build_internal_view(archived)
    internal_html = render_internal_html(internal)
    notice = build_internal_notice(internal)
    notice_html = render_internal_notice_html(notice)
    assert "Ficha interna de preparación" in internal_html
    assert "Pendiente interno: no existen criterios de comprobación" in internal_html
    assert "Sin asignar" in internal_html and "Sin confirmar" in internal_html
    assert internal["snapshot_sha256"] in internal_html
    assert notice["sent"] is False and notice["provider"] is None
    assert "NO ENVIADO" in notice_html and "DESTINATARIO INTERNO PENDIENTE" in notice_html
    assert f'/qa-control/orders/{internal["order_id"]}/internal' in notice_html


def test_new_archived_preview_matches_canonical_subject_without_duplicate_window(tmp_path):
    _, _, _, archived = archived_new_order(tmp_path)
    preview = archived["email_preview"]
    assert preview["subject"].startswith("Pedido confirmado · Orden END-")
    assert preview["template_version"] == TEMPLATE_VERSION
    assert preview["sent"] is False and preview["provider"] is None
    assert preview["body"].count("2 a 5 días hábiles desde la confirmación del pago") == 1
    assert preview["platform_label"] == "Entorno simulado de ENDRIAN"
    assert "Corrección ficticia" not in json.dumps(archived["order"], ensure_ascii=False)


def test_snapshot_has_no_transcript_and_idempotent_replay_preserves_hash(tmp_path):
    svc, sid, order_id, archived = archived_new_order(tmp_path)
    snapshot = archived["order"]["construction_request_snapshot"]
    assert snapshot["snapshot_version"] == 3 and snapshot["immutable"] is True
    assert snapshot["conversation_evidence_included"] is False
    assert "transcript" not in json.dumps(snapshot, ensure_ascii=False).lower()
    replay = svc.order_replay(sid)
    assert replay["same_order"] is True and replay["order"]["order_id"] == order_id
    assert svc.archived_order(order_id)["snapshot_sha256"] == archived["snapshot_sha256"]
