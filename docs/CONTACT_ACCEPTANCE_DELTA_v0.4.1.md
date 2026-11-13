# ENDRIAN Laboratorio — ajuste localizado v0.4.1

## Base

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.0.zip`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.
- Sin IA, correo, pago, proveedor, publicación o construcción real.

## Implementación

- El copy visible de plazo es `2 a 5 días hábiles desde la confirmación del pago.` en resumen, pre‑pago, confirmación y correo simulado.
- La condición aplicable a órdenes nuevas se versionó como `QA-CONDITIONS-0.2`; snapshots anteriores no se migran ni sobrescriben.
- País de facturación utiliza la etiqueta `País de facturación*`, placeholder `Selecciona tu país`, 249 códigos ISO, búsqueda, cero preselección y cero geolocalización.
- Los selectores son componentes propios del Laboratorio; no dependen del panel gris nativo de `datalist`.
- Teléfono opcional separa país/prefijo y número. Registra país, prefijo, número nacional y número internacional como estructura independiente del país de facturación.
- La pantalla `Antes de pagar` presenta los datos como información de revisión. El formulario aparece únicamente al pulsar `Modificar datos`.
- Se eliminó la aceptación independiente de correo en contacto y se añadió el aviso de uso operativo junto al campo.
- Pre‑pago exige exactamente dos aceptaciones: términos/pedido y tratamiento de datos. Ambas conservan timestamp y referencias de `scope_version`, `solution_request_version`, `quotation_version` y documentos aplicables.
- Los documentos se muestran con títulos simplificados y una nota conjunta de provisionalidad.

## Conversación y privacidad

La conversación continúa almacenándose dentro del snapshot local de sesión, en `full_flow.conversation_evidence`, clasificada como `INTERNO / NO EXPORTABLE`. El snapshot se guarda en SQLite local (`data/qa_sessions.db`) con TTL predeterminado de 86.400 segundos. No se incorpora a `client_output`, cotización, orden ni correo simulado. Este encargo no modifica ese almacenamiento.

## QA

- Regresión automatizada: **112 PASS / 0 FAIL**.
- Sintaxis JavaScript y compilación Python: PASS.
- Coherencia de plazo y condición `QA-CONDITIONS-0.2`: PASS.
- País y teléfono sin valores chilenos predeterminados: PASS.
- Persistencia y recuperación estructurada: PASS.
- Dos aceptaciones obligatorias y trazadas: PASS.
- Ruta estándar, espera backend, orden única y correo desde snapshot: PASS.
- Ruta especial sin precio ni pago: PASS.

## Evidencia visual

No se generaron pantallazos nuevos: el navegador remoto bloquea loopback y la descarga del navegador local devolvió artefactos truncados. Desktop/móvil requieren revisión manual sobre este candidato. No se reutilizan capturas de versiones anteriores como evidencia de v0.4.1.
