from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from app.config import settings as base_settings
from app.full_flow import (
    CAPABILITY_MATRIX_VERSION, COMMERCIAL_RULES_VERSION, DELIVERY_MODE,
    ENVIRONMENT_CATALOG_VERSION, ENVIRONMENT_ID, FIXTURE_INITIAL, FIXTURE_REPLY,
    PREPAYMENT_CONDITIONS_VERSION, QA_CURRENCY, QA_PRICES, SPECIAL_FIXTURE_INITIAL,
    build_scope_version, build_solution_request, default_full_flow, payment_gate,
)
from app.service import GuideService
from app.session_repository import SessionRepository

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'frontend/app.js').read_text(encoding='utf-8')
INDEX=(ROOT/'frontend/index.html').read_text(encoding='utf-8')

def service(tmp_path,name='v036'):
    cfg=replace(base_settings,model_mode='deterministic',db_path=str(tmp_path/f'{name}.db'),cookie_secure=False)
    return GuideService(cfg,SessionRepository(cfg.db_path,ttl_seconds=3600))

def summary_ready(s,sid='STD'):
    s.chat(sid,FIXTURE_INITIAL); s.chat(sid,FIXTURE_REPLY)
    return s.chat(sid,'No, eso es todo.')

def prepayment_ready(s,sid='STD'):
    summary_ready(s,sid); s.proposal_action(sid,'continue')
    return s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False)

def test_standard_professional_summary_precedes_contact_and_is_traced(tmp_path):
    out=summary_ready(service(tmp_path),'STD'); f=out['summary']['full_flow']; req=f['solution_request_versions'][0]; quote=f['quotations'][0]
    assert f['state']=='S5' and f['qa_identity'] is None
    assert f['workflow_status']=='VALIDATED_FOR_QUOTATION' and f['validation_result']=='VALIDATED_FOR_QUOTATION' and f['validation_causes']==[]
    assert req['route']=='STANDARD' and req['matrix_version']==CAPABILITY_MATRIX_VERSION
    assert {'PRO-CAP-001','PRO-CAP-002','PRO-CAP-004','PRO-CAP-005','PRO-CAP-006','PRO-CTL-001'} <= set(req['matrix_item_ids'])
    assert req['environment_id']==ENVIRONMENT_ID and req['delivery_mode']==DELIVERY_MODE and req['environment_catalog_version']==ENVIRONMENT_CATALOG_VERSION
    assert quote['amount']==QA_PRICES['especializado']==89 and quote['currency']==QA_CURRENCY=='USD' and quote['commercial_rules_version']==COMMERCIAL_RULES_VERSION

def test_initial_preference_requires_explicit_product_conformity(tmp_path):
    s=service(tmp_path,'pref'); s.select_agent('PREF','esencial'); s.chat('PREF',FIXTURE_INITIAL); s.chat('PREF',FIXTURE_REPLY)
    blocked=s.chat('PREF','No, eso es todo.'); f=blocked['summary']['full_flow']
    assert f['state']=='S4' and f['validation_result']=='RECLASSIFICATION_REQUIRED' and f['quotations']==[]
    accepted=s.confirm_product_change('PREF'); f=accepted['summary']['full_flow']; pc=f['product_conformity']
    assert f['state']=='S5' and pc['previous_product']=='esencial' and pc['accepted_product']=='especializado' and pc['accepted_at']

def test_advanced_is_standard_but_integral_and_premium_are_special():
    for agent,route in [('esencial','STANDARD'),('especializado','STANDARD'),('integral','SPECIAL_REVIEW')]:
        flow=default_full_flow(agent); flow['selected_agent']=agent
        build_scope_version(flow,{'interpreted_need':'Necesidad sintética','objective':'Objetivo sintético','recommended_agent':f'Agente {agent.capitalize()}'})
        req=build_solution_request(flow)
        assert req['route']==route

