from dataclasses import replace
from pathlib import Path
from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL,FIXTURE_REPLY,PREPAYMENT_CONDITIONS_VERSION,QA_CANONICAL_CONTACT_EMAIL
from app.service import GuideService
from app.session_repository import SessionRepository

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'frontend/app.js').read_text(encoding='utf-8')
INDEX=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
CSS=(ROOT/'frontend/styles.css').read_text(encoding='utf-8')

def service(tmp_path,name):
    cfg=replace(base_settings,model_mode='deterministic',db_path=str(tmp_path/f'{name}.db'),cookie_secure=False)
    return GuideService(cfg,SessionRepository(cfg.db_path,ttl_seconds=3600))

def pending(s,sid):
    s.chat(sid,FIXTURE_INITIAL); s.chat(sid,FIXTURE_REPLY); s.chat(sid,'No, eso es todo.')
    s.proposal_action(sid,'continue')
    s.complete_registration(sid,'Juan Pérez',QA_CANONICAL_CONTACT_EMAIL,True,True,False)
    prepared=s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True}); assert prepared['summary']['full_flow']['state']=='S6'
    return s.payment_start(sid)

def test_public_prepayment_is_minimal_and_has_no_payment_controls():
    for text in ['Antes de pagar','Modificar datos','Continuar al pago','Acepto los Términos y Condiciones de ENDRIAN','Autorizo a ENDRIAN a tratar mis datos personales','No se realizarán cobros ni se solicitarán datos financieros.']: assert text in APP
    for text in ['Tipo<select','Razón social','Identificador fiscal','Confirmar pago','Marcar expirado','paymentReject','paymentCancel','/api/full-flow/payment/resolve','PaymentGate']: assert text not in APP
    assert 'Adjuntos desactivados en QA' not in INDEX and 'Adjuntos no disponibles' in INDEX

def test_composer_uses_one_component_with_structured_compact_mode():
    assert "composer: $('#composerZone')" in APP and "classList.toggle('composer--compact',!chatAllowed)" in APP
    assert '.composer-zone.composer--compact' in CSS and '.composer-zone.composer--compact .composer-help' in CSS

def test_payment_gate_minimal_data_and_versioned_acceptance(tmp_path):
    s=service(tmp_path,'gate'); out=pending(s,'GATE'); summary=out['summary']; data=summary['full_flow']['contracting_data']; conditions=summary['payment_gate']['conditions']
    assert conditions['prepayment_data_complete'] is True and 'contracting_data_complete' not in conditions and all(conditions.values())
    assert data['conditions_version']==PREPAYMENT_CONDITIONS_VERSION and data['contract_terms_acceptance']['accepted_at'].endswith('+00:00')
    assert data['phone'] is None and not {'type','company_name_qa','fiscal_id_qa'} & set(data)

def test_create_or_reuse_payment_attempt_is_idempotent(tmp_path):
    s=service(tmp_path,'idem'); first=pending(s,'IDEM'); ref=first['summary']['full_flow']['payment_qa']['reference']; second=s.payment_start('IDEM')
    assert first['reused'] is False and second['reused'] is True and second['event']=='PAYMENT_ATTEMPT_REUSED'
    assert second['summary']['full_flow']['payment_qa']['reference']==ref
    frozen=second['summary']['full_flow']['payment_qa']
    for key in ['amount','currency','scope_version_id','solution_request_version_id','quotation_id','quotation_version','quotation_ref']: assert frozen.get(key) is not None

def test_separate_qa_resolution_all_outcomes_and_reference_guard(tmp_path):
    expected={'confirmed':'S7','rejected':'S6','cancelled':'S5','expired':'S5'}
    for outcome,state in expected.items():
        s=service(tmp_path,outcome); started=pending(s,outcome); ref=started['summary']['full_flow']['payment_qa']['reference']
        assert s.qa_payment_resolve(outcome,'PAY-QA-INVALID',outcome)['ok'] is False
        resolved=s.qa_payment_resolve(outcome,ref,outcome); assert resolved['summary']['full_flow']['state']==state
        if outcome=='confirmed':
            order=resolved['summary']['full_flow']['order_qa']; replay=s.order_replay(outcome)
            assert order and replay['same_order'] is True and replay['order']['order_id']==order['order_id']

def test_qa_console_is_separate_and_unlinked():
    html=(ROOT/'qa_control/payment.html').read_text(encoding='utf-8'); js=(ROOT/'qa_control/payment.js').read_text(encoding='utf-8')
    assert 'QA_CONTROLLED_TEST_ONLY' in html and '/api/qa-control/payment/resolve' in js
    assert '/qa-control/' not in APP and '/qa-control/' not in INDEX
