from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings, validate_runtime_settings
from .rate_limit import SlidingWindowLimiter
from .safety import contains_obvious_personal_data
from .security import basic_auth_ok, unauthorized_response
from .service import GuideService
from .session_repository import SessionRepository
from .customer_confirmation import (
    build_confirmation,
    build_internal_notice,
    build_internal_view,
    render_contract_pdf,
    render_email_html,
    render_internal_html,
    render_internal_notice_html,
)

ROOT = Path(__file__).resolve().parent.parent
validate_runtime_settings(settings)
FRONTEND = ROOT / "frontend"
QA_CONTROL = ROOT / "qa_control"
COPY_PATH = ROOT / "config" / "ui_copy.json"
COUNTRIES_PATH = ROOT / "config" / "billing_country_codes.json"
PHONE_PREFIXES_PATH = ROOT / "config" / "phone_country_prefixes.json"
repo = SessionRepository(str(ROOT / settings.db_path), settings.session_ttl_seconds)
service = GuideService(settings, repo)
limiter = SlidingWindowLimiter()

app = FastAPI(title="ENDRIAN Laboratorio Full Flow QA", version="0.5.15", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2400)


class RegistrationIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=8, max_length=180)
    data_processing: bool = False
    operational_comms: bool = False
    marketing: bool = False
    phone: str = Field(default="",max_length=80)
    country_code: str = Field(min_length=2,max_length=2)
    country_name: str = Field(min_length=2,max_length=120)
    phone_country_code: str = Field(default="",max_length=2)
    phone_country_name: str = Field(default="",max_length=120)
    phone_calling_code: str = Field(default="",max_length=8)
    phone_national_number: str = Field(default="",max_length=32)


class DimensioningIn(BaseModel):
    context: str = Field(min_length=1, max_length=1000)
    volume: str = Field(min_length=1, max_length=160)
    tools: List[str] = Field(default_factory=list, max_length=8)
    desired_timeline: str = Field(min_length=1, max_length=160)
    restrictions: str = Field(default="", max_length=800)
    data_profile: str = "no_sensible"
    autonomy: str = "supervisada"
    integration_known: bool = True


class OrientationActionIn(BaseModel):
    action: str
    correction: str = Field(default="", max_length=1200)


class ProposalActionIn(BaseModel):
    action: str
    accept_scope: bool = False
    accept_delivery: bool = False
    addition: str = Field(default="", max_length=800)


class ContractingIn(BaseModel):
    phone: str = Field(default="", max_length=80)
    contract_terms_accepted: bool = False
    privacy_authorization_accepted: bool = False


class PaymentOutcomeIn(BaseModel):
    outcome: str


class QAPaymentOutcomeIn(BaseModel):
    reference: str = Field(min_length=8, max_length=80)
    outcome: str

class ContactEditIn(BaseModel):
    name: str = Field(min_length=2,max_length=120)
    email: str = Field(min_length=8,max_length=180)
    phone: str = Field(default="",max_length=80)
    country_code: str = Field(min_length=2,max_length=2)
    country_name: str = Field(min_length=2,max_length=120)
    phone_country_code: str = Field(default="",max_length=2)
    phone_country_name: str = Field(default="",max_length=120)
    phone_calling_code: str = Field(default="",max_length=8)
    phone_national_number: str = Field(default="",max_length=32)

class QASpecialReviewIn(BaseModel):
    actor: str = Field(min_length=2,max_length=80)
    decision: str
    amount: Optional[int] = Field(default=None,gt=0)
    delivery_window: str = Field(default="",max_length=120)


class HumanReviewResolveIn(BaseModel):
    target: str


class AgentSelectionIn(BaseModel):
    agent_id: Optional[str] = None


class RecoverIn(BaseModel):
    qa_identity_ref: str = Field(min_length=5, max_length=64)


class RefundIn(BaseModel):
    confirmed: bool = False


