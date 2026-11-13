from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
COPY = json.loads((ROOT / "config" / "ui_copy.json").read_text(encoding="utf-8"))


def test_header_navigation_exact_visible_set():
    for label in ["Volver a ENDRIAN", "Servicios", "Precios", "Contacto", "Nueva conversación"]:
        assert label in INDEX
    assert 'id="agentsButton"' not in INDEX
    assert 'id="howButton"' not in INDEX
    assert 'id="privacyButton"' not in INDEX
    assert 'id="profileButton"' not in INDEX


def test_privacy_remains_secondary():
    assert 'id="privacyFooter"' in INDEX
    assert 'Política de Privacidad' in INDEX
    assert 'id="contactPrivacyLink"' in INDEX


def test_help_starters_removed_completely_from_runtime_ui():
    assert "O explora algunos temas de ayuda" not in INDEX
    assert 'id="startersWrap"' not in INDEX
    assert 'id="starters"' not in INDEX
    assert "cfg.copy.starters" not in APP
    assert "starters" not in COPY


def test_contact_panel_is_local_only_and_has_requested_fields():
    for field in ['id="generalContactName"', 'id="generalContactEmail"', 'id="generalContactSubject"', 'id="generalContactMessage"']:
        assert field in INDEX
    assert 'id="generalContactCountrySlot"' in INDEX
    assert 'id="generalContactPhoneSlot"' in INDEX
    assert "Enviar mensaje" in INDEX
    assert "no envía ni almacena información" in INDEX
    assert "contactForm" in APP
    assert "/api/" not in APP.split("$('#contactForm').addEventListener", 1)[1].split("$('#privacyFooter')", 1)[0]


def test_public_services_and_prices_are_independent_from_internal_catalog():
    assert (ROOT / "config" / "agents_catalog.json").exists()  # internal catalogue preserved
    assert "USD 39" in INDEX and "USD 89" in INDEX and "USD 149" in INDEX
    assert "USD 79 · Precio de lanzamiento" not in INDEX + APP
    assert "agentCatalog.categories" not in APP
    assert "cfg.copy.prices.categories" not in APP
    assert "categories" not in COPY["prices"]


def test_agent_and_price_panels_use_integrated_drawer_language():
    assert ".price-drawer,.contact-drawer" in CSS
    assert ".agent-explorer" in CSS
    assert "background:linear-gradient(180deg,#052b41,#031b2b)" in CSS


def test_close_and_arrow_controls_have_explicit_centering():
    assert ".close-button{" in CSS and "align-items:center" in CSS and "justify-content:center" in CSS
    assert ".send-button{" in CSS
    assert ".price-agent-arrow,.agent-option-arrow" in CSS
    assert "place-items:center" in CSS


def test_conversational_and_backend_authority_not_redefined_in_ux_patch():
    # The UX patch does not introduce new flow endpoints or model behavior.
    assert "renderFlow()" in APP
    assert "PaymentGate" not in APP
    assert "MODEL_MODE" not in INDEX
