# ENDRIAN Laboratorio — Full Flow QA v0.5.15

**Estado:** QA SIMULADO / NO PRODUCCIÓN / MODELO DETERMINISTA / SIN SERVICIOS EXTERNOS.

Este candidato extiende de forma localizada la base verificada `ENDRIAN_LAB_AGENTES_QA_v0.1.2` para probar el recorrido completo `S0 → S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8`, con `SH` como salida protegida. Implementa registro sintético, dimensionamiento, orientación, propuesta QA, PaymentGate, pago simulado, orden QA idempotente, vista previa de correo, matriz interna, seguimiento y recuperación.

Para abrir localmente en Windows usa `START_LAB_QA.bat`. Consulta `README_LOCAL_QA.md` y `docs/FULL_FLOW_QA_REPORT_v0.2.md`.

**v0.5.12:** cierre visual localizado sobre v0.5.11. Ajusta la jerarquía tipográfica de Servicios, fichas individuales y Precios, y compacta mediante reglas compartidas el espaciado vertical de Contacto. Mantiene contenido, controles, rutas y comportamiento funcional sin cambios. Ver `docs/VISUAL_TYPOGRAPHY_CONTACT_DELTA_v0.5.12.md`.

**v0.5.13:** consolida el recorrido QA desde la bienvenida hasta `Pedido recibido`, reconcilia el fixture activo con ENDRIAN Especializado y USD 89, amplía la solicitud pública estructurada y corrige el fallback determinista para no anunciar comprensiones inexistentes. Ver `docs/CONTRACT_JOURNEY_DELTA_v0.5.13.md`.

**v0.5.14:** consolida las salidas posteriores a la orden: correo breve, PDF detallado, ficha interna privada y aviso interno no enviado, todos derivados de la orden archivada y su snapshot. También completa remates localizados del recorrido sin reabrir el catálogo ni los módulos cerrados. Ver `docs/POST_CONFIRMATION_CONSOLIDATED_DELTA_v0.5.14.md`.

**v0.5.15:** simplifica la proyección pública del resumen, la revisión previa, la simulación de pago y el PDF. Mantiene íntegros los datos canónicos y la ficha interna, y versiona el PDF como `ENDRIAN-POST-CONFIRMACION-1.1-QA`. Ver `docs/SIMPLIFIED_PUBLIC_SURFACES_DELTA_v0.5.15.md`.

**v0.2.1:** corrección exclusivamente visual del header Mobile para impedir que el contenido desplazado quede visible o se confunda por debajo del encabezado sticky. Sin cambios en rutas, estados, backend, PaymentGate, copy, agentes ni funcionalidad.

**v0.2.2:** corrección UX localizada de interfaz general. Se actualiza únicamente navegación/paneles/contenido visible del Laboratorio: nuevo menú superior, catálogo `Agentes` en panel integrado, `Precios` derivado del mismo catálogo, panel local de `Contacto`, `Privacidad` secundaria, eliminación del bloque de temas sugeridos y microalineación de flechas/X. No se modifica el comportamiento conversacional del Agente Guía, backend, S0–S8/SH, PaymentGate, agentes ni infraestructura.

**v0.2.3:** corrección UX espacial localizada sobre v0.2.2. La columna visible pasa de `Recorrido QA` a `Tu recorrido` con cuatro etapas públicas derivadas de S0–S8/SH; el chat usa altura controlada, scroll interno y composer estable; los glifos de cierre y envío reciben centrado óptico consistente. No se modifica el comportamiento conversacional del Agente Guía, backend, estados internos, PaymentGate, catálogo, pagos ni infraestructura. Ver `docs/UX_SPATIAL_DELTA_v0.2.3.md`.

**v0.2.4:** microajuste final de iconografía sobre v0.2.3. Los caracteres tipográficos de los cinco cierres circulares y del envío circular se sustituyen por SVG de trazo centrados mediante `viewBox`, sin compensaciones manuales ni cambios de botón, función o comportamiento. Ver `docs/ICONOGRAPHY_DELTA_v0.2.4.md`.

