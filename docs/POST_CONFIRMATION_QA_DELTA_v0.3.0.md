# ENDRIAN Laboratorio — delta post-confirmación QA v0.3.0

## Identificación y alcance

- Base exacta: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.4.zip`.
- SHA-256 base/rollback: `50994f1d637cc4038ffb6ca0e8bc4e91066502e8839b5bdb26d3a42b8486e3f7`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`; sin producción, modelo real, correo real, pago real ni proveedor externo.
- Fixture: `QA-PROFESIONAL-01`, con identidad `QA Profesional 01 / qa.profesional.01@example.invalid`.

## Implementación

Se materializó el recorrido `Conversación → Definición → Confirmación de alcance → Identificación mínima → Cotización → Decisión → Datos de contratación QA → PaymentGate → Pago QA → Orden → Seguimiento`.

La salida visible se construye desde `client_output`, mediante allowlist. `conversation_evidence` permanece interno y se elimina del resumen/API pública. La cotización y su vista previa de correo son locales, versionadas y no enviadas (`sent=false`, `provider=null`, `external_service=false`). El PaymentGate calcula trece condiciones. Una corrección material conserva la versión previa como `SUPERSEDED_SCOPE_CHANGE` con microestado `S5.Q-SUPERSEDED`. La orden queda fijada a versión de alcance, cotización y referencia de pago; el replay devuelve la misma orden.

## Archivos modificados

- `app/full_flow.py`
- `app/service.py`
- `app/main.py`
- `frontend/app.js`
- `tests/test_api.py`
- `tests/test_full_flow_v02.py`
- `tests/test_service_flow.py`
- `tests/test_ux_spatial_v023.py`
- documentación, resultados y manifests propios de v0.3.0.

## Invariantes byte-identical respecto de v0.2.4

Permanecen idénticos todos los demás archivos de la base, en particular `frontend/index.html`, `frontend/styles.css`, catálogos, assets, `agent_guide`, adaptadores/modelo, seguridad, launchers, configuración, infraestructura y documentación previa. El inventario SHA-256 permite verificarlo.

## QA ejecutado

- `python -m pytest -q`: **60 passed**.
- `python -m py_compile app/*.py`: PASS.
- `node --check frontend/app.js`: PASS.
- Arranque local y `/health`: HTTP 200.
- Navegador remoto: no pudo acceder a `127.0.0.1` por bloqueo del propio entorno; no se atribuye PASS visual manual. El candidato queda listo para esa revisión local de Eduardo + Lía.
- No se realizó ninguna llamada externa. La CSP conserva `connect-src 'self'`.

## Rollback

Detener el servidor, retirar la carpeta candidata v0.3.0 y restaurar/descomprimir el ZIP v0.2.4 cuyo SHA-256 figura arriba. El rollback es el artefacto original preservado, no una reconstrucción.

## Estado propuesto

`CANDIDATO QA v0.3.0 / APTO PARA REVISIÓN MANUAL EDUARDO + LÍA / SIN DECLARAR CIERRE`.
