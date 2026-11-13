# Delta consolidado posterior a la orden — v0.5.14

## Base y autoridad

- Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.13_DESCARGA.zip`.
- Autoridad editorial: `ENDRIAN_POST_CONFIRMACION_PLANTILLAS_v1.0.docx`.
- Plantilla de representación: `ENDRIAN-POST-CONFIRMACION-1.0-QA`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`; sin correo, pago, proveedor o construcción real.

## Implementado

- Correo breve de confirmación derivado de la orden archivada, `sent=false` y sin proveedor.
- Un único PDF, **Detalle y condiciones de tu pedido**, con información confirmada y advertencias QA.
- Ficha interna privada por orden, con contenido operativo primero y trazabilidad técnica secundaria.
- Vista previa de aviso interno, sin envío ni destinatario corporativo inventado.
- Estado honesto de materiales: `Recibido`, `Pendiente confirmado` o `Sin confirmar`; nunca se infiere recepción desde `materials_needed`.
- Representaciones versionadas sin modificar el snapshot ni su hash.
- Corrección de asunto y contenido entre la vista archivada y la vista privada; plazo sin repetición.
- Eliminación del compromiso ficticio de corrección de siete días en órdenes nuevas.
- Copy localizado del recorrido: aclaración sin “nivel de autonomía”, pregunta de confirmación solo en la tarjeta, “Servicio recomendado” antes de pagar, vigencia visible retirada y composer inactivo acorde al estado.

## Mapeo de campos

| Campo | Fuente | Estado |
|---|---|---|
| Orden, fecha y estado | Orden archivada | Disponible |
| Solución | `construction_request_snapshot.solution_title` | Disponible |
| Servicio | `service_label` / `agent` | Disponible |
| Necesidad, objetivo, contexto y alcance | Snapshot v3 | Disponible en órdenes nuevas |
| Entregables, plataforma, uso y entrega | Snapshot v3 | Disponible en órdenes nuevas |
| Materiales necesarios | `materials_needed` | Disponible |
| Estado de recepción de materiales | `materials_status` | Ausente actualmente; se muestra `Sin confirmar` |
| Criterios de comprobación acordados | `verification_criteria` | Ausente actualmente; pendiente interno |
| Responsable, bloqueos y notas operativas | Campos operativos futuros | No registrados; no se inventan |
| Términos y privacidad | Versiones y aceptaciones del snapshot | Provisionales QA |
| Remitente, canal y destinatario interno | Configuración futura | Pendientes QA |

## Preservación

No se modifican órdenes ni snapshots históricos. La generación de correo, PDF, ficha y aviso es una proyección de presentación con versión de plantilla. El transcript no se incorpora a ninguna salida.
