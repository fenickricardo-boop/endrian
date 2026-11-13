# ENDRIAN Laboratorio QA — cierre público post-pago v0.5.1

Entorno: `QA_CONTROLLED_TEST_ONLY`.

## Delta autorizado

- El snapshot inmutable incorpora `solution_title`, tomado de la solicitud canónica versionada.
- La confirmación pública proyecta exclusivamente ese título. Su ausencia produce un error localizado y no oculta el pago ni la orden.
- Se retiraron de la ficha pública `Verificar pedido` y `Ver seguimiento`; los mecanismos privados permanecen intactos.
- `Finalizar conversación` es la única acción pública post-pago.
- El cuarto paso visible pasa a `Pedido recibido`. En S7/S8 los cuatro pasos se muestran completados sin declarar construcción o entrega.

## Invariantes

Pago, correo y construcción reales permanecen desactivados. Se preservan PaymentGate, idempotencia, archivo privado de la orden, snapshot sin transcript y vista previa del correo con `sent=false`.

## Límite de verificación

La regresión automatizada cubre datos, estados y contrato de renderizado. La inspección visual final desktop/móvil debe realizarse manualmente cuando no exista navegador ejecutable en el entorno de construcción.
