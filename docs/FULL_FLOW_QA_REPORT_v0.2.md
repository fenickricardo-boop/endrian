# ENDRIAN LAB FULL FLOW QA v0.2 — informe final

## Estado
`IMPLEMENTACIÓN CONTROLADA LOCAL / QA SIMULADO / NO PRODUCCIÓN / SIN DEPLOY / SIN GITHUB / SIN RAILWAY / MODELO REAL NO CONECTADO`

## Fuente verificada
- Fuente: `ENDRIAN_LAB_AGENTES_QA_v0.1.2.zip`
- SHA-256 esperado/verificado: `91e42504d0b1cf4bb1a1c7bb8b13b560ac7579678c3d376dc8f5d64a79e7d5a1`
- La fuente original no fue modificada.
- Una copia byte-idéntica de rollback se conserva en `rollback/ENDRIAN_LAB_AGENTES_QA_v0.1.2_SOURCE.zip`.

## Implementación
Se añadió una máquina de recorrido QA determinista sobre la capa de integración, sin modificar el núcleo congelado `agent_guide/core_v0_1/candidate/guide_agent.py`.

Recorrido: `S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8`; `SH` es salida protegida.

Capacidades QA:
- comprensión preliminar y confirmación;
- registro exclusivamente sintético (`qa_identity_ref`, alias y `example.invalid`);
- dimensionamiento editable;
- orientación con retornos por materialidad;
- propuesta simulada con valores QA aprobados;
- PaymentGate autoritativo de nueve condiciones;
- pago local simulado con estados y retornos deterministas;
- orden QA idempotente;
- vista previa de correo persistida, nunca enviada;
- matriz interna posterior al pago;
- seguimiento y recuperación por `qa_identity_ref`;
- revisión humana con pago bloqueado;
- reembolsos como controles QA avanzados sobre la misma orden.

## Valores QA
- Monto: `$123.456 CLP` — solo simulación.
- Plazo: `10 días hábiles QA` — no comercial.
- Vigencia: `7 días QA`.
- Orden: `END-QA-AAAAMMDD-NNNN` con secuencia local SQLite.
- Pago: `PAY-QA-<identificador>`.

## Archivos funcionales modificados desde v0.1.2
- `app/main.py`
- `app/service.py`
- `app/session_repository.py`
- `frontend/app.js`
- `frontend/index.html`
- `frontend/styles.css`
- pruebas heredadas actualizadas para el nuevo recorrido completo.

## Archivos funcionales añadidos
- `app/full_flow.py`
- `START_LAB_QA.bat`
- `start_lab_qa.py`
- `README_LOCAL_QA.md`
- `tests/test_full_flow_v02.py`
- documentos fuente v0.2.1 bajo `docs/reference/`
- evidencia y resultados QA bajo `evidence/full_flow/` y `qa_results/full_flow/`.

## QA ejecutado
- `pytest`: **60/60 PASS**.
- Núcleo QA heredado: **PASS**.
- Black-box heredado: **PASS**.
- `node --check frontend/app.js`: **PASS**.
- Inicio FastAPI real local + `/health`: **PASS**.
- Browser visual QA: **18/18 PASS** (Desktop/Mobile, controles visibles sin overflow, selector sin recortes, foco/Tab/Escape y Reduced Motion).
- Sin red externa: **PASS**; prueba funcional completada con `socket.connect` bloqueado.
- Rollback exacto: **PASS**.

## F01–F18
Todos **PASS**. Resultado detallado: `qa_results/full_flow/F01_F18_RESULTS.json`.

## C01–C07
Todos **PASS**. Resultado detallado: `qa_results/full_flow/C01_C07_RESULTS.json`.

## R01–R09
Todas **PASS**. Resultado detallado: `qa_results/full_flow/R01_R09_RESULTS.json`.

## Limitaciones reales
1. El modelo real no está conectado ni validado; `START_LAB_QA.bat` fuerza `MODEL_MODE=deterministic`.
2. Todo registro, pago, orden, correo, matriz y reembolso es simulado y local.
3. La recuperación depende de que el SQLite local y el snapshot sigan dentro del TTL vigente o no hayan sido limpiados manualmente.
4. El lanzador requiere Python y las dependencias de `requirements.txt` instaladas en el equipo.
5. El copy añadido para estados nuevos permanece **provisional QA**; no modifica el copy aprobado de las cuatro fichas de agentes.
6. Las capturas visuales fueron producidas con Chromium usando el HTML/CSS/JS real y estados API simulados del mismo candidato; la funcionalidad backend se verificó separadamente mediante tests y arranque FastAPI real.

## No modificación de entornos externos
No se accedió ni modificó GitHub, Railway, staging, dominio, credenciales ni producción durante esta implementación.
