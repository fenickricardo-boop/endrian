from dataclasses import replace
import pytest

from app.config import settings as base_settings, validate_runtime_settings
from app.security import basic_auth_ok


def test_staging_fails_closed_when_access_secret_missing():
    with pytest.raises(RuntimeError, match="fail-closed"):
        validate_runtime_settings(replace(base_settings, app_env="staging", staging_user="", staging_password="secret"))
    with pytest.raises(RuntimeError, match="fail-closed"):
        validate_runtime_settings(replace(base_settings, app_env="staging", staging_user="qa", staging_password=""))


def test_staging_accepts_config_only_when_both_secrets_present():
    validate_runtime_settings(replace(base_settings, app_env="staging", staging_user="qa", staging_password="secret", cookie_secure=True))


def test_basic_auth_never_opens_when_expected_credentials_are_missing():
    class RequestStub:
        headers = {}
    assert basic_auth_ok(RequestStub(), "", "") is False


def test_actual_app_boot_fails_in_staging_without_access_secrets(tmp_path):
    import os, subprocess, sys
    env = os.environ.copy()
    env["APP_ENV"] = "staging"
    env.pop("STAGING_ACCESS_USER", None)
    env.pop("STAGING_ACCESS_PASSWORD", None)
    env["QA_DB_PATH"] = str(tmp_path / "boot.db")
    env["PYTHONPATH"] = str(__import__('pathlib').Path(__file__).resolve().parents[1])
    proc = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=env["PYTHONPATH"], env=env, capture_output=True, text=True, check=False,
    )
    assert proc.returncode != 0
    assert "Staging access is fail-closed" in (proc.stderr + proc.stdout)


def test_staging_runtime_requires_basic_auth_and_health_is_minimal(tmp_path):
    import os, subprocess, sys, textwrap
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.update({
        "APP_ENV": "staging",
        "STAGING_ACCESS_USER": "qa-user",
        "STAGING_ACCESS_PASSWORD": "qa-pass",
        "QA_DB_PATH": str(tmp_path / "runtime.db"),
        "PYTHONPATH": str(root),
        "COOKIE_SECURE": "true",
    })
    code = textwrap.dedent('''
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as c:
            assert c.get('/').status_code == 401
            h = c.get('/health')
            assert h.status_code == 200
            assert h.json() == {'ok': True, 'status': 'QA / NO PRODUCCIÓN'}
            assert c.get('/', auth=('qa-user','qa-pass')).status_code == 200
        print('PASS')
    ''')
    proc = subprocess.run([sys.executable, "-c", code], cwd=str(root), env=env, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "PASS" in proc.stdout


def test_staging_rejects_insecure_cookie_setting():
    with pytest.raises(RuntimeError, match="COOKIE_SECURE"):
        validate_runtime_settings(replace(base_settings, app_env="staging", staging_user="qa", staging_password="secret", cookie_secure=False))
