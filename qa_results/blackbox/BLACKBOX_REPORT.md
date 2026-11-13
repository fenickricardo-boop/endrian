# v0.2 Black-box QA — handle_message only

Resultado: **PASS** — 16/16 PASS.

Todas las pruebas llaman únicamente `handle_message(session_id, user_message)`. No llaman `dimension()`, `classify()`, `register()`, `make_proposal()` ni métodos internos del núcleo.

**Límite del dictamen:** no se ejecutó un modelo de IA real. Este PASS verifica la capa conversacional determinista/integrable y su separación del motor de control; la conducta de un proveedor/modelo futuro queda expresamente no verificada.

## BB-QA01 — PASS
**Esperado:** 'Automatiza mi compañía' debe producir una sola aclaración material, sin adivinar.

```json
{
  "output": {
    "event": "CLARIFICATION_REQUIRED",
    "session_id": "BB01",
    "state": "CONVERSACIÓN INICIAL",
    "simulation": true,
    "message": "Puedo ayudarte, pero todavía sería adivinar. ¿Qué proceso o tarea concreta quieres mejorar primero?",
    "required_action": "ANSWER_CLARIFICATION",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
    "data": {}
  }
}
```

## BB-QA02 — PASS
**Esperado:** 'Necesito un bot' se trata como necesidad vaga y solicita concretar tarea.

```json
{
  "output": {
    "event": "CLARIFICATION_REQUIRED",
    "session_id": "BB02",
    "state": "CONVERSACIÓN INICIAL",
    "simulation": true,
    "message": "Puedo ayudarte, pero todavía sería adivinar. ¿Qué proceso o tarea concreta quieres mejorar primero?",
    "required_action": "ANSWER_CLARIFICATION",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
    "data": {}
  }
}
```

## BB-QA03 — PASS
**Esperado:** 'Quiero mejorar todo' no genera orientación ni propuesta; pide aclaración.

```json
{
  "output": {
    "event": "CLARIFICATION_REQUIRED",
    "session_id": "BB03",
    "state": "CONVERSACIÓN INICIAL",
    "simulation": true,
    "message": "Puedo ayudarte, pero todavía sería adivinar. ¿Qué proceso o tarea concreta quieres mejorar primero?",
    "required_action": "ANSWER_CLARIFICATION",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
    "data": {}
  }
}
```

## BB-QA04 — PASS
**Esperado:** Necesidad completa extrae usuarios, volumen, herramienta y datos personales desde lenguaje natural.

```json
{
  "output": {
    "event": "PRELIMINARY_UNDERSTANDING",
    "session_id": "BB04",
    "state": "COMPRENSIÓN PRELIMINAR",
    "simulation": true,
    "message": "Entiendo la necesidad a nivel preliminar: Necesito clasificar y responder 500 solicitudes al mes para 20 usuarios usando HubSpot, con datos personales. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
    "required_action": "CONTINUE_REQUEST",
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
    "data": {
      "extracted": {
        "users": 20,
        "volume": "500 por mes",
        "frequency": "mensual",
        "systems": "Hubspot",
        "data_sensitivity": "sensible",
        "integration_type": "known",
        "functions": [
          "clasificar",
          "responder"
        ]
      }
    }
  },
  "dimensioning": {
    "users": 20,
    "volume": "500 por mes",
    "frequency": "mensual",
    "systems": "Hubspot",
    "data_sensitivity": "sensible",
    "integration_type": "known",
    "functions": [
      "clasificar",
      "responder"
    ]
  }
}
```

