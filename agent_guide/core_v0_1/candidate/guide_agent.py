#!/usr/bin/env python3
"""ENDRIAN Agente Guía MVP QA v0.1
Deterministic QA candidate. NO PRODUCCIÓN.
No network, no email, no payment provider, no production order creation.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import json, re, uuid

QA_MATRIX_COMPLETE = "MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN"
MATRIX_REVIEW = "MATRIZ EN REVISIÓN"

STATES = {
    "CONVERSACIÓN INICIAL", "COMPRENSIÓN PRELIMINAR", "REGISTRO PENDIENTE",
    "DIMENSIONAMIENTO INCOMPLETO", "ORIENTACIÓN EN REVISIÓN",
    "REVISIÓN HUMANA REQUERIDA", "PROPUESTA DISPONIBLE", "PRECIO PENDIENTE",
    "PAGO DISPONIBLE", "PAGO PENDIENTE", "PAGO RECHAZADO", "PAGO CANCELADO",
    "PAGO EXPIRADO", "PAGO CONFIRMADO", "ORDEN CONFIRMADA", MATRIX_REVIEW,
    QA_MATRIX_COMPLETE, "REEMBOLSO PENDIENTE", "REEMBOLSO CONFIRMADO"
}

SOURCE = "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx"
REFS = {
    "role": f"{SOURCE} · §0 Resumen ejecutivo y regla maestra; §1 Propósito, rol y fronteras",
    "initial": f"{SOURCE} · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
    "registration": f"{SOURCE} · §4 Puerta de registro, datos, consentimientos y recuperación",
    "dimensioning": f"{SOURCE} · §5 Dimensionamiento posterior al registro",
    "orientation": f"{SOURCE} · §6 Orientación recomendada y solicitud estructurada",
    "classification": f"{SOURCE} · §7 Clasificación comercial controlada",
    "proposal": f"{SOURCE} · §8 Propuesta previa al pago: alcance, precio y plazo",
    "payment": f"{SOURCE} · §9 Pago: habilitación, estados, recuperación y reembolsos",
    "order": f"{SOURCE} · §10 Confirmación posterior al pago y número de orden",
    "matrix": f"{SOURCE} · §11 Matriz interna de solicitud y producción",
    "human": f"{SOURCE} · §12 Revisión humana y reunión como excepción",
    "antiexfil": f"{SOURCE} · §13 Restricciones anti-exfiltración de valor",
    "attachments": f"{SOURCE} · §14.2 Adjuntos",
    "states": f"{SOURCE} · §17 Estados funcionales consolidados",
    "acceptance": f"{SOURCE} · §18 Criterios binarios de aceptación funcional",
    "pending": f"{SOURCE} · §19 Decisiones pendientes de Eduardo antes de producción",
}

FORBIDDEN_TECH_PATTERNS = [
    r"prompt final", r"prompt de sistema", r"dame.*c[oó]digo", r"pseudoc[oó]digo",
    r"arquitectura t[eé]cnica", r"stack", r"api exacta", r"paso a paso", r"configur"
]

@dataclass
class Session:
    session_id: str
    state: str = "CONVERSACIÓN INICIAL"
    simulation: bool = True
    conversation: List[Dict[str, str]] = field(default_factory=list)
    original_need: Optional[str] = None
    interpreted_need: Optional[str] = None
    objective: Optional[str] = None
    registration: Dict[str, Any] = field(default_factory=dict)
    dimensioning: Dict[str, Any] = field(default_factory=dict)
    orientation: Dict[str, Any] = field(default_factory=dict)
    classification: Optional[str] = None
    proposal: Dict[str, Any] = field(default_factory=dict)
    payment: Dict[str, Any] = field(default_factory=lambda: {"status":"NO INICIADO", "simulation":True})
    order: Optional[Dict[str, Any]] = None
    matrix: Optional[Dict[str, Any]] = None
    human_review_reason: Optional[str] = None
    trace: List[Dict[str, str]] = field(default_factory=list)

class GuideAgentQA:
    def __init__(self, fixtures: Optional[Dict[str, Any]]=None):
        self.fixtures = fixtures or {}
        self.sessions: Dict[str, Session] = {}

    def new_session(self, session_id: Optional[str]=None) -> Session:
        sid = session_id or f"QA-{uuid.uuid4().hex[:10].upper()}"
        s = Session(session_id=sid)
        s.trace.append({"event":"SESSION_CREATED","reference":REFS["initial"]})
        self.sessions[sid] = s
        return s

    def _contains(self, text:str, words:List[str]) -> bool:
        low = text.lower()
        return any(w in low for w in words)

    def interpret(self, s:Session, text:str) -> Dict[str,Any]:
        s.conversation.append({"role":"user","text":text})
        s.original_need = s.original_need or text
        low = text.lower()
        broad = any(x in low for x in ["automatizar mi empresa", "mejorar mi empresa", "necesito ayuda", "quiero automatizar"])
        if broad and len(text.split()) < 9:
            s.state = "CONVERSACIÓN INICIAL"
            out = {"action":"PEDIR ACLARACIÓN", "message":"Puedo ayudarte. Para orientarte sin adivinar, ¿qué proceso o tarea quieres mejorar primero?", "reference":REFS["initial"]}
            s.trace.append({"event":"CLARIFICATION_REQUESTED","reference":REFS["initial"]})
            return out
        s.interpreted_need = text.strip()
        if "reducir" in low or "ahorrar" in low or "tiempo" in low:
            s.objective = "Reducir trabajo manual y tiempo operativo en la necesidad descrita."
        elif "se me pierden" in low or "seguimiento" in low:
            s.objective = "Ordenar y dar seguimiento confiable a las solicitudes."
        else:
            s.objective = "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN."
        s.state = "COMPRENSIÓN PRELIMINAR"
        msg = f"Entiendo la necesidad a nivel preliminar: {s.interpreted_need}. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN."
        s.trace.append({"event":"PRELIMINARY_UNDERSTANDING","reference":REFS["initial"]})
        return {"action":"CONTINUAR", "message":msg, "next":"REGISTRO PENDIENTE", "reference":REFS["initial"]}

    def register(self, s:Session, *, name:str, email:str, data_processing:bool, operational_comms:bool, marketing:bool=False, company:Optional[str]=None, phone:Optional[str]=None, email_verified_qa:bool=True) -> Dict[str,Any]:
        s.state = "REGISTRO PENDIENTE"
        if not name.strip() or "@" not in email or not data_processing or not operational_comms or not email_verified_qa:
            return {"ok":False,"state":s.state,"reason":"Registro QA incompleto: nombre, correo QA verificado y consentimientos necesarios son obligatorios.","reference":REFS["registration"]}
        s.registration = {"name":name,"email":email,"company":company,"phone":phone,"email_verified_qa":True,"consent":{"data_processing":True,"operational_comms":True,"marketing":bool(marketing)},"simulation":True}
        s.state = "DIMENSIONAMIENTO INCOMPLETO"
        s.trace.append({"event":"QA_REGISTRATION_COMPLETED","reference":REFS["registration"]})
        return {"ok":True,"state":s.state,"registration":"REGISTRO SIMULADO","reference":REFS["registration"]}

    def dimension(self, s:Session, **kwargs) -> Dict[str,Any]:
        allowed = {"users","volume","frequency","systems","autonomy","data_sensitivity","custom_development","support","urgency","functions","integration_type"}
        for k,v in kwargs.items():
            if k in allowed and v is not None:
                s.dimensioning[k]=v
        # material review signals
        reason = None
        if str(s.dimensioning.get("data_sensitivity","")).lower() in {"sensible","sensitive","regulated","regulado"}:
            reason = "DATOS SENSIBLES / REGULADOS"
        if str(s.dimensioning.get("autonomy","")).lower() in {"alta","high","impacto","de impacto"}:
            reason = reason or "ALTA AUTONOMÍA / IMPACTO"
        if str(s.dimensioning.get("integration_type","")).lower() in {"unknown","desconocida","new","nueva","multiple_complex","múltiples complejas"}:
            reason = reason or "INTEGRACIÓN NO CONOCIDA O NO VALIDADA"
        if bool(s.dimensioning.get("custom_development")):
            reason = reason or "DESARROLLO PERSONALIZADO"
        if str(s.dimensioning.get("urgency","")).lower() in {"no estándar","nonstandard","urgente no validada"}:
            reason = reason or "URGENCIA NO PARAMETRIZADA"
        if reason:
            s.human_review_reason = reason
            s.state = "REVISIÓN HUMANA REQUERIDA"
            s.trace.append({"event":"HUMAN_REVIEW_REQUIRED","reference":REFS["human"]})
            return {"state":s.state,"reason":reason,"message":"Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.","reference":REFS["human"]}
        s.state = "ORIENTACIÓN EN REVISIÓN"
        s.trace.append({"event":"DIMENSIONING_READY","reference":REFS["dimensioning"]})
        return {"state":s.state,"reference":REFS["dimensioning"]}

    def build_orientation(self, s:Session) -> Dict[str,Any]:
        if s.state == "REVISIÓN HUMANA REQUERIDA":
            return {"state":s.state,"reason":s.human_review_reason,"reference":REFS["human"]}
        if not s.registration:
            return {"blocked":True,"reason":"La Orientación recomendada completa requiere registro QA previo.","reference":REFS["registration"]}
        funcs = s.dimensioning.get("functions")
        capabilities = []
        if isinstance(funcs,list): capabilities = funcs[:5]
        elif isinstance(funcs,str) and funcs.strip(): capabilities = [funcs.strip()]
        if not capabilities: capabilities = ["Organizar la necesidad descrita", "Aplicar el flujo funcional acordado"]
        s.orientation = {
            "title":"Orientación recomendada",
            "interpreted_need":s.interpreted_need,
            "objective":s.objective,
            "recommended":"Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
            "why":"Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
            "capabilities":capabilities,
            "preliminary_scope":"Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
            "simulation":True
        }
        s.state = "ORIENTACIÓN EN REVISIÓN"
        s.trace.append({"event":"ORIENTATION_READY","reference":REFS["orientation"]})
        return {"state":s.state,"orientation":s.orientation,"reference":REFS["orientation"]}

    def correct_orientation(self, s:Session, correction:str, material:bool) -> Dict[str,Any]:
        s.conversation.append({"role":"user","text":correction})
        if material:
            s.interpreted_need = correction
            s.orientation = {}
            s.proposal = {}
            s.classification = None
            s.state = "DIMENSIONAMIENTO INCOMPLETO"
            s.trace.append({"event":"MATERIAL_CORRECTION","reference":REFS["orientation"]})
            return {"state":s.state,"proposal_invalidated":True,"reference":REFS["orientation"]}
        if s.orientation:
            s.orientation["minor_correction"] = correction
        s.trace.append({"event":"MINOR_CORRECTION","reference":REFS["orientation"]})
        return {"state":"ORIENTACIÓN EN REVISIÓN","proposal_invalidated":False,"reference":REFS["orientation"]}

    def answer_post_orientation_question(self, s:Session, question:str) -> Dict[str,Any]:
        low = question.lower()
        if any(re.search(p, low) for p in FORBIDDEN_TECH_PATTERNS):
            return {"message":"Puedo explicarte qué conviene solicitar a ENDRIAN y el alcance funcional, pero no entregar una implementación, prompt, código, arquitectura o procedimiento listo para construir fuera de ENDRIAN.","boundary":"ANTI-EXFILTRACIÓN","reference":REFS["antiexfil"]}
        return {"message":"Puedo aclarar el encaje y las capacidades funcionales generales sin ejecutar ni diseñar la implementación técnica.","reference":REFS["antiexfil"]}

    def classify(self, s:Session, rules_fixture:Dict[str,Any]) -> Dict[str,Any]:
        if s.human_review_reason:
            s.classification = "Personalizado"
            s.state = "REVISIÓN HUMANA REQUERIDA"
            return {"classification":s.classification,"state":s.state,"source":"fixture QA + señal de revisión","reference":REFS["classification"]}
        # Explicit QA fixture only; never inferred from invented commercial thresholds.
        fixture_class = rules_fixture.get("classification")
        if fixture_class not in {"Esencial","Profesional","Personalizado"}:
            s.state = "PRECIO PENDIENTE"
            return {"classification":None,"state":s.state,"blocked":True,"reason":"Fixture comercial QA no autorizado o ausente.","reference":REFS["classification"]}
        s.classification = fixture_class
        if fixture_class == "Personalizado":
            s.state = "REVISIÓN HUMANA REQUERIDA"
            s.human_review_reason = s.human_review_reason or "CLASIFICACIÓN PERSONALIZADO QA"
        else:
            s.state = "PROPUESTA DISPONIBLE"
        s.trace.append({"event":"QA_CLASSIFICATION","reference":REFS["classification"]})
        return {"classification":fixture_class,"state":s.state,"simulation":True,"reference":REFS["classification"]}

    def make_proposal(self, s:Session, fixture:Dict[str,Any]) -> Dict[str,Any]:
        if s.state == "REVISIÓN HUMANA REQUERIDA" or s.classification == "Personalizado":
            s.state = "PRECIO PENDIENTE"
            return {"state":s.state,"payment_enabled":False,"reason":"Revisión/cotización humana QA requerida antes de precio/plazo exactos.","reference":REFS["proposal"]}
        price_kind = fixture.get("price_kind")
        price = fixture.get("price")
        delivery = fixture.get("delivery_window")
        if price_kind == "range":
            s.proposal = {"price_kind":"range","range":fixture.get("range","QA-RANGO-FICTICIO"),"delivery_window":delivery,"simulation":True}
            s.state = "PRECIO PENDIENTE"
            return {"state":s.state,"proposal":s.proposal,"payment_enabled":False,"reference":REFS["proposal"]}
        if price_kind != "exact" or price is None or not delivery:
            s.state = "PRECIO PENDIENTE"
            return {"state":s.state,"payment_enabled":False,"reason":"Falta precio exacto QA o plazo/ventana QA.","reference":REFS["proposal"]}
        s.proposal = {
            "request":s.interpreted_need,
            "includes":fixture.get("includes",["Capacidades funcionales del fixture QA"]),
            "excludes":fixture.get("excludes",["Implementación fuera del alcance QA"]),
            "classification":s.classification,
            "price_kind":"exact","price":price,"currency":"QA-UNIT","delivery_window":delivery,
            "accepted":False,"delivery_accepted":False,"simulation":True
        }
        s.state = "PROPUESTA DISPONIBLE"
        s.trace.append({"event":"QA_PROPOSAL_READY","reference":REFS["proposal"]})
        return {"state":s.state,"proposal":s.proposal,"payment_enabled":False,"reference":REFS["proposal"]}

    def accept_proposal(self, s:Session, accept:bool, accept_delivery:bool) -> Dict[str,Any]:
        if not s.proposal or s.proposal.get("price_kind") != "exact":
            s.state = "PRECIO PENDIENTE"
            return {"state":s.state,"payment_enabled":False,"reference":REFS["proposal"]}
        s.proposal["accepted"] = bool(accept)
        s.proposal["delivery_accepted"] = bool(accept_delivery)
        if accept and accept_delivery and not s.human_review_reason:
            s.state = "PAGO DISPONIBLE"
            return {"state":s.state,"payment_enabled":True,"reference":REFS["payment"]}
        s.state = "PROPUESTA DISPONIBLE"
        return {"state":s.state,"payment_enabled":False,"reference":REFS["payment"]}

    def start_payment(self, s:Session) -> Dict[str,Any]:
        if s.state != "PAGO DISPONIBLE" or not s.proposal.get("accepted") or not s.proposal.get("delivery_accepted"):
            return {"blocked":True,"state":s.state,"reason":"Pago QA no habilitado.","reference":REFS["payment"]}
        s.state = "PAGO PENDIENTE"
        s.payment = {"status":"PAGO PENDIENTE","simulation":True}
        return {"state":s.state,"order_created":False,"reference":REFS["payment"]}

    def resolve_payment(self, s:Session, outcome:str) -> Dict[str,Any]:
        mapping = {"confirmed":"PAGO CONFIRMADO","rejected":"PAGO RECHAZADO","cancelled":"PAGO CANCELADO","expired":"PAGO EXPIRADO"}
        if outcome not in mapping:
            raise ValueError("Unsupported QA payment outcome")
        target=mapping[outcome]
        s.payment={"status":target,"simulation":True}
        s.state=target
        if target != "PAGO CONFIRMADO":
            s.order=None; s.matrix=None
            return {"state":target,"order_created":False,"request_preserved":True,"reference":REFS["payment"]}
        return self._create_qa_order_and_matrix(s)

    def _create_qa_order_and_matrix(self,s:Session) -> Dict[str,Any]:
        order_id = "QA-ORDER-" + uuid.uuid5(uuid.NAMESPACE_DNS, s.session_id).hex[:10].upper()
        s.order={"order_id":order_id,"simulation":True,"price":s.proposal.get("price"),"currency":"QA-UNIT","delivery_window":s.proposal.get("delivery_window"),"visible_immediately":True}
        s.state="ORDEN CONFIRMADA"
        matrix = {
            "label":"MATRIZ INTERNA DE SOLICITUD Y PRODUCCIÓN — QA / NO PRODUCCIÓN",
            "status":QA_MATRIX_COMPLETE,
            "simulation":True,
            "order_id":order_id,
            "contact":{"name":s.registration.get("name"),"email":s.registration.get("email"),"email_verified_qa":s.registration.get("email_verified_qa")},
            "original_need":s.original_need,
            "confirmed_need":s.interpreted_need,
            "objective":s.objective,
            "functional_help":"Solicitud funcional ENDRIAN (QA)",
            "contracted_scope":s.orientation.get("preliminary_scope"),
            "includes":s.proposal.get("includes",[]),
            "excludes":s.proposal.get("excludes",[]),
            "functional_capabilities":s.orientation.get("capabilities",[]),
            "provided_information":dict(s.dimensioning),
            "pending_information":[],
            "systems":s.dimensioning.get("systems"),
            "scale":{"volume":s.dimensioning.get("volume"),"frequency":s.dimensioning.get("frequency"),"users":s.dimensioning.get("users")},
            "autonomy":s.dimensioning.get("autonomy"),
            "data_sensitivity":s.dimensioning.get("data_sensitivity"),
            "commercial_classification":s.classification,
            "price_paid_qa":s.proposal.get("price"),
            "delivery_window_accepted":s.proposal.get("delivery_window"),
            "acceptance_criteria":["Solicitud y alcance QA confirmados","Precio y plazo QA preservados sin cambio"],
            "alerts":[],"human_review":{"required":False,"reason":None},
            "traceability":{"conversation":s.session_id,"references":[REFS["matrix"],REFS["order"],REFS["payment"]]}
        }
        # QA completeness gate: no production semantics.
        required=[matrix["order_id"],matrix["contact"]["name"],matrix["confirmed_need"],matrix["contracted_scope"],matrix["price_paid_qa"],matrix["delivery_window_accepted"]]
        if not all(x is not None and x != "" for x in required):
            matrix["status"]=MATRIX_REVIEW
        s.matrix=matrix
        s.state=matrix["status"]
        s.trace.append({"event":"QA_ORDER_AND_MATRIX_CREATED","reference":REFS["matrix"]})
        return {"state":s.state,"order":s.order,"matrix":s.matrix,"email_sent":False,"email_note":"Correo real no construido; copia por correo solo representada como requisito futuro.","reference":REFS["order"]}

    def refund(self,s:Session, confirmed:bool=False) -> Dict[str,Any]:
        if not s.order:
            return {"blocked":True,"reason":"No existe orden QA pagada.","reference":REFS["payment"]}
        s.state="REEMBOLSO CONFIRMADO" if confirmed else "REEMBOLSO PENDIENTE"
        return {"state":s.state,"order_preserved":True,"simulation":True,"reference":REFS["payment"]}

    def recover(self,s:Session) -> Dict[str,Any]:
        if not s.registration.get("email_verified_qa"):
            return {"blocked":True,"reason":"Recuperación QA exige correo marcado como verificado.","reference":REFS["registration"]}
        return {"restored":True,"state":s.state,"conversation_preserved":len(s.conversation)>0,"dimensioning":dict(s.dimensioning),"proposal":dict(s.proposal),"reference":REFS["registration"]}

    def attachment_status(self) -> Dict[str,Any]:
        return {"enabled":False,"message":"En esta etapa no es necesario adjuntar archivos. ENDRIAN podrá solicitar documentación posteriormente si el caso lo requiere.","reference":REFS["attachments"]}

    def export_session(self,s:Session) -> Dict[str,Any]:
        return asdict(s)

if __name__ == "__main__":
    g=GuideAgentQA(); s=g.new_session("DEMO-QA")
    print(json.dumps(g.interpret(s,"Necesito un agente para organizar correos"),ensure_ascii=False,indent=2))
