from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")


def test_public_journey_has_exact_four_authorized_steps():
    expected = [
        ("Conversación", "Cuéntanos qué necesitas."),
        ("Definición de tu solicitud", "Aclaramos contigo el alcance y lo que recibirás."),
        ("Revisión y pago", "Revisas tu propuesta y confirmas los datos antes de pagar."),
        ("Pedido recibido", "Confirmamos tu pago y registramos tu pedido."),
    ]
    assert "<h2>Tu recorrido</h2>" in APP
    assert "<h2>Recorrido QA</h2>" not in APP
    for title, description in expected:
        assert title in APP
        assert description in APP


def test_internal_state_to_public_journey_mapping_is_explicit():
    for mapping in [
        "states:['S0','S1']",
        "states:['S3','S4','SH']",
        "states:['S2','S5','S6']",
        "states:['S7','S8']",
    ]:
        assert mapping in APP
    assert "aria-current=\"step\"" in APP
    assert "journeyCompleted=['S7','S8'].includes(state)" in APP
    assert all(label in APP for label in ["Completado", "Etapa actual", "Pendiente"])


def test_sidebar_hides_internal_qa_nomenclature_from_normal_view():
    summary = APP.split("function summaryMarkup", 1)[1].split("function renderSummary", 1)[0]
    for internal_label in ["Registro QA", "Pago QA", "PaymentGate", "flow-state-chip"]:
        assert internal_label not in summary
    assert 'data-panel-mode="journey"' in summary


def test_chat_has_bounded_composition_internal_scroll_and_stable_composer():
    assert "height:clamp(620px,calc(100dvh - 150px),780px)" in CSS
    assert ".conversation-panel{display:flex;flex-direction:column;height:100%;min-height:0;overflow:hidden}" in CSS
    assert "overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable" in CSS
    assert ".composer-zone{flex:0 0 auto" in CSS
    assert "height:clamp(540px,calc(100dvh - 122px),760px)" in CSS


def test_new_messages_keep_existing_natural_auto_scroll():
    assert APP.count("scrollHeight") >= 3
    assert "behavior:'smooth'" in APP


def test_close_and_send_controls_use_centered_svg_icons_without_button_redesign():
    assert INDEX.count("control-icon-close") == 4
    assert INDEX.count("control-icon-arrow") == 1
    assert INDEX.count('viewBox="0 0 24 24"') == 6  # Incluye la flecha SVG de Volver a Servicios.
    assert "control-glyph" not in INDEX
    assert ".control-icon{" in CSS
    assert "transform:translate" not in CSS.split(".control-icon{", 1)[1].split("@media", 1)[0]
    assert ".close-button{" in CSS and ".send-button{" in CSS


def test_authorized_navigation_and_panels_remain_present():
    for label in ["Volver a ENDRIAN", "Servicios", "Precios", "Contacto", "Nueva conversación"]:
        assert label in INDEX
    assert 'id="agentsButton"' not in INDEX
    assert 'id="privacyFooter"' in INDEX
    assert 'id="contactForm"' in INDEX


def test_patch_does_not_add_new_backend_calls_or_conversational_model_controls():
    assert "MODEL_MODE" not in INDEX
    assert "fetch('/api/" not in APP
    assert "renderFlow()" in APP
    assert "PaymentGate" not in APP