## BB-QA05 — PASS
**Esperado:** Respuesta fragmentada acumula contexto y dimensionamiento sin perder mensajes previos.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB05",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito organizar correos y dar seguimiento. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "functions": [
            "seguimiento",
            "organizar"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB05",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB05",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "¿Con qué sistema o herramienta existente tendría que trabajar?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {}
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB05",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito organizar correos y dar seguimiento | Aclaración: sí, es eso",
          "objective": "Ordenar y dar seguimiento confiable a las solicitudes.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "seguimiento",
            "organizar"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "users": 12
        }
      }
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB05",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito organizar correos y dar seguimiento | Aclaración: sí, es eso",
          "objective": "Ordenar y dar seguimiento confiable a las solicitudes.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "seguimiento",
            "organizar"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "volume": "300 por mes",
          "frequency": "mensual"
        }
      }
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB05",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito organizar correos y dar seguimiento | Aclaración: sí, es eso",
          "objective": "Ordenar y dar seguimiento confiable a las solicitudes.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "seguimiento",
            "organizar"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "systems": "Gmail",
          "integration_type": "known"
        }
      }
    }
  ],
  "dimensioning": {
    "functions": [
      "seguimiento",
      "organizar"
    ],
    "users": 12,
    "volume": "300 por mes",
    "frequency": "mensual",
    "systems": "Gmail",
    "integration_type": "known"
  }
}
```

## BB-QA06 — PASS
**Esperado:** Corrección material posterior actualiza necesidad, preserva sesión e invalida propuesta dependiente.

```json
{
  "output": {
    "event": "MATERIAL_CORRECTION_APPLIED",
    "session_id": "BB06",
    "state": "REVISIÓN HUMANA REQUERIDA",
    "simulation": true,
    "message": "Actualicé la necesidad y descarté cualquier propuesta QA anterior que dependiera de la interpretación previa. Continuaremos desde el dimensionamiento afectado.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
    "data": {
      "extracted": {
        "integration_type": "unknown",
        "functions": [
          "responder"
        ]
      }
    }
  },
  "state": "REVISIÓN HUMANA REQUERIDA",
  "interpreted_need": "En realidad ahora necesito además responder automáticamente y conectar un sistema nuevo"
}
```

## BB-QA07 — PASS
**Esperado:** Contradicción de autonomía activa revisión humana y no fuerza cierre.

```json
{
  "output": {
    "event": "HUMAN_REVIEW_REQUIRED",
    "session_id": "BB07",
    "state": "REVISIÓN HUMANA REQUERIDA",
    "simulation": true,
    "message": "Detecté instrucciones incompatibles sobre el nivel de autonomía. No cerraré alcance, precio ni pago hasta resolver esta contradicción.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción",
    "data": {
      "reason": "CONTRADICCIÓN SOBRE AUTONOMÍA / APROBACIÓN HUMANA"
    }
  }
}
```

## BB-QA08 — PASS
**Esperado:** Solicitud de código/prompt aplica frontera anti-exfiltración.

```json
{
  "output": {
    "event": "BOUNDARY_ENFORCED",
    "session_id": "BB08",
    "state": "CONVERSACIÓN INICIAL",
    "simulation": true,
    "message": "Puedo explicarte qué conviene solicitar a ENDRIAN y el alcance funcional, pero no entregar una implementación, prompt, código, arquitectura o procedimiento listo para construir fuera de ENDRIAN.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §13 Restricciones anti-exfiltración de valor",
    "data": {
      "boundary": "ANTI-EXFILTRACIÓN"
    }
  }
}
```

## BB-QA09 — PASS
**Esperado:** Intento de saltar registro bloquea orientación completa.

```json
{
  "output": {
    "event": "ORIENTATION_BLOCKED_PRE_REGISTRATION",
    "session_id": "BB09",
    "state": "COMPRENSIÓN PRELIMINAR",
    "simulation": true,
    "message": "Puedo confirmar que entendí tu necesidad, pero la Orientación recomendada completa requiere registro QA previo.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
    "data": {}
  }
}
```

## BB-QA10 — PASS
**Esperado:** Intento de saltar pago bloquea creación de orden.

```json
{
  "output": {
    "event": "ORDER_BLOCKED",
    "session_id": "BB10",
    "state": "CONVERSACIÓN INICIAL",
    "simulation": true,
    "message": "No puedo generar una orden QA sin pago QA confirmado. La solicitud se conserva.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos",
    "data": {}
  }
}
```

## BB-QA11 — PASS
**Esperado:** Pregunta adaptativa consume respuesta natural y extrae autonomía/herramienta.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB11",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito responder correos. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "functions": [
            "responder"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB11",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB11",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "¿Debe actuar por sí solo o quedar sujeto a aprobación humana antes de ejecutar acciones?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB11",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "¿Con qué sistema o herramienta existente tendría que trabajar?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {
        "extracted": {
          "autonomy": "baja",
          "functions": [
            "responder"
          ]
        }
      }
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB11",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito responder correos",
          "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "responder"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "systems": "Gmail",
          "integration_type": "known"
        }
      }
    }
  ],
  "state": "ORIENTACIÓN EN REVISIÓN",
  "dimensioning": {
    "functions": [
      "responder"
    ],
    "autonomy": "baja",
    "systems": "Gmail",
    "integration_type": "known"
  }
}
```

