# ENDRIAN Laboratorio QA v0.5.2 — delta localizado

Base verificada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.1.zip`  
SHA-256: `2adf11fbf080ad9017a950eaecf93da0eb7ea75b160de4e84a64ed2e52aa64e1`

## Implementado

- Vista previa privada QA del correo de confirmación, derivada únicamente de la orden archivada y su `construction_request_snapshot`.
- Un solo PDF: `Copia_de_contratacion_[numero_de_orden].pdf`.
- `sent=false`, sin proveedor ni envío real.
- Referencia `QA-TERMS-0.1` y avisos provisionales autorizados; no se redactaron T&C nuevos ni se afirma contenido completo.
- Referencia de privacidad provisional, sin segundo adjunto.
- Vista previa retirada de la ficha pública post-pago.
- Acceso conservado después de finalizar la conversación mediante la orden archivada.

## Acceso privado

Con el servidor local en `QA_CONTROLLED_TEST_ONLY` y una orden existente:

- Correo: `/qa-control/orders/END-AAAAMMDD-NNNN/confirmation`
- JSON: `/api/qa-control/orders/END-AAAAMMDD-NNNN/customer-confirmation`
- PDF: `/api/qa-control/orders/END-AAAAMMDD-NNNN/contract-copy.pdf`

Las rutas privadas solo responden desde localhost en el entorno QA controlado.

## Pendientes para producción

- Cuerpo completo y aprobación legal de T&C por Clara.
- RUT, domicilio y representante autorizados.
- Correo corporativo operativo.
- URL operativa y versión definitiva de Política de Privacidad.
- Proveedor de correo y envío real.

Ningún snapshot existente fue modificado.