def test_special_review_cannot_override_prohibition_or_pending_authority(tmp_path):
    s=service(tmp_path,'special'); core,meta,app=s._hydrate('SPECIAL'); flow=app['full_flow']; flow['selected_agent']='premium'
    build_scope_version(flow,{'interpreted_need':'Necesidad sintética','objective':'Objetivo','recommended_agent':'Agente Premium'}); req=build_solution_request(flow)
    flow['state']='SH'; flow['human_review']={'pending':True,'reason':'Revisión','return_state':'S5'}; req['validation_result']='BLOCKED_UNAUTHORIZED'; s._persist('SPECIAL',app)
    out=s.qa_special_review_resolve('SPECIAL','QA-AUTHORIZED','approved',30,'7 días hábiles')
    assert out['ok'] is False and out['event']=='SPECIAL_REVIEW_CANNOT_OVERRIDE_AUTHORITY' and out['summary']['full_flow']['quotations']==[]

def test_special_review_private_quote_needs_valid_decision(tmp_path):
    s=service(tmp_path,'review'); core,meta,app=s._hydrate('REVIEW'); flow=app['full_flow']; flow['selected_agent']='integral'
    build_scope_version(flow,{'interpreted_need':'Necesidad sintética','objective':'Objetivo','recommended_agent':'Agente Integral'}); req=build_solution_request(flow)
    flow['state']='SH'; flow['human_review']={'pending':True,'reason':'Revisión','return_state':'S5'}; s._persist('REVIEW',app)
    out=s.qa_special_review_resolve('REVIEW','QA-AUTHORIZED','approved',30,'7 días hábiles'); f=out['summary']['full_flow']
    assert f['state']=='S5' and f['quotations'][0]['reviewed'] is True and f['quotations'][0]['review_actor']=='QA-AUTHORIZED'
    assert '/api/qa-control/special-review/resolve' not in APP and '/qa-control/' not in INDEX

def test_contact_edit_rules_preserve_quote_and_reset_acceptance(tmp_path):
    s=service(tmp_path,'contact'); before=prepayment_ready(s,'CONTACT')['summary']['full_flow']; ref=before['current_quotation_ref']
    updated=s.edit_contact('CONTACT','Juan Pérez QA','juan.actualizado@example.com','')['summary']['full_flow']
    assert updated['current_quotation_ref']==ref and updated['contracting_data'] is None
    assert updated['qa_identity']['previous_email_verification_invalidated'] is True and updated['qa_identity']['email_verification_status']=='SIMULATED_VERIFIED'

def test_expired_quote_blocks_payment(tmp_path):
    s=service(tmp_path,'expiry'); prepayment_ready(s,'EXP'); s.complete_contracting('EXP',{'contract_terms_accepted':True,'privacy_authorization_accepted':True})
    core,meta,app=s._hydrate('EXP'); q=app['full_flow']['quotations'][0]; expired=(datetime.now(timezone.utc)-timedelta(seconds=1)).replace(microsecond=0).isoformat(); q['valid_until']=expired; q['expires_at']=expired; s._persist('EXP',app)
    gate=s.summary('EXP')['payment_gate']; assert gate['payment_enabled'] is False and gate['conditions']['quotation_not_expired'] is False

def test_payment_order_snapshot_is_unique_versioned_and_has_no_transcript(tmp_path):
    s=service(tmp_path,'order'); prepayment_ready(s,'ORDER'); s.complete_contracting('ORDER',{'contract_terms_accepted':True,'privacy_authorization_accepted':True}); started=s.payment_start('ORDER'); ref=started['summary']['full_flow']['payment_qa']['reference']
    first=s.qa_payment_resolve('ORDER',ref,'confirmed'); replay=s.order_replay('ORDER'); order=first['summary']['full_flow']['order_qa']; snap=order['construction_request_snapshot']
    assert replay['same_order'] is True and replay['order']['order_id']==order['order_id']
    assert snap['immutable'] is True and snap['snapshot_version']==3 and snap['conversation_evidence_included'] is False
    assert snap['need_confirmed'] and snap['objective'] and snap['context']
    assert snap['particular_conditions']==[]
    serialized=json.dumps(snap,ensure_ascii=False).lower(); assert 'transcript' not in serialized and FIXTURE_INITIAL.lower() not in serialized

