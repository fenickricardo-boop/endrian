# ENDRIAN Lab — corrección de confirmación conversacional v0.3.3

Fecha: 2026-10-07  
Entorno: `QA_CONTROLLED_TEST_ONLY`

## Origen y rollback

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.2.zip`
- SHA-256 del origen: `a72e4f4fea86cf9a32cf47b204f694ca0175e98898339f0cbe375f80e350f1ce`
- Rollback: restaurar la extracción limpia del ZIP v0.3.2 y verificar ese hash.

## Causa

`_confirmation_intent()` normalizaba mayúsculas y espacios, pero conservaba la puntuación periférica. Por ello, `No, eso es todo.` no coincidía con la frase autorizada sin punto, devolvía `UNRESOLVED` y repetía la pregunta de confirmación.

## Corrección localizada

- Uso de `casefold()` para normalización estable de mayúsculas/minúsculas.
- Eliminación exclusiva de punto e interrogación/exclamación periféricos (`.`, `?`, `!`, `¿`, `¡`).
- El conjunto de frases autorizadas permanece sin ampliación.
- Sin cambios en recorrido, copy, UI, estados, versionado, PaymentGate, recuperación, idempotencia o propuesta.

## Resultado verificado

`No, eso es todo.` produce:

1. `CONFIRM_NO_CHANGES`;
2. `SCOPE_CONFIRMED_SEMANTIC_EVENT`;
3. una sola `scope_version`;
4. transición `S4 → S2`;
5. salida de `needs_confirmation_chat`;
6. Datos de contacto sin repetición de la pregunta.

El reenvío accidental de la misma frase desde S2 produce `FLOW_CONTROL_REQUIRED` y conserva exactamente una `scope_version`.

## QA

- Pruebas focalizadas: **7/7 PASS**.
- Regresión completa: **80/80 PASS**.
- JavaScript: **PASS**.
- Compilación Python: **PASS**.
- Advertencia no funcional: deprecación de `Starlette TestClient` heredada de dependencia.

Estado propuesto: **BUG DE CONFIRMACIÓN CORREGIDO / REPETICIÓN ELIMINADA / FLUJO LISTO PARA REPRUEBA EDUARDO + LÍA**.
