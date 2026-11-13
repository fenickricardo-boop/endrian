from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

QA_PRICES = {"esencial": 39, "especializado": 89, "integral": 149}
QA_CURRENCY = "USD"
QA_DELIVERY_WINDOWS = {
    "esencial": "2 a 5 días hábiles desde la confirmación del pago",
    "especializado": "2 a 5 días hábiles desde la confirmación del pago",
    "integral": "2 a 5 días hábiles desde la confirmación del pago",
}
QA_AMOUNT_CLP = QA_PRICES["especializado"]
QA_DELIVERY_WINDOW = QA_DELIVERY_WINDOWS["especializado"]
QA_PLATFORM_LABEL = "Entorno simulado de ENDRIAN"
QA_PLATFORM_NOTICE = "Dato ficticio de plataforma para QA; pendiente de definición comercial."
QA_DELIVERY_NOTICE = "Dato ficticio de plazo para QA; pendiente de aprobación operativa y comercial."
SERVICE_LABELS = {"esencial": "ENDRIAN Esencial", "especializado": "ENDRIAN Especializado", "integral": "ENDRIAN Integral"}
QA_CANONICAL_CONTACT_NAME = "Juan Pérez"
QA_CANONICAL_CONTACT_EMAIL = "juan.perez@example.com"
QA_OPTIONAL_PHONE = "+12025550147"
PREPAYMENT_CONDITIONS_VERSION = "QA-CONDITIONS-0.2"
QA_TERMS_VERSION = "QA-TERMS-0.1"
QA_PRIVACY_VERSION = "QA-PRIVACY-0.1"
QA_VALIDITY_DAYS = 7
COMMERCIAL_RULES_VERSION = "QA-COMMERCIAL-0.5"
CAPABILITY_MATRIX_VERSION = "0.2.1"
ENVIRONMENT_CATALOG_VERSION = "0.1.1"
EDITORIAL_CARDS_VERSION = "1.1"
ENVIRONMENT_ID = "ENV-ENDRIAN-MANAGED"
DELIVERY_MODE = "ENDRIAN_MANAGED_ACCESS"
FLOW_STATES = {"S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "SH"}
WORKFLOW_STATUSES = {"DRAFT", "CLARIFICATION_REQUIRED", "VALIDATION_BLOCKED", "SPECIAL_REVIEW_REQUIRED", "VALIDATED_FOR_QUOTATION", "SUPERSEDED"}
VALIDATION_RESULTS = {"VALIDATED_FOR_QUOTATION", "REQUIRES_HUMAN_REVIEW", "BLOCKED_UNAUTHORIZED", "PENDING_AUTHORITY", "RECLASSIFICATION_REQUIRED"}
FORBIDDEN_EXTERNAL_FIELDS = {"chat_summary", "conversation_text", "transcript", "raw_messages", "turn_history", "narrative_chat_recap", "conversation_evidence", "internal_dimensioning"}
CLIENT_OUTPUT_FIELDS = {"request_title", "request_description", "need_confirmed", "objective", "service", "why_fit", "scope", "deliverables", "information_input", "materials_needed", "agent", "commitments", "context", "environment_label", "environment_notice", "delivery_label", "delivery_notice", "dependencies", "limits", "price", "amount_label", "currency", "delivery_window", "conditions", "quotation_ref", "quotation_valid_until", "order_ref"}

QA_CONDITIONS = [
    "Pago simulado.",
    "2 a 5 días hábiles desde la confirmación del pago.",
    "El precio no incluye suscripciones, licencias ni consumo de servicios externos. Si tu agente los necesita, te indicaremos cuáles y sus costos antes del pago.",
    "Las nuevas funciones y el acompañamiento posterior se gestionan por separado.",
]
QA_TERMS = ["Términos generales provisionales para esta simulación.", "No constituyen condiciones comerciales o legales definitivas."]
QA_PRIVACY_NOTICE = ["Aviso de privacidad provisional para QA.", "Utiliza únicamente datos ficticios; no se envía información a servicios externos."]

FIXTURE_ID = "QA-ESPECIALIZADO-01"
FIXTURE_INITIAL = "Necesito algo para ordenar los correos que nos llegan de clientes porque se nos pierden cosas. Somos cuatro personas y usamos correo para consultas, reclamos y solicitudes. Me gustaría que pudiera responder y hacer seguimiento."
FIXTURE_REPLY = "Son unos 80 correos al día. Mejor que no responda solo. Quiero que clasifique, priorice y nos ayude a llevar seguimiento, pero que una persona revise las respuestas. Lo de responder automáticamente descártalo."
FIXTURE_SCOPE = {
    "need_confirmed": "Organizar y dar seguimiento a las consultas de clientes recibidas por correo para que un equipo de cuatro personas pueda priorizar pendientes y mantener continuidad en la atención.",
    "objective": "Reducir pérdidas y demoras en la gestión de solicitudes manteniendo el control del equipo.",
    "recommended_agent": "ENDRIAN Especializado", "why_fit": "Corresponde a una función concreta y acotada: organizar la atención por correo con criterios definidos y revisión del equipo.",
    "scope_confirmed": "ENDRIAN preparará una configuración especializada para clasificar, priorizar y organizar el seguimiento de consultas, reclamos y solicitudes. La solución preparará borradores, pero no enviará respuestas ni se conectará a cuentas reales en esta prueba.",
    "deliverable_summary": "Solución para gestión de atención por correo",
    "information_input": "Tu equipo incorporará los datos de cada caso en el entorno acordado. Esta prueba no conecta ni lee cuentas de correo reales.",
    "materials_needed": ["Criterios de prioridad.", "Ejemplos ficticios de consultas, reclamos y solicitudes.", "Criterios de revisión de los borradores."],
    "deliverables": ["Configuración especializada con instrucciones y criterios acordados.", "Estructura para clasificar, priorizar y registrar el seguimiento.", "Pruebas con ejemplos ficticios antes de la entrega.", "Guía breve para comenzar a utilizar la configuración."],
    "includes": ["Clasificación de consultas, reclamos y solicitudes.", "Priorización según criterios definidos.", "Seguimiento del estado de cada caso.", "Preparación de respuestas para revisión del equipo.", "Organización compartida de pendientes."],
    "excludes": ["Envío autónomo de respuestas.", "Conexión a cuentas de correo o sistemas externos.", "SLA, operación 24/7 o acciones externas autónomas."],
}
FIXTURE_COMMITMENTS = [
    {"item_id": "PRO-CAP-001", "label": "Clasificar consultas, reclamos y solicitudes."},
    {"item_id": "PRO-CAP-004", "label": "Priorizar mensajes y pendientes según los criterios definidos."},
    {"item_id": "PRO-CAP-005", "label": "Mantener seguimiento del estado de los casos."},
    {"item_id": "PRO-CAP-002", "label": "Preparar borradores de respuesta para que el equipo los revise antes del envío."},
    {"item_id": "PRO-CAP-006", "label": "Organizar el trabajo compartido del equipo de cuatro personas para mantener continuidad."},
]

SPECIAL_FIXTURE_ID = "QA-INTEGRAL-REVIEW-01"
SPECIAL_FIXTURE_INITIAL = "Necesito un agente que coordine atención por correo, documentos internos y seguimiento entre varias áreas, con decisiones que requieren revisión de responsables distintos."
SPECIAL_FIXTURE_SCOPE = {
    "need_confirmed": "Coordinar un proceso compartido de atención, documentación y seguimiento entre varias áreas, manteniendo decisiones sensibles bajo revisión de sus responsables.",
    "objective": "Definir una solución integrada entre áreas sin automatizar decisiones materiales ni asumir dependencias todavía no validadas.",
    "recommended_agent": "ENDRIAN Integral",
    "why_fit": "La solicitud cruza varios procesos y requiere validar dependencias y responsables antes de cotizar.",
    "scope_confirmed": "Coordinación entre atención por correo, documentación interna y seguimiento multiárea, sujeta a revisión especial de dependencias y controles.",
    "deliverable_summary": "Solución integral para coordinación de atención y seguimiento multiárea",
    "includes": ["Coordinación del flujo entre las áreas definidas.", "Organización de solicitudes y documentos asociados.", "Seguimiento compartido con responsables identificados."],
    "excludes": ["Decisiones sensibles autónomas.", "Integraciones o permisos no validados.", "Precio o plazo automático antes de la revisión."],
}
SPECIAL_FIXTURE_COMMITMENTS = [
    {"item_id":"INT-CAP-001","label":"Coordinar el flujo entre las áreas definidas."},
    {"item_id":"INT-CAP-002","label":"Organizar solicitudes y documentos asociados."},
    {"item_id":"INT-CAP-003","label":"Mantener seguimiento compartido con responsables identificados."},
]

def utc_now() -> datetime: return datetime.now(timezone.utc)
def iso(dt: datetime) -> str: return dt.replace(microsecond=0).isoformat()

def default_full_flow(session_id: str) -> Dict[str, Any]:
    return {"state":"S0","state_label":"Entrada","microstate":None,"fixture_id":None,"qa_identity":None,"dimensioning":{},
        "internal_dimensioning":{"classification":"INTERNO / NO EXPORTABLE","values":{}},"orientation_summary":None,
        "scope_versions":[],"current_scope_version_id":None,"solution_request_versions":[],"current_solution_request_version_id":None,
        "workflow_status":"DRAFT","validation_result":None,"validation_causes":[],"quotations":[],"current_quotation_ref":None,"client_output":None,
        "contracting_data":None,"payment_qa":{"status":"NO_INICIADO","simulation":True},"order_qa":None,"email_preview":None,"internal_matrix_qa":None,
        "conversation_evidence":{"classification":"INTERNO / NO EXPORTABLE","turns":[]},"human_review":{"pending":False,"reason":None,"return_state":None},
        "material_contradiction":False,"selected_agent":None,"validated_agent":None,"product_conformity":None,"previous_state":None,"tracking_origin":None,
        "trace":[{"event":"FULL_FLOW_V036_INITIALIZED","state":"S0","at":iso(utc_now())}],"simulation":True,"no_production":True,"external_services":False}

def ensure_flow(app_meta: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    flow=app_meta.get("full_flow")
    if not isinstance(flow,dict): flow=default_full_flow(session_id); app_meta["full_flow"]=flow
    for key,value in default_full_flow(session_id).items(): flow.setdefault(key,deepcopy(value))
    return flow

def set_state(flow: Dict[str, Any], state: str, event: str, **extra: Any) -> None:
    if state not in FLOW_STATES: raise ValueError(f"Unsupported full-flow state: {state}")
    previous=flow.get("state"); flow["previous_state"]=previous; flow["state"]=state
    labels={"S0":"Entrada","S1":"Comprensión","S2":"Datos de contacto","S3":"Definición","S4":"Confirmación","S5":"Solicitud y aceptación","S6":"Pago simulado","S7":"Orden","S8":"Seguimiento","SH":"Revisión especial"}
    flow["state_label"]=labels[state]; item={"event":event,"from":previous,"state":state,"at":iso(utc_now())}; item.update({k:v for k,v in extra.items() if v is not None})
    flow.setdefault("trace",[]).append(item); flow["trace"]=flow["trace"][-200:]

def build_identity(session_id: str, name: str=QA_CANONICAL_CONTACT_NAME, email: str=QA_CANONICAL_CONTACT_EMAIL, phone: Optional[Dict[str, Any]]=None, country_code: str="CL", country_name: str="Chile") -> Dict[str, Any]:
    digest=hashlib.sha256(session_id.encode()).hexdigest()[:12]
    return {"qa_identity_ref":f"QID-{digest.upper()}","name":name,"email":email,"phone":deepcopy(phone),"billing_country":{"country_code":country_code,"country_name":country_name},"contact_confirmed_at":None,"email_verification_status":"SIMULATED_UNVERIFIED","email_verified_qa":False,"consents":{"contract_terms":False,"data_processing":False,"marketing":False},"simulation":True}

def validate_client_output(data: Dict[str, Any]) -> Dict[str, Any]:
    if FORBIDDEN_EXTERNAL_FIELDS.intersection(data): raise ValueError("Forbidden internal field in client_output")
    return {k:deepcopy(v) for k,v in data.items() if k in CLIENT_OUTPUT_FIELDS}

def build_scope_version(flow: Dict[str, Any], orientation: Dict[str, Any]) -> Dict[str, Any]:
    current=current_scope(flow)
    if current and current.get("status")=="CONFIRMED": return current
    number=len(flow.get("scope_versions",[]))+1
    base=deepcopy(FIXTURE_SCOPE) if flow.get("fixture_id")==FIXTURE_ID else deepcopy(SPECIAL_FIXTURE_SCOPE) if flow.get("fixture_id")==SPECIAL_FIXTURE_ID else {"need_confirmed":orientation.get("interpreted_need") or "Necesidad funcional confirmada.","objective":orientation.get("objective") or "Objetivo funcional confirmado.","recommended_agent":orientation.get("recommended_agent") or orientation.get("recommended") or "SH / revisión humana","why_fit":orientation.get("why") or "Validación pendiente.","scope_confirmed":orientation.get("preliminary_scope") or "Alcance confirmado.","deliverable_summary":"Construcción configurada dentro del alcance confirmado.","includes":["Configuración y pruebas dentro del alcance confirmado."],"excludes":["Producción y servicios externos no confirmados."]}
    scope={"scope_version_id":f"SCOPE-QA-{number:04d}","scope_version":number,"status":"CONFIRMED","confirmed":True,"confirmed_at":iso(utc_now()),**base}
    flow.setdefault("scope_versions",[]).append(scope); flow["current_scope_version_id"]=scope["scope_version_id"]; return scope

def current_scope(flow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref=flow.get("current_scope_version_id"); return next((x for x in reversed(flow.get("scope_versions",[])) if x.get("scope_version_id")==ref),None)

def current_solution_request(flow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref=flow.get("current_solution_request_version_id"); return next((x for x in reversed(flow.get("solution_request_versions",[])) if x.get("solution_request_version_id")==ref),None)

def build_solution_request(flow: Dict[str, Any]) -> Dict[str, Any]:
    scope=current_scope(flow)
    if not scope: raise ValueError("Confirmed scope required")
    n=len(flow.get("solution_request_versions",[]))+1; validated="especializado" if flow.get("fixture_id")==FIXTURE_ID else "integral" if flow.get("fixture_id")==SPECIAL_FIXTURE_ID else (flow.get("selected_agent") or "integral"); preference=flow.get("selected_agent")
    route="STANDARD" if validated in {"esencial","especializado"} else "SPECIAL_REVIEW"; result="VALIDATED_FOR_QUOTATION" if route=="STANDARD" else "REQUIRES_HUMAN_REVIEW"; workflow="VALIDATED_FOR_QUOTATION" if route=="STANDARD" else "SPECIAL_REVIEW_REQUIRED"; causes=[] if route=="STANDARD" else ["PRODUCT_REQUIRES_SPECIAL_REVIEW"]
    conformity=None
    if preference and preference!=validated:
        result="RECLASSIFICATION_REQUIRED"; workflow="VALIDATION_BLOCKED"; causes=["INITIAL_PREFERENCE_DIFFERS_FROM_VALIDATED_PRODUCT"]; conformity={"previous_product":preference,"proposed_product":validated,"accepted":False,"accepted_at":None}
    commitments=deepcopy(FIXTURE_COMMITMENTS) if validated=="especializado" and flow.get("fixture_id")==FIXTURE_ID else deepcopy(SPECIAL_FIXTURE_COMMITMENTS) if flow.get("fixture_id")==SPECIAL_FIXTURE_ID else []
    special=flow.get("fixture_id")==SPECIAL_FIXTURE_ID
    service_label=SERVICE_LABELS.get(validated, validated)
    request_title=FIXTURE_SCOPE["deliverable_summary"] if validated=="especializado" and flow.get("fixture_id")==FIXTURE_ID else SPECIAL_FIXTURE_SCOPE["deliverable_summary"] if special else f"Solución {service_label}"
    request={"solution_request_version_id":f"SOLREQ-QA-{n:04d}","solution_request_version":n,"scope_version_id":scope["scope_version_id"],"status":"CURRENT","workflow_status":workflow,"validation_result":result,"validation_causes":causes,"route":route,"initial_preference":preference,"validated_agent":validated,"validated_agent_label":service_label,"service_label":service_label,"request_title":request_title,"product_conformity":conformity,"objective":scope["objective"],"context":"Atención por correo de un equipo de cuatro personas" if flow.get("fixture_id")==FIXTURE_ID else "Coordinación de atención, documentación y seguimiento entre varias áreas" if special else scope["need_confirmed"],"why_fit":scope.get("why_fit"),"scope":scope.get("scope_confirmed"),"deliverables":deepcopy(scope.get("deliverables") or commitments),"information_input":scope.get("information_input"),"materials_needed":deepcopy(scope.get("materials_needed") or []),"commitments":commitments,"controls":[{"item_id":"PRO-CTL-001","label":"El equipo revisa los borradores antes de enviarlos."}] if validated=="especializado" else [{"item_id":"INT-CTL-001","label":"Las decisiones materiales permanecen bajo revisión de sus responsables."}] if special else [],"exclusions":[{"item_id":"PRO-EXC-002","label":"Sin envío autónomo de respuestas."},{"item_id":"PRO-EXC-003","label":"Sin conexión a cuentas de correo o sistemas externos."},{"item_id":"PRO-EXC-004","label":"Sin SLA, operación 24/7 ni acciones externas autónomas."}] if validated=="especializado" else [{"item_id":"INT-EXC-001","label":"Sin integraciones, permisos ni decisiones autónomas antes de validación."}] if special else [],"environment_id":ENVIRONMENT_ID,"environment_catalog_version":ENVIRONMENT_CATALOG_VERSION,"platform_label":QA_PLATFORM_LABEL,"platform_notice":QA_PLATFORM_NOTICE,"delivery_mode":DELIVERY_MODE,"dependencies":["Áreas y responsables simulados","Documentos internos simulados","Dependencias e integraciones pendientes de revisión"] if special else ["Datos de casos incorporados manualmente en QA","Criterios de prioridad definidos","Ejemplos ficticios para pruebas","El equipo revisa los borradores antes de enviarlos."],"matrix_version":CAPABILITY_MATRIX_VERSION,"matrix_item_ids":[x["item_id"] for x in commitments]+(["PRO-CTL-001"] if validated=="especializado" else ["INT-CTL-001"] if special else []),"created_at":iso(utc_now()),"simulation":True}
    flow.setdefault("solution_request_versions",[]).append(request); flow["current_solution_request_version_id"]=request["solution_request_version_id"]; flow["workflow_status"]=workflow; flow["validation_result"]=result; flow["validation_causes"]=causes; flow["validated_agent"]=validated; flow["product_conformity"]=conformity; flow["client_output"]=project_client_output(flow,request,None); return request

def accept_product_change(flow: Dict[str, Any]) -> bool:
    req=current_solution_request(flow); conformity=(req or {}).get("product_conformity")
    if not req or not conformity or conformity.get("accepted"): return False
    conformity.update({"accepted":True,"accepted_at":iso(utc_now()),"accepted_product":req["validated_agent"],"solution_request_version_id":req["solution_request_version_id"]}); req["workflow_status"]="VALIDATED_FOR_QUOTATION" if req["route"]=="STANDARD" else "SPECIAL_REVIEW_REQUIRED"; req["validation_result"]="VALIDATED_FOR_QUOTATION" if req["route"]=="STANDARD" else "REQUIRES_HUMAN_REVIEW"; req["validation_causes"]=[] if req["route"]=="STANDARD" else ["PRODUCT_REQUIRES_SPECIAL_REVIEW"]; flow["workflow_status"]=req["workflow_status"]; flow["validation_result"]=req["validation_result"]; flow["validation_causes"]=deepcopy(req["validation_causes"]); flow["product_conformity"]=deepcopy(conformity); return True

def current_quotation(flow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ref=flow.get("current_quotation_ref"); return next((x for x in reversed(flow.get("quotations",[])) if x.get("quotation_ref")==ref),None)

def project_client_output(flow: Dict[str, Any], request: Dict[str, Any], quote: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    scope=current_scope(flow) or {}; output={"request_title":request.get("request_title",""),"request_description":"Configuración especializada para organizar la atención por correo con criterios definidos y control del equipo.","need_confirmed":scope.get("need_confirmed"),"objective":scope.get("objective"),"service":request.get("service_label"),"why_fit":request.get("why_fit"),"scope":request.get("scope"),"deliverables":[x.get("label","") if isinstance(x,dict) else str(x) for x in request.get("deliverables",[])],"information_input":request.get("information_input"),"materials_needed":request.get("materials_needed",[]),"agent":request.get("validated_agent_label"),"commitments":[x["label"] for x in request.get("commitments",[])],"context":request.get("context"),"environment_label":request.get("platform_label") or QA_PLATFORM_LABEL,"environment_notice":request.get("platform_notice") or QA_PLATFORM_NOTICE,"delivery_label":"Configuración preparada para el entorno acordado","delivery_notice":QA_DELIVERY_NOTICE,"dependencies":request.get("dependencies",[]),"limits":[x["label"] for x in request.get("exclusions",[])],"conditions":deepcopy((quote or {}).get("conditions",[]))}
    if quote: output.update({"price":quote["amount"],"amount_label":quote["amount_label"],"currency":quote["currency"],"delivery_window":quote["delivery_window"],"quotation_ref":quote["quotation_ref"],"quotation_valid_until":quote["expires_at"]})
    return validate_client_output(output)

def build_email_preview(client_output: Dict[str, Any], identity: Dict[str, Any]) -> Dict[str, Any]:
    c=validate_client_output(client_output); ref=c.get("quotation_ref",""); body=(f"Resumen de tu solicitud · {ref}\n\n{c.get('request_title','')}\n{c.get('request_description','')}\n\nLo que prepararemos\n"+"\n".join(f"• {x}" for x in c.get("commitments",[]))+f"\n\nValor\n{c.get('amount_label','')}\n\nPlazo estimado\n{c.get('delivery_window','')}\n\nCondiciones\n"+"\n".join(c.get("conditions",[])))
    return {"label":"Vista previa del correo · No enviado","to":identity.get("email",""),"subject":f"Tu solicitud ENDRIAN · {str(ref).split('/')[0]}","content":c,"body":body,"cta_label":"Continuar con mi solicitud","sent":False,"provider":None,"external_service":False,"simulation":True}

def build_order_email_preview(order: Dict[str, Any]) -> Dict[str, Any]:
    snap=deepcopy(order.get("construction_request_snapshot") or {})
    service=snap.get("service_label") or snap.get("agent") or ""
    body=(f"Hola {(snap.get('contact') or {}).get('name','cliente')},\n\n"
          "Confirmamos tu pago de prueba y recibimos tu pedido.\n\n"
          f"Orden: {order.get('order_id','')}\n"
          f"Solución: {snap.get('solution_title','')}\n"
          f"Servicio contratado: {service}\n"
          f"Importe: {snap.get('currency','')} {snap.get('amount','')}\n"
          f"Plazo acordado: {snap.get('delivery_window','')}\n\n"
          "Siguiente paso: ENDRIAN continuará con la preparación y comprobación de la solución según el alcance confirmado.\n\n"
          "Adjuntamos un único PDF con el detalle y las condiciones de tu pedido.\n\nENDRIAN")
    return {"template_version":"ENDRIAN-POST-CONFIRMACION-1.1-QA","label":"Vista previa del correo · No enviado","to":(snap.get("contact") or {}).get("email",""),"subject":f"Pedido confirmado · Orden {order.get('order_id','')}","order_id":order.get("order_id"),"order_status":"Pedido recibido","solution_title":snap.get("solution_title"),"service":service,"agent":service,"amount":snap.get("amount"),"currency":snap.get("currency"),"delivery_window":snap.get("delivery_window"),"platform_label":snap.get("platform_label"),"delivery_label":snap.get("delivery_label"),"features":[x.get("label","") if isinstance(x,dict) else str(x) for x in snap.get("commitments",[])],"dependencies":deepcopy(snap.get("dependencies",[])),"conditions_version":snap.get("conditions_version"),"terms_version":snap.get("terms_version"),"privacy_notice_version":snap.get("privacy_notice_version"),"body":body,"sent":False,"provider":None,"external_service":False,"simulation":True,"conversation_evidence_included":False}

def build_quotation(flow: Dict[str, Any], reviewed: bool=False, actor: Optional[str]=None, reviewed_amount: Optional[int]=None, reviewed_delivery: Optional[str]=None) -> Dict[str, Any]:
    req=current_solution_request(flow)
    if not req: raise ValueError("Validated solution request required")
    if req.get("validation_result") in {"BLOCKED_UNAUTHORIZED","PENDING_AUTHORITY","RECLASSIFICATION_REQUIRED"}: raise ValueError("Material validation block")
    if req.get("route")=="SPECIAL_REVIEW" and not reviewed: raise ValueError("Special review required")
    agent=req["validated_agent"]
    if agent not in QA_PRICES and (not reviewed or not isinstance(reviewed_amount,int) or reviewed_amount<=0 or not reviewed_delivery): raise ValueError("Reviewed price and delivery required")
    n=len(flow.get("quotations",[]))+1; now=utc_now(); qid="END-QA-COT-0001"
    # A human reviewer's approved amount/delivery_window must win over the
    # catalog default for that agent id — QA_PRICES/QA_DELIVERY_WINDOWS already
    # happen to define an entry for every agent (including "integral"), so
    # `.get(agent, reviewed_*)` previously never fell back to the reviewed
    # value and silently discarded what the reviewer approved.
    amount=reviewed_amount if (reviewed and isinstance(reviewed_amount,int) and reviewed_amount>0) else QA_PRICES.get(agent,reviewed_amount)
    delivery_window=reviewed_delivery if (reviewed and reviewed_delivery) else QA_DELIVERY_WINDOWS.get(agent,reviewed_delivery)
    expires_at=iso(now+timedelta(days=QA_VALIDITY_DAYS))
    quote={"quotation_id":qid,"quotation_version":n,"quotation_ref":f"{qid}/v{n}","scope_version_id":req["scope_version_id"],"solution_request_version_id":req["solution_request_version_id"],"matrix_version":req["matrix_version"],"matrix_item_ids":deepcopy(req["matrix_item_ids"]),"commercial_rules_version":COMMERCIAL_RULES_VERSION,"conditions_version":PREPAYMENT_CONDITIONS_VERSION,"status":"ISSUED","microstate":"S5.Q-ISSUED","amount":amount,"amount_label":f"USD {amount}","currency":QA_CURRENCY,"delivery_window":delivery_window,"delivery_window_accepted":False,"conditions":deepcopy(QA_CONDITIONS),"expires_at":expires_at,"valid_until":expires_at,"created_at":iso(now),"reviewed":reviewed,"review_actor":actor,"simulation":True}
    client=project_client_output(flow,req,quote); preview=build_email_preview(client,flow.get("qa_identity") or {}); quote["email_preview"]=preview; flow.setdefault("quotations",[]).append(quote); flow["current_quotation_ref"]=quote["quotation_ref"]; flow["client_output"]=client; flow["microstate"]="S5.Q-ISSUED"; flow["email_preview"]=preview; return quote

def quotation_expired(q: Optional[Dict[str, Any]]) -> bool:
    if not q or q.get("force_expired_qa"): return True
    try: return utc_now()>=datetime.fromisoformat(q.get("expires_at") or q.get("valid_until", ""))
    except Exception: return True

def prepayment_complete(flow: Dict[str, Any]) -> bool:
    d=flow.get("contracting_data") or {}; identity=flow.get("qa_identity") or {}
    country=identity.get("billing_country") or {}
    if not (identity.get("name") and identity.get("email") and identity.get("contact_confirmed_at") and country.get("country_code") and country.get("country_name")): return False
    if not d.get("contract_terms_accepted") or not d.get("privacy_authorization_accepted"): return False
    if d.get("conditions_version")!=PREPAYMENT_CONDITIONS_VERSION or d.get("terms_version")!=QA_TERMS_VERSION or d.get("privacy_notice_version")!=QA_PRIVACY_VERSION: return False
    return True

def payment_gate(flow: Dict[str, Any]) -> Dict[str, Any]:
    q=current_quotation(flow) or {}; scope=current_scope(flow) or {}; req=current_solution_request(flow) or {}; identity=flow.get("qa_identity") or {}; material_results={"BLOCKED_UNAUTHORIZED","PENDING_AUTHORITY","RECLASSIFICATION_REQUIRED","REQUIRES_HUMAN_REVIEW"}
    standard=req.get("route")=="STANDARD"; price_valid=(q.get("amount")==QA_PRICES.get(req.get("validated_agent"))) if standard else bool(q.get("reviewed") and isinstance(q.get("amount"),int) and q.get("amount")>0); delivery_valid=(q.get("delivery_window")==QA_DELIVERY_WINDOWS.get(req.get("validated_agent"))) if standard else bool(q.get("reviewed") and q.get("delivery_window"))
    conditions={"solution_request_validated":req.get("validation_result")=="VALIDATED_FOR_QUOTATION","no_material_validation_block":req.get("validation_result") not in material_results,"quotation_accepted":q.get("status")=="ACCEPTED","quotation_version_current":q.get("quotation_ref")==flow.get("current_quotation_ref"),"scope_version_match":q.get("scope_version_id")==scope.get("scope_version_id"),"solution_request_version_match":q.get("solution_request_version_id")==req.get("solution_request_version_id"),"price_exact_valid":price_valid,"currency_defined":q.get("currency")==QA_CURRENCY,"delivery_window_present":delivery_valid,"delivery_window_accepted":bool(q.get("delivery_window_accepted")),"prepayment_data_complete":prepayment_complete(flow),"contact_confirmed":bool(identity.get("contact_confirmed_at")),"human_review_pending":not bool((flow.get("human_review") or {}).get("pending")),"material_contradiction":not bool(flow.get("material_contradiction")),"quotation_not_expired":not quotation_expired(q),"quotation_not_superseded":q.get("status") not in {"SUPERSEDED","SUPERSEDED_SCOPE_CHANGE","EXPIRED"}}
    return {"payment_enabled":all(conditions.values()),"conditions":conditions,"simulation":True}

def payment_reference(flow: Dict[str, Any]) -> str:
    q=current_quotation(flow) or {}; identity=(flow.get("qa_identity") or {}).get("qa_identity_ref",""); return "PAY-QA-"+hashlib.sha256(f"{identity}|{q.get('quotation_ref')}".encode()).hexdigest()[:10].upper()

def order_idempotency_key(flow: Dict[str, Any]) -> str:
    q=current_quotation(flow) or {}; p=flow.get("payment_qa") or {}; return hashlib.sha256(f"{q.get('solution_request_version_id')}|{q.get('quotation_id')}|{q.get('quotation_version')}|{p.get('reference')}|CONFIRMADO".encode()).hexdigest()

def build_internal_matrix(flow: Dict[str, Any], core_session: Any) -> Dict[str, Any]:
    q=current_quotation(flow) or {}; req=current_solution_request(flow) or {}; o=flow.get("order_qa") or {}; return {"status":"MATRIZ INTERNA QA / POST-PAGO / NO PRODUCCIÓN","conversation_evidence_ref":"INTERNAL_ONLY","client_output":validate_client_output(flow.get("client_output") or {}),"contracting_data":deepcopy(flow.get("contracting_data")),"traceability":{"scope_version_id":q.get("scope_version_id"),"solution_request_version_id":req.get("solution_request_version_id"),"quotation_id":q.get("quotation_id"),"quotation_version":q.get("quotation_version"),"order_id":o.get("order_id")},"simulation":True}
