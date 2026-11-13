# Arquitectura y matriz — Agente Guía MVP QA v0.1

Estado: **QA / NO PRODUCCIÓN**.

Arquitectura aprobada: `AGG-01–AGG-09`.

- AGG-01 Intake conversacional — referencia: `ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro`.
- AGG-02 Interpretación y comprensión preliminar — referencia: `§3.4 Salida máxima antes del registro`.
- AGG-03 Registro controlado — referencia: `§4 Puerta de registro, datos, consentimientos y recuperación`.
- AGG-04 Dimensionamiento adaptativo — referencia: `§5 Dimensionamiento posterior al registro`.
- AGG-05 Orientación recomendada — referencia: `§6 Orientación recomendada y solicitud estructurada`.
- AGG-06 Clasificación comercial controlada — referencia: `§7 Clasificación comercial controlada`.
- AGG-07 Propuesta + pago simulado — referencia: `§8 Propuesta previa al pago` y `§9 Pago`.
- AGG-08 Orden QA + Matriz interna QA — referencia: `§10 Confirmación posterior al pago` y `§11 Matriz interna de solicitud y producción`.
- AGG-09 Orquestador de estados y trazabilidad — referencia: `§17 Estados funcionales consolidados`.

## Corrección obligatoria instalada

El candidato **no utiliza** `MATRIZ APTA PARA PRODUCCIÓN` como estado propio. El equivalente QA es exclusivamente:

`MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN`

La expresión productiva solo puede aparecer al citar textualmente el nombre del estado de la fuente, nunca como estado operativo del candidato.

## Matriz mínima

| Nodo | Entrada | Decisión | Salida | Gate |
|---|---|---|---|---|
| AGG-01 | texto libre | claridad inicial | necesidad original | continuar/aclarar |
| AGG-02 | necesidad/contexto | comprensión suficiente | síntesis preliminar | registro |
| AGG-03 | identidad + consentimientos QA | registro completo | registro simulado | dimensionar |
| AGG-04 | variables materiales | faltantes/riesgo | dimensión normalizada | orientar/revisar |
| AGG-05 | dimensión | confirmación/corrección | Orientación recomendada | clasificar |
| AGG-06 | fixture reglas QA | modalidad | clasificación QA | propuesta/revisión |
| AGG-07 | fixture propuesta QA | exactitud precio/plazo | propuesta/pago QA | pagar/bloquear |
| AGG-08 | pago QA confirmado | completitud interna | orden + matriz QA | evaluar |
| AGG-09 | transición | validez | estado + trazabilidad | siguiente |