def _sign_sid(sid: str) -> str:
    mac = hmac.new(settings.session_secret.encode("utf-8"), sid.encode("utf-8"), hashlib.sha256).hexdigest()[:32]
    return f"{sid}.{mac}"


def _session_id(request: Request) -> str:
    # The cookie must carry a valid HMAC over the session id so a client can
    # never pick/forge an arbitrary id (which previously let a caller rotate
    # the session id per request to dodge the per-session rate limit).
    cookie = request.cookies.get(settings.cookie_name) or ""
    sid, sep, _mac = cookie.rpartition(".")
    if sep and sid and len(cookie) <= 120 and hmac.compare_digest(_sign_sid(sid), cookie):
        return sid
    return "QA-" + uuid.uuid4().hex


def _set_cookie(response: Response, sid: str):
    response.set_cookie(
        settings.cookie_name, _sign_sid(sid), max_age=settings.session_ttl_seconds,
        httponly=True, secure=settings.cookie_secure, samesite="lax", path="/",
    )


def _client_ip(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.client.host if request.client else "unknown"


def _qa_control_authorized(request: Request) -> bool:
    if not settings.qa_control_enabled:
        return False
    if settings.qa_control_user and settings.qa_control_password:
        return basic_auth_ok(request, settings.qa_control_user, settings.qa_control_password)
    # No QA_CONTROL_USER/PASSWORD configured: only the bare local-launcher
    # scenario is safe to allow (uvicorn bound directly to 127.0.0.1, no
    # reverse proxy in front, so the TCP peer is genuinely the caller).
    # This does NOT protect a proxied/staged deployment of
    # QA_CONTROLLED_TEST_ONLY — set QA_CONTROL_USER/PASSWORD for those.
    host = request.client.host if request.client else ""
    return host in {"127.0.0.1", "::1"}


def _check_rate(request: Request, sid: str):
    ip = _client_ip(request)
    if not limiter.allow("ip:" + ip, settings.ip_requests_per_minute):
        raise HTTPException(status_code=429, detail="Límite de solicitudes excedido. Intenta nuevamente en un minuto.")
    if not limiter.allow("sid:" + sid, settings.session_requests_per_minute):
        raise HTTPException(status_code=429, detail="Límite de solicitudes de esta conversación excedido. Intenta nuevamente en un minuto.")


def _contains_pii_in_values(value: Any) -> bool:
    if isinstance(value, str):
        return contains_obvious_personal_data(value)
    if isinstance(value, list):
        return any(_contains_pii_in_values(x) for x in value)
    if isinstance(value, dict):
        return any(_contains_pii_in_values(x) for x in value.values())
    return False


def _json_result(result: Dict[str, Any], sid: str, ok_status: int=200, fail_status: int=409):
    response = JSONResponse(result, status_code=ok_status if result.get("ok", True) else fail_status)
    _set_cookie(response, sid)
    return response


@app.middleware("http")
async def qa_access_control(request: Request, call_next):
    if request.url.path.startswith(("/qa-control/","/api/qa-control/")):
        if not settings.qa_control_enabled:
            return JSONResponse({"detail":"Not found"},status_code=404)
        if not _qa_control_authorized(request):
            return unauthorized_response()
    if settings.basic_auth_required and request.url.path not in {"/health", "/api/health"}:
        if not basic_auth_ok(request, settings.staging_user, settings.staging_password):
            return unauthorized_response()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.get("/qa-control/payment")
def qa_payment_console():
    return FileResponse(QA_CONTROL / "payment.html")


@app.get("/qa-control/payment.js")
def qa_payment_console_js():
    return FileResponse(QA_CONTROL / "payment.js",media_type="application/javascript")


@app.get("/qa-control/payment.css")
def qa_payment_console_css():
    return FileResponse(QA_CONTROL / "payment.css",media_type="text/css")


@app.post("/api/qa-control/payment/resolve")
def qa_payment_resolve(payload: QAPaymentOutcomeIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    return _json_result(service.qa_payment_resolve(sid,payload.reference,payload.outcome),sid)

@app.get("/api/qa-control/orders/{order_id}")
def qa_archived_order(order_id: str, request: Request):
    archived=service.archived_order(order_id.strip().upper())
    if not archived:
        raise HTTPException(status_code=404,detail="Orden QA no encontrada")
    return {"ok":True,"environment":"QA_CONTROLLED_TEST_ONLY","archived_order":archived}

@app.get("/qa-control/confirmation.css")
def qa_confirmation_css():
    return FileResponse(QA_CONTROL / "confirmation.css",media_type="text/css")

def _confirmation_for(order_id: str):
    archived=service.archived_order(order_id.strip().upper())
    if not archived:
        raise HTTPException(status_code=404,detail="Orden QA no encontrada")
    try:
        return build_confirmation(archived)
    except ValueError as exc:
        raise HTTPException(status_code=409,detail=str(exc)) from exc

@app.get("/qa-control/orders/{order_id}/confirmation",response_class=HTMLResponse)
def qa_customer_confirmation_page(order_id: str,request: Request):
    return HTMLResponse(render_email_html(_confirmation_for(order_id)))

@app.get("/api/qa-control/orders/{order_id}/customer-confirmation")
def qa_customer_confirmation(order_id: str,request: Request):
    return {"ok":True,"environment":"QA_CONTROLLED_TEST_ONLY","confirmation":_confirmation_for(order_id)}

@app.get("/api/qa-control/orders/{order_id}/contract-copy.pdf")
def qa_contract_copy(order_id: str,request: Request):
    data=_confirmation_for(order_id); payload=render_contract_pdf(data)
    headers={"Content-Disposition":f'attachment; filename="{data["attachment"]["filename"]}"'}
    return StreamingResponse(iter([payload]),media_type="application/pdf",headers=headers)

@app.get("/qa-control/orders/{order_id}/internal",response_class=HTMLResponse)
def qa_internal_order_page(order_id: str,request: Request):
    archived=service.archived_order(order_id.strip().upper())
    if not archived:
        raise HTTPException(status_code=404,detail="Orden QA no encontrada")
    return HTMLResponse(render_internal_html(build_internal_view(archived)))

@app.get("/api/qa-control/orders/{order_id}/internal")
def qa_internal_order(order_id: str,request: Request):
    archived=service.archived_order(order_id.strip().upper())
    if not archived:
        raise HTTPException(status_code=404,detail="Orden QA no encontrada")
    return {"ok":True,"environment":"QA_CONTROLLED_TEST_ONLY","internal_order":build_internal_view(archived)}

@app.get("/qa-control/orders/{order_id}/internal-notice",response_class=HTMLResponse)
def qa_internal_notice_page(order_id: str,request: Request):
    data=_confirmation_for(order_id)
    return HTMLResponse(render_internal_notice_html(build_internal_notice(data)))

@app.get("/api/qa-control/orders/{order_id}/internal-notice")
def qa_internal_notice(order_id: str,request: Request):
    data=_confirmation_for(order_id)
    return {"ok":True,"environment":"QA_CONTROLLED_TEST_ONLY","notice":build_internal_notice(data)}

@app.post("/api/qa-control/special-review/resolve")
def qa_special_review_resolve(payload: QASpecialReviewIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    return _json_result(service.qa_special_review_resolve(sid,payload.actor,payload.decision,payload.amount,payload.delivery_window),sid)


@app.get("/health")
@app.get("/api/health")
def health():
    return {"ok": True, "status": "QA / NO PRODUCCIÓN"}


@app.get("/")
def index(request: Request):
    sid = _session_id(request)
    response = FileResponse(FRONTEND / "index.html")
    _set_cookie(response, sid)
    return response


@app.get("/api/config")
def public_config(request: Request):
    sid = _session_id(request)
    with open(COPY_PATH, "r", encoding="utf-8") as f:
        copy = json.load(f)
    with open(COUNTRIES_PATH,"r",encoding="utf-8") as f: country_codes=json.load(f)
    with open(PHONE_PREFIXES_PATH,"r",encoding="utf-8") as f: phone_prefixes=json.load(f)
    response = JSONResponse({"qa": True, "model_mode": settings.model_mode, "max_turns": settings.max_turns_per_session, "copy": copy, "full_flow": True,"billing_country_codes":country_codes,"phone_country_prefixes":phone_prefixes})
    _set_cookie(response, sid)
    return response


@app.get("/api/session")
def get_session(request: Request):
    sid = _session_id(request); _check_rate(request, sid)
    response = JSONResponse(service.summary(sid)); _set_cookie(response, sid); return response


@app.post("/api/chat")
def chat(payload: ChatIn, request: Request):
    sid = _session_id(request); _check_rate(request, sid)
    current = repo.get(sid); turn_count = (current or {}).get("_repo", {}).get("turn_count", 0)
    if turn_count >= settings.max_turns_per_session:
        raise HTTPException(status_code=429, detail="Esta conversación alcanzó el máximo de turnos. Inicia una nueva conversación.")
    text = payload.message.strip()
    if contains_obvious_personal_data(text):
        result={"ok":False,"event":"QA_PERSONAL_DATA_BLOCKED","simulation":True,"message":"Por seguridad, no ingreses correos, teléfonos, RUT, tarjetas ni otros datos personales reales. Usa ejemplos ficticios."}
        return _json_result(result,sid,fail_status=400)
    if settings.real_model_enabled and not os.getenv("OPENAI_API_KEY"):
        result={"ok":False,"event":"MODEL_NOT_CONFIGURED","simulation":True,"message":"El modo real no está configurado. Este candidato debe ejecutarse con MODEL_MODE=deterministic."}
        return _json_result(result,sid,fail_status=503)
    return _json_result(service.chat(sid,text),sid)


@app.post("/api/full-flow/understanding/confirm")
def confirm_understanding(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.confirm_understanding(sid),sid)


@app.post("/api/full-flow/registration")
def registration(payload: RegistrationIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    return _json_result(service.complete_registration(sid,payload.name,payload.email,payload.data_processing,payload.operational_comms,payload.marketing,payload.phone,payload.country_code,payload.country_name,payload.phone_country_code,payload.phone_country_name,payload.phone_calling_code,payload.phone_national_number),sid)

@app.post("/api/full-flow/contact/edit")
def edit_contact(payload: ContactEditIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    return _json_result(service.edit_contact(sid,payload.name,payload.email,payload.phone,payload.country_code,payload.country_name,payload.phone_country_code,payload.phone_country_name,payload.phone_calling_code,payload.phone_national_number),sid)

@app.post("/api/full-flow/product-change/confirm")
def confirm_product_change(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.confirm_product_change(sid),sid)

@app.post("/api/full-flow/confirmation/action")
def confirmation_action(payload: OrientationActionIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    return _json_result(service.confirmation_action(sid,payload.action),sid)


@app.post("/api/full-flow/dimensioning")
def dimensioning(payload: DimensioningIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid); data=payload.model_dump()
    if _contains_pii_in_values(data):
        return _json_result({"ok":False,"event":"QA_PERSONAL_DATA_BLOCKED","message":"No introduzcas datos personales reales en este entorno. Usa descripciones ficticias o genéricas.","simulation":True},sid,fail_status=400)
    if data["data_profile"] not in {"no_sensible","sensible"} or data["autonomy"] not in {"supervisada","alta"}:
        return _json_result({"ok":False,"event":"DIMENSIONING_VALUE_INVALID","message":"Revisa este dato para continuar.","simulation":True},sid,fail_status=400)
    return _json_result(service.dimension(sid,data),sid)


@app.post("/api/full-flow/orientation/action")
def orientation_action(payload: OrientationActionIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    if payload.correction and contains_obvious_personal_data(payload.correction):
        return _json_result({"ok":False,"event":"QA_PERSONAL_DATA_BLOCKED","message":"La corrección no puede incluir datos personales reales.","simulation":True},sid,fail_status=400)
    return _json_result(service.orientation_action(sid,payload.action,payload.correction),sid)


@app.post("/api/full-flow/proposal/action")
def proposal_action(payload: ProposalActionIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid)
    if payload.addition and contains_obvious_personal_data(payload.addition):
        return _json_result({"ok":False,"event":"PERSONAL_DATA_BLOCKED","message":"No incluyas datos personales en este campo.","simulation":True},sid,fail_status=400)
    return _json_result(service.proposal_action(sid,payload.action,payload.accept_scope,payload.accept_delivery,payload.addition),sid)


@app.post("/api/full-flow/contracting")
def contracting(payload: ContractingIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid); data=payload.model_dump()
    return _json_result(service.complete_contracting(sid,data),sid)


@app.post("/api/full-flow/payment/start")
def payment_start(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.create_or_reuse_payment_attempt(sid),sid)

@app.post("/api/full-flow/payment/return")
def payment_return(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.payment_return(sid),sid)

@app.post("/api/full-flow/payment/recovery")
def payment_recovery(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.payment_recovery(sid),sid)


@app.post("/api/full-flow/order/replay")
def order_replay(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.order_replay(sid),sid)

@app.post("/api/full-flow/conversation/finalize")
def finalize_conversation(request: Request):
    old=_session_id(request); _check_rate(request,old); result=service.finalize_conversation(old)
    if not result.get("ok"):
        return _json_result(result,old)
    sid="QA-"+uuid.uuid4().hex
    result["summary"]=service.summary(sid)
    response=JSONResponse(result); _set_cookie(response,sid); return response


@app.post("/api/full-flow/tracking/open")
def tracking_open(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.tracking_open(sid),sid)


@app.post("/api/full-flow/tracking/return")
def tracking_return(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.tracking_return(sid),sid)


@app.post("/api/full-flow/human-review/resolve")
def human_review_resolve(payload: HumanReviewResolveIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.human_review_resolve(sid,payload.target),sid)


@app.post("/api/full-flow/agent-selection")
def agent_selection(payload: AgentSelectionIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.select_agent(sid,payload.agent_id),sid)


@app.post("/api/full-flow/recover")
def recover(payload: RecoverIn, request: Request):
    current=_session_id(request); _check_rate(request,current); ref=payload.qa_identity_ref.strip().upper()
    if not re.fullmatch(r"QID-[A-F0-9]{12}", ref):
        return _json_result({"ok":False,"event":"RECOVERY_REF_INVALID","message":"Usa únicamente el qa_identity_ref sintético mostrado por el Laboratorio.","simulation":True},current,fail_status=400)
    target=service.recovery_target(ref)
    if not target:
        return _json_result({"ok":False,"event":"RECOVERY_NOT_FOUND","message":"No encontramos una conversación vigente para esa referencia.","simulation":True},current,fail_status=404)
    result={"ok":True,"event":"RECOVERY_READY","message":"Conversación recuperada sin repetir el pago ni recrear la orden.","simulation":True,"summary":service.summary(target)}
    response=JSONResponse(result); _set_cookie(response,target); return response


@app.post("/api/full-flow/refund")
def refund(payload: RefundIn, request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.refund(sid,payload.confirmed),sid)


# Legacy endpoint names remain wired to deterministic full-flow transitions for compatibility.
@app.post("/api/orientation/confirm")
def confirm_orientation(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.confirm_orientation(sid),sid)


@app.post("/api/qa-submit")
def submit_qa(request: Request):
    sid=_session_id(request); _check_rate(request,sid); return _json_result(service.submit_qa(sid),sid)


@app.post("/api/session/new")
def new_session(request: Request):
    old=request.cookies.get(settings.cookie_name)
    if old: service.reset(old)
    sid="QA-"+uuid.uuid4().hex
    response=JSONResponse({"ok":True,"event":"NEW_QA_SESSION","message":"Nueva conversación creada."}); _set_cookie(response,sid); return response
