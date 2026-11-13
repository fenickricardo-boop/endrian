from dataclasses import replace
from pathlib import Path
import pytest
from app.config import settings as base_settings
from app.full_flow import FIXTURE_INITIAL,FIXTURE_REPLY,QA_CANONICAL_CONTACT_EMAIL,QA_CANONICAL_CONTACT_NAME,QA_DELIVERY_WINDOW
from app.service import GuideService
from app.session_repository import SessionRepository

ROOT=Path(__file__).resolve().parents[1]; APP=(ROOT/'frontend/app.js').read_text(encoding='utf-8')

def svc(tmp_path):
    c=replace(base_settings,model_mode='deterministic',db_path=str(tmp_path/'v032.db'),cookie_secure=False)
    return GuideService(c,SessionRepository(c.db_path,ttl_seconds=3600))

def quote(s,sid):
    s.chat(sid,FIXTURE_INITIAL); ready=s.chat(sid,FIXTURE_REPLY); assert ready['summary']['ui_state']=='needs_confirmation_chat'
    closed=s.chat(sid,'No, está bien'); assert closed['summary']['full_flow']['state']=='S5'
    s.proposal_action(sid,'continue')
    return s.complete_registration(sid,QA_CANONICAL_CONTACT_NAME,QA_CANONICAL_CONTACT_EMAIL,True,True,False)

def test_contact_is_empty_normal_and_has_no_early_consent():
    assert 'placeholder="Escribe tu nombre completo"' in APP and 'placeholder="Escribe tu correo"' in APP
    assert 'value="QA Profesional 01"' not in APP and 'example.invalid' not in APP and 'Registro QA' not in APP
    s2=APP[APP.index("} else if(state==='S2')"):APP.index("} else if(state==='S3')")]
    assert s2.count('type="checkbox"')==0 and 'Utiliza únicamente datos ficticios' in s2

def test_canonical_synthetic_contact_and_specific_validation_order(tmp_path):
    s=svc(tmp_path); s.chat('CONTACT',FIXTURE_INITIAL); s.chat('CONTACT',FIXTURE_REPLY); s.chat('CONTACT','No, eso es todo.')
    s.proposal_action('CONTACT','continue')
    bad_name=s.complete_registration('CONTACT','123',QA_CANONICAL_CONTACT_EMAIL,False,False,False)
    assert bad_name['event']=='SYNTHETIC_NAME_REQUIRED' and bad_name['message']=='Revisa el nombre completo ingresado.'
    accepted=s.complete_registration('CONTACT',QA_CANONICAL_CONTACT_NAME,'otro@correo.test',False,False,False)
    assert accepted['event']=='PREPAYMENT_DATA_READY' and accepted['summary']['full_flow']['state']=='S5'
    assert accepted['summary']['full_flow']['qa_identity']['email']=='otro@correo.test'

def test_agent_absent_from_initial_visible_flow_and_chat_closes_scope(tmp_path):
    s=svc(tmp_path); first=s.chat('J1',FIXTURE_INITIAL); ready=s.chat('J1',FIXTURE_REPLY)
    assert 'Agente Profesional' not in first['message'] and 'Agente Profesional' not in ready['message']
    assert 'Entonces, entiendo que necesitas lo siguiente:' in ready['message']
    assert '¿Esto refleja bien lo que necesitas o quieres cambiar algo?' not in ready['message']
    closed=s.chat('J1','No, eso es todo'); assert closed['summary']['full_flow']['state']=='S5' and len(closed['summary']['full_flow']['scope_versions'])==1

@pytest.mark.parametrize('text',[
    'No, eso es todo.',
    'NO, ESO ES TODO.',
    '   No, eso es todo.   ',
    '¿No, eso es todo?',
    '¡No, eso es todo!',
])
def test_authorized_close_phrase_accepts_peripheral_punctuation(text):
    assert GuideService._confirmation_intent(text)=='CONFIRM_NO_CHANGES'

