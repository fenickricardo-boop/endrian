from __future__ import annotations
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8000/"

def wait_ready(proc, seconds=20):
    deadline=time.time()+seconds
    while time.time()<deadline:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(URL+"health", timeout=0.5) as r:
                if r.status==200:
                    return True
        except Exception:
            time.sleep(0.25)
    return False

def main():
    env=os.environ.copy()
    env.update({
        "APP_ENV":"QA_CONTROLLED_TEST_ONLY",
        "MODEL_MODE":"deterministic",
        "COOKIE_SECURE":"false",
        "QA_DB_PATH":"data/full_flow_qa.db",
        "QA_EPHEMERAL_REGISTRATION":"false",
        "PYTHONDONTWRITEBYTECODE":"1",
    })
    cmd=[sys.executable,"-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000"]
    print("ENDRIAN Laboratorio QA v0.5.15 — NO PRODUCCIÓN")
    print("Iniciando servidor local…")
    proc=subprocess.Popen(cmd,cwd=str(ROOT),env=env)
    try:
        if not wait_ready(proc):
            raise RuntimeError("El servidor local no inició correctamente. Revisa que las dependencias de requirements.txt estén instaladas.")
        webbrowser.open(URL)
        print(f"Abierto: {URL}")
        print("Para cerrar el Laboratorio y detener el servidor, vuelve a esta ventana y presiona Ctrl+C.")
        proc.wait()
    except KeyboardInterrupt:
        print("\nCerrando servidor QA…")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
        print("Servidor QA detenido. No quedan procesos de este lanzador en ejecución.")

if __name__=="__main__":
    main()