def test_public_projection_and_email_have_no_internal_evidence(tmp_path):
    f=summary_ready(service(tmp_path,'leak'),'LEAK')['summary']['full_flow']; serialized=json.dumps({'client_output':f['client_output'],'email':f['email_preview']},ensure_ascii=False).lower()
    for forbidden in ['conversation_evidence','internal_dimensioning','raw_messages','turn_history',FIXTURE_INITIAL.lower()]: assert forbidden not in serialized

def test_global_test_notice_and_new_summary_contract_are_static():
    assert 'id="qaWarning"' in INDEX and "Entorno de prueba · Sin operaciones reales" in APP
    for required in ['Resumen de tu solicitud','Servicio recomendado','Qué incluye','Volver a la conversación','Continuar con mi solicitud','Enviar mi solicitud para revisión']: assert required in APP
    for removed in ['Necesidad comprendida','Por qué encaja','Alcance concreto','Materiales o información necesarios','Límites relevantes']: assert removed not in APP
    assert 'Oferta válida hasta' not in APP
    for removed in ['Tu solución recomendada','proposalAddition','¿Necesitas agregar algo?','$123.456 CLP','Plazo estimado de prueba']: assert removed not in APP

def test_complete_email_case_renders_understanding_then_summary_without_loop(tmp_path):
    initial=("Necesito un agente para organizar la atención por correo de mi negocio. Somos cuatro "
        "personas y recibimos unos 80 correos diarios entre consultas, reclamos y solicitudes. "
        "Queremos que clasifique los correos, priorice los pendientes, dé seguimiento a los casos y "
        "prepare borradores de respuesta. Cada respuesta debe revisarla una persona antes de enviarla. "
        "Necesitamos compartir el estado de los casos para mantener continuidad en la atención.")
    agreement="Estoy de acuerdo con lo que describí. ¿Puedes mostrarme el resumen de mi solicitud para revisarlo?"
    s=service(tmp_path,'observed-loop')
    first=s.chat('OBSERVED',initial); first_flow=first['summary']['full_flow']
    assert first['event']=='SUPPORTED_EMAIL_DEFINITION_READY'
    assert first_flow['state']=='S4' and first['summary']['ui_state']=='needs_confirmation_chat'
    assert 'Entonces, entiendo que necesitas lo siguiente:' in first['message']
    assert '¿Esto refleja bien lo que necesitas o quieres cambiar algo?' not in first['message']
    second=s.chat('OBSERVED',agreement); flow=second['summary']['full_flow']
    assert second['event']=='SCOPE_CONFIRMED_SEMANTIC_EVENT'
    assert flow['state']=='S5' and second['summary']['ui_state']=='request_summary'
    assert len(flow['scope_versions'])==1 and len(flow['solution_request_versions'])==1 and len(flow['quotations'])==1
    assert flow['client_output']['request_title']=='Solución para gestión de atención por correo'
    assert 'Preparé una comprensión preliminar' not in first['message']+second['message']
    replay=s.chat('OBSERVED',agreement); replay_flow=replay['summary']['full_flow']
    assert replay['event']=='FLOW_CONTROL_REQUIRED'
    assert len(replay_flow['scope_versions'])==1 and len(replay_flow['solution_request_versions'])==1
    assert 'Resumen de tu solicitud' in APP and "if(state==='S5')" in APP

def test_standard_visible_actions_complete_to_unique_order(tmp_path):
    s=service(tmp_path,'standard-visible'); sid='STANDARD-VISIBLE'
    s.chat(sid,FIXTURE_INITIAL); ready=s.chat(sid,FIXTURE_REPLY)
    assert ready['summary']['full_flow']['state']=='S4'
    summary=s.confirmation_action(sid,'confirm'); flow=summary['summary']['full_flow']
    assert flow['state']=='S5' and flow['quotations'][0]['amount']==89
    s.proposal_action(sid,'continue')
    s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False)
    s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True})
    attempt=s.create_or_reuse_payment_attempt(sid); ref=attempt['summary']['full_flow']['payment_qa']['reference']
    order=s.qa_payment_resolve(sid,ref,'confirmed')['summary']['full_flow']['order_qa']
    assert order and order['construction_request_snapshot']['immutable'] is True
    assert s.order_replay(sid)['same_order'] is True

