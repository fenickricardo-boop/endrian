# ENDRIAN Laboratorio QA v0.5.3 — delta consolidado

Entorno: `QA_CONTROLLED_TEST_ONLY`  
Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.2`  
Producción, publicación, IA, correo y pago reales: no autorizados / no conectados.

## Cambios localizados

- El chat decide si sigue el último mensaje antes de actualizar el DOM y desplaza después de renderizar la tarjeta y sus acciones. Si la persona está leyendo mensajes anteriores, conserva su posición.
- La ficha de pago confirmado muestra `Plazo de entrega: 2 a 5 días hábiles.`; el snapshot conserva el plazo aceptado y la fecha de confirmación.
- El contacto general usa identificadores propios y queda aislado del formulario de contratación. Añade nombre completo, correo, país opcional, teléfono opcional, asunto y mensaje; valida localmente y no envía ni almacena.
- El catálogo conserva el contenido editorial vigente, agrupa Avanzado/Profesional como ofertas principales e Integral/Premium como revisión/cotización, y muestra `USD · Precio pendiente de aprobación` fuera de los importes técnicos del recorrido QA.
- Correo y PDF proyectan solo el `label` público de características, controles, exclusiones, dependencias y condiciones particulares. Los IDs permanecen en la orden archivada. Una entrada sin texto público válido produce un error controlado.
- Las órdenes nuevas usan `construction_request_snapshot.snapshot_version = 2` y añaden `need_confirmed`, `objective`, `context` y `particular_conditions`. No se migran ni modifican órdenes archivadas anteriores.

## Archivos funcionales modificados

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`
- `frontend/agents_catalog.json`
- `config/agents_catalog.json`
- `app/customer_confirmation.py`
- `app/service.py`
- `app/main.py`
- `start_lab_qa.py`
- pruebas y documentación de v0.5.3

## Prueba

- Regresión automatizada: 145 PASS.
- Sintaxis JavaScript: PASS.
- Proyección de listas estructuradas: PASS; no aparecen `item_id`, llaves ni nombres internos en HTML/PDF.
- Snapshot v2 de orden nueva, campos canónicos y ausencia de transcript: PASS.
- Idempotencia, PaymentGate, finalización, archivo, ruta estándar y revisión especial: PASS por regresión.
- Contacto general aislado y sin llamada de red: PASS por contrato automatizado.

## Comprobación visual

La inspección mediante navegador local automatizado no pudo ejecutarse en este entorno: el navegador remoto bloqueó `localhost` y no había un ejecutable local disponible. Por ello, las capturas desktop/móvil solicitadas quedan **pendientes de revisión manual Eduardo + Lía**. No se presentan maquetas como si fueran evidencia de navegador.

## Límites preservados

- Sin envío ni almacenamiento del contacto general.
- `sent=false` en la confirmación al cliente.
- Sin modificación de snapshots existentes.
- Sin transcript en correo, PDF u orden.
- Sin precios comerciales definitivos.
- Sin servicios externos ni producción.

