from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'frontend/styles.css').read_text(encoding='utf-8')
HTML = (ROOT / 'frontend/index.html').read_text(encoding='utf-8')


def test_mobile_qa_banner_wraps_without_horizontal_clip():
    assert '.qa-warning{' in CSS
    assert 'white-space:normal' in CSS
    assert 'overflow-wrap:anywhere' in CSS
    assert 'max-width:calc(100vw - 24px)' in CSS


def test_mobile_explore_agents_remains_in_normal_flow_below_intro():
    assert '.intro-message{margin-bottom:16px}' in CSS
    assert '.agent-explore-entry{' in CSS
    assert 'position:relative' in CSS
    assert 'clear:both' in CSS


def test_mobile_selected_agent_card_can_grow_without_overlap():
    assert 'grid-template-rows:auto auto' in CSS
    assert 'height:auto' in CSS
    assert '.agent-selection-line>div{min-width:0}' in CSS
    assert 'grid-row:2' in CSS
    assert 'overflow-wrap:anywhere' in CSS


def test_mobile_route_actions_stack_when_width_is_constrained():
    assert re.search(r'\.card-actions\{[^}]*flex-direction:column', CSS, re.S)
    assert re.search(r'\.card-actions \.primary-cta,\s*\.card-actions \.secondary-cta\{[^}]*width:100%', CSS, re.S)


def test_mobile_agent_selector_cards_expand_for_full_copy():
    assert re.search(r'\.agent-option\{[^}]*min-height:0;[^}]*height:auto', CSS, re.S)
    assert re.search(r'\.agent-option strong,\s*\.agent-option small\{[^}]*white-space:normal;[^}]*overflow:visible', CSS, re.S)


def test_desktop_header_has_single_wordmark_source():
    # The SVG itself contains the ENDRIAN wordmark. HTML must not add a second ENDRIAN text node.
    header = HTML.split('<header class="lab-header">', 1)[1].split('</header>', 1)[0]
    assert header.count('ENDRIAN_LOCKUP_HORIZONTAL_DARK.svg') == 1
    assert '>ENDRIAN<' not in header
    # Mobile sticky header must be visually opaque so scrolling content cannot show through it.
    assert re.search(r'@media \(max-width:900px\).*?\.lab-header\{[^}]*background:#000e19;[^}]*isolation:isolate;[^}]*box-shadow:', CSS, re.S)
    assert re.search(r'\.lab-header::before\{[^}]*position:absolute;[^}]*inset:0;[^}]*background:#000e19;', CSS, re.S)
