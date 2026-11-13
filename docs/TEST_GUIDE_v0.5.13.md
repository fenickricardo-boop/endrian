# Guía exacta de prueba v0.5.13

## Inicio

Ejecutar `START_LAB_QA.bat` en Windows o:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/` en una ventana nueva o recargar sin caché para no reutilizar un servidor anterior.

## Recorrido estándar autorizado

1. Enviar exactamente:

   `Necesito algo para ordenar los correos que nos llegan de clientes porque se nos pierden cosas. Somos cuatro personas y usamos correo para consultas, reclamos y solicitudes. Me gustaría que pudiera responder y hacer seguimiento.`

2. Responder exactamente:

   `Son unos 80 correos al día. Mejor que no responda solo. Quiero que clasifique, priorice y nos ayude a llevar seguimiento, pero que una persona revise las respuestas. Lo de responder automáticamente descártalo.`

3. Revisar la síntesis y pulsar `Sí, preparar mi resumen`.
4. En `Resumen de tu solicitud`, comprobar `ENDRIAN Especializado`, USD 89 y los campos estructurados. Pulsar `Continuar con mi solicitud`.
5. Completar datos ficticios válidos y pulsar `Continuar`.
6. En `Antes de pagar`, revisar la solicitud y marcar las dos aceptaciones. Pulsar `Continuar al pago`.
7. En la simulación, pulsar `Volver al Laboratorio`. Debe verse `Estamos verificando tu pago` y no debe existir una orden.
8. Abrir en otra pestaña privada del mismo navegador `http://127.0.0.1:8000/qa-control/payment`, cargar la referencia pendiente y elegir `Confirmado`.
9. Volver al Laboratorio y recargar. Debe aparecer `Pago confirmado`, una única orden y `Finalizar conversación`.
10. Repetir la confirmación o recargar: la orden y su número no deben cambiar.
11. Pulsar `Finalizar conversación`: la interfaz vuelve al inicio, la conversación no reaparece y la orden archivada permanece disponible en la herramienta privada QA.

## Corrección y fallback

- `Quiero corregir algo` vuelve al chat.
- `Volver a la conversación` desde el resumen invalida la oferta vigente y conserva los datos de contacto ya registrados.
- Una entrada fuera del guion muestra una indicación QA explícita y no crea una comprensión ni un resumen.

## Recorrido especial autorizado

Enviar exactamente:

`Necesito un agente que coordine atención por correo, documentos internos y seguimiento entre varias áreas, con decisiones que requieren revisión de responsables distintos.`

Confirmar la comprensión, revisar el resumen y enviar la solicitud para revisión. El recorrido debe solicitar contacto, quedar en revisión especial y no inventar precio ni habilitar pago.

