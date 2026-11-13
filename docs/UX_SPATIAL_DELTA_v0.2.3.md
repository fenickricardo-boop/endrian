# ENDRIAN Laboratorio — Delta UX localizado v0.2.3

## Estado

`CANDIDATO QA / NO PRODUCCIÓN / LISTO PARA REVISIÓN MANUAL EDUARDO + LÍA`

## Fuente exacta

- Fuente: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.2.zip`
- SHA-256 verificado: `88b2c5d4e160eda0392d962b19cea0c383d59a29dcd0460c2f92a8cdaa3c4349`
- La fuente adjunta permaneció inmutable.

## Alcance materializado

1. Centrado óptico explícito para los cinco controles circulares de cierre y el botón circular de envío, sin alterar dimensiones, función ni lenguaje visual.
2. Sustitución de la vista pública `Recorrido QA` por `Tu recorrido`:
   - `S0–S1` → `Conversación`.
   - `S2–S4` y `SH` → `Definición de tu solución`.
   - `S5–S6` → `Confirmación y pago`.
   - `S7–S8` → `Entrega y seguimiento`.
3. Estados visibles derivados en tiempo de ejecución: `Completado`, `Etapa actual` y `Pendiente`.
4. La revisión humana conserva `SH` internamente y se presenta al usuario como una pausa acotada dentro de la definición, sin exponer nomenclatura técnica.
5. La superficie lateral queda semánticamente identificada mediante `data-panel-mode="journey"`, preparada para una evolución posterior autorizada a seguimiento sin implementar datos ni funciones nuevas.
6. Composición de chat con altura controlada en Desktop y Mobile, historial con scroll interno, contención de overscroll, composer sin contracción y autoscroll vigente al último mensaje.

## Archivos funcionales modificados

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`

## Evidencia y QA

- Suite total: **76/76 PASS**.
- Regresión heredada de v0.2.2: **68/68 PASS**.
- Contrato específico v0.2.3: **8/8 PASS**.
- `node --check frontend/app.js`: **PASS**.
- Smoke HTTP local: `/health` responde 200 y sirve HTML, JS y CSS con navegación, `Tu recorrido` y reglas espaciales esperadas.
- Comparación byte-a-byte contra v0.2.2: `app/**`, `agent_guide/**`, ambos catálogos, launchers Python/Windows: **PASS**, excepto directorios efímeros `__pycache__`, excluidos del paquete.
- Revisión visual final de percepción óptica: deliberadamente pendiente de Eduardo + Lía sobre el candidato navegable.

## Invariantes preservados

- Backend y endpoints: sin cambios.
- Agente Guía, prompts, interpretación, preguntas, respuestas y resumen: sin cambios.
- S0–S8/SH y PaymentGate: sin cambios.
- Catálogo, navegación, paneles Agentes/Precios/Contacto, formulario, Privacidad secundaria y eliminación de chips: preservados.
- Pagos, GitHub, Railway, infraestructura, servicios externos, producción y lanzamiento: sin cambios/no activados.

## Hallazgos

- No se detectaron contradicciones materiales ni defectos adicionales dentro del alcance.
- La validación automatizada confirma contrato estructural y regresión; la aceptación estética del centrado óptico corresponde a la revisión manual solicitada.

## Rollback

Rollback directo al ZIP fuente `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.2.zip`, identificado por su SHA-256 verificado. El candidato no sobrescribe esa fuente.
