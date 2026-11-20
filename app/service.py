from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import threading
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_ROOT = os.path.join(ROOT, "agent_guide")
CANDIDATE_DIR = os.path.join(AGENT_ROOT, "candidate")
CORE_DIR = os.path.join(AGENT_ROOT, "core_v0_1", "candidate")
for path in (CANDIDATE_DIR, CORE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from conversational_agent import ConversationalGuideQA  # type: ignore
from guide_agent import Session  # type: ignore

from .config import Settings
from .full_flow import (
    FIXTURE_ID,
    FIXTURE_INITIAL,
    FIXTURE_REPLY,
    FIXTURE_SCOPE,
    SPECIAL_FIXTURE_ID,
    SPECIAL_FIXTURE_INITIAL,
    SPECIAL_FIXTURE_SCOPE,
    QA_AMOUNT_CLP,
    QA_CANONICAL_CONTACT_EMAIL,
    QA_CANONICAL_CONTACT_NAME,
    QA_DELIVERY_WINDOW,
    QA_PLATFORM_LABEL,
    QA_PLATFORM_NOTICE,
    QA_DELIVERY_NOTICE,
    PREPAYMENT_CONDITIONS_VERSION,
    QA_TERMS_VERSION,
    QA_PRIVACY_VERSION,
    accept_product_change,
    build_email_preview,
    build_order_email_preview,
    build_identity,
    build_internal_matrix,
    build_quotation,
    build_solution_request,
    build_scope_version,
    current_quotation,
    current_solution_request,
    current_scope,
    ensure_flow,
    order_idempotency_key,
    payment_gate,
    payment_reference,
    set_state,
    utc_now,
    validate_client_output,
)
from .model_adapter import DeterministicModelAdapter, GeminiModelAdapter, OpenAIModelAdapter
from .model_signal_policy import DeterministicModelSignalPolicy
from .session_repository import SessionRepository

CONSUMED_MODEL_ACTIONS = {
    "ASK_MATERIAL_QUESTION", "UPDATE_INTERPRETATION", "EXTRACT_DIMENSIONING",
    "FLAG_HUMAN_REVIEW", "ANSWER_FUNCTIONAL_CLARIFICATION",
    "REFUSE_IMPLEMENTATION_DETAIL", "NO_OP",
}

with open(os.path.join(ROOT,"config","billing_country_codes.json"),"r",encoding="utf-8") as _country_file:
    BILLING_COUNTRY_CODES=set(json.load(_country_file))
with open(os.path.join(ROOT,"config","phone_country_prefixes.json"),"r",encoding="utf-8") as _phone_file:
    PHONE_PREFIXES={item["country_code"]:item["calling_code"] for item in json.load(_phone_file)}

def _structured_phone(country_code: str="", country_name: str="", calling_code: str="", national_number: str="") -> Optional[Dict[str, str]]:
    country_code=country_code.strip().upper(); country_name=country_name.strip(); calling_code=calling_code.strip(); national_number=re.sub(r"[\s().-]","",national_number.strip())
    if not any((country_code,country_name,calling_code,national_number)): return None
    if country_code not in PHONE_PREFIXES or PHONE_PREFIXES[country_code]!=calling_code or len(country_name)<2: raise ValueError("PHONE_COUNTRY_INVALID")
    if not re.fullmatch(r"\d{4,15}",national_number): raise ValueError("PHONE_NUMBER_INVALID")
    international=f"{calling_code}{national_number}"
    return {"country_code":country_code,"country_name":country_name,"calling_code":calling_code,"national_number":national_number,"international_number":international}

def _synthetic_email_error(email: str) -> Optional[str]:
    value=email.strip().casefold()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}",value): return "EMAIL_FORMAT_INVALID"
    return None