def test_close_with_period_advances_once_without_repeating_question(tmp_path):
    s=svc(tmp_path); s.chat('CLOSE',FIXTURE_INITIAL); ready=s.chat('CLOSE',FIXTURE_REPLY)
    assert ready['summary']['ui_state']=='needs_confirmation_chat'
    closed=s.chat('CLOSE','No, eso es todo.')
    f=closed['summary']['full_flow']
    assert closed['event']=='SCOPE_CONFIRMED_SEMANTIC_EVENT'
    assert f['state']=='S5' and closed['summary']['ui_state']=='request_summary'
    assert len(f['scope_versions'])==1
    assert '¿Necesitas agregar o cambiar algo?' not in closed['message']
    repeated=s.chat('CLOSE','No, eso es todo.')
    assert repeated['event']=='FLOW_CONTROL_REQUIRED'
    assert len(repeated['summary']['full_flow']['scope_versions'])==1
    assert '¿Necesitas agregar o cambiar algo?' not in repeated['message']

def test_unauthorized_phrase_remains_unresolved():
    assert GuideService._confirmation_intent('Tal vez más adelante.')=='UNRESOLVED'

def test_simplified_proposal_and_canonical_values(tmp_path):
    f=quote(svc(tmp_path),'J2')['summary']['full_flow']; assert f['state']=='S5'
    assert f['client_output']['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'==QA_DELIVERY_WINDOW
    proposal=APP[APP.index("} else if(state==='S5')"):APP.index("} else if(state==='S6')")]
    for visible in ['Resumen de tu solicitud','Servicio recomendado','Qué incluye','Precio','Plazo estimado de entrega','Volver a la conversación','Continuar con mi solicitud']: assert visible in proposal
    for removed in ['Necesidad comprendida','Por qué encaja','Alcance concreto','Materiales o información necesarios','Límites relevantes']: assert removed not in proposal
    assert 'Oferta válida hasta' not in proposal
    for removed in ['Tu solución recomendada','Agente recomendado —','¿Necesitas agregar algo?','proposalAddition','Vista previa del correo']: assert removed not in proposal

def test_summary_continue_and_return_to_chat(tmp_path):
    s=svc(tmp_path); s.chat('N0',FIXTURE_INITIAL); s.chat('N0',FIXTURE_REPLY); s.chat('N0','No, está bien')
    continued=s.proposal_action('N0','continue'); assert continued['summary']['full_flow']['state']=='S2'
    s=svc(tmp_path); s.chat('N1',FIXTURE_INITIAL); s.chat('N1',FIXTURE_REPLY); s.chat('N1','No, está bien')
    returned=s.proposal_action('N1','return_to_chat'); assert returned['summary']['full_flow']['state']=='S3' and returned['summary']['full_flow']['quotations'][0]['status']=='SUPERSEDED'

def test_reconfirmation_reuses_contact_and_versions_new_scope_quote(tmp_path):
    s=svc(tmp_path); s.chat('V1',FIXTURE_INITIAL); s.chat('V1',FIXTURE_REPLY); s.chat('V1','No, está bien'); s.proposal_action('V1','return_to_chat')
    s.chat('V1','No quiero respuestas automáticas; debe existir revisión humana')
    out=s.chat('V1','No, está bien'); f=out['summary']['full_flow']
    assert f['state']=='S5' and len(f['scope_versions'])==2 and len(f['quotations'])==2
    assert f['quotations'][0]['status']=='SUPERSEDED' and f['quotations'][1]['status']=='ISSUED'
    assert [q['quotation_version'] for q in f['quotations']]==[1,2]
    assert [q['quotation_ref'] for q in f['quotations']]==['END-QA-COT-0001/v1','END-QA-COT-0001/v2']

def test_canonical_deadline_reaches_email_gate_and_order(tmp_path):
    s=svc(tmp_path); quoted=quote(s,'CHAIN')['summary']; flow=quoted['full_flow']
    assert flow['email_preview']['content']['delivery_window']==QA_DELIVERY_WINDOW
    assert QA_DELIVERY_WINDOW in flow['email_preview']['body']
    paid=s.complete_contracting('CHAIN',{'contract_terms_accepted':True,'privacy_authorization_accepted':True})['summary']
    assert paid['payment_gate']['conditions']['delivery_window_present'] is True
    s.payment_start('CHAIN'); order=s.payment_resolve('CHAIN','confirmed')['summary']['full_flow']['order_qa']
    assert order['delivery_window']==QA_DELIVERY_WINDOW

def test_no_visible_internal_qa_language():
    forbidden=['QA Profesional 01','example.invalid','registro QA','demostración','PaymentGate','fixture','QA faltante','QA SIMULADO']
    for text in forbidden: assert text.lower() not in APP.lower()
