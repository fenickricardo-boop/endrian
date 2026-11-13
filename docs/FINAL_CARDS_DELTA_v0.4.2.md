# Delta localizado de fichas QA — v0.4.2

## Base y alcance

- Base recuperable: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.1.zip`.
- SHA-256 de la base: `9d70867b49bc79b7e4f597ce871ceb2d6a113a9e70cbd145825c73239a4377f3`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.
- Sin cambios en pago pendiente, orden, correo, Agente Guía, precios, capacidades ni documentos.

## Cambios

- `Nombre` y `Correo` comienzan vacíos con los placeholders aprobados.
- La validación admite identidades sintéticas diversas bajo los dominios reservados `example.com`, `example.net` y `example.org`; no exige una identidad exacta.
- El teléfono opcional es un único grupo visual con selector buscable de país/prefijo y número.
- La selección muestra bandera y prefijo; no existe selección inicial.
- Teléfono vacío pasa; teléfono completo sintético pasa; entrada parcial muestra una indicación localizada y no avanza.
- La síntesis `Antes de pagar` incorpora `Plataforma de uso: Entorno de prueba de ENDRIAN`.
- Se preservan los cuatro desplegables cerrados y el resto del recorrido aprobado.

## QA ejecutado

- JavaScript: `node --check frontend/app.js` — PASS.
- Compilación Python — PASS.
- Pytest: **115 passed / 0 failed**.
- Contacto sintético A sin teléfono — PASS.
- Contacto sintético B con teléfono completo — PASS.
- Teléfono parcial bloqueado y posterior omisión válida — PASS.
- Persistencia y contratos heredados — PASS por regresión.
- Ausencia de `[object Object]` en el contrato estático — PASS.

## Evidencia visual

La comprobación visual automatizada en navegador no pudo producir pantallazos: el navegador remoto no puede acceder al servidor loopback del entorno de construcción y no existe un navegador ejecutable local. El paquete queda preparado para revisión manual Desktop/Mobile; este bloqueo no se declara como PASS visual.

## Recuperación

Restaurar el ZIP independiente v0.4.1 y verificar su SHA-256. La versión anterior no fue sobrescrita ni incluida dentro del nuevo paquete.
