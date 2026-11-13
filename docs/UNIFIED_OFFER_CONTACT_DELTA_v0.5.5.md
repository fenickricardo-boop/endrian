# Delta localizado v0.5.5 — oferta unificada y Contacto general

## Base preservada

- Baseline: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.4.zip`
- Tamaño: `243458880` bytes
- SHA-256: `2e55abbf2878ed8a691e97c005bdcafa0e25e8b6b4129d86499b658bff0678ab`
- Integridad de extracción: PASS antes de modificar.

## Implementado

- `Agentes` y `Precios` se sustituyen por una única entrada `Características y precio` en desktop y móvil.
- El panel lateral existente muestra exclusivamente la oferta pública de agente personalizado por `USD 89 · Pago único de lanzamiento`, con el copy autorizado y dos CTA.
- `Hablar con ENDRIAN` cierra el panel y devuelve el foco al composer sin crear ni reiniciar sesión.
- `Contactar con ENDRIAN` abre el Contacto general sin perder la conversación.
- Se elimina el botón `Explorar agentes` situado bajo el saludo inicial.
- El Contacto general agrupa cada etiqueta y su asterisco en una misma línea, conserva dos columnas en desktop y apila en móvil.
- Selectores, validación opcional de teléfono, recuperación de datos y scrollbars oscuras/cyan se preservan.

## Frontera preservada

La oferta pública única no remapea todavía las categorías internas `Avanzado / Integral / Profesional / Premium`, la selección del Guía ni las rutas `STANDARD / SPECIAL_REVIEW`. Tampoco reemplaza `QA_PRICE_ADVANCED=USD 10` y `QA_PRICE_PROFESSIONAL=USD 20` del recorrido simulado. Órdenes y snapshots anteriores permanecen inmutables.

## Reconciliación mínima pendiente

Antes de cambiar la clasificación interna se requiere una decisión funcional que defina: (1) qué combinación validada de capacidades constituye la oferta única; (2) cuándo una solicitud deja de caber en ella y pasa a cotización particular; (3) cómo se proyectan las categorías históricas en datos archivados sin reescribir órdenes ni snapshots. Hasta entonces, la nueva oferta se limita a la superficie comercial pública.

## Producción

No autorizada. Sin IA, pagos, correo, SMS, publicación ni servicios externos reales.
