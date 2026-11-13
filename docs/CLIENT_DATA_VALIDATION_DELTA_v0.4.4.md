# Datos del cliente — delta v0.4.4

Base preservada: `ENDRIAN_LAB_FULL_FLOW_QA_v0.4.3.zip`  
SHA-256 base: `49be807f6b0617064e90cae7d09a377cd9a526a5b85c7fb87c88b5e1c5fe7283`

## Cambio localizado

- Correo: acepta cualquier dirección con estructura válida; no verifica existencia ni restringe dominios.
- Teléfono: sigue siendo opcional. Vacío pasa; prefijo y número completos pasan si su estructura es válida; entradas parciales o inválidas se explican junto al grupo.
- Se retiró la allowlist de números exactos y su archivo de fixtures.
- Selector telefónico: muestra solo código ISO y prefijo (`CL +56`, `AR +54`, `US +1`); conserva nombre completo como etiqueta accesible, búsqueda y teclado.
- El formulario conserva valores y solicitud ante errores corregibles y permite reenviar en la misma sesión.
- La interfaz conserva una única instrucción general para usar datos ficticios; no activa correo, SMS ni verificación externa.

## Criterios de formato

- Nombre completo: 2–120 caracteres; letras latinas, espacios, punto, apóstrofo y guion.
- Correo: una parte local, `@`, dominio y sufijo de al menos dos caracteres; validación de formato solamente.
- Teléfono: país/prefijo autorizado por `phone_country_prefixes.json` y número nacional de 4–15 dígitos después de retirar espacios, paréntesis, puntos y guiones.
- País de facturación: selección obligatoria e independiente del país telefónico.

## Datos ficticios para repetir pruebas

- Sin teléfono: `Ana Prueba` / `ana@laboratorio.test` / Chile.
- Con CL: `Mario Ensayo` / `mario@correo.test` / Argentina / `CL +56` / `212345678`.
- Con AR: `Lucía Control` / `lucia@dominio.test` / Uruguay / `AR +54` / `1123456789`.
- Con US: `Tomás Revisión` / `tomas@prueba.test` / España / `US +1` / `2025550199`.

Los dominios `.test` y los datos anteriores se usan solo para pruebas locales; el sistema ya no depende de esos valores exactos.

## Fuera de alcance

Sin cambios en redirección, pago pendiente, orden, legal, precios, correo, SMS o Agente Guía. Sin conexiones externas ni publicación.
