# Contrato técnico posterior para Valeria — QA / NO PRODUCCIÓN

## Punto de entrada
`handle_message(session_id: str, user_message: str) -> object`

La UI envía exclusivamente el identificador de sesión y el mensaje natural. La respuesta incluye:
- `event`
- `session_id`
- `state`
- `simulation=true`
- `message`
- `required_action`
- `reference`
- `data`

## Eventos previstos
`CLARIFICATION_REQUIRED`, `PRELIMINARY_UNDERSTANDING`, `REGISTRATION_REQUIRED`, `REGISTRATION_INCOMPLETE`, `REGISTRATION_ACCEPTED_QA`, `DIMENSIONING_QUESTION`, `ORIENTATION_READY`, `MATERIAL_CORRECTION_APPLIED`, `HUMAN_REVIEW_REQUIRED`, `BOUNDARY_ENFORCED`, `PROPOSAL_READY_QA`, `PAYMENT_AVAILABLE_QA`, `PAYMENT_STATUS_QA`, `PAYMENT_CONFIRMATION_BLOCKED`, `ORDER_BLOCKED`, `ORDER_CONFIRMED_QA`, `ORIENTATION_BLOCKED_PRE_REGISTRATION`, `INVALID_INPUT`, `NO_OP`.

## Regla de UI
La interfaz no deriva estados por texto libre. Renderiza `event/state` devueltos por la capa y nunca convierte `simulation=true` en operación real.

## Futuro adaptador de modelo
La futura integración IA se coloca entre comprensión lingüística y el núcleo de control, conforme `MODEL_INTEGRATION_CONTRACT.md`. El modelo nunca reemplaza el núcleo de estados.

Trazabilidad: `ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx`, especialmente secciones 2, 4–13, 16–19.
