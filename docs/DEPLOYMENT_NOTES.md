# Deployment notes — preparación Railway QA REV1

Este archivo documenta configuración futura. No se realizó despliegue ni se generó gasto.

## Servicio único

FastAPI sirve frontend y API desde el mismo origen. No requiere Node ni build frontend.

## Variables previstas para staging

- `APP_ENV=staging`
- `MODEL_MODE=real` (solo cuando se autorice credencial)
- `OPENAI_MODEL=gpt-5.6-terra`
- `OPENAI_API_KEY=<Railway secret>`
- `QA_DB_PATH=/data/qa_sessions.db`
- `COOKIE_SECURE=true`
- `SESSION_TTL_SECONDS=86400`
- `MAX_TURNS_PER_SESSION=30`
- `STAGING_ACCESS_USER=<secret obligatorio>`
- `STAGING_ACCESS_PASSWORD=<secret obligatorio>`

**Fail-closed:** con `APP_ENV=staging`, si falta cualquiera de los secretos de acceso o `COOKIE_SECURE` no es true, la aplicación falla al arrancar.

## Volumen

Montar `/data` para SQLite QA. La aplicación elimina sesiones vencidas por TTL.

## Frontera

No añadir pago, correo, orden o producción en este staging. El panel de Precios sigue informativo/provisional.
