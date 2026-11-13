# Evidencia visual v0.5.13

No se adjuntan capturas nuevas porque el navegador remoto de esta sesión no pudo abrir el servidor local de la candidata.

Errores observados:

- `http://127.0.0.1:8000/`: `Missing or invalid bearer token`.
- `http://localhost:8000/`: `Missing or invalid bearer token`.
- `http://host.docker.internal:8000/`: conexión restablecida antes de recibir encabezados.

No se declara PASS visual desktop/móvil. La verificación funcional se ejecutó por la API real de FastAPI y la regresión automatizada; la revisión visual queda explícitamente pendiente en el navegador local de Eduardo + Lía, siguiendo `docs/TEST_GUIDE_v0.5.13.md`.

