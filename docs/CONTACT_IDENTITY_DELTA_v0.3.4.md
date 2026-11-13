# ENDRIAN Lab — desbloqueo de Datos de contacto v0.3.4

Fecha: 2026-10-07  
Entorno: `QA_CONTROLLED_TEST_ONLY`

## Origen y rollback

- Origen preservado: `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.3.zip`
- SHA-256: `eec7ec823500a8bb9a4171eadb083d7467e7b7a46b6cd323ed12171f137fd797`
- Rollback: restaurar la extracción limpia de ese ZIP y verificar el hash.

## Corrección localizada

Se congeló una única identidad ficticia autorizada:

- Nombre: `Juan Pérez`
- Correo: `juan.perez@example.com`

La fuente canónica reside en `app/full_flow.py` y la validación se ejecuta exclusivamente en backend. El frontend no mantiene una segunda allowlist.

Orden visible de validación:

1. nombre inválido → `Revisa el nombre ingresado.`;
2. correo inválido → `Revisa el correo ingresado.`;
3. datos válidos sin consentimiento → `Confirma esta opción para continuar.`;
4. datos y consentimiento válidos → propuesta.

`example.com` es un dominio reservado para documentación y pruebas. No se requiere ni admite PII real en este fixture.

## Archivos funcionales modificados

- `app/full_flow.py`
- `app/service.py`
- `frontend/app.js`
- `tests/test_full_flow_v02.py`
- `tests/test_visible_journey_v032.py`

No se modificaron conversación, `scope_version`, propuesta, PaymentGate, contratación/pago, diseño general ni estados S0–S8/SH.

## QA

- Pruebas focalizadas de contacto: **3/3 PASS**.
- Regresión completa: **81/81 PASS**.
- JavaScript: **PASS**.
- Compilación Python: **PASS**.
- El candidato tiene nombre y checksum propios; debe iniciarse desde el directorio extraído `ENDRIAN_LAB_FULL_FLOW_QA_v0.3.4` para evitar ejecutar una versión anterior.

Estado propuesto: **DATOS DE CONTACTO DESBLOQUEADOS / IDENTIDAD FICTICIA CANÓNICA VALIDADA / CANDIDATO LISTO PARA CONTINUAR PRUEBA EDUARDO + LÍA**.
