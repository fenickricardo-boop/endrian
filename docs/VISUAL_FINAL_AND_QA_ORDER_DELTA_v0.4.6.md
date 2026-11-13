# Delta visual final y continuación de orden QA — v0.4.6

Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.5`.

## Cambios localizados

- El selector de facturación usa el ancho disponible y evita cortes prematuros u overflow horizontal.
- El selector telefónico conserva únicamente ISO + prefijo, con tipografía uniforme y nombre accesible completo.
- Se corrige la alineación del grupo telefónico respecto del país de facturación.
- El área desplazable incorpora separación interior superior e inferior para sus indicadores.
- Se retira `Acción aplicada.` del chat público y las transiciones hacia la simulación se ejecutan silenciosamente; la tarjeta visible conserva el aviso suficiente.
- No se modificaron precios comerciales, documentos legales, capacidades, One Page, arquitectura de entrega ni conexiones externas.

## Controles preservados

- Teléfono opcional y validación de formato sin fixtures exactos.
- Correos válidos sin allowlist de dominios.
- PaymentGate, pago pendiente, confirmación privada, idempotencia y orden única.
- Vista previa local del correo generada desde la orden, con `sent: false`.

## Límite de evidencia visual

La validación automatizada de contratos CSS/DOM y la regresión funcional se ejecutaron. La captura automática en navegador no pudo producirse en este entorno porque el runtime Chromium no pudo descargarse íntegramente; la revisión visual desktop/móvil queda como verificación manual del candidato navegable, sin sustituirla por evidencia fabricada.
