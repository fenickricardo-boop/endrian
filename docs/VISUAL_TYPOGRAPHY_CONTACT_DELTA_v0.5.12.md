# Cierre visual localizado v0.5.12

Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.5.11`.

## Ajustes implementados

- Se conserva la familia declarada `Inter` con la misma pila de respaldo; no se incorporó ni sustituyó el wordmark ni la identidad.
- Servicios: nombres a 16 px en listado y 19 px en ficha; descripciones a 12/13 px con peso moderado; cuerpo de ficha a 12 px con interlineado 1.62.
- Controles: `Ver ficha` y `Volver a Servicios` a 12 px con peso 650 y separación existente preservada.
- Precios: nombres e importes a 15 px; descripción a 12 px con interlineado 1.55.
- Contacto: separación compartida entre grupos reducida de 12 px a 9 px; etiquetas a 12.5 px; campos a 13 px y peso 500; errores/estado vacíos dejan de reservar espacio; el área Mensaje conserva su altura mayor.

## Preservación

No se modificaron textos, estructura HTML, JavaScript, rutas, validaciones, paneles, pagos, órdenes, correo, PDF, One Page ni comportamiento conversacional. Precios conserva únicamente la X superior como cierre visible.

## Límite de evidencia visual

La revisión estática, las pruebas automatizadas y la verificación HTTP fueron ejecutadas. La captura automatizada en navegador quedó pendiente porque el entorno de construcción no dispone de un navegador ejecutable y el navegador remoto no puede acceder a `localhost`. No se declara PASS visual interactivo.
