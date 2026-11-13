from dataclasses import replace

from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL, FIXTURE_REPLY
from app.service import GuideService
from app.session_repository import SessionRepository


def service(tmp_path):
    cfg=replace(base_settings,model_mode="deterministic",db_path=str(tmp_path/"v050.db"),cookie_secure=False)
    repo=SessionRepository(cfg.db_path,ttl_seconds=3600)
    return GuideService(cfg,repo),repo


def confirmed_order(svc,sid):
    svc.chat(sid,FIXTURE_INITIAL); svc.chat(sid,FIXTURE_REPLY); svc.confirmation_action(sid,"confirm")
    svc.proposal_action(sid,"continue")
    svc.complete_registration(sid,"Persona Sintética","persona@correo.test",country_code="CL",country_name="Chile")
    svc.complete_contracting(sid,{"contract_terms_accepted":True,"privacy_authorization_accepted":True})
    started=svc.create_or_reuse_payment_attempt(sid); ref=started["summary"]["full_flow"]["payment_qa"]["reference"]
    svc.payment_return(sid); resolved=svc.qa_payment_resolve(sid,ref,"confirmed")
    return ref,resolved["summary"]["full_flow"]["order_qa"]


def test_finalize_clears_conversation_but_preserves_archived_order(tmp_path):
    svc,repo=service(tmp_path); sid="FINALIZE-V050"; ref,order=confirmed_order(svc,sid); order_id=order["order_id"]
    before=repo.get(sid); assert before is not None
    archived=repo.get_archived_order(order_id)
    assert archived["order"]["order_id"]==order_id
    assert archived["order"]["construction_request_snapshot"]["immutable"] is True
    assert archived["order"]["construction_request_snapshot"]["conversation_evidence_included"] is False
    out=svc.finalize_conversation(sid)
    assert out["ok"] is True and out["order_id"]==order_id
    assert repo.get(sid) is None
    preserved=svc.archived_order(order_id)
    assert preserved["order"]["order_id"]==order_id
    assert preserved["email_preview"]["sent"] is False
    assert ref==preserved["order"]["construction_request_snapshot"]["payment_reference"]


def test_finalize_requires_confirmed_order_and_archive_is_idempotent(tmp_path):
    svc,repo=service(tmp_path)
    blocked=svc.finalize_conversation("EMPTY-V050")
    assert blocked["ok"] is False and blocked["event"]=="CONVERSATION_FINALIZE_BLOCKED"
    _,order=confirmed_order(svc,"IDEMPOTENT-V050")
    first=repo.get_archived_order(order["order_id"]); second=repo.archive_order("IDEMPOTENT-V050",first)
    assert second["order"]["order_id"]==first["order"]["order_id"]


def test_public_contract_has_finalize_and_no_fixed_additional_conditions():
    from pathlib import Path
    app=(Path(__file__).resolve().parents[1]/"frontend"/"app.js").read_text(encoding="utf-8")
    assert "Finalizar conversación" in app
    assert "/api/full-flow/conversation/finalize" in app
    assert "Condiciones de mi pedido" not in app
    assert "Pago confirmado" in app and "Tu pedido fue recibido correctamente." in app


def test_postpayment_public_card_has_only_finalize_action_and_snapshot_title():
    from pathlib import Path
    app=(Path(__file__).resolve().parents[1]/"frontend"/"app.js").read_text(encoding="utf-8")
    card=app.split("} else if(state==='S7'){",1)[1].split("} else if(state==='S8'){",1)[0]
    assert "snapshot.solution_title" in card
    assert "El título del agente no está disponible en el snapshot de esta orden." in card
    assert "Finalizar conversación" in card
    assert "Verificar pedido" not in card
    assert "Ver seguimiento" not in card
