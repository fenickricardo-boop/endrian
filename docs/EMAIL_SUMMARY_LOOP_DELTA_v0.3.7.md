# ENDRIAN Laboratorio — corrección localizada v0.3.7

## Base

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.6.zip`
- Entorno: `QA_CONTROLLED_TEST_ONLY`
- Alcance: generación, transición y renderizado del resumen para el caso soportado de atención por correo.

## Causa

El caso completo expresado con una redacción distinta del fixture exacto entraba en la rama genérica `PRELIMINARY_UNDERSTANDING`. Esa rama fijaba `ui_state=preliminary` y S1, mientras que S1 no renderiza una ficha ni acciones. La respuesta de conformidad posterior volvía a evaluarse como una necesidad nueva y repetía la misma rama.

## Corrección

- Reconocimiento acotado del caso QA de correo por requisitos materiales, sin exigir una oración exacta.
- Generación de la formulación profesional y transición S1 → S3 → S4 con `needs_confirmation_chat`.
- Reconocimiento de la conformidad explícita que solicita ver el resumen.
- Transición única S4 → S5 con `scope_version`, `solution_request_version`, cotización y `client_output` estructurado.
- Reenvío posterior bloqueado por el control normal del flujo, sin duplicar versiones.
- Sin cambios en frontend, diseño, PaymentGate, pagos, orden, infraestructura o servicios externos.

## Regresión

Se añadió el caso observado completo con sus dos turnos. Comprueba contenido visible, estado, proyección del resumen, ausencia del mensaje huérfano, no repetición y no duplicación.

Resultado consolidado: **98 PASS / 0 FAIL**.
