from dataclasses import replace
from app.config import settings as base_settings
from app.service import GuideService
from app.session_repository import SessionRepository

def make_service(tmp_path):
    c=replace(base_settings,model_mode="deterministic",db_path=str(tmp_path/"service.db"),cookie_secure=False)
    return GuideService(c,SessionRepository(c.db_path,ttl_seconds=3600))

def test_clear_need_enters_definition_before_identity(tmp_path):
    s=make_service(tmp_path); out=s.chat("SIMPLE","Necesito organizar correos y dar seguimiento en Gmail")
    assert out["summary"]["full_flow"]["state"]=="S1"
    assert out["event"]=="DETERMINISTIC_SCRIPT_REQUIRED" and out["summary"]["full_flow"]["orientation_summary"] is None
    assert out["summary"]["full_flow"]["qa_identity"] is None

def test_sensitive_dimension_triggers_human_review(tmp_path):
    s=make_service(tmp_path); core,meta,app=s._hydrate("SENS"); core.original_need="Necesidad sintética"; app["full_flow"]["state"]="S3"; s._persist("SENS",app)
    out=s.dimension("SENS",{"context":"QA","volume":"80/día","tools":["Correo"],"desired_timeline":"10 días","restrictions":"QA","data_profile":"sensible","autonomy":"supervisada","integration_known":True})
    assert out["summary"]["full_flow"]["state"]=="SH" and out["summary"]["payment_gate"]["payment_enabled"] is False
