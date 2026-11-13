import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")


def catalog():
    return json.loads((ROOT / "frontend/agents_catalog.json").read_text(encoding="utf-8"))


def test_editorial_v141_is_complete_and_internal_notes_are_absent():
    data = catalog()
    expected = {
        "avanzado": "Un agente especializado: instrucciones, criterios, formato de resultado y pruebas para ese caso.",
        "integral": "Reglas, contexto y fuentes organizados para trabajar con consistencia en el entorno acordado.",
        "profesional": "Un agente preparado para clasificar, priorizar y organizar el seguimiento, con criterios acordados.",
        "premium": "Coordinación de etapas, fuentes o equipos y, si el alcance lo incluye, de herramientas definidas.",
    }
    assert {k: v["card_description"] for k, v in data["agents"].items()} == expected
    assert data["agents"]["profesional"]["card_need"] == "Un proceso de trabajo definido."
    public = json.dumps(data, ensure_ascii=False)
    for forbidden in ["usd 89", "usd 149", "usd 239", "evaluación comercial interna", "notas internas"]:
        assert forbidden not in public.lower()


def test_price_panel_uses_approved_modes_and_full_public_copy():
    data = catalog()
    assert data["categories"][0]["agents"] == ["avanzado", "profesional"]
    assert data["categories"][1]["agents"] == ["integral", "premium"]
    assert len(data["price_panel"]["delivery_steps"]) == 5
    assert "ENDRIAN no vende el modelo de IA ni una plataforma propia." in data["price_panel"]["delivery"]
    # The internal catalogue remains preserved but is not rendered in the public panels.
    assert "agentCatalog.price_panel" not in APP
    assert "USD 39" in INDEX and "USD 89" in INDEX and "USD 149" in INDEX


def test_general_contact_final_distribution_and_isolation():
    for identifier in [
        "generalContactName", "generalContactLastName", "generalContactEmail",
        "generalContactCountrySlot", "generalContactPhoneSlot",
        "generalContactSubject", "generalContactMessage",
    ]:
        assert f'id="{identifier}"' in INDEX
    assert "'País','Selecciona tu país'" in APP
    assert "general-contact-phone-row" in INDEX
    assert "El mensaje no fue enviado ni almacenado." in APP
    handler = APP.split("$('#contactForm').addEventListener", 1)[1].split("$('#privacyFooter')", 1)[0]
    assert "/api/" not in handler


def test_general_contact_validations_and_scrollbar_contract():
    assert "if(!country)" in APP
    assert "if(!country&&!number)" in APP
    assert "Completa el prefijo y el número" in APP
    assert "scrollbar-color:#0c6688 #021722" in CSS
    for selector in [".price-drawer", ".contact-drawer", ".country-picker-list"]:
        assert selector in CSS


def test_backend_and_frontend_catalogs_are_identical():
    assert (ROOT / "config/agents_catalog.json").read_bytes() == (ROOT / "frontend/agents_catalog.json").read_bytes()