**v0.3.6:** incorpora la solicitud canónica versionada, separación `workflow_status` / `validation_result`, resumen anterior al contacto, rutas `STANDARD` y `SPECIAL_REVIEW`, precios QA configurables en USD, revisión privada, expiración e invalidación de cotizaciones y snapshot inmutable del pedido de construcción. Ver `docs/HANDOFF_LOCALIZADO_DELTA_v0.3.6.md`.

**v0.3.7:** corrige el bucle del caso completo de atención por correo: genera y muestra la comprensión profesional, reconoce la conformidad explícita, crea una única versión y renderiza `Resumen de tu solicitud`. Ver `docs/EMAIL_SUMMARY_LOOP_DELTA_v0.3.7.md`.

**v0.3.8:** limita el simulador a dos guiones QA cerrados, incorpora acciones visibles de confirmar/corregir, completa la ruta estándar hasta orden y la ruta especial hasta solicitud de revisión sin precio ni pago. La validación funcional está completa; la evidencia visual automatizada queda bloqueada por ausencia de un navegador ejecutable en el entorno de construcción. Ver `docs/MINIMAL_QA_CLOSURE_DELTA_v0.3.8.md`.

**v0.4.1:** aplica el ajuste localizado de plazo, selectores integrados, teléfono estructurado y dos aceptaciones versionadas. Ver `docs/CONTACT_ACCEPTANCE_DELTA_v0.4.1.md`.

**v0.4.2:** cierra de forma localizada las fichas de contacto y pre-pago: campos vacíos con validación sintética no ligada a una identidad exacta, teléfono opcional agrupado y coherente, plataforma visible en la síntesis y regresión específica. Ver `docs/FINAL_CARDS_DELTA_v0.4.2.md`.

**v0.4.3:** corrige el formulario de datos del cliente y su recuperación: distribución definitiva, validaciones por campo, mensajes diferenciados, varios teléfonos ficticios autorizados, tratamiento legible de errores `422` y reintento sin perder la solicitud. Ver `docs/CLIENT_DATA_RECOVERY_DELTA_v0.4.3.md`.

**v0.4.4:** elimina las allowlists de dominios y teléfonos del formulario QA, conserva validación estructural equivalente en frontend/backend, simplifica el selector de prefijo a `CL +56`/equivalentes y mantiene recuperación sin perder la solicitud. Ver `docs/CLIENT_DATA_VALIDATION_DELTA_v0.4.4.md`.

**v0.4.5:** iguala tipografía y alineación del grupo telefónico, muestra `Nombre completo` en la revisión, aclara las condiciones de servicios externos y simplifica el estado visible de pago pendiente. Ver `docs/FINAL_CARDS_AND_PAYMENT_QA_DELTA_v0.4.5.md`.

**v0.4.6:** corrige ancho de países, uniformidad ISO/prefijo, alineación del formulario y separación de indicadores; elimina mensajes internos/repetidos antes del pago. Ver `docs/VISUAL_FINAL_AND_QA_ORDER_DELTA_v0.4.6.md`.

**v0.4.7:** restablece la búsqueda normalizada de países y completa la ficha persistente posterior a la confirmación privada del pago QA. Ver `docs/COUNTRY_SEARCH_AND_ORDER_CONFIRMATION_DELTA_v0.4.7.md`.

**v0.4.8:** corrige la regla CSS que impedía ocultar países no coincidentes y carga automáticamente el intento pendiente en el control privado de pago.

**v0.4.9:** retira el bloque fijo `Condiciones de mi pedido` cuando no existen particularidades materiales, preservando aceptación, PaymentGate y snapshot.

**v0.5.0:** completa la confirmación privada hasta orden, archiva la orden QA fuera de la sesión conversacional y añade `Finalizar conversación` para limpiar la interfaz y rotar la sesión sin borrar el pedido. Ver `docs/POSTPAYMENT_FINALIZATION_DELTA_v0.5.0.md`.

