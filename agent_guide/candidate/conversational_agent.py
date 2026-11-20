#!/usr/bin/env python3
"""ENDRIAN Agente Guía MVP QA v0.2
Conversational integration layer over the preserved v0.1 deterministic control core.
QA / NO PRODUCCIÓN. No network, credentials, real email, payment, orders or production.

Public black-box entry point:
    handle_message(session_id, user_message)
"""
from __future__ import annotations
import os, sys, re, json
from typing import Dict, Any, Optional, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORE = os.path.join(ROOT, "core_v0_1")
sys.path.insert(0, os.path.join(CORE, "candidate"))
from guide_agent import GuideAgentQA, REFS, QA_MATRIX_COMPLETE  # preserved v0.1 core

QA_FIXTURES = {
    "simple": {"classification":"Esencial"},
    "professional": {"classification":"Profesional"},
    "personalized": {"classification":"Personalizado"},
    "proposal_simple": {"price_kind":"exact","price":"QA-100","delivery_window":"QA-WINDOW-5","includes":["QA-CAPACIDAD-FUNCIONAL"],"excludes":["PRODUCCIÓN REAL"]},
    "proposal_professional": {"price_kind":"exact","price":"QA-250","delivery_window":"QA-WINDOW-10","includes":["QA-CAPACIDADES-FUNCIONALES"],"excludes":["PRODUCCIÓN REAL"]},
}

ALLOWED_MODEL_ACTIONS = {
    "ASK_MATERIAL_QUESTION", "UPDATE_INTERPRETATION", "EXTRACT_DIMENSIONING",
    "FLAG_HUMAN_REVIEW", "DRAFT_ORIENTATION", "ANSWER_FUNCTIONAL_CLARIFICATION",
    "REFUSE_IMPLEMENTATION_DETAIL", "NO_OP"
}
ALLOWED_MODEL_FIELDS = {
    "interpreted_need","objective","extracted","missing_material","contradiction",
    "human_review_reason","action","question","functional_answer","confidence"
}

