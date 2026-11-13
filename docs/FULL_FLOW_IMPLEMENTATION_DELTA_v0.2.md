# ENDRIAN LAB FULL FLOW QA v0.2 — implementación controlada

Base fuente verificada: `ENDRIAN_LAB_AGENTES_QA_v0.1.2.zip`  
SHA-256: `91e42504d0b1cf4bb1a1c7bb8b13b560ac7579678c3d376dc8f5d64a79e7d5a1`

Autoridad funcional aplicada: `ENDRIAN_LAB_DELTA_RUTAS_FUNCIONALES_QA_v0.2.1` y cierre final PASS de Sofía.

## Correcciones C01–C07
- **C01**: orden visible S1 → S2 → S3 → S4 antes de propuesta/pago.
- **C02**: S4 Confirmar→S5; corrección material→S3; corrección menor→S4 actualizando resumen; Revisión→SH. S5 retorna a S3/S4/SH; SH nunca enlaza directo a S6.
- **C03**: PaymentGate autoritativo de nueve condiciones en servicio determinista.
- **C04**: estados de pago con retornos deterministas; solo CONFIRMADO crea/recupera S7.
- **C05**: orden QA idempotente por versión de propuesta + confirmación QA; replay devuelve la misma orden.
- **C06**: recuperación por `qa_identity_ref` restaura el snapshot persistido sin reejecutar pago ni recrear orden.
- **C07**: rollback incorpora el ZIP fuente byte-idéntico y verifica el SHA-256 exacto.

## Rutas R01–R09
R01 necesidad abierta; R02 agente elegido; R03 registro QA; R04 propuesta simulada; R05 revisión humana; R06 pago aprobado; R07 pago no aprobado; R08 recuperación; R09 confirmación + vista previa de correo.

## Seguridad / no producción
Todo el flujo es local y determinista. No se integra proveedor de IA, pago, correo, orden productiva ni servicio externo. El correo es una vista previa persistida con `sent=false`. Los valores `$123.456 CLP`, `10 días hábiles QA` y vigencia `7 días QA` existen solo para demostrar estados y relaciones.