def test_special_visible_route_ends_in_review_confirmation_without_quote_or_payment(tmp_path):
    s=service(tmp_path,'special-visible'); sid='SPECIAL-VISIBLE'
    ready=s.chat(sid,SPECIAL_FIXTURE_INITIAL)
    assert ready['summary']['full_flow']['state']=='S4' and 'revisión específica' in ready['message']
    summary=s.confirmation_action(sid,'confirm'); flow=summary['summary']['full_flow']
    assert flow['state']=='S5' and flow['validation_result']=='REQUIRES_HUMAN_REVIEW'
    assert flow['quotations']==[] and flow['payment_qa']['status']=='NO_INICIADO'
    s.proposal_action(sid,'send_for_review')
    submitted=s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False); flow=submitted['summary']['full_flow']
    assert submitted['event']=='SPECIAL_REVIEW_SUBMITTED' and flow['state']=='SH'
    assert submitted['summary']['ui_state']=='special_review_waiting'
    assert flow['quotations']==[] and flow['order_qa'] is None
    assert 'Solicitud enviada para revisión' in APP and 'Sí, preparar mi resumen' in APP

def test_professional_offer_projection_is_simplified_and_consistent(tmp_path):
    s=service(tmp_path,'offer-v039'); out=summary_ready(s,'OFFER-V039'); flow=out['summary']['full_flow']; quote=flow['quotations'][0]; client=flow['client_output']
    assert quote['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'==client['delivery_window']
    assert quote['expires_at']==quote['valid_until']==client['quotation_valid_until']
    assert client['commitments']==[
        'Clasificar consultas, reclamos y solicitudes.',
        'Priorizar mensajes y pendientes según los criterios definidos.',
        'Mantener seguimiento del estado de los casos.',
        'Preparar borradores de respuesta para que el equipo los revise antes del envío.',
        'Organizar el trabajo compartido del equipo de cuatro personas para mantener continuidad.',
    ]
    summary_section=APP[APP.index("} else if(state==='S5')"):APP.index("} else if(state==='S6')")]
    assert 'Precio de prueba, sin cobro real' in summary_section
    assert 'Oferta válida hasta' not in summary_section
    assert '<strong>Configurado para</strong>' not in summary_section
    assert '<strong>Entorno y entrega</strong>' not in summary_section

def test_new_order_snapshot_uses_updated_professional_delivery_window(tmp_path):
    s=service(tmp_path,'order-v039'); sid='ORDER-V039'
    summary_ready(s,sid); s.proposal_action(sid,'continue'); s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False)
    s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True}); started=s.create_or_reuse_payment_attempt(sid); ref=started['summary']['full_flow']['payment_qa']['reference']
    flow=s.qa_payment_resolve(sid,ref,'confirmed')['summary']['full_flow']
    assert flow['quotations'][0]['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'
    assert flow['order_qa']['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'
    assert flow['order_qa']['construction_request_snapshot']['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'

def test_billing_country_is_required_structured_and_preserved(tmp_path):
    s=service(tmp_path,'country'); sid='COUNTRY'
    summary_ready(s,sid); s.proposal_action(sid,'continue')
    blocked=s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False,'','','')
    assert blocked['event']=='BILLING_COUNTRY_REQUIRED'
    accepted=s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False,'','CL','Chile'); identity=accepted['summary']['full_flow']['qa_identity']
    assert identity['billing_country']=={'country_code':'CL','country_name':'Chile'}
    assert identity['phone'] is None

def test_checkout_return_stays_pending_until_backend_confirmation(tmp_path):
    s=service(tmp_path,'return'); sid='RETURN'
    summary_ready(s,sid); s.proposal_action(sid,'continue'); s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False,'','CL','Chile')
    s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True}); started=s.create_or_reuse_payment_attempt(sid); ref=started['summary']['full_flow']['payment_qa']['reference']
    returned=s.payment_return(sid); flow=returned['summary']['full_flow']
    assert returned['event']=='PAYMENT_RETURNED_PENDING' and returned['summary']['ui_state']=='payment_verifying'
    assert flow['payment_qa']['status']=='PENDIENTE' and flow['order_qa'] is None
    confirmed=s.qa_payment_resolve(sid,ref,'confirmed'); flow=confirmed['summary']['full_flow']; preview=flow['email_preview']; snap=flow['order_qa']['construction_request_snapshot']
    assert flow['order_qa'] and preview['sent'] is False and preview['order_id']==flow['order_qa']['order_id']
    assert snap['contact']['billing_country']=={'country_code':'CL','country_name':'Chile'}
    assert snap['terms_version']=='QA-TERMS-0.1' and snap['privacy_notice_version']=='QA-PRIVACY-0.1'
    serialized=json.dumps(preview,ensure_ascii=False).lower()
    assert 'transcript' not in serialized and FIXTURE_INITIAL.lower() not in serialized

