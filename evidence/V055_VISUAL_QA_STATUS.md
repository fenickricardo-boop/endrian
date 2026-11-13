# Estado de QA visual v0.5.5

La aplicación respondió correctamente en el servidor local y la regresión automatizada verificó estructura, contenido, rutas y preservación del flujo.

La inspección visual real en navegador no pudo completarse en este entorno: el navegador remoto bloqueó `http://127.0.0.1:8000` (`ERR_BLOCKED_BY_CLIENT`) y la descarga de Chromium para Playwright devolvió repetidamente un archivo vacío/truncado (`0 MiB`).

Por tanto:

- Desktop browser visual: `PENDING_MANUAL_REVIEW`.
- Mobile browser visual: `PENDING_MANUAL_REVIEW`.
- No se reutilizaron capturas de versiones anteriores.
- No se generaron capturas simuladas.

## Revisión manual requerida

1. Abrir `Características y precio` a 1440 × 900 y 390 × 844.
2. Confirmar una sola oferta, scroll oscuro/cyan y ausencia de tarjetas anteriores.
3. Probar `Hablar con ENDRIAN`: cerrar panel, volver al chat y conservar historial.
4. Probar `Contactar con ENDRIAN`: abrir Contacto y conservar historial.
5. Revisar Contacto vacío/completado, etiquetas y asteriscos en una línea, selectores abiertos, búsqueda y teclado.
6. Probar teléfono vacío y parcial; corregir sin pérdida de otros datos.
7. Ejecutar el recorrido QA anterior hasta orden y finalización.
