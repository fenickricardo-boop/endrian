# Pendientes y defectos reales v0.2

## Defectos observados
Se documentan a partir de la ejecución de `qa/run_blackbox_qa.py`. Ver `qa/results/BLACKBOX_REPORT.md`.

## Dependencias no resueltas (esperadas)
- Selección e integración de un modelo de IA real: pendiente de Valeria/proveedor.
- Conducta del modelo real: **NO VERIFICADA** por este paquete.
- Precios, umbrales, plazos, políticas legales/comerciales, pago, correo, registro, órdenes y Laboratorio productivos: fuera de alcance y pendientes de producción según el contrato funcional.

No existe configuración de claves ni credenciales.

## Defecto localizado corregido durante v0.2
- Primera ejecución black-box: `BB-QA13` falló porque `PAGO PENDIENTE` no estaba incluido en la rama conversacional que acepta el mensaje natural de confirmación QA. Se corrigió únicamente el router conversacional; el núcleo v0.1 no fue modificado. Reejecución completa: 16/16 PASS.
