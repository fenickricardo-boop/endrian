from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")


def test_services_and_prices_have_independent_entries_and_panels():
    assert INDEX.count('id="servicesButton"') == 1
    assert INDEX.count('id="priceButton"') == 1
    assert '>Servicios<' in INDEX and '>Precios<' in INDEX
    assert 'id="agentsButton"' not in INDEX
    assert 'data-mobile-action="agents"' not in INDEX
    assert 'data-mobile-action="services"' in INDEX
    assert 'data-mobile-action="prices"' in INDEX
    assert 'id="servicesDrawer"' in INDEX and 'id="priceDrawer"' in INDEX


def test_public_content_is_exact_and_old_offer_is_not_rendered():
    expected = [
        "ENDRIAN Esencial", "ENDRIAN Especializado", "ENDRIAN Integral",
        "USD 39", "USD 89", "USD 149",
    ]
    for text in expected:
        assert text in INDEX
    assert "Agente personalizado" not in INDEX + APP
    assert "USD 79 · Precio de lanzamiento" not in INDEX + APP
    assert "¿Buscas una configuración para tu equipo o empresa?" not in INDEX + APP


def test_chat_explore_button_is_removed_and_panel_returns_preserve_session():
    intro = INDEX.split('id="conversationScroll"', 1)[1].split('id="history"', 1)[0]
    assert "Explorar agentes" not in intro
    assert 'id="exploreAgents"' not in INDEX
    assert "function closeServices(options)" in APP
    assert 'id="pricesReturn"' not in INDEX
    assert "$('#closePrices').onclick=()=>closePrices()" in APP
    assert "els.input.focus()" in APP


def test_general_contact_labels_and_layout_are_stable():
    assert INDEX.count('class="field-label"') >= 5
    assert '<span class="field-label">Nombre <span aria-hidden="true">*</span></span>' in INDEX
    assert '<span class="field-label">Apellido</span>' in INDEX
    assert '<span class="field-label">Correo <span aria-hidden="true">*</span></span>' in INDEX
    assert "general-contact-phone-row" in INDEX
    assert ".contact-form .field-label{display:inline-flex" in CSS
    assert ".general-contact-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)" in CSS
    assert "@media (max-width:520px)" in CSS and ".general-contact-grid{grid-template-columns:1fr}" in CSS
    assert "if(!country&&!number)" in APP
    assert "Completa el prefijo y el número" in APP
    assert "[object Object]" not in INDEX + APP


def test_commercial_price_does_not_replace_qa_flow_prices():
    full_flow = (ROOT / "app/full_flow.py").read_text(encoding="utf-8")
    assert '"especializado":89' in full_flow.replace(" ", "")
    assert '"esencial":39' in full_flow.replace(" ", "")
    assert "USD 79" not in full_flow