## BB-QA12 — PASS
**Esperado:** Confirmación de orientación desde mensaje natural avanza solo a propuesta QA o revisión humana.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB12",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito clasificar correos. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "functions": [
            "clasificar"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB12",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB12",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "¿Con qué sistema o herramienta existente tendría que trabajar?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {}
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB12",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito clasificar correos",
          "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "clasificar"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "functions": [
            "clasificar"
          ]
        }
      }
    },
    {
      "event": "PROPOSAL_READY_QA",
      "session_id": "BB12",
      "state": "PROPUESTA DISPONIBLE",
      "simulation": true,
      "message": "Propuesta QA disponible con valores ficticios. Debe aceptarse junto con la ventana QA antes de habilitar pago QA.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo",
      "data": {
        "proposal": {
          "request": "Necesito clasificar correos",
          "includes": [
            "QA-CAPACIDAD-FUNCIONAL"
          ],
          "excludes": [
            "PRODUCCIÓN REAL"
          ],
          "classification": "Esencial",
          "price_kind": "exact",
          "price": "QA-100",
          "currency": "QA-UNIT",
          "delivery_window": "QA-WINDOW-5",
          "accepted": false,
          "delivery_accepted": false,
          "simulation": true
        },
        "classification": "Esencial"
      }
    }
  ]
}
```

## BB-QA13 — PASS
**Esperado:** Happy path completo por mensajes naturales genera solo orden/matriz QA y estado de evaluación, nunca producción.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB13",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito clasificar correos. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "functions": [
            "clasificar"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB13",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB13",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "¿Con qué sistema o herramienta existente tendría que trabajar?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {}
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB13",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito clasificar correos",
          "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "clasificar"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "functions": [
            "clasificar"
          ]
        }
      }
    },
    {
      "event": "PROPOSAL_READY_QA",
      "session_id": "BB13",
      "state": "PROPUESTA DISPONIBLE",
      "simulation": true,
      "message": "Propuesta QA disponible con valores ficticios. Debe aceptarse junto con la ventana QA antes de habilitar pago QA.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §8 Propuesta previa al pago: alcance, precio y plazo",
      "data": {
        "proposal": {
          "request": "Necesito clasificar correos",
          "includes": [
            "QA-CAPACIDAD-FUNCIONAL"
          ],
          "excludes": [
            "PRODUCCIÓN REAL"
          ],
          "classification": "Esencial",
          "price_kind": "exact",
          "price": "QA-100",
          "currency": "QA-UNIT",
          "delivery_window": "QA-WINDOW-5",
          "accepted": true,
          "delivery_accepted": true,
          "simulation": true
        },
        "classification": "Esencial"
      }
    },
    {
      "event": "PAYMENT_AVAILABLE_QA",
      "session_id": "BB13",
      "state": "PAGO DISPONIBLE",
      "simulation": true,
      "message": "Pago QA habilitado con valores ficticios.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos",
      "data": {
        "payment_enabled": true
      }
    },
    {
      "event": "PAYMENT_STATUS_QA",
      "session_id": "BB13",
      "state": "PAGO PENDIENTE",
      "simulation": true,
      "message": "Estado de pago QA actualizado.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos",
      "data": {
        "payment": {
          "state": "PAGO PENDIENTE",
          "order_created": false,
          "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos"
        }
      }
    },
    {
      "event": "ORDER_CONFIRMED_QA",
      "session_id": "BB13",
      "state": "MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN",
      "simulation": true,
      "message": "Pago QA confirmado. Se generó una orden QA y una matriz marcada exclusivamente para evaluación.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §10 Confirmación posterior al pago y número de orden",
      "data": {
        "order": {
          "order_id": "QA-ORDER-7F3DE2B0A0",
          "simulation": true,
          "price": "QA-100",
          "currency": "QA-UNIT",
          "delivery_window": "QA-WINDOW-5",
          "visible_immediately": true
        },
        "matrix": {
          "label": "MATRIZ INTERNA DE SOLICITUD Y PRODUCCIÓN — QA / NO PRODUCCIÓN",
          "status": "MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN",
          "simulation": true,
          "order_id": "QA-ORDER-7F3DE2B0A0",
          "contact": {
            "name": "Tom QA",
            "email": "tom@example.com",
            "email_verified_qa": true
          },
          "original_need": "Necesito clasificar correos",
          "confirmed_need": "Necesito clasificar correos",
          "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
          "functional_help": "Solicitud funcional ENDRIAN (QA)",
          "contracted_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "includes": [
            "QA-CAPACIDAD-FUNCIONAL"
          ],
          "excludes": [
            "PRODUCCIÓN REAL"
          ],
          "functional_capabilities": [
            "clasificar"
          ],
          "provided_information": {
            "functions": [
              "clasificar"
            ]
          },
          "pending_information": [],
          "systems": null,
          "scale": {
            "volume": null,
            "frequency": null,
            "users": null
          },
          "autonomy": null,
          "data_sensitivity": null,
          "commercial_classification": "Esencial",
          "price_paid_qa": "QA-100",
          "delivery_window_accepted": "QA-WINDOW-5",
          "acceptance_criteria": [
            "Solicitud y alcance QA confirmados",
            "Precio y plazo QA preservados sin cambio"
          ],
          "alerts": [],
          "human_review": {
            "required": false,
            "reason": null
          },
          "traceability": {
            "conversation": "BB13",
            "references": [
              "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §11 Matriz interna de solicitud y producción",
              "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §10 Confirmación posterior al pago y número de orden",
              "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos"
            ]
          }
        }
      }
    }
  ],
  "final": {
    "event": "ORDER_CONFIRMED_QA",
    "session_id": "BB13",
    "state": "MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN",
    "simulation": true,
    "message": "Pago QA confirmado. Se generó una orden QA y una matriz marcada exclusivamente para evaluación.",
    "required_action": null,
    "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §10 Confirmación posterior al pago y número de orden",
    "data": {
      "order": {
        "order_id": "QA-ORDER-7F3DE2B0A0",
        "simulation": true,
        "price": "QA-100",
        "currency": "QA-UNIT",
        "delivery_window": "QA-WINDOW-5",
        "visible_immediately": true
      },
      "matrix": {
        "label": "MATRIZ INTERNA DE SOLICITUD Y PRODUCCIÓN — QA / NO PRODUCCIÓN",
        "status": "MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN",
        "simulation": true,
        "order_id": "QA-ORDER-7F3DE2B0A0",
        "contact": {
          "name": "Tom QA",
          "email": "tom@example.com",
          "email_verified_qa": true
        },
        "original_need": "Necesito clasificar correos",
        "confirmed_need": "Necesito clasificar correos",
        "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
        "functional_help": "Solicitud funcional ENDRIAN (QA)",
        "contracted_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
        "includes": [
          "QA-CAPACIDAD-FUNCIONAL"
        ],
        "excludes": [
          "PRODUCCIÓN REAL"
        ],
        "functional_capabilities": [
          "clasificar"
        ],
        "provided_information": {
          "functions": [
            "clasificar"
          ]
        },
        "pending_information": [],
        "systems": null,
        "scale": {
          "volume": null,
          "frequency": null,
          "users": null
        },
        "autonomy": null,
        "data_sensitivity": null,
        "commercial_classification": "Esencial",
        "price_paid_qa": "QA-100",
        "delivery_window_accepted": "QA-WINDOW-5",
        "acceptance_criteria": [
          "Solicitud y alcance QA confirmados",
          "Precio y plazo QA preservados sin cambio"
        ],
        "alerts": [],
        "human_review": {
          "required": false,
          "reason": null
        },
        "traceability": {
          "conversation": "BB13",
          "references": [
            "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §11 Matriz interna de solicitud y producción",
            "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §10 Confirmación posterior al pago y número de orden",
            "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §9 Pago: habilitación, estados, recuperación y reembolsos"
          ]
        }
      }
    }
  }
}
```

