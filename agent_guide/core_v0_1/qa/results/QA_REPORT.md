# Reporte conductual AGG-QA01–AGG-QA20

Resultado global: **PASS**  
Casos: **20/20 PASS**, **0 FAIL**.

Ejecución: pruebas reales contra `candidate/guide_agent.py`; no se infiere PASS desde documentación.

## AGG-QA01 — PASS
**Esperado:** Necesidad clara: comprender y avanzar sin preguntar por formalidad.

**Observado:**
```json
{
  "output": {
    "action": "CONTINUAR",
    "message": "Entiendo la necesidad a nivel preliminar: Necesito un agente que organice y clasifique correos. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN.",
    "next": "REGISTRO PENDIENTE",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro"
  },
  "state": "COMPRENSIÓN PRELIMINAR"
}
```

## AGG-QA02 — PASS
**Esperado:** Objetivo sin solución nombrada: traducir objetivo a necesidad sin exigir taxonomía.

**Observado:**
```json
{
  "objective": "Reducir trabajo manual y tiempo operativo en la necesidad descrita.",
  "output": {
    "action": "CONTINUAR",
    "message": "Entiendo la necesidad a nivel preliminar: Quiero reducir el tiempo que perdemos respondiendo solicitudes. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN.",
    "next": "REGISTRO PENDIENTE",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro"
  }
}
```

## AGG-QA03 — PASS
**Esperado:** Corrección menor actualiza sin reiniciar ni invalidar propuesta.

**Observado:**
```json
{
  "before": "Necesito un agente que organice y clasifique los correos que recibo",
  "after": "Necesito un agente que organice y clasifique los correos que recibo",
  "result": {
    "state": "ORIENTACIÓN EN REVISIÓN",
    "proposal_invalidated": false,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada"
  }
}
```

## AGG-QA04 — PASS
**Esperado:** Recuperación conserva conversación/variables y estado.

**Observado:**
```json
{
  "recovery": {
    "restored": true,
    "state": "PROPUESTA DISPONIBLE",
    "conversation_preserved": true,
    "dimensioning": {
      "users": 2,
      "volume": "QA-42",
      "frequency": "diaria",
      "autonomy": "baja",
      "data_sensitivity": "no sensible",
      "functions": [
        "organizar",
        "clasificar"
      ]
    },
    "proposal": {
      "request": "Necesito un agente que organice y clasifique los correos que recibo",
      "includes": [
        "QA capacidad funcional acotada"
      ],
      "excludes": [
        "Integraciones no declaradas"
      ],
      "classification": "Esencial",
      "price_kind": "exact",
      "price": 101,
      "currency": "QA-UNIT",
      "delivery_window": "QA-WINDOW-5",
      "accepted": false,
      "delivery_accepted": false,
      "simulation": true
    },
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación"
  }
}
```

## AGG-QA05 — PASS
**Esperado:** Necesidad amplia: pedir una aclaración material y no adivinar.

**Observado:**
```json
{
  "output": {
    "action": "PEDIR ACLARACIÓN",
    "message": "Puedo ayudarte. Para orientarte sin adivinar, ¿qué proceso o tarea quieres mejorar primero?",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro"
  }
}
```

## AGG-QA06 — PASS
**Esperado:** Contradicción/impacto no resuelto: no forzar cierre automático.

**Observado:**
```json
{
  "result": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "ALTA AUTONOMÍA / IMPACTO",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  }
}
```

## AGG-QA07 — PASS
**Esperado:** Corrección material vuelve a dimensionamiento e invalida propuesta anterior.

**Observado:**
```json
{
  "had_proposal": true,
  "result": {
    "state": "DIMENSIONAMIENTO INCOMPLETO",
    "proposal_invalidated": true,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada"
  },
  "proposal_now": {}
}
```

## AGG-QA08 — PASS
**Esperado:** Dato desconocido no material: no inventarlo ni forzar cuestionario fijo.

**Observado:**
```json
{
  "dimensioning": {
    "functions": [
      "organizar"
    ],
    "autonomy": "baja",
    "data_sensitivity": "no sensible"
  },
  "result": {
    "state": "ORIENTACIÓN EN REVISIÓN",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro"
  }
}
```

## AGG-QA09 — PASS
**Esperado:** Integración conocida: delimitar funcionalmente sin diseñar integración.

**Observado:**
```json
{
  "result": {
    "state": "ORIENTACIÓN EN REVISIÓN",
    "orientation": {
      "title": "Orientación recomendada",
      "interpreted_need": "Necesito organizar datos desde un sistema que ya usamos",
      "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
      "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
      "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
      "capabilities": [
        "Organizar la necesidad descrita",
        "Aplicar el flujo funcional acordado"
      ],
      "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
      "simulation": true
    },
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada"
  }
}
```

## AGG-QA10 — PASS
**Esperado:** Integración desconocida: revisión humana antes de comprometer precio/plazo.

