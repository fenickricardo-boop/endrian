from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_frontend_secret_reference():
    for rel in ["frontend/index.html","frontend/app.js","frontend/styles.css","config/ui_copy.json"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "OPENAI_API_KEY" not in text
        assert "sk-" not in text


def test_attachments_disabled_and_price_provisional():
    html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    copy = (ROOT / "config/ui_copy.json").read_text(encoding="utf-8")
    assert "disabled" in html
    assert "provisional" in copy.lower()
