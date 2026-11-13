from copy import deepcopy
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.customer_confirmation import (
    TEMPLATE_VERSION,
    build_confirmation,
    build_internal_view,
    render_contract_pdf,
    render_internal_html,
)


ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")


def archived_order():
    return {
        "snapshot_sha256": "f" * 64,
        "order": {
            "order_id": "END-20261028-0099",
            "created_at": "2026-10-28T12:00:00+00:00",
            "quotation_version": 1,
            "construction_request_snapshot": {
                "snapshot_version": 3,
                "solution_title": "Solución para gestión de atención por correo",
                "service_label": "ENDRIAN Especializado",
                "need_confirmed": "Organizar la atención por correo.",
                "objective": "Mantener continuidad.",
                "context": "Equipo de cuatro personas.",
                "scope": "ENDRIAN preparará una configuración para clasificar, priorizar y organizar el seguimiento. No enviará respuestas ni se conectará a cuentas de correo.",
                "deliverables": [
                    "Configuración especializada con instrucciones y criterios acordados.",
                    "Estructura para clasificar, priorizar y registrar el seguimiento.",
                    "Guía breve para comenzar a utilizar la configuración.",
                ],
                "information_input": "Tu equipo incorporará los datos de cada caso en el entorno acordado. Esta prueba no conecta cuentas reales.",
                "materials_needed": ["Criterios de prioridad."],
                "commitments": [{"item_id": "PRO-CAP-002", "label": "Preparar borradores de respuesta."}],
                "controls": [{"item_id": "PRO-CTL-001", "label": "El equipo revisa los borradores antes de enviarlos."}],
                "exclusions": [{"item_id": "PRO-EXC-002", "label": "Sin envío autónomo."}],
                "dependencies": ["Datos incorporados manualmente."],
                "platform_label": "Entorno simulado de ENDRIAN",
                "delivery_label": "Configuración preparada para el entorno acordado",
                "amount": 89,
                "currency": "USD",
                "payment_status": "CONFIRMADO",
                "delivery_window": "2 a 5 días hábiles desde la confirmación del pago",
                "particular_conditions": [],
                "terms_version": "QA-TERMS-0.1",
                "privacy_notice_version": "QA-PRIVACY-0.1",
                "contact": {
                    "name": "Ana Sintética",
                    "email": "ana@example.net",
                    "phone": None,
                    "billing_country": {"country_code": "CL", "country_name": "Chile"},
                },
                "conversation_evidence_included": False,
                "immutable": True,
            },
        },
    }


def pdf_text(payload):
    return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(payload)).pages)


def test_public_summary_and_prepayment_use_compact_projection():
    state5 = APP.split("} else if(state==='S5')", 1)[1].split("} else if(state==='S6')", 1)[0]
    for visible in ("Resumen de tu solicitud", "Servicio recomendado", "Qué incluye", "Plataforma de uso", "Precio", "Plazo estimado de entrega"):
        assert visible in state5
    for removed in ("Necesidad comprendida", "Por qué encaja", "Alcance concreto", "Materiales o información necesarios", "Límites relevantes"):
        assert removed not in state5
    assert "La solución prepara borradores; tu equipo los revisa y realiza el envío." in state5
    assert "Datos del cliente" in state5 and "contractTermsAccepted" in state5 and "privacyAccepted" in state5


def test_payment_simulation_is_transition_only():
    state6 = APP.split("} else if(state==='S6')", 1)[1].split("} else if(state==='S7')", 1)[0]
    simulation = state6.split("<h2>Simulación de pago</h2>", 1)[1]
    assert "<strong>Servicio</strong>" in simulation
    assert "<strong>Importe</strong>" in simulation
    assert "Volver al Laboratorio" in simulation
    assert "<strong>Solución</strong>" not in simulation
    assert "<strong>Plataforma</strong>" not in simulation
    assert "<strong>Plazo</strong>" not in simulation


def test_compact_pdf_preserves_internal_detail_and_historical_snapshot():
    source = archived_order()
    before = deepcopy(source)
    public = build_confirmation(source)
    text = pdf_text(render_contract_pdf(public))
    assert public["template_version"] == TEMPLATE_VERSION == "ENDRIAN-POST-CONFIRMACION-1.1-QA"
    assert "Qué incluye tu pedido" in text
    assert text.count("La solución prepara borradores; tu equipo los revisa y realiza el envío.") == 1
    assert "No existe constancia de recepción" not in text
    assert "Criterios de prioridad." not in text
    assert "Snapshot" not in text and "Plantilla ENDRIAN" not in text
    internal_html = render_internal_html(build_internal_view(source))
    assert "Criterios de prioridad." in internal_html
    assert "Snapshot" in internal_html
    assert "Restricciones, exclusiones y dependencias" in internal_html
    assert source == before
