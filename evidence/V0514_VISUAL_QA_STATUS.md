# Estado visual v0.5.14

## Comprobado

- PDF **Detalle y condiciones de tu pedido** generado desde una orden archivada real del fixture QA.
- Dos páginas A4 renderizadas a PNG e inspeccionadas completas.
- Sin cortes, solapamientos ni una página final artificialmente vacía.
- Materiales mostrados como `Sin confirmar` cuando la orden no acredita recepción.
- Aviso legal provisional visible y sin afirmación de T&C definitivos.

La carpeta `evidence/v0514_pdf/` contiene el PDF y los renders inspeccionados.

## Pendiente declarado

No se ejecutó QA visual interactivo desktop/móvil del HTML: el runtime incluye Playwright, pero no un ejecutable de Chromium; cuatro intentos de descarga devolvieron un archivo truncado de 0 MiB. No se declara PASS visual del navegador.

Las rutas HTML, JSON y PDF sí fueron iniciadas localmente y respondieron HTTP 200 con la orden temporal `END-20261028-0001`. La regresión automatizada valida contenido, ausencia de filtraciones, versionado, inmutabilidad e idempotencia.
