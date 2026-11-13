# ENDRIAN Laboratorio — Delta UX general v0.2.2

## Estado
`CORRECCIÓN UX LOCALIZADA / INTERFAZ GENERAL / NO PRODUCCIÓN / SIN DEPLOY / SIN MODELO REAL`

## Fuente exacta
- Fuente: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.1.zip`
- SHA-256 esperado/verificado: `7dbde92e8b8bd691f97c6ce67c1f757f2e3dc3a7878ddf82b033ee42f9d81b93`
- La fuente permaneció inmutable.

## Alcance aplicado
- Menú superior visible: `Volver a ENDRIAN · Agentes · Precios · Contacto · Nueva conversación`.
- `Nueva conversación` queda destacada y ejecuta la misma acción vigente.
- `Privacidad` sale del menú principal y permanece como enlace secundario en footer y formulario de contacto.
- `Agentes` abre el catálogo vigente de cuatro agentes dentro del Laboratorio.
- `Precios` se alimenta del mismo `agentCatalog` utilizado por Agentes y muestra el placeholder comercial vigente; se eliminó el catálogo paralelo Esencial/Profesional/Personalizado del copy UI.
- `Contacto` abre un drawer local con Nombre, Correo electrónico, Mensaje y `Enviar mensaje`; el submit no llama backend, no almacena y no envía.
- Eliminado el bloque `O explora algunos temas de ayuda` y todos sus chips.
- Paneles Agentes/Precios/Contacto comparten el lenguaje visual de drawer/sheet vigente.
- Flechas y controles `×` tienen centrado explícito.

## Volver a ENDRIAN en local
No se inventó URL pública. El botón usa, en este orden:
1. una ruta local relativa opcional recibida mediante `?home=/ruta-local`;
2. `document.referrer` si el Laboratorio fue abierto desde la Home local;
3. si no existe referencia, muestra un aviso integrado que explica que la Home no está incluida en este ZIP.

## Invariantes preservados
- Backend `app/**`: byte-identical a v0.2.1.
- `agent_guide/**`: byte-identical a v0.2.1.
- `frontend/agents_catalog.json` y `config/agents_catalog.json`: byte-identical.
- `START_LAB_QA.bat` y `start_lab_qa.py`: byte-identical.
- S0–S8/SH, PaymentGate, lógica conversacional, modelo, pagos, infraestructura, GitHub y Railway: sin cambios.

## Archivos funcionales modificados
- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`
- `config/ui_copy.json`

## QA
- Suite total: **68/68 PASS**.
- Regresión heredada: **60/60 PASS**.
- Contrato UX específico v0.2.2: **8/8 PASS**.
- `node --check frontend/app.js`: **PASS**.
- FastAPI local: `/health` 200; HTML, JS, CSS, config y catálogo servidos correctamente; cierre del servidor verificado.
- Launcher Windows: `START_LAB_QA.bat` y `start_lab_qa.py` permanecen byte-identical al candidato v0.2.1 previamente validado.

## Límite deliberado
Esta versión **no** corrige la presentación de fichas/estados durante la conversación ni modifica el comportamiento conversacional del Agente Guía. Ese frente queda separado para la etapa posterior indicada por Eduardo + Lía.