## BB-QA14 — PASS
**Esperado:** Señales sensibles extraídas del lenguaje activan revisión humana antes de propuesta/pago.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB14",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito analizar datos personales de salud en HubSpot. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "systems": "Hubspot",
          "data_sensitivity": "sensible",
          "integration_type": "known",
          "functions": [
            "analizar"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB14",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "REGISTRATION_ACCEPTED_QA",
      "session_id": "BB14",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "Registro QA completado. Continuaré con el dimensionamiento sin pedir datos que no cambien la decisión.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "HUMAN_REVIEW_REQUIRED",
      "session_id": "BB14",
      "state": "REVISIÓN HUMANA REQUERIDA",
      "simulation": true,
      "message": "Tu caso necesita revisión humana QA antes de cerrar alcance, precio o plazo.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción",
      "data": {
        "reason": "DATOS SENSIBLES / REGULADOS",
        "extracted": {
          "users": 25
        }
      }
    }
  ],
  "state": "REVISIÓN HUMANA REQUERIDA",
  "reason": "DATOS SENSIBLES / REGULADOS"
}
```

## BB-QA15 — PASS
**Esperado:** Entrada vacía se valida y no altera estado.

```json
{
  "output": {
    "event": "INVALID_INPUT",
    "state": "NO_STATE_CHANGE",
    "simulation": true,
    "message": "session_id y user_message son obligatorios."
  }
}
```

## BB-QA16 — PASS
**Esperado:** Alta autonomía declarada en respuesta fragmentada activa revisión humana.

```json
{
  "outputs": [
    {
      "event": "PRELIMINARY_UNDERSTANDING",
      "session_id": "BB16",
      "state": "COMPRENSIÓN PRELIMINAR",
      "simulation": true,
      "message": "Entiendo la necesidad a nivel preliminar: Necesito responder solicitudes. Puedo ayudarte a convertirla en una solicitud clara para ENDRIAN. Si esto refleja lo que necesitas, podemos continuar con el registro QA.",
      "required_action": "CONTINUE_REQUEST",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §3 Interacción inicial sin registro; §3.4 Salida máxima antes del registro",
      "data": {
        "extracted": {
          "functions": [
            "responder"
          ]
        }
      }
    },
    {
      "event": "REGISTRATION_REQUIRED",
      "session_id": "BB16",
      "state": "REGISTRO PENDIENTE",
      "simulation": true,
      "message": "Para continuar y conservar lo que ya me contaste, necesitamos crear tu solicitud QA. Indica tu nombre, correo y confirma que aceptas el tratamiento necesario de datos y las comunicaciones operativas. Marketing es opcional.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §4 Puerta de registro, datos, consentimientos y recuperación",
      "data": {}
    },
    {
      "event": "DIMENSIONING_QUESTION",
      "session_id": "BB16",
      "state": "DIMENSIONAMIENTO INCOMPLETO",
      "simulation": true,
      "message": "¿Debe actuar por sí solo o quedar sujeto a aprobación humana antes de ejecutar acciones?",
      "required_action": "RESPOND_MATERIAL_QUESTION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §5 Dimensionamiento posterior al registro",
      "data": {}
    },
    {
      "event": "ORIENTATION_READY",
      "session_id": "BB16",
      "state": "ORIENTACIÓN EN REVISIÓN",
      "simulation": true,
      "message": "Preparé una Orientación recomendada QA para que la revises y corrijas antes de continuar.",
      "required_action": "CONFIRM_OR_CORRECT_ORIENTATION",
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §6 Orientación recomendada y solicitud estructurada",
      "data": {
        "orientation": {
          "title": "Orientación recomendada",
          "interpreted_need": "Necesito responder solicitudes",
          "objective": "Resolver funcionalmente la necesidad descrita mediante una solicitud clara para ENDRIAN.",
          "recommended": "Solicitar a ENDRIAN una solución funcional orientada a la necesidad confirmada.",
          "why": "Encaja porque traduce el objetivo expresado a capacidades funcionales delimitadas sin definir implementación técnica.",
          "capabilities": [
            "responder"
          ],
          "preliminary_scope": "Cobertura funcional suficiente para contratar; sin arquitectura técnica ni instrucciones implementables.",
          "simulation": true
        },
        "extracted": {
          "functions": [
            "responder"
          ]
        }
      }
    },
    {
      "event": "HUMAN_REVIEW_REQUIRED",
      "session_id": "BB16",
      "state": "REVISIÓN HUMANA REQUERIDA",
      "simulation": true,
      "message": "Tu caso necesita revisión humana QA antes de cerrar alcance, precio o plazo.",
      "required_action": null,
      "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción",
      "data": {
        "reason": "ALTA AUTONOMÍA / IMPACTO",
        "extracted": {
          "autonomy": "alta"
        }
      }
    }
  ],
  "state": "REVISIÓN HUMANA REQUERIDA"
}
```

