# Datos del cliente y recuperación — v0.4.3

## Base

- Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.2.zip`.
- SHA-256: `c5c5367867a8421452ed3257ee88eb07ad87035ea0fad9ac4b89e0b65b4ecd9c`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.

## Causas corregidas

1. Los errores `422` de FastAPI podían llegar al frontend como una lista de objetos y convertirse en `[object Object]`.
2. Un error corregible volvía a renderizar la ficha y eliminaba los valores locales.
3. El correo QA no distinguía formato inválido de dominio no autorizado.
4. El teléfono completo dependía silenciosamente de un único valor canónico.
5. La composición del formulario no fijaba explícitamente las dos filas aprobadas.

## Implementación localizada

- Campo único `Nombre completo`.
- Desktop: `Nombre completo | Correo` y `País de facturación | Teléfono (opcional)`.
- Mobile: campos apilados; prefijo y número permanecen unidos.
- Errores por campo, sin objetos técnicos.
- Los errores corregibles no reconstruyen el formulario: conservan valores, selectores y solicitud.
- Selector de prefijo buscable por país, ISO o código, con teclado (`↑`, `↓`, `Enter`, `Escape`).
- Fuente única versionada para los teléfonos ficticios autorizados.
- Backend y frontend mantienen validación equivalente.

## Datos ficticios admitidos

Correos: cualquier dirección con formato válido terminada en:

- `example.com`
- `example.net`
- `example.org`

Teléfonos:

- `🇺🇸 +1 202 555 0107`
- `🇺🇸 +1 202 555 0147`
- `🇺🇸 +1 202 555 0199`

El teléfono puede omitirse dejando prefijo y número vacíos. No se deben utilizar datos reales.

## QA

- JavaScript syntax: PASS.
- Python compile: PASS.
- Pytest: 120 PASS / 0 FAIL.
- Dos contactos sintéticos diferentes: PASS.
- Teléfono vacío: PASS.
- Tres teléfonos autorizados: PASS.
- Teléfono parcial, error y posterior omisión: PASS.
- Formato de correo y dominio QA diferenciados: PASS.
- `422` estructurado, sesión preservada y reintento exitoso: PASS.
- Persistencia hasta `Antes de pagar`: cubierta por regresión heredada.

## Evidencia visual

La infraestructura de construcción no dispone de navegador ejecutable y el navegador remoto no puede acceder al servidor loopback. Por ello no se fabricaron pantallazos ni se declaró PASS visual. La verificación Desktop/Mobile queda pendiente de revisión manual sobre este candidato.

## Fronteras

Sin cambios en legal, precios, capacidades, pago, orden, correo, Agente Guía, conexiones externas o publicación.
