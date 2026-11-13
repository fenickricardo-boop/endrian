# Confirmación, orden y finalización QA — v0.5.0

Entorno: `QA_CONTROLLED_TEST_ONLY`.

## Implementado

- Confirmación privada del intento pendiente mediante la consola local existente.
- Orden `END-AAAAMMDD-NNNN` creada una sola vez desde confirmación backend QA.
- Archivo independiente `qa_orders` con orden, snapshot inmutable, vista previa no enviada y matriz interna, sin transcript.
- Acción pública posterior a la orden: `Finalizar conversación`.
- La finalización borra la sesión conversacional activa, rota la cookie y devuelve el Laboratorio a una sesión limpia.
- La orden archivada no se elimina y puede consultarse únicamente en el control privado local mediante `/api/qa-control/orders/{order_id}`.

## Limitación explícita

Cerrar el navegador no es un evento fiable de backend. Solo la acción explícita `Finalizar conversación` garantiza la limpieza inmediata. Si se cierra el navegador antes de finalizar, la sesión QA puede restaurarse mientras la cookie y el TTL local sigan vigentes.

## Fronteras

Sin pago, correo, SMS, IA o construcción reales. Sin portal de clientes, cuentas, publicación ni cambios en One Page, catálogo, precios comerciales o documentos legales.
