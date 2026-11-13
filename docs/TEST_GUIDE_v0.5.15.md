# Guía de prueba — v0.5.15

## Recorrido

1. Inicia el paquete nuevo mediante `START_LAB_QA.bat` o `python start_lab_qa.py`.
2. Envía:

   `Necesito algo para ordenar los correos que nos llegan de clientes porque se nos pierden cosas. Somos cuatro personas y usamos correo para consultas, reclamos y solicitudes. Me gustaría que pudiera responder y hacer seguimiento.`

3. Responde:

   `Son unos 80 correos al día. Mejor que no responda solo. Quiero que clasifique, priorice y nos ayude a llevar seguimiento, pero que una persona revise las respuestas. Lo de responder automáticamente descártalo.`

4. Pulsa `Sí, preparar mi resumen`.
5. Comprueba que el resumen solo muestra solución, servicio, `Qué incluye`, plataforma, precio y plazo.
6. Continúa, completa datos ficticios y comprueba el resumen desplegable compacto de `Antes de pagar`.
7. Acepta los dos documentos QA y pulsa `Continuar al pago`.
8. Comprueba que la simulación solo muestra servicio e importe.
9. Regresa al Laboratorio, confirma el pago desde `http://127.0.0.1:8000/qa-control/payment` y revisa la orden.

## PDF

Con la orden creada, abre:

`http://127.0.0.1:8000/api/qa-control/orders/NUMERO-DE-ORDEN/contract-copy.pdf`

El PDF no debe mostrar tabla de materiales, estados operativos, snapshot, hash ni versión técnica de plantilla. La ficha interna conserva esos datos en:

`http://127.0.0.1:8000/qa-control/orders/NUMERO-DE-ORDEN/internal`