class GuideService:
    """Local QA integration shell for S0→S8 with SH as protected exit.

    The preserved conversational/core layers still interpret the user's need and build
    the functional orientation. The S-state machine, QA commercial simulation,
    PaymentGate, payment outcomes, order idempotency, email preview, matrix, tracking
    and recovery are deterministic local controls. No external provider is called.
    """

    def __init__(self, settings: Settings, repository: SessionRepository):
        self.settings = settings
        self.repository = repository
        self.runtime = ConversationalGuideQA()
        self._lock = threading.RLock()
        self.model_adapter = (
            OpenAIModelAdapter(settings.openai_model, settings.max_output_tokens) if settings.model_mode == "real"
            else GeminiModelAdapter(settings.gemini_model, settings.gemini_max_output_tokens) if settings.model_mode == "gemini"
            else DeterministicModelAdapter()
        )

    @staticmethod
    def session_fingerprint(session_id: str) -> str:
        return hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:12]

    def _default_app_meta(self, session_id: str) -> Dict[str, Any]:
        meta = {
            "ui_history": [], "ui_state": "conversation", "orientation_confirmed": False,
            "submitted_qa": False, "qa_ephemeral_registration": False, "model_trace": [],
        }
        ensure_flow(meta, session_id)
        return meta

    def _hydrate(self, session_id: str):
        snapshot = self.repository.get(session_id)
        if snapshot and snapshot.get("core_session"):
            core_data = dict(snapshot["core_session"])
            core_data["session_id"] = session_id
            self.runtime.core.sessions[session_id] = Session(**core_data)
            self.runtime.meta[session_id] = snapshot.get("candidate_meta") or {
                "pending_question": None, "registered": False, "orientation_confirmed": False,
                "history": [], "last_output": None, "model_mode": "DETERMINISTIC_QA_ADAPTER",
            }
            app_meta = snapshot.get("app_meta") or self._default_app_meta(session_id)
            ensure_flow(app_meta, session_id)
            return self.runtime.core.sessions[session_id], self.runtime.meta[session_id], app_meta
        s, m = self.runtime._session(session_id)
        app_meta = self._default_app_meta(session_id)
        self._persist(session_id, app_meta)
        return s, m, app_meta

    def _persist(self, session_id: str, app_meta: Dict[str, Any]):
        s, m = self.runtime._session(session_id)
        snapshot = {
            "core_session": self.runtime.core.export_session(s),
            "candidate_meta": m,
            "app_meta": app_meta,
        }
        current = self.repository.get(session_id)
        turn_count = (current or {}).get("_repo", {}).get("turn_count", 0)
        self.repository.save(session_id, snapshot, turn_count=turn_count)

    def _model_payload(self, s: Session, app_meta: Dict[str, Any], latest: str) -> Dict[str, Any]:
        return {
            "session_id": s.session_id, "state": s.state,
            "conversation": app_meta.get("ui_history", [])[-12:],
            "latest_user_message": latest,
            "known": {"interpreted_need": s.interpreted_need, "objective": s.objective, "dimensioning": s.dimensioning},
        }

    def _apply_model_pre_core(self, s: Session, proposal: Dict[str, Any] | None):
        if not proposal or proposal.get("action") != "EXTRACT_DIMENSIONING":
            return
        for key, value in (proposal.get("extracted") or {}).items():
            if value is not None:
                s.dimensioning[key] = value

    def _apply_model_interpretation(self, s: Session, proposal: Dict[str, Any] | None):
        if not proposal or proposal.get("action") != "UPDATE_INTERPRETATION":
            return
        if proposal.get("interpreted_need") and s.original_need:
            s.interpreted_need = proposal["interpreted_need"]
        if proposal.get("objective") and s.original_need:
            s.objective = proposal["objective"]

    def _record_model(self, app_meta: Dict[str, Any], result, proposal: Optional[Dict[str, Any]]):
        app_meta["model_trace"].append({
            "mode": self.settings.model_mode,
            "used_real_model": result.used_real_model,
            "valid": result.valid,
            "attempts": result.attempts,
            "fallback": bool(result.fallback_reason),
            "action": proposal.get("action") if proposal else None,
            "action_consumed": bool(proposal and proposal.get("action") in CONSUMED_MODEL_ACTIONS),
        })
        app_meta["model_trace"] = app_meta["model_trace"][-20:]

    def _orientation_summary(self, s: Session) -> Dict[str, Any]:
        orientation = s.orientation or {}
        return {
            "interpreted_need": orientation.get("interpreted_need") or s.interpreted_need or s.original_need,
            "objective": orientation.get("objective") or s.objective,
            "recommended": orientation.get("recommended") or "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
            "why": orientation.get("why") or "La necesidad quedó suficientemente delimitada para preparar una recomendación.",
            "capabilities": orientation.get("capabilities", []),
            "pending": orientation.get("pending", []),
            "preliminary_scope": orientation.get("preliminary_scope") or "Alcance funcional preliminar delimitado con la información disponible.",
        }

    @staticmethod
    def _confirmation_intent(message: str) -> str:
        normalized=" ".join(message.casefold().strip().split())
        normalized=re.sub(r"^[¿¡!?.]+|[¿¡!?.]+$", "", normalized).strip()
        if "estoy de acuerdo" in normalized and "resumen de mi solicitud" in normalized: return "CONFIRM_NO_CHANGES"
        if normalized in {"no", "no, está bien", "no está bien", "no, eso es todo", "no eso es todo", "está bien", "eso es todo"}: return "CONFIRM_NO_CHANGES"
        if normalized.startswith(("sí", "si")) or any(x in normalized for x in ("agregar", "cambiar", "corregir")): return "CONTINUE_CONVERSATION"
        return "UNRESOLVED"

    @staticmethod
    def _is_complete_supported_email_case(message: str) -> bool:
        """Recognize the bounded QA email case without depending on one exact sentence."""
        normalized=" ".join(message.casefold().split())
        groups=(
            ("correo", "correos"),
            ("cuatro", "4"),
            ("consulta", "consultas"),
            ("reclamo", "reclamos"),
            ("priorice", "priorizar", "prioridad"),
            ("seguimiento",),
            ("revise", "revisar", "revisión"),
            ("antes de envi", "sin envío autónomo"),
        )
        return all(any(term in normalized for term in alternatives) for alternatives in groups)

    @staticmethod
    def _prepare_supported_email_confirmation(flow: Dict[str, Any], app_meta: Dict[str, Any], s: Session) -> str:
        s.interpreted_need = FIXTURE_SCOPE["need_confirmed"]
        s.objective = FIXTURE_SCOPE["objective"]
        values={"context":"Equipo de cuatro personas gestiona consultas, reclamos y solicitudes por correo","volume":"80 correos/día","tools":["Correo"],"desired_timeline":QA_DELIVERY_WINDOW,"restrictions":"Respuestas bajo revisión humana; sin envío autónomo.","data_profile":"no_sensible","autonomy":"supervisada","integration_known":True}
        flow["fixture_id"]=FIXTURE_ID
        flow["dimensioning"]=deepcopy(values)
        flow["internal_dimensioning"]={"classification":"INTERNO / NO EXPORTABLE","values":deepcopy(values)}
        flow["orientation_summary"]={"interpreted_need":FIXTURE_SCOPE["need_confirmed"],"objective":FIXTURE_SCOPE["objective"],"recommended":"ENDRIAN Especializado","recommended_agent":"ENDRIAN Especializado","why":FIXTURE_SCOPE["why_fit"],"preliminary_scope":FIXTURE_SCOPE["scope_confirmed"],"deliverable_summary":FIXTURE_SCOPE["deliverable_summary"],"includes":FIXTURE_SCOPE["includes"],"excludes":FIXTURE_SCOPE["excludes"]}
        flow["client_output"]=validate_client_output(FIXTURE_SCOPE)
        app_meta["ui_state"]="needs_confirmation_chat"
        set_state(flow,"S3","SUPPORTED_EMAIL_CASE_INTERNAL_DIMENSIONING")
        set_state(flow,"S4","SUPPORTED_EMAIL_CASE_PROFESSIONAL_OUTPUT_READY")
        return f"Entonces, entiendo que necesitas lo siguiente: {FIXTURE_SCOPE['need_confirmed']}"

    @staticmethod
    def _proposal_addition_classification(addition: str) -> str:
        text=" ".join(addition.lower().strip().split())
        if not text: return "EMPTY"
        if text in {"mantener revisión humana en las respuestas.", "mantener revisión humana en las respuestas"}: return "NON_MATERIAL"
        material=("responder automáticamente", "responda automáticamente", "otra integración", "otro canal", "cambiar el agente", "cambiar el precio", "cambiar el plazo")
        return "MATERIAL" if any(x in text for x in material) else "UNCERTAIN"

    def _close_understanding(self, flow: Dict[str, Any], app_meta: Dict[str, Any], s: Session) -> str:
        build_scope_version(flow,flow.get("orientation_summary") or self._orientation_summary(s))
        request=build_solution_request(flow)
        if request.get("validation_result")=="RECLASSIFICATION_REQUIRED":
            app_meta["ui_state"]="product_conformity"
            return f"Por lo que definimos, corresponde {request['validated_agent_label']} y no la preferencia inicial. Revisa este cambio antes de continuar."
        if request.get("route")=="STANDARD":
            build_quotation(flow); app_meta["ui_state"]="request_summary"; set_state(flow,"S5","S4_REQUEST_VALIDATED_TO_S5_SUMMARY")
            return "Perfecto. Preparé el resumen de tu solicitud para que revises qué entendimos, qué servicio encaja con tu caso y qué incluiría el trabajo antes de continuar."
        flow["human_review"]={"pending":True,"reason":"El producto requiere revisión y cotización especial.","return_state":"S5"}
        app_meta["ui_state"]="request_summary"; set_state(flow,"S5","S4_SPECIAL_REQUEST_TO_S5_SUMMARY")
        return "Perfecto. Preparé el resumen de lo confirmado y de lo que requiere revisión."

    def confirm_product_change(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow["state"]!="S4" or not accept_product_change(flow):
                return self._blocked("PRODUCT_CONFORMITY_BLOCKED","No existe un cambio de producto pendiente de conformidad.",session_id,(s,m,app_meta))
            req=current_solution_request(flow) or {}
            if req.get("route")=="STANDARD":
                build_quotation(flow); app_meta["ui_state"]="request_summary"; set_state(flow,"S5","PRODUCT_CHANGE_ACCEPTED_TO_STANDARD_SUMMARY")
            else:
                flow["human_review"]={"pending":True,"reason":"El producto requiere revisión y cotización especial.","return_state":"S5"}; app_meta["ui_state"]="request_summary"; set_state(flow,"S5","PRODUCT_CHANGE_ACCEPTED_TO_SPECIAL_SUMMARY")
            self._persist(session_id,app_meta)
            return self._ok("PRODUCT_CHANGE_CONFIRMED","Cambio de producto confirmado.",session_id,(s,m,app_meta))

    def confirmation_action(self, session_id: str, action: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow.get("state")!="S4" or app_meta.get("ui_state")!="needs_confirmation_chat":
                return self._blocked("CONFIRMATION_ACTION_BLOCKED","La comprensión todavía no está lista para confirmar.",session_id,(s,m,app_meta))
            action=action.strip().lower()
            if action=="confirm":
                reply=self._close_understanding(flow,app_meta,s); event="SCOPE_CONFIRMED_VISIBLE_ACTION"
            elif action=="correct":
                flow["client_output"]=None; flow["orientation_summary"]=None
                app_meta["ui_state"]="scope_correction_chat"; set_state(flow,"S3","S4_VISIBLE_CORRECTION_TO_CHAT")
                reply="Claro. Cuéntame qué necesitas cambiar."; event="SCOPE_CORRECTION_VISIBLE_ACTION"
            else:
                return self._blocked("UNKNOWN_CONFIRMATION_ACTION","Acción no reconocida.",session_id,(s,m,app_meta))
            app_meta["ui_history"].append({"role":"assistant","text":reply}); app_meta["ui_history"]=app_meta["ui_history"][-40:]
            self._persist(session_id,app_meta)
            return self._ok(event,reply,session_id,(s,m,app_meta))

    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id)
            flow = ensure_flow(app_meta, session_id)
            correction_chat = flow["state"] == "S3" and app_meta.get("ui_state") == "scope_correction_chat"
            confirmation_chat = flow["state"] == "S4" and app_meta.get("ui_state") == "needs_confirmation_chat"
            if flow["state"] not in {"S0", "S1", "SH"} and not correction_chat and not confirmation_chat:
                return {
                    "event": "FLOW_CONTROL_REQUIRED", "state": s.state, "simulation": True,
                    "message": "Conservo el contexto. Continúa con el siguiente paso indicado.",
                    "summary": self.summary(session_id, hydrated=(s, m, app_meta)),
                }

            if flow["state"] == "S0":
                set_state(flow, "S1", "R01_NEED_STARTED")

            if confirmation_chat:
                evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]}); evidence["turns"].append({"role":"user","text":message})
                intent=self._confirmation_intent(message)
                if intent=="CONFIRM_NO_CHANGES": reply=self._close_understanding(flow,app_meta,s); event="SCOPE_CONFIRMED_SEMANTIC_EVENT"
                elif intent=="CONTINUE_CONVERSATION":
                    flow["client_output"]=None; flow["orientation_summary"]=None; app_meta["ui_state"]="scope_correction_chat"; set_state(flow,"S3","S4_SEMANTIC_CHANGE_TO_CHAT")
                    reply="Claro. Cuéntame qué necesitas agregar o cambiar."; event="SCOPE_CHANGE_SEMANTIC_EVENT"
                else:
                    reply="¿Necesitas agregar o cambiar algo? Puedes responder que está bien o contarme qué quieres modificar."; event="SCOPE_CONFIRMATION_CLARIFICATION"
                evidence["turns"].append({"role":"assistant","text":reply}); app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}]); app_meta["ui_history"]=app_meta["ui_history"][-40:]
                self._persist(session_id,app_meta); turn_count=self.repository.increment_turn(session_id)
                return {"ok":True,"event":event,"message":reply,"simulation":True,"turn_count":turn_count,"summary":self.summary(session_id,hydrated=(s,m,app_meta))}

            if correction_chat:
                evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]})
                evidence["turns"].append({"role":"user","text":message})
                supported=any(term in message.lower() for term in ("respond", "autom", "supervisi", "revis"))
                if not supported:
                    reply="Para ajustar este punto, dime si las respuestas deben quedar bajo revisión de tu equipo antes del envío."
                    evidence["turns"].append({"role":"assistant","text":reply}); app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}])
                    self._persist(session_id,app_meta)
                    return {"ok":True,"event":"DETERMINISTIC_CORRECTION_CLARIFICATION","message":reply,"simulation":True,"summary":self.summary(session_id,hydrated=(s,m,app_meta))}
                values={"context":"Equipo de cuatro personas gestiona consultas, reclamos y solicitudes por correo","volume":"80 correos/día","tools":["Correo"],"desired_timeline":QA_DELIVERY_WINDOW,"restrictions":"Respuestas bajo revisión humana; sin envío autónomo.","data_profile":"no_sensible","autonomy":"supervisada","integration_known":True,"correction_route":"SUPPORTED_AUTONOMY_REVIEW"}
                flow["dimensioning"]=deepcopy(values); flow["internal_dimensioning"]={"classification":"INTERNO / NO EXPORTABLE","values":deepcopy(values)}
                flow["orientation_summary"]={"interpreted_need":FIXTURE_SCOPE["need_confirmed"],"objective":FIXTURE_SCOPE["objective"],"recommended":"ENDRIAN Especializado","recommended_agent":"ENDRIAN Especializado","why":FIXTURE_SCOPE["why_fit"],"preliminary_scope":FIXTURE_SCOPE["scope_confirmed"],"deliverable_summary":FIXTURE_SCOPE["deliverable_summary"],"includes":FIXTURE_SCOPE["includes"],"excludes":FIXTURE_SCOPE["excludes"]}
                flow["client_output"]=validate_client_output(FIXTURE_SCOPE); app_meta["ui_state"]="needs_confirmation_chat"; set_state(flow,"S4","S3_CORRECTION_CHAT_TO_S4_PROFESSIONAL_OUTPUT")
                reply=f"Entonces, entiendo que necesitas lo siguiente: {FIXTURE_SCOPE['need_confirmed']}"
                evidence["turns"].append({"role":"assistant","text":reply}); app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}])
                self._persist(session_id,app_meta)
                return {"ok":True,"event":"PROFESSIONAL_CONFIRMATION_READY","message":reply,"simulation":True,"summary":self.summary(session_id,hydrated=(s,m,app_meta))}

            # Frozen deterministic QA fixture. It demonstrates natural input ->
            # professional output without a real model and never exports these turns.
            normalized = " ".join(message.split())
            # These deterministic QA scripts represent the FIRST turn(s) of a
            # conversation and jump straight to S3/S4. While SH (human review
            # pending) is open, they must not fire: that would skip
            # human_review_resolve entirely and leave human_review.pending
            # orphaned on an abandoned SH record.
            if flow["state"] != "SH" and normalized == " ".join(SPECIAL_FIXTURE_INITIAL.split()):
                self.runtime.handle_message(session_id,message); s,m=self.runtime._session(session_id)
                s.original_need=message; s.interpreted_need=SPECIAL_FIXTURE_SCOPE["need_confirmed"]; s.objective=SPECIAL_FIXTURE_SCOPE["objective"]
                flow["fixture_id"]=SPECIAL_FIXTURE_ID; flow["selected_agent"]="integral"
                flow["orientation_summary"]={"interpreted_need":SPECIAL_FIXTURE_SCOPE["need_confirmed"],"objective":SPECIAL_FIXTURE_SCOPE["objective"],"recommended":"ENDRIAN Integral","recommended_agent":"ENDRIAN Integral","why":SPECIAL_FIXTURE_SCOPE["why_fit"],"preliminary_scope":SPECIAL_FIXTURE_SCOPE["scope_confirmed"],"deliverable_summary":SPECIAL_FIXTURE_SCOPE["deliverable_summary"],"includes":SPECIAL_FIXTURE_SCOPE["includes"],"excludes":SPECIAL_FIXTURE_SCOPE["excludes"]}
                flow["client_output"]=validate_client_output(SPECIAL_FIXTURE_SCOPE); app_meta["ui_state"]="needs_confirmation_chat"
                set_state(flow,"S3","SPECIAL_FIXTURE_DEFINED"); set_state(flow,"S4","SPECIAL_FIXTURE_CONFIRMATION_READY")
                reply=(f"Entonces, entiendo que necesitas lo siguiente: {SPECIAL_FIXTURE_SCOPE['need_confirmed']} "
                    "Como intervienen varias áreas, responsables y dependencias todavía no validadas, esta solicitud necesita una revisión específica antes de cotizar.")
                evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]}); evidence["turns"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}])
                app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}]); app_meta["ui_history"]=app_meta["ui_history"][-40:]
                self._persist(session_id,app_meta); turn_count=self.repository.increment_turn(session_id)
                return {"ok":True,"event":"SPECIAL_FIXTURE_CONFIRMATION_READY","message":reply,"simulation":True,"turn_count":turn_count,"summary":self.summary(session_id,hydrated=(s,m,app_meta))}
            if flow["state"] != "SH" and self._is_complete_supported_email_case(message):
                self.runtime.handle_message(session_id, message)
                s, m = self.runtime._session(session_id)
                s.original_need = s.original_need or message
                evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]})
                evidence["turns"].append({"role":"user","text":message})
                reply=self._prepare_supported_email_confirmation(flow,app_meta,s)
                evidence["turns"].append({"role":"assistant","text":reply})
                app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}]); app_meta["ui_history"]=app_meta["ui_history"][-40:]
                self._persist(session_id,app_meta); turn_count=self.repository.increment_turn(session_id)
                return {"ok":True,"event":"SUPPORTED_EMAIL_DEFINITION_READY","message":reply,"simulation":True,"turn_count":turn_count,"model":{"mode":"deterministic","real_model_called":False,"structured_output_valid":True,"attempts":0},"summary":self.summary(session_id,hydrated=(s,m,app_meta))}
            if flow["state"] != "SH" and normalized in {" ".join(FIXTURE_INITIAL.split()), " ".join(FIXTURE_REPLY.split())}:
                core_result = self.runtime.handle_message(session_id, message)
                s, m = self.runtime._session(session_id)
                flow["fixture_id"] = FIXTURE_ID
                flow.setdefault("conversation_evidence", {"classification":"INTERNO / NO EXPORTABLE","turns":[]})["turns"].append({"role":"user","text":message})
                if normalized == " ".join(FIXTURE_INITIAL.split()):
                    reply = "Para definir bien el alcance: ¿aproximadamente cuántos correos reciben y prefieren que la solución prepare borradores para que el equipo los revise antes de enviarlos?"
                    set_state(flow, "S1", "QA_ESPECIALIZADO_01_MATERIAL_QUESTION")
                else:
                    s.original_need = s.original_need or FIXTURE_INITIAL
                    s.interpreted_need = FIXTURE_SCOPE["need_confirmed"]
                    s.objective = FIXTURE_SCOPE["objective"]
                    values={"context":"Equipo de cuatro personas gestiona consultas, reclamos y solicitudes por correo","volume":"80 correos/día","tools":["Correo"],"desired_timeline":QA_DELIVERY_WINDOW,"restrictions":"Respuestas bajo revisión humana; sin envío autónomo.","data_profile":"no_sensible","autonomy":"supervisada","integration_known":True}
                    flow["dimensioning"]=deepcopy(values); flow["internal_dimensioning"]={"classification":"INTERNO / NO EXPORTABLE","values":deepcopy(values)}
                    flow["orientation_summary"]={"interpreted_need":FIXTURE_SCOPE["need_confirmed"],"objective":FIXTURE_SCOPE["objective"],"recommended":"ENDRIAN Especializado","recommended_agent":"ENDRIAN Especializado","why":FIXTURE_SCOPE["why_fit"],"preliminary_scope":FIXTURE_SCOPE["scope_confirmed"],"deliverable_summary":FIXTURE_SCOPE["deliverable_summary"],"includes":FIXTURE_SCOPE["includes"],"excludes":FIXTURE_SCOPE["excludes"]}
                    flow["client_output"]=validate_client_output(FIXTURE_SCOPE)
                    reply = f"Entonces, entiendo que necesitas lo siguiente: {FIXTURE_SCOPE['need_confirmed']}"
                    app_meta["ui_state"] = "needs_confirmation_chat"
                    set_state(flow, "S3", "QA_ESPECIALIZADO_01_INTERNAL_DIMENSIONING")
                    set_state(flow, "S4", "QA_ESPECIALIZADO_01_PROFESSIONAL_OUTPUT_READY")
                flow["conversation_evidence"]["turns"].append({"role":"assistant","text":reply})
                app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}]); app_meta["ui_history"]=app_meta["ui_history"][-40:]
                self._persist(session_id,app_meta); turn_count=self.repository.increment_turn(session_id)
                return {"ok":True,"event":"FIXTURE_MATERIAL_QUESTION" if normalized==" ".join(FIXTURE_INITIAL.split()) else "FIXTURE_DEFINITION_READY",
                        "message":reply,"simulation":True,"turn_count":turn_count,"model":{"mode":"deterministic","real_model_called":False,"structured_output_valid":True,"attempts":0},
                        "summary":self.summary(session_id,hydrated=(s,m,app_meta))}

            if flow["state"] != "SH" and not self.settings.real_model_enabled and isinstance(self.model_adapter, DeterministicModelAdapter):
                reply=("Este simulador QA solo completa el recorrido con los guiones de prueba autorizados. "
                       "Este mensaje no generó una comprensión ni un resumen. Utiliza el caso de correos "
                       "indicado en la guía de prueba o inicia una nueva conversación.")
                app_meta["ui_state"]="deterministic_script_required"
                set_state(flow,"S1","DETERMINISTIC_SCRIPT_REQUIRED")
                app_meta["ui_history"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}])
                app_meta["ui_history"]=app_meta["ui_history"][-40:]
                evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]})
                evidence["turns"].extend([{"role":"user","text":message},{"role":"assistant","text":reply}])
                evidence["turns"]=evidence["turns"][-40:]
                self._persist(session_id,app_meta); turn_count=self.repository.increment_turn(session_id)
                return {"ok":True,"event":"DETERMINISTIC_SCRIPT_REQUIRED","message":reply,"simulation":True,"turn_count":turn_count,
                        "model":{"mode":"deterministic","real_model_called":False,"structured_output_valid":True,"attempts":0},
                        "summary":self.summary(session_id,hydrated=(s,m,app_meta))}

            model_result = self.model_adapter.interpret(self._model_payload(s, app_meta, message))
            proposal = model_result.proposal if model_result.valid else None
            self._apply_model_pre_core(s, proposal)
            core_result = self.runtime.handle_message(session_id, message)
            s, m = self.runtime._session(session_id)
            self._apply_model_interpretation(s, proposal)

            if proposal and proposal.get("action") == "FLAG_HUMAN_REVIEW":
                result = DeterministicModelSignalPolicy.apply_human_review(s, proposal)
                flow["human_review"] = {"pending": True, "reason": s.human_review_reason, "return_state": "S3"}
                set_state(flow, "SH", "MODEL_SIGNAL_TO_SH")
            elif s.state == "REVISIÓN HUMANA REQUERIDA":
                result = {
                    "event": "HUMAN_REVIEW_REQUIRED", "state": s.state, "simulation": True,
                    "message": "Tu caso necesita una revisión más específica. Conservaremos lo conversado y el pago permanecerá bloqueado.",
                    "data": {"reason": s.human_review_reason},
                }
                flow["human_review"] = {"pending": True, "reason": s.human_review_reason, "return_state": "S3"}
                set_state(flow, "SH", "CORE_RISK_TO_SH")
            else:
                result = dict(core_result)
                if core_result.get("event") in {"PRELIMINARY_UNDERSTANDING", "REGISTRATION_REQUIRED"}:
                    app_meta["ui_state"] = "preliminary"
                    set_state(flow, "S1", "PRELIMINARY_UNDERSTANDING_READY")
                    if core_result.get("event") == "PRELIMINARY_UNDERSTANDING":
                        need = (s.interpreted_need or "").strip()
                        objective = (s.objective or "").strip()
                        if need:
                            result["message"] = (
                                f"Entendí lo siguiente: {need}" + (f" {objective}" if objective else "") +
                                " Cuéntame un poco más (por ejemplo volumen, canal o urgencia) para afinarlo, "
                                "o escribe \"continuar\" si esto ya refleja lo que necesitas."
                            )
                        else:
                            result["message"] = "Preparé una comprensión preliminar de tu necesidad. Revísala para continuar."
                    # REGISTRATION_REQUIRED already carries its own actionable
                    # message (what to provide: name, email, consent) — the
                    # generic placeholder above was silently replacing it,
                    # leaving the user with no visible next step.
                elif core_result.get("event") == "CLARIFICATION_REQUIRED":
                    set_state(flow, "S1", "MATERIAL_CLARIFICATION_REQUIRED")
                if proposal:
                    action = proposal.get("action")
                    if action == "ASK_MATERIAL_QUESTION" and proposal.get("question") and result.get("event") == "CLARIFICATION_REQUIRED":
                        result["message"] = proposal["question"]
                    elif action == "ANSWER_FUNCTIONAL_CLARIFICATION" and proposal.get("functional_answer"):
                        result["message"] = proposal["functional_answer"]
                    elif action == "REFUSE_IMPLEMENTATION_DETAIL" and proposal.get("functional_answer"):
                        result["message"] = proposal["functional_answer"]

            self._record_model(app_meta, model_result, proposal)
            app_meta["ui_history"].append({"role": "user", "text": message})
            app_meta["ui_history"].append({"role": "assistant", "text": result.get("message", "")})
            app_meta["ui_history"] = app_meta["ui_history"][-40:]
            evidence=flow.setdefault("conversation_evidence",{"classification":"INTERNO / NO EXPORTABLE","turns":[]})
            evidence["turns"].extend([{"role":"user","text":message},{"role":"assistant","text":result.get("message","")}]); evidence["turns"]=evidence["turns"][-40:]
            self._persist(session_id, app_meta)
            turn_count = self.repository.increment_turn(session_id)
            result["turn_count"] = turn_count
            result["model"] = {"mode": self.settings.model_mode, "real_model_called": model_result.used_real_model, "structured_output_valid": model_result.valid, "attempts": model_result.attempts}
            result["summary"] = self.summary(session_id, hydrated=(s, m, app_meta))
            return result

    def confirm_understanding(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S1" or not s.original_need:
                return self._blocked("UNDERSTANDING_CONFIRM_BLOCKED", "La comprensión preliminar todavía no está lista.", session_id, (s,m,app_meta))
            app_meta["ui_state"] = "dimensioning"
            set_state(flow, "S3", "S1_TO_S3_DEFINITION_STARTED")
            self._persist(session_id, app_meta)
            return self._ok("DEFINITION_QA_READY", "Continúa con la definición de tu necesidad. Aún no existe precio ni cotización.", session_id, (s,m,app_meta))

    def complete_registration(self, session_id: str, name: str, email: str, data_processing: bool=False, operational_comms: bool=False, marketing: bool=False, phone: str="", country_code: str="CL", country_name: str="Chile", phone_country_code: str="", phone_country_name: str="", phone_calling_code: str="", phone_national_number: str="") -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S2":
                return self._blocked("REGISTRATION_STATE_BLOCKED", "Los datos de contacto todavía no están disponibles.", session_id, (s,m,app_meta))
            if not current_scope(flow): return self._blocked("SCOPE_REQUIRED_FOR_IDENTIFICATION","Confirma primero el alcance.",session_id,(s,m,app_meta))
            if len(name.strip())<2 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ .'-]+",name.strip()):
                return self._blocked("SYNTHETIC_NAME_REQUIRED","Revisa el nombre completo ingresado.",session_id,(s,m,app_meta))
            email_error=_synthetic_email_error(email)
            if email_error=="EMAIL_FORMAT_INVALID": return self._blocked(email_error,"Revisa el formato del correo.",session_id,(s,m,app_meta))
            country_code=country_code.strip().upper(); country_name=country_name.strip()
            try: structured_phone=_structured_phone(phone_country_code,phone_country_name,phone_calling_code,phone_national_number)
            except ValueError as exc:
                event=str(exc); message="Completa un prefijo y número válidos, o borra ambos para omitir el teléfono."
                return self._blocked(event,message,session_id,(s,m,app_meta))
            if country_code not in BILLING_COUNTRY_CODES or len(country_name)<2: return self._blocked("BILLING_COUNTRY_REQUIRED","Selecciona tu país o territorio.",session_id,(s,m,app_meta))
            previous=flow.get("qa_identity") or {}; identity = build_identity(session_id,name.strip(),email.strip().lower(),structured_phone,country_code,country_name); flow["qa_identity"] = identity
            identity["contact_confirmed_at"]=utc_now().replace(microsecond=0).isoformat(); identity["email_verification_status"]="SIMULATED_VERIFIED"; identity["email_verified_qa"]=True
            if previous.get("email") and previous.get("email")!=identity["email"]: identity["previous_email_verification_invalidated"]=True
            m["registered"] = False; app_meta["qa_ephemeral_registration"] = True
            req=current_solution_request(flow) or {}; quote=current_quotation(flow)
            if req.get("route")=="SPECIAL_REVIEW" and not quote:
                app_meta["ui_state"]="special_review_waiting"; set_state(flow,"SH","S2_CONTACT_TO_SPECIAL_REVIEW")
                self._persist(session_id,app_meta); return self._ok("SPECIAL_REVIEW_SUBMITTED","Tu solicitud fue enviada para revisión.",session_id,(s,m,app_meta))
            app_meta["ui_state"] = "contracting"; flow["microstate"]="S5.CONTRACT-DATA"; set_state(flow, "S5", "S2_CONTACT_TO_S5_PREPAYMENT")
            self._persist(session_id, app_meta)
            return self._ok("PREPAYMENT_DATA_READY", "Revisa los datos antes de continuar al pago.", session_id, (s,m,app_meta))

    def edit_contact(self, session_id: str, name: str, email: str, phone: str="", country_code: str="CL", country_name: str="Chile", phone_country_code: str="", phone_country_name: str="", phone_calling_code: str="", phone_national_number: str="") -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow["state"]!="S5" or flow.get("microstate")!="S5.CONTRACT-DATA": return self._blocked("CONTACT_EDIT_BLOCKED","Los datos no están disponibles para edición.",session_id,(s,m,app_meta))
            name=name.strip(); email=email.strip().casefold()
            if len(name)<2 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ .'-]+",name): return self._blocked("SYNTHETIC_NAME_REQUIRED","Revisa el nombre completo ingresado.",session_id,(s,m,app_meta))
            email_error=_synthetic_email_error(email)
            if email_error=="EMAIL_FORMAT_INVALID": return self._blocked(email_error,"Revisa el formato del correo.",session_id,(s,m,app_meta))
            try: structured_phone=_structured_phone(phone_country_code,phone_country_name,phone_calling_code,phone_national_number)
            except ValueError as exc:
                event=str(exc); message="Completa un prefijo y número válidos, o borra ambos para omitir el teléfono."
                return self._blocked(event,message,session_id,(s,m,app_meta))
            country_code=country_code.strip().upper(); country_name=country_name.strip()
            if country_code not in BILLING_COUNTRY_CODES or len(country_name)<2: return self._blocked("BILLING_COUNTRY_REQUIRED","Selecciona tu país o territorio.",session_id,(s,m,app_meta))
            identity=flow.get("qa_identity") or build_identity(session_id); email_changed=identity.get("email")!=email; country_changed=(identity.get("billing_country") or {}).get("country_code")!=country_code; material_contact_changed=email_changed or identity.get("name")!=name or country_changed
            identity.update({"name":name,"email":email,"phone":structured_phone,"billing_country":{"country_code":country_code,"country_name":country_name},"contact_confirmed_at":utc_now().replace(microsecond=0).isoformat(),"email_verification_status":"SIMULATED_VERIFIED","email_verified_qa":True})
            if email_changed: identity["previous_email_verification_invalidated"]=True
            flow["qa_identity"]=identity
            if material_contact_changed: flow["contracting_data"]=None
            else:
                data=flow.get("contracting_data") or {}; data["phone"]=deepcopy(structured_phone); flow["contracting_data"]=data
            self._persist(session_id,app_meta); return self._ok("CONTACT_UPDATED","Datos actualizados.",session_id,(s,m,app_meta))

    def dimension(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S3":
                return self._blocked("DIMENSIONING_STATE_BLOCKED", "El dimensionamiento solo puede confirmarse desde S3.", session_id, (s,m,app_meta))
            dim = {
                "context": str(payload.get("context", "")).strip(),
                "volume": str(payload.get("volume", "")).strip(),
                "tools": [str(x).strip() for x in (payload.get("tools") or []) if str(x).strip()][:8],
                "desired_timeline": str(payload.get("desired_timeline", "")).strip(),
                "restrictions": str(payload.get("restrictions", "")).strip(),
                "data_profile": payload.get("data_profile", "no_sensible"),
                "autonomy": payload.get("autonomy", "supervisada"),
                "integration_known": bool(payload.get("integration_known", True)),
            }
            if not dim["context"] or not dim["volume"] or not dim["desired_timeline"]:
                flow["dimensioning"] = dim; self._persist(session_id, app_meta)
                return self._blocked("DIMENSIONING_INCOMPLETE", "Falta información para continuar.", session_id, (s,m,app_meta))
            flow["dimensioning"] = dim
            flow["internal_dimensioning"]={"classification":"INTERNO / NO EXPORTABLE","values":deepcopy(dim)}
            core_kwargs = {
                "volume": dim["volume"], "systems": dim["tools"],
                "data_sensitivity": "sensible" if dim["data_profile"] == "sensible" else "no sensible",
                "autonomy": "alta" if dim["autonomy"] == "alta" else "supervisada",
                "integration_type": "desconocida" if not dim["integration_known"] else "conocida",
            }
            d = self.runtime.core.dimension(s, **core_kwargs)
            if s.state == "REVISIÓN HUMANA REQUERIDA":
                flow["human_review"] = {"pending": True, "reason": s.human_review_reason, "return_state": "S3"}
                app_meta["ui_state"] = "human_review"; set_state(flow, "SH", "S3_RISK_TO_SH")
                self._persist(session_id, app_meta)
                return self._ok("HUMAN_REVIEW_REQUIRED", "Necesitamos revisar esta solicitud antes de continuar.", session_id, (s,m,app_meta))
            if flow.get("fixture_id")==FIXTURE_ID:
                flow["selected_agent"]="especializado"
                flow["orientation_summary"]={"interpreted_need":FIXTURE_SCOPE["need_confirmed"],"objective":FIXTURE_SCOPE["objective"],"recommended":"ENDRIAN Especializado","recommended_agent":"ENDRIAN Especializado","why":FIXTURE_SCOPE["why_fit"],"preliminary_scope":FIXTURE_SCOPE["scope_confirmed"],"deliverable_summary":FIXTURE_SCOPE["deliverable_summary"],"includes":FIXTURE_SCOPE["includes"],"excludes":FIXTURE_SCOPE["excludes"]}
            else: flow["orientation_summary"] = self._orientation_summary(s)
            app_meta["ui_state"] = "route"; set_state(flow, "S4", "S3_CONFIRMED_TO_S4")
            self._persist(session_id, app_meta)
            return self._ok("ORIENTATION_READY", "La información está lista para revisión.", session_id, (s,m,app_meta))

    def orientation_action(self, session_id: str, action: str, correction: str="") -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S4":
                return self._blocked("ORIENTATION_ACTION_BLOCKED", "Las acciones de orientación solo están disponibles en S4.", session_id, (s,m,app_meta))
            action = action.lower().strip()
            if action == "confirm":
                if not flow.get("client_output"):
                    return self._blocked("PROFESSIONAL_OUTPUT_REQUIRED", "La salida profesional todavía no está disponible.", session_id, (s,m,app_meta))
                build_scope_version(flow,flow.get("orientation_summary") or self._orientation_summary(s))
                flow["qa_identity"]=build_identity(session_id)
                app_meta["orientation_confirmed"] = True; app_meta["ui_state"] = "registration"; set_state(flow, "S2", "S4_SCOPE_CONFIRMED_TO_S2")
            elif action in {"material_correction","request_correction"}:
                flow["orientation_summary"]=None; flow["client_output"]=None
                app_meta["ui_state"] = "scope_correction_chat"; set_state(flow, "S3", "S4_CORRECTION_REQUESTED_TO_CHAT")
            elif action == "minor_correction":
                if not correction.strip():
                    return self._blocked("MINOR_CORRECTION_EMPTY", "Describe la corrección menor para actualizar el resumen.", session_id, (s,m,app_meta))
                self.runtime.core.correct_orientation(s, correction.strip(), material=False)
                summary = flow.get("orientation_summary") or self._orientation_summary(s)
                summary["minor_correction"] = correction.strip(); summary["updated_summary"] = f"{summary.get('interpreted_need','')} | Ajuste menor: {correction.strip()}"
                flow["orientation_summary"] = summary; app_meta["ui_state"] = "route"; set_state(flow, "S4", "S4_MINOR_CORRECTION_STAYS_S4")
            elif action == "review":
                s.state = "REVISIÓN HUMANA REQUERIDA"; s.human_review_reason = "REVISIÓN SOLICITADA"
                flow["human_review"] = {"pending": True, "reason": s.human_review_reason, "return_state": "S4"}
                app_meta["ui_state"] = "human_review"; set_state(flow, "SH", "S4_REVIEW_TO_SH")
            else:
                return self._blocked("UNKNOWN_ORIENTATION_ACTION", "Acción de orientación no reconocida.", session_id, (s,m,app_meta))
            self._persist(session_id, app_meta)
            return self._ok("ORIENTATION_ACTION_APPLIED", "", session_id, (s,m,app_meta))

    def proposal_action(self, session_id: str, action: str, accept_scope: bool=False, accept_delivery: bool=False, addition: str="") -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S5":
                return self._blocked("QUOTATION_ACTION_BLOCKED", "La cotización solo puede gestionarse desde S5.", session_id, (s,m,app_meta))
            quote=current_quotation(flow); request=current_solution_request(flow) or {}
            action = action.lower().strip()
            if action in {"accept","continue"}:
                if request.get("route")!="STANDARD" or not quote:
                    return self._blocked("STANDARD_ROUTE_REQUIRED","Esta solicitud requiere revisión antes de continuar.",session_id,(s,m,app_meta))
                if quote.get("status")!="ISSUED" or quote.get("force_expired_qa"):
                    return self._blocked("QUOTATION_NOT_CONTRACTABLE","La cotización no está vigente para continuar.",session_id,(s,m,app_meta))
                app_meta["ui_state"]="contact"; set_state(flow,"S2","S5_SUMMARY_TO_S2_CONTACT")
            elif action=="send_for_review":
                if request.get("route")!="SPECIAL_REVIEW": return self._blocked("SPECIAL_ROUTE_REQUIRED","La solicitud no requiere revisión especial.",session_id,(s,m,app_meta))
                app_meta["ui_state"]="contact"; set_state(flow,"S2","S5_SPECIAL_SUMMARY_TO_S2_CONTACT")
            elif action == "revalidate":
                special_review=request.get("route")=="SPECIAL_REVIEW"
                if special_review and not (quote and quote.get("reviewed")):
                    return self._blocked("SPECIAL_REVIEW_REQUIRED","Esta solicitud requiere revisión antes de recotizar.",session_id,(s,m,app_meta))
                if quote: quote["status"]="EXPIRED"; quote["microstate"]="S5.Q-EXPIRED"
                try:
                    if special_review:
                        build_quotation(flow,reviewed=True,actor=quote.get("review_actor"),reviewed_amount=quote.get("amount"),reviewed_delivery=quote.get("delivery_window"))
                    else:
                        build_quotation(flow)
                except ValueError as exc:
                    return self._blocked("QUOTATION_REVALIDATION_BLOCKED",str(exc),session_id,(s,m,app_meta))
                app_meta["ui_state"]="request_summary"
            elif action in {"material_correction","minor_correction","modify_scope","return_to_chat"}:
                if quote: quote["status"]="SUPERSEDED"; quote["microstate"]="S5.Q-SUPERSEDED"
                request["status"]="SUPERSEDED"; request["workflow_status"]="SUPERSEDED"; flow["workflow_status"]="SUPERSEDED"; flow["microstate"]="S5.Q-SUPERSEDED"
                flow["payment_qa"]={"status":"NO_INICIADO","simulation":True}; flow["contracting_data"]=None; flow["client_output"]=None; flow["orientation_summary"]=None
                scope=current_scope(flow)
                if scope: scope["status"]="SUPERSEDED"
                flow["current_scope_version_id"]=None; flow["current_solution_request_version_id"]=None; flow["current_quotation_ref"]=None
                s.state="DIMENSIONAMIENTO INCOMPLETO"; app_meta["ui_state"]="scope_correction_chat"; set_state(flow,"S3","S5_SCOPE_CHANGE_TO_S3",superseded=quote.get("quotation_ref") if quote else None)
            elif action == "no_continue":
                flow["microstate"]="S5.Q-ISSUED"; app_meta["ui_state"]="quotation"
            elif action == "review":
                flow["human_review"] = {"pending": True, "reason": "REVISIÓN SOLICITADA", "return_state": "S4"}; app_meta["ui_state"] = "human_review"; set_state(flow, "SH", "S5_REVIEW_TO_SH")
            else:
                return self._blocked("UNKNOWN_QUOTATION_ACTION", "Acción de cotización no reconocida.", session_id, (s,m,app_meta))
            self._persist(session_id, app_meta)
            return self._ok("QUOTATION_ACTION_APPLIED", "", session_id, (s,m,app_meta))

    def complete_contracting(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); quote=current_quotation(flow)
            if flow["state"]!="S5" or flow.get("microstate")!="S5.CONTRACT-DATA" or not quote or quote.get("status")!="ISSUED":
                return self._blocked("CONTRACTING_STATE_BLOCKED","Revisa primero una cotización vigente.",session_id,(s,m,app_meta))
            identity=flow.get("qa_identity") or {}; phone=deepcopy(identity.get("phone")); terms_accepted=bool(payload.get("contract_terms_accepted")); privacy_accepted=bool(payload.get("privacy_authorization_accepted"))
            now=utc_now().replace(microsecond=0).isoformat(); request=current_solution_request(flow) or {}
            common_refs={"scope_version_id":quote.get("scope_version_id"),"solution_request_version_id":quote.get("solution_request_version_id"),"quotation_id":quote.get("quotation_id"),"quotation_version":quote.get("quotation_version"),"quotation_ref":quote.get("quotation_ref"),"conditions_version":PREPAYMENT_CONDITIONS_VERSION,"terms_version":QA_TERMS_VERSION,"privacy_notice_version":QA_PRIVACY_VERSION}
            data={"name":identity.get("name"),"email":identity.get("email"),"phone":phone,"billing_country":deepcopy(identity.get("billing_country")),"contract_terms_accepted":terms_accepted,"privacy_authorization_accepted":privacy_accepted,
                  **common_refs,"contract_terms_acceptance":{"accepted":terms_accepted,"accepted_at":now if terms_accepted else None,"scope_version_id":quote.get("scope_version_id"),"solution_request_version_id":request.get("solution_request_version_id"),"quotation_id":quote.get("quotation_id"),"quotation_version":quote.get("quotation_version"),"quotation_ref":quote.get("quotation_ref"),"conditions_version":PREPAYMENT_CONDITIONS_VERSION,"terms_version":QA_TERMS_VERSION},
                  "privacy_acceptance":{"accepted":privacy_accepted,"accepted_at":now if privacy_accepted else None,"scope_version_id":quote.get("scope_version_id"),"solution_request_version_id":request.get("solution_request_version_id"),"quotation_id":quote.get("quotation_id"),"quotation_version":quote.get("quotation_version"),"quotation_ref":quote.get("quotation_ref"),"privacy_notice_version":QA_PRIVACY_VERSION},"simulation":True}
            if not (terms_accepted and privacy_accepted):
                flow["contracting_data"]=data; self._persist(session_id,app_meta)
                return self._blocked("PREPAYMENT_CONFIRMATION_REQUIRED","Confirma ambas opciones para continuar.",session_id,(s,m,app_meta))
            r=self.runtime.core.register(s,name=identity["name"],email=identity["email"],data_processing=True,operational_comms=True,marketing=False,email_verified_qa=True)
            if not r.get("ok"): return self._blocked("REGISTRATION_CORE_BLOCKED","Revisa los datos antes de continuar.",session_id,(s,m,app_meta))
            m["registered"]=True; identity["consents"]={"contract_terms":True,"data_processing":True,"marketing":False}
            flow["contracting_data"]=data
            quote["status"]="ACCEPTED"; quote["delivery_window_accepted"]=True; quote["accepted_at"]=utc_now().replace(microsecond=0).isoformat(); quote["microstate"]="S5.Q-ACCEPTED"
            gate=payment_gate(flow)
            if not gate["payment_enabled"]:
                self._persist(session_id,app_meta); out=self._blocked("PAYMENT_GATE_FALSE","El pago todavía no está disponible.",session_id,(s,m,app_meta)); out["payment_gate"]=gate; return out
            flow["payment_qa"]={"status":"DISPONIBLE","simulation":True}; app_meta["ui_state"]="payment"; set_state(flow,"S6","PAYMENT_GATE_TRUE_TO_S6")
            self._persist(session_id,app_meta); return self._ok("PREPAYMENT_READY","La solicitud está lista para preparar el pago.",session_id,(s,m,app_meta))

    def create_or_reuse_payment_attempt(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id); gate = payment_gate(flow)
            if flow["state"] != "S6" or not gate["payment_enabled"]:
                out = self._blocked("PAYMENT_START_BLOCKED", "El pago todavía no está habilitado.", session_id, (s,m,app_meta)); out["payment_gate"] = gate; return out
            status = (flow.get("payment_qa") or {}).get("status")
            if status in {"PENDIENTE","CONFIRMADO"}:
                return self._ok("PAYMENT_ATTEMPT_REUSED", "El proceso de pago ya está preparado.", session_id, (s,m,app_meta), reused=True, payment_gate=gate)
            q=current_quotation(flow) or {}
            req=current_solution_request(flow) or {}
            flow["payment_qa"] = {"status":"PENDIENTE","reference":payment_reference(flow),"amount":q.get("amount"),"currency":q.get("currency"),
                                  "scope_version_id":q.get("scope_version_id"),"quotation_id":q.get("quotation_id"),
                                  "solution_request_version_id":q.get("solution_request_version_id"),"quotation_version":q.get("quotation_version"),"quotation_ref":q.get("quotation_ref"),
                                  "service_id":req.get("validated_agent"),"service_label":req.get("service_label"),"solution_title":req.get("request_title"),
                                  "platform_label":req.get("platform_label") or QA_PLATFORM_LABEL,"delivery_window":q.get("delivery_window"),
                                  "provider":None,"checkout_url":None,"started_at":utc_now().replace(microsecond=0).isoformat(),"simulation":True}
            app_meta["ui_state"]="checkout_simulation"
            self._persist(session_id, app_meta)
            return self._ok("PAYMENT_ATTEMPT_CREATED", "El proceso de pago está preparado. En este entorno de prueba no se realizará ninguna operación real.", session_id, (s,m,app_meta), reused=False, payment_gate=gate)

    def payment_start(self, session_id: str) -> Dict[str, Any]:
        """Compatibility endpoint alias for the provider-neutral idempotent operation."""
        return self.create_or_reuse_payment_attempt(session_id)

    def payment_return(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); payment=flow.get("payment_qa") or {}
            if flow.get("state")!="S6" or payment.get("status")!="PENDIENTE":
                return self._blocked("PAYMENT_RETURN_BLOCKED","No existe un pago pendiente para verificar.",session_id,(s,m,app_meta))
            app_meta["ui_state"]="payment_verifying"; payment["returned_at"]=utc_now().replace(microsecond=0).isoformat()
            self._persist(session_id,app_meta)
            return self._ok("PAYMENT_RETURNED_PENDING","Estamos verificando tu pago.",session_id,(s,m,app_meta))

    def qa_payment_resolve(self, session_id: str, reference: str, outcome: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); payment=flow.get("payment_qa") or {}
            if not payment.get("reference") or reference!=payment.get("reference"):
                return self._blocked("PAYMENT_REFERENCE_INVALID","La referencia de pago no es válida.",session_id,(s,m,app_meta))
            return self.payment_resolve(session_id,outcome)

    def qa_special_review_resolve(self, session_id: str, actor: str, decision: str, amount: Optional[int]=None, delivery_window: str="") -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); req=current_solution_request(flow)
            if not req or req.get("route")!="SPECIAL_REVIEW" or flow["state"]!="SH":
                return self._blocked("SPECIAL_REVIEW_STATE_BLOCKED","No existe una revisión especial pendiente.",session_id,(s,m,app_meta))
            if req.get("validation_result") in {"BLOCKED_UNAUTHORIZED","PENDING_AUTHORITY"}:
                return self._blocked("SPECIAL_REVIEW_CANNOT_OVERRIDE_AUTHORITY","La revisión no puede levantar una prohibición o autoridad pendiente.",session_id,(s,m,app_meta))
            decision=decision.lower().strip(); req["review"]={"actor":actor,"decision":decision,"at":utc_now().replace(microsecond=0).isoformat(),"reviewed_versions":{"scope_version_id":req.get("scope_version_id"),"solution_request_version_id":req.get("solution_request_version_id")}}
            if decision=="rejected":
                req["workflow_status"]="VALIDATION_BLOCKED"; req["validation_result"]="RECLASSIFICATION_REQUIRED"; req["validation_causes"]=["SPECIAL_REVIEW_REJECTED"]
                flow["workflow_status"]=req["workflow_status"]; flow["validation_result"]=req["validation_result"]; flow["validation_causes"]=deepcopy(req["validation_causes"]); flow["human_review"]={"pending":False,"reason":"Solicitud no cotizada en revisión.","return_state":None}
                # Leave SH instead of leaving the flow stuck there with pending
                # already cleared: route back to definition so the client can
                # redefine the scope, the same destination S5's own
                # "modify_scope" action uses for a blocked request.
                s.state="DIMENSIONAMIENTO INCOMPLETO"; app_meta["ui_state"]="scope_correction_chat"
                set_state(flow,"S3","SPECIAL_REVIEW_REJECTED_TO_S3")
                self._persist(session_id,app_meta)
                return self._ok("SPECIAL_REVIEW_REJECTED","La solicitud no fue cotizada.",session_id,(s,m,app_meta))
            if decision!="approved": return self._blocked("SPECIAL_REVIEW_DECISION_INVALID","Decisión de revisión no reconocida.",session_id,(s,m,app_meta))
            req["workflow_status"]="VALIDATED_FOR_QUOTATION"; req["validation_result"]="VALIDATED_FOR_QUOTATION"; req["validation_causes"]=[]
            flow["workflow_status"]="VALIDATED_FOR_QUOTATION"; flow["validation_result"]="VALIDATED_FOR_QUOTATION"; flow["validation_causes"]=[]; flow["human_review"]={"pending":False,"reason":None,"return_state":None}
            build_quotation(flow,reviewed=True,actor=actor,reviewed_amount=amount,reviewed_delivery=delivery_window); flow["microstate"]="S5.CONTRACT-DATA"; app_meta["ui_state"]="contracting"; set_state(flow,"S5","SPECIAL_REVIEW_QUOTED_TO_S5_PREPAYMENT")
            self._persist(session_id,app_meta); return self._ok("SPECIAL_REVIEW_QUOTATION_ISSUED","Cotización revisada disponible.",session_id,(s,m,app_meta))

    def payment_resolve(self, session_id: str, outcome: str) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow = ensure_flow(app_meta, session_id)
            if flow["state"] != "S6":
                return self._blocked("PAYMENT_RESOLVE_BLOCKED", "Los resultados de pago solo pueden simularse desde S6.", session_id, (s,m,app_meta))
            payment = flow.get("payment_qa") or {}; outcome = outcome.lower().strip()
            mapping = {"pending":"PENDIENTE", "confirmed":"CONFIRMADO", "rejected":"RECHAZADO", "cancelled":"CANCELADO", "expired":"EXPIRADO"}
            if outcome not in mapping:
                return self._blocked("PAYMENT_OUTCOME_UNKNOWN", "No reconocimos el resultado del pago.", session_id, (s,m,app_meta))
            if outcome == "confirmed" and payment.get("status") != "PENDIENTE":
                return self._blocked("PAYMENT_CONFIRMATION_BLOCKED", "Solo un intento pendiente puede confirmarse.", session_id, (s,m,app_meta))
            payment["status"] = mapping[outcome]; payment["resolved_at"] = utc_now().replace(microsecond=0).isoformat(); payment["simulation"] = True; flow["payment_qa"] = payment
            if outcome == "confirmed":
                self._ensure_order(flow, s); app_meta["ui_state"] = "order"; set_state(flow, "S7", "PAYMENT_CONFIRMED_TO_S7")
            elif outcome == "cancelled":
                quote=current_quotation(flow)
                if quote: quote["status"]="ISSUED"; quote["delivery_window_accepted"]=False
                flow["contracting_data"]=None; flow["microstate"]="S5.CONTRACT-DATA"; app_meta["ui_state"] = "contracting"; set_state(flow, "S5", "PAYMENT_CANCELLED_TO_S5")
            elif outcome == "expired":
                quote=current_quotation(flow)
                if quote: quote["force_expired_qa"]=True; quote["status"]="EXPIRED"; quote["microstate"]="S5.Q-EXPIRED"
                flow["microstate"]="S5.Q-EXPIRED"; app_meta["ui_state"] = "quotation"; set_state(flow, "S5", "PAYMENT_EXPIRED_TO_S5")
            elif outcome == "rejected":
                # proposal remains valid; a controlled retry is possible in S6.
                set_state(flow, "S6", "PAYMENT_REJECTED_STAYS_S6")
            else:
                set_state(flow, "S6", "PAYMENT_PENDING_STAYS_S6")
            self._persist(session_id, app_meta)
            return self._ok("PAYMENT_OUTCOME_APPLIED", "Estado del pago actualizado sin operación financiera real.", session_id, (s,m,app_meta))

    def payment_recovery(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); payment=flow.get("payment_qa") or {}; quote=current_quotation(flow)
            if flow.get("state")!="S6" or payment.get("status")!="RECHAZADO" or not quote:
                return self._blocked("PAYMENT_RECOVERY_BLOCKED","No existe un pago rechazado recuperable.",session_id,(s,m,app_meta))
            quote["status"]="ISSUED"; quote["delivery_window_accepted"]=False; flow["contracting_data"]=None; flow["microstate"]="S5.CONTRACT-DATA"; app_meta["ui_state"]="contracting"; set_state(flow,"S5","PAYMENT_REJECTED_RECOVERY_TO_S5")
            self._persist(session_id,app_meta)
            return self._ok("PAYMENT_RECOVERY_READY","Revisa nuevamente la solicitud antes de continuar.",session_id,(s,m,app_meta))

    def _ensure_order(self, flow: Dict[str, Any], s: Session) -> Dict[str, Any]:
        if flow.get("order_qa"):
            self.repository.archive_order(s.session_id,{"order":deepcopy(flow["order_qa"]),"email_preview":deepcopy(flow.get("email_preview")),"internal_matrix_qa":deepcopy(flow.get("internal_matrix_qa")),"simulation":True})
            return flow["order_qa"]
        if (flow.get("payment_qa") or {}).get("status") != "CONFIRMADO":
            raise RuntimeError("Order creation requires confirmed QA payment")
        day = datetime.now(timezone.utc).strftime("%Y%m%d"); seq = self.repository.next_order_sequence(day)
        quote=current_quotation(flow) or {}; request=current_solution_request(flow) or {}; scope=current_scope(flow) or {}; key = order_idempotency_key(flow)
        construction_snapshot={"snapshot_version":3,"solution_request_version_id":request.get("solution_request_version_id"),"scope_version_id":request.get("scope_version_id"),"solution_title":request.get("request_title"),"service_id":request.get("validated_agent"),"service_label":request.get("service_label"),"agent":request.get("service_label"),"need_confirmed":scope.get("need_confirmed"),"objective":request.get("objective"),"context":request.get("context"),"why_fit":request.get("why_fit"),"scope":request.get("scope"),"deliverables":deepcopy(request.get("deliverables",[])),"information_input":request.get("information_input"),"materials_needed":deepcopy(request.get("materials_needed",[])),"matrix_version":request.get("matrix_version"),"matrix_item_ids":deepcopy(request.get("matrix_item_ids",[])),"commitments":deepcopy(request.get("commitments",[])),"controls":deepcopy(request.get("controls",[])),"exclusions":deepcopy(request.get("exclusions",[])),"platform_label":request.get("platform_label") or QA_PLATFORM_LABEL,"platform_notice":request.get("platform_notice") or QA_PLATFORM_NOTICE,"environment_id":request.get("environment_id"),"delivery_label":"Configuración preparada para el entorno acordado","delivery_mode":request.get("delivery_mode"),"delivery_notice":QA_DELIVERY_NOTICE,"dependencies":deepcopy(request.get("dependencies",[])),"quotation_ref":quote.get("quotation_ref"),"commercial_rules_version":quote.get("commercial_rules_version"),"amount":quote.get("amount"),"currency":quote.get("currency"),"delivery_window":quote.get("delivery_window"),"conditions_version":quote.get("conditions_version"),"particular_conditions":deepcopy(quote.get("particular_conditions") or []),"terms_version":(flow.get("contracting_data") or {}).get("terms_version"),"privacy_notice_version":(flow.get("contracting_data") or {}).get("privacy_notice_version"),"acceptances":{"contract_terms":deepcopy((flow.get("contracting_data") or {}).get("contract_terms_acceptance")),"privacy":deepcopy((flow.get("contracting_data") or {}).get("privacy_acceptance"))},"payment_reference":(flow.get("payment_qa") or {}).get("reference"),"payment_status":"CONFIRMADO","contact":{"name":(flow.get("qa_identity") or {}).get("name"),"email":(flow.get("qa_identity") or {}).get("email"),"phone":deepcopy((flow.get("qa_identity") or {}).get("phone")),"billing_country":deepcopy((flow.get("qa_identity") or {}).get("billing_country"))},"conversation_evidence_included":False,"immutable":True}
        order = {
            "order_id": f"END-{day}-{seq:04d}", "status": "RECIBIDA",
            "next_step": "REVISIÓN INTERNA", "created_at": utc_now().replace(microsecond=0).isoformat(),
            "scope_version_id":quote.get("scope_version_id"),"solution_request_version_id":quote.get("solution_request_version_id"),"quotation_id":quote.get("quotation_id"),"quotation_version":quote.get("quotation_version"),
            "amount_label": quote.get("amount_label"), "delivery_window": quote.get("delivery_window"), "selected_agent": flow.get("selected_agent"),
            "need_confirmed": (flow.get("client_output") or {}).get("need_confirmed"),"construction_request_snapshot":construction_snapshot,
            "idempotency_key": key, "simulation": True,
        }
        flow["order_qa"] = order; flow["client_output"]={**(flow.get("client_output") or {}),"order_ref":order["order_id"]}; flow["internal_matrix_qa"] = build_internal_matrix(flow, s); flow["email_preview"]=build_order_email_preview(order)
        self.repository.archive_order(s.session_id,{"order":deepcopy(order),"email_preview":deepcopy(flow["email_preview"]),"internal_matrix_qa":deepcopy(flow["internal_matrix_qa"]),"simulation":True})
        return order

    def order_replay(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s, m, app_meta = self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if (flow.get("payment_qa") or {}).get("status") != "CONFIRMADO":
                return self._blocked("ORDER_REPLAY_BLOCKED", "No existe un pago confirmado para recuperar la orden.", session_id, (s,m,app_meta))
            existing=deepcopy(flow.get("order_qa")); order=self._ensure_order(flow,s); self._persist(session_id,app_meta)
            return {"ok":True,"event":"ORDER_IDEMPOTENT_REPLAY","same_order": bool(existing and existing.get('order_id')==order.get('order_id')),"order":order,"summary":self.summary(session_id,hydrated=(s,m,app_meta))}

    def finalize_conversation(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); order=deepcopy(flow.get("order_qa"))
            if flow.get("state") != "S7" or not order or (flow.get("payment_qa") or {}).get("status") != "CONFIRMADO":
                return self._blocked("CONVERSATION_FINALIZE_BLOCKED","La conversación solo puede finalizar después de una orden confirmada.",session_id,(s,m,app_meta))
            archived=self.repository.archive_order(session_id,{"order":order,"email_preview":deepcopy(flow.get("email_preview")),"internal_matrix_qa":deepcopy(flow.get("internal_matrix_qa")),"simulation":True})
            self.reset(session_id)
            return {"ok":True,"event":"CONVERSATION_FINALIZED","message":"Conversación finalizada.","order_id":order["order_id"],"snapshot_sha256":archived["snapshot_sha256"],"simulation":True}

    def archived_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.repository.get_archived_order(order_id)

    def tracking_open(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow["state"] not in {"S3","S4","S5","S6","S7","S8"}:
                return self._blocked("TRACKING_BLOCKED","El seguimiento todavía no está disponible.",session_id,(s,m,app_meta))
            if flow["state"] != "S8": flow["tracking_origin"] = flow["state"]
            app_meta["ui_state"]="tracking"; set_state(flow,"S8","TRACKING_OPENED")
            self._persist(session_id,app_meta); return self._ok("TRACKING_READY","Seguimiento disponible.",session_id,(s,m,app_meta))

    def tracking_return(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow["state"] != "S8": return self._blocked("TRACKING_RETURN_BLOCKED","Solo S8 puede volver al estado persistido.",session_id,(s,m,app_meta))
            target=flow.get("tracking_origin") or ("S7" if flow.get("order_qa") else "S4")
            if target not in {"S3","S4","S5","S6","S7"}: target="S4"
            app_meta["ui_state"]={"S3":"scope_correction_chat","S4":"professional_confirmation","S5":"proposal","S6":"payment","S7":"order"}[target]
            set_state(flow,target,"S8_RETURN_TO_PERSISTED_STATE"); self._persist(session_id,app_meta)
            return self._ok("TRACKING_RETURNED","Se restauró el estado persistido sin reejecutar pagos ni órdenes.",session_id,(s,m,app_meta))

    def human_review_resolve(self, session_id: str, target: str) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if flow["state"] != "SH": return self._blocked("HUMAN_REVIEW_RESOLVE_BLOCKED","La sesión no está en revisión humana.",session_id,(s,m,app_meta))
            target=target.upper().strip()
            if target not in {"S3","S4"}: return self._blocked("HUMAN_REVIEW_TARGET_BLOCKED","SH solo puede volver a S3 o S4; nunca a pago directo.",session_id,(s,m,app_meta))
            flow["human_review"]={"pending":False,"reason":None,"return_state":None}; s.human_review_reason=None
            if target=="S3": s.state="DIMENSIONAMIENTO INCOMPLETO"; app_meta["ui_state"]="scope_correction_chat"
            else: s.state="ORIENTACIÓN EN REVISIÓN"; app_meta["ui_state"]="professional_confirmation"
            set_state(flow,target,"SH_RESOLVED_RETURN"); self._persist(session_id,app_meta)
            return self._ok("HUMAN_REVIEW_RESOLVED","Revisión resuelta; el recorrido vuelve al punto seguro.",session_id,(s,m,app_meta))

    def select_agent(self, session_id: str, agent_id: Optional[str]) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            allowed={None,"esencial","especializado","integral"}
            if agent_id not in allowed: return self._blocked("AGENT_SELECTION_INVALID","Agente no reconocido.",session_id,(s,m,app_meta))
            flow["selected_agent"] = agent_id; flow.setdefault("trace",[]).append({"event":"AGENT_SELECTION_CHANGED","state":flow["state"],"agent":agent_id,"at":utc_now().replace(microsecond=0).isoformat()})
            self._persist(session_id,app_meta); return self._ok("AGENT_SELECTION_SAVED","Selección de agente conservada en la misma conversación.",session_id,(s,m,app_meta))

    def recovery_target(self, qa_identity_ref: str) -> Optional[str]:
        return self.repository.find_session_by_identity_ref(qa_identity_ref.strip().upper())

    def refund(self, session_id: str, confirmed: bool=False) -> Dict[str, Any]:
        with self._lock:
            s,m,app_meta=self._hydrate(session_id); flow=ensure_flow(app_meta,session_id)
            if not flow.get("order_qa"): return self._blocked("REFUND_BLOCKED","No existe una orden para gestionar el reembolso.",session_id,(s,m,app_meta))
            flow["payment_qa"]["status"]="REEMBOLSO_CONFIRMADO" if confirmed else "REEMBOLSO_PENDIENTE"
            flow["order_qa"]["refund_status"] = flow["payment_qa"]["status"]
            self._persist(session_id,app_meta); return self._ok("REFUND_QA_UPDATED","Estado del reembolso actualizado sobre la misma orden.",session_id,(s,m,app_meta))

    def _invalidate_commercial(self, flow: Dict[str, Any]):
        flow["payment_qa"]={"status":"NO_INICIADO","simulation":True}; flow["order_qa"]=None; flow["internal_matrix_qa"]=None

    def _ok(self, event: str, message: str, session_id: str, hydrated, **extra: Any) -> Dict[str, Any]:
        return {"ok":True,"event":event,"simulation":True,"message":message,"summary":self.summary(session_id,hydrated=hydrated),**extra}

    def _blocked(self, event: str, message: str, session_id: str, hydrated, **extra: Any) -> Dict[str, Any]:
        return {"ok":False,"event":event,"simulation":True,"message":message,"summary":self.summary(session_id,hydrated=hydrated),**extra}

    # Compatibility aliases retained for the v0.1.2 UI endpoint names.
    def confirm_orientation(self, session_id: str) -> Dict[str, Any]:
        return self.orientation_action(session_id,"confirm")

    def submit_qa(self, session_id: str) -> Dict[str, Any]:
        s,m,app_meta=self._hydrate(session_id)
        return self._blocked("LEGACY_QA_SUBMIT_REPLACED","Continúa desde la propuesta y el pago disponibles en pantalla.",session_id,(s,m,app_meta))

    def summary(self, session_id: str, hydrated=None) -> Dict[str, Any]:
        s,m,app_meta=hydrated or self._hydrate(session_id); flow=ensure_flow(app_meta,session_id); orientation=s.orientation or {}
        public_flow=deepcopy(flow); public_flow.pop("conversation_evidence",None); public_flow.pop("internal_dimensioning",None); public_flow.pop("dimensioning",None)
        return {
            "session_id":session_id,"state":s.state,"ui_state":app_meta.get("ui_state","conversation"),
            "need":s.interpreted_need or s.original_need,"objective":s.objective,
            "route":orientation.get("recommended"),"why":orientation.get("why"),"capabilities":orientation.get("capabilities",[]),"orientation":orientation,
            "confirmed":bool(app_meta.get("orientation_confirmed")),"submitted_qa":bool(app_meta.get("submitted_qa")),"history":app_meta.get("ui_history",[]),
            "qa_ephemeral_registration":bool(app_meta.get("qa_ephemeral_registration")),"turn_count":(self.repository.get(session_id) or {}).get("_repo",{}).get("turn_count",0),
            "full_flow": public_flow, "payment_gate": payment_gate(flow),
        }

    def reset(self, session_id: str):
        with self._lock:
            self.repository.delete(session_id); self.runtime.core.sessions.pop(session_id,None); self.runtime.meta.pop(session_id,None)