def test_country_selector_and_post_payment_copy_are_public_contracts():
    for required in ['Selecciona tu país','País de facturación*','Términos y Condiciones de ENDRIAN','Política de Privacidad','Estamos verificando tu pago','Pago confirmado','Tu pedido fue recibido correctamente.','Esta simulación no inicia una construcción real ni habilita acceso a la solución.']:
        assert required in APP

def _started_payment(s, sid):
    summary_ready(s,sid); s.proposal_action(sid,'continue')
    s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',True,True,False,'','CL','Chile')
    s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True})
    started=s.create_or_reuse_payment_attempt(sid)
    return started['summary']['full_flow']['payment_qa']['reference']

def test_rejected_cancelled_and_expired_payments_have_controlled_recovery(tmp_path):
    s=service(tmp_path,'payment-recovery')
    rejected_ref=_started_payment(s,'REJECTED')
    rejected=s.qa_payment_resolve('REJECTED',rejected_ref,'rejected')['summary']['full_flow']
    assert rejected['state']=='S6' and rejected['order_qa'] is None
    recovered=s.payment_recovery('REJECTED')['summary']['full_flow']
    assert recovered['state']=='S5' and recovered['microstate']=='S5.CONTRACT-DATA'
    assert recovered['current_quotation_ref']==rejected['current_quotation_ref']

    cancelled_ref=_started_payment(s,'CANCELLED')
    cancelled=s.qa_payment_resolve('CANCELLED',cancelled_ref,'cancelled')['summary']['full_flow']
    assert cancelled['state']=='S5' and cancelled['microstate']=='S5.CONTRACT-DATA' and cancelled['order_qa'] is None

    expired_ref=_started_payment(s,'EXPIRED')
    expired=s.qa_payment_resolve('EXPIRED',expired_ref,'expired')['summary']['full_flow']
    old_ref=expired['current_quotation_ref']
    assert expired['state']=='S5' and expired['quotations'][-1]['status']=='EXPIRED' and expired['order_qa'] is None
    refreshed=s.proposal_action('EXPIRED','revalidate')['summary']['full_flow']
    assert refreshed['state']=='S5' and refreshed['current_quotation_ref']!=old_ref
    assert refreshed['quotations'][-1]['status']=='ISSUED'

def test_order_email_preview_is_snapshot_derived_and_uses_public_platform_labels(tmp_path):
    s=service(tmp_path,'order-preview'); sid='ORDER-PREVIEW'; ref=_started_payment(s,sid)
    flow=s.qa_payment_resolve(sid,ref,'confirmed')['summary']['full_flow']
    preview=flow['email_preview']; snapshot=flow['order_qa']['construction_request_snapshot']
    assert preview['platform_label']=='Entorno simulado de ENDRIAN'
    assert preview['features']==[item['label'] for item in snapshot['commitments']]
    assert preview['amount']==snapshot['amount']==89 and preview['currency']==snapshot['currency']=='USD'
    assert preview['delivery_window']==snapshot['delivery_window']=='2 a 5 días hábiles desde la confirmación del pago'
    assert preview['sent'] is False and preview['conversation_evidence_included'] is False
    assert snapshot['environment_id'] not in preview['body'] and snapshot['delivery_mode'] not in preview['body']

