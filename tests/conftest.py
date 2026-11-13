from pathlib import Path
import os
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Keep default app imports from creating SQLite state inside the candidate tree.
os.environ.setdefault("APP_ENV", "local")
os.environ.setdefault("QA_DB_PATH", str(Path(tempfile.gettempdir()) / "endrian_rev1_pytest_default.db"))
os.environ.setdefault("COOKIE_SECURE", "false")
