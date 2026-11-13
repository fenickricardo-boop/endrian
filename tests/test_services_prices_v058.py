from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")


def test_menu_order_and_mobile_actions_are_exact():
    desktop = INDEX.split('<nav class="header-nav"', 1)[1].split('</nav>', 1)[0]
    assert desktop.index("Volver a ENDRIAN") < desktop.index("Servicios") < desktop.index("Precios") < desktop.index("Contacto") < desktop.index("Nueva conversación")
    assert 'data-mobile-action="services"' in INDEX
    assert 'data-mobile-action="prices"' in INDEX
    assert 'data-mobile-action="commercial"' not in INDEX


def test_three_service_cards_include_every_authorized_section():
    assert INDEX.count('class="service-summary-card"') == 3
    assert INDEX.count('data-service-detail=') == 3
    for label in ["Necesidad", "Qué hacemos", "Qué recibes", "Diferencia de alcance"]:
        assert INDEX.count(f"<h4>{label}</h4>") == 3
    exact_leads = [
        "Mejoramos algo concreto de lo que ya utilizas.",
        "Creamos agentes especializados y soluciones preparadas para una función concreta.",
        "Coordinamos varias funciones relacionadas en una misma solución.",
    ]
    for text in exact_leads:
        assert text in INDEX


def test_prices_and_public_notes_are_exact():
    expected = {
        "ENDRIAN Esencial": "USD 39",
        "ENDRIAN Especializado": "USD 89",
        "ENDRIAN Integral": "USD 149",
    }
    for name, price in expected.items():
        assert name in INDEX and price in INDEX
    assert "Precios vigentes de los tres servicios. Consultarlos no te obliga a elegir ni contratar." in INDEX
    assert "Consultar estos servicios no inicia una contratación." in INDEX


def test_drawer_controls_preserve_session_focus_and_single_open_panel():
    assert "publicDrawers().forEach(hideDrawer)" in APP
    assert "function returnToConversation(drawer)" in APP
    assert "els.input.focus()" in APP
    assert "document.addEventListener('keydown'" in APP and "e.key==='Escape'" in APP
    panel_logic = APP.split("let lastDrawerTrigger", 1)[1].split("function openInfo", 1)[0]
    assert "/api/session/new" not in panel_logic
    assert "send(" not in panel_logic


def test_contact_visual_normalization_is_scoped_and_message_stays_taller():
    assert ".contact-form input,.contact-form .country-picker-input{height:42px;min-height:42px" in CSS
    assert ".contact-form .phone-number-label input,.contact-form .phone-controls .country-picker-input{height:42px;min-height:42px;margin:0}" in CSS
    assert ".contact-form textarea{resize:vertical;min-height:130px}" in CSS
    assert ".contact-form .phone-controls{grid-template-columns:104px minmax(0,1fr)}" in CSS
    assert "if(!country&&!number)" in APP
    assert "Completa el prefijo y el número" in APP
