# Seguridad del candidato QA — REV1

## Incluido

- Clave OpenAI únicamente vía `OPENAI_API_KEY` del servidor.
- `store=False` en Responses API.
- Pydantic `extra=forbid` + validación semántica por acción + bloqueo de campos de autoridad.
- Máximo un retry por salida estructurada inválida; fallback determinista posterior.
- SQLite con TTL 24 h y eliminación de sesiones vencidas.
- Cookie `HttpOnly`, `SameSite=Lax`; `Secure=true` obligatorio en staging.
- Rate limit de 60 req/min por IP y 45 req/min por sesión por defecto.
- Máximo 30 turnos por sesión.
- PII evidente bloqueada antes del modelo.
- CSP same-origin y `frame-ancestors 'none'`.

## Acceso staging fail-closed

Con `APP_ENV=staging` el proceso exige **ambos** secretos:

- `STAGING_ACCESS_USER`
- `STAGING_ACCESS_PASSWORD`

Si falta cualquiera, el proceso falla al arrancar. No existe fallback abierto. El middleware exige HTTP Basic para la aplicación. `/health` permanece público únicamente para healthcheck y devuelve `{"ok": true, "status": "QA / NO PRODUCCIÓN"}`; no expone presencia de clave, modo del modelo ni detalles del proveedor.

## Deliberadamente no construido

Autenticación productiva, correo verificado real, pagos, órdenes, recuperación productiva, WAF, DLP productivo, política legal definitiva, cifrado específico de DB o producción.
