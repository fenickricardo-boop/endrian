# QA report — v0.5.15

## Resultado

| Comprobación | Resultado |
|---|---|
| Base y sidecar | PASS — tamaño y SHA-256 coincidentes |
| Integridad ZIP base | PASS |
| Regresión Python | PASS — 186 pruebas |
| Sintaxis JavaScript y Python | PASS |
| Nueva orden QA | PASS — `END-20261028-0001` |
| Replay / orden única | PASS |
| Snapshot inmutable | PASS |
| Resumen público condensado | PASS automatizado |
| Simulación de pago condensada | PASS automatizado |
| PDF público condensado | PASS |
| PDF renderizado e inspeccionado | PASS — 2 páginas A4 |
| Ficha interna íntegra | PASS |
| Interacción visual en navegador real | PENDIENTE — navegador ejecutable no disponible en el entorno |

## Evidencia

- Capturas estáticas de los componentes reales de resumen y simulación, generadas con los estilos vigentes.
- PDF generado desde una nueva orden QA y render de sus dos páginas.
- Proyecciones JSON del resumen, intento de pago y orden archivada.

Las capturas estáticas permiten revisar contenido y jerarquía, pero no sustituyen una prueba de foco, scroll o interacción en navegador. Esas interacciones permanecen cubiertas por regresión automatizada y pendientes de repetición visual local.

## Preservación

La orden, snapshot, versiones, aceptaciones, materiales, dependencias y hash no fueron alterados. Los detalles retirados del cliente siguen disponibles en la ficha privada.
