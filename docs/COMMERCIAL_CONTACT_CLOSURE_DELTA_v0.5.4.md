# ENDRIAN Laboratorio QA v0.5.4 — cierre de Agentes, Precios y Contacto

Entorno: `QA_CONTROLLED_TEST_ONLY`  
Baseline preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.3.zip`  
Baseline SHA-256: `4b2f92e13735efe66d5cb9966f5c142ac4443442db5eebc3fd6fa56c1bf57818`

## Autoridad editorial

`ENDRIAN_LAB_FICHAS_COMERCIALES_AGENTES_PRECIOS_CIERRE_CANDIDATO_v1.4.1.docx`  
SHA-256: `769839c889112466b937e9ada3319acb5532a9b84acb2806eeb5f794969d20f3`

Se incorporó únicamente la Parte 1, secciones 1 a 3, correspondiente al copy público. Las notas internas, el changelog y los precios candidatos USD 89/149/239 no se publican.

## Cambios implementados

- Tarjetas y fichas completas de los cuatro agentes sustituidas por el copy público v1.4.1.
- Profesional: `Un proceso de trabajo definido` y descripción aprobada sobre clasificación, prioridad y organización del seguimiento.
- Avanzado y Profesional: `Precio pendiente de aprobación · USD · Pago único`.
- Integral y Premium: `Revisión y cotización`.
- Panel Precios actualizado con las cuatro ofertas, cómo se entrega, qué entrega ENDRIAN y condiciones previas.
- CTA único: `Hablar con ENDRIAN`.
- Contacto general: Nombre requerido, Apellido opcional, Correo requerido, País requerido, Teléfono opcional, Asunto requerido y Mensaje requerido.
- Contacto general conserva validación local, datos ante errores y separación total respecto del formulario de contratación.
- Scrollbars de Agentes, fichas, Precios, Contacto y selectores ajustadas al lenguaje oscuro/cyan.

## Archivos funcionales modificados

- `frontend/agents_catalog.json`
- `config/agents_catalog.json`
- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`
- `app/main.py` (identidad de versión únicamente)
- `start_lab_qa.py` (identidad de versión únicamente)
- pruebas y documentación v0.5.4

## QA ejecutado

- Suite automatizada: 150 PASS, 0 FAIL.
- Sintaxis JavaScript: PASS.
- Catálogos backend/frontend byte-identical: PASS.
- Ausencia de precios candidatos y notas internas en el copy público: PASS.
- Contacto general sin llamadas de red ni almacenamiento: PASS por contrato automatizado.
- PaymentGate, orden única, idempotencia, finalización, correo/PDF y snapshots: PASS por regresión.

## QA visual

El servidor local respondió correctamente, pero el navegador disponible en la sesión bloqueó `localhost` y el navegador local no pudo descargarse por la restricción de red. Por ello, desktop y móvil quedan **PENDIENTES DE REVISIÓN MANUAL**. No se declara PASS visual sin evidencia de navegador.

## Límites preservados

- Sin precios comerciales definitivos.
- Integral continúa en revisión/cotización; este build no la habilita como oferta estándar.
- Sin IA, correo, pago o SMS reales.
- Sin publicación, producción o construcción automática.
- Sin modificación de fichas previas al pago, formulario de contratación, PaymentGate, órdenes o snapshots existentes.
