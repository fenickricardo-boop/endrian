from dataclasses import replace
from pathlib import Path
from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY, FIXTURE_SCOPE
from app.service import GuideService
from app.session_repository import SessionRepository

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/"frontend/app.js").read_text(encoding="utf-8")

def service(tmp_path):
    c=replace(base_settings,model_mode="deterministic",db_path=str(tmp_path/"ux031.db"),cookie_secure=False)
    return GuideService(c,SessionRepository(c.db_path,ttl_seconds=3600))

def test_no_public_dimensioning_form_or_repeated_qa_badges():
    for forbidden in ["dimContext","dimVolume","dimTools","dimTimeline","dimRestrictions","dimData","dimAutonomy","dimKnown","Corrección QA opcional","QA SIMULADO · NO PRODUCCIÓN","Registro QA sintético","PaymentGate"]:
        assert forbidden not in APP
    assert APP.count("Entorno de prueba · Sin operaciones reales")==1

def test_fixture_moves_through_internal_s3_directly_to_professional_card(tmp_path):
    s=service(tmp_path); s.chat("UX1",FIXTURE_INITIAL); out=s.chat("UX1",FIXTURE_REPLY); f=out["summary"]["full_flow"]
    assert f["state"]=="S4" and f["client_output"]["need_confirmed"]==FIXTURE_SCOPE["need_confirmed"]
    assert "dimensioning" not in f and "internal_dimensioning" not in f
    assert not f["scope_versions"] and not f["quotations"]

def test_professional_confirmation_is_chat_only_without_card_or_raw_fallbacks():
    s4=APP[APP.index("} else if(state==='S4')"):APP.index("} else if(state==='S5')")]
    assert "product_conformity" in s4
    for forbidden in ["session.need","session.objective","orientation_summary","client_output","textarea","<input","Agente recomendado"]: assert forbidden not in s4

def test_correction_returns_to_chat_and_supported_route_regenerates_output(tmp_path):
    s=service(tmp_path); s.chat("UX2",FIXTURE_INITIAL); s.chat("UX2",FIXTURE_REPLY)
    back=s.chat("UX2","Sí, quiero cambiar algo"); assert back["summary"]["full_flow"]["state"]=="S3"
    assert back["summary"]["ui_state"]=="scope_correction_chat" and back["summary"]["full_flow"]["client_output"] is None
    unsupported=s.chat("UX2","Quiero cambiar otra cosa"); assert unsupported["event"]=="DETERMINISTIC_CORRECTION_CLARIFICATION" and unsupported["summary"]["full_flow"]["state"]=="S3"
    ready=s.chat("UX2","No quiero respuestas automáticas; debe existir revisión humana")
    assert ready["summary"]["full_flow"]["state"]=="S4" and ready["summary"]["full_flow"]["client_output"]["need_confirmed"]==FIXTURE_SCOPE["need_confirmed"]

def test_scope_request_and_quote_exist_after_confirmation_before_identity(tmp_path):
    s=service(tmp_path); s.chat("UX3",FIXTURE_INITIAL); ready=s.chat("UX3",FIXTURE_REPLY)
    assert ready["summary"]["full_flow"]["scope_versions"]==[] and ready["summary"]["full_flow"]["quotations"]==[]
    confirmed=s.chat("UX3","No, eso es todo"); assert len(confirmed["summary"]["full_flow"]["scope_versions"])==1
    assert len(confirmed["summary"]["full_flow"]["quotations"])==1 and confirmed["summary"]["full_flow"]["state"]=="S5"
    assert len(confirmed["summary"]["full_flow"]["solution_request_versions"])==1

def test_public_summary_never_exports_conversation_or_internal_dimensioning(tmp_path):
    s=service(tmp_path); s.chat("UX4",FIXTURE_INITIAL); out=s.chat("UX4",FIXTURE_REPLY); f=out["summary"]["full_flow"]
    assert "conversation_evidence" not in f and "internal_dimensioning" not in f and "dimensioning" not in f
