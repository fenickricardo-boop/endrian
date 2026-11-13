# ENDRIAN Laboratorio — Delta de iconografía v0.2.4

## Estado

`MICROAJUSTE VISUAL LOCALIZADO / CANDIDATO QA / NO PRODUCCIÓN`

## Fuente

- Base: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.3`.
- La base v0.2.3 se preservó sin sobrescritura.

## Cambio único

Se sustituyeron caracteres tipográficos por SVG simples de trazo, centrados mediante `viewBox="0 0 24 24"`, en:

- cinco controles circulares de cierre: Precios, Contacto, catálogo de Agentes, ficha de Agente y diálogo informativo;
- botón circular de envío del chat.

Los SVG usan `currentColor`; por tanto conservan el color existente. Se mantienen dimensiones, borde, fondo, función, accesibilidad y comportamiento de los botones. Se eliminaron las compensaciones tipográficas `transform: translate(...)` de estos iconos.

## Archivos funcionales modificados

- `frontend/index.html`
- `frontend/styles.css`

## Invariantes

Sin cambios en estructura, `Tu recorrido`, navegación, paneles, copy, catálogo, Contacto, chat, `frontend/app.js`, backend, Agente Guía, S0–S8/SH, PaymentGate, modelo, pagos e infraestructura.

## QA

- Contrato SVG: seis controles con `viewBox` uniforme, cinco cierres y un envío.
- Sin caracteres tipográficos `×` o `→` dentro de los controles circulares alcanzados.
- Suite completa y regresión: consultar evidencia incluida en `qa_results/pytest_v0.2.4.txt`.

## Revisión

Candidato preparado exclusivamente para revisión manual de Eduardo + Lía. No abre ningún frente posterior.
