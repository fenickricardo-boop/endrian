# Fichas finales y continuación del pago QA — v0.4.5

Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.4_VERIFIED.zip`  
SHA-256: `9336c86299249603c5bdf729931ca51c2f64211032a642c65a44ffe78af0455a`

## Ajustes localizados

- El grupo `Teléfono (opcional)`, el prefijo y el número usan la misma tipografía de 12 px y altura de 38 px que el formulario.
- El selector mantiene la representación compacta `CL +56`/equivalentes, sin nombres completos visibles ni desplazamiento horizontal.
- La síntesis previa al pago muestra `Nombre completo` y conserva íntegramente el valor ingresado.
- Las validaciones abiertas de v0.4.4 permanecen: correo por formato, teléfono opcional por estructura y sin identidad o fixture exactos.
- Las condiciones aclaran que suscripciones, licencias y consumo externo no están incluidos y se informarían antes del pago.
- El estado pendiente muestra únicamente `Estamos verificando tu pago` y `Conservamos tu solicitud. No necesitas intentar pagar nuevamente.`

## Continuación privada

La confirmación usa la consola local `/qa-control/payment`, inaccesible fuera de localhost y fuera de `QA_CONTROLLED_TEST_ONLY`. Requiere la referencia vigente del intento obtenida desde `/api/session` en el mismo navegador. La confirmación repetida no crea otra orden. La vista previa de correo se genera desde el snapshot de la orden y permanece sin enviar.

## Límites preservados

No se conectaron IA, proveedor de pago, correo, SMS ni verificación externa. No se modificaron las dos aceptaciones legales, precio, plazo, capacidades, Agente Guía ni estados arquitectónicos.
