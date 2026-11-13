# ENDRIAN Laboratorio — cierre mínimo QA v0.3.8

## Base

- Origen: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.7.zip`.
- Recuperación histórica preservada: v0.3.7, v0.3.6 y v0.3.5.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.

## Cambios localizados

- Confirmación y corrección mediante acciones visibles; el avance no depende de escribir frases exactas.
- La comprensión profesional permanece en el chat; S4 solo ofrece las acciones correspondientes.
- Caso estándar de correo cerrado hasta pago confirmado por backend QA y orden única.
- Caso especial fijo `QA-INTEGRAL-REVIEW-01`: excepción evaluable por dependencias y responsables multiárea; sin prohibición, precio inventado ni pago habilitado.
- Confirmación pública de solicitud enviada para revisión después del contacto.
- Retirado el mensaje visible que exponía limitaciones internas del guion de corrección.
- Entorno y entrega se presentan sin etiquetas repetidas de simulación; la señal global de prueba permanece visible.

## Controles verificados

- Solicitud, alcance y cotización versionados.
- Precio, moneda, plazo y condiciones coherentes en estándar.
- PaymentGate y confirmación backend QA.
- Idempotencia y orden única con snapshot inmutable.
- Ruta especial sin cotización, pago ni orden.
- Transcript excluido de proyección, oferta y snapshot.
- Prohibiciones y autoridades pendientes no anulables por revisión.

## Resultado

- Pytest: **100 PASS / 0 FAIL**.
- Compilación Python: PASS.
- Sintaxis JavaScript: PASS.
- Ejecución HTTP local: PASS.

## Bloqueo de evidencia visual

La automatización de navegador no pudo ejecutarse porque el entorno no contiene Chromium. Playwright está instalado, pero su binario no; la descarga fue rechazada por la política de red del entorno. El navegador remoto no puede acceder al servidor `127.0.0.1` local.

Por esa razón, esta versión no declara cierre visual desktop/móvil. La interfaz debe someterse a una revisión manual o reejecutarse en un entorno con Chromium antes de aceptar el cierre.
