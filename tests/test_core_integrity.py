from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent_guide"


def test_preserved_v02_manifest():
    manifest = AGENT / "MANIFEST_SHA256.txt"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        expected, rel = line.split(None, 1)
        data = (AGENT / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected, rel
