# ENDRIAN Laboratorio — Integración visual de agentes — QA v0.1

## Base y autoridad
- Base congelada: `72548d8e8a0b58d521a8ec5fc4b02c7cecdbbcd2`.
- Handoff visual: `ENDRIAN_LAB_AGENTES_INTEGRATION_HANDOFF_v1.0.zip`.
- SHA-256 handoff: `9d26bf20c4932b6a3238ef478a35b527b0cc72ee1beb948cc714e39f3b861e99` — verificado.
- Copy: `ENDRIAN_AUDITORIA_EDITORIAL_FICHAS_AGENTES_v1.1`, versión consolidada pública.

## Preflight
- Repositorio/commit de partida: PASS exacto.
- Copy editorial v1.1: DISPONIBLE y leído.
- Cambios localizados: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`, nuevo `frontend/agents_catalog.json`, `config/agents_catalog.json`, cuatro SVG aprobados en `frontend/assets/agents/`, test y este reporte.
- Núcleo determinista, `app/service.py`, `app/model_adapter.py`: preservados byte a byte.
- Dependencias nuevas: ninguna.
- Railway/modelo real/variables protegidas: no tocados.
- Rollback: volver al commit base congelado; la integración vive en rama QA independiente.

## Implementación
- `Explorar agentes` secundario dentro del chat.
- Selector con `Uso personal` y `Negocios y equipos`.
- Cuatro agentes con identificadores lineales aprobados.
- Ficha continua con 10 campos públicos, scroll interno, wrap completo, precio provisional y CTA.
- Desktop: modal superpuesto. Mobile: sheet expandido/pantalla casi completa con footer persistente.
- `Hablar con ENDRIAN`: conserva la conversación, almacena la selección por `session_id`, cierra la ficha y vuelve al chat mostrando el estado de selección.
- Cambio posterior de agente sin nueva sesión.
- Escape, foco inicial, trampa de foco y restauración de foco.
- `prefers-reduced-motion` sin animaciones/transiciones del nuevo módulo.

## QA
- `pytest`: 30/30 PASS.
- Núcleo AGG-QA01–QA20: PASS.
- Caja negra determinista: PASS.
- `node --check frontend/app.js`: PASS.
- UI browser harness: 22/22 PASS, incluyendo Desktop/Mobile, 10 campos, scroll, wrap, selección, cambio de agente, conversación preservada, teclado/foco, reduced motion y ausencia de overflow horizontal.
- Evidencias: `evidence/served_agents/`.

## Límites preservados
No se conectó ni ejecutó modelo real. No se habilitaron pagos, correos, órdenes, registro productivo ni producción. No se cambió Railway, dominio, credenciales, variables protegidas, contrato funcional, estados canónicos ni reglas deterministas.

## Observación
La prueba visual automatizada usa un harness local con respuestas API simuladas exclusivamente para renderizar y validar interacción del frontend; la regresión del flujo determinista real se cubre por las suites existentes. No se desplegó este candidato al staging.
