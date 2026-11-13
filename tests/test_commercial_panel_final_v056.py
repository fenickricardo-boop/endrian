from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")


def test_obsolete_single_offer_is_absent_from_current_public_panels():
    public = INDEX + APP
    for obsolete in ["Agente personalizado", "USD 79 · Precio de lanzamiento", "precio de lanzamiento", "¿Buscas una configuración para tu equipo o empresa?"]:
        assert obsolete not in public


def test_authorized_service_and_price_sets_are_complete():
    assert INDEX.count('class="service-summary-card"') == 3
    assert INDEX.count('data-service-detail=') == 3
    assert INDEX.count('class="pricing-row"') == 3
    for service in ["ENDRIAN Esencial", "ENDRIAN Especializado", "ENDRIAN Integral"]:
        assert service in INDEX
    for price in ["USD 39", "USD 89", "USD 149"]:
        assert price in INDEX


def test_service_close_and_price_return_do_not_start_a_session():
    assert INDEX.count("Volver a la conversación") == 0
    assert 'id="closeServices"' in INDEX
    assert 'id="serviceBack"' in INDEX and 'Volver a Servicios</span></button>' in INDEX
    assert "function closeServices(options)" in APP
    assert 'id="pricesReturn"' not in INDEX
    assert "$('#closePrices').onclick=()=>closePrices()" in APP
    service_logic = APP.split("let lastServiceCardTrigger", 1)[1].split("function openInfo", 1)[0]
    assert "/api/session/new" not in service_logic
    assert "send(" not in service_logic


def test_qa_prices_remain_separate():
    full_flow = (ROOT / "app/full_flow.py").read_text(encoding="utf-8").replace(" ", "")
    assert 'QA_PRICES={"esencial":39,"especializado":89,"integral":149}' in full_flow
    assert "USD79" not in full_flow

