# ENDRIAN Laboratorio — corrección UX conversacional v0.3.1

## Identidad

- Candidato: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.1`.
- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.0.zip`.
- SHA-256 del origen: `6f3f3598f7b40c1b6603f4ae74a8c7949a12fe9ffaa6e852e75bdd303d11cdec`.
- Baseline técnico anterior preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.4.zip`.
- SHA-256 de v0.2.4: `50994f1d637cc4038ffb6ca0e8bc4e91066502e8839b5bdb26d3a42b8486e3f7`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.

## Corrección localizada

El fixture `QA-PROFESIONAL-01` mantiene internamente `S1 → S3 → S4`, pero S3 dejó de renderizar un formulario público. El segundo turno del fixture completa `internal_dimensioning`, valida la salida profesional y muestra directamente una única tarjeta de confirmación.

La tarjeta usa exclusivamente `full_flow.client_output`. No contiene fallback hacia `session.need`, `session.objective`, mensajes, historial u orientación bruta. Si falta una salida profesional válida, la tarjeta no se renderiza y la confirmación queda bloqueada.

`Quiero corregir algo` lleva a `S3 / scope_correction_chat`. La corrección se realiza en el composer. Este candidato sin modelo real soporta explícitamente la corrección determinista sobre autonomía/revisión humana; otras correcciones permanecen en chat y solicitan una precisión soportada, sin simular comprensión general.

Se retiraron de la interfaz normal los formularios de contexto, volumen, herramientas, plazo, restricciones, perfil de datos, autonomía e integraciones, el textarea de corrección y los badges QA repetidos. Se conserva una única señal global: `Entorno de prueba · Sin operaciones reales`.

## Separación de datos

- `conversation_evidence`: interno, no exportable.
- `internal_dimensioning`: interno, no exportable.
- `client_output`: estructurado, allowlisted y única fuente de la tarjeta, cotización y correo.

El resumen/API pública elimina las dos primeras estructuras y también la clave heredada `dimensioning`.

## Archivos modificados respecto de v0.3.0

- `app/full_flow.py`
- `app/service.py`
- `frontend/app.js`
- `tests/test_full_flow_v02.py`
- `tests/test_ux_general_v022.py`
- `tests/test_ux_spatial_v023.py`
- `tests/test_ux_conversational_v031.py` (nuevo)
- documentación, resultados y manifests de v0.3.1.

`app/main.py` permanece byte-identical.

## Preservación byte-identical

Permanecen sin modificación todos los demás archivos funcionales de v0.3.0, incluidos `frontend/index.html`, `frontend/styles.css`, SVG/assets, navegación, `Tu recorrido`, catálogos, `agent_guide/**`, adaptadores/configuración de modelo, seguridad, rate limit, infraestructura, launchers, `Procfile` y `railway.json`.

## QA

- Suite completa: **66 passed / 0 failed**.
- Sintaxis JavaScript: PASS.
- Compilación Python: PASS.
- Sin formulario visible S3: PASS.
- Sin badges QA repetidos: PASS.
- Tarjeta únicamente desde `client_output`: PASS.
- Sin fallback bruto: PASS.
- Corrección vuelve al chat: PASS.
- Sin cotización previa a confirmación: PASS.
- Scope/cotización/PaymentGate/idempotencia/recuperación: PASS.
- Sin modelo, correo, pago o servicio externo real: PASS.

## Flujo visible resultante

`chat → pregunta material → tarjeta profesional → confirmar/corregir en chat → nombre/correo → cotización → contratación/pago → orden → seguimiento`

## Rollback

Restaurar el ZIP original v0.3.0 y verificar su SHA-256. Si se requiere volver al baseline técnico anterior, restaurar el ZIP original v0.2.4 y verificar su hash. Ninguno fue sobrescrito.

## Dictamen

`CORRECCIÓN UX APLICADA / CANDIDATO QA LISTO PARA REVISIÓN EDUARDO + LÍA`.
