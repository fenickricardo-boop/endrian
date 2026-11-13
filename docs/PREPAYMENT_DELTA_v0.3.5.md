# ENDRIAN Lab — tramo previo al pago v0.3.5

Base: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.4.zip`  
SHA-256 de origen: `202ec13a095e7175d45505dba2f880da15b18c8a66be6ff4972e20a4354243de`  
Entorno: `QA_CONTROLLED_TEST_ONLY`

## Delta autorizado

- Composer único con modo conversacional completo y modo estructurado compacto.
- `Antes de pagar` consolida solución, valor, plazo, identidad, teléfono opcional y confirmación.
- Se retiraron Persona/Empresa, razón social, identificador fiscal y controles públicos de resultados de pago.
- La aceptación registra versión `PREPAYMENT-CONDITIONS-0.1` y timestamp UTC.
- PaymentGate sustituye `contracting_data_complete` por `prepayment_data_complete` sin eliminar las restantes protecciones.
- `payment_start` crea o reutiliza un intento idempotente y congela importe, moneda, alcance y cotización.
- Sin proveedor: el intento permanece pendiente y no genera orden.
- Resultados simulados se aplican mediante una consola localhost separada, disponible únicamente en `QA_CONTROLLED_TEST_ONLY` y no enlazada desde la interfaz pública.
- La creación de orden sigue exigiendo confirmación backend y conserva idempotencia.
- Copy público de adjuntos: `Adjuntos no disponibles`.

No se conectó proveedor, modelo, correo, pago real ni producción. Conversación, scope/quotation versioning, agentes, navegación, identidad, SVG, recuperación y estados S0–S8/SH permanecen preservados.
