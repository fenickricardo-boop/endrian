from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from io import BytesIO
from pathlib import Path
import re
from typing import Any, Dict, Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

TEMPLATE_VERSION = "ENDRIAN-POST-CONFIRMACION-1.1-QA"
TERMS_REFERENCE = "QA-TERMS-0.1"
TERMS_EXISTING_NOTICE = "Documento QA-TERMS-0.1. No constituye términos legales definitivos."
TERMS_PENDING_NOTICE = "Contenido completo de Términos y Condiciones pendiente. Documento de prueba, no válido para contratación real."
CONTACT_PLACEHOLDER = "[CORREO CORPORATIVO PENDIENTE - QA]"
INTERNAL_RECIPIENT_PLACEHOLDER = "[DESTINATARIO INTERNO PENDIENTE - QA]"
PRIVACY_PLACEHOLDER = "[ENLACE PROVISIONAL QA-PRIVACY-0.1 - NO OPERATIVO]"
FONT_ROOT = Path(__file__).resolve().parent.parent / "assets" / "fonts"
pdfmetrics.registerFont(TTFont("EndrianSans", str(FONT_ROOT / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("EndrianSansBold", str(FONT_ROOT / "DejaVuSans-Bold.ttf")))


def _fmt_date(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%d-%m-%Y %H:%M UTC")
    except Exception:
        return value or "No disponible"


def _public_text(item: Any, field: str) -> str:
    if isinstance(item, str) and item.strip():
        return item.strip()
    if isinstance(item, dict):
        label = item.get("label")
        if isinstance(label, str) and label.strip():
            return label.strip()
    raise ValueError(f"{field}: falta texto público válido en el snapshot archivado")


def _customer_wording(value: str) -> str:
    replacements = {
        "Revisión humana antes de cualquier envío.": "El equipo revisa los borradores antes de enviarlos.",
        "Preparar borradores de respuesta para revisión humana antes del envío.": "Preparar borradores de respuesta para que el equipo los revise antes del envío.",
        "Revisión humana antes del envío": "Revisión del equipo antes del envío",
    }
    return replacements.get(value, value)


def _public_list(value: Any, field: str) -> list[str]:
    if value in (None, []):
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field}: formato no válido en el snapshot archivado")
    return [_customer_wording(_public_text(item, field)) for item in value]


def _split_delivery_window(value: Any) -> tuple[str, str | None]:
    text = str(value or "").strip()
    marker = " desde "
    if marker in text.casefold():
        index = text.casefold().index(marker)
        return text[:index].strip().rstrip("."), text[index + len(marker):].strip().rstrip(".")
    return text or "No registrado", None


def _material_rows(snapshot: Dict[str, Any]) -> list[Dict[str, str]]:
    needed = _public_list(snapshot.get("materials_needed"), "Materiales")
    recorded = snapshot.get("materials_status") if isinstance(snapshot.get("materials_status"), list) else []
    by_label = {
        str(item.get("label")).strip().casefold(): item
        for item in recorded
        if isinstance(item, dict) and isinstance(item.get("label"), str)
    }
    rows = []
    for label in needed:
        source = by_label.get(label.casefold())
        if not source:
            rows.append({"material": label, "state": "Sin confirmar", "note": "No existe constancia de recepción en la orden."})
            continue
        state = str(source.get("status") or "").strip().upper()
        public_state = {"RECEIVED": "Recibido", "PENDING": "Pendiente confirmado"}.get(state, "Sin confirmar")
        rows.append({"material": label, "state": public_state, "note": str(source.get("note") or "").strip() or "Sin observación registrada."})
    return rows


def _accepted_at(snapshot: Dict[str, Any]) -> str:
    terms = ((snapshot.get("acceptances") or {}).get("contract_terms") or {})
    return _fmt_date(str(terms.get("accepted_at") or ""))


def build_confirmation(archived: Dict[str, Any]) -> Dict[str, Any]:
    order = archived.get("order") or {}
    snap = order.get("construction_request_snapshot") or {}
    contact = snap.get("contact") or {}
    required = {"order_id": order.get("order_id"), "solution_title": snap.get("solution_title"), "email": contact.get("email")}
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ValueError("Snapshot de orden incompleto: " + ", ".join(missing))
    conditions = snap.get("particular_conditions") if "particular_conditions" in snap else None
    duration, start_condition = _split_delivery_window(snap.get("delivery_window"))
    phone = contact.get("phone") if isinstance(contact.get("phone"), dict) else {}
    billing = contact.get("billing_country") if isinstance(contact.get("billing_country"), dict) else {}
    data = {
        "template_version": TEMPLATE_VERSION,
        "sent": False,
        "provider": None,
        "order_id": order["order_id"],
        "order_status": "Pedido recibido",
        "to": contact["email"],
        "subject": f'Pedido confirmado · Orden {order["order_id"]}',
        "confirmed_at": order.get("created_at") or "",
        "customer_name": contact.get("name") or "cliente",
        "customer_email": contact.get("email") or "No registrado",
        "customer_phone": phone.get("international_number") or "No registrado",
        "billing_country": billing.get("country_name") or "No registrado",
        "solution_title": snap["solution_title"],
        "service": snap.get("service_label") or snap.get("agent") or "No registrado",
        "need_confirmed": snap.get("need_confirmed") or "No registrado",
        "objective": snap.get("objective") or "No registrado",
        "context": snap.get("context") or "No registrado",
        "why_fit": snap.get("why_fit") or "No registrado",
        "scope": snap.get("scope") or "No registrado",
        "deliverables": _public_list(snap.get("deliverables"), "Entregables"),
        "characteristics": _public_list(snap.get("commitments"), "Características"),
        "controls": _public_list(snap.get("controls"), "Controles"),
        "platform": snap.get("platform_label") or snap.get("environment_id") or "No registrado",
        "platform_notice": snap.get("platform_notice") or "",
        "information_input": snap.get("information_input") or "No registrado",
        "delivery": snap.get("delivery_label") or snap.get("delivery_mode") or "No registrado",
        "delivery_notice": snap.get("delivery_notice") or "",
        "dependencies": _public_list(snap.get("dependencies"), "Dependencias"),
        "exclusions": _public_list(snap.get("exclusions"), "Exclusiones"),
        "materials": _material_rows(snap),
        "verification_criteria": _public_list(snap.get("verification_criteria"), "Criterios de comprobación"),
        "amount": snap.get("amount"),
        "currency": snap.get("currency"),
        "payment_status": snap.get("payment_status") or "No registrado",
        "payment_reference": snap.get("payment_reference") or "No registrada",
        "delivery_window": snap.get("delivery_window") or "No registrado",
        "delivery_duration": duration,
        "delivery_start_condition": start_condition,
        "particular_conditions": None if conditions is None else _public_list(conditions, "Condiciones particulares"),
        "terms_version": snap.get("terms_version") or TERMS_REFERENCE,
        "privacy_version": snap.get("privacy_notice_version") or "QA-PRIVACY-0.1",
        "conditions_version": snap.get("conditions_version") or "No registrada",
        "accepted_at": _accepted_at(snap),
        "snapshot_version": snap.get("snapshot_version"),
        "snapshot_sha256": archived.get("snapshot_sha256"),
        "scope_version_id": snap.get("scope_version_id"),
        "solution_request_version_id": snap.get("solution_request_version_id"),
        "quotation_ref": snap.get("quotation_ref"),
        "quotation_version": order.get("quotation_version"),
        "conversation_evidence_included": bool(snap.get("conversation_evidence_included")),
        "contact_channel": CONTACT_PLACEHOLDER,
        "privacy_link": PRIVACY_PLACEHOLDER,
        "next_step": order.get("next_step") or "REVISIÓN INTERNA",
    }
    data["attachment"] = {"filename": f'Copia_de_contratacion_{order["order_id"]}.pdf', "kind": "copia de contratación de prueba", "legal_content": "pendiente", "count": 1}
    return data


def _amount(d: Dict[str, Any]) -> str:
    return f'{d.get("currency") or ""} {d.get("amount") if d.get("amount") is not None else ""}'.strip() or "No registrado"


def render_email_html(d: Dict[str, Any]) -> str:
    pdf = f'/api/qa-control/orders/{escape(d["order_id"])}/contract-copy.pdf'
    condition = f' · contado desde {escape(d["delivery_start_condition"])}' if d.get("delivery_start_condition") else ""
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(d["subject"])}</title><link rel="stylesheet" href="/qa-control/confirmation.css"></head><body><main><div class="qa">QA CONTROLADO · VISTA PREVIA · sent=false · {escape(d["template_version"])}</div><section class="meta"><b>Destinatario:</b> {escape(d["to"])}<br><b>Asunto:</b> {escape(d["subject"])}<br><b>Orden:</b> {escape(d["order_id"])}</section><article><header>ENDRIAN</header><h1>Pedido confirmado</h1><p>Hola {escape(d["customer_name"])},</p><p>Confirmamos tu pago de prueba y recibimos tu pedido.</p><dl><dt>Orden</dt><dd>{escape(d["order_id"])}</dd><dt>Solución</dt><dd>{escape(d["solution_title"])}</dd><dt>Servicio contratado</dt><dd>{escape(d["service"])}</dd><dt>Importe</dt><dd>{escape(_amount(d))}</dd><dt>Plazo acordado</dt><dd>{escape(d["delivery_duration"])}{condition}</dd></dl><h2>Siguiente paso</h2><p>ENDRIAN continuará con la preparación y comprobación de la solución según el alcance confirmado.</p><p>Adjuntamos un único PDF con el detalle y las condiciones de tu pedido.</p><aside><b>Adjunto:</b> copia de contratación de prueba. Contenido legal pendiente; este documento no es válido para contratación real.</aside><p>Para consultas, utiliza {escape(d["contact_channel"])} e indica tu número de orden.</p><p><a href="{pdf}">Abrir o descargar el único PDF adjunto</a></p><footer>ENDRIAN · operado por ENDRIAN SpA</footer></article></main></body></html>'''


def _styles():
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "EndrianSans"
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 12.4
    styles["Title"].fontName = styles["Heading1"].fontName = styles["Heading2"].fontName = "EndrianSansBold"
    styles["Heading1"].fontSize = 16
    styles["Heading2"].fontSize = 11.5
    styles["Heading2"].spaceBefore = 7
    styles["Heading2"].spaceAfter = 4
    styles.add(ParagraphStyle(name="Brand", parent=styles["Title"], fontName="EndrianSansBold", textColor=colors.HexColor("#0B6570"), alignment=TA_CENTER, fontSize=15))
    styles.add(ParagraphStyle(name="Warn", parent=styles["BodyText"], textColor=colors.HexColor("#8A1C1C"), borderColor=colors.HexColor("#D9A7A7"), borderWidth=.5, borderPadding=7, leading=14))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.6, leading=10, textColor=colors.HexColor("#52696D")))
    return styles


def _table(rows: Iterable[tuple[str, Any]], styles, widths=(42 * mm, 118 * mm)) -> Table:
    body = [[Paragraph(escape(str(label)), styles["BodyText"]), Paragraph(escape(str(value or "No registrado")), styles["BodyText"])] for label, value in rows]
    table = Table(body, colWidths=list(widths))
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F4F5")), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#91AEB2")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return table


def _list_story(values: list[str], styles) -> list[Any]:
    if not values:
        return [Paragraph("No se registraron elementos.", styles["BodyText"])]
    return [ListFlowable([ListItem(Paragraph(escape(str(value)), styles["BodyText"])) for value in values], bulletType="bullet")]


def _compact_public_conditions(d: Dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    information_input = str(d.get("information_input") or "").strip()
    if information_input and information_input != "No registrado":
        first_sentence = re.split(r"\.\s+(?:Esta prueba|No se)", information_input, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        if first_sentence:
            conditions.append(first_sentence.rstrip(".") + ".")
    review_source = " ".join(d.get("controls") or []) + " " + " ".join(d.get("characteristics") or [])
    if "borrador" in review_source.casefold():
        conditions.append("La solución prepara borradores; tu equipo los revisa y realiza el envío.")
    conditions.extend(d.get("particular_conditions") or [])
    unique: list[str] = []
    seen: set[str] = set()
    for value in conditions:
        key = " ".join(str(value).split()).casefold()
        if key and key not in seen:
            seen.add(key)
            unique.append(str(value).strip())
    return unique


def render_contract_pdf(d: Dict[str, Any]) -> bytes:
    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=14 * mm, bottomMargin=14 * mm, title=d["attachment"]["filename"])
    s = _styles()
    compact_conditions = _compact_public_conditions(d)
    story: list[Any] = [
        Paragraph("ENDRIAN", s["Brand"]),
        Paragraph("Detalle y condiciones de tu pedido", s["Title"]),
        Paragraph(TERMS_PENDING_NOTICE, s["Warn"]),
        Spacer(1, 3 * mm),
        _table([("Número de orden", d["order_id"]), ("Fecha de confirmación", _fmt_date(d["confirmed_at"])), ("Estado", d["order_status"])], s),
        Paragraph("Cliente", s["Heading2"]),
        _table([("Nombre", d["customer_name"]), ("Correo", d["customer_email"]), ("País de facturación", d["billing_country"]), ("Teléfono", d["customer_phone"])], s),
        Paragraph("Solución y servicio contratado", s["Heading2"]),
        _table([("Solución", d["solution_title"]), ("Servicio contratado", d["service"])], s),
        Paragraph("Qué incluye tu pedido", s["Heading2"]),
        Paragraph(escape(d["scope"]), s["BodyText"]),
        *_list_story(d["deliverables"], s),
    ]
    if compact_conditions:
        story += [Paragraph("Condiciones específicas acordadas", s["Heading2"]), *_list_story(compact_conditions, s)]
    story += [
        Paragraph("Plataforma y modalidad de entrega", s["Heading2"]),
        _table([("Plataforma", d["platform"]), ("Modalidad de entrega", d["delivery"])], s),
        Paragraph("Importe, pago y plazo", s["Heading2"]),
        _table([("Importe", _amount(d)), ("Pago", d["payment_status"]), ("Plazo", d["delivery_duration"]), ("Inicio del plazo", d["delivery_start_condition"] or "No registrado por separado")], s),
        Paragraph("Siguiente paso", s["Heading2"]),
        Paragraph("ENDRIAN preparará, comprobará y entregará la solución según lo confirmado en este pedido.", s["BodyText"]),
        Paragraph("Condiciones aceptadas", s["Heading2"]),
        Paragraph(f'<b>Términos y Condiciones:</b> {escape(str(d["terms_version"]))}. {escape(TERMS_EXISTING_NOTICE)}', s["BodyText"]),
        Paragraph(f'<b>Política de Privacidad:</b> {escape(str(d["privacy_version"]))}. Referencia provisional no operativa.', s["BodyText"]),
        Paragraph(f'<b>Aceptación registrada:</b> {escape(d["accepted_at"])}', s["BodyText"]),
        Spacer(1, 4 * mm),
        Paragraph("Este documento de prueba no es boleta, factura ni comprobante emitido por un proveedor de pago.", s["Small"]),
    ]
    doc.build(story)
    return out.getvalue()


def build_internal_view(archived: Dict[str, Any]) -> Dict[str, Any]:
    data = build_confirmation(archived)
    order = archived.get("order") or {}
    data.update({"internal_status": order.get("status") or "No registrado", "internal_owner": "Sin asignar", "internal_blockers": "Sin confirmar: la orden no contiene un campo operativo de bloqueos.", "internal_next_action": order.get("next_step") or "Revisión interna", "internal_notes": "Sin notas operativas registradas.", "internal_notice_sent": False})
    return data


def _html_list(values: list[str], empty: str = "No registrado") -> str:
    return "<ul>" + "".join(f"<li>{escape(value)}</li>" for value in values) + "</ul>" if values else f"<p>{escape(empty)}</p>"


def render_internal_html(d: Dict[str, Any]) -> str:
    material_rows = "".join(f'<tr><td>{escape(row["material"])}</td><td>{escape(row["state"])}</td><td>{escape(row["note"])}</td></tr>' for row in d["materials"]) or '<tr><td>No registrado</td><td>Sin confirmar</td><td>La orden no contiene materiales necesarios.</td></tr>'
    criteria = _html_list(d["verification_criteria"], "Pendiente interno: no existen criterios de comprobación registrados en la orden.")
    notice = f'/qa-control/orders/{escape(d["order_id"])}/internal-notice'
    confirmation = f'/qa-control/orders/{escape(d["order_id"])}/confirmation'
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ficha interna · {escape(d["order_id"])}</title><link rel="stylesheet" href="/qa-control/confirmation.css"></head><body><main><div class="qa">QA CONTROLADO · FICHA PRIVADA · {escape(d["template_version"])}</div><section class="meta"><b>Orden:</b> {escape(d["order_id"])}<br><b>Snapshot:</b> v{escape(str(d["snapshot_version"] or "No registrada"))} · {escape(str(d["snapshot_sha256"] or "Hash no disponible"))}<br><b>Fuente:</b> orden archivada; transcript excluido</section><article><header>ENDRIAN · USO INTERNO</header><h1>Ficha interna de preparación</h1><h2>Control de la orden</h2><dl><dt>Orden</dt><dd>{escape(d["order_id"])}</dd><dt>Fecha</dt><dd>{escape(_fmt_date(d["confirmed_at"]))}</dd><dt>Estado interno</dt><dd>{escape(d["internal_status"])}</dd><dt>Servicio</dt><dd>{escape(d["service"])}</dd><dt>Solución</dt><dd>{escape(d["solution_title"])}</dd><dt>Importe</dt><dd>{escape(_amount(d))}</dd><dt>Pago</dt><dd>{escape(d["payment_status"])} · {escape(d["payment_reference"])}</dd><dt>Plazo</dt><dd>{escape(d["delivery_window"])}</dd></dl><h2>Contacto del cliente</h2><dl><dt>Nombre</dt><dd>{escape(d["customer_name"])}</dd><dt>Correo</dt><dd>{escape(d["customer_email"])}</dd><dt>País</dt><dd>{escape(d["billing_country"])}</dd><dt>Teléfono</dt><dd>{escape(d["customer_phone"])}</dd></dl><h2>Necesidad, objetivo y contexto</h2><p><b>Necesidad:</b> {escape(d["need_confirmed"])}</p><p><b>Objetivo:</b> {escape(d["objective"])}</p><p><b>Contexto:</b> {escape(d["context"])}</p><p><b>Por qué encaja:</b> {escape(d["why_fit"])}</p><h2>Alcance y compromisos</h2><p>{escape(d["scope"])}</p>{_html_list(d["characteristics"])}<h2>Entregables</h2>{_html_list(d["deliverables"])}<h2>Plataforma, información y entrega</h2><dl><dt>Plataforma</dt><dd>{escape(d["platform"])}</dd><dt>Forma de incorporar información</dt><dd>{escape(d["information_input"])}</dd><dt>Modalidad de entrega</dt><dd>{escape(d["delivery"])}</dd></dl><h2>Restricciones, exclusiones y dependencias</h2>{_html_list(d["exclusions"] + d["controls"] + d["dependencies"])}<h2>Materiales</h2><div class="table-wrap"><table><thead><tr><th>Material</th><th>Estado</th><th>Pendiente / nota</th></tr></thead><tbody>{material_rows}</tbody></table></div><h2>Criterios de comprobación acordados</h2>{criteria}<h2>Seguimiento interno de preparación</h2><dl><dt>Responsable interno</dt><dd>{escape(d["internal_owner"])}</dd><dt>Bloqueos</dt><dd>{escape(d["internal_blockers"])}</dd><dt>Próxima acción</dt><dd>{escape(d["internal_next_action"])}</dd><dt>Observaciones</dt><dd>{escape(d["internal_notes"])}</dd></dl><h2>Trazabilidad técnica secundaria</h2><dl><dt>Cotización</dt><dd>{escape(str(d["quotation_ref"] or "No registrada"))} · v{escape(str(d["quotation_version"] or "No registrada"))}</dd><dt>Scope version</dt><dd>{escape(str(d["scope_version_id"] or "No registrada"))}</dd><dt>Solicitud versionada</dt><dd>{escape(str(d["solution_request_version_id"] or "No registrada"))}</dd><dt>Referencia de pago</dt><dd>{escape(d["payment_reference"])}</dd><dt>Snapshot / hash</dt><dd>v{escape(str(d["snapshot_version"] or "No registrada"))} · {escape(str(d["snapshot_sha256"] or "No disponible"))}</dd><dt>Versiones documentales</dt><dd>{escape(str(d["terms_version"]))} · {escape(str(d["privacy_version"]))} · {escape(str(d["conditions_version"]))}</dd><dt>Evidencia de conversación</dt><dd>Referencia interna; el chat no forma parte del pedido archivado.</dd></dl><p><a href="{confirmation}">Abrir vista previa del correo al cliente</a> · <a href="{notice}">Abrir aviso interno QA</a></p><footer>Uso interno QA · Sin asignación, envío ni construcción automática</footer></article></main></body></html>'''


def build_internal_notice(d: Dict[str, Any]) -> Dict[str, Any]:
    return {"template_version": d["template_version"], "sent": False, "provider": None, "to": INTERNAL_RECIPIENT_PLACEHOLDER, "subject": f'Nueva orden {d["order_id"]} · {d["service"]} · revisión interna', "order_id": d["order_id"], "service": d["service"], "solution_title": d["solution_title"], "internal_path": f'/qa-control/orders/{d["order_id"]}/internal'}


def render_internal_notice_html(notice: Dict[str, Any]) -> str:
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(notice["subject"])}</title><link rel="stylesheet" href="/qa-control/confirmation.css"></head><body><main><div class="qa">QA CONTROLADO · AVISO INTERNO · NO ENVIADO · sent=false</div><section class="meta"><b>Destinatario:</b> {escape(notice["to"])}<br><b>Asunto:</b> {escape(notice["subject"])}</section><article><header>ENDRIAN · USO INTERNO</header><h1>Nueva orden para revisión interna</h1><dl><dt>Orden</dt><dd>{escape(notice["order_id"])}</dd><dt>Servicio</dt><dd>{escape(notice["service"])}</dd><dt>Solución</dt><dd>{escape(notice["solution_title"])}</dd></dl><p>La orden quedó archivada y requiere revisión interna antes de preparar el trabajo.</p><p><a href="{escape(notice["internal_path"])}">Abrir ficha interna de preparación</a></p><aside>No se envió ningún aviso. No existe proveedor ni destinatario corporativo configurado.</aside><footer>Plantilla {escape(notice["template_version"])}</footer></article></main></body></html>'''
