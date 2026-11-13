# ENDRIAN Lab — delta de recorrido visible v0.3.2

Fecha de verificación: 2026-10-07 (UTC)  
Entorno: `QA_CONTROLLED_TEST_ONLY`

## Origen y rollback

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.1.zip`
- SHA-256 del origen: `b5e7f76f5c7ce72b9d320561b786d1d970fb32785e1790a3c34af286f0a09da7`
- Baseline técnico anterior preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.4`
- SHA-256 de v0.2.4: `e67d128c4850492a15d7844dd720b76de932d42ef241c2a09bf72e2bba836aaa`
- Rollback: sustituir el directorio v0.3.2 por la extracción limpia del ZIP v0.3.1 y verificar su SHA-256 antes de iniciar.

## Delta autorizado

- S1–S4 permanecen internamente; el levantamiento visible ocurre solo en el chat.
- La comprensión se cierra conversacionalmente y genera `scope_version` solo tras confirmación.
- Nombre y correo aparecen vacíos, con placeholders públicos y un solo consentimiento.
- El agente se presenta por primera vez en `Tu solución recomendada`.
- La propuesta se redujo a necesidad, agente y explicación aplicada, objetivo, valor y plazo.
- Se añadió el campo opcional dentro de la propuesta.
- Un agregado no material queda como nota; uno material o incierto invalida la cotización vigente y devuelve al chat conservando contacto.
- Las regeneraciones preservan versiones anteriores y elevan `quotation_version`.
- Se retiró lenguaje interno de QA de los mensajes y superficies normales del recorrido.
- El plazo canónico `2 a 5 días hábiles` se propaga a propuesta, correo, habilitación de pago y orden.

## Separación y fronteras

- `conversation_evidence` e `internal_dimensioning` permanecen internos y no exportables.
- `client_output` validado continúa siendo la única fuente para propuesta, correo y orden.
- El adaptador determinista permanece fuera de los componentes visuales y puede sustituirse posteriormente sin rediseñar el recorrido.
- Sin modelo real, API externa, correo real, pago real, PII real, producción ni cambios de infraestructura.

## Archivos funcionales modificados

- `frontend/app.js`
- `app/service.py`
- `app/full_flow.py`
- `app/main.py`
- `tests/test_full_flow_v02.py`
- `tests/test_ux_conversational_v031.py`
- `tests/test_visible_journey_v032.py` (nuevo)

Además se actualizaron este delta, resultados QA y manifests del paquete.

## Invariantes verificados

`frontend/index.html`, SVG, estilos, navegación, paneles, `Tu recorrido`, catálogos, `agent_guide/**`, configuración/adaptadores de modelo, launchers, seguridad/rate limit, `Procfile`, `railway.json` e infraestructura permanecen byte-identical respecto de v0.3.1, salvo los manifests regenerados del nuevo paquete.

## Resultado

- `python -m pytest -q`: **73 passed**.
- `node --check frontend/app.js`: **PASS**.
- `python -m py_compile app/*.py`: **PASS**.
- Dependencias externas necesarias durante QA: **0**.

Estado propuesto: **IMPLEMENTACIÓN LOCALIZADA COMPLETADA / CANDIDATO LISTO PARA REVISIÓN EDUARDO + LÍA**.