**v0.5.1:** simplifica el cierre público post-pago, proyecta el título específico desde el snapshot y completa visualmente `Pedido recibido`. Ver `docs/POSTPAYMENT_PUBLIC_CLOSURE_DELTA_v0.5.1.md`.

**v0.5.2:** incorpora la vista previa privada QA del correo al cliente y un único PDF de copia de contratación de prueba generado desde la orden archivada. Mantiene `sent=false`, no envía correo, no redacta T&C nuevos y no modifica snapshots existentes. Ver `docs/CUSTOMER_CONFIRMATION_DELTA_v0.5.2.md`.

**v0.5.4:** cierre localizado de Agentes, Precios y Contacto general: copy público v1.4.1 completo, modalidades comerciales provisionales por agente, formulario definitivo de contacto general y barras oscuras/cyan. PaymentGate, órdenes, snapshots y el formulario de contratación permanecen sin cambios. Ver `docs/COMMERCIAL_CONTACT_CLOSURE_DELTA_v0.5.4.md`.

**v0.5.5:** unifica `Agentes` y `Precios` en el panel público `Características y precio`, publica una única oferta de agente personalizado por USD 89, retira `Explorar agentes` del saludo y corrige la alineación semántica del Contacto general. El catálogo interno, la clasificación del Guía, los importes QA, PaymentGate, órdenes y snapshots no se remapean. Ver `docs/UNIFIED_OFFER_CONTACT_DELTA_v0.5.5.md`.

**v0.5.6:** corrige exclusivamente el panel público unificado: precio de lanzamiento `USD 79`, introducción final autorizada, retirada de la aclaración sobre suscripción y CTA principal ubicado inmediatamente después del plazo. Los importes QA internos y el resto del Laboratorio permanecen sin cambios. Ver `docs/COMMERCIAL_PANEL_FINAL_DELTA_v0.5.6.md`.

**v0.5.8:** sustituye el panel comercial único por dos paneles informativos independientes, `Servicios` y `Precios`, con el contenido público aprobado en `ENDRIAN_LAB_CONTENIDO_SERVICIOS_Y_PRECIOS_v1.0`. Reaplica la normalización visual del Contacto general sobre la base verificable v0.5.6. La ruta conversacional, contratación, pagos, órdenes, correo, PDF y One Page permanecen sin cambios. Ver `docs/SERVICES_PRICES_CONSOLIDATED_DELTA_v0.5.8.md`.

**v0.4.0:** completa el handoff consolidado de ficha, país de facturación, condiciones previas, checkout simulado, espera de confirmación backend, orden única y vista previa de correo derivada del snapshot.

**v0.3.9:** simplifica la ficha pública del caso estándar, integra la revisión humana en los compromisos, adopta el plazo QA `2 a 5 días hábiles` y muestra la fecha concreta de expiración de la oferta.

**No hay pagos, correos, órdenes productivas, PII real, proveedores externos ni modelo real.** Los importes, plazos, condiciones y verificaciones de contacto son exclusivamente fixtures controlados.

---

## Historial técnico heredado de la base v0.1.2

# ENDRIAN LAB + Agente Guía — QA Candidate REV1

**Estado:** CANDIDATO QA / REV1 CORREGIDO / NO PRODUCCIÓN / SIN PAGOS / SIN CREDENCIALES / COPY PROVISIONAL.

REV1 parte de `ENDRIAN_LAB_AGENTE_GUIA_QA_CANDIDATE_v0.1` y corrige únicamente los hallazgos de auditoría: acceso staging fail-closed, consumo real de `FLAG_HUMAN_REVIEW`, suites QA no destructivas, evidencia visual descrita honestamente y health público mínimo.

## Qué contiene

