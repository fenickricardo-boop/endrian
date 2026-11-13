# Inventario funcional — ENDRIAN_LAB_FULL_FLOW_QA_v0.2.2

| Ruta | Función | Estado v0.2.2 |
|---|---|---|
| `frontend/index.html` | Shell y navegación del Laboratorio | Modificado UX |
| `frontend/styles.css` | Diseño responsive, drawers y microalineación | Modificado UX |
| `frontend/app.js` | Eventos de navegación/paneles; flujo funcional existente preservado | Modificado UX localizado |
| `config/ui_copy.json` | Copy UI auxiliar; elimina starters y catálogo de precios paralelo | Modificado contenido |
| `frontend/agents_catalog.json` | Fuente visible vigente de cuatro agentes y precio provisional | Byte-identical |
| `config/agents_catalog.json` | Catálogo de referencia vigente | Byte-identical |
| `app/**` | Backend, estados, PaymentGate, persistencia, seguridad | Byte-identical |
| `agent_guide/**` | Núcleo y capa determinista | Byte-identical |
| `START_LAB_QA.bat` | Lanzador Windows | Byte-identical |
| `start_lab_qa.py` | Arranque/cierre FastAPI local | Byte-identical |
| `tests/test_ux_general_v022.py` | Contrato automatizado de UX general | Nuevo |
| `docs/UX_GENERAL_DELTA_v0.2.2.md` | Reporte de corrección UX localizada | Nuevo |
| `qa_results/ux_general/` | Evidencia estructurada y resultados QA | Nuevo |
