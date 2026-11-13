# ENDRIAN Laboratorio — handoff consolidado v0.4.0

## Base

- Origen: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.9.zip`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.
- v0.3.5 permanece preservada como recuperación histórica.

## Cambios localizados

- El resumen estándar presenta las cinco características autorizadas, plataforma de prueba, precio `USD 20`, plazo `2 a 5 días hábiles` y fecha de expiración derivada de la cotización.
- Datos del cliente incorpora teléfono opcional y país o territorio de facturación obligatorio, buscable, sin geolocalización ni valor predeterminado en la interfaz.
- El país se conserva como dato estructurado `{country_code, country_name}` durante edición y recuperación.
- Antes del pago separa condiciones particulares, términos provisionales y aviso provisional de privacidad; registra una aceptación contractual versionada y referencia la privacidad por separado.
- `Continuar al pago` crea o reutiliza un intento idempotente. El retorno del checkout mantiene el pago pendiente y muestra `Estamos verificando tu pago`; no crea una orden.
- Rechazo, cancelación y expiración tienen recuperación controlada. La interfaz pública no expone controles técnicos de resolución.
- Solo la confirmación backend QA crea una orden única con snapshot inmutable.
- La vista previa del correo se genera desde la orden y su snapshot, se marca como no enviada y no contiene transcript.
- La ruta especial conserva contacto y país, confirma solicitud de revisión y no inventa precio ni habilita pago.

## Controles preservados

- `scope_version`, `solution_request_version`, `quotation_version`, PaymentGate, expiración e idempotencia.
- Bloqueos materiales y rutas STANDARD/SPECIAL_REVIEW.
- Ausencia de IA, correo, pago o proveedor reales.
- One Page, catálogo, fichas comerciales e infraestructura sin modificación.

## QA

- Regresión automatizada: **108 PASS / 0 FAIL**.
- País obligatorio, conservación estructurada y edición: PASS.
- Retorno pendiente sin orden: PASS.
- Confirmación backend, orden única y replay idempotente: PASS.
- Rechazo/cancelación/expiración y recuperación: PASS.
- Snapshot y vista previa sin transcript: PASS.
- Ruta estándar y ruta especial: PASS.

## Evidencia visual

La superficie de navegador disponible bloquea el acceso a `127.0.0.1` y el entorno no incluye un binario Chromium local. Por tanto, desktop/móvil quedan **pendientes de revisión manual**; no se declara cierre visual. La entrega es funcionalmente apta para esa revisión.