- `frontend/`: Laboratorio Desktop/Mobile basado en el master visual consolidado v1.0.
- `app/`: FastAPI, sesiones SQLite QA, rate limiting, acceso staging, adaptador/validador del modelo y política determinista para señales del modelo.
- `agent_guide/`: capa conversacional v0.2 y **lógica de control `guide_agent.py` v0.1 preservada byte-identical**. Los runners QA/documentación de integración fueron corregidos en REV1 para no mutar archivos congelados y reconciliar acciones del schema.
- `config/ui_copy.json`: copy y categorías comerciales provisionales, reemplazables.
- `tests/`: QA automatizado REV1.
- `evidence/static_partial/`: evidencia visual estática parcial, explícitamente no E2E.
- `qa_results/`: resultados reproducibles de las suites ejecutadas para REV1.
- `railway.json` + `Procfile`: preparación de staging posterior; no despliega ni crea cargos.

## Modos de modelo

- `MODEL_MODE=deterministic`: default, sin API ni credenciales.
- `MODEL_MODE=real`: OpenAI Responses API + Structured Outputs, preparado pero **no ejecutado** por falta deliberada de credencial.

La llamada real usa `store=False`, razonamiento bajo, máximo un retry y salida Pydantic estricta. El modelo no controla estados, clasificación comercial, precio, plazo, pago, orden ni matriz. `FLAG_HUMAN_REVIEW` es una **solicitud validada** que pasa por `DeterministicModelSignalPolicy`; la política local es quien aplica el estado canónico de revisión humana.

## Flujo implementado

`Entrada → conversación → preguntas materiales → interpretación → ruta sugerida → confirmación → envío QA`

No se construyeron operaciones productivas de registro, pago, correo, orden o producción. Para atravesar el gate de registro sin recopilar PII real, se usa una identidad QA sintética `example.invalid`.

## Seguridad REV1

- En `APP_ENV=staging`, `STAGING_ACCESS_USER` y `STAGING_ACCESS_PASSWORD` son obligatorios: si falta cualquiera, el proceso **no arranca**.
- En staging también se exige `COOKIE_SECURE=true`.
- `/health` es público pero mínimo: no revela modo de modelo, proveedor ni existencia de `OPENAI_API_KEY`.
- Cookie `HttpOnly + SameSite=Lax`; Secure obligatorio en staging.
- Rate limit por IP/sesión, máximo 30 turnos, TTL 24 h.
- Sin secretos en frontend, ZIP o repositorio.
- PII evidente se bloquea antes del modelo.

## QA

Consultar `docs/QA_REPORT.md`, `docs/REV1_DELTA_REPORT.md` y `docs/REV1_REPRODUCIBLE_QA.md`.

La conducta real de `gpt-5.6-terra` continúa **NO VERIFICADA**. El siguiente gate sigue siendo credencial controlada + staging protegido + evidencia visual servida realmente desde FastAPI.


## Integración visual de agentes QA v0.1
Candidato localizado sobre REV1 para selector/fichas de los cuatro agentes. Sin deploy. Ver `docs/AGENTS_INTEGRATION_QA_REPORT.md`.


## Corrección responsive de agentes QA v0.1.2
Corrección exclusivamente Mobile sobre v0.1.1: ajuste de flujo de `Explorar agentes`, wrapping de franja QA, crecimiento de tarjeta de agente seleccionado, apilado de acciones de ruta y crecimiento de tarjetas del selector. No modifica copy, lógica, backend, selección, identificadores ni arquitectura. Ver `docs/AGENTS_INTEGRATION_DELTA_v0.1.2.md`.


**v0.5.9:** corrección localizada de presentación del panel `Servicios`: sustituye las tres fichas completas apiladas por tres tarjetas resumen y una ficha individual visible a la vez dentro del mismo drawer. Mantiene literalmente el contenido público de `ENDRIAN_LAB_CONTENIDO_SERVICIOS_Y_PRECIOS_v1.0`, elimina el botón redundante `Volver a la conversación` del panel Servicios y utiliza `×` para cerrar y `← Servicios` para regresar al selector. No modifica Precios, Contacto, conversación, recorrido, contratación, pago, órdenes ni backend. Ver `docs/SERVICES_PANEL_COMPACT_DELTA_v0.5.9.md`.
