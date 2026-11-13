# REV1 — Delta localizado requerido por auditoría independiente

## Fuente

`ENDRIAN_LAB_AGENTE_GUIA_QA_CANDIDATE_v0.1.zip`  
SHA-256: `3da74ee772e0ffd1d86dd9f0129a8e84813f33286812a0715e87d099ec005a02`

## 1. Acceso staging fail-closed — CORREGIDO

- `APP_ENV=staging` exige `STAGING_ACCESS_USER` + `STAGING_ACCESS_PASSWORD`.
- Falta de cualquiera produce error de arranque explícito.
- Staging exige además `COOKIE_SECURE=true`.
- `basic_auth_ok()` ya no interpreta secretos vacíos como acceso permitido.
- Pruebas específicas cubren configuración, boot real y HTTP 401/200 con Basic Auth.

## 2. `FLAG_HUMAN_REVIEW` — CONECTADO

- Se añadió `DeterministicModelSignalPolicy`.
- El modelo solo emite una señal estructurada validada.
- La política determinista local aplica `REVISIÓN HUMANA REQUERIDA`, invalida orientación/propuesta y mantiene bloqueados pago/orden/matriz.
- Prueba positiva: FLAG produce revisión humana.
- Prueba negativa: `NO_OP` no produce revisión.
- `FLAG_HUMAN_REVIEW` sin razón es inválido.
- Se retiró `DRAFT_ORIENTATION` del schema ejecutable porque no tenía consumidor real.
- El set de acciones declaradas debe coincidir exactamente con `CONSUMED_MODEL_ACTIONS` en pruebas.

## 3. Evidencia visual — DESCRIPCIÓN CORREGIDA

Las cuatro capturas existentes fueron renombradas como `STATIC_PARTIAL_*` y movidas a `evidence/static_partial/`. `evidence/README.md` declara expresamente que no prueban runtime FastAPI ni interacción E2E.

La evidencia real queda pendiente del staging servido: Desktop entrada, Desktop conversación/ruta, Mobile entrada, Mobile conversación/ruta, Precios Desktop y Precios Mobile.

## 4. QA no destructivo — CORREGIDO

- `core_v0_1/qa/run_qa.py` ya no modifica `docs/PENDING_AND_DEFECTS.md` ni resultados congelados.
- `agent_guide/qa/run_blackbox_qa.py` tampoco sobrescribe resultados congelados.
- Ambos escriben únicamente en `ENDRIAN_QA_OUTPUT_DIR` o en un directorio temporal externo.
- Prueba automatizada ejecuta ambas suites en ambos órdenes y verifica `hashes antes == hashes después` para todo `agent_guide/`.
- `guide_agent.py` conserva SHA-256 original `915ea83f85f025c6c84177b8b91646d2d379fea3bb38899442324a1d8ea934d2`.

## 5. Limpieza menor — CORREGIDA

- `.pytest_cache` excluida.
- `/health` no revela existencia de `OPENAI_API_KEY` ni model mode.
- Pagos, correo, órdenes productivas, producción y copy definitivo permanecen fuera de alcance.
