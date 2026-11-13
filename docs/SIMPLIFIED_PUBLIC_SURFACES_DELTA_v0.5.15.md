# Simplificación localizada de superficies públicas — v0.5.15

## Base

- Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.14.zip`.
- SHA-256: `b4bf297b041ada3811e5e0a8a7bd38ea182a3c7502935db06da41c718753592b`.
- Plantilla pública PDF: `ENDRIAN-POST-CONFIRMACION-1.1-QA`.

## Cambios

- `Resumen de tu solicitud` conserva solución, servicio recomendado, `Qué incluye`, plataforma, precio y plazo.
- `Qué incluye` utiliza la descripción y entregables existentes, más las condiciones materiales del fixture: información incorporada por el equipo y borradores revisados/enviados por el equipo.
- `Antes de pagar` mantiene una síntesis corta y un resumen desplegable condensado, sin eliminar datos del cliente, documentos ni aceptaciones.
- `Simulación de pago` muestra únicamente aviso QA, servicio, importe y retorno.
- El PDF público elimina materiales/estados, notas operativas, hash, snapshot y referencias de implementación.
- El PDF conserva identificación, solución, servicio, contenido contratado, plataforma, modalidad, importe, pago, plazo, siguiente paso y condiciones aceptadas.
- La ficha interna conserva alcance, compromisos, entregables, materiales, dependencias y trazabilidad técnica.

## Preservación

No se modifican `scope_version`, `solution_request_version`, `quotation_version`, PaymentGate, intento de pago, orden, snapshot, aceptaciones, hash ni registros históricos. La corrección cambia renderizadores y pruebas, no los datos contratados.
