# QA REPORT — ENDRIAN LAB + Agente Guía Candidate REV1

## Dictamen

**REV1 CORREGIDO / QA / NO PRODUCCIÓN / SIN CREDENCIALES / MODELO REAL NO EJECUTADO.**

## Fuente y alcance

- Fuente: `ENDRIAN_LAB_AGENTE_GUIA_QA_CANDIDATE_v0.1.zip`.
- SHA-256 fuente verificado: `3da74ee772e0ffd1d86dd9f0129a8e84813f33286812a0715e87d099ec005a02`.
- Lógica de control preservada: `agent_guide/core_v0_1/candidate/guide_agent.py` conserva SHA-256 `915ea83f85f025c6c84177b8b91646d2d379fea3bb38899442324a1d8ea934d2`.
- REV1 modifica únicamente integración/seguridad/tests/documentación y los runners QA necesarios para que sean no destructivos.

## Suites ejecutadas

- Núcleo AGG-QA01–AGG-QA20: **20/20 PASS**.
- Caja negra `handle_message`: **16/16 PASS**.
- Pytest candidato REV1: **26/26 PASS**.
- Python compile: **PASS**.
- Escaneo básico de secretos `sk-*`: **PASS / 0 hallazgos**.
- QA runners no destructivos: **PASS**; snapshot de todo `agent_guide/` idéntico antes/después.

Resultados conservados en `qa_results/` y procedimiento en `docs/REV1_REPRODUCIBLE_QA.md`.

## Hallazgos REV1 cerrados

### 1. Acceso staging fail-closed — PASS

- `APP_ENV=staging` sin user/password: boot falla explícitamente.
- Falta cualquiera de los dos secretos: boot falla.
- `COOKIE_SECURE=false` en staging: boot falla.
- Con ambos secretos y cookie segura: aplicación arranca.
- `/` sin Basic Auth: HTTP 401.
- `/` con credenciales correctas: HTTP 200.
- `/health`: público y mínimo; no expone model mode ni presencia de `OPENAI_API_KEY`.

### 2. `FLAG_HUMAN_REVIEW` — PASS

- Schema valida razón obligatoria.
- `DeterministicModelSignalPolicy` consume la señal validada.
- Prueba positiva: señal produce `REVISIÓN HUMANA REQUERIDA`, invalida orientación/propuesta y no crea orden.
- Prueba negativa: `NO_OP` no produce revisión humana.
- El modelo no escribe directamente el estado: la transición la aplica la política determinista local.
- `DRAFT_ORIENTATION` fue retirado del schema ejecutable porque no tenía consumidor real.
- Test de contrato: acciones declaradas == acciones consumidas.

### 3. QA no destructivo — PASS

Los runners de núcleo y caja negra escriben solo en `ENDRIAN_QA_OUTPUT_DIR` o en un directorio temporal externo. Se ejecutaron en ambos órdenes y los hashes de `agent_guide/` fueron idénticos antes/después.

### 4. Evidencia visual — CORREGIDA / E2E PENDIENTE

Las cuatro capturas incluidas son ahora `evidence/static_partial/STATIC_PARTIAL_*`. Se documentan exclusivamente como evidencia estática parcial. **No se declara PASS E2E visual del runtime.**

El siguiente gate de staging debe capturar desde la aplicación realmente servida:

1. Desktop entrada.
2. Desktop conversación/ruta.
3. Mobile entrada.
4. Mobile conversación/ruta.
5. Precios Desktop.
6. Precios Mobile.

## Modelo real

Preparado, no ejecutado:

- OpenAI Responses API.
- `gpt-5.6-terra` configurable.
- reasoning low.
- Structured Outputs.
- `store=False`.
- `max_output_tokens=700` default.
- máximo un retry.
- fallback determinista.

**NO VERIFICADO:** conducta real, latencia, coste real, adherencia conversacional, errores de proveedor y hard cap US$20.

## Fuera de alcance

No se desplegó Railway, no se creó API key, no se generó cargo, y permanecen fuera registro productivo, correo real, pagos, órdenes productivas, recuperación productiva, producción y copy comercial definitivo.
