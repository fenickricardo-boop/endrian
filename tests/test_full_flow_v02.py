"""v0.3 post-confirmation contract and preserved full-flow regression tests."""
from dataclasses import replace
import json, socket
from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY, FIXTURE_SCOPE, QA_CANONICAL_CONTACT_EMAIL
from app.service import GuideService
from app.session_repository import SessionRepository

def make_service(tmp_path):
    c=replace(base_settings,model_mode="deterministic",db_path=str(tmp_path/"qa.db"),cookie_secure=False)
    return GuideService(c,SessionRepository(c.db_path,ttl_seconds=3600))

def dim(**changes):
    d={"context":"Equipo de cuatro personas gestiona consultas, reclamos y solicitudes por correo","volume":"80 correos/día","tools":["Correo"],"desired_timeline":"10 días hábiles","restrictions":"Supervisión humana y datos ficticios","data_profile":"no_sensible","autonomy":"supervisada","integration_known":True}
    d.update(changes); return d

def to_quote(s,sid="FLOW"):
    assert s.chat(sid,FIXTURE_INITIAL)["summary"]["full_flow"]["state"]=="S1"
    ready=s.chat(sid,FIXTURE_REPLY); assert ready["summary"]["full_flow"]["state"]=="S4"
    assert any(x["state"]=="S3" for x in ready["summary"]["full_flow"]["trace"])
    assert s.chat(sid,"No, está bien")["summary"]["full_flow"]["state"]=="S5"
    s.proposal_action(sid,"continue")
    return s.complete_registration(sid,"Juan Pérez",QA_CANONICAL_CONTACT_EMAIL,True,True,False)

def to_payment(s,sid="FLOW",kind="persona"):
    assert to_quote(s,sid)["summary"]["full_flow"]["state"]=="S5"
    p={"contract_terms_accepted":True,"privacy_authorization_accepted":True}
    return s.complete_contracting(sid,p)

def to_order(s,sid="FLOW"):
    assert to_payment(s,sid)["summary"]["full_flow"]["state"]=="S6"; s.payment_start(sid)
    return s.payment_resolve(sid,"confirmed")

def test_fixture_professional_output_and_no_early_price(tmp_path):
    s=make_service(tmp_path); first=s.chat("F01",FIXTURE_INITIAL); assert "cotización" not in json.dumps(first,ensure_ascii=False).lower()
    ready=s.chat("F01",FIXTURE_REPLY); assert ready["model"]["real_model_called"] is False
    o=ready["summary"]["full_flow"]["orientation_summary"]
    assert o["interpreted_need"]==FIXTURE_SCOPE["need_confirmed"] and o["recommended"]=="ENDRIAN Especializado"

def test_scope_identity_quote_and_client_output_separation(tmp_path):
    f=to_quote(make_service(tmp_path),"F02")["summary"]["full_flow"]
    assert f["scope_versions"][0]["status"]=="CONFIRMED" and f["qa_identity"]["email"]==QA_CANONICAL_CONTACT_EMAIL
    assert f["quotations"][0]["quotation_id"]=="END-QA-COT-0001" and "conversation_evidence" not in f["client_output"]
    serialized=json.dumps(f["client_output"],ensure_ascii=False)
    for x in ["chat_summary","conversation_text","transcript","raw_messages","turn_history","narrative_chat_recap",FIXTURE_INITIAL]: assert x not in serialized

def test_email_preview_local_unsent_allowlisted(tmp_path):
    f=to_quote(make_service(tmp_path),"F03")["summary"]["full_flow"]; em=f["quotations"][0]["email_preview"]
    assert em["sent"] is False and em["provider"] is None and em["external_service"] is False
    assert f["client_output"]["request_title"] in em["body"] and FIXTURE_INITIAL not in em["body"]

def test_prepayment_confirmation_required(tmp_path):
    s=make_service(tmp_path); out=to_payment(s,"F04"); assert out["summary"]["full_flow"]["state"]=="S6"
    assert out["summary"]["full_flow"]["contracting_data"]["contract_terms_accepted"] is True
    s=make_service(tmp_path); to_quote(s,"F04B")
    assert s.complete_contracting("F04B",{"contract_terms_accepted":False,"privacy_authorization_accepted":False})["ok"] is False
    assert s.complete_contracting("F04B",{"contract_terms_accepted":True,"privacy_authorization_accepted":True})["summary"]["full_flow"]["state"]=="S6"

def test_payment_gate_thirteen_derived_conditions(tmp_path):
    gate=to_payment(make_service(tmp_path),"F05")["summary"]["payment_gate"]
    assert gate["payment_enabled"] is True and len(gate["conditions"])>=13 and all(gate["conditions"].values())

def test_scope_change_supersedes_and_returns_definition(tmp_path):
    s=make_service(tmp_path); to_quote(s,"F06"); out=s.proposal_action("F06","modify_scope"); q=out["summary"]["full_flow"]["quotations"][0]
    assert q["status"]=="SUPERSEDED" and q["microstate"]=="S5.Q-SUPERSEDED" and out["summary"]["full_flow"]["state"]=="S3"

def test_payment_outcomes_and_order_idempotency(tmp_path):
    for outcome,expected in [("rejected","S6"),("cancelled","S5"),("expired","S5")]:
        s=make_service(tmp_path); sid="P"+outcome; to_payment(s,sid); s.payment_start(sid); f=s.payment_resolve(sid,outcome)["summary"]["full_flow"]
        assert f["state"]==expected and f["order_qa"] is None
    s=make_service(tmp_path); f=to_order(s,"F07")["summary"]["full_flow"]; replay=s.order_replay("F07")
    assert replay["same_order"] is True and replay["order"]["order_id"]==f["order_qa"]["order_id"] and f["order_qa"]["quotation_version"]==1

def test_recovery_tracking_and_human_review(tmp_path):
    s=make_service(tmp_path); f=to_order(s,"F08")["summary"]["full_flow"]; assert s.recovery_target(f["qa_identity"]["qa_identity_ref"])=="F08"
    oid=f["order_qa"]["order_id"]; s.tracking_open("F08"); assert s.tracking_return("F08")["summary"]["full_flow"]["order_qa"]["order_id"]==oid
    s=make_service(tmp_path); core,meta,app=s._hydrate("HR"); core.original_need="Necesidad sintética"; app["full_flow"]["state"]="S3"; s._persist("HR",app)
    out=s.dimension("HR",dim(data_profile="sensible")); assert out["summary"]["full_flow"]["state"]=="SH" and not out["summary"]["payment_gate"]["payment_enabled"]

def test_no_external_network_needed(monkeypatch,tmp_path):
    monkeypatch.setattr(socket.socket,"connect",lambda *a,**k: (_ for _ in ()).throw(AssertionError("network")))
    assert to_order(make_service(tmp_path),"F09")["summary"]["full_flow"]["state"]=="S7"
