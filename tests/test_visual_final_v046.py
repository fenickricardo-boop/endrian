from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
SERVICE = (ROOT / "app" / "service.py").read_text(encoding="utf-8")

def test_country_and_phone_picker_visual_contracts():
    assert ".billing-country-picker .country-picker-list{overflow-x:hidden}" in CSS
    assert "display:block;white-space:normal" in CSS
    assert ".phone-prefix-picker .country-picker-list button span,.phone-prefix-picker .country-picker-list button small{font:inherit;font-weight:inherit;color:inherit}" in CSS
    assert "aria-label=\"${escapeHtml(x.name)}, ${escapeHtml(x.code)} ${escapeHtml(x.calling_code)}\"" in APP

def test_scroll_inset_and_public_message_cleanup():
    assert ".conversation-scroll{flex:1 1 auto;min-height:0;margin-block:8px" in CSS
    assert "Acción aplicada." not in APP
    assert "Acción aplicada." not in SERVICE
    assert "Conservamos tu solicitud. No necesitas intentar pagar nuevamente." in APP

def test_payment_transition_is_silent_and_private_console_remains_isolated():
    assert "'/api/full-flow/payment/start',{}, {silent:true}" in APP
    assert "if(!options.silent&&out.message)appendMessage('assistant',out.message)" in APP
    assert "QA_CONTROLLED_TEST_ONLY" in (ROOT / "qa_control" / "payment.html").read_text(encoding="utf-8")
