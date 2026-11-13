# Delta localizado v0.5.9 — Servicios compactos

## Base

- Base: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.8.zip`.
- SHA-256 base: `44cb361edbbf1fbd1a5dfef5d7d8a4ce5685f95e91fbd1fbd3a8779ee7dfabfa`.
- Autoridad editorial: `ENDRIAN_LAB_CONTENIDO_SERVICIOS_Y_PRECIOS_v1.0.docx`.
- Referencia visual recuperada: `ENDRIAN_LAB_AGENTES_QA_v0.1.2.zip`.

## Cambio

- `Servicios` conserva el drawer lateral vigente.
- Vista inicial: tres tarjetas breves, una por servicio, con número, nombre, descripción aprobada y `Ver ficha`.
- Ficha: una sola visible a la vez, dentro del mismo drawer.
- Campos de ficha: `Necesidad`, `Qué hacemos`, `Qué recibes`, `Diferencia de alcance`.
- `← Servicios` regresa a las tres tarjetas.
- `×` cierra el panel completo y restaura el foco al disparador de Servicios.
- Se retira del panel Servicios el botón visual redundante `Volver a la conversación`.
- No hay selección, contratación ni precio dentro de Servicios.

## Preservado

Precios, Contacto, conversación, `Tu recorrido`, flujo comercial, registro, contratación, pago, orden, backend, PDFs y One Page permanecen sin cambios.

## Responsive

- Desktop: tarjetas compactas de una columna dentro del drawer.
- Mobile: tarjetas apiladas; `Ver ficha` ocupa el ancho disponible en pantalla estrecha.
- La ficha usa el cuerpo desplazable del drawer; `×` permanece en la cabecera del panel y `← Servicios` permanece accesible al comienzo de la ficha.
