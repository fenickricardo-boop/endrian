# QA report — ENDRIAN Laboratorio v0.5.14

## Identidad verificada

- Base: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.13_DESCARGA(1).zip`.
- Tamaño base: `9.794.019 bytes`.
- SHA-256 base: `a38a97e65ee292355a708d00a3facd28710c5da4c956b42a4a3291d3712cab7d`.
- Integridad base: `unzip -t` PASS.
- Autoridad: `ENDRIAN_POST_CONFIRMACION_PLANTILLAS_v1.0(1).docx`.
- SHA-256 autoridad: `6dfc1164d36080172ff73bd4408c1a5a85c7e297e93b8fc855367b0aa8999484`.

## Comprobaciones ejecutadas

| Comprobación | Resultado |
|---|---|
| Regresión Python | PASS — 183 pruebas |
| Sintaxis JavaScript | PASS |
| Creación de orden QA nueva | PASS |
| Orden única y replay idempotente | PASS |
| Snapshot inmutable y hash preservado | PASS |
| Correo breve derivado de snapshot | PASS |
| PDF completo derivado de snapshot | PASS |
| Ficha interna privada | PASS |
| Aviso interno `sent=false` | PASS |
| API privada de las cuatro salidas | PASS — HTTP 200 |
| PDF A4 renderizado | PASS — 2 páginas inspeccionadas, sin cortes |
| Ausencia de transcript / `item_id` en salidas cliente | PASS |
| Ausencia de compromiso ficticio de 7 días en órdenes nuevas | PASS |
| Descarga e instalación de navegador Playwright | BLOQUEADA — ejecutable ausente y descarga truncada por el entorno |
| QA visual interactivo desktop/móvil | PENDIENTE — no se declara PASS sin navegador ejecutable |

## Evidencia generada

- PDF de muestra generado desde la orden archivada `END-20261027-0001`.
- Render PNG de todas las páginas del PDF e inspección visual completa.
- HTML de muestra del correo, ficha interna y aviso interno.
- Proyección JSON pública versionada.
- PDF servido por la ruta privada sobre una orden nueva `END-20261028-0001` en base temporal de prueba.

La base temporal y sus órdenes de prueba no forman parte del paquete distribuible.

## Campos disponibles y pendientes

| Área | Estado |
|---|---|
| Orden, contacto, solución, servicio, alcance, entregables, plataforma, modalidad, importe, moneda, plazo, versiones y pago | Disponibles en snapshot v3 |
| Estado de recepción de materiales | No registrado actualmente; se muestra `Sin confirmar` |
| Criterios de comprobación acordados | No registrados actualmente; pendiente interno |
| Responsable, bloqueos y notas operativas | No registrados; no se inventan |
| Remitente y canal corporativo | Pendientes QA |
| Destinatario del aviso interno | Pendiente QA |
| T&C y privacidad definitivos | Pendientes de autoridad legal |

## Fronteras preservadas

Sin IA real, correo real, proveedor de pago, cobro, construcción automática ni publicación. No se modificaron órdenes o snapshots históricos.
