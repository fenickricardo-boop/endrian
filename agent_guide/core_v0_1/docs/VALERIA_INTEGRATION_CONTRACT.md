# Contrato técnico de integración posterior — Valeria

**NO IMPLEMENTADO. VALERIA EN ESPERA.** Este documento define interfaz funcional futura; no autoriza web, backend, pagos ni producción.

## Responsabilidades

- **Valeria/Web**: renderizar conversación/estados, capturar acciones, mostrar resultados; no inventar transiciones ni datos comerciales.
- **Agente Guía**: interpretar, solicitar datos materiales, dimensionar, producir Orientación recomendada y estados.
- **Motor comercial futuro**: clasificación/precio/plazo/vigencia con reglas aprobadas.
- **Proveedor de pago futuro**: resultado transaccional real.

## Envelope mínimo

```json
{
  "session_id":"string",
  "request_id":"string",
  "state":"string",
  "simulation":true,
  "user_message":"string|null",
  "conversation_context":{},
  "required_action":"string|null",
  "visible_output":{},
  "internal_output":{},
  "blocking_reason":"string|null",
  "human_review":{},
  "trace":[]
}
```

## Objetos
`registration`, `dimensioning`, `orientation`, `commercial_classification`, `proposal`, `payment`, `order`, `production_matrix`.

Cada objeto debe portar `status`, `source`, `simulation`, `version` y `confirmed_by_user` cuando aplique.

## UI → Guía
`START_CONVERSATION`, `SEND_MESSAGE`, `CONTINUE_REQUEST`, `SUBMIT_REGISTRATION_QA`, `CONFIRM_ORIENTATION`, `CORRECT_ORIENTATION`, `ACCEPT_PROPOSAL_QA`, `START_PAYMENT_QA`, `RESUME_REQUEST_QA`.

## Guía → UI
`UNDERSTANDING_READY`, `REGISTRATION_REQUIRED`, `DIMENSIONING_QUESTION`, `ORIENTATION_READY`, `HUMAN_REVIEW_REQUIRED`, `PROPOSAL_READY_QA`, `PRICE_PENDING`, `PAYMENT_AVAILABLE_QA`, `PAYMENT_STATUS_QA`, `ORDER_CONFIRMED_QA`, `MATRIX_CREATED_QA`.

## Invariantes
1. PAGO PENDIENTE → jamás crea orden.
2. Rango → jamás habilita pago.
3. Precio exacto o plazo no aceptado → jamás habilita pago.
4. Corrección material → invalida propuesta previa.
5. Revisión humana requerida → bloquea pago automático.
6. Matriz QA incompleta → `MATRIZ EN REVISIÓN`.
7. Matriz QA completa → `MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN`; nunca semántica productiva.
8. `simulation=true` obligatorio en esta versión.

Referencias de autoridad: `ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §§6–13, 17–19`.
