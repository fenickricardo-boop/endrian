# ENDRIAN Laboratorio — delta localizado v0.3.6

## Base

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.5.zip`
- SHA-256: `be59faa0417ed04ada18a394507cbdee71edfa7a7d6c9c4f07a792f35f2b004f`
- Entorno: `QA_CONTROLLED_TEST_ONLY`

## Cambios implementados

- `solution_request_version` separada de alcance, cotización y proyección pública.
- `workflow_status`, `validation_result` y causas concurrentes separados.
- `Resumen de tu solicitud` antes del contacto, sin textarea ni transcript.
- Profesional y Avanzado admiten ruta `STANDARD` cuando están validados; Integral y Premium usan `SPECIAL_REVIEW`.
- Cambio de preferencia/producto requiere conformidad explícita.
- Fixture de correo trazado a `PRO-CAP-001/002/004/005/006` y `PRO-CTL-001`.
- Entorno `ENV-ENDRIAN-MANAGED` y entrega `ENDRIAN_MANAGED_ACCESS` registrados como simulación.
- `QA_PRICE_ADVANCED=USD 10`, `QA_PRICE_PROFESSIONAL=USD 20`, reglas `QA-COMMERCIAL-0.4`, condiciones `QA-CONDITIONS-0.1` y vigencia de siete días.
- Contacto posterior al resumen; edición segura de nombre, correo sintético y teléfono opcional.
- Revisión especial privada incapaz de levantar prohibiciones o autoridades pendientes.
- PaymentGate valida solicitud, versiones, importe, moneda, condiciones, aceptación y vigencia.
- Orden única con `construction_request_snapshot` inmutable, versionado y sin transcript.
- Señal global `Entorno de prueba · Sin operaciones reales` preservada en la estructura común de todas las vistas.

## Límites

- Sin IA, correo, pagos, conectores, proveedor o producción reales.
- La verificación de correo es simulada y está separada de la confirmación de contacto.
- Los fixtures no demuestran compatibilidad técnica, viabilidad comercial ni modalidad definitiva de entrega.
- La consola opcional de trazabilidad no se incorporó.

## Archivos funcionales modificados

- `app/full_flow.py`
- `app/service.py`
- `app/main.py`
- `frontend/app.js`
- pruebas directamente afectadas y `tests/test_handoff_v036.py`

Identidad, navegación, SVG, catálogo editorial, One Page, `agent_guide/**`, infraestructura y configuración de despliegue permanecen sin modificaciones funcionales.