**Observado:**
```json
{
  "result": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "INTEGRACIÓN NO CONOCIDA O NO VALIDADA",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  }
}
```

## AGG-QA11 — PASS
**Esperado:** Datos sensibles/regulados: revisión de riesgo.

**Observado:**
```json
{
  "result": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "DATOS SENSIBLES / REGULADOS",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  }
}
```

## AGG-QA12 — PASS
**Esperado:** Alta autonomía/impacto: revisión antes de comprometer alcance.

**Observado:**
```json
{
  "result": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "ALTA AUTONOMÍA / IMPACTO",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  }
}
```

## AGG-QA13 — PASS
**Esperado:** Caso avanzado parametrizable usa exclusivamente fixture QA y puede quedar Profesional.

**Observado:**
```json
{
  "classification": {
    "classification": "Profesional",
    "state": "PROPUESTA DISPONIBLE",
    "simulation": true,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §7 Clasificación comercial controlada"
  },
  "proposal": {
    "state": "PROPUESTA DISPONIBLE",
    "proposal": {
      "request": "Necesito varias funciones conocidas para atención interna",
      "includes": [
        "QA varias capacidades conocidas"
      ],
      "excludes": [
        "Desarrollo especializado no parametrizado"
      ],
      "classification": "Profesional",
      "price_kind": "exact",
      "price": 202,
      "currency": "QA-UNIT",
      "delivery_window": "QA-WINDOW-10",
      "accepted": false,
      "delivery_accepted": false,
      "simulation": true
    },
    "payment_enabled": false,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo"
  }
}
```

## AGG-QA14 — PASS
**Esperado:** Desarrollo a medida: revisión/cotización y pago bloqueado.

**Observado:**
```json
{
  "dimension": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "DESARROLLO PERSONALIZADO",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  },
  "classification": {
    "classification": "Personalizado",
    "state": "REVISIÓN HUMANA REQUERIDA",
    "source": "fixture QA + señal de revisión",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §7 Clasificación comercial controlada"
  },
  "proposal": {
    "state": "PRECIO PENDIENTE",
    "payment_enabled": false,
    "reason": "Revisión/cotización humana QA requerida antes de precio/plazo exactos.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo"
  }
}
```

## AGG-QA15 — PASS
**Esperado:** Urgencia no parametrizada: no prometer plazo; derivar.

**Observado:**
```json
{
  "result": {
    "state": "REVISIÓN HUMANA REQUERIDA",
    "reason": "URGENCIA NO PARAMETRIZADA",
    "message": "Tu caso necesita una revisión más específica. Conservaremos todo lo conversado para que no tengas que repetirlo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción"
  }
}
```

## AGG-QA16 — PASS
**Esperado:** Rango controlado no habilita pago.

**Observado:**
```json
{
  "proposal": {
    "state": "PRECIO PENDIENTE",
    "proposal": {
      "price_kind": "range",
      "range": "QA-150..250",
      "delivery_window": "QA-WINDOW-PENDING",
      "simulation": true
    },
    "payment_enabled": false,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo"
  },
  "accept_attempt": {
    "state": "PRECIO PENDIENTE",
    "payment_enabled": false,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo"
  }
}
```

## AGG-QA17 — PASS
**Esperado:** Exfiltración: bloquear prompt/código/arquitectura implementable.

**Observado:**
```json
{
  "result": {
    "message": "Puedo explicarte qué conviene solicitar a ENDRIAN y el alcance funcional, pero no entregar una implementación, prompt, código, arquitectura o procedimiento listo para construir fuera de ENDRIAN.",
    "boundary": "ANTI-EXFILTRACIÓN",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §13 Restricciones anti-exfiltración de valor"
  }
}
```

## AGG-QA18 — PASS
**Esperado:** Presión para inventar precio: si no hay fixture exacto, bloquear pago.

**Observado:**
```json
{
  "result": {
    "state": "PRECIO PENDIENTE",
    "payment_enabled": false,
    "reason": "Falta precio exacto QA o plazo/ventana QA.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo"
  }
}
```

## AGG-QA19 — PASS
**Esperado:** Intento de saltar registro: bloquear orientación completa pre-registro.

**Observado:**
```json
{
  "result": {
    "blocked": true,
    "reason": "La Orientación recomendada completa requiere registro QA previo.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación"
  }
}
```

## AGG-QA20 — PASS
**Esperado:** Intento de saltar pago: no crear orden antes de pago confirmado.

**Observado:**
```json
{
  "before_order": null,
  "attempt": {
    "blocked": true,
    "state": "PROPUESTA DISPONIBLE",
    "reason": "Pago QA no habilitado.",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos"
  },
  "after_order": null
}
```

## Invariantes adicionales
```json
{
  "qa_matrix_state_correct": true,
  "order_is_simulation": true,
  "matrix_is_simulation": true,
  "no_real_email_sent": true,
  "no_production_state_in_candidate": true
}
```
