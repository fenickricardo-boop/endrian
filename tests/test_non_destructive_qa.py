from pathlib import Path
import hashlib
import os
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent_guide"


def snapshot_agent_tree():
    out = {}
    for p in sorted(AGENT.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        out[str(p.relative_to(AGENT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


@pytest.mark.parametrize("order", [
    ("core", "blackbox"),
    ("blackbox", "core"),
])
def test_qa_suites_do_not_mutate_frozen_agent_files(order):
    scripts = {
        "core": AGENT / "core_v0_1" / "qa" / "run_qa.py",
        "blackbox": AGENT / "qa" / "run_blackbox_qa.py",
    }
    before = snapshot_agent_tree()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # No ENDRIAN_QA_OUTPUT_DIR on purpose: each suite must default to an external temp directory.
    env.pop("ENDRIAN_QA_OUTPUT_DIR", None)
    for name in order:
        proc = subprocess.run(
            [sys.executable, str(scripts[name])],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
        assert '"global_result": "PASS"' in proc.stdout
    after = snapshot_agent_tree()
    assert before == after
