from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")


def service_panel():
    return INDEX.split('id="servicesDrawer"', 1)[1].split('id="priceDrawer"', 1)[0]


def test_services_initial_view_is_three_compact_cards_only():
    panel = service_panel()
    assert panel.count('class="service-summary-card"') == 3
    assert panel.count('class="service-open-detail"') == 3
    for name in ["ENDRIAN Esencial", "ENDRIAN Especializado", "ENDRIAN Integral"]:
        assert name in panel
    assert 'id="servicesReturn"' not in panel
    assert "Volver a la conversación" not in panel


def test_three_detail_templates_preserve_exact_authorized_fields():
    panel = service_panel()
    assert panel.count('data-service-detail="esencial"') == 1
    assert panel.count('data-service-detail="especializado"') == 1
    assert panel.count('data-service-detail="integral"') == 1
    for label in ["Necesidad", "Qué hacemos", "Qué recibes", "Diferencia de alcance"]:
        assert panel.count(f"<h4>{label}</h4>") == 3
    assert "Es una intervención localizada sobre algo existente. No rehace toda la solución." in panel
    assert "Resuelve una función principal completa. Va más allá de un ajuste puntual, sin coordinar todavía varias funciones relacionadas." in panel
    assert "Coordina varias funciones relacionadas dentro de una misma finalidad y solución." in panel


def test_service_navigation_is_back_plus_close_only():
    panel = service_panel()
    assert 'id="closeServices"' in panel
    assert 'id="serviceBack"' in panel
    assert 'aria-label="Volver a Servicios"' in panel
    assert 'class="service-back-icon"' in panel
    assert '<span>Volver a Servicios</span>' in panel
    assert "openServiceDetail" in APP
    assert "backToServices" in APP
    assert "resetServicesPanel" in APP
    assert "returnToConversation(els.servicesDrawer)" not in APP
    assert "servicesListScrollTop" in APP
    assert "focus({preventScroll:true})" in APP


def test_services_are_informational_and_have_no_prices():
    panel = service_panel()
    for price in ["USD 39", "USD 89", "USD 149"]:
        assert price not in panel
    assert "Consultar estos servicios no inicia una contratación." in panel


def test_responsive_contract_keeps_single_column_and_scrollable_detail():
    assert ".service-summary-cards{display:flex;flex-direction:column" in CSS
    assert ".services-panel-view{min-height:0;overflow-y:auto" in CSS
    assert ".service-detail-backbar{" in CSS and "position:sticky" in CSS
    assert "@media (max-width:520px)" in CSS
    assert ".service-open-detail{width:100%;height:38px;justify-self:stretch}" in CSS


def test_price_panel_uses_only_top_close_without_conversation_side_effects():
    assert 'id="pricesReturn"' not in INDEX
    assert '>Cerrar</button>' not in INDEX
    assert 'id="closePrices"' in INDEX
    assert "$('#closePrices').onclick=()=>closePrices()" in APP
    assert "pricesReturn" not in APP
