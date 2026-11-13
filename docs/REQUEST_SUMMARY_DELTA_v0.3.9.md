# ENDRIAN Laboratorio — ajuste localizado v0.3.9

## Base

- Origen: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.8.zip`.
- Entorno: `QA_CONTROLLED_TEST_ONLY`.
- Recuperación de v0.3.5 preservada y verificada.

## Cambios

- La ficha estándar ya no muestra `Configurado para`, `Entorno y entrega` ni un bloque separado de límites redundantes.
- La revisión humana quedó integrada en `Lo que prepararemos`.
- Los cinco compromisos visibles del fixture de correos coinciden con el copy autorizado.
- El precio se presenta como `USD 20 · Precio de prueba, sin cobro real`.
- Profesional usa `2 a 5 días hábiles` en cotización, proyección pública, aceptación y snapshots de órdenes nuevas.
- La ficha muestra `Oferta válida hasta` con una fecha concreta derivada de `expires_at`.
- `expires_at` es canónico para nuevas cotizaciones; `valid_until` se conserva como alias compatible.
- Los datos internos de entorno, entrega, dependencias, controles y exclusiones permanecen trazables.
- La ruta especial conserva contexto, dependencias y límites materiales, sin precio ni pago automático.

## QA

- Regresión: **102 PASS / 0 FAIL**.
- Compilación Python: PASS.
- Sintaxis JavaScript: PASS.
- Coherencia de cotización, resumen, aceptación y snapshot: PASS.
- Orden existente: no se modifica; la nueva regla solo se aplica al crear cotizaciones y órdenes nuevas.

## Evidencia visual

El entorno de construcción continúa sin un ejecutable Chromium. Playwright no puede ejecutar las vistas desktop/móvil y la política de red impide descargar el navegador. No se declara cierre visual hasta completar una revisión manual del candidato o repetir la automatización en un entorno con navegador.
