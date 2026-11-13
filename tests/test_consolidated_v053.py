import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.customer_confirmation import build_confirmation, render_contract_pdf, render_email_html

ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'frontend/app.js').read_text(encoding='utf-8')
INDEX=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
CSS=(ROOT/'frontend/styles.css').read_text(encoding='utf-8')


def archived_order():
    return {
        'snapshot_sha256':'abc',
        'order':{
            'order_id':'END-20261013-0001','created_at':'2026-10-13T10:00:00+00:00',
            'construction_request_snapshot':{
                'solution_title':'Agente Profesional para gestión de atención por correo',
                'contact':{'name':'Persona Sintética','email':'persona@dominio.test'},
                'commitments':[{'item_id':'PRO-CAP-001','label':'Clasificar consultas.'}],
                'controls':[{'item_id':'PRO-CTRL-001','label':'Revisión antes del envío.'}],
                'exclusions':[{'item_id':'PRO-EX-001','label':'Sin envío autónomo.'}],
                'dependencies':[{'item_id':'PRO-DEP-001','label':'Acceso simulado.'}],
                'particular_conditions':[], 'platform_label':'Entorno de prueba de ENDRIAN',
                'delivery_label':'Acceso administrado', 'amount':20, 'currency':'USD',
                'delivery_window':'2 a 5 días hábiles','terms_version':'QA-TERMS-0.1',
                'privacy_notice_version':'QA-PRIVACY-0.1'
            }
        }
    }


def test_public_confirmation_projects_labels_only_without_mutating_snapshot():
    source=archived_order(); before=deepcopy(source)
    data=build_confirmation(source); html=render_email_html(data); pdf=render_contract_pdf(data)
    assert data['characteristics']==['Clasificar consultas.']
    assert data['controls']==['Revisión antes del envío.']
    assert data['exclusions']==['Sin envío autónomo.']
    assert data['dependencies']==['Acceso simulado.']
    assert 'item_id' not in html and 'PRO-CAP-001' not in html
    assert pdf.startswith(b'%PDF') and source==before


def test_missing_public_label_is_controlled_error():
    source=archived_order(); source['order']['construction_request_snapshot']['commitments']=[{'item_id':'PRO-CAP-001'}]
    with pytest.raises(ValueError, match='falta texto público válido'):
        build_confirmation(source)


def test_general_contact_is_namespaced_local_and_responsive():
    assert 'generalContactName' in INDEX and 'generalContactCountrySlot' in INDEX
    assert "renderGeneralContactControls" in APP and "validateGeneralContact" in APP
    assert "El mensaje no fue enviado ni almacenado" in APP
    assert "/api/" not in APP.split("$('#contactForm').addEventListener",1)[1].split("$('#privacyFooter')",1)[0]
    assert '.general-contact-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)' in CSS
    assert '@media (max-width:520px)' in CSS and '.general-contact-grid{grid-template-columns:1fr}' in CSS


def test_chat_scroll_waits_for_rendered_actions_and_preserves_reader_position():
    assert 'function nearChatBottom()' in APP
    assert 'requestAnimationFrame(()=>requestAnimationFrame' in APP
    assert "const target=els.special.lastElementChild||els.history.lastElementChild" in APP
    assert 'revealLatest(shouldFollow)' in APP
    assert 'scroll-padding-block:24px' in CSS


def test_confirmed_card_uses_short_visible_delivery_copy():
    state7=APP.split("} else if(state==='S7')",1)[1].split("} else if(state==='S8')",1)[0]
    assert "snapshot.delivery_window" in state7
    assert 'desde la confirmación del pago' not in state7


def test_catalog_price_and_offer_groups_are_provisional():
    catalog=json.loads((ROOT/'config/agents_catalog.json').read_text(encoding='utf-8'))
    frontend_catalog=json.loads((ROOT/'frontend/agents_catalog.json').read_text(encoding='utf-8'))
    assert catalog['agents']['avanzado']['price']=='Precio pendiente de aprobación · USD · Pago único'
    assert catalog['agents']['profesional']['price']=='Precio pendiente de aprobación · USD · Pago único'
    assert catalog['agents']['integral']['price']=='Revisión y cotización'
    assert catalog['agents']['premium']['price']=='Revisión y cotización'
    assert catalog['categories'][0]['agents']==['avanzado','profesional']
    assert catalog['categories'][1]['agents']==['integral','premium']
    assert frontend_catalog==catalog
