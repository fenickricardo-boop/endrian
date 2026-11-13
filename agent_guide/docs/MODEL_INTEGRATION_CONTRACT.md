# Contrato de integración de modelo conversacional — QA / NO PRODUCCIÓN

## Separación obligatoria
El **modelo conversacional** puede interpretar lenguaje, extraer candidatos de variables, detectar ambigüedad/contradicción, formular una pregunta material y redactar aclaraciones funcionales. El **núcleo determinista v0.1** conserva autoridad exclusiva sobre estados, gates, propuesta/pago/orden/matriz QA y fronteras.

Un modelo futuro **NO** puede crear/forzar estados, precio, plazo, clasificación comercial definitiva, pagos, órdenes ni matriz. Sus salidas son propuestas estructuradas que deben ser validadas antes de entrar al núcleo.

## Entrada al modelo
```json
{
  "session_id": "string",
  "state": "estado canónico",
  "conversation": [{"role":"user|assistant","text":"string"}],
  "known": {
    "interpreted_need": "string|null",
    "objective": "string|null",
    "dimensioning": "object"
  },
  "task": "interpret_next_user_message"
}
```

## Salida estructurada permitida
```json
{
  "action": "ASK_MATERIAL_QUESTION|UPDATE_INTERPRETATION|EXTRACT_DIMENSIONING|FLAG_HUMAN_REVIEW|ANSWER_FUNCTIONAL_CLARIFICATION|REFUSE_IMPLEMENTATION_DETAIL|NO_OP",
  "interpreted_need": "string|null",
  "objective": "string|null",
  "extracted": {
    "users": "integer|null",
    "volume": "string|null",
    "frequency": "string|null",
    "systems": "string|array|null",
    "autonomy": "string|null",
    "data_sensitivity": "string|null",
    "custom_development": "boolean|null",
    "support": "string|null",
    "urgency": "string|null",
    "functions": "array|null",
    "integration_type": "string|null"
  },
  "missing_material": ["string"],
  "contradiction": "string|null",
  "human_review_reason": "string|null",
  "question": "string|null",
  "functional_answer": "string|null",
  "confidence": "0..1|null"
}
```

## Validación
1. Rechazar campos no permitidos.
2. Rechazar acciones fuera del enum.
3. Normalizar valores, longitudes y tipos.
4. No aceptar del modelo: `state`, `price`, `delivery_window`, `payment_status`, `order_id`, `matrix_status`, credenciales o código ejecutable.
5. Si la salida es inválida: registrar `MODEL_OUTPUT_INVALID`, no cambiar estado, y pedir al modelo reintento una sola vez con esquema estricto. Si vuelve a fallar, usar fallback determinista/solicitar aclaración sin inventar datos.
6. Si existe contradicción o señal material de riesgo, el núcleo puede elevar a revisión humana aunque el modelo no lo proponga.

## Instrucciones base del Agente Guía
- Comprende antes de preguntar.
- Pregunta solo si la respuesta puede cambiar comprensión, alcance, clasificación, precio, plazo, riesgo o completitud de la matriz.
- Mantén contexto; no hagas repetir información conocida.
- Expresa orientación en lenguaje funcional/comercial, no técnico implementable.
- No entregues prompts finales, código, pseudocódigo, arquitectura, stack, configuración ni procedimiento paso a paso.
- No inventes precio, plazo, viabilidad o capacidad.
- Revisión humana es excepción material, no paso estándar.
- Nunca presentes un artefacto QA como productivo.

## Dependencia real pendiente
La ejecución con un modelo real requiere selección/configuración posterior por Valeria del proveedor/modelo y su interfaz de invocación. **No hay API key, proveedor pago ni credencial en este paquete.** El QA de v0.2 no constituye PASS de conducta de ese modelo futuro.

Trazabilidad: `ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx`, secciones 1, 3, 5, 6, 7, 8, 9, 11, 12, 13, 17, 18 y 19.


## Consumidores REV1
Cada acción declarada tiene un consumidor explícito en `app/service.py`; no se mantienen acciones decorativas.

- `ASK_MATERIAL_QUESTION` → reescritura autorizada de una pregunta ya abierta por el flujo.
- `UPDATE_INTERPRETATION` → actualiza únicamente necesidad/objetivo interpretados.
- `EXTRACT_DIMENSIONING` → entrega dimensiones validadas al núcleo determinista.
- `FLAG_HUMAN_REVIEW` → solicita revisión; `DeterministicModelSignalPolicy` decide y aplica la transición canónica.
- `ANSWER_FUNCTIONAL_CLARIFICATION` → redacta aclaración funcional dentro de eventos autorizados.
- `REFUSE_IMPLEMENTATION_DETAIL` → redacta la frontera anti-exfiltración.
- `NO_OP` → no modifica estado ni contenido.

`DRAFT_ORIENTATION` fue retirado del schema ejecutable REV1 porque no existía un consumidor real autorizado en este candidato. La orientación visible sigue siendo producida por el núcleo determinista.
