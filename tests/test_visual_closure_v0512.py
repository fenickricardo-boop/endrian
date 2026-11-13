from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "frontend/styles.css").read_text(encoding="utf-8")
INDEX = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
APP = (ROOT / "frontend/app.js").read_text(encoding="utf-8")


def test_typographic_hierarchy_is_shared_and_readable():
    assert ".service-summary-card h3{margin:0;color:#f2fbff;font-size:16px;line-height:1.3}" in CSS
    assert ".service-summary-card .service-lead{margin:7px 0 0;color:#c9dee6;font-size:12px;line-height:1.5;font-weight:500" in CSS
    assert ".service-detail-sheet>h3{margin:0;color:#f2fbff;font-size:19px;line-height:1.3}" in CSS
    assert ".service-detail-section p{margin:0;color:#aac2cd;font-size:12px;line-height:1.62" in CSS
    assert ".pricing-row h3{margin:0 0 5px;color:#effbff;font-size:15px;line-height:1.35}" in CSS
    assert ".pricing-row p{margin:0;color:#a9c2cf;font-size:12px;line-height:1.55}" in CSS


def test_contact_spacing_is_compact_without_changing_fields():
    assert ".contact-form{display:flex;flex-direction:column;gap:10px;margin-top:8px}" in CSS
    assert "gap:9px 14px;align-items:start" in CSS
    assert ".contact-form .field-error:empty{display:none}" in CSS
    assert ".contact-form textarea{resize:vertical;min-height:130px}" in CSS
    for field_id in (
        "generalContactName",
        "generalContactLastName",
        "generalContactEmail",
        "generalContactSubject",
        "generalContactMessage",
    ):
        assert f'id="{field_id}"' in INDEX


def test_closed_visual_contracts_remain_intact():
    assert 'id="pricesReturn"' not in INDEX
    assert 'id="closePrices"' in INDEX
    assert "$('#closePrices').onclick=()=>closePrices()" in APP
    for price in ("USD 39", "USD 89", "USD 149"):
        assert price in INDEX
    assert "Volver a Servicios</span></button>" in INDEX
