# ENDRIAN Laboratorio QA v0.5.10 — Delta localizado

## Base verificada

- Base: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.9.zip`
- Tamaño: `244519706` bytes
- SHA-256: `64aaa071fd8ad4f3262a125091190ad87f35320f9f4d0a88bf92d958e6ced0b1`
- Extracción: PASS

## Cambios implementados

- `Volver a Servicios` usa flecha SVG, alineación vertical estable y área interactiva ampliada.
- Al volver desde una ficha se restaura el desplazamiento del listado y el foco al botón `Ver ficha` usado.
- La columna de acciones de las tres tarjetas tiene ancho estable; sus botones comparten dimensiones.
- En pantalla estrecha la acción pasa debajo del texto y ocupa el ancho disponible.
- Se moderó el peso de las descripciones sin modificar su contenido.
- `Precios` usa `Cerrar`, sin flecha; conserva sesión y restaura el foco a `Precios`.
- Se reservó espacio para `USD 149` y se mantuvo accesible el cierre inferior del panel.

## Verificación ejecutada

- Suite automatizada: `170 PASS / 0 FAIL`.
- Compilación Python: PASS.
- Sintaxis JavaScript: PASS.
- HTTP local mediante `TestClient`: `/` 200 y `/api/health` 200.
- ZIP base y sidecar: hash coincidente y extracción PASS.

## Verificación visual

Desktop y móvil quedan `PENDING_MANUAL_REVIEW`. El navegador QA disponible no pudo acceder al servidor local y devolvió `Missing or invalid bearer token`. No se generaron ni reutilizaron capturas como si correspondieran a v0.5.10.

## Preservación y pendientes

- Sin cambios en contenido de Sofía, nombres, precios USD 39/89/149, Contacto, conversación, PaymentGate, pagos, órdenes, correo o PDF.
- Permanecen fuera de alcance los nombres, categorías y precios QA heredados del flujo posterior y catálogos internos.
- Producción, publicación y conexiones reales continúan desactivadas.