class ConversationalGuideQA:
    def __init__(self):
        self.core = GuideAgentQA(QA_FIXTURES)
        self.meta: Dict[str, Dict[str, Any]] = {}

    def _session(self, session_id: str):
        if session_id not in self.core.sessions:
            self.core.new_session(session_id)
            self.meta[session_id] = {
                "pending_question": None,
                "registered": False,
                "orientation_confirmed": False,
                "history": [],
                "last_output": None,
                "model_mode": "DETERMINISTIC_QA_ADAPTER",
            }
        return self.core.sessions[session_id], self.meta[session_id]

    @staticmethod
    def _norm(text:str)->str:
        return re.sub(r"\s+"," ",text.strip().lower())

    @staticmethod
    def _extract_email(text:str)->Optional[str]:
        m=re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",text,re.I)
        return m.group(0) if m else None

    @staticmethod
    def _extract_name(text:str)->Optional[str]:
        m=re.search(r"(?:me llamo|mi nombre es)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,50}?)(?=,|\.| y mi correo| correo|$)",text,re.I)
        return m.group(1).strip() if m else None

    def _extract_dimensions(self,text:str)->Dict[str,Any]:
        low=self._norm(text); out={}
        m=re.search(r"\b(\d{1,6})\s+(?:usuarios|personas|agentes|empleados)\b",low)
        if m: out["users"]=int(m.group(1))
        m=re.search(r"\b(\d{1,9})\s+(?:correos|emails|solicitudes|casos|tickets|tareas)(?:\s+(?:al|por)\s+(día|dia|semana|mes))?",low)
        if m: out["volume"]=(m.group(1)+(" por "+m.group(2) if m.group(2) else ""))
        if any(x in low for x in ["cada día","cada dia","diario","todos los días","todos los dias"]): out["frequency"]="diaria"
        elif "seman" in low: out["frequency"]="semanal"
        elif "mensual" in low or "al mes" in low or "por mes" in low: out["frequency"]="mensual"
        systems=[]
        for name in ["hubspot","salesforce","gmail","outlook","slack","notion","zendesk","shopify","sap","excel"]:
            if name in low: systems.append(name.title())
        if systems: out["systems"] = systems if len(systems)>1 else systems[0]
        if any(x in low for x in ["datos personales","datos sensibles","ficha médica","ficha medica","salud","rut","tarjeta","información confidencial","informacion confidencial"]):
            out["data_sensitivity"]="sensible"
        elif any(x in low for x in ["sin datos personales","no sensible","datos públicos","datos publicos"]): out["data_sensitivity"]="no sensible"
        if any(x in low for x in ["sin revisión humana","sin revision humana","autónomo","autonomo","decida solo","actúe solo","actue solo"]): out["autonomy"]="alta"
        elif any(x in low for x in ["con aprobación humana","con aprobacion humana","baja autonomía","baja autonomia"]): out["autonomy"]="baja"
        if any(x in low for x in ["a medida","código propio","codigo propio","desarrollo personalizado"]): out["custom_development"]=True
        if any(x in low for x in ["sistema nuevo","integración desconocida","integracion desconocida","api nueva"]): out["integration_type"]="unknown"
        elif systems: out["integration_type"]="known"
        funcs=[]
        fmap=[("clasific","clasificar"),("resum", "resumir"),("respond", "responder"),("deriv", "derivar"),("seguim", "seguimiento"),("organ", "organizar"),("analiz", "analizar")]
        for token,label in fmap:
            if token in low and label not in funcs: funcs.append(label)
        if funcs: out["functions"]=funcs
        return out

    def _is_broad(self,text:str)->bool:
        low=self._norm(text)
        phrases=["automatiza mi compañía","automatiza mi compania","automatizar mi compañía","automatizar mi compania","necesito un bot","quiero mejorar todo","automatiza mi empresa","quiero automatizar mi empresa","necesito ayuda"]
        return any(p in low for p in phrases) and len(low.split()) < 12

    def _contradiction(self,text:str)->Optional[str]:
        low=self._norm(text)
        auto=any(x in low for x in ["responda automáticamente","responda automaticamente","sin revisión humana","sin revision humana","decida solo"])
        manual=any(x in low for x in ["nunca responda sin revisión","nunca responda sin revision","siempre con aprobación","siempre con aprobacion","no responda automáticamente","no responda automaticamente"])
        if auto and manual: return "CONTRADICCIÓN SOBRE AUTONOMÍA / APROBACIÓN HUMANA"
        return None

    def _anti_exfil(self,text:str)->bool:
        low=self._norm(text)
        return any(x in low for x in ["dame el código","dame el codigo","escribe el código","escribe el codigo","prompt final","prompt de sistema","paso a paso para construir","arquitectura técnica","arquitectura tecnica","configúralo","configuralo"])

    def _registration_request(self,s):
        s.state="REGISTRO PENDIENTE"
        need=(s.interpreted_need or s.original_need or "").strip()
        intro=f'Para avanzar con "{need}", n' if need else "N"
        return self._out(s,"REGISTRATION_REQUIRED",f"{intro}ecesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.", reference=REFS["registration"])

    def _out(self,s,event,message,**extra):
        obj={"event":event,"session_id":s.session_id,"state":s.state,"simulation":True,"message":message,"required_action":extra.pop("required_action",None),"reference":extra.pop("reference",REFS["states"]),"data":extra}
        self.meta[s.session_id]["last_output"]=obj
        return obj

    def _next_material_question(self,s)->Optional[str]:
        d=s.dimensioning
        need=self._norm(s.interpreted_need or s.original_need or "")
        # Ask only when material to current need.
        if any(x in need for x in ["automat", "bot", "agente", "proceso", "correo", "solicitud"]):
            if "functions" not in d:
                return "¿Qué tarea concreta debe realizar: organizar, clasificar, responder, resumir, derivar u otra?"
            if "autonomy" not in d and any(x in d.get("functions",[]) for x in ["responder","derivar"]):
                return "¿Debe actuar por sí solo o quedar sujeto a aprobación humana antes de ejecutar acciones?"
        if "systems" not in d and any(x in need for x in ["integr", "correo", "crm", "sistema", "herramient"]):
            return "¿Con qué sistema o herramienta existente tendría que trabajar?"
        return None

    def _apply_extracted(self,s,extracted):
        if not extracted: return None
        return self.core.dimension(s,**extracted)

    def _qa_classification(self,s):
        if s.human_review_reason:
            return self.core.classify(s,QA_FIXTURES["personalized"])
        funcs=s.dimensioning.get("functions",[])
        systems=s.dimensioning.get("systems")
        if isinstance(funcs,list) and len(funcs)>=3:
            return self.core.classify(s,QA_FIXTURES["professional"])
        if isinstance(systems,list) and len(systems)>1:
            return self.core.classify(s,QA_FIXTURES["professional"])
        return self.core.classify(s,QA_FIXTURES["simple"])

    def handle_message(self, session_id:str, user_message:str)->Dict[str,Any]:
        if not isinstance(session_id,str) or not session_id.strip() or not isinstance(user_message,str) or not user_message.strip():
            return {"event":"INVALID_INPUT","state":"NO_STATE_CHANGE","simulation":True,"message":"session_id y user_message son obligatorios."}
        s,m=self._session(session_id.strip()); text=user_message.strip(); low=self._norm(text)
        m["history"].append({"role":"user","text":text})

        # Hard boundaries first.
        if self._anti_exfil(text):
            core_out=self.core.answer_post_orientation_question(s,text)
            return self._out(s,"BOUNDARY_ENFORCED",core_out["message"],boundary="ANTI-EXFILTRACIÓN",reference=REFS["antiexfil"])
        if any(x in low for x in ["genera la orden sin pagar","crea la orden sin pagar","dame el número de orden sin pagar","dame el numero de orden sin pagar"]):
            return self._out(s,"ORDER_BLOCKED","No puedo generar una orden QA sin pago QA confirmado. La solicitud se conserva.",reference=REFS["payment"])
        if any(x in low for x in ["sin registrarme","sin registro","no me quiero registrar"]):
            if not s.registration:
                return self._out(s,"ORIENTATION_BLOCKED_PRE_REGISTRATION","Puedo confirmar que entendí tu necesidad, pero la Orientación recomendada completa requiere registro QA previo.",reference=REFS["registration"])

        # Material correction after prior interpretation/orientation.
        if s.interpreted_need and any(x in low for x in ["en realidad","corrijo","cambio importante","ahora necesito","mejor dicho"]):
            extracted=self._extract_dimensions(text)
            self.core.correct_orientation(s,text,material=True)
            if extracted: self._apply_extracted(s,extracted)
            return self._out(s,"MATERIAL_CORRECTION_APPLIED","Actualicé la necesidad y descarté cualquier propuesta QA anterior que dependiera de la interpretación previa. Continuaremos desde el dimensionamiento afectado.",extracted=extracted,reference=REFS["orientation"])

        contradiction=self._contradiction(text)
        if contradiction:
            if not s.original_need:
                s.original_need=text; s.interpreted_need=text
            s.human_review_reason=contradiction; s.state="REVISIÓN HUMANA REQUERIDA"
            s.trace.append({"event":"CONTRADICTION_DETECTED","reference":REFS["human"]})
            return self._out(s,"HUMAN_REVIEW_REQUIRED","Detecté instrucciones incompatibles sobre el nivel de autonomía. No cerraré alcance, precio ni pago hasta resolver esta contradicción.",reason=contradiction,reference=REFS["human"])

        # Registration supplied naturally.
        email=self._extract_email(text); name=self._extract_name(text)
        if s.state=="REGISTRO PENDIENTE" or (email and name):
            consent_data=any(x in low for x in ["acepto tratamiento","acepto el tratamiento","consiento tratamiento"])
            consent_ops=any(x in low for x in ["acepto comunicaciones operativas","acepto las comunicaciones operativas","comunicaciones operativas"])
            if email and name and consent_data and consent_ops:
                r=self.core.register(s,name=name,email=email,data_processing=True,operational_comms=True,marketing=("marketing" in low and "acepto marketing" in low),email_verified_qa=True)
                m["registered"]=bool(r.get("ok"))
                q=self._next_material_question(s)
                if q:
                    m["pending_question"]=q
                    return self._out(s,"DIMENSIONING_QUESTION",q,required_action="RESPOND_MATERIAL_QUESTION",reference=REFS["dimensioning"])
                return self._out(s,"REGISTRATION_ACCEPTED_QA","Registro QA completado. Continuaré con el dimensionamiento sin pedir datos que no cambien la decisión.",reference=REFS["registration"])
            return self._out(s,"REGISTRATION_INCOMPLETE","Faltan datos de registro QA: nombre, correo y aceptación separada de tratamiento necesario y comunicaciones operativas.",reference=REFS["registration"])

        # First/broad need.
        if not s.original_need:
            if self._is_broad(text):
                s.conversation.append({"role":"user","text":text}); s.original_need=text
                return self._out(s,"CLARIFICATION_REQUIRED","Puedo ayudarte, pero todavía sería adivinar. ¿Qué proceso o tarea concreta quieres mejorar primero?",required_action="ANSWER_CLARIFICATION",reference=REFS["initial"])
            base=self.core.interpret(s,text)
            extracted=self._extract_dimensions(text)
            if extracted:
                s.dimensioning.update(extracted)  # pre-registration accumulation only; no commercial transition.
            return self._out(s,"PRELIMINARY_UNDERSTANDING",base["message"]+" Si esto refleja lo que necesitas, podemos continuar con el registro QA.",extracted=extracted,required_action="CONTINUE_REQUEST",reference=REFS["initial"])

        # Broad clarification answer before registration: update interpretation cumulatively.
        if not s.registration and s.state in {"CONVERSACIÓN INICIAL","COMPRENSIÓN PRELIMINAR"}:
            if low in {"continuar","sí, continuar","si, continuar","continuar mi solicitud","sí","si"}:
                return self._registration_request(s)
            if len(text.split())>=2:
                s.interpreted_need=((s.interpreted_need or s.original_need)+" | Aclaración: "+text).strip()
                extracted=self._extract_dimensions(text); s.dimensioning.update(extracted)
                s.state="COMPRENSIÓN PRELIMINAR"
                return self._registration_request(s)

        # After registration, consume natural-language answers and accumulate dimensioning.
        if s.registration and s.state in {"DIMENSIONAMIENTO INCOMPLETO","ORIENTACIÓN EN REVISIÓN","PROPUESTA DISPONIBLE","PRECIO PENDIENTE","PAGO DISPONIBLE","PAGO PENDIENTE"}:
            if any(x in low for x in ["esta orientación refleja", "confirmo la orientación", "sí, refleja", "si, refleja"]):
                m["orientation_confirmed"]=True
                c=self._qa_classification(s)
                if c["state"]=="REVISIÓN HUMANA REQUERIDA":
                    return self._out(s,"HUMAN_REVIEW_REQUIRED","La solicitud requiere revisión humana QA antes de precio/plazo.",classification=c.get("classification"),reason=s.human_review_reason,reference=REFS["human"])
                pf=QA_FIXTURES["proposal_professional"] if c.get("classification")=="Profesional" else QA_FIXTURES["proposal_simple"]
                p=self.core.make_proposal(s,pf)
                return self._out(s,"PROPOSAL_READY_QA","Propuesta QA disponible con valores ficticios. Debe aceptarse junto con la ventana QA antes de habilitar pago QA.",proposal=p.get("proposal"),classification=c.get("classification"),reference=REFS["proposal"])
            if any(x in low for x in ["acepto la propuesta", "acepto propuesta"]):
                a=self.core.accept_proposal(s,True,True)
                return self._out(s,"PAYMENT_AVAILABLE_QA" if a.get("payment_enabled") else "PAYMENT_BLOCKED","Pago QA habilitado con valores ficticios." if a.get("payment_enabled") else "El pago QA sigue bloqueado.",payment_enabled=a.get("payment_enabled",False),reference=REFS["payment"])
            if any(x in low for x in ["inicia el pago", "continuar al pago", "pagar ahora"]):
                p=self.core.start_payment(s)
                return self._out(s,"PAYMENT_STATUS_QA","Estado de pago QA actualizado.",payment=p,reference=REFS["payment"])
            if any(x in low for x in ["pago confirmado", "simula pago confirmado"]):
                if s.state!="PAGO PENDIENTE":
                    return self._out(s,"PAYMENT_CONFIRMATION_BLOCKED","No se puede confirmar un pago QA que no fue iniciado desde PAGO DISPONIBLE.",reference=REFS["payment"])
                r=self.core.resolve_payment(s,"confirmed")
                return self._out(s,"ORDER_CONFIRMED_QA","Pago QA confirmado. Se generó una orden QA y una matriz marcada exclusivamente para evaluación.",order=r.get("order"),matrix=r.get("matrix"),reference=REFS["order"])

            extracted=self._extract_dimensions(text)
            if extracted:
                d=self._apply_extracted(s,extracted)
                if s.state=="REVISIÓN HUMANA REQUERIDA":
                    return self._out(s,"HUMAN_REVIEW_REQUIRED","Tu caso necesita revisión humana QA antes de cerrar alcance, precio o plazo.",reason=s.human_review_reason,extracted=extracted,reference=REFS["human"])
            q=self._next_material_question(s)
            if q and q != m.get("pending_question"):
                m["pending_question"]=q
                return self._out(s,"DIMENSIONING_QUESTION",q,extracted=extracted,required_action="RESPOND_MATERIAL_QUESTION",reference=REFS["dimensioning"])
            o=self.core.build_orientation(s)
            if o.get("blocked"):
                return self._out(s,"ORIENTATION_BLOCKED",o["reason"],reference=REFS["registration"])
            return self._out(s,"ORIENTATION_READY","Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",orientation=o.get("orientation"),extracted=extracted,required_action="CONFIRM_OR_CORRECT_ORIENTATION",reference=REFS["orientation"])

        return self._out(s,"NO_OP","Conservo el contexto de la solicitud. Indica el siguiente dato o acción relacionada con el estado actual.",reference=REFS["states"])

    def export_session(self,session_id:str)->Dict[str,Any]:
        s,_=self._session(session_id)
        return self.core.export_session(s)

# Module-level singleton entry point for Valeria/black-box QA.
_RUNTIME = ConversationalGuideQA()
def handle_message(session_id:str,user_message:str)->Dict[str,Any]:
    return _RUNTIME.handle_message(session_id,user_message)

def export_session(session_id:str)->Dict[str,Any]:
    return _RUNTIME.export_session(session_id)

if __name__=="__main__":
    import sys
    sid=sys.argv[1] if len(sys.argv)>1 else "DEMO-V02"
    msg=" ".join(sys.argv[2:]) if len(sys.argv)>2 else "Necesito un bot"
    print(json.dumps(handle_message(sid,msg),ensure_ascii=False,indent=2))
