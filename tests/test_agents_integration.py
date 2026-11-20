from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_agent_catalog_has_four_agents_and_complete_v141_public_sections():
    data=json.loads((ROOT/'config/agents_catalog.json').read_text(encoding='utf-8'))
    assert list(data['agents']) == ['avanzado','integral','profesional','premium']
    assert [c['label'] for c in data['categories']] == ['Ofertas principales','Revisión y cotización']
    assert data['categories'][0]['agents'] == ['avanzado','profesional']
    assert data['categories'][1]['agents'] == ['integral','premium']
    assert all([f['label'] for f in a['fields']] == [
        'Para qué puedes utilizarlo','Características de la configuración',
        'Beneficios de la entrega','Qué recibes'
    ] for a in data['agents'].values())
    assert data['agents']['avanzado']['price'] == 'Precio pendiente de aprobación · USD · Pago único'
    assert data['agents']['profesional']['price'] == 'Precio pendiente de aprobación · USD · Pago único'
    assert data['agents']['integral']['price'] == 'Revisión y cotización'
    assert data['agents']['premium']['price'] == 'Revisión y cotización'
    assert data['cta'] == 'Hablar con ENDRIAN'

def test_agent_identifiers_are_only_approved_linear_assets():
    assets=sorted(p.name for p in (ROOT/'frontend/assets/agents').glob('*.svg'))
    assert assets == ['ENDRIAN_AGENT_ID_AVANZADO.svg','ENDRIAN_AGENT_ID_INTEGRAL.svg','ENDRIAN_AGENT_ID_PREMIUM.svg','ENDRIAN_AGENT_ID_PROFESIONAL.svg']

def test_ui_contract_for_agents():
    html=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
    js=(ROOT/'frontend/app.js').read_text(encoding='utf-8')
    css=(ROOT/'frontend/styles.css').read_text(encoding='utf-8')
    assert 'Explorar agentes' not in html
    assert 'agentDetailScroll' not in html and 'talkWithEndrian' not in html
    assert 'endrian_agent_selection:' not in js
    assert 'openAgentExplorer' not in js and 'selectAgent' not in js
    assert '>Servicios<' in html and '>Precios<' in html
    assert 'text-overflow:clip' in css and 'overflow-wrap:anywhere' in css
    assert '@media (prefers-reduced-motion:reduce)' in css

def test_conversational_and_control_core_files_untouched():
    import hashlib
    expected={
      'agent_guide/core_v0_1/candidate/guide_agent.py':'915ea83f85f025c6c84177b8b91646d2d379fea3bb38899442324a1d8ea934d2',
      'app/model_adapter.py':'f73efdd1a29f16e7799d0f9cc94c943af9d3fb8cb302ac9d1b9fea5711910e3a',
    }
    for rel,sha in expected.items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha
