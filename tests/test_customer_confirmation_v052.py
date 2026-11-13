from io import BytesIO

from pypdf import PdfReader

from app.customer_confirmation import build_confirmation, render_email_html, render_contract_pdf, TERMS_PENDING_NOTICE


def archived_order():
    return {
        "snapshot_sha256":"a"*64,
        "order":{
            "order_id":"END-20261013-0001","created_at":"2026-10-13T12:00:00+00:00",
            "construction_request_snapshot":{
                "solution_title":"Agente Profesional para gestión de atención por correo",
                "commitments":["Clasificar consultas.","Preparar borradores para revisión humana."],
                "controls":["Revisión del equipo antes del envío."],"exclusions":["Envío autónomo."],
                "dependencies":[],"platform_label":"Entorno de prueba de ENDRIAN",
                "delivery_label":"Acceso administrado en el entorno de prueba","amount":20,"currency":"USD",
                "delivery_window":"2 a 5 días hábiles desde la confirmación del pago.",
                "terms_version":"QA-TERMS-0.1","privacy_notice_version":"QA-PRIVACY-0.1",
                "contact":{"name":"Alex Prueba","email":"alex@correo.test"},"conversation_evidence_included":False,
                "immutable":True,"particular_conditions":[]
            }
        }
    }


def test_confirmation_is_private_unsent_and_one_test_attachment():
    data=build_confirmation(archived_order())
    assert data["sent"] is False and data["provider"] is None
    assert data["subject"]=="Pedido confirmado · Orden END-20261013-0001"
    assert data["attachment"]["count"]==1
    html=render_email_html(data)
    assert "copia de contratación de prueba" in html
    assert "contenido legal pendiente" in html.lower()
    assert "transcript" not in html.lower()
    assert "Condiciones particulares" not in html


def test_pdf_contains_only_provisional_terms_notice_and_no_complete_claim():
    data=build_confirmation(archived_order()); payload=render_contract_pdf(data)
    assert payload.startswith(b"%PDF-")
    text="\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(payload)).pages)
    assert "QA-TERMS-0.1" in text
    assert " ".join(TERMS_PENDING_NOTICE.split()) in " ".join(text.split())
    assert "Términos y Condiciones completos" not in text
    assert "transcript" not in text.lower()


def test_existing_snapshot_is_not_mutated():
    source=archived_order(); before=repr(source)
    build_confirmation(source)
    assert repr(source)==before


def test_public_postpayment_card_has_no_email_preview():
    app_js=open("frontend/app.js",encoding="utf-8").read()
    assert "Vista previa del correo · No enviado" not in app_js
