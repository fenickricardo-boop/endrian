# Búsqueda de país y confirmación de orden QA — v0.4.7

Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.6`.

- La búsqueda de países normaliza mayúsculas y diacríticos, filtra inmediatamente y permite confirmar por clic o teclado sin selección silenciosa.
- La confirmación privada existente conserva el pago pendiente hasta recibir el evento backend QA.
- Tras la confirmación se presenta una ficha persistente con número de orden, agente, estado, importe de prueba y plazo.
- La ficha obtiene sus datos de la orden y su snapshot; no reconstruye información desde el transcript.
- La vista previa del correo permanece plegada, consultable y marcada como no enviada.
- No se conectaron pagos, correo, SMS, IA ni servicios externos reales.