def test_public_payment_recovery_controls_are_present_without_qa_resolution_controls():
    assert '/api/full-flow/payment/recovery' in APP
    assert 'El pago no fue confirmado' in APP and 'Revisar antes de pagar' in APP
    for forbidden in ['Confirmar pago','Marcar expirado','qa-payment-confirm','qa-payment-reject']:
        assert forbidden not in APP

def test_v041_delivery_copy_is_consistent_and_old_qualifiers_are_absent(tmp_path):
    s=service(tmp_path,'v041-delivery'); sid='V041-DELIVERY'; ref=_started_payment(s,sid)
    flow=s.qa_payment_resolve(sid,ref,'confirmed')['summary']['full_flow']
    exact='2 a 5 días hábiles desde la confirmación del pago'
    assert APP.count(exact)>=1 and exact in flow['email_preview']['body']
    assert flow['quotations'][0]['conditions_version']=='QA-CONDITIONS-0.2'
    assert exact+'.' in flow['quotations'][0]['conditions']
    for removed in ['Plazo estimado de prueba','alcance cerrado e insumos disponibles']:
        assert removed not in APP and removed not in flow['email_preview']['body']

def test_structured_phone_and_billing_country_are_independent(tmp_path):
    s=service(tmp_path,'v041-phone'); sid='V041-PHONE'; summary_ready(s,sid); s.proposal_action(sid,'continue')
    out=s.complete_registration(sid,'Juan Pérez','juan.perez@example.com',False,False,False,'','CL','Chile','US','Estados Unidos','+1','2025550147')
    identity=out['summary']['full_flow']['qa_identity']
    assert identity['billing_country']=={'country_code':'CL','country_name':'Chile'}
    assert identity['phone']=={'country_code':'US','country_name':'Estados Unidos','calling_code':'+1','national_number':'2025550147','international_number':'+12025550147'}
    recovered=s.summary(s.recovery_target(identity['qa_identity_ref']))['full_flow']['qa_identity']
    assert recovered['phone']==identity['phone'] and recovered['billing_country']==identity['billing_country']

def test_two_acceptances_are_required_and_version_traced(tmp_path):
    s=service(tmp_path,'v041-accept'); sid='V041-ACCEPT'; prepayment_ready(s,sid)
    one=s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':False})
    assert one['ok'] is False and one['event']=='PREPAYMENT_CONFIRMATION_REQUIRED'
    both=s.complete_contracting(sid,{'contract_terms_accepted':True,'privacy_authorization_accepted':True}); flow=both['summary']['full_flow']; data=flow['contracting_data']
    assert flow['state']=='S6'
    assert data['contract_terms_acceptance']['quotation_ref']==flow['current_quotation_ref']
    assert data['contract_terms_acceptance']['quotation_version']==flow['quotations'][-1]['quotation_version']
    assert data['contract_terms_acceptance']['conditions_version']=='QA-CONDITIONS-0.2'
    assert data['contract_terms_acceptance']['terms_version']=='QA-TERMS-0.1'
    assert data['privacy_acceptance']['privacy_notice_version']=='QA-PRIVACY-0.1'
    assert data['contract_terms_acceptance']['solution_request_version_id']==data['privacy_acceptance']['solution_request_version_id']

def test_v041_public_contact_and_document_contracts():
    assert len(json.loads((ROOT/'config/billing_country_codes.json').read_text()))==249
    assert len(json.loads((ROOT/'config/phone_country_prefixes.json').read_text()))>=240
    for required in ['País de facturación*','Selecciona tu país','Prefijo','Número de teléfono','Documentos de prueba, no válidos para contratación real.','Términos y Condiciones de ENDRIAN','Política de Privacidad']:
        assert required in APP
    assert 'Condiciones de mi pedido' not in APP
    s2=APP[APP.index("} else if(state==='S2')"):APP.index("} else if(state==='S3')")]
    assert 'type="checkbox"' not in s2 and '+56' not in s2 and 'Chile' not in s2
    s5=APP[APP.index("} else if(state==='S5')"):APP.index("} else if(state==='S6')")]
    assert s5.count('type="checkbox"')==2
