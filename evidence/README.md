# Evidencia visual REV1

## Alcance honesto de las imágenes incluidas

Las cuatro capturas en `static_partial/` son **evidencia estática parcial**, obtenida a partir del HTML/CSS/SVG fuente del candidato. No demuestran navegación real contra el runtime FastAPI, sesión HTTP, conversación dinámica ni integración del modelo.

Por ello **NO constituyen evidencia E2E** y no deben utilizarse para declarar PASS visual del staging.

## Evidencia visual obligatoria en el siguiente gate de staging

Debe capturarse navegando la aplicación realmente servida, con control de acceso habilitado:

1. Desktop — entrada.
2. Desktop — conversación / ruta sugerida.
3. Mobile — entrada.
4. Mobile — conversación / ruta sugerida.
5. Panel de Precios — Desktop.
6. Panel de Precios — Mobile.

La conducta del modelo real también permanece no verificada hasta configurar una credencial controlada en la etapa autorizada posterior.
